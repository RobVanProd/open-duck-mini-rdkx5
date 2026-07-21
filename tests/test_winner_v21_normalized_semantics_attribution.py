from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v21_normalized_semantics_attribution.py"
RESULT = ROOT / "outputs/analysis/winner_v21_normalized_semantics_attribution.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v21_semantics_attribution", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_attribution_is_rederived_from_committed_evidence() -> None:
    module = load()
    actual = json.loads(RESULT.read_text(encoding="utf-8"))
    assert actual == module.build_payload()
    assert actual["status"] == "PASS_WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION"


def test_coordinate_mismatch_is_selected_without_reclassifying_v21() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    findings = value["findings"]
    assert findings["v13_auxiliary_head_outputs_normalized_coordinates"]
    assert findings["v21_training_compared_normalized_output_as_if_raw"]
    assert findings["v21_gate_compared_normalized_output_as_if_raw"]
    assert findings["completed_v21_result_remains_a_hold"]
    assert not findings["flat_transport_equation_selected"]


def test_physical_hold_and_authority_remain_closed() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["support_gate"]["checkpoints"]
    assert (half["passing_support_cells"], final["passing_support_cells"]) == (109, 108)
    assert half["terminal_failed_check_counts"] == {"roll_pitch": 15}
    assert final["terminal_failed_check_counts"] == {"roll_pitch": 16}
    assert value["authority"]["optimizer_updates_authorized_now"] == 0
    assert not value["authority"]["locomotion_training_authorized"]
    assert not value["authority"]["robot_clearance"]
