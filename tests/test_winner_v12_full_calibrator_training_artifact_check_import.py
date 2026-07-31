from __future__ import annotations

import importlib.util
import copy
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = (
    ROOT / "tools/import_winner_v12_full_calibrator_training_artifact_check.py"
)


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v12_artifact_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_artifact(path: Path, raw: bytes = b"{}") -> str:
    importer = load_importer()
    digest = importer.sha256_bytes(raw)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(importer.RAW_RESULT_NAME, raw)
        archive.writestr(
            importer.RAW_RECEIPT_NAME,
            f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode(),
        )
    return digest


def checkpoint_identity(label: str) -> dict:
    update = {"half": 50, "final": 100}[label]
    return {
        "label": label,
        "update": update,
        "checkpoint": {
            "file": f"winner_v12_calibrator_{label}.npz",
            "sha256": "1" * 64,
            "bytes": 1,
        },
        "onnx": {
            "file": f"winner_v12_calibrator_{label}.onnx",
            "sha256": "2" * 64,
            "bytes": 1,
            "inputs": [
                {"name": "obs", "shape": [1, 115]},
                {"name": "previous_action", "shape": [1, 14]},
                {"name": "h_in", "shape": [1, 64]},
            ],
            "outputs": [
                {"name": "calibration_actions", "shape": [1, 14]},
                {"name": "previous_action_out", "shape": [1, 14]},
                {"name": "h_out", "shape": [1, 64]},
            ],
            "abi_exact": True,
            "all_initializers_finite": True,
            "all_chain_outputs_finite": True,
            "training_only_tensors_absent": True,
            "jax_onnx_max_abs_error": 0.0,
            "jax_onnx_at_most_1e_7": True,
            "previous_action_out_equals_action_bit_exact": True,
        },
        "receipt": {
            "file": f"winner_v12_calibrator_{label}_receipt.json",
            "sha256": "3" * 64,
            "bytes": 1,
        },
    }


def valid_bound_result(importer) -> tuple[dict, dict]:
    training_attribution = {
        "repository": "RobVanProd/open-duck-mini-rdkx5",
        "github_run_id": 29808732634,
        "github_run_attempt": 1,
        "github_run_head_sha": "a" * 40,
        "github_artifact_id": 123,
        "github_artifact_name": (
            "winner-v12-full-calibrator-training-29808732634"
        ),
        "github_artifact_digest": f"sha256:{'b' * 64}",
    }
    result = {
        "schema_version": "winner_v12.full_calibrator_training_artifact_check.v1",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK",
        "decision": "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY",
        "checks": {name: True for name in importer.EXPECTED_CHECKS},
        "failed_checks": [],
        "artifact_zip": {
            "path": "/tmp/winner-v12-full-calibrator-training.zip",
            "sha256": "b" * 64,
            "bytes": 1,
            "member_count": 415,
        },
        "repository_attribution": training_attribution,
        "training_result_sha256": "c" * 64,
        "verified_checkpoints": {
            "half": checkpoint_identity("half"),
            "final": checkpoint_identity("final"),
        },
        "parameter_deltas": {
            "stage1": [{"key": "a", "changed": True, "max_abs_delta": 1.0}],
            "stage2": [{"key": "b", "changed": True, "max_abs_delta": 1.0}],
        },
        "optimizer_moments": {
            "stage1": [{"key": "a", "m_nonzero": True, "v_nonzero": True}],
            "stage2": [{"key": "b", "m_nonzero": True, "v_nonzero": True}],
        },
        "execution": {
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "artifact_verification_only": True,
            "pass_authorizes_only": (
                "the separately frozen 124-cell calibrator support/context gate"
            ),
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "robot_clearance": False,
        },
        "limitation": (
            "per-update episode receipts are represented by immutable SHA-256 values "
            "in each metric row; raw per-update episode payloads were not retained by "
            "the frozen trainer"
        ),
    }
    launch = {
        "repository_attribution": training_attribution,
        "expected_hashes": {
            "artifact_zip_sha256": "b" * 64,
            "training_result_sha256": "c" * 64,
        },
    }
    return result, launch


def test_reads_exact_two_file_verification_artifact(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "verification.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_verification_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_verification_artifact_member(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "extra.zip"
    write_artifact(archive)
    with zipfile.ZipFile(archive, "a") as stream:
        stream.writestr("extra", b"unexpected")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_verification_artifact(archive)


def test_rejects_symlink_verification_artifact_member(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo(importer.RAW_RESULT_NAME)
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    receipt = "0" * 64 + f"  /tmp/{importer.RAW_RESULT_NAME}\n"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(link, "target")
        stream.writestr(importer.RAW_RECEIPT_NAME, receipt)
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_verification_artifact(archive)


def test_verification_attribution_is_exact() -> None:
    importer = load_importer()
    result = importer.verification_attribution(
        run_id=42,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=73,
        artifact_name="winner-v12-full-calibrator-training-artifact-check-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert result["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert result["github_artifact_id"] == 73


def test_raw_result_binds_to_exact_frozen_training_launch() -> None:
    importer = load_importer()
    result, launch = valid_bound_result(importer)
    importer.validate_result_binding(result, launch)


@pytest.mark.parametrize(
    "mutation",
    ["training_run", "training_zip", "training_result", "missing_check"],
)
def test_raw_result_rejects_frozen_launch_or_check_drift(mutation: str) -> None:
    importer = load_importer()
    result, launch = valid_bound_result(importer)
    if mutation == "training_run":
        result["repository_attribution"] = {
            **result["repository_attribution"],
            "github_run_id": 1,
            "github_artifact_name": "winner-v12-full-calibrator-training-1",
        }
    elif mutation == "training_zip":
        launch["expected_hashes"]["artifact_zip_sha256"] = "d" * 64
    elif mutation == "training_result":
        launch["expected_hashes"]["training_result_sha256"] = "d" * 64
    else:
        result["checks"].pop(next(iter(importer.EXPECTED_CHECKS)))
    with pytest.raises(ValueError):
        importer.validate_result_binding(copy.deepcopy(result), copy.deepcopy(launch))


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("run_attempt", 2),
        ("run_head_sha", "a" * 39),
        ("artifact_id", 0),
        ("artifact_name", "wrong"),
        ("artifact_digest", f"sha256:{'c' * 64}"),
    ],
)
def test_verification_attribution_rejects_drift(key: str, value: object) -> None:
    importer = load_importer()
    arguments = {
        "run_id": 42,
        "run_attempt": 1,
        "run_head_sha": "a" * 40,
        "artifact_id": 73,
        "artifact_name": "winner-v12-full-calibrator-training-artifact-check-42",
        "artifact_digest": f"sha256:{'b' * 64}",
        "artifact_zip_sha256": "b" * 64,
    }
    arguments[key] = value
    with pytest.raises(ValueError, match="attribution"):
        importer.verification_attribution(**arguments)


def test_expected_check_names_match_verifier_source() -> None:
    importer = load_importer()
    source = (
        ROOT / "tools/check_winner_v12_full_calibrator_training_artifact.py"
    ).read_text(encoding="utf-8")
    assert len(importer.EXPECTED_CHECKS) == 22
    for name in importer.EXPECTED_CHECKS:
        assert f'"{name}"' in source
