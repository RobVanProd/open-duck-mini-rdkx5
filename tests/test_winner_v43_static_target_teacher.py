from __future__ import annotations

import json
from pathlib import Path
import sys

import jax
import jax.numpy as jnp
import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
sys.path.insert(0, str(PATCHES))

import winner_v43_static_target_teacher as v43  # noqa: E402


RESULT = ROOT / "outputs/analysis/winner_v42_static_target_teacher_table_result.json"


def table():
    return v43.load_teacher_table(json.loads(RESULT.read_text(encoding="utf-8")))


def test_exact_table_expands_only_reviewed_pitch_basis() -> None:
    values = table()
    assert tuple(values) == v43.CONFIGURATION_IDS
    assert all(value.shape == (14,) and value.dtype == np.float32 for value in values.values())
    nonpitch = sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES))
    assert all(np.array_equal(value[nonpitch], np.zeros(8, dtype=np.float32)) for value in values.values())


def test_teacher_batch_requires_two_plant_pairs_and_masks_only_pitch() -> None:
    values = table()
    identifiers = [name for name in v43.CONFIGURATION_IDS for _ in range(2)]
    previous = np.zeros((30, 3, 14), dtype=np.float32)
    valid = np.ones((30, 3), dtype=np.float32)
    raw, bounded, mask = v43.build_teacher_batch(identifiers, previous, valid, values)
    assert raw.shape == bounded.shape == mask.shape == (30, 3, 14)
    assert int(np.sum(np.asarray(mask))) == 30 * 3 * 6
    nonpitch = sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES))
    assert np.array_equal(np.asarray(mask)[..., nonpitch], np.zeros((30, 3, 8), dtype=np.float32))
    with pytest.raises(ValueError, match="two-plant pairs"):
        v43.build_teacher_batch(identifiers[:-1] + [identifiers[0]], previous, valid, values)


def test_teacher_loss_gradient_is_pitch_only_and_default_off_is_exact() -> None:
    values = table()
    identifiers = [name for name in v43.CONFIGURATION_IDS for _ in range(2)]
    previous = jnp.zeros((30, 2, 14), dtype=jnp.float32)
    valid = np.ones((30, 2), dtype=np.float32)
    candidate = jnp.full((30, 2, 14), jnp.float32(0.125))

    def teacher_objective(actions):
        loss, _ = v43.static_target_teacher_loss(
            actions, identifiers, previous, valid, values
        )
        return loss

    teacher_loss, teacher_grad = jax.value_and_grad(teacher_objective)(candidate)
    baseline = lambda actions: jnp.mean(jnp.square(actions + jnp.float32(0.2)))
    baseline_loss, baseline_grad = jax.value_and_grad(baseline)(candidate)

    def disabled(actions):
        current_teacher, _ = v43.static_target_teacher_loss(
            actions, identifiers, previous, valid, values
        )
        return v43.combine_objective(
            baseline(actions), current_teacher, jnp.float32(3.0), enabled=False
        )

    disabled_loss, disabled_grad = jax.value_and_grad(disabled)(candidate)
    assert float(teacher_loss) > 0.0
    assert np.array_equal(np.asarray(disabled_loss), np.asarray(baseline_loss))
    assert np.array_equal(np.asarray(disabled_grad), np.asarray(baseline_grad))
    nonpitch = sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES))
    assert np.array_equal(
        np.asarray(teacher_grad)[..., nonpitch], np.zeros((30, 2, 8), dtype=np.float32)
    )
    assert np.all(np.any(np.asarray(teacher_grad)[..., v43.PITCH_ACTION_INDICES] != 0.0, axis=(0, 1)))
