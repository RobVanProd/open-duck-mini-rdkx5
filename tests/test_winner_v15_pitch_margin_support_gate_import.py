from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v15_pitch_margin_support_gate_result.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v15_pitch_margin_gate_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_artifact(path: Path, raw: bytes = b"{}") -> str:
    importer = load()
    digest = importer.sha256_bytes(raw)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(importer.RAW_RESULT_NAME, raw)
        archive.writestr(importer.RAW_RECEIPT_NAME, f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode())
    return digest


def test_reads_exact_two_member_artifact(tmp_path: Path) -> None:
    importer = load()
    archive = tmp_path / "gate.zip"
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


def test_repository_attribution_is_exact() -> None:
    importer = load()
    value = importer.repository_attribution(
        run_id=42, run_attempt=1, run_head_sha="a" * 40, artifact_id=73,
        artifact_name="winner-v15-pitch-margin-support-gate-42",
        artifact_digest=f"sha256:{'b' * 64}", artifact_zip_sha256="b" * 64,
    )
    assert value["repository"] == importer.EXPECTED_REPOSITORY


def test_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "--formal-gate-authorized" not in source
    assert "--hardware-authorized" not in source
    assert "onnxruntime" not in source
    assert "import jax" not in source
