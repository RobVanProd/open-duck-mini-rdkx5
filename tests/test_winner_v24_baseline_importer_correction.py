from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools/import_winner_v24_baseline_anchored_cpu_result_v2.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_import_v2", WRAPPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_correction_is_one_variable_and_hash_bound() -> None:
    module = load()
    value = module.validate_correction()
    assert value["correction"]["all_other_import_validation_unchanged"] is True
    assert value["authority"]["new_workflow_run_authorized"] is False
    assert value["authority"]["optimizer_or_training_authorized"] is False


def test_wrapper_changes_only_importer_key_inventory() -> None:
    module = load()
    corrected = module.load_corrected_importer()
    assert set(corrected.GRADIENT_KEYS) == module.CORRECTED_GRADIENT_KEYS
    assert set(corrected.RECURRENT_KEYS) == module.CORRECTED_RECURRENT_KEYS
    assert Path(corrected.__file__).resolve() == WRAPPER.resolve()
    assert corrected.RAW_RESULT_NAME == "winner-v24-baseline-anchored-cpu-result.json"
    assert corrected.RAW_RECEIPT_NAME == "winner-v24-baseline-anchored-cpu-result.sha256"
