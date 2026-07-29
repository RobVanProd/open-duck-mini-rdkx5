#!/usr/bin/env python3
"""Run T95's preregistered calibration-FiLM CPU falsifier."""

from __future__ import annotations

import argparse
from contextlib import chdir
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t95_film_conditioned_cpu_preregistration_v3.json"
)
RESULT = (
    ANALYSIS / "t95_film_conditioned_cpu_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "T95_FILM_CONDITIONED_CPU_RESULT_20260728.md"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)
EXPECTED_ABI = {
    "inputs": {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
        "calibration_context": [1, 64],
    },
    "outputs": {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(entry, "key", getattr(entry, "idx", entry)))
        for entry in path
    )


def tree_deltas(left: Any, right: Any) -> tuple[bool, dict[str, float]]:
    left_rows, left_structure = jax.tree_util.tree_flatten_with_path(left)
    right_rows, right_structure = jax.tree_util.tree_flatten_with_path(
        right
    )
    if left_structure != right_structure:
        return False, {}
    result = {}
    for (left_path, before), (right_path, after) in zip(
        left_rows,
        right_rows,
        strict=True,
    ):
        if left_path != right_path:
            return False, {}
        result[path_name(left_path)] = float(
            np.max(
                np.abs(
                    np.asarray(after, dtype=float)
                    - np.asarray(before, dtype=float)
                )
            )
        )
    return True, result


def numeric_tree_finite(value: Any) -> bool:
    return all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(value)
    )


def validate_receipt(item: dict[str, Any], *, directory: bool) -> None:
    path = Path(item["path"])
    observed = directory_sha256(path) if directory else sha256(path)
    if observed != item["sha256"]:
        raise RuntimeError(f"T95 frozen input changed: {path}")
    if not directory and path.stat().st_size != item["bytes"]:
        raise RuntimeError(f"T95 frozen input size changed: {path}")


