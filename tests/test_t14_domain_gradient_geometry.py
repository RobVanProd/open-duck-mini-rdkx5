from __future__ import annotations

import importlib.util
from pathlib import Path

import jax.numpy as jnp


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "run_t14_domain_gradient_geometry.py"
SPEC = importlib.util.spec_from_file_location("t14_geometry", MODULE_PATH)
assert SPEC and SPEC.loader
T14 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T14)


def test_geometry_reports_conflicting_descent() -> None:
    broad = {"x": jnp.asarray([1.0, 0.0], dtype=jnp.float32)}
    negative = {"x": jnp.asarray([-2.0, 0.0], dtype=jnp.float32)}
    row = T14.geometry(broad, negative)
    assert row["gradient_cosine"] == -1.0
    assert row["right_loss_derivative_along_left_descent"] == 2.0
    assert row["left_self_descent_derivative"] == -1.0
    assert row["right_self_descent_derivative"] == -4.0


def test_exact_negative_randomizer_changes_only_torso_x() -> None:
    class Array:
        def __init__(self, value):
            self.value = value

        @property
        def at(self):
            return At(self)

    class At:
        def __init__(self, parent):
            self.parent = parent

        def __getitem__(self, index):
            self.index = index
            return self

        def add(self, value):
            updated = self.parent.value.at[self.index].add(float(value))
            return Array(updated)

    class Model:
        def __init__(self, body_ipos):
            self.body_ipos = body_ipos

        def tree_replace(self, values):
            return Model(values["body_ipos"])

    original = jnp.zeros((3, 4, 3), dtype=jnp.float32)

    def base(model, rng):
        del rng
        return model, "axes"

    wrapped = T14.exact_negative_com_randomizer(base)
    model, axes = wrapped(Model(Array(original.copy())), None)
    expected = original.at[:, T14.TORSO_BODY_ID, 0].add(-0.05)
    assert jnp.array_equal(model.body_ipos.value, expected)
    assert axes == "axes"


def test_tree_mean_and_dot() -> None:
    first = {"a": jnp.asarray([1.0, 2.0])}
    second = {"a": jnp.asarray([3.0, 4.0])}
    mean = T14.tree_mean([first, second])
    assert jnp.array_equal(mean["a"], jnp.asarray([2.0, 3.0]))
    assert T14.tree_dot(mean, mean) == 13.0
