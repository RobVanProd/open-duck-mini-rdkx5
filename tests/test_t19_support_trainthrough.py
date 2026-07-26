from __future__ import annotations

import importlib.util
from pathlib import Path

import jax.numpy as jnp
import numpy as np
from mujoco_playground._src import mjx_env


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "patches" / "t19_support_trainthrough.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "t19_support_trainthrough_test_module",
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_action_homeomorphism_roundtrip() -> None:
    module = load_module()
    rng = np.random.default_rng(20260726)
    source = rng.uniform(-1.0, 1.0, size=(512, 14)).astype(np.float32)
    final = np.asarray(module.forward_action(jnp.asarray(source)))
    recovered = np.asarray(module.inverse_action(jnp.asarray(final)))
    assert np.max(np.abs(recovered - source)) <= 8 * np.finfo(np.float32).eps
    assert np.all(final >= -1.0)
    assert np.all(final <= 1.0)
    assert np.array_equal(
        np.asarray(module.forward_action(jnp.zeros(14, dtype=jnp.float32))),
        module.SUPPORT_ACTION,
    )


def test_observation_inverse_matches_t17_definition() -> None:
    module = load_module()
    from tools.t17_support_homeomorphism_onnx import (
        HOME_ACTION_RAD,
        forward_observation,
    )

    rng = np.random.default_rng(19)
    source = rng.normal(0.0, 0.2, size=(32, 115)).astype(np.float32)
    source[:, 83:97] = HOME_ACTION_RAD + rng.uniform(
        -0.2, 0.2, size=(32, 14)
    ).astype(np.float32)
    final = forward_observation(source)
    recovered = np.asarray(
        module.inverse_observation(
            jnp.asarray(final),
            jnp.asarray(HOME_ACTION_RAD),
        )
    )
    assert np.max(np.abs(recovered - source)) <= 32 * np.finfo(
        np.float32
    ).eps


def test_calibrator_reaches_exact_support_inside_t18_rate_box() -> None:
    module = load_module()
    previous = jnp.zeros(14, dtype=jnp.float32)
    history = []
    for _ in range(module.CALIBRATION_TICKS):
        current = module.next_calibration_action(previous)
        history.append(np.asarray(current))
        previous = current
    values = np.asarray(history)
    assert np.array_equal(values[-1], module.SUPPORT_ACTION)
    assert np.max(
        np.abs(np.diff(values, axis=0))
        - module.CALIBRATOR_MAX_ACTION_DELTA
    ) <= np.finfo(np.float32).eps
    assert np.all(
        module.CALIBRATOR_MAX_ACTION_DELTA <= module.MAX_ACTION_DELTA
    )


def test_patch_freezes_full_handoff_reset_and_default_off_flag() -> None:
    source = (
        ROOT / "patches" / "winner_t19_support_trainthrough.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t19_support_trainthrough=False" in source
    assert "FullHandoffAutoResetWrapper" not in source
    assert "wrap_for_brax_training" in source
    assert "t19_source_motor_targets" in source
    assert "t19_support_prefix_valid" in source
    assert "t19.inverse_observation" in source


def test_full_handoff_reset_restores_nested_info_trees() -> None:
    module = load_module()

    class DummyEnvironment:
        def reset(self, rng):
            del rng
            return mjx_env.State(
                data={"x": jnp.asarray([[1.0], [2.0]])},
                obs={"state": jnp.asarray([[3.0], [4.0]])},
                reward=jnp.zeros(2),
                done=jnp.zeros(2),
                metrics={},
                info={
                    "rng": jnp.asarray([[5, 6], [7, 8]]),
                    "nested": {
                        "x": jnp.asarray([[9.0], [10.0]])
                    },
                },
            )

        def step(self, state, action):
            del action
            info = dict(state.info)
            info["nested"] = {
                "x": state.info["nested"]["x"] + 100.0
            }
            return state.replace(
                data={"x": state.data["x"] + 100.0},
                obs={"state": state.obs["state"] + 100.0},
                done=jnp.ones(2),
                info=info,
            )

    wrapper = module.FullHandoffAutoResetWrapper(DummyEnvironment())
    state = wrapper.reset(jnp.zeros((2, 2), dtype=jnp.uint32))
    next_state = wrapper.step(state, jnp.zeros((2, 1)))
    assert np.array_equal(
        np.asarray(next_state.data["x"]),
        np.asarray([[1.0], [2.0]]),
    )
    assert np.array_equal(
        np.asarray(next_state.obs["state"]),
        np.asarray([[3.0], [4.0]]),
    )
    assert np.array_equal(
        np.asarray(next_state.info["nested"]["x"]),
        np.asarray([[9.0], [10.0]]),
    )