def validate_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "assets",
            "software_contract",
            "architecture_contract",
            "cpu_smoke",
            "decision_rule",
            "authority",
            "execution_now",
            "preexecution_correction",
            "context_observability",
        )
    }
    if (
        value.get("schema_version")
        != "open_duck.t95_film_cpu_preregistration.v3"
        or value.get("status")
        != "PREREGISTERED_T95_FILM_CONDITIONED_CPU_CONTRACT_V3"
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T95 preregistration identity changed")
    for item in value["sources"].values():
        validate_receipt(item, directory=False)
    for name, item in value["assets"].items():
        validate_receipt(
            item,
            directory=name in {"expanded_checkpoint"},
        )


def configure_environment(
    playground: Path,
    calibrator: Path,
    *,
    command_x: float,
) -> Any:
    if str(playground) not in sys.path:
        sys.path.insert(0, str(playground))
    from playground.common.t10_command_aware_response_wrapper import (
        wrap_command_aware_response,
    )
    from playground.open_duck_mini_v2 import joystick

    config = joystick.default_config()
    config.reward_config.scales.imitation = 1.0
    config.reference_feature_table_path = str(REFERENCE)
    config.recurrent_hidden_dim = 64
    config.nominal_reference_bootstrap = True
    config.nominal_reference_command_x = command_x
    config.ground_up_hard_vector_command_support = command_x > 0.01
    config.ground_up_command_support_range = [command_x, command_x + 1.0e-6]
    config.ground_up_action_velocity_limits_rad_s = [
        float(value) for value in VELOCITY_LIMITS.split(",")
    ]
    config.ground_up_measured_actuator_bridge = True
    config.ground_up_applied_target_observation = True
    config.reward_config.scales.tracking_tail_exceedance = (
        -6572.254964031055
    )
    config.ground_up_tracking_tail_threshold_rad = 0.20
    config.reward_config.scales.peak_torque_exceedance = 0.0
    config.reward_config.scales.linear_peak_torque_exceedance = (
        -307.48131091308585
    )
    config.ground_up_actuator_bridge_delay_ticks = [
        3,
        3,
        3,
        3,
        3,
        3,
        2,
        3,
        3,
        3,
        2,
        3,
        2,
        3,
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
    config.winner_v3_deviation_scale = 1.0
    config.winner_v119_train_transition_match = True
    config.noise_config.level = 1.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 3
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 3
    config.push_config.enable = False
    return wrap_command_aware_response(
        joystick.Joystick(
            task="flat_terrain_backlash",
            config=config,
        ),
        calibrator,
        calibration_ticks=250,
        home_return_ticks=0,
        zero_command_bypass=True,
    )


def reset_receipt(
    playground: Path,
    calibrator: Path,
    *,
    command_x: float,
    seed: int,
) -> dict[str, Any]:
    # The preserved simulator loads its polynomial reference through a
    # repository-relative path during environment construction.  The training
    # subprocess already runs with this cwd; give the reset-only preflight the
    # same source-root context.
    with chdir(playground):
        environment = configure_environment(
            playground,
            calibrator,
            command_x=command_x,
        )
    state = jax.jit(environment.reset)(jax.random.PRNGKey(seed))
    observation = {
        key: np.asarray(jax.device_get(value))
        for key, value in state.obs.items()
    }
    info = {
        key: np.asarray(jax.device_get(value))
        for key, value in state.info.items()
        if key
        in {
            "command",
            "step",
            "imitation_phase",
            "last_act",
            "motor_targets",
            "ground_up_actuator_bridge_applied_targets",
            "response_calibration_context",
            "response_calibration_valid",
            "response_calibration_bypassed",
            "response_calibration_ticks",
        }
    }
    applied = info["ground_up_actuator_bridge_applied_targets"]
    return {
        "command_x": float(command_x),
        "seed": seed,
        "observation_shapes": {
            key: list(value.shape) for key, value in observation.items()
        },
        "command": info["command"].astype(float).tolist(),
        "step": int(info["step"]),
        "phase": info["imitation_phase"].astype(float).tolist(),
        "done": float(np.asarray(state.done)),
        "valid": bool(info["response_calibration_valid"]),
        "bypassed": bool(info["response_calibration_bypassed"]),
        "calibration_ticks": int(info["response_calibration_ticks"]),
        "context_linf": float(
            np.max(np.abs(observation["calibration_context"]))
        ),
        "context_finite": bool(
            np.isfinite(observation["calibration_context"]).all()
        ),
        "hidden_linf": float(
            np.max(np.abs(observation["policy_hidden"]))
        ),
        "previous_action_linf": float(
            np.max(np.abs(observation["policy_previous_action"]))
        ),
        "previous_action_matches_realized": bool(
            np.array_equal(
                observation["policy_previous_action"],
                info["last_act"],
            )
        ),
        "applied_target_observation_matches_bridge": bool(
            np.array_equal(observation["state"][83:97], applied)
        ),
        "state_finite": bool(np.isfinite(observation["state"]).all()),
    }


def run_training(
    *,
    playground: Path,
    expanded_checkpoint: Path,
    calibrator: Path,
    output: Path,
    log: Path,
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
        "64",
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
        "response_conditioned_v121",
        "--recurrent_hidden_size",
        "64",
        "--t10_response_calibrator_path",
        str(calibrator),
        "--t10_response_calibration_ticks",
        "250",
        "--t10_response_home_return_ticks",
        "0",
        "--t10_command_aware_zero_bypass",
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
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,"
        ".035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale",
        "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad",
        "0.20",
        "--ground_up_peak_torque_exceedance_scale",
        "0",
        "--ground_up_linear_peak_torque_exceedance_scale",
        "-307.48131091308585",
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
        "--winner_v119_train_transition_match",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(expanded_checkpoint),
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
    log.write_text(
        completed.stdout,
        encoding="utf-8",
        newline="\n",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T95 CPU smoke failed rc={completed.returncode}; "
            f"log={log}; tail={completed.stdout[-8000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    graphs = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(
        int(path.name.rsplit("_", 1)[1]) for path in checkpoints
    )
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in graphs
    )
    if checkpoint_steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise RuntimeError(
            f"T95 exports changed: {checkpoint_steps}, {onnx_steps}"
        )
    return {
        "command": command,
        "elapsed_seconds": elapsed,
        "log": receipt(log),
        "checkpoints": checkpoints,
        "graphs": graphs,
        "checkpoint_steps": checkpoint_steps,
        "onnx_steps": onnx_steps,
    }


def describe_onnx(path: Path) -> dict[str, dict[str, list[int]]]:
    import onnx

    model = onnx.load(path)

    def values(items) -> dict[str, list[int]]:
        return {
            item.name: [
                dim.dim_value for dim in item.type.tensor_type.shape.dim
            ]
            for item in items
        }

    return {
        "inputs": values(model.graph.input),
        "outputs": values(model.graph.output),
    }


def graph_contract(path: Path, *, seed: int, cases: int) -> dict[str, Any]:
    import onnx
    import onnxruntime as ort

    model = onnx.load(path)
    initializers = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item))
        for item in model.graph.initializer
    }
    session = ort.InferenceSession(
        str(path),
        providers=["CPUExecutionProvider"],
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    max_rate_excess = 0.0
    max_previous_error = 0.0
    zero_exact = True
    all_finite = True
    for index in range(cases):
        observation = rng.normal(
            0.0,
            0.2,
            size=(1, 115),
        ).astype(np.float32)
        observation[:, 101:115] = rng.uniform(
            -0.8,
            0.8,
            size=(1, 14),
        ).astype(np.float32)
        observation[:, 13:27] = rng.uniform(
            -0.1,
            0.1,
            size=(1, 14),
        ).astype(np.float32)
        if index % 5 == 0:
            observation[:, 6:13] = 0.0
        else:
            observation[:, 6] = np.float32(
                (0.074, 0.077, 0.080)[index % 3]
            )
        context = rng.normal(
            0.0,
            0.7,
            size=(1, 64),
        ).astype(np.float32)
        action, previous_out, hidden_out = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        all_finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(previous_out).all()
            and np.isfinite(hidden_out).all()
        )
        max_previous_error = max(
            max_previous_error,
            float(np.max(np.abs(previous_out - action))),
        )
        if index % 5 == 0:
            zero_exact &= np.count_nonzero(action) == 0
        else:
            max_rate_excess = max(
                max_rate_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(action - previous)
                            - initializers["max_action_delta"],
                            0.0,
                        )
                    )
                ),
            )
        previous = np.asarray(previous_out, dtype=np.float32)
        hidden = np.asarray(hidden_out, dtype=np.float32)

    producer = {
        output: (node.op_type, list(node.input))
        for node in model.graph.node
        for output in node.output
    }
    hierarchy = {
        "context_film_projection": producer.get(
            "context_film_scale"
        )
        == (
            "MatMul",
            ["calibration_context", "context_film_weight"],
        ),
        "context_state_bilinear_path": producer.get(
            "context_film_delta"
        )
        == (
            "Mul",
            ["h_out", "context_film_scale"],
        ),
        "film_hidden_composition": producer.get("film_hidden")
        == (
            "Add",
            ["h_out", "context_film_delta"],
        ),
        "film_drives_action_head": producer.get("adapter_location")
        == (
            "Gemm",
            ["film_hidden", "adapter_weight", "adapter_bias"],
        ),
        "actual_centered_guard": producer.get("guard_actual_target")
        == ("Add", ["guard_home", "guard_joint_offsets"]),
        "first_deadband": producer.get("v121_preprojection_action")
        == (
            "Where",
            [
                "deadband_is_zero_command",
                "deadband_zero_action",
                "deadband_source_actions",
            ],
        ),
        "final_rate": producer.get("v121_final_rate_action")
        == (
            "Min",
            ["v121_final_above_lower", "v121_final_rate_upper"],
        ),
        "restored_deadband": producer.get("continuous_actions")
        == (
            "Where",
            [
                "deadband_is_zero_command",
                "deadband_zero_action",
                "v121_final_rate_action",
            ],
        ),
        "graph_owned_state": producer.get("previous_action_out")
        == ("Identity", ["continuous_actions"]),
    }
    return {
        "abi": describe_onnx(path),
        "providers": session.get_providers(),
        "cases": cases,
        "all_finite": all_finite,
        "max_rate_excess": max_rate_excess,
        "max_previous_action_error": max_previous_error,
        "x0_exact_zero": bool(zero_exact),
        "hierarchy": hierarchy,
        "all_hierarchy_checks": all(hierarchy.values()),
        "initializers_finite": all(
            np.isfinite(value).all() for value in initializers.values()
        ),
    }


