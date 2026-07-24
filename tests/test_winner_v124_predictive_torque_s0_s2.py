from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v124_predictive_torque_preregistration_is_frozen() -> None:
    path = (
        ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "61364c864ef3bf97d13df92a79645140a3918ecc8923f52810dd360f16b8042f"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
    )
    assert value["failed_checks"] == []
    assert value["pre_run_ruling"][
        "uniform_wrapper_satisfies_both_checkpoint_rule"
    ]
    assert value["execution_now"]["behavior_rollouts"] == 0
    assert not value["authority"]["s3_behavior_screen_authorized"]


def test_v124_ctrl_tolerance_amendment_reuses_frozen_bound() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v124_s0_ctrl_tolerance_amendment.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V124_S0_CTRL_TOLERANCE_AMENDMENT"
    )
    assert value["failed_checks"] == []
    assert value["correction"]["ctrl_applied_tolerance_rad"] == 6.0e-8
    assert value["correction"][
        "all_other_equations_thresholds_inputs_and_decisions_unchanged"
    ]


def test_v124_source_and_credit_close_but_reserve_box_fails() -> None:
    path = (
        ANALYSIS
        / "winner_v124_predictive_torque_s0_s2_compact_result.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "85f1313fe02a6feb2d4e34a94c07ff755c178c117470fe8e8b92cfe365b1bc29"
    )
    assert value["status"] == "HOLD_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
    assert value["s0"]["pass"]
    assert value["s1"]["pass"]
    assert not value["s2"]["pass"]
    assert value["s1"]["summary"]["v121_locally_preventable"] == 15
    assert value["s1"]["summary"]["v123_locally_preventable"] == 181
    assert value["s1"]["s1b"]["direct_credit_events"] == 37
    assert value["s1"]["s1b"]["zero_direct_credit_events"] == 147
    assert value["s1"]["s1b"]["fraction_removed_by_clipping"] > 0.98
    assert value["s2"]["summary"]["empty_intersections"] == 20048
    assert value["decision"]["status"] == (
        "CLOSE_V124_PREDICTIVE_TORQUE_BOX_WITHOUT_ROLLOUT"
    )
    assert value["execution"]["behavior_rollouts"] == 0
    assert value["execution"]["training_steps"] == 0
    assert not value["authority"]["s3_preregistration_authorized"]
    assert not value["authority"]["hosted_training_authorized"]
