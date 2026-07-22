from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v40_response_jacobian_invalidity_attribution.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v40_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_saved_result_audit_scope_is_exact() -> None:
    module = load()
    assert module.PLANTS == ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
    assert module.RESPONSE_HORIZON_TICKS == 8
    assert module.MAXIMUM_TERMINAL_FRINGE_TICKS == 2


def test_runner_is_saved_result_only_and_cannot_rerun_v39() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "Episode(" not in source
    assert "mj_step" not in source
    assert "bounded_action_numpy" not in source
    assert "np.linalg" not in source
    assert "--playground-root" not in source
    assert "--hardware-authorized" not in source
    assert '"simulation_cells": 0' in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"v39_rerun_authorized": False' in source


def test_analyze_cell_attributes_only_terminal_truncated_zero_columns() -> None:
    module = load()
    receipt = {
        "valid_ticks": 1,
        "terminal": {"tick": 1},
        "response": [0.2, 0.3],
        "action_sequence_sha256": "a" * 64,
    }
    perturbations = [
        {"axis": axis, "minus": receipt, "plus": dict(receipt)}
        for axis in range(3)
    ]
    row = {
        "plant": module.PLANTS[0],
        "terminal": {"tick": 2},
        "support_pass": False,
        "all_actions_bounded": True,
        "any_nonzero_action": True,
        "trace": [
            {"tick": 0, "planning": {"jacobian_rank": 2}},
            {"tick": 1, "planning": {
                "jacobian_rank": 0,
                "singular_values": [0.0, 0.0],
                "perturbations": perturbations,
            }},
            {"tick": 2, "planning": {
                "jacobian_rank": 0,
                "singular_values": [0.0, 0.0],
                "perturbations": perturbations,
            }},
        ],
    }
    result = module.analyze_cell(row, 10)
    assert result["first_rank_loss_tick"] == 1
    assert result["ticks_from_first_rank_loss_to_terminal"] == 1
    assert result["all_pre_loss_jacobians_full_row_rank"] is True
    assert result["all_rank_losses_in_terminal_fringe"] is True
    assert result["all_rank_losses_accounted_for_by_terminal_truncation"] is True
    assert result["source_terminated_earlier_than_v38"] is True