def graph_pair_parity(
    left_path: Path,
    right_path: Path,
    *,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    left = ort.InferenceSession(
        str(left_path),
        providers=["CPUExecutionProvider"],
    )
    right = ort.InferenceSession(
        str(right_path),
        providers=["CPUExecutionProvider"],
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    left_previous = np.zeros((1, 14), dtype=np.float32)
    right_previous = left_previous.copy()
    left_hidden = np.zeros((1, 64), dtype=np.float32)
    right_hidden = left_hidden.copy()
    maximum = {
        "continuous_actions": 0.0,
        "previous_action_out": 0.0,
        "h_out": 0.0,
    }
    exact = {key: True for key in maximum}
    for index in range(cases):
        observation = rng.normal(
            0.0,
            0.2,
            size=(1, 115),
        ).astype(np.float32)
        observation[:, 101:115] = rng.uniform(
            -0.8,
            0.8,
            size=(1, 14),
        ).astype(np.float32)
        observation[:, 6] = np.float32(
            0.0 if index % 5 == 0 else 0.077
        )
        context = rng.normal(
            0.0,
            0.7,
            size=(1, 64),
        ).astype(np.float32)
        left_outputs = left.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": left_previous,
                "h_in": left_hidden,
                "calibration_context": context,
            },
        )
        right_outputs = right.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": right_previous,
                "h_in": right_hidden,
                "calibration_context": context,
            },
        )
        for name, left_value, right_value in zip(
            maximum,
            left_outputs,
            right_outputs,
            strict=True,
        ):
            maximum[name] = max(
                maximum[name],
                float(
                    np.max(
                        np.abs(
                            left_value.astype(float)
                            - right_value.astype(float)
                        )
                    )
                ),
            )
            exact[name] &= bool(
                np.array_equal(left_value, right_value)
            )
        left_previous = left_outputs[1]
        right_previous = right_outputs[1]
        left_hidden = left_outputs[2]
        right_hidden = right_outputs[2]
    return {
        "cases": cases,
        "maximum_abs_errors": maximum,
        "bit_exact": exact,
        "all_outputs_bit_exact": all(exact.values()),
    }


