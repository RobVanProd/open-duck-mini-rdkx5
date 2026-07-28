from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t86_preregisters_unchanged_full_sequential_r2() -> None:
    value = load("t86_rolling_midpoint_r2_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T86_ROLLING_MIDPOINT_SEQUENTIAL_R2"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["t85_persistent_nominal_all_sixteen_green"]
    assert value["checks"]["t85_exact_two_rolling_exports"]
    assert [item["checkpoint_id"] for item in value["policies"]] == [
        "T84_ROLLING_HALF",
        "T84_ROLLING_FINAL",
    ]
    assert len(value["conditions"]) == 20
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["cells_per_condition"] == 16
    assert value["matrix"]["strictly_sequential_conditions"]
    assert value["matrix"]["stop_after_first_failed_condition"]
    assert value["matrix"]["both_checkpoints_required"]
    assert not value["matrix"]["checkpoint_cherry_pick"]
    assert not value["matrix"]["reuse_nominal_evidence"]
    assert value["decision_rule"]["no_retry"]
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["authority"]["one_sequential_cpu_r2_matrix"]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t86_result_obeys_sequential_stop_if_present() -> None:
    path = ANALYSIS / "t86_rolling_midpoint_r2_result.json"
    if not path.is_file():
        pytest.skip("formal T86 R2 result has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["completed_cells"] == (
        16 * summary["completed_conditions"]
    )
    assert summary["green_cells"] <= summary["completed_cells"]
    if value["status"].startswith("PASS_"):
        assert summary["completed_conditions"] == 20
        assert summary["completed_cells"] == 320
        assert summary["green_cells"] == 320
        assert summary["first_failed_condition"] is None
        assert value["authority"][
            "gate5_deployment_readiness_package_preregistration"
        ]
    else:
        assert summary["completed_conditions"] <= 20
        assert summary["first_failed_condition"] is not None
        assert not value["authority"][
            "gate5_deployment_readiness_package_preregistration"
        ]
    assert not value["authority"]["gate5_hardware"]
    assert not value["authority"]["rdkx5_or_robot"]
