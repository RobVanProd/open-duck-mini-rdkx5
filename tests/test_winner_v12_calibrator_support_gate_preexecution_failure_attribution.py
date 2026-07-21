from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/"
    "winner_v12_calibrator_support_gate_preexecution_failure_attribution.json"
)


def load() -> dict:
    return json.loads(ATTRIBUTION.read_text(encoding="utf-8"))


def test_failed_attempt_is_closed_before_any_behavior_cell() -> None:
    result = load()
    assert result["status"] == (
        "ATTRIBUTED_WINNER_V12_SUPPORT_GATE_PREEXECUTION_FAILURE"
    )
    assert result["decision"] == (
        "AUTHORIZE_ONE_PROVENANCE_BOUND_INPUT_BINDING_CORRECTION_ONLY"
    )
    assert result["attempt"] == {
        "artifact_count": 0,
        "commit": "b2231429cd3d0618cf03c8f68a1414f3cac6f650",
        "conclusion": "failure",
        "github_job_id": 88585511382,
        "github_run_attempt": 1,
        "github_run_id": 29815413956,
        "github_run_url": (
            "https://github.com/RobVanProd/open-duck-mini-rdkx5/"
            "actions/runs/29815413956"
        ),
    }
    assert result["execution"] == {
        "formal_support_cells_completed": 0,
        "heldout_repeat_cells_completed": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert result["evidence"]["result_artifact_available"] is False
    assert result["checks"] and all(result["checks"].values())
    assert result["failed_checks"] == []


def test_correction_is_binding_only_and_keeps_robot_blocked() -> None:
    result = load()
    assert "calibrator_training_preregistration.json" in result["root_cause"][
        "correction"
    ]
    assert result["authority"] == {
        "locomotion_training": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }
