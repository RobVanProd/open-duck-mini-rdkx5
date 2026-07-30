from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from patches import t185_in_episode_single_support_prefix as t185


def test_reference_derived_support_phases_and_targets() -> None:
    assert t185.REFERENCE_PERIOD_TICKS == 27
    assert np.array_equal(
        np.asarray(t185.REFERENCE_SUPPORT_PHASES),
        np.asarray([2, 15], dtype=np.int32),
    )
    assert np.array_equal(
        np.asarray(t185.target_support(t185.LEFT_SUPPORT_SIDE)),
        np.asarray([True, False]),
    )
    assert np.array_equal(
        np.asarray(t185.target_support(t185.RIGHT_SUPPORT_SIDE)),
        np.asarray([False, True]),
    )


def test_phase_is_frozen_for_exact_prefix_then_advances() -> None:
    for side, anchor in (
        (t185.LEFT_SUPPORT_SIDE, 2),
        (t185.RIGHT_SUPPORT_SIDE, 15),
    ):
        phase = jnp.asarray(anchor, dtype=jnp.int32)
        remaining = jnp.asarray(t185.PREFIX_TICKS, dtype=jnp.int32)
        observed = []
        for _ in range(t185.PREFIX_TICKS):
            phase = t185.phase_for_step(phase, anchor, remaining)
            observed.append(int(phase))
            remaining = t185.remaining_after_step(remaining)
        assert observed == [anchor] * t185.PREFIX_TICKS
        assert int(remaining) == 0
        assert int(t185.phase_for_step(phase, anchor, remaining)) == (
            anchor + 1
        ) % t185.REFERENCE_PERIOD_TICKS
        assert int(t185.support_phase_index(side)) == anchor


def test_reward_uses_explicit_reference_side_not_phase_sign() -> None:
    gravity = jnp.asarray([0.0, 0.0, -1.0])
    gyro = jnp.zeros(3)
    left = t185.single_support_balance_reward(
        gravity,
        gyro,
        jnp.asarray([True, False]),
        t185.LEFT_SUPPORT_SIDE,
    )
    right = t185.single_support_balance_reward(
        gravity,
        gyro,
        jnp.asarray([False, True]),
        t185.RIGHT_SUPPORT_SIDE,
    )
    assert float(left) == pytest.approx(t185.ALIVE_REWARD_PER_TICK)
    assert float(right) == pytest.approx(t185.ALIVE_REWARD_PER_TICK)
    assert float(
        t185.single_support_balance_reward(
            gravity,
            gyro,
            jnp.asarray([False, True]),
            t185.LEFT_SUPPORT_SIDE,
        )
    ) == 0.0


def test_reward_switches_inside_episode_without_blending() -> None:
    original = jnp.asarray(np.float32(0.3125))
    support = jnp.asarray(np.float32(0.25))
    prefix = t185.curriculum_reward(original, support, 1)
    walking = t185.curriculum_reward(original, support, 0)
    assert np.asarray(prefix).tobytes() == np.asarray(support).tobytes()
    assert np.asarray(walking).tobytes() == np.asarray(original).tobytes()


def test_side_sampling_is_symmetric_and_exercises_both_sides() -> None:
    keys = jax.random.split(jax.random.PRNGKey(185), 256)
    sides = np.asarray(jax.vmap(t185.sample_support_side)(keys))
    assert set(sides.tolist()) == {0, 1}
