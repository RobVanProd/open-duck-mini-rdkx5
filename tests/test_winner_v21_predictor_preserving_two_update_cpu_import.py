from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v21_predictor_preserving_two_update_result.py"
RESULT = ROOT / "outputs/analysis/winner_v21_predictor_preserving_two_update_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v21_two_update_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_is_exact_and_binary_outputs_are_bound() -> None:
    module = load()
    assert module.RAW_RESULT_NAME.endswith("result.json")
    assert module.RAW_RECEIPT_NAME.endswith("result.sha256")
    assert module.SNAPSHOT_NAME.endswith("update_002.npz")
    assert module.GRAPH_NAME.endswith("update_002.onnx")


def test_repository_attribution_requires_first_attempt_and_digest_binding() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v21-predictor-preserving-two-update-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert value["github_run_attempt"] == 1


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["artifact_zip_sha256"] == value[
        "repository_attribution"
    ]["github_artifact_digest"].removeprefix("sha256:")


def test_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "import jax" not in source
    assert "onnxruntime" not in source
    assert "--hardware-authorized" not in source
