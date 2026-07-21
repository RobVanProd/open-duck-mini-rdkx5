from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v21_gradient_composition_attribution.py"
RESULT = ROOT / "outputs/analysis/winner_v21_gradient_composition_attribution.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v21_gradient_attribution", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_attribution_is_rederived_and_does_not_relax_source_hold() -> None:
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value == module.build_payload()
    assert value["status"] == "PASS_WINNER_V21_GRADIENT_COMPOSITION_ATTRIBUTION"
    assert value["decision"] == "PREREGISTER_EXPLICITLY_COMPOSED_TWO_UPDATE_CPU_PROOF"
    assert value["source_hold"]["passing_checks"] == 16
    assert value["source_hold"]["total_checks"] == 17
    assert value["classification"]["threshold_relaxed"] is False
    assert value["classification"]["source_hold_relabelled_as_pass"] is False
    assert value["classification"]["rerun_of_source_contract_authorized"] is False
    assert value["authority"]["optimizer_updates_authorized_now"] == 0
