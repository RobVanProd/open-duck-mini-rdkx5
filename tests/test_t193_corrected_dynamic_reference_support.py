from __future__ import annotations

import json
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest

from patches import t193_corrected_dynamic_reference_support as t193


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def reference(left: float, right: float) -> jnp.ndarray:
    value = jnp.zeros(34, dtype=jnp.float32)
    return value.at[32:34].set(jnp.asarray([left, right]))


def test_reference_contact_channels_select_exact_support_only() -> None:
    assert np.array_equal(
        np.asarray(t193.reference_support_sides(reference(1.0, 0.0))),
        np.asarray([True, False]),
    )
    assert np.array_equal(
        np.asarray(t193.reference_support_sides(reference(0.0, 1.0))),
        np.asarray([False, True]),
    )
    for row in (reference(0.0, 0.0), reference(1.0, 1.0)):
        assert not np.any(np.asarray(t193.reference_support_sides(row)))


def test_matches_left_and_right_without_phase_heuristic() -> None:
    left = t193.matched_support_sides(
        jnp.asarray([True, False]), reference(1.0, 0.0)
    )
    right = t193.matched_support_sides(
        jnp.asarray([False, True]), reference(0.0, 1.0)
    )
    assert np.array_equal(np.asarray(left), np.asarray([True, False]))
    assert np.array_equal(np.asarray(right), np.asarray([False, True]))
    assert not np.any(
        np.asarray(
            t193.matched_support_sides(
                jnp.asarray([False, True]), reference(1.0, 0.0)
            )
        )
    )


def test_perfect_reward_is_alive_derived_for_both_sides() -> None:
    gravity = jnp.asarray([0.0, 0.0, -1.0])
    gyro = jnp.zeros(3)
    for contact, row in (
        (jnp.asarray([True, False]), reference(1.0, 0.0)),
        (jnp.asarray([False, True]), reference(0.0, 1.0)),
    ):
        reward = t193.single_support_balance_reward(
            gravity, gyro, contact, row
        )
        assert float(reward) == pytest.approx(
            t193.ALIVE_REWARD_PER_TICK
        )


def test_nonmatching_or_nonsingle_reference_has_zero_reward() -> None:
    gravity = jnp.asarray([0.0, 0.0, -1.0])
    gyro = jnp.zeros(3)
    cases = (
        (jnp.asarray([False, True]), reference(1.0, 0.0)),
        (jnp.asarray([True, True]), reference(1.0, 0.0)),
        (jnp.asarray([True, False]), reference(1.0, 1.0)),
        (jnp.asarray([False, False]), reference(0.0, 1.0)),
    )
    for contact, row in cases:
        reward = t193.single_support_balance_reward(
            gravity, gyro, contact, row
        )
        assert float(reward) == 0.0


def test_objective_is_additive_without_new_scale() -> None:
    original = jnp.asarray(np.float32(0.3125))
    support = jnp.asarray(np.float32(0.25))
    value = t193.curriculum_reward(original, support)
    assert float(value) == pytest.approx(0.5625)


def test_source_patch_is_reference_driven_default_off() -> None:
    text = (
        ROOT
        / "patches"
        / "winner_t193_corrected_dynamic_reference_support.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t193_corrected_dynamic_reference_support=False" in text
    assert 'state.info["current_reference_motion"]' in text
    assert "reference_channels=32:34" in text
    assert "phase_heuristic=none" in text
    assert "winner_t55" not in text
    assert "prefix_ticks" not in text


def test_t193_preregistration_contract_when_present() -> None:
    path = (
        ANALYSIS
        / "t193_corrected_dynamic_reference_support_cpu_"
        "preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
        "CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["reference_contact_slice"] == [32, 34]
    assert value["mechanism"]["perfect_match_reward_per_tick"] == 0.4
    assert value["mechanism"]["phase_sign_heuristic"] is False
    assert value["mechanism"]["phase_freeze_or_prefix"] is False
    assert value["authority"]["hosted_training"] is False


def test_t193_result_contract_when_present() -> None:
    path = (
        ANALYSIS
        / "t193_corrected_dynamic_reference_support_cpu_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert (
            value["status"]
            == "HOLD_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
            "CPU_CONTRACT"
        )
        return
    assert (
        value["status"]
        == "PASS_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_CPU_CONTRACT"
    )
    assert (
        value["decision"]
        == "EARN_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution"]["optimizer_steps"] == 1024
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0


def test_t193b_recovery_contract_when_present() -> None:
    prereg_path = (
        ANALYSIS / "t193b_metric_namespace_recovery_preregistration.json"
    )
    if prereg_path.exists():
        value = json.loads(prereg_path.read_text(encoding="utf-8"))
        assert (
            value["status"]
            == "PREREGISTERED_T193B_METRIC_NAMESPACE_RECOVERY"
        )
        assert value["failed_checks"] == []
        assert value["authority"]["optimizer"] is False
        assert value["execution_now"]["simulator_transitions"] == 0
        assert value["execution_now"]["optimizer_steps"] == 0

    result_path = (
        ANALYSIS / "t193b_metric_namespace_recovery_result.json"
    )
    if not result_path.exists():
        return
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_T193B_METRIC_NAMESPACE_RECOVERY"
    assert (
        result["classification"]
        == "T193_CPU_HOLD_WAS_REPORTING_NAMESPACE_ONLY"
    )
    assert (
        result["decision"]
        == "EARN_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_"
        "PREREGISTRATION_ONLY"
    )
    assert result["failed_checks"] == []
    assert result["execution_now"]["optimizer_steps"] == 0
    assert result["execution_now"]["hosted_compute_units"] == 0
