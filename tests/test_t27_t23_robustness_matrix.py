from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "tools"))

from run_t27_t23_robustness_matrix import matrix_plan  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t27_matrix_plan_is_exact_and_condition_major() -> None:
    conditions = [
        {"condition_index": 1, "id": "A", "override": {"x": 1}},
        {"condition_index": 2, "id": "B", "override": {"x": 2}},
    ]
    policies = [
        {"checkpoint_id": "H", "step": 1, "sha256": "h"},
        {"checkpoint_id": "F", "step": 2, "sha256": "f"},
    ]
    fits = [
        {"fit_id": "p30", "sha256": "30"},
        {"fit_id": "p31", "sha256": "31"},
    ]
    rows = matrix_plan(conditions, policies, fits, [0.0, 0.08], 7)
    assert len(rows) == 16
    assert [row["condition_id"] for row in rows[:8]] == ["A"] * 8
    assert [row["condition_id"] for row in rows[8:]] == ["B"] * 8
    assert rows[0]["checkpoint_id"] == "H"
    assert rows[4]["checkpoint_id"] == "F"
    assert rows[0]["duration_ticks"] == 600


def test_t27_runner_contract_has_zero_formal_cells() -> None:
    value = load("t27_t23_robustness_runner_contract.json")
    assert value["status"] == (
        "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["unscored_support_ticks"] == 250
    assert value["execution"]["scored_contract_ticks"] == 1
    assert value["authority"]["formal_robustness_execution_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_t27_preregistration_freezes_sequential_320_cell_ceiling() -> None:
    value = load("t27_t23_robustness_matrix_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["conditions"]) == 20
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["cells_per_condition"] == 16
    assert value["matrix"]["strictly_sequential_conditions"] is True
    assert value["matrix"]["stop_after_first_failed_condition"] is True
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["authority"]["additional_training_authorized"] is False
    assert value["authority"]["gate5_hardware_authorized"] is False
