from __future__ import annotations

import json
from pathlib import Path
import sys

import jax
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
sys.path.insert(0, str(PATCHES))

import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


TABLE_RESULT = ROOT / "outputs/analysis/winner_v42_static_target_teacher_table_result.json"


def table():
    return v49.v43.load_teacher_table(json.loads(TABLE_RESULT.read_text(encoding="utf-8")))


def test_full_teacher_selects_every_valid_action_element() -> None:
    values = table()
    identifiers = [name for name in v49.v43.CONFIGURATION_IDS for _ in range(2)]
    previous = np.zeros((30, 3, 14), dtype=np.float32)
    valid = np.ones((30, 3), dtype=np.float32)
    raw, bounded, mask = v49.build_teacher_batch(identifiers, previous, valid, values)
    old_raw, old_bounded, _ = v49.v43.build_teacher_batch(
        identifiers, previous, valid, values
    )
    assert np.array_equal(np.asarray(raw), np.asarray(old_raw))
    assert np.array_equal(np.asarray(bounded), np.asarray(old_bounded))
    assert np.array_equal(np.asarray(mask), np.ones((30, 3, 14), dtype=np.float32))


def test_full_teacher_gradient_reaches_nonpitch_and_default_off_is_exact() -> None:
    values = table()
    identifiers = [name for name in v49.v43.CONFIGURATION_IDS for _ in range(2)]
    previous = jnp.zeros((30, 2, 14), dtype=jnp.float32)
    valid = np.ones((30, 2), dtype=np.float32)
    candidate = jnp.full((30, 2, 14), jnp.float32(0.125))

    def teacher(actions):
        return v49.full_action_teacher_loss(
            actions, identifiers, previous, valid, values
        )[0]

    teacher_loss, teacher_grad = jax.value_and_grad(teacher)(candidate)
    baseline = lambda actions: jnp.mean(jnp.square(actions + jnp.float32(0.2)))
    baseline_loss, baseline_grad = jax.value_and_grad(baseline)(candidate)

    def disabled(actions):
        return v49.combine_objective(baseline(actions), teacher(actions), enabled=False)

    disabled_loss, disabled_grad = jax.value_and_grad(disabled)(candidate)
    assert float(teacher_loss) > 0.0
    assert all(np.any(np.asarray(teacher_grad)[..., index] != 0.0) for index in range(14))
    assert np.array_equal(np.asarray(disabled_loss), np.asarray(baseline_loss))
    assert np.array_equal(np.asarray(disabled_grad), np.asarray(baseline_grad))


def test_scale_preserves_old_pitch_per_element_weight_bit_exact() -> None:
    assert float(v49.OLD_PITCH_TEACHER_SCALE) == 58.436370849609375
    assert float(v49.FULL_ACTION_TEACHER_SCALE) == 136.35153198242188
    assert v49.per_element_scale_is_preserved() is True
