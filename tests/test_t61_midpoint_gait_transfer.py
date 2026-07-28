from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest

from patches import t61_midpoint_gait_transfer as t61


def test_midpoint_is_derived_from_closed_stage_endpoints() -> None:
    assert t61.BALANCE_LOCOMOTION_WEIGHT == 0.0
    assert t61.FULL_TRANSFER_LOCOMOTION_WEIGHT == 1.0
    assert t61.MIDPOINT_LOCOMOTION_WEIGHT == 0.5


def test_midpoint_reward_is_support_plus_half_locomotion() -> None:
    original = jnp.asarray(np.float32(0.3125))
    support = jnp.asarray(np.float32(0.25))
    reward = t61.midpoint_transfer_reward(original, support)
    assert float(reward) == pytest.approx(0.40625)


def test_t61_patch_is_default_off_and_mutually_exclusive() -> None:
    text = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "patches"
        / "winner_t61_midpoint_gait_transfer.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t61_midpoint_transfer_stage=False" in text
    assert "or self._config.winner_t61_midpoint_transfer_stage" in text
    assert "sum(" in text
    assert "> 1" in text
    assert "--winner_t61_midpoint_transfer_stage" in text
