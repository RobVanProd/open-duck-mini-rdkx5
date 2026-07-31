from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest

from patches import t55_dynamic_single_support_curriculum as t55


def test_phase_target_support_is_bilateral_and_deterministic() -> None:
    assert np.array_equal(
        np.asarray(t55.phase_target_support(jnp.asarray([1.0, 0.0]))),
        np.asarray([True, False]),
    )
    assert np.array_equal(
        np.asarray(t55.phase_target_support(jnp.asarray([0.0, -1.0]))),
        np.asarray([True, False]),
    )
    assert np.array_equal(
        np.asarray(t55.phase_target_support(jnp.asarray([0.0, 1.0]))),
        np.asarray([False, True]),
    )


def test_balance_reward_requires_correct_exact_single_support() -> None:
    gravity = jnp.asarray([0.0, 0.0, -1.0])
    gyro = jnp.zeros(3)
    left_phase = jnp.asarray([1.0, 0.0])
    right_phase = jnp.asarray([0.0, 1.0])
    left = float(
        t55.single_support_balance_reward(
            gravity, gyro, jnp.asarray([True, False]), left_phase
        )
    )
    right = float(
        t55.single_support_balance_reward(
            gravity, gyro, jnp.asarray([False, True]), right_phase
        )
    )
    assert left == pytest.approx(t55.ALIVE_REWARD_PER_TICK)
    assert right == pytest.approx(t55.ALIVE_REWARD_PER_TICK)
    for contact, phase in (
        ([True, True], left_phase),
        ([False, False], left_phase),
        ([False, True], left_phase),
        ([True, False], right_phase),
    ):
        reward = t55.single_support_balance_reward(
            gravity, gyro, jnp.asarray(contact), phase
        )
        assert float(reward) == 0.0
    assert np.array_equal(
        np.asarray(
            t55.matched_support_sides(
                jnp.asarray([True, False]),
                left_phase,
            )
        ),
        np.asarray([True, False]),
    )
    assert np.array_equal(
        np.asarray(
            t55.matched_support_sides(
                jnp.asarray([False, True]),
                right_phase,
            )
        ),
        np.asarray([False, True]),
    )


def test_gate_and_control_horizon_are_derived_exactly() -> None:
    predicted = t55.predicted_tilt_rad(
        jnp.asarray([0.0, 0.0, -1.0]),
        jnp.asarray(
            [
                t55.PITCH_ROLL_GATE_RAD / t55.CONTROL_HORIZON_S,
                0.0,
                0.0,
            ]
        ),
    )
    assert np.allclose(
        np.asarray(predicted),
        np.asarray([t55.PITCH_ROLL_GATE_RAD, 0.0]),
        atol=1e-7,
    )
    reward = t55.single_support_balance_reward(
        jnp.asarray([0.0, 0.0, -1.0]),
        jnp.asarray(
            [
                t55.PITCH_ROLL_GATE_RAD / t55.CONTROL_HORIZON_S,
                0.0,
                0.0,
            ]
        ),
        jnp.asarray([True, False]),
        jnp.asarray([1.0, 0.0]),
    )
    assert float(reward) == pytest.approx(
        t55.ALIVE_REWARD_PER_TICK * np.exp(-1.0),
        rel=1e-6,
    )


def test_curriculum_reward_is_default_off_exact() -> None:
    original = jnp.asarray(np.float32(0.3125))
    support = jnp.asarray(np.float32(0.25))
    disabled = t55.curriculum_reward(
        original,
        support,
        balance_stage=False,
        transfer_stage=False,
    )
    assert np.asarray(disabled).tobytes() == np.asarray(original).tobytes()
    assert float(
        t55.curriculum_reward(
            original,
            support,
            balance_stage=True,
            transfer_stage=False,
        )
    ) == pytest.approx(0.25)
    assert float(
        t55.curriculum_reward(
            original,
            support,
            balance_stage=False,
            transfer_stage=True,
        )
    ) == pytest.approx(0.5625)
    with pytest.raises(ValueError):
        t55.curriculum_reward(
            original,
            support,
            balance_stage=True,
            transfer_stage=True,
        )
