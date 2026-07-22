from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools/import_winner_v24_baseline_anchored_one_update_result_v2.py"
RESULT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_result_v2.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_one_update_import_v2", WRAPPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_path_correction_is_one_variable_and_hash_bound() -> None:
    module = load()
    value = module.validate_correction()
    assert set(value["correction"]["actual_members"]) == module.EXPECTED_PATHS
    assert value["authority"]["new_workflow_run_authorized"] is False
    assert value["authority"]["optimizer_or_training_authorized"] is False


def test_wrapper_preserves_frozen_result_validator() -> None:
    module = load()
    corrected = module.load_corrected_importer()
    assert corrected.OUTPUT_JSON == RESULT
    assert Path(corrected.__file__).resolve() == WRAPPER.resolve()
    assert corrected.validate_result.__module__ == "winner_v24_one_update_frozen_importer"


def test_corrected_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    import json

    module = load()
    corrected = module.load_corrected_importer()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    corrected.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1
