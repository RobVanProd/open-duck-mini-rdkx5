from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_winner_v12_full_calibrator_training_artifact.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("winner_v12_artifact_check", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_success_inventory_is_exact() -> None:
    checker = load_checker()
    files = checker.expected_artifact_files()
    assert len(files) == 415
    assert checker.ROOT_LOG_NAME in files
    assert checker.ROOT_RESULT_HASH_NAME in files
    assert f"{checker.WORK_ROOT_NAME}/snapshots/snapshot_stage1_update_001.npz" in files
    assert (
        f"{checker.WORK_ROOT_NAME}/snapshots/snapshot_stage2_update_100.receipt.json"
        in files
    )


def test_safe_zip_extracts_regular_relative_members(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "safe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("root/file.txt", b"safe")
    destination = tmp_path / "extracted"
    assert checker.safe_extract_zip(archive, destination) == ["root/file.txt"]
    assert (destination / "root/file.txt").read_bytes() == b"safe"


@pytest.mark.parametrize("name", ["../escape", "/absolute"])
def test_safe_zip_rejects_traversal_or_non_posix_path(
    tmp_path: Path, name: str
) -> None:
    checker = load_checker()
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(name, b"unsafe")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")


def test_safe_zip_rejects_duplicate_member(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("same", b"one")
        stream.writestr("same", b"two")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")


def test_safe_zip_rejects_symlink(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(link, "target")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")


def test_verified_checkpoint_identity_exposes_exact_gate_inputs(
    tmp_path: Path,
) -> None:
    checker = load_checker()
    checkpoint = tmp_path / "winner_v12_calibrator_half.npz"
    graph = tmp_path / "winner_v12_calibrator_half.onnx"
    receipt = tmp_path / "winner_v12_calibrator_half_receipt.json"
    checkpoint.write_bytes(b"checkpoint")
    graph.write_bytes(b"graph")
    receipt.write_bytes(b"receipt")
    graph_contract = {
        "abi_exact": True,
        "all_chain_outputs_finite": True,
        "all_initializers_finite": True,
        "inputs": [
            {"name": "obs", "shape": [1, 115]},
            {"name": "previous_action", "shape": [1, 14]},
            {"name": "h_in", "shape": [1, 64]},
        ],
        "jax_onnx_at_most_1e_7": True,
        "jax_onnx_max_abs_error": 0.0,
        "outputs": [
            {"name": "calibration_actions", "shape": [1, 14]},
            {"name": "previous_action_out", "shape": [1, 14]},
            {"name": "h_out", "shape": [1, 64]},
        ],
        "previous_action_out_equals_action_bit_exact": True,
        "training_only_tensors_absent": True,
    }
    result = checker.verified_checkpoint_identity(
        label="half",
        update=50,
        checkpoint_path=checkpoint,
        graph_path=graph,
        receipt_path=receipt,
        graph_contract=graph_contract,
    )
    assert result["checkpoint"] == {
        "file": checkpoint.name,
        "sha256": checker.sha256(checkpoint),
        "bytes": checkpoint.stat().st_size,
    }
    assert result["onnx"]["sha256"] == checker.sha256(graph)
    assert result["receipt"]["sha256"] == checker.sha256(receipt)
    assert result["update"] == 50


def test_verified_checkpoint_identity_rejects_wrong_boundary(
    tmp_path: Path,
) -> None:
    checker = load_checker()
    path = tmp_path / "artifact"
    path.write_bytes(b"artifact")
    with pytest.raises(ValueError, match="boundary"):
        checker.verified_checkpoint_identity(
            label="half",
            update=49,
            checkpoint_path=path,
            graph_path=path,
            receipt_path=path,
            graph_contract={},
        )


def test_repository_attribution_binds_exact_run_and_artifact() -> None:
    checker = load_checker()
    result = checker.repository_attribution(
        run_id=29808732634,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=123,
        artifact_name="winner-v12-full-calibrator-training-29808732634",
        artifact_digest=f"sha256:{'b' * 64}",
        expected_zip_sha256="b" * 64,
    )
    assert result["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert result["github_run_id"] == 29808732634
    assert result["github_artifact_id"] == 123


def test_repository_attribution_rejects_rerun_or_digest_drift() -> None:
    checker = load_checker()
    arguments = {
        "run_id": 29808732634,
        "run_attempt": 1,
        "run_head_sha": "a" * 40,
        "artifact_id": 123,
        "artifact_name": "winner-v12-full-calibrator-training-29808732634",
        "artifact_digest": f"sha256:{'b' * 64}",
        "expected_zip_sha256": "b" * 64,
    }
    with pytest.raises(ValueError, match="attribution"):
        checker.repository_attribution(**{**arguments, "run_attempt": 2})
    with pytest.raises(ValueError, match="attribution"):
        checker.repository_attribution(
            **{**arguments, "artifact_digest": f"sha256:{'c' * 64}"}
        )
    with pytest.raises(ValueError, match="object ID"):
        checker.repository_attribution(**{**arguments, "run_head_sha": "a" * 64})