def context_sensitivity(
    graph: Path,
    *,
    seed: int,
    ticks_per_context: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    session = ort.InferenceSession(
        str(graph),
        providers=["CPUExecutionProvider"],
    )
    t94 = json.loads(
        (
            ANALYSIS / "t94_r2_calibration_manifold_result.json"
        ).read_text(encoding="utf-8")
    )
    contexts = [
        (
            cell["configuration_id"],
            cell["fit_id"],
            np.asarray(cell["context"], dtype=np.float32)[None, :],
        )
        for cell in t94["cells"]
    ]
    rng = np.random.Generator(np.random.PCG64(seed))
    maximum_action_delta = 0.0
    maximum_hidden_delta = 0.0
    action_effect_ticks = 0
    pair_effects: dict[str, bool] = {}
    total_ticks = len(contexts) * ticks_per_context
    for configuration_id, fit_id, context in contexts:
        zero_previous = np.zeros((1, 14), dtype=np.float32)
        context_previous = zero_previous.copy()
        zero_hidden = np.zeros((1, 64), dtype=np.float32)
        context_hidden = zero_hidden.copy()
        pair_effect = False
        for tick in range(ticks_per_context):
            observation = rng.normal(
                0.0,
                0.2,
                size=(1, 115),
            ).astype(np.float32)
            observation[:, 6] = np.float32(
                (0.074, 0.077, 0.080)[tick % 3]
            )
            observation[:, 101:115] = rng.uniform(
                -0.8,
                0.8,
                size=(1, 14),
            ).astype(np.float32)
            zero = session.run(
                ["continuous_actions", "h_out"],
                {
                    "obs": observation,
                    "previous_action": zero_previous,
                    "h_in": zero_hidden,
                    "calibration_context": np.zeros(
                        (1, 64), dtype=np.float32
                    ),
                },
            )
            conditioned = session.run(
                ["continuous_actions", "h_out"],
                {
                    "obs": observation,
                    "previous_action": context_previous,
                    "h_in": context_hidden,
                    "calibration_context": context,
                },
            )
            action_delta = float(
                np.max(np.abs(zero[0] - conditioned[0]))
            )
            hidden_delta = float(
                np.max(np.abs(zero[1] - conditioned[1]))
            )
            maximum_action_delta = max(
                maximum_action_delta, action_delta
            )
            maximum_hidden_delta = max(
                maximum_hidden_delta, hidden_delta
            )
            changed = action_delta > 1.0e-8
            action_effect_ticks += int(changed)
            pair_effect |= changed
            zero_previous = zero[0]
            context_previous = conditioned[0]
            zero_hidden = zero[1]
            context_hidden = conditioned[1]
        pair_effects[f"{configuration_id}:{fit_id}"] = pair_effect
    negative_com_pairs = [
        changed
        for name, changed in pair_effects.items()
        if name.startswith("TORSO_COM_X_NEG:")
    ]
    return {
        "contexts": len(contexts),
        "ticks_per_context": ticks_per_context,
        "total_ticks": total_ticks,
        "maximum_action_delta": maximum_action_delta,
        "maximum_hidden_delta": maximum_hidden_delta,
        "action_effect_ticks": action_effect_ticks,
        "action_effect_tick_fraction": action_effect_ticks / total_ticks,
        "context_pairs_with_action_effect": sum(pair_effects.values()),
        "context_pair_effect_fraction": (
            sum(pair_effects.values()) / len(pair_effects)
        ),
        "both_negative_com_pairs_change_action": all(negative_com_pairs)
        and len(negative_com_pairs) == 2,
        "context_state_path_remains_exactly_invariant": (
            maximum_hidden_delta == 0.0
        ),
        "pair_effects": pair_effects,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--assets-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--cpu-smoke-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.cpu_smoke_authorized:
        raise PermissionError(
            "T95 requires --offline-cpu-only --cpu-smoke-authorized"
        )
    playground = args.playground_root.resolve()
    assets_root = args.assets_root.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing to reuse T95 work root: {work}")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T95 formal result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_preregistration(prereg)
    if (
        Path(prereg["sources"]["playground_manifest"]["path"]).parent
        != playground
        or Path(prereg["sources"]["asset_manifest"]["path"]).parent
        != assets_root
    ):
        raise RuntimeError("T95 execution roots differ from preregistration")
    work.mkdir(parents=True)
    output = work / "smoke"
    output.mkdir()
    log = work / "training.log"
    calibrator = Path(prereg["assets"]["calibrator"]["path"])
    expanded = Path(prereg["assets"]["expanded_checkpoint"]["path"])
    step_zero_asset = Path(prereg["assets"]["step_zero_onnx"]["path"])

    reset_x0 = reset_receipt(
        playground,
        calibrator,
        command_x=0.0,
        seed=100,
    )
    reset_moving = reset_receipt(
        playground,
        calibrator,
        command_x=0.077,
        seed=101,
    )
    training = run_training(
        playground=playground,
        expanded_checkpoint=expanded,
        calibrator=calibrator,
        output=output,
        log=log,
    )
    initial_checkpoint = next(
        path
        for path in training["checkpoints"]
        if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path
        for path in training["checkpoints"]
        if path.name.endswith("_1024")
    )
    initial_graph = next(
        path for path in training["graphs"] if path.stem.endswith("_0")
    )
    final_graph = next(
        path
        for path in training["graphs"]
        if path.stem.endswith("_1024")
    )
    checkpointer = ocp.PyTreeCheckpointer()
    expanded_tree = checkpointer.restore(str(expanded))
    initial_tree = checkpointer.restore(
        str(initial_checkpoint),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    final_tree = checkpointer.restore(
        str(final_checkpoint),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    initial_structure, initial_deltas = tree_deltas(
        expanded_tree,
        initial_tree,
    )
    trained_structure, trained_deltas = tree_deltas(
        initial_tree,
        final_tree,
    )
    policy_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("1/params/")
    }
    critic_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("2/")
    }
    film_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if "/context_film_scale/" in name
    }
    protected_actor_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if name not in film_deltas
    }
    step_zero_parity = graph_pair_parity(
        step_zero_asset,
        initial_graph,
        seed=1010200,
        cases=256,
    )
    initial_contract = graph_contract(
        initial_graph,
        seed=1010201,
        cases=256,
    )
    final_contract = graph_contract(
        final_graph,
        seed=1010202,
        cases=256,
    )
    sensitivity = context_sensitivity(
        final_graph,
        seed=1010203,
        ticks_per_context=64,
    )

    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "x0_bypass_receipt_exact": (
            reset_x0["bypassed"]
            and reset_x0["calibration_ticks"] == 0
            and reset_x0["context_linf"] == 0.0
            and reset_x0["hidden_linf"] == 0.0
            and reset_x0["previous_action_linf"] == 0.0
            and reset_x0["phase"] == [1.0, 0.0]
            and reset_x0["step"] == 0
            and reset_x0["done"] == 0.0
            and reset_x0["valid"]
            and reset_x0["applied_target_observation_matches_bridge"]
        ),
        "moving_response_receipt_exact": (
            not reset_moving["bypassed"]
            and reset_moving["calibration_ticks"] == 250
            and reset_moving["context_linf"] > 0.0
            and reset_moving["context_finite"]
            and reset_moving["hidden_linf"] == 0.0
            and reset_moving["previous_action_linf"] > 0.0
            and reset_moving["previous_action_matches_realized"]
            and reset_moving["phase"] == [1.0, 0.0]
            and reset_moving["step"] == 0
            and reset_moving["done"] == 0.0
            and reset_moving["valid"]
            and reset_moving[
                "applied_target_observation_matches_bridge"
            ]
        ),
        "exact_exports_0_and_1024": (
            training["checkpoint_steps"] == [0, 1024]
            and training["onnx_steps"] == [0, 1024]
        ),
        "expanded_restore_structure_exact": initial_structure,
        "expanded_restore_bit_exact": max(
            initial_deltas.values(),
            default=math.inf,
        )
        == 0.0,
        "trained_structure_exact": trained_structure,
        "trained_tree_finite": numeric_tree_finite(final_tree),
        "exact_one_film_leaf_updated": (
            len(film_deltas) == 1
            and all(value > 0.0 for value in film_deltas.values())
        ),
        "every_protected_actor_leaf_bit_exact": (
            bool(protected_actor_deltas)
            and all(
                value == 0.0
                for value in protected_actor_deltas.values()
            )
        ),
        "critic_updated": bool(critic_deltas)
        and any(value > 0.0 for value in critic_deltas.values()),
        "step_zero_export_bit_exact_to_asset": step_zero_parity[
            "all_outputs_bit_exact"
        ],
        "initial_graph_contract_green": (
            initial_contract["abi"] == EXPECTED_ABI
            and initial_contract["providers"] == ["CPUExecutionProvider"]
            and initial_contract["all_finite"]
            and initial_contract["max_rate_excess"] <= 1.0e-7
            and initial_contract["max_previous_action_error"] == 0.0
            and initial_contract["x0_exact_zero"]
            and initial_contract["all_hierarchy_checks"]
            and initial_contract["initializers_finite"]
        ),
        "trained_graph_contract_green": (
            final_contract["abi"] == EXPECTED_ABI
            and final_contract["providers"] == ["CPUExecutionProvider"]
            and final_contract["all_finite"]
            and final_contract["max_rate_excess"] <= 1.0e-7
            and final_contract["max_previous_action_error"] == 0.0
            and final_contract["x0_exact_zero"]
            and final_contract["all_hierarchy_checks"]
            and final_contract["initializers_finite"]
        ),
        "film_does_not_mutate_recurrent_state": sensitivity[
            "context_state_path_remains_exactly_invariant"
        ],
        "both_negative_com_contexts_change_action": sensitivity[
            "both_negative_com_pairs_change_action"
        ],
        "context_action_effect_at_least_ten_x_t11": sensitivity[
            "action_effect_tick_fraction"
        ]
        >= 0.05,
        "at_least_half_context_pairs_change_action": sensitivity[
            "context_pair_effect_fraction"
        ]
        >= 0.50,
        "maximum_context_action_delta_material": sensitivity[
            "maximum_action_delta"
        ]
        >= 1.0e-5,
        "wall_seconds_at_most_3600": (
            training["elapsed_seconds"] <= 3600.0
        ),
        "robot_or_rdk_access_zero": True,
        "hosted_or_colab_compute_zero": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    decision = (
        "EARN_ONE_FILM_CONDITIONED_HOSTED_CONTINUATION_PREREGISTRATION"
        if not failed
        else "CLOSE_FILM_CONDITIONED_CONTINUATION_WITHOUT_HOSTED_RUN"
    )
    basis = {
        "schema_version": "open_duck.t95_film_cpu_result.v1",
        "status": (
            "PASS_T95_FILM_CONDITIONED_CPU_CONTRACT"
            if not failed
            else "HOLD_T95_FILM_CONDITIONED_CPU_CONTRACT"
        ),
        "decision": decision,
        "failed_checks": failed,
        "checks": checks,
        "reset_contract": {
            "x0": reset_x0,
            "moving": reset_moving,
        },
        "training": {
            "command": training["command"],
            "elapsed_seconds": training["elapsed_seconds"],
            "checkpoint_steps": training["checkpoint_steps"],
            "onnx_steps": training["onnx_steps"],
            "log": training["log"],
            "initial_checkpoint": directory_receipt(
                initial_checkpoint
            ),
            "final_checkpoint": directory_receipt(final_checkpoint),
            "initial_onnx": receipt(initial_graph),
            "final_onnx": receipt(final_graph),
            "policy_leaf_deltas": policy_deltas,
            "critic_leaf_deltas": critic_deltas,
            "film_leaf_deltas": film_deltas,
            "protected_actor_leaf_deltas": protected_actor_deltas,
        },
        "step_zero_export_parity": step_zero_parity,
        "initial_graph_contract": initial_contract,
        "trained_graph_contract": final_contract,
        "trained_context_sensitivity": sensitivity,
        "input_hashes": {
            "preregistration": receipt(PREREG),
            "playground_manifest": prereg["sources"][
                "playground_manifest"
            ],
            "asset_manifest": prereg["sources"]["asset_manifest"],
        },
        "execution": {
            "optimizer_steps": 1024,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_training_authorized": False,
            "hosted_preregistration_authorized": not failed,
            "behavior_matrix_authorized": False,
            "gate5_authorized": False,
            "robot_or_rdk_access": False,
            "torque_or_motion": False,
            "robot_clearance": False,
        },
    }
    value = {
        **basis,
        "result_sha256": canonical_sha256(basis),
    }
    RESULT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T95 calibration-FiLM CPU contract\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{decision}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- CPU smoke wall time: `{training['elapsed_seconds']:.3f} s`\n"
        f"- Context action delta: "
        f"`{sensitivity['maximum_action_delta']:.9g}`\n"
        f"- Context hidden delta: "
        f"`{sensitivity['maximum_hidden_delta']:.9g}`\n"
        f"- Context-effect ticks: "
        f"`{sensitivity['action_effect_ticks']}/"
        f"{sensitivity['total_ticks']}`\n"
        f"- Context pairs with action effect: "
        f"`{sensitivity['context_pairs_with_action_effect']}/"
        f"{sensitivity['contexts']}`\n"
        "- Hosted/Colab compute: `0`\n"
        "- Formal behavior cells: `0`\n"
        "- Robot/RDK-X5 access: `0`\n"
        f"- Canonical result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={decision}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    print(f"file_sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
