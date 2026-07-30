from __future__ import annotations

from pathlib import Path

import jax.numpy as jnp
import numpy as np

from training import t215b_axis_complete_tilt as tilt


ROOT = Path(__file__).resolve().parents[1]


def test_t215b_identity_quaternion_and_zero_rates_are_zero() -> None:
    roll, pitch = tilt.predicted_axis_risks_rad(
        jnp.asarray([1.0, 0.0, 0.0, 0.0]),
        jnp.asarray(0.0),
        jnp.asarray(0.0),
    )
    assert float(roll) == 0.0
    assert float(pitch) == 0.0
    assert float(tilt.tilt_box_score(roll, pitch)) == 0.0
    assert float(tilt.tilt_box_cost(jnp.asarray(0.0))) == 0.0


def test_t215b_axis_envelopes_define_componentwise_unit_box() -> None:
    roll_score = tilt.tilt_box_score(
        jnp.asarray(tilt.ROLL_PASSING_ENVELOPE_RAD),
        jnp.asarray(0.0),
    )
    pitch_score = tilt.tilt_box_score(
        jnp.asarray(0.0),
        jnp.asarray(tilt.PITCH_PASSING_ENVELOPE_RAD),
    )
    assert np.isclose(float(roll_score), 1.0, atol=1.0e-7)
    assert np.isclose(float(pitch_score), 1.0, atol=1.0e-7)
    assert float(tilt.tilt_box_excess(jnp.asarray(1.0))) == 0.0
    assert np.isclose(
        float(tilt.tilt_box_cost(jnp.asarray(1.5))),
        0.25,
        atol=1.0e-7,
    )


def test_t215b_patch_is_training_only_axis_complete_cost() -> None:
    text = (
        ROOT / "patches/winner_t215b_axis_complete_tilt.patch"
    ).read_text(encoding="utf-8")
    assert "winner_t215b_axis_complete_tilt_cost=False" in text
    assert "data.qvel[base_qvel + 3]" in text
    assert "data.qvel[base_qvel + 4]" in text
    assert "box_score = jp.maximum(" in text
    assert "constrained_cost = jp.square(box_excess)" in text
    assert "reward_channel=unchanged" in text
    assert "deployment_graph=unchanged" in text
    assert "not args.winner_t209_dual_roll_cost" in text


def test_t215b_environment_contract_checks_both_axes() -> None:
    text = (
        ROOT / "tools/run_t215b_environment_contract_worker.py"
    ).read_text(encoding="utf-8")
    assert 'for index, axis in enumerate(("roll", "pitch"))' in text
    assert "both_synthetic_axes_exceed_box" in text
    assert "synthetic_dominant_axis_exact" in text
    assert "cost_is_unscaled_squared_box_excess" in text
    assert "cost_is_outside_and_does_not_change_reward" in text


def test_t215b_cpu_contract_freezes_scope_and_authority() -> None:
    builder = (
        ROOT
        / "tools/build_t215b_axis_complete_tilt_cpu_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t215b_axis_complete_tilt_cpu_contract.py"
    ).read_text(encoding="utf-8")
    assert '"source": "T203_HALF"' in builder
    assert '"t210_eta_retry": False' in builder
    assert '"cost_scale": 1.0' in builder
    assert '"deployment_graph_change": False' in builder
    assert '"hosted_training": False' in builder
    assert '"--winner_v127_constrained_cost"' in runner
    assert '"--winner_t215b_axis_complete_tilt_cost"' in runner
    assert '"--winner_t209_dual_roll_cost"' in runner
    assert "not in value[\"training\"][\"command\"]" in runner
    assert "both_axis_environment_contract_green" in runner
    assert 'value["authority"]["hosted_training"] = False' in runner
    assert 'value["authority"]["gate5"] = False' in runner
