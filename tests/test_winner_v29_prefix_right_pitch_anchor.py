from __future__ import annotations

import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patches"))

import winner_v12_calibrator_training as training  # noqa: E402
import winner_v20_joint_recurrent_support as v20  # noqa: E402
import winner_v21_predictor_preserving_joint_support as v21  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402


def parameters() -> dict[str, jax.Array]:
    rng = np.random.default_rng(29)

    def sample(shape: tuple[int, ...]) -> jax.Array:
        return jnp.asarray(rng.normal(0.0, 0.03, shape).astype(np.float32))

    return {
        "obs_weight": sample((training.OBS_SIZE, training.HIDDEN_SIZE)),
        "previous_action_weight": sample((training.ACTION_SIZE, training.HIDDEN_SIZE)),
        "hidden_weight": sample((training.HIDDEN_SIZE, training.HIDDEN_SIZE)),
        "hidden_bias": sample((training.HIDDEN_SIZE,)),
        "action_weight": sample((training.HIDDEN_SIZE, training.ACTION_SIZE)),
        "action_bias": sample((training.ACTION_SIZE,)),
        "training_only_log_std": sample((training.ACTION_SIZE,)),
        "training_only_value_weight": sample((training.HIDDEN_SIZE,)),
        "training_only_value_bias": sample((1,)),
        "auxiliary_hidden_weight": sample((training.HIDDEN_SIZE, 6)),
        "auxiliary_action_weight": sample((training.ACTION_SIZE, 6)),
        "auxiliary_bias": sample((6,)),
    }


def population() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for identifier in v29.SELECTED_TRAINING_CONFIGURATION_IDS:
        rows.extend([{"id": identifier}, {"id": identifier}])
    rows.extend({"id": f"OTHER_{index:02d}"} for index in range(64))
    return rows


def test_anchor_mask_is_exactly_sixteen_by_eight_by_three() -> None:
    valid = np.ones((80, 12), dtype=np.float32)
    mask = v29.build_anchor_mask(population(), valid)
    assert mask.shape == (80, 12, 14)
    assert int(np.sum(mask)) == v29.EXPECTED_ANCHOR_ELEMENTS == 384
    assert np.all(mask[:16, :8, 11:14] == 1.0)
    assert np.all(mask[:16, 8:] == 0.0)
    assert np.all(mask[:16, :, :11] == 0.0)
    assert np.all(mask[16:] == 0.0)


def test_anchor_mask_rejects_stale_prefix() -> None:
    valid = np.ones((80, 12), dtype=np.float32)
    valid[0, 7] = 0.0
    with pytest.raises(ValueError, match="stale/invalid"):
        v29.build_anchor_mask(population(), valid)


def test_source_equal_candidate_is_exact_zero_loss() -> None:
    candidate = parameters()
    observations = jnp.zeros((2, 8, training.OBS_SIZE), dtype=jnp.float32)
    previous = jnp.zeros((2, 8, training.ACTION_SIZE), dtype=jnp.float32)
    mask = np.zeros((2, 8, training.ACTION_SIZE), dtype=np.float32)
    mask[:, :, 11:14] = 1.0
    loss, evidence = v29.prefix_anchor_loss(
        candidate,
        candidate,
        {"observations": observations, "previous_actions": previous},
        mask,
    )
    assert float(loss) == 0.0
    assert float(evidence["maximum_selected_action_delta"]) == 0.0


def test_anchor_gradient_locality_and_composition() -> None:
    candidate = parameters()
    source = {key: value for key, value in candidate.items()}
    source["action_bias"] = source["action_bias"].at[11:14].add(0.05)
    observations = jnp.asarray(
        np.random.default_rng(30).normal(0.0, 0.1, (2, 8, training.OBS_SIZE)),
        dtype=jnp.float32,
    )
    previous = jnp.zeros((2, 8, training.ACTION_SIZE), dtype=jnp.float32)
    mask = np.zeros((2, 8, training.ACTION_SIZE), dtype=np.float32)
    mask[:, :, 11:14] = 1.0
    trainable = v21.joint_trainable_parameters(candidate)

    def objective(values):
        return v29.prefix_anchor_loss(
            values,
            source,
            {"observations": observations, "previous_actions": previous},
            mask,
        )[0]

    gradients = jax.grad(objective)(trainable)
    assert v29.tree_rms(gradients, v29.ANCHOR_GRADIENT_KEYS) > 0.0
    for key in v29.NON_ANCHOR_GRADIENT_KEYS:
        assert np.array_equal(np.asarray(gradients[key]), np.zeros_like(gradients[key]))

    baseline = {key: jnp.ones_like(value) for key, value in gradients.items()}
    scale, evidence = v29.gradient_balance_scale(baseline, gradients)
    assert float(scale) > 0.0
    assert np.isclose(
        evidence["baseline_policy_gradient_rms"],
        evidence["scaled_anchor_policy_gradient_rms"],
        rtol=2.0e-6,
    )
    disabled = v29.compose_gradients(baseline, gradients, scale, enabled=False)
    enabled = v29.compose_gradients(baseline, gradients, scale, enabled=True)
    for key in v21.JOINT_TRAINABLE_KEYS:
        assert np.array_equal(np.asarray(disabled[key]), np.asarray(baseline[key]))
    assert any(
        not np.array_equal(np.asarray(enabled[key]), np.asarray(baseline[key]))
        for key in v29.ANCHOR_GRADIENT_KEYS
    )
    for key in v29.NON_ANCHOR_GRADIENT_KEYS:
        assert np.array_equal(np.asarray(enabled[key]), np.asarray(baseline[key]))


def test_selected_contract_constants() -> None:
    assert v29.PREFIX_TICKS == 8
    assert v29.RIGHT_PITCH_ACTION_INDICES == (11, 12, 13)
    assert v29.ANCHOR_GRADIENT_KEYS == (
        "obs_weight",
        "previous_action_weight",
        "hidden_weight",
        "hidden_bias",
        "action_weight",
        "action_bias",
    )
    assert set(v29.ANCHOR_GRADIENT_KEYS).isdisjoint(v29.NON_ANCHOR_GRADIENT_KEYS)
    assert set(v29.ANCHOR_GRADIENT_KEYS + v29.NON_ANCHOR_GRADIENT_KEYS) == set(
        v21.JOINT_TRAINABLE_KEYS
    )
