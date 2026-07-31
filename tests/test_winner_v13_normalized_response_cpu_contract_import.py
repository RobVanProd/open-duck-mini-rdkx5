from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_normalized_response_cpu_contract.py"
RAW_RESULT = Path(
    r"D:\open-duck-mini-rdkx5-policy\winner-v13\run-29818644996\winner-v13-normalized-response-cpu-result.json"
)
IMPORTED_RESULT = (
    ROOT / "outputs/analysis/winner_v13_normalized_response_cpu_contract_result.json"
)


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v13_cpu_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validates_recovered_cpu_result_when_available() -> None:
    importer = load_importer()
    if not RAW_RESULT.is_file():
        pytest.skip("external recovered result is not part of the repository")
    importer.validate_result(json.loads(RAW_RESULT.read_text(encoding="utf-8")))


def test_committed_import_preserves_raw_result_and_exact_attribution() -> None:
    importer = load_importer()
    payload = json.loads(IMPORTED_RESULT.read_text(encoding="utf-8"))
    attribution = payload.pop("repository_attribution")
    importer.validate_result(payload)
    assert attribution["github_run_id"] == 29818644996
    assert attribution["github_run_attempt"] == 1
    assert attribution["github_artifact_id"] == 8490421077
    assert attribution["artifact_zip_sha256"] == (
        "c28766ffa8a2e43205301fc13a604214046b80200f6aeba0700206f025894bbe"
    )
    assert attribution["graph_artifact_sha256"] == (
        "cc564314a347257da114c5db81a24a592ea8fb12629b1b20632f7064a9483952"
    )


def test_artifact_reader_requires_result_receipt_and_graph(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "valid.zip"
    raw = b'{"status":"PASS"}\n'
    digest = importer.sha256_bytes(raw)
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(importer.RAW_RESULT_NAME, raw)
        stream.writestr(
            importer.RAW_RECEIPT_NAME,
            f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode(),
        )
        stream.writestr(importer.RAW_GRAPH_NAME, b"graph")
    observed = importer.read_result_artifact(archive)
    assert observed == (
        raw,
        f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode(),
        b"graph",
    )


def test_artifact_reader_rejects_extra_and_symlink_members(tmp_path: Path) -> None:
    importer = load_importer()
    extra = tmp_path / "extra.zip"
    with zipfile.ZipFile(extra, "w") as stream:
        for name in (
            importer.RAW_RESULT_NAME,
            importer.RAW_RECEIPT_NAME,
            importer.RAW_GRAPH_NAME,
            "extra",
        ):
            stream.writestr(name, b"x")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(extra)

    unsafe = tmp_path / "unsafe.zip"
    link = zipfile.ZipInfo(importer.RAW_GRAPH_NAME)
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(unsafe, "w") as stream:
        stream.writestr(importer.RAW_RESULT_NAME, b"{}")
        stream.writestr(importer.RAW_RECEIPT_NAME, b"bad")
        stream.writestr(link, b"target")
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_result_artifact(unsafe)


def test_repository_attribution_is_exact() -> None:
    importer = load_importer()
    value = importer.repository_attribution(
        run_id=42,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=73,
        artifact_name="winner-v13-normalized-response-cpu-contract-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"


def test_importer_has_no_execution_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "--zero-cell-contract-authorized" not in source
    assert "--hardware-authorized" not in source
    assert "onnxruntime" not in source
