#!/usr/bin/env python3
"""Run the preregistered Winner-v98 response-conditioned CPU smoke."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

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
ANALYSIS = ROOT / "outputs/analysis"
PATCHES = ROOT / "patches"
PREREGISTRATION = (
    ANALYSIS / "winner_v101_response_conditioned_cpu_retry_preregistration.json"
)
OUTPUT_JSON = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
OUTPUT_MD = ANALYSIS / "WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT_20260722.md"
POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
GOLDENS = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.000.npz",
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.080.npz",
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
BASE_KEYS = ("residual_trunk", "residual_location", "scale_logits")
ADAPTER_MAPPING = {
    "adapter_obs_weight": "obs_weight",
    "adapter_previous_action_weight": "previous_action_weight",
    "adapter_hidden_weight": "hidden_weight",
    "adapter_context_hidden_weight": "context_hidden_weight",
    "adapter_hidden_bias": "hidden_bias",
    "adapter_hidden_action_weight": "hidden_action_weight",
    "adapter_context_action_weight": "context_action_weight",
    "adapter_action_bias": "action_bias",
}
VELOCITY_LIMITS = "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout.strip()


@contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(entry, "key", getattr(entry, "idx", entry))) for entry in path
    )


def leaf_deltas(initial: Any, final: Any) -> dict[str, float]:
    initial_rows, structure = jax.tree_util.tree_flatten_with_path(initial)
    final_rows, final_structure = jax.tree_util.tree_flatten_with_path(final)
    if structure != final_structure:
        raise ValueError("Winner-v98 trained actor tree structure changed")
    result = {}
    for (initial_path, before), (final_path, after) in zip(
        initial_rows, final_rows, strict=True
    ):
        if initial_path != final_path:
            raise ValueError("Winner-v98 trained actor leaf ordering changed")
        result[path_name(initial_path)] = float(
            np.max(np.abs(np.asarray(after) - np.asarray(before)))
        )
    return result


def numeric_tree_finite(value: Any) -> bool:
    for leaf in jax.tree_util.tree_leaves(value):
        array = np.asarray(leaf)
        if array.dtype.kind in "biufc" and not np.isfinite(array).all():
            return False
    return True


def tree_error(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(after) - np.asarray(before))))
        for before, after in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def source_template(base_networks: Any) -> list[Any]:
    key_policy, key_value = jax.random.split(jax.random.PRNGKey(100))
    return [
        {
            "mean": {
                "state": jnp.zeros(115, dtype=jnp.float32),
                "privileged_state": jnp.zeros(226, dtype=jnp.float32),
            },
            "std": {
                "state": jnp.ones(115, dtype=jnp.float32),
                "privileged_state": jnp.ones(226, dtype=jnp.float32),
            },
            "count": {
                "hi": jnp.asarray(0, dtype=jnp.uint32),
                "lo": jnp.asarray(0, dtype=jnp.uint32),
            },
            "summed_variance": {
                "state": jnp.ones(115, dtype=jnp.float32),
                "privileged_state": jnp.ones(226, dtype=jnp.float32),
            },
            "std_eps": jnp.asarray(1.0e-6, dtype=jnp.float32),
        },
        base_networks.policy_network.init(key_policy),
        base_networks.value_network.init(key_value),
    ]


def normalizer_state(value: Mapping[str, Any]) -> Any:
    from brax.training import types
    from brax.training.acme import running_statistics

    return running_statistics.RunningStatisticsState(
        mean=value["mean"],
        std=value["std"],
        count=types.UInt64(hi=value["count"]["hi"], lo=value["count"]["lo"]),
        summed_variance=value["summed_variance"],
        std_eps=value["std_eps"],
    )


def expand_checkpoint(source: list[Any], response_networks: Any, v96: Any) -> list[Any]:
    initialized = flax.core.unfreeze(
        response_networks.policy_network.init(jax.random.PRNGKey(60798))
    )
    source_policy = flax.core.unfreeze(source[1])
    for key in BASE_KEYS:
        initialized["params"][key] = copy.deepcopy(source_policy["params"][key])
    initialized["params"]["protected_obs_mean"] = copy.deepcopy(
        source[0]["mean"]["state"]
    )
    initialized["params"]["protected_obs_std"] = copy.deepcopy(
        source[0]["std"]["state"]
    )
    adapter = v96.initialize_locomotion_adapter_parameters(seed=60721)
    for destination, source_name in ADAPTER_MAPPING.items():
        initialized["params"][destination] = copy.deepcopy(adapter[source_name])
    expanded = copy.deepcopy(source)
    expanded[1] = initialized
    count = np.float32(np.asarray(source[0]["count"]["lo"]))
    for name, width in (
        ("policy_hidden", 64),
        ("calibration_context", 64),
        ("policy_previous_action", 14),
    ):
        expanded[0]["mean"][name] = jnp.zeros(width, dtype=jnp.float32)
        expanded[0]["std"][name] = jnp.ones(width, dtype=jnp.float32)
        expanded[0]["summed_variance"][name] = jnp.full(
            width, count, dtype=jnp.float32
        )
    return expanded


def validate_preregistration(value: Mapping[str, Any], playground: Path) -> None:
    if (
        value.get("schema_version")
        != "winner_v101.response_conditioned_cpu_retry_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V101_RESPONSE_CONDITIONED_CPU_RETRY"
        or value.get("decision")
        != "AUTHORIZE_ONE_LAZY_IMPORT_CORRECTED_1024_STEP_CPU_SMOKE_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v101 preregistration identity changed")
    for name, item in value["sources"].items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v101 source changed: {name}")
    for name, item in value["repository_binaries"].items():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v101 binary changed: {name}")
    if git_output(playground, "rev-parse", "HEAD") != CONTROL_COMMIT:
        raise ValueError("Winner-v101 Playground control commit changed")
    for relative, expected in value["composed_playground_files"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"Winner-v101 composed source changed: {relative}")


def make_environment(reference: Path, calibrator: Path) -> Any:
    from playground.common import winner_v3_variable_configuration as winner_v3
    from playground.common.winner_v98_response_calibration_wrapper import (
        wrap_response_calibration,
    )
    from playground.open_duck_mini_v2 import joystick

    config = joystick.default_config()
    config.reward_config.scales.imitation = 1.0
    config.reference_feature_table_path = str(reference)
    config.recurrent_hidden_dim = 64
    config.nominal_reference_bootstrap = True
    config.nominal_reference_command_x = 0.074
    config.ground_up_hard_vector_command_support = True
    config.ground_up_command_support_range = [0.074, 0.080]
    config.ground_up_action_velocity_limits_rad_s = [
        float(value) for value in VELOCITY_LIMITS.split(",")
    ]
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_applied_target_observation = True
    config.reward_config.scales.tracking_tail_exceedance = -6572.254964031055
    config.ground_up_tracking_tail_threshold_rad = 0.20
    config.ground_up_actuator_bridge_delay_ticks = [
        3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 2, 3, 2, 3
    ]
    config.ground_up_actuator_bridge_tau_s = [
        0.015,
        0.015,
        0.005,
        0.010,
        0.010,
        0.120,
        0.120,
        0.120,
        0.120,
        0.020,
        0.035,
        0.010,
        0.030,
        0.005,
    ]
    config.reference_start_phase = 0
    config.ground_up_signed_progress_objective = True
    config.winner_v3_variable_configuration = True
    config.winner_v3_deviation_scale = 0.0
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 3
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 3
    config.push_config.enable = False
    if not bool(
        jnp.array_equal(
            jnp.asarray(config.ground_up_action_velocity_limits_rad_s),
            winner_v3.CONSERVATIVE_VELOCITY_LIMITS_RAD_S,
        )
    ):
        raise ValueError("Winner-v98 conservative action vector changed")
    return wrap_response_calibration(
        joystick.Joystick(task="flat_terrain_backlash", config=config),
        calibrator,
        calibration_ticks=250,
        home_return_ticks=250,
    )


def check_wrapper_reset(
    playground: Path, reference: Path, calibrator: Path
) -> dict[str, Any]:
    with working_directory(playground):
        env = make_environment(reference, calibrator)
        state = jax.jit(env.reset)(jax.random.PRNGKey(100))
        next_state = jax.jit(env.step)(state, jnp.zeros(14, dtype=jnp.float32))
    context = np.asarray(state.obs["calibration_context"])
    command = np.asarray(state.info["command"])
    previous = np.asarray(state.obs["policy_previous_action"])
    hidden = np.asarray(state.obs["policy_hidden"])
    return {
        "observation_shapes": {
            key: list(np.asarray(value).shape) for key, value in state.obs.items()
        },
        "calibration_context_sha256": hashlib.sha256(
            np.ascontiguousarray(context).tobytes()
        ).hexdigest(),
        "calibration_context_linf": float(np.max(np.abs(context))),
        "command": command.tolist(),
        "phase": np.asarray(state.info["imitation_phase"]).tolist(),
        "step": int(np.asarray(state.info["step"])),
        "valid": bool(np.asarray(state.info["response_calibration_valid"])),
        "calibration_ticks": int(
            np.asarray(state.info["response_calibration_ticks"])
        ),
        "done": float(np.asarray(state.done)),
        "previous_action_max_abs": float(np.max(np.abs(previous))),
        "policy_hidden_max_abs": float(np.max(np.abs(hidden))),
        "context_immutable_one_step": bool(
            np.array_equal(
                context, np.asarray(next_state.obs["calibration_context"])
            )
        ),
        "all_finite": bool(
            np.isfinite(context).all()
            and np.isfinite(np.asarray(state.obs["state"])).all()
            and np.isfinite(np.asarray(state.obs["privileged_state"])).all()
        ),
    }


def run_training(
    playground: Path,
    expanded: Path,
    output: Path,
    calibrator: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task",
        "flat_terrain_backlash",
        "--env",
        "joystick",
        "--output_dir",
        str(output),
        "--num_timesteps",
        "1024",
        "--ppo_seed",
        "100",
        "--ppo_num_envs",
        "4",
        "--ppo_num_evals",
        "2",
        "--ppo_episode_length",
        "600",
        "--ppo_unroll_length",
        "8",
        "--ppo_batch_size",
        "4",
        "--ppo_num_minibatches",
        "1",
        "--ppo_num_updates_per_batch",
        "2",
        "--ppo_learning_rate",
        "0.0003",
        "--ppo_discounting",
        "0.97",
        "--ppo_entropy_cost",
        "0.005",
        "--policy_architecture",
        "response_conditioned_reference_residual",
        "--recurrent_hidden_size",
        "64",
        "--winner_v98_protected_policy_path",
        str(POLICY),
        "--winner_v98_calibrator_path",
        str(calibrator),
        "--winner_v98_calibration_ticks",
        "250",
        "--winner_v98_home_return_ticks",
        "250",
        "--imitation_scale",
        "1.0",
        "--reference_feature_table_path",
        str(REFERENCE),
        "--nominal_reference_bootstrap",
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x",
        "0.074",
        "--ground_up_command_support_max_x",
        "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        VELOCITY_LIMITS,
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale",
        "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad",
        "0.20",
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "0.25",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(expanded),
    ]
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONPATH": str(playground),
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
        }
    )
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=3600,
        check=False,
    )
    elapsed = time.monotonic() - started
    log = output.parent / "winner_v98_response_conditioned_cpu_smoke.log"
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"Winner-v98 CPU smoke failed rc={completed.returncode}; log={log}; "
            f"tail={completed.stdout[-6000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    graphs = sorted(output.glob("*.onnx"))
    final_checkpoints = [path for path in checkpoints if path.name.endswith("_1024")]
    final_graphs = [path for path in graphs if path.stem.endswith("_1024")]
    if len(final_checkpoints) != 1 or len(final_graphs) != 1:
        raise RuntimeError(f"Winner-v98 smoke exports changed: {checkpoints}, {graphs}")
    return {
        "command": command,
        "elapsed_seconds": elapsed,
        "log_path": str(log),
        "log_sha256": sha256(log),
        "final_checkpoint": final_checkpoints[0],
        "final_onnx": final_graphs[0],
        "checkpoint_steps": sorted(
            int(path.name.rsplit("_", 1)[1]) for path in checkpoints
        ),
        "onnx_steps": sorted(int(path.stem.rsplit("_", 1)[1]) for path in graphs),
    }


def describe_onnx(path: Path) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    import onnx

    model = onnx.load(path)

    def values(items: Any) -> dict[str, list[int]]:
        return {
            item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim]
            for item in items
        }

    return values(model.graph.input), values(model.graph.output)


def graph_boundary_contract(path: Path) -> dict[str, Any]:
    import onnx
    from onnx import numpy_helper

    model = onnx.load(path)
    protected = onnx.load(POLICY)
    values = {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }
    protected_values = {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in protected.graph.initializer
    }
    inherited = (
        "max_action_delta",
        "guard_joint_obs_indices",
        "guard_home",
        "guard_action_scale",
        "guard_margin",
        "guard_pitch_mask",
        "guard_action_min",
        "guard_action_max",
        "deadband_command_index",
        "deadband_abs_limit",
        "deadband_zero_action",
    )
    initializers_exact = all(
        name in values
        and name in protected_values
        and np.array_equal(values[name], protected_values[name])
        for name in inherited
    )
    producer = {
        output: (node.op_type, list(node.input))
        for node in model.graph.node
        for output in node.output
    }
    expected = {
        "v98_absolute": (
            "Clip",
            ["v98_proposed", "v98_action_minimum", "v98_action_maximum"],
        ),
        "v98_rate_lower_raw": (
            "Sub",
            ["previous_action", "max_action_delta"],
        ),
        "v98_rate_upper_raw": (
            "Add",
            ["previous_action", "max_action_delta"],
        ),
        "v98_rate_bounded": (
            "Max",
            ["v98_rate_below", "v98_rate_lower"],
        ),
        "v98_actual_target": (
            "Add",
            ["guard_home", "v98_joint_offsets"],
        ),
        "v98_target_clipped": (
            "Min",
            ["v98_target_above", "v98_target_max"],
        ),
        "v98_guarded_action": (
            "Where",
            ["guard_pitch_mask", "v98_pitch_action", "v98_rate_bounded"],
        ),
        "continuous_actions": (
            "Where",
            ["v98_zero_command", "deadband_zero_action", "v98_guarded_action"],
        ),
        "previous_action_out": ("Identity", ["continuous_actions"]),
    }
    node_hierarchy_exact = all(producer.get(name) == value for name, value in expected.items())
    return {
        "inherited_initializers_exact": initializers_exact,
        "boundary_node_hierarchy_exact": node_hierarchy_exact,
        "exact": initializers_exact and node_hierarchy_exact,
    }


def graph_jax_equivalence(
    graph: Path,
    response_networks: Any,
    policy_parameters: Any,
    *,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    rng = np.random.Generator(np.random.PCG64(seed))
    maximum_exact_action_error = 0.0
    maximum_mode_action_error = 0.0
    maximum_hidden_error = 0.0
    saturated_mode_mismatch_cases = 0
    x0_exact = True
    for index in range(cases):
        observation = rng.normal(0.0, 0.15, (1, 115)).astype(np.float32)
        observation[:, 6] = np.float32(0.0 if index % 7 == 0 else 0.08)
        previous = rng.uniform(-0.5, 0.5, (1, 14)).astype(np.float32)
        hidden = rng.uniform(-0.5, 0.5, (1, 64)).astype(np.float32)
        context = rng.uniform(-1.0, 1.0, (1, 64)).astype(np.float32)
        observation_mapping = {
            "state": jnp.asarray(observation),
            "policy_hidden": jnp.asarray(hidden),
            "calibration_context": jnp.asarray(context),
            "policy_previous_action": jnp.asarray(previous),
        }
        logits, expected_hidden = response_networks.policy_network.apply_with_state(
            None,
            policy_parameters,
            observation_mapping,
        )
        expected_action, exact_hidden = (
            response_networks.policy_network.apply_action_with_state(
                None, policy_parameters, observation_mapping
            )
        )
        mode_action = np.tanh(np.asarray(logits)[:, :14])
        actual_action, previous_out, actual_hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        maximum_exact_action_error = max(
            maximum_exact_action_error,
            float(np.max(np.abs(actual_action - np.asarray(expected_action)))),
            float(np.max(np.abs(previous_out - actual_action))),
        )
        mode_error = float(np.max(np.abs(actual_action - mode_action)))
        maximum_mode_action_error = max(maximum_mode_action_error, mode_error)
        if mode_error > 1.0e-6:
            if not np.any(np.abs(actual_action) == 1.0):
                raise ValueError("Winner-v101 nonsaturated PPO-mode mismatch")
            saturated_mode_mismatch_cases += 1
        maximum_hidden_error = max(
            maximum_hidden_error,
            float(np.max(np.abs(actual_hidden - np.asarray(expected_hidden)))),
            float(np.max(np.abs(actual_hidden - np.asarray(exact_hidden)))),
        )
        if observation[0, 6] == 0.0:
            x0_exact &= bool(np.count_nonzero(actual_action) == 0)
    return {
        "cases": cases,
        "providers": session.get_providers(),
        "maximum_exact_action_error": maximum_exact_action_error,
        "maximum_ppo_mode_action_error": maximum_mode_action_error,
        "maximum_hidden_error": maximum_hidden_error,
        "saturated_ppo_mode_mismatch_cases": saturated_mode_mismatch_cases,
        "x0_exact_zero": x0_exact,
    }


def golden_zero_update(graph: Path) -> dict[str, Any]:
    import onnxruntime as ort

    selected = ort.InferenceSession(str(POLICY), providers=["CPUExecutionProvider"])
    response = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    maximum_selected_error = 0.0
    maximum_golden_error = 0.0
    maximum_golden_rate_excess = 0.0
    x0_exact = True
    ticks = 0
    for path in GOLDENS:
        data = np.load(path)
        hidden = np.zeros((1, 64), dtype=np.float32)
        context = np.zeros((1, 64), dtype=np.float32)
        for observation, previous, expected in zip(
            data["obs"], data["previous_action_in"], data["final_action"], strict=True
        ):
            observation = observation[None].astype(np.float32)
            previous = previous[None].astype(np.float32)
            selected_action, _ = selected.run(
                ["continuous_actions", "previous_action_out"],
                {"obs": observation, "previous_action": previous},
            )
            action, previous_out, hidden = response.run(
                ["continuous_actions", "previous_action_out", "h_out"],
                {
                    "obs": observation,
                    "previous_action": previous,
                    "h_in": hidden,
                    "calibration_context": context,
                },
            )
            maximum_selected_error = max(
                maximum_selected_error,
                float(np.max(np.abs(action - selected_action))),
                float(np.max(np.abs(previous_out - action))),
            )
            maximum_golden_error = max(
                maximum_golden_error,
                float(np.max(np.abs(action[0] - expected))),
            )
            from playground.common.winner_v98_response_conditioned_ppo_networks import (
                MAX_ACTION_DELTA,
            )

            maximum_golden_rate_excess = max(
                maximum_golden_rate_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(action - previous)
                            - np.asarray(MAX_ACTION_DELTA)[None, :],
                            0.0,
                        )
                    )
                ),
            )
            if float(observation[0, 6]) == 0.0:
                x0_exact &= bool(np.count_nonzero(action) == 0)
            ticks += 1
    return {
        "ticks": ticks,
        "maximum_selected_graph_error": maximum_selected_error,
        "maximum_golden_error": maximum_golden_error,
        "maximum_golden_rate_excess": maximum_golden_rate_excess,
        "x0_exact_zero": x0_exact,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--cpu-smoke-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.cpu_smoke_authorized:
        raise PermissionError(
            "Winner-v98 requires --offline-cpu-only --cpu-smoke-authorized"
        )
    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    calibrator = args.calibrator.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing Winner-v98 retry/resume: {work}")
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("refusing to overwrite Winner-v98 formal result")
    work.mkdir(parents=True)

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration, playground)
    observed_versions = {
        name: importlib.metadata.version(name)
        for name in preregistration["software_versions"]
    }
    external = preregistration["external_binaries"]
    if directory_sha256(source_checkpoint) != external["source_checkpoint"]["sha256"]:
        raise ValueError("Winner-v98 source checkpoint changed")
    if sha256(calibrator) != external["calibrator_onnx"]["sha256"]:
        raise ValueError("Winner-v98 calibrator changed")

    sys.path.insert(0, str(playground))
    sys.path.insert(0, str(PATCHES))
    from brax.training.acme import running_statistics
    from playground.common.reference_residual_ppo_networks import (
        make_reference_residual_ppo_networks,
    )
    from playground.common.winner_v98_response_conditioned_export import (
        export_response_conditioned_onnx,
    )
    from playground.common.winner_v98_response_conditioned_ppo_networks import (
        make_response_conditioned_ppo_networks,
    )
    import winner_v96_response_conditioned_networks as v96

    devices = [str(device) for device in jax.devices()]
    cpu_only = bool(devices) and all(device.platform == "cpu" for device in jax.devices())
    base_observation_size = {"state": (115,), "privileged_state": (226,)}
    response_observation_size = {
        **base_observation_size,
        "policy_hidden": (64,),
        "calibration_context": (64,),
        "policy_previous_action": (14,),
    }
    base_networks = make_reference_residual_ppo_networks(
        base_observation_size,
        14,
        preprocess_observations_fn=running_statistics.normalize,
    )
    response_networks = make_response_conditioned_ppo_networks(
        response_observation_size,
        14,
        preprocess_observations_fn=running_statistics.normalize,
        recurrent_hidden_size=64,
    )
    template = source_template(base_networks)
    checkpointer = ocp.PyTreeCheckpointer()
    source = checkpointer.restore(
        str(source_checkpoint),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )
    expanded = expand_checkpoint(source, response_networks, v96)
    expanded_path = work / "expanded_checkpoint"
    checkpointer.save(str(expanded_path), expanded)
    restored_expanded = checkpointer.restore(str(expanded_path))
    round_trip_structure, round_trip_error = tree_error(expanded, restored_expanded)
    initial_parameters = flax.core.unfreeze(restored_expanded[1])["params"]
    source_parameters = flax.core.unfreeze(source[1])["params"]

    base_exact = all(
        jax.tree_util.tree_structure(source_parameters[key])
        == jax.tree_util.tree_structure(initial_parameters[key])
        and all(
            np.array_equal(np.asarray(left), np.asarray(right))
            for left, right in zip(
                jax.tree_util.tree_leaves(source_parameters[key]),
                jax.tree_util.tree_leaves(initial_parameters[key]),
                strict=True,
            )
        )
        for key in BASE_KEYS
    )
    protected_normalizer_exact = bool(
        np.array_equal(
            np.asarray(initial_parameters["protected_obs_mean"]),
            np.asarray(source[0]["mean"]["state"]),
        )
        and np.array_equal(
            np.asarray(initial_parameters["protected_obs_std"]),
            np.asarray(source[0]["std"]["state"]),
        )
    )
    initial_graph = work / "winner_v98_step_zero.onnx"
    export_response_conditioned_onnx(
        restored_expanded,
        POLICY,
        initial_graph,
    )
    golden = golden_zero_update(initial_graph)
    initial_equivalence = graph_jax_equivalence(
        initial_graph,
        response_networks,
        restored_expanded[1],
        seed=60798,
        cases=64,
    )
    initial_boundary = graph_boundary_contract(initial_graph)
    reset = check_wrapper_reset(playground, REFERENCE, calibrator)

    pretraining_checks = {
        "cpu_only_jax": cpu_only,
        "software_versions_exact": observed_versions
        == preregistration["software_versions"],
        "source_checkpoint_structure_exact": (
            jax.tree_util.tree_structure(source)
            == jax.tree_util.tree_structure(template)
        ),
        "expanded_checkpoint_round_trip_exact": round_trip_structure
        and round_trip_error == 0.0,
        "protected_base_actor_bit_exact": base_exact,
        "protected_normalizer_bit_exact": protected_normalizer_exact,
        "golden_population_exact": golden["ticks"] == 1200,
        "zero_update_selected_graph_within_1e_6": golden[
            "maximum_selected_graph_error"
        ]
        <= 1.0e-6,
        "zero_update_golden_within_1e_6": golden["maximum_golden_error"] <= 1.0e-6,
        "zero_update_x0_exact": golden["x0_exact_zero"],
        "initial_exact_action_jax_onnx_within_1e_6": max(
            initial_equivalence["maximum_exact_action_error"],
            initial_equivalence["maximum_hidden_error"],
        )
        <= 1.0e-6,
        "initial_ppo_mode_representation_within_1p1e_5": initial_equivalence[
            "maximum_ppo_mode_action_error"
        ]
        <= 1.1e-5,
        "initial_graph_boundary_hierarchy_exact": initial_boundary["exact"],
        "golden_final_rate_excess_within_1e_6": golden[
            "maximum_golden_rate_excess"
        ]
        <= 1.0e-6,
        "reset_observation_abi_exact": reset["observation_shapes"].get("state")
        == [115]
        and reset["observation_shapes"].get("policy_hidden") == [64]
        and reset["observation_shapes"].get("calibration_context") == [64]
        and reset["observation_shapes"].get("policy_previous_action") == [14],
        "reset_calibration_exact_250_valid_ticks": reset["valid"]
        and reset["calibration_ticks"] == 250,
        "reset_phase_zero_observe_state_exact": reset["phase"] == [1.0, 0.0]
        and reset["step"] == 0,
        "reset_handoff_finite_nonzero": reset["all_finite"]
        and reset["calibration_context_linf"] > 0.0,
        "reset_policy_state_zero": reset["policy_hidden_max_abs"] == 0.0,
        "reset_previous_action_home_zero": reset["previous_action_max_abs"] == 0.0,
        "reset_context_immutable": reset["context_immutable_one_step"],
    }
    failed_pretraining = sorted(
        name for name, passed in pretraining_checks.items() if not passed
    )
    if failed_pretraining:
        raise RuntimeError(f"Winner-v101 pretraining contract failed: {failed_pretraining}")

    smoke_output = work / "smoke"
    smoke_output.mkdir()
    training = run_training(playground, expanded_path, smoke_output, calibrator)
    trained = checkpointer.restore(str(training["final_checkpoint"]))
    trained_parameters = flax.core.unfreeze(trained[1])["params"]
    deltas = leaf_deltas(initial_parameters, trained_parameters)
    protected_names = (*BASE_KEYS, "protected_obs_mean", "protected_obs_std")
    protected_delta = max(
        (
            value
            for name, value in deltas.items()
            if any(token in name for token in protected_names)
        ),
        default=0.0,
    )
    adapter_state_delta = max(
        (
            value
            for name, value in deltas.items()
            if any(
                token in name
                for token in (
                    "adapter_obs_weight",
                    "adapter_previous_action_weight",
                    "adapter_hidden_weight",
                    "adapter_hidden_bias",
                )
            )
        ),
        default=0.0,
    )
    adapter_context_delta = max(
        (
            value
            for name, value in deltas.items()
            if "adapter_context" in name
        ),
        default=0.0,
    )
    adapter_action_delta = max(
        (
            value
            for name, value in deltas.items()
            if any(
                token in name
                for token in (
                    "adapter_hidden_action_weight",
                    "adapter_context_action_weight",
                    "adapter_action_bias",
                )
            )
        ),
        default=0.0,
    )
    value_delta = max(
        leaf_deltas(source[2], trained[2]).values(), default=0.0
    )
    final_graph = Path(training["final_onnx"])
    graph_inputs, graph_outputs = describe_onnx(final_graph)
    final_equivalence = graph_jax_equivalence(
        final_graph,
        response_networks,
        trained[1],
        seed=60799,
        cases=256,
    )
    final_boundary = graph_boundary_contract(final_graph)
    expected_inputs = {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
        "calibration_context": [1, 64],
    }
    expected_outputs = {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    }
    checks = {
        **pretraining_checks,
        "smoke_exports_exact_steps": training["checkpoint_steps"] == [0, 1024]
        and training["onnx_steps"] == [0, 1024],
        "trained_tree_numeric_leaves_finite": numeric_tree_finite(trained),
        "protected_actor_and_normalizer_unchanged": protected_delta == 0.0,
        "adapter_state_path_updated": adapter_state_delta > 0.0,
        "adapter_context_path_updated": adapter_context_delta > 0.0,
        "adapter_action_path_updated": adapter_action_delta > 0.0,
        "critic_updated": value_delta > 0.0,
        "trained_onnx_abi_exact": graph_inputs == expected_inputs
        and graph_outputs == expected_outputs,
        "trained_onnx_cpu_provider": final_equivalence["providers"]
        == ["CPUExecutionProvider"],
        "trained_exact_action_jax_onnx_within_1e_6": max(
            final_equivalence["maximum_exact_action_error"],
            final_equivalence["maximum_hidden_error"],
        )
        <= 1.0e-6,
        "trained_ppo_mode_representation_within_1p1e_5": final_equivalence[
            "maximum_ppo_mode_action_error"
        ]
        <= 1.1e-5,
        "trained_graph_boundary_hierarchy_exact": final_boundary["exact"],
        "trained_graph_x0_exact": final_equivalence["x0_exact_zero"],
        "smoke_wall_seconds_at_most_3600": training["elapsed_seconds"] <= 3600.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
        if not failed
        else "HOLD_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v101.response_conditioned_cpu_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "devices": devices,
        "source_checkpoint_directory_sha256": directory_sha256(source_checkpoint),
        "expanded_checkpoint_directory_sha256": directory_sha256(expanded_path),
        "initial_graph": {
            "path": str(initial_graph),
            "sha256": sha256(initial_graph),
        },
        "golden_zero_update": golden,
        "initial_graph_equivalence": initial_equivalence,
        "initial_graph_boundary": initial_boundary,
        "automatic_calibration_reset": reset,
        "training": {
            key: value
            for key, value in training.items()
            if key not in ("final_checkpoint", "final_onnx")
        },
        "training_artifacts": {
            "final_checkpoint_path": str(training["final_checkpoint"]),
            "final_checkpoint_directory_sha256": directory_sha256(
                training["final_checkpoint"]
            ),
            "final_onnx_path": str(final_graph),
            "final_onnx_sha256": sha256(final_graph),
        },
        "actor_leaf_max_deltas": deltas,
        "update_family_max_delta": {
            "protected": protected_delta,
            "adapter_state": adapter_state_delta,
            "adapter_context": adapter_context_delta,
            "adapter_action": adapter_action_delta,
            "critic": value_delta,
        },
        "trained_onnx_abi": {"inputs": graph_inputs, "outputs": graph_outputs},
        "trained_graph_equivalence": final_equivalence,
        "trained_graph_boundary": final_boundary,
        "authority": {
            "separate_hosted_curriculum_preregistration_after_pass": not failed,
            "hosted_or_colab_run_authorized_by_this_result": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "# Winner-v101 response-conditioned CPU contract\n\n"
        f"Status: `{status}`\n\n"
        f"- zero-update golden ticks: `{golden['ticks']}`\n"
        f"- protected update maximum: `{protected_delta}`\n"
        f"- adapter state/context/action updates: `{adapter_state_delta}` / "
        f"`{adapter_context_delta}` / `{adapter_action_delta}`\n"
        f"- final ONNX SHA-256: `{sha256(final_graph)}`\n"
        f"- failed checks: `{failed}`\n\n"
        "This is a CPU mechanics and finite-update result only. It does not select "
        "a policy or authorize hosted training, RDK-X5 access, robot execution, "
        "Gate 5, torque, motion, deployment, or robot clearance.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"sha256={sha256(OUTPUT_JSON)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
