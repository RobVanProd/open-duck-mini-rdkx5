from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v12_calibrator_support_gate_result.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v12_gate_import", IMPORTER)
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


def checkpoint_result(label: str) -> dict:
    checks = {
        "all_16_heldout_contexts_separate": True,
        "all_32_heldout_repeats_bit_exact": True,
        "all_jax_onnx_hidden_errors_at_most_1e_7": True,
        "all_previous_action_chains_exact": True,
        "all_support_cells_pass": True,
        "exact_124_main_cells": True,
        "learned_prediction_beats_constant_per_plant": True,
    }
    return {
        "label": label,
        "update": {"half": 50, "final": 100}[label],
        "checkpoint_sha256": "a" * 64,
        "onnx_sha256": "b" * 64,
        "core_model_plant_cells": [{} for _ in range(112)],
        "sensor_transport_plant_cells": [{} for _ in range(12)],
        "heldout_repeatability": [{"bit_exact": True} for _ in range(32)],
        "heldout_context_separation": [{} for _ in range(16)],
        "heldout_prediction": {"P30": {}, "P31_34": {}},
        "checks": checks,
        "failed_checks": [],
    }


def valid_result(importer) -> dict:
    return {
        "schema_version": "winner_v12.calibrator_support_gate_result.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE",
        "decision": "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY",
        "checks": {
            "all_248_main_cells_pass": True,
            "both_checkpoints_evaluated": True,
            "formal_cell_count_exact": True,
        },
        "failed_checks": [],
        "sources": {
            "preregistration_lf_sha256": importer.lf_sha256(
                importer.PREREGISTRATION
            ),
            "calibrator_design_lf_sha256": importer.lf_sha256(
                importer.CALIBRATOR_DESIGN
            ),
            "domain_lf_sha256": importer.lf_sha256(importer.DOMAIN),
            "training_runner_lf_sha256": importer.lf_sha256(
                importer.TRAINING_RUNNER
            ),
            "gate_runner_lf_sha256": importer.lf_sha256(importer.RUNNER),
        },
        "checkpoint_results": [
            checkpoint_result("half"),
            checkpoint_result("final"),
        ],
        "execution": {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate response-conditioned locomotion-training preregistration"
            ),
        },
    }


def test_reads_exact_formal_result_artifact(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "formal.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_result_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_formal_result_member(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "extra.zip"
    write_artifact(archive)
    with zipfile.ZipFile(archive, "a") as stream:
        stream.writestr("extra", b"unexpected")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(archive)


def test_rejects_symlink_formal_result_member(tmp_path: Path) -> None:
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
        importer.read_result_artifact(archive)


def test_repository_attribution_is_exact() -> None:
    importer = load_importer()
    result = importer.repository_attribution(
        run_id=42,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=73,
        artifact_name="winner-v12-calibrator-support-gate-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert result["repository"] == "RobVanProd/open-duck-mini-rdkx5"


def test_validates_complete_pass_population_and_authority() -> None:
    importer = load_importer()
    importer.validate_result(valid_result(importer))


def test_rejects_incomplete_formal_population() -> None:
    importer = load_importer()
    result = valid_result(importer)
    result["checkpoint_results"][0]["core_model_plant_cells"].pop()
    with pytest.raises(ValueError, match="population"):
        importer.validate_result(result)


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
def test_repository_attribution_rejects_drift(key: str, value: object) -> None:
    importer = load_importer()
    arguments = {
        "run_id": 42,
        "run_attempt": 1,
        "run_head_sha": "a" * 40,
        "artifact_id": 73,
        "artifact_name": "winner-v12-calibrator-support-gate-42",
        "artifact_digest": f"sha256:{'b' * 64}",
        "artifact_zip_sha256": "b" * 64,
    }
    arguments[key] = value
    with pytest.raises(ValueError, match="attribution"):
        importer.repository_attribution(**arguments)


def test_importer_cannot_run_training_or_hardware() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "--formal-gate-authorized" not in source
    assert "--hardware-authorized" not in source
    assert "onnxruntime" not in source
