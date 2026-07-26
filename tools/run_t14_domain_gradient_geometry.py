#!/usr/bin/env python3
"""Run T14's CPU-only broad-vs-negative-COM actor-gradient audit.

The audit executes no optimizer step.  It collects three paired 80-tick
rollouts from the frozen V121-half policy:

* the exact winner-v3 full variable-configuration distribution,
* the exact P30 plant with torso COM x shifted by -0.05 m, and
* the exact nominal P30 plant.

The 256 environments and four 20-tick windows reproduce the 20,480
observations collected by one frozen winner-v3 PPO training batch.  A single
frozen permutation creates four 256-sequence minibatches.  Actor gradients are
then measured without changing the checkpoint.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import flax
from flax.training import orbax_utils
import jax
import jax.numpy as jnp
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t14_domain_gradient_geometry_preregistration.json"
RESULT = ANALYSIS / "t14_domain_gradient_geometry_result.json"
MARKDOWN = ANALYSIS / "T14_DOMAIN_GRADIENT_GEOMETRY_RESULT_20260726.md"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"

SOURCE = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v119-extracted-20260724"
    r"\winner_v119_transition_continuation\training"
    r"\2026_07_24_193907_1003520"
)
CPU_TEMPLATE = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v119-transition-cpu-smoke-20260724\smoke"
    r"\2026_07_24_150649_0"
)
DEFAULT_WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t14_domain_gradient_geometry_v1"
)

ACTION_SIZE = 14
HIDDEN_SIZE = 64
OBSERVATION_SIZE = 115
PRIVILEGED_SIZE = 226
TORSO_BODY_ID = 2
FORMAL_ENVIRONMENTS = 256
FORMAL_TICKS = 80
UNROLL_LENGTH = 20
MINIBATCHES = 4
FORMAL_SEED = 20260726
COM_NEGATIVE_OFFSET_M = -0.05
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def normalizer_state(value: dict[str, Any]) -> Any:
    from brax.training import types
    from brax.training.acme import running_statistics

    return running_statistics.RunningStatisticsState(
        mean=value["mean"],
        std=value["std"],
        count=types.UInt64(
            hi=value["count"]["hi"],
            lo=value["count"]["lo"],
        ),
        summed_variance=value["summed_variance"],
        std_eps=value["std_eps"],
    )


def runner_args(output: Path, deviation_scale: float) -> argparse.Namespace:
    """Build the exact source-policy environment contract."""
    return argparse.Namespace(
        output_dir=str(output),
        num_timesteps=0,
        ppo_seed=FORMAL_SEED,
        ppo_num_envs=FORMAL_ENVIRONMENTS,
        ppo_num_evals=1,
        ppo_episode_length=600,
        ppo_unroll_length=UNROLL_LENGTH,
        ppo_batch_size=256,
        ppo_num_minibatches=4,
        ppo_num_updates_per_batch=4,
        ppo_learning_rate=0.0003,
        ppo_discounting=0.97,
        ppo_entropy_cost=0.005,
        policy_architecture="reference_residual_recurrent_adapter",
        recurrent_hidden_size=HIDDEN_SIZE,
        winner_v98_protected_policy_path=None,
        winner_v98_calibrator_path=None,
        winner_v98_calibration_ticks=250,
        winner_v98_home_return_ticks=250,
        imitation_scale=1.0,
        reference_feature_table_path=str(REFERENCE),
        ground_up_command_curriculum=False,
        nominal_reference_bootstrap=True,
        nominal_reference_command_x=0.074,
        ground_up_torso_com_randomization=False,
        ground_up_torso_com_x_min_m=-0.05,
        ground_up_torso_com_x_max_m=0.05,
        ground_up_torso_com_distribution="uniform",
        ground_up_hard_vector_command_support=True,
        ground_up_command_support_min_x=0.074,
        ground_up_command_support_max_x=0.080,
        ground_up_action_velocity_limits_rad_s=VELOCITY_LIMITS,
        ground_up_measured_actuator_bridge=True,
        ground_up_applied_target_observation=True,
        ground_up_tracking_tail_exceedance_scale=-6572.254964031055,
        ground_up_tracking_tail_threshold_rad=0.20,
        ground_up_peak_torque_exceedance_scale=0.0,
        ground_up_linear_peak_torque_exceedance_scale=0.0,
        ground_up_actuator_bridge_delay_ticks=(
            "3,3,3,3,3,3,2,3,3,3,2,3,2,3"
        ),
        ground_up_actuator_bridge_tau_s=(
            ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,"
            ".035,.010,.030,.005"
        ),
        reference_start_phase=0,
        ground_up_signed_progress_objective=True,
        winner_v3_variable_configuration=True,
        winner_v119_train_transition_match=True,
        winner_v127_constrained_cost=False,
        winner_v3_deviation_scale=float(deviation_scale),
        critic_observation="privileged_state",
        env="joystick",
        task="flat_terrain_backlash",
        restore_checkpoint_path=None,
    )


def exact_negative_com_randomizer(
    base_randomizer: Callable[..., Any],
) -> Callable[..., Any]:
    """Turn the exact scale-zero P30 model into the exact COM_NEG model."""

    def randomizer(model, rng):
        randomized, in_axes = base_randomizer(model, rng)
        body_ipos = randomized.body_ipos.at[:, TORSO_BODY_ID, 0].add(
            jnp.float32(COM_NEGATIVE_OFFSET_M)
        )
        return randomized.tree_replace({"body_ipos": body_ipos}), in_axes

    return randomizer


def tree_finite(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def tree_dot(left: Any, right: Any) -> float:
    value = sum(
        (
            jnp.vdot(jnp.asarray(a), jnp.asarray(b))
            for a, b in zip(
                jax.tree_util.tree_leaves(left),
                jax.tree_util.tree_leaves(right),
                strict=True,
            )
        ),
        jnp.asarray(0.0, dtype=jnp.float32),
    )
    return float(np.asarray(value))


def tree_scale(value: Any, scale: float) -> Any:
    return jax.tree_util.tree_map(lambda leaf: leaf * scale, value)


def tree_mean(values: list[Any]) -> Any:
    if not values:
        raise ValueError("cannot average an empty gradient list")
    return jax.tree_util.tree_map(
        lambda *leaves: sum(leaves) / len(leaves),
        *values,
    )


def tree_max_abs_error(left: Any, right: Any) -> float:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return float("inf")
    return max(
        (
            float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
            for a, b in zip(
                jax.tree_util.tree_leaves(left),
                jax.tree_util.tree_leaves(right),
                strict=True,
            )
        ),
        default=0.0,
    )


def model_readback(wrapped_env: Any) -> dict[str, Any]:
    model = wrapped_env._mjx_model_v
    torso_x = np.asarray(model.body_ipos[:, TORSO_BODY_ID, 0])
    return {
        "environments": int(torso_x.shape[0]),
        "torso_com_x_min_m": float(np.min(torso_x)),
        "torso_com_x_mean_m": float(np.mean(torso_x)),
        "torso_com_x_max_m": float(np.max(torso_x)),
        "torso_com_x_unique_count": int(np.unique(torso_x).size),
    }


def paired_standard_noise(
    transition: Any,
) -> np.ndarray:
    params = np.asarray(
        transition.extras["policy_extras"]["distribution_params"]
    )
    raw = np.asarray(transition.extras["policy_extras"]["raw_action"])
    location, scale_logits = np.split(params, 2, axis=-1)
    scale = np.logaddexp(scale_logits, 0.0) + 0.001
    return (raw - location) / scale


def collect_rollout(
    *,
    env: Any,
    make_policy: Callable[..., Any],
    processor: Any,
    policy_params: Any,
    reset_keys: jax.Array,
    action_keys: list[jax.Array],
    ticks: int,
) -> tuple[Any, dict[str, Any]]:
    """Collect one paired stochastic rollout without updating any parameter."""
    from brax.training import acting

    policy = make_policy((processor, policy_params), deterministic=False)
    reset = jax.jit(env.reset)
    state = reset(reset_keys)
    initial_command = np.asarray(state.info["command"])

    @jax.jit
    def step(current, key):
        return acting.actor_step(
            env,
            current,
            policy,
            key,
            extra_fields=("truncation",),
        )

    transitions = []
    for tick in range(ticks):
        state, transition = step(state, action_keys[tick])
        transitions.append(transition)
    jax.block_until_ready(state.reward)
    data = jax.tree_util.tree_map(
        lambda *rows: jnp.stack(rows, axis=1),
        *transitions,
    )
    return data, {
        "initial_command": initial_command,
        "reward_mean": float(np.mean(np.asarray(data.reward))),
        "reward_min": float(np.min(np.asarray(data.reward))),
        "reward_max": float(np.max(np.asarray(data.reward))),
        "termination_count": int(
            np.count_nonzero(np.asarray(data.discount) == 0.0)
        ),
        "finite": tree_finite(data),
    }


def concatenate_windows(
    data: Any,
    permutation: np.ndarray,
    *,
    ticks: int,
    unroll_length: int,
) -> Any:
    windows = [
        jax.tree_util.tree_map(
            lambda value, start=start: value[
                :, start : start + unroll_length
            ],
            data,
        )
        for start in range(0, ticks, unroll_length)
    ]
    rows = jax.tree_util.tree_map(
        lambda *values: jnp.concatenate(values, axis=0),
        *windows,
    )
    return jax.tree_util.tree_map(lambda value: value[permutation], rows)


def actor_objective(
    policy_params: Any,
    *,
    processor: Any,
    value_params: Any,
    data: Any,
    rng: jax.Array,
    network: Any,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    """Exact frozen PPO reward+entropy actor objective; no value loss."""
    from brax.training.agents.ppo import losses as ppo_losses

    data = jax.tree_util.tree_map(lambda value: jnp.swapaxes(value, 0, 1), data)
    policy_logits = network.policy_network.apply(
        processor,
        policy_params,
        data.observation,
    )
    baseline = network.value_network.apply(
        processor,
        value_params,
        data.observation,
    )
    terminal_observation = jax.tree_util.tree_map(
        lambda value: value[-1],
        data.next_observation,
    )
    bootstrap = network.value_network.apply(
        processor,
        value_params,
        terminal_observation,
    )
    truncation = data.extras["state_extras"]["truncation"]
    termination = (1.0 - data.discount) * (1.0 - truncation)
    _, advantages = ppo_losses.compute_gae(
        truncation=truncation,
        termination=termination,
        rewards=data.reward,
        values=baseline,
        bootstrap_value=bootstrap,
        lambda_=0.95,
        discount=0.97,
    )
    advantages = (advantages - advantages.mean()) / (
        advantages.std() + 1.0e-8
    )
    distribution = network.parametric_action_distribution
    target_log_prob = distribution.log_prob(
        policy_logits,
        data.extras["policy_extras"]["raw_action"],
    )
    behavior_log_prob = data.extras["policy_extras"]["log_prob"]
    ratio = jnp.exp(target_log_prob - behavior_log_prob)
    surrogate_1 = ratio * advantages
    surrogate_2 = jnp.clip(ratio, 0.8, 1.2) * advantages
    policy_loss = -jnp.mean(jnp.minimum(surrogate_1, surrogate_2))
    entropy = jnp.mean(distribution.entropy(policy_logits, rng))
    objective = policy_loss - 0.005 * entropy
    return objective, {
        "objective": objective,
        "policy_loss": policy_loss,
        "entropy": entropy,
        "advantage_mean": jnp.mean(advantages),
        "advantage_std": jnp.std(advantages),
        "ratio_mean": jnp.mean(ratio),
        "ratio_min": jnp.min(ratio),
        "ratio_max": jnp.max(ratio),
    }


def gradient_batches(
    *,
    policy_params: Any,
    processor: Any,
    value_params: Any,
    shuffled_data: Any,
    network: Any,
    gradient_keys: list[jax.Array],
    minibatches: int,
    minibatch_size: int,
) -> tuple[list[Any], list[dict[str, float]]]:
    objective = functools.partial(
        actor_objective,
        processor=processor,
        value_params=value_params,
        network=network,
    )
    value_and_grad = jax.jit(
        jax.value_and_grad(objective, has_aux=True)
    )
    gradients = []
    metrics = []
    for index in range(minibatches):
        start = index * minibatch_size
        stop = start + minibatch_size
        batch = jax.tree_util.tree_map(
            lambda value: value[start:stop],
            shuffled_data,
        )
        (loss, aux), gradient = value_and_grad(
            policy_params,
            data=batch,
            rng=gradient_keys[index],
        )
        jax.block_until_ready(loss)
        gradients.append(gradient)
        metrics.append(
            {
                name: float(np.asarray(value))
                for name, value in aux.items()
            }
        )
    return gradients, metrics


def geometry(left: Any, right: Any) -> dict[str, float]:
    left_norm_sq = tree_dot(left, left)
    right_norm_sq = tree_dot(right, right)
    dot = tree_dot(left, right)
    product = math.sqrt(max(left_norm_sq * right_norm_sq, 0.0))
    cosine = dot / product if product > 0.0 else 0.0
    # Gradients point uphill in loss.  The broad optimizer direction is
    # -g_broad, so g_neg dot (-g_broad) = -dot.
    return {
        "left_gradient_norm": math.sqrt(max(left_norm_sq, 0.0)),
        "right_gradient_norm": math.sqrt(max(right_norm_sq, 0.0)),
        "gradient_dot": dot,
        "gradient_cosine": cosine,
        "right_loss_derivative_along_left_descent": -dot,
        "left_loss_derivative_along_right_descent": -dot,
        "left_self_descent_derivative": -left_norm_sq,
        "right_self_descent_derivative": -right_norm_sq,
    }


def processor_count(processor: Any) -> int:
    hi = int(np.asarray(processor.count.hi))
    lo = int(np.asarray(processor.count.lo))
    return (hi << 32) | lo


def source_inputs(prereg: dict[str, Any], playground: Path) -> dict[str, str]:
    expected = prereg["input_hashes"]
    observed = {
        "runner": sha256(Path(__file__).resolve()),
        "reference": sha256(REFERENCE),
        "source_checkpoint_directory": sha256_directory(SOURCE),
        "cpu_template_directory": sha256_directory(CPU_TEMPLATE),
        "playground_manifest": sha256(
            playground / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "recurrent_network": sha256(
            playground
            / "playground/common/"
            "reference_residual_recurrent_adapter_ppo_networks.py"
        ),
        "joystick": sha256(
            playground / "playground/open_duck_mini_v2/joystick.py"
        ),
        "winner_v3_randomizer": sha256(
            playground
            / "playground/common/winner_v3_variable_configuration.py"
        ),
    }
    if observed != expected:
        raise ValueError(f"T14 input hashes changed: {observed} != {expected}")
    return observed


def run(
    *,
    playground: Path,
    work: Path,
    environments: int,
    ticks: int,
    formal: bool,
) -> dict[str, Any]:
    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise RuntimeError("T14 must execute on CPU only")
    if environments != FORMAL_ENVIRONMENTS or ticks != FORMAL_TICKS:
        if formal:
            raise ValueError("formal T14 dimensions changed")
    unroll_length = UNROLL_LENGTH if formal else ticks
    minibatches = MINIBATCHES if formal else 1

    sys.path.insert(0, str(playground))
    os.chdir(playground)
    from brax.training.acme import running_statistics
    from mujoco_playground import wrapper
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (
        install_recurrent_adapter_collector_hooks,
        make_recurrent_adapter_inference_fn,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )
    from playground.open_duck_mini_v2.runner import OpenDuckMiniV2Runner

    install_recurrent_adapter_collector_hooks()
    work.mkdir(parents=True)
    runners = {}
    for domain, scale in (
        ("broad_v3", 1.0),
        ("negative_com_p30", 0.0),
        ("nominal_p30", 0.0),
    ):
        domain_output = work / f"runner_{domain}"
        domain_output.mkdir()
        runner = OpenDuckMiniV2Runner(
            runner_args(domain_output, scale)
        )
        runner.writer.close()
        runners[domain] = runner
    runners["negative_com_p30"].randomizer = exact_negative_com_randomizer(
        runners["negative_com_p30"].randomizer
    )
    nominal_model_x = float(
        np.asarray(
            runners["nominal_p30"].env.mjx_model.body_ipos[
                TORSO_BODY_ID, 0
            ]
        )
    )

    wrapped = {
        name: wrapper.wrap_for_brax_training(
            runner.env,
            episode_length=600,
            action_repeat=1,
            randomization_fn=functools.partial(
                runner.randomizer,
                rng=jax.random.split(
                    jax.random.PRNGKey(FORMAL_SEED + 101),
                    environments,
                ),
            ),
        )
        for name, runner in runners.items()
    }

    checkpointer = ocp.PyTreeCheckpointer()
    cpu_template = checkpointer.restore(str(CPU_TEMPLATE))
    restore_args = orbax_utils.restore_args_from_target(cpu_template)
    source = checkpointer.restore(
        str(SOURCE),
        item=cpu_template,
        restore_args=restore_args,
    )
    source_before = flax.serialization.to_bytes(source)
    processor = normalizer_state(source[0])
    policy_params = source[1]
    value_params = source[2]

    network = make_reference_residual_recurrent_adapter_ppo_networks(
        {
            "state": (OBSERVATION_SIZE,),
            "privileged_state": (PRIVILEGED_SIZE,),
            "policy_hidden": (HIDDEN_SIZE,),
        },
        ACTION_SIZE,
        preprocess_observations_fn=running_statistics.normalize,
        recurrent_hidden_size=HIDDEN_SIZE,
    )
    make_policy = make_recurrent_adapter_inference_fn(network)

    reset_base = jax.random.split(
        jax.random.PRNGKey(FORMAL_SEED + 202),
        environments,
    )
    action_keys = list(
        jax.random.split(
            jax.random.PRNGKey(FORMAL_SEED + 303),
            ticks,
        )
    )
    collected = {}
    rollout_metadata = {}
    for name in ("broad_v3", "negative_com_p30", "nominal_p30"):
        started = time.monotonic()
        data, metadata = collect_rollout(
            env=wrapped[name],
            make_policy=make_policy,
            processor=processor,
            policy_params=policy_params,
            reset_keys=reset_base,
            action_keys=action_keys,
            ticks=ticks,
        )
        metadata["wall_seconds"] = time.monotonic() - started
        metadata["model_readback"] = model_readback(wrapped[name])
        collected[name] = data
        rollout_metadata[name] = metadata
        print(
            f"T14_ROLLOUT={name},wall={metadata['wall_seconds']:.3f},"
            f"reward={metadata['reward_mean']:.6f},"
            f"terminations={metadata['termination_count']}",
            flush=True,
        )

    reset_pair_errors = {
        name: float(
            np.max(
                np.abs(
                    rollout_metadata[name]["initial_command"]
                    - rollout_metadata["negative_com_p30"]["initial_command"]
                )
            )
        )
        for name in ("broad_v3", "nominal_p30")
    }
    noise_pair_errors = {
        name: float(
            np.max(
                np.abs(
                    paired_standard_noise(collected[name])
                    - paired_standard_noise(collected["negative_com_p30"])
                )
            )
        )
        for name in ("broad_v3", "nominal_p30")
    }

    broad_updated_processor = running_statistics.update(
        processor,
        collected["broad_v3"].observation,
    )
    sequences = (ticks // unroll_length) * environments
    permutation = np.random.Generator(
        np.random.PCG64(FORMAL_SEED + 404)
    ).permutation(sequences)
    shuffled = {
        name: concatenate_windows(
            data,
            permutation,
            ticks=ticks,
            unroll_length=unroll_length,
        )
        for name, data in collected.items()
    }
    gradient_keys = list(
        jax.random.split(
            jax.random.PRNGKey(FORMAL_SEED + 505),
            minibatches,
        )
    )

    processors = {
        "broad_updated": broad_updated_processor,
        "source_frozen": processor,
    }
    all_gradients: dict[str, dict[str, list[Any]]] = {}
    all_metrics: dict[str, dict[str, list[dict[str, float]]]] = {}
    all_geometry: dict[str, Any] = {}
    for processor_id, selected_processor in processors.items():
        all_gradients[processor_id] = {}
        all_metrics[processor_id] = {}
        for domain in ("broad_v3", "negative_com_p30", "nominal_p30"):
            grads, metrics = gradient_batches(
                policy_params=policy_params,
                processor=selected_processor,
                value_params=value_params,
                shuffled_data=shuffled[domain],
                network=network,
                gradient_keys=gradient_keys,
                minibatches=minibatches,
                minibatch_size=sequences // minibatches,
            )
            all_gradients[processor_id][domain] = grads
            all_metrics[processor_id][domain] = metrics
        broad_mean = tree_mean(all_gradients[processor_id]["broad_v3"])
        negative_mean = tree_mean(
            all_gradients[processor_id]["negative_com_p30"]
        )
        nominal_mean = tree_mean(
            all_gradients[processor_id]["nominal_p30"]
        )
        replicate_geometry = [
            geometry(
                all_gradients[processor_id]["broad_v3"][index],
                all_gradients[processor_id]["negative_com_p30"][index],
            )
            for index in range(minibatches)
        ]
        all_geometry[processor_id] = {
            "broad_vs_negative_com": geometry(
                broad_mean,
                negative_mean,
            ),
            "nominal_vs_negative_com": geometry(
                nominal_mean,
                negative_mean,
            ),
            "broad_vs_nominal": geometry(
                broad_mean,
                nominal_mean,
            ),
            "broad_vs_negative_com_minibatches": replicate_geometry,
            "negative_harmed_minibatches": sum(
                row[
                    "right_loss_derivative_along_left_descent"
                ]
                > 0.0
                for row in replicate_geometry
            ),
        }

    primary = all_geometry["broad_updated"]["broad_vs_negative_com"]
    sensitivity = all_geometry["source_frozen"]["broad_vs_negative_com"]
    tolerance = (
        64.0
        * float(np.finfo(np.float32).eps)
        * max(
            1.0,
            abs(primary["gradient_dot"]),
            primary["left_gradient_norm"]
            * primary["right_gradient_norm"],
        )
    )
    negative_readback = rollout_metadata["negative_com_p30"][
        "model_readback"
    ]
    broad_readback = rollout_metadata["broad_v3"]["model_readback"]
    nominal_readback = rollout_metadata["nominal_p30"]["model_readback"]
    nominal_x = nominal_model_x
    expected_negative_x = nominal_x + COM_NEGATIVE_OFFSET_M

    source_after = flax.serialization.to_bytes(source)
    checks = {
        "cpu_only": True,
        "formal_dimensions_exact": (
            environments == FORMAL_ENVIRONMENTS
            and ticks == FORMAL_TICKS
            and len(permutation) == 20_480
        ),
        "all_rollouts_finite": all(
            row["finite"] for row in rollout_metadata.values()
        ),
        "paired_initial_commands_bit_exact": max(
            reset_pair_errors.values()
        )
        == 0.0,
        "paired_standardized_action_noise_within_2e_6": max(
            noise_pair_errors.values()
        )
        <= 2.0e-6,
        "negative_com_readback_exact": (
            negative_readback["torso_com_x_unique_count"] == 1
            and math.isclose(
                negative_readback["torso_com_x_min_m"],
                expected_negative_x,
                rel_tol=0.0,
                abs_tol=2.0e-7,
            )
            and math.isclose(
                negative_readback["torso_com_x_max_m"],
                expected_negative_x,
                rel_tol=0.0,
                abs_tol=2.0e-7,
            )
        ),
        "nominal_com_readback_exact": (
            nominal_readback["torso_com_x_unique_count"] == 1
            and math.isclose(
                nominal_readback["torso_com_x_min_m"],
                nominal_x,
                rel_tol=0.0,
                abs_tol=2.0e-7,
            )
        ),
        "broad_com_support_within_frozen_bounds": (
            broad_readback["torso_com_x_min_m"]
            >= nominal_x - 0.0500002
            and broad_readback["torso_com_x_max_m"]
            <= nominal_x + 0.0500002
            and broad_readback["torso_com_x_unique_count"] > 1
        ),
        "all_gradients_finite": all(
            tree_finite(gradient)
            for processor_rows in all_gradients.values()
            for domain_rows in processor_rows.values()
            for gradient in domain_rows
        ),
        "primary_gradients_nonzero": (
            primary["left_gradient_norm"] > 0.0
            and primary["right_gradient_norm"] > 0.0
        ),
        "primary_broad_and_negative_gradients_conflict": (
            primary["gradient_cosine"] < 0.0
        ),
        "primary_broad_descent_strictly_harms_negative_com": (
            primary[
                "right_loss_derivative_along_left_descent"
            ]
            > tolerance
        ),
        "at_least_three_of_four_minibatches_show_harm": (
            all_geometry["broad_updated"][
                "negative_harmed_minibatches"
            ]
            >= 3
        ),
        "source_normalizer_sensitivity_preserves_harm_sign": (
            sensitivity[
                "right_loss_derivative_along_left_descent"
            ]
            > tolerance
            and sensitivity["gradient_cosine"] < 0.0
        ),
        "source_checkpoint_bytes_unchanged": source_before == source_after,
        "no_optimizer_steps": True,
        "no_behavior_cells": True,
    }
    if not formal:
        checks = {
            "cpu_only": True,
            "all_rollouts_finite": all(
                row["finite"] for row in rollout_metadata.values()
            ),
            "paired_initial_commands_bit_exact": max(
                reset_pair_errors.values()
            )
            == 0.0,
            "paired_standardized_action_noise_within_2e_6": max(
                noise_pair_errors.values()
            )
            <= 2.0e-6,
            "negative_com_readback_exact": checks[
                "negative_com_readback_exact"
            ],
            "all_gradients_finite": checks["all_gradients_finite"],
            "source_checkpoint_bytes_unchanged": (
                source_before == source_after
            ),
            "no_optimizer_steps": True,
            "no_behavior_cells": True,
        }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    payload = {
        "schema_version": "open_duck.t14_domain_gradient_geometry_result.v1",
        "status": (
            (
                "PASS_T14_DOMAIN_GRADIENT_GEOMETRY"
                if formal
                else "PASS_T14_DOMAIN_GRADIENT_GEOMETRY_SMOKE"
            )
            if passed
            else (
                "HOLD_T14_DOMAIN_GRADIENT_GEOMETRY"
                if formal
                else "HOLD_T14_DOMAIN_GRADIENT_GEOMETRY_SMOKE"
            )
        ),
        "failed_checks": failed,
        "checks": checks,
        "decision": (
            (
                "EARN_WORST_DOMAIN_OBJECTIVE_CPU_CONTRACT_ONLY"
                if formal
                else "SMOKE_PLUMBING_ONLY"
            )
            if passed
            else (
                "CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF"
                if formal
                else "FIX_SMOKE_BEFORE_PREREGISTRATION"
            )
        ),
        "dimensions": {
            "environments_per_domain": environments,
            "ticks_per_environment": ticks,
            "unroll_length": unroll_length,
            "minibatches": minibatches,
            "sequences_per_domain": (
                environments * ticks // unroll_length
            ),
            "observations_per_domain": environments * ticks,
            "optimizer_steps": 0,
            "behavior_cells": 0,
        },
        "rollouts": {
            name: {
                key: value
                for key, value in row.items()
                if key != "initial_command"
            }
            for name, row in rollout_metadata.items()
        },
        "pairing": {
            "initial_command_max_abs_error": reset_pair_errors,
            "standardized_action_noise_max_abs_error": noise_pair_errors,
        },
        "normalizer": {
            "source_count": processor_count(processor),
            "broad_updated_count": processor_count(
                broad_updated_processor
            ),
            "state_mean_max_abs_delta": float(
                np.max(
                    np.abs(
                        np.asarray(
                            broad_updated_processor.mean["state"]
                        )
                        - np.asarray(processor.mean["state"])
                    )
                )
            ),
        },
        "geometry": all_geometry,
        "gradient_metrics": all_metrics,
        "float32_directional_tolerance": tolerance,
        "source_checkpoint": {
            "path": str(SOURCE),
            "directory_sha256": sha256_directory(SOURCE),
            "bytes_unchanged": source_before == source_after,
        },
        "execution": {
            "platform": "cpu",
            "devices": [str(device) for device in jax.devices()],
            "work_root": str(work),
            "formal_seed": FORMAL_SEED,
            "permutation_sha256": hashlib.sha256(
                permutation.astype(np.int64).tobytes()
            ).hexdigest(),
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "candidate_selection": False,
            "behavior_or_robustness_matrix": False,
            "deployment_or_gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "next_authority": (
                "CPU implementation contract only" if passed else "none"
            ),
        },
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument(
        "--work-root",
        type=Path,
        default=DEFAULT_WORK_ROOT,
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    work = args.work_root.resolve()
    formal = not args.smoke
    if work.exists():
        raise FileExistsError(f"refusing to overwrite T14 work: {work}")
    if formal and (RESULT.exists() or MARKDOWN.exists()):
        raise FileExistsError("refusing to overwrite formal T14 evidence")
    if not SOURCE.exists() or not CPU_TEMPLATE.exists():
        raise FileNotFoundError("permanent D: checkpoint inputs are missing")
    if formal:
        prereg = json.loads(PREREG.read_text(encoding="utf-8"))
        if (
            prereg.get("status")
            != "PREREGISTERED_T14_DOMAIN_GRADIENT_GEOMETRY"
            or prereg.get("failed_checks") != []
        ):
            raise ValueError("T14 preregistration is not green")
        observed_hashes = source_inputs(prereg, playground)
    else:
        observed_hashes = {}

    started = time.monotonic()
    payload = run(
        playground=playground,
        work=work,
        environments=(FORMAL_ENVIRONMENTS if formal else 4),
        ticks=(FORMAL_TICKS if formal else 4),
        formal=formal,
    )
    payload["execution"]["wall_seconds"] = time.monotonic() - started
    payload["input_hashes"] = observed_hashes
    if formal:
        payload["input_hashes"]["preregistration"] = sha256(PREREG)
        RESULT.write_text(
            json.dumps(
                payload,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        primary = payload["geometry"]["broad_updated"][
            "broad_vs_negative_com"
        ]
        MARKDOWN.write_text(
            "\n".join(
                [
                    "# T14 domain-gradient geometry result",
                    "",
                    f"- Status: `{payload['status']}`",
                    f"- Decision: `{payload['decision']}`",
                    (
                        "- Broad vs negative-COM gradient cosine: "
                        f"`{primary['gradient_cosine']}`"
                    ),
                    (
                        "- Negative-COM loss derivative along broad descent: "
                        f"`{primary['right_loss_derivative_along_left_descent']}`"
                    ),
                    (
                        "- Harm-sign minibatches: "
                        f"`{payload['geometry']['broad_updated']['negative_harmed_minibatches']}/4`"
                    ),
                    f"- Failed checks: `{payload['failed_checks']}`",
                    (
                        "- CPU-only; zero optimizer steps, behavior cells, "
                        "hosted compute, hardware, torque, or motion."
                    ),
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
    else:
        smoke_path = work / "smoke_result.json"
        smoke_path.write_text(
            json.dumps(
                payload,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "decision": payload["decision"],
                "failed_checks": payload["failed_checks"],
                "formal": formal,
                "wall_seconds": payload["execution"]["wall_seconds"],
            }
        ),
        flush=True,
    )
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
