from __future__ import annotations

import json
import math
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest

from patches import t202_predicted_roll_risk as t202


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def roll_quaternion(angle_rad: float) -> jnp.ndarray:
    half = angle_rad / 2.0
    return jnp.asarray(
        [math.cos(half), math.sin(half), 0.0, 0.0],
        dtype=jnp.float32,
    )


def test_quaternion_roll_matches_frozen_evaluator_convention() -> None:
    for angle in (-1.2, -0.25, 0.0, 0.4, 1.1):
        actual = float(
            t202.quaternion_wxyz_to_roll(roll_quaternion(angle))
        )
        assert actual == pytest.approx(angle, abs=1.0e-6)


def test_predicted_roll_risk_uses_exact_frozen_horizon() -> None:
    risk = t202.predicted_roll_risk_rad(
        roll_quaternion(0.2),
        jnp.asarray(-1.0, dtype=jnp.float32),
    )
    assert float(risk) == pytest.approx(0.12, abs=1.0e-6)


def test_envelope_is_zero_cost_and_exceedance_is_quadratic() -> None:
    envelope = t202.PASSING_ENVELOPE_RAD
    assert float(t202.roll_risk_cost(envelope)) == 0.0
    assert float(t202.roll_risk_cost(envelope - 0.1)) == 0.0
    expected = t202.ROLL_RISK_SCALE * 0.1**2
    assert float(t202.roll_risk_cost(envelope + 0.1)) == pytest.approx(
        expected, rel=1.0e-5
    )


def test_scale_is_derived_from_both_frozen_failures() -> None:
    expected = (
        t202.ALIVE_REWARD_PER_TICK
        * t202.FROZEN_FAILURE_EXCEEDANCE_ROWS
        / t202.FROZEN_FAILURE_SQUARED_EXCESS_INTEGRAL
    )
    assert t202.ROLL_RISK_SCALE == pytest.approx(expected)
    weighted_mean = (
        t202.ROLL_RISK_SCALE
        * t202.FROZEN_FAILURE_SQUARED_EXCESS_INTEGRAL
        / t202.FROZEN_FAILURE_EXCEEDANCE_ROWS
    )
    assert weighted_mean == pytest.approx(t202.ALIVE_REWARD_PER_TICK)


def test_cost_is_subtracted_outside_original_reward() -> None:
    original = jnp.asarray(0.3, dtype=jnp.float32)
    cost = jnp.asarray(0.5, dtype=jnp.float32)
    assert float(t202.curriculum_reward(original, cost)) == pytest.approx(
        -0.2
    )


def test_source_patch_is_default_off_and_after_reward_clip() -> None:
    text = (
        ROOT / "patches" / "winner_t202_predicted_roll_risk.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t202_predicted_roll_risk=False" in text
    assert "objective=original_clipped_reward_minus_cost" in text
    reward_clip_index = text.index(
        "reward = jp.clip(sum(rewards.values()) * self.dt"
    )
    assert reward_clip_index < text.index(
        "if self._config.winner_t202_predicted_roll_risk:",
        reward_clip_index,
    )
    assert "reward = t202.curriculum_reward(reward, roll_risk_cost)" in text
    assert "winner_t193" not in text


def test_t202_preregistration_contract_when_present() -> None:
    path = ANALYSIS / "t202_predicted_roll_risk_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["source"] == "T170_HALF"
    assert value["mechanism"]["deployment_graph_change"] is False
    assert value["authority"]["hosted_training"] is False


def test_t202_result_contract_when_present() -> None:
    path = ANALYSIS / "t202_predicted_roll_risk_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert (
            value["status"]
            == "HOLD_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
        )
        return
    assert value["status"] == "PASS_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
    assert (
        value["decision"]
        == "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_PREREGISTRATION_ONLY"
    )
    assert value["execution"]["optimizer_steps"] == 1024
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
