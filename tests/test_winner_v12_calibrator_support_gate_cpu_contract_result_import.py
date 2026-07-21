from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = (
    ROOT / "tools/import_winner_v12_calibrator_support_gate_cpu_contract_result.py"
)


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v12_zero_cell_import", IMPORTER)
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


def test_reads_exact_zero_cell_result_artifact(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "result.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_result_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_zero_cell_result_member(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "extra.zip"
    write_artifact(archive)
    with zipfile.ZipFile(archive, "a") as stream:
        stream.writestr("extra", b"unexpected")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(archive)


def test_rejects_symlink_zero_cell_result_member(tmp_path: Path) -> None:
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
        artifact_name="winner-v12-calibrator-support-gate-cpu-contract-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert result["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert result["github_artifact_id"] == 73


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
        "artifact_name": "winner-v12-calibrator-support-gate-cpu-contract-42",
        "artifact_digest": f"sha256:{'b' * 64}",
        "artifact_zip_sha256": "b" * 64,
    }
    arguments[key] = value
    with pytest.raises(ValueError, match="attribution"):
        importer.repository_attribution(**arguments)


def test_importer_has_no_formal_gate_surface() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "--formal-gate-authorized" not in source
    assert "run_winner_v12_calibrator_support_gate" not in source
