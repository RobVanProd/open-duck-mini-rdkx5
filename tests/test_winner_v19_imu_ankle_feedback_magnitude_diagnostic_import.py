from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = (
    ROOT / "tools/import_winner_v19_imu_ankle_feedback_magnitude_diagnostic_result.py"
)
RESULT = (
    ROOT / "outputs/analysis/winner_v19_imu_ankle_feedback_magnitude_diagnostic_result.json"
)


def load():
    spec = importlib.util.spec_from_file_location("winner_v19_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_artifact(path: Path, raw: bytes = b"{}") -> str:
    importer = load()
    digest = importer.sha256_bytes(raw)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(importer.RAW_RESULT_NAME, raw)
        archive.writestr(
            importer.RAW_RECEIPT_NAME,
            f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode(),
        )
    return digest


def test_reads_exact_two_member_artifact(tmp_path: Path) -> None:
    importer = load()
    archive = tmp_path / "result.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_result_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_or_symlink_members(tmp_path: Path) -> None:
    importer = load()
    extra = tmp_path / "extra.zip"
    write_artifact(extra)
    with zipfile.ZipFile(extra, "a") as archive:
        archive.writestr("extra", b"unexpected")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(extra)
    symlink = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo(importer.RAW_RESULT_NAME)
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(symlink, "w") as archive:
        archive.writestr(link, "target")
        archive.writestr(importer.RAW_RECEIPT_NAME, "0" * 64)
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_result_artifact(symlink)


def test_imported_result_falsifies_insufficient_wrapper_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
    )
    assert value["decision"] == (
        "INSUFFICIENT_FEEDBACK_AUTHORITY_FALSIFIED_STOP_WITH_ATTRIBUTION"
    )
    assert value["failed_validity_checks"] == []
    assert value["full_pass_candidates"] == []
    assert value["selected_direction"] is None
    summaries = value["intervention_summary"]
    assert [
        summaries[name]["half_failure_count"]
        for name in ("CONSTANT_003", "CONSTANT_006", "CONSTANT_009")
    ] == [8, 12, 12]
    assert [
        summaries[name]["final_failure_count"]
        for name in ("CONSTANT_003", "CONSTANT_006", "CONSTANT_009")
    ] == [6, 12, 12]
    assert [
        summaries[name]["half_failure_count"]
        for name in ("TILT_RATE_003", "TILT_RATE_006", "TILT_RATE_009")
    ] == [10, 10, 10]
    assert [
        summaries[name]["final_failure_count"]
        for name in ("TILT_RATE_003", "TILT_RATE_006", "TILT_RATE_009")
    ] == [10, 8, 8]
    assert value["repository_attribution"]["github_run_id"] == 29850348125
    assert value["repository_attribution"]["github_artifact_id"] == 8503113171
    assert value["authority"]["robot_clearance"] is False


def test_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "onnxruntime" not in source
    assert "import jax" not in source
    assert "--hardware-authorized" not in source
