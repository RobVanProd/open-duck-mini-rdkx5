from __future__ import annotations

from dataclasses import dataclass, replace
import importlib.util
from pathlib import Path
from typing import Any

import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "patches" / "t128_negative_only_hidden_expert.py"
COMPOSER_PATH = (
    ROOT / "tools" / "compose_t128_negative_only_expert_playground.py"
)
SPEC = importlib.util.spec_from_file_location("t128_mechanism", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
T128 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T128)


@dataclass(frozen=True)
class FakeModel:
    geom_friction: Any
    dof_frictionloss: Any
    dof_armature: Any
    body_mass: Any
    body_ipos: Any
    body_inertia: Any
    body_iquat: Any

    def tree_replace(self, replacements: dict[str, Any]) -> "FakeModel":
        return replace(self, **replacements)


def fake_model(offset: float = 0.0, population: int | None = None) -> FakeModel:
    prefix = () if population is None else (population,)
    return FakeModel(
        geom_friction=jnp.full((*prefix, 2, 3), 1.0 + offset),
        dof_frictionloss=jnp.full((*prefix, 4), 2.0 + offset),
        dof_armature=jnp.full((*prefix, 4), 3.0 + offset),
        body_mass=jnp.full((*prefix, 4), 4.0 + offset),
        body_ipos=jnp.full((*prefix, 4, 3), 5.0 + offset),
        body_inertia=jnp.full((*prefix, 4, 3), 6.0 + offset),
        body_iquat=jnp.full((*prefix, 4, 4), 7.0 + offset),
    )


def test_negative_only_randomizer_replaces_every_physical_field() -> None:
    nominal = fake_model()
    randomized = fake_model(offset=10.0, population=8)

    def base(_model: FakeModel, _rng: Any) -> tuple[FakeModel, str]:
        return randomized, "axes"

    wrapped = T128.make_negative_only_randomizer(base, torso_body_id=2)
    actual, axes = wrapped(nominal, jnp.zeros((8, 2), dtype=jnp.uint32))
    assert axes == "axes"
    for name in T128.MODEL_FIELDS:
        expected = np.broadcast_to(
            np.asarray(getattr(nominal, name)),
            np.asarray(getattr(actual, name)).shape,
        ).copy()
        if name == "body_ipos":
            expected[:, 2, 0] -= 0.05
        np.testing.assert_array_equal(np.asarray(getattr(actual, name)), expected)


def test_negative_only_offsets_are_exact_and_population_checked() -> None:
    offsets = np.asarray(T128.negative_only_offsets(8))
    np.testing.assert_array_equal(
        offsets,
        np.tile(np.asarray([-0.05, 0.0, 0.0], np.float32), (8, 1)),
    )
    try:
        T128.negative_only_offsets(0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero population must fail closed")


def test_update_mask_changes_only_expert_and_critic() -> None:
    updates = {
        "actor": {
            "negative_adapter_location": {"kernel": jnp.ones((2, 2))},
            "residual_location": {"kernel": jnp.ones((2, 2))},
        },
        "critic": {"kernel": jnp.ones((2, 2))},
    }
    masked = T128.mask_protected_actor_updates(updates)
    assert np.all(np.asarray(masked["actor"]["negative_adapter_location"]["kernel"]) == 1)
    assert np.all(np.asarray(masked["actor"]["residual_location"]["kernel"]) == 0)
    assert np.all(np.asarray(masked["critic"]["kernel"]) == 1)


def test_composer_freezes_exact_negative_readback() -> None:
    text = COMPOSER_PATH.read_text(encoding="utf-8")
    assert "strata=1,exact=torso_com_x_neg,offset_m=-0.05" in text
    assert "make_negative_only_randomizer" in text
