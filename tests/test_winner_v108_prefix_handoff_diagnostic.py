from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_winner_v108_prefix_handoff_diagnostic import (  # noqa: E402
    select_attribution,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v108_preregistration_freezes_the_four_cell_no_prefix_control() -> None:
    path = (
        ROOT / "outputs/analysis/winner_v108_prefix_handoff_preregistration.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "ef0dd3b94c8ebb2ce1d3434e153ab454ae8852d2c9d507e708cbfa9a4f3bbcd7"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
    )
    assert payload["failed_checks"] == []
    assert payload["matrix"]["cells"] == 4
    assert payload["matrix"]["sha256"] == (
        "3d32af63e21da7453685ac582b95e405ec96e6268fb8ece02f1f8acf6d6e49d0"
    )
    assert {
        row["command_x_m_s"] for row in payload["matrix"]["rows"]
    } == {0.0, 0.074, 0.077, 0.08}
    assert all(
        row["calibration_ticks"] == 0
        and row["home_return_ticks"] == 0
        for row in payload["matrix"]["rows"]
    )
    assert payload["authority"]["formal_behavior_cells_authorized"] == 4
    assert payload["authority"]["hosted_training_authorized"] is False
    assert payload["authority"]["robot_clearance"] is False


def test_v108_preregistration_proves_step_zero_graph_action_equivalence() -> None:
    payload = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v108_prefix_handoff_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    equivalence = payload["graph_equivalence"]
    assert equivalence == {
        "cases": 256,
        "exact": True,
        "maximum_context_action_effect": 0.0,
        "maximum_hidden_action_effect": 0.0,
        "maximum_source_to_expanded_action_error": 0.0,
        "maximum_source_to_expanded_previous_action_error": 0.0,
    }


def test_v108_attribution_requires_both_control_pass_and_graph_equivalence() -> None:
    selected = select_attribution(
        all_source_cells_pass=True,
        graph_equivalence_exact=True,
        v107_expanded_initial_passing_cells=1,
    )
    assert selected["status"] == "PREFIX_PHYSICAL_STATE_HANDOFF_ATTRIBUTED"
    assert selected["selected_causal_boundary"] == (
        "CALIBRATION_PREFIX_PHYSICAL_STATE_HANDOFF"
    )

    for values in (
        (False, True, 1),
        (True, False, 1),
        (True, True, 4),
    ):
        held = select_attribution(
            all_source_cells_pass=values[0],
            graph_equivalence_exact=values[1],
            v107_expanded_initial_passing_cells=values[2],
        )
        assert held["status"] == "BASELINE_CONTROL_DID_NOT_ISOLATE_PREFIX"
