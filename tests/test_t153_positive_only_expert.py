from __future__ import annotations

import importlib.util
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "patches" / "t153_positive_only_hidden_expert.py"
COMPOSER_PATH = (
    ROOT / "tools" / "compose_t153_positive_only_expert_playground.py"
)
SPEC = importlib.util.spec_from_file_location("t153_mechanism", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
T153 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T153)


class FakeModel:
    def __init__(self, population: int | None = None) -> None:
        shapes = {
            "geom_friction": (3, 3),
            "dof_frictionloss": (5,),
            "dof_armature": (5,),
            "body_mass": (4,),
            "body_ipos": (4, 3),
            "body_inertia": (4, 3),
            "body_iquat": (4, 4),
        }
        self.values = {}
        for index, (name, shape) in enumerate(shapes.items(), start=1):
            full_shape = shape if population is None else (population, *shape)
            value = jnp.full(full_shape, float(index), dtype=jnp.float32)
            self.values[name] = value
            setattr(self, name, value)

    def tree_replace(self, replacements):
        result = FakeModel.__new__(FakeModel)
        result.values = dict(self.values)
        result.values.update(replacements)
        for name, value in result.values.items():
            setattr(result, name, value)
        return result


def test_positive_only_randomizer_replaces_every_physical_field() -> None:
    population = 8
    nominal = FakeModel()
    randomized = FakeModel(population)

    def base(model, rng):
        del model, rng
        return randomized, {"axis": 0}

    wrapped = T153.make_positive_only_randomizer(base, torso_body_id=2)
    result, axes = wrapped(nominal, jnp.zeros((population, 2)))
    assert axes == {"axis": 0}
    for name in T153.MODEL_FIELDS:
        expected = np.broadcast_to(
            np.asarray(getattr(nominal, name)),
            np.asarray(getattr(result, name)).shape,
        ).copy()
        if name == "body_ipos":
            expected[:, 2, 0] += np.float32(0.05)
        np.testing.assert_array_equal(np.asarray(getattr(result, name)), expected)


def test_positive_only_offsets_are_exact_and_population_checked() -> None:
    offsets = np.asarray(T153.positive_only_offsets(8))
    np.testing.assert_array_equal(
        offsets,
        np.tile(np.asarray([0.05, 0.0, 0.0], dtype=np.float32), (8, 1)),
    )
    with pytest.raises(ValueError):
        T153.positive_only_offsets(0)


def test_only_isolated_expert_actor_updates_survive() -> None:
    updates = {
        "actor": {
            "residual_location": {"kernel": jnp.ones((2, 2))},
            "negative_adapter_location": {"kernel": jnp.ones((2, 2))},
        },
        "critic": {"hidden_0": {"kernel": jnp.ones((2, 2))}},
    }
    masked = T153.mask_protected_actor_updates(updates)
    assert np.all(
        np.asarray(masked["actor"]["residual_location"]["kernel"]) == 0
    )
    assert np.all(
        np.asarray(masked["actor"]["negative_adapter_location"]["kernel"]) == 1
    )
    assert np.all(np.asarray(masked["critic"]["hidden_0"]["kernel"]) == 1)


def test_composer_freezes_exact_positive_readback() -> None:
    text = COMPOSER_PATH.read_text(encoding="utf-8")
    assert "torso_com_x_pos,offset_m=+0.05" in text
    assert "make_positive_only_randomizer" in text
    assert "isolated_positive_expert_slot_only" in text
    assert T153.TRAINABLE_ACTOR_NAME == "negative_adapter_location"


def test_frozen_actor_inventory_is_disjoint() -> None:
    assert T153.TRAINABLE_ACTOR_NAME not in T153.FROZEN_ACTOR_NAMES
    assert jax.tree_util.keystr(("negative_adapter_location",))
