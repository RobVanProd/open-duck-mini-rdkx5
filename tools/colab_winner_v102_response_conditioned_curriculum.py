#!/usr/bin/env python3
"""Run the single frozen Winner-v102 response-conditioned GPU curriculum."""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import traceback
from typing import Any

import flax
from flax.training import orbax_utils
import jax
import jax.numpy as jnp
import numpy as np
import onnx
import onnxruntime as ort
from orbax import checkpoint as ocp


PREREGISTRATION_NAME = (
    "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
CPU_CONTRACT_NAME = "winner_v101_response_conditioned_cpu_contract.json"
SOURCE_ARCHIVE_NAME = "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE_NAME = "ground_up_projected_reference_feature_table.npz"
PROTECTED_POLICY_NAME = "T2_EQUAL_512000.onnx"
CALIBRATOR_NAME = "winner_v22_final.onnx"
SOURCE_MEMBER = Path(
    "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190026_512000"
)
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
STAGES = (
    {
        "id": "DOMAIN_25_PERCENT",
        "deviation_scale": 0.25,
        "steps": 245_760,
        "num_evals": 2,
        "expected_steps": [0, 245_760],
    },
    {
        "id": "DOMAIN_50_PERCENT",
        "deviation_scale": 0.5,
        "steps": 245_760,
        "num_evals": 2,
        "expected_steps": [0, 245_760],
    },
    {
        "id": "DOMAIN_100_PERCENT",
        "deviation_scale": 1.0,
        "steps": 2_007_040,
        "num_evals": 3,
        "expected_steps": [0, 1_003_520, 2_007_040],
    },
)
MAX_WALL_SECONDS = 21_600


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


def tree_finite(value: Any) -> bool:
    for leaf in jax.tree_util.tree_leaves(value):
        array = np.asarray(leaf)
        if array.dtype.kind in "biufc" and not np.isfinite(array).all():
            return False
    return True


def tree_error(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return False, float("inf")
    errors = []
    for before, after in zip(
        jax.tree_util.tree_leaves(left),
        jax.tree_util.tree_leaves(right),
        strict=True,
    ):
        before_array = np.asarray(before)
        after_array = np.asarray(after)
        if before_array.dtype.kind not in "biufc":
            if not np.array_equal(before_array, after_array):
                return False, float("inf")
            continue
        errors.append(float(np.max(np.abs(after_array - before_array))))
    return True, max(errors, default=0.0)


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(entry, "key", getattr(entry, "idx", entry))) for entry in path
    )


def leaf_deltas(initial: Any, final: Any) -> dict[str, float]:
    initial_rows, structure = jax.tree_util.tree_flatten_with_path(initial)
    final_rows, final_structure = jax.tree_util.tree_flatten_with_path(final)
    if structure != final_structure:
        raise ValueError("Winner-v102 trained actor tree structure changed")
    result: dict[str, float] = {}
    for (initial_path, before), (final_path, after) in zip(
        initial_rows, final_rows, strict=True
    ):
        if initial_path != final_path:
            raise ValueError("Winner-v102 trained actor leaf ordering changed")
        before_array = np.asarray(before)
        after_array = np.asarray(after)
        if before_array.dtype.kind not in "biufc":
            result[path_name(initial_path)] = (
                0.0 if np.array_equal(before_array, after_array) else float("inf")
            )
        else:
            result[path_name(initial_path)] = float(
                np.max(np.abs(after_array - before_array))
            )
    return result


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


def step_from_name(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def describe_onnx(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
    inputs = {
        item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim]
        for item in model.graph.input
    }
    outputs = {
        item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim]
        for item in model.graph.output
    }
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
    initializers_finite = all(
        np.isfinite(onnx.numpy_helper.to_array(item)).all()
        for item in model.graph.initializer
    )
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    zero_inputs = {
        "obs": np.zeros((1, 115), dtype=np.float32),
        "previous_action": np.zeros((1, 14), dtype=np.float32),
        "h_in": np.zeros((1, 64), dtype=np.float32),
        "calibration_context": np.zeros((1, 64), dtype=np.float32),
    }
    action, previous_out, hidden_out = session.run(None, zero_inputs)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "inputs": inputs,
        "outputs": outputs,
        "abi_exact": inputs == expected_inputs and outputs == expected_outputs,
        "initializers_finite": bool(initializers_finite),
        "x0_action_exact_zero": bool(np.array_equal(action, np.zeros_like(action))),
        "x0_previous_action_out_exact_zero": bool(
            np.array_equal(previous_out, np.zeros_like(previous_out))
        ),
        "x0_hidden_finite": bool(np.isfinite(hidden_out).all()),
        "providers": session.get_providers(),
    }


def runner_command(
    playground: Path,
    output: Path,
    restore: Path,
    stage: dict[str, Any],
    assets: Path,
) -> list[str]:
    return [
        sys.executable,
        str(playground / "playground/open_duck_mini_v2/runner.py"),
        "--task",
        "flat_terrain_backlash",
        "--env",
        "joystick",
        "--output_dir",
        str(output),
        "--num_timesteps",
        str(stage["steps"]),
        "--ppo_seed",
        "100",
        "--ppo_num_envs",
        "256",
        "--ppo_num_evals",
        str(stage["num_evals"]),
        "--ppo_episode_length",
        "600",
        "--ppo_unroll_length",
        "20",
        "--ppo_batch_size",
        "256",
        "--ppo_num_minibatches",
        "4",
        "--ppo_num_updates_per_batch",
        "4",
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
        str(assets / PROTECTED_POLICY_NAME),
        "--winner_v98_calibrator_path",
        str(assets / CALIBRATOR_NAME),
        "--winner_v98_calibration_ticks",
        "250",
        "--winner_v98_home_return_ticks",
        "250",
        "--imitation_scale",
        "1.0",
        "--reference_feature_table_path",
        str(assets / REFERENCE_NAME),
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
        str(stage["deviation_scale"]),
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(restore),
    ]


def inspect_stage(
    stage: dict[str, Any], output: Path, checkpointer: ocp.PyTreeCheckpointer
) -> dict[str, Any]:
    checkpoints = sorted(
        (path for path in output.iterdir() if path.is_dir()), key=step_from_name
    )
    graphs = sorted(output.glob("*.onnx"), key=step_from_name)
    checkpoint_steps = [step_from_name(path) for path in checkpoints]
    onnx_steps = [step_from_name(path) for path in graphs]
    if (
        checkpoint_steps != stage["expected_steps"]
        or onnx_steps != stage["expected_steps"]
    ):
        raise ValueError(
            f"unexpected {stage['id']} exports: {checkpoint_steps}, {onnx_steps}"
        )
    checkpoint_rows = []
    for path in checkpoints:
        value = checkpointer.restore(str(path))
        if not tree_finite(value):
            raise FloatingPointError(f"nonfinite checkpoint: {path}")
        checkpoint_rows.append(
            {
                "step": step_from_name(path),
                "path": str(path),
                "directory_sha256": directory_sha256(path),
                "all_leaves_finite": True,
            }
        )
    graph_rows = []
    for path in graphs:
        row = describe_onnx(path)
        if not all(
            row[name]
            for name in (
                "abi_exact",
                "initializers_finite",
                "x0_action_exact_zero",
                "x0_previous_action_out_exact_zero",
                "x0_hidden_finite",
            )
        ):
            raise ValueError(f"invalid ONNX artifact: {row}")
        row["step"] = step_from_name(path)
        graph_rows.append(row)
    return {
        "id": stage["id"],
        "deviation_scale": stage["deviation_scale"],
        "requested_steps": stage["steps"],
        "checkpoint_steps": checkpoint_steps,
        "onnx_steps": onnx_steps,
        "checkpoints": checkpoint_rows,
        "onnx": graph_rows,
        "initial_checkpoint": checkpoints[0],
        "final_checkpoint": checkpoints[-1],
    }


def make_artifact(work: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise FileExistsError(destination)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(work, arcname="winner_v102_response_conditioned_curriculum")
    temporary.replace(destination)
    return {
        "path": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def validate_inputs(bundle: Path, playground: Path, assets: Path) -> dict[str, Any]:
    prereg_path = bundle / PREREGISTRATION_NAME
    cpu_result_path = bundle / CPU_CONTRACT_NAME
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    cpu_result = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    if (
        prereg.get("schema_version")
        != "winner_v102.response_conditioned_hosted_curriculum_preregistration.v1"
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or prereg.get("decision")
        != "AUTHORIZE_ONE_HASH_FROZEN_GPU_CURRICULUM_WITHOUT_RETRY"
        or cpu_result.get("status")
        != "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
        or cpu_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v102 prerequisite identity changed")
    files = {
        "driver": Path(__file__).resolve(),
        "v96_network": bundle / "winner_v96_response_conditioned_networks.py",
        "cpu_contract": cpu_result_path,
        "composed_manifest": playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "source_archive": assets / SOURCE_ARCHIVE_NAME,
        "reference_features": assets / REFERENCE_NAME,
        "protected_policy": assets / PROTECTED_POLICY_NAME,
        "calibrator": assets / CALIBRATOR_NAME,
    }
    observed = {name: sha256(path) for name, path in files.items()}
    if observed != prereg.get("input_hashes"):
        raise ValueError(
            f"Winner-v102 input hashes changed: observed={observed}, "
            f"expected={prereg.get('input_hashes')}"
        )
    composed = prereg["composed_playground_files"]
    for relative, expected in composed.items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"Winner-v102 composed file changed: {relative}")
    if prereg.get("training", {}).get("stages") != [
        {
            "id": stage["id"],
            "deviation_scale": stage["deviation_scale"],
            "timesteps": stage["steps"],
            **(
                {"exports": [1_003_520, 2_007_040]}
                if stage["id"] == "DOMAIN_100_PERCENT"
                else {}
            ),
        }
        for stage in STAGES
    ]:
        raise ValueError("Winner-v102 stage schedule changed")
    devices = [str(device) for device in jax.devices()]
    if not devices or not all(device.platform == "gpu" for device in jax.devices()):
        raise RuntimeError(f"Winner-v102 requires GPU-only JAX devices: {devices}")
    if jax.process_count() != 1:
        raise RuntimeError("Winner-v102 requires one JAX process")
    return {
        "preregistration_sha256": sha256(prereg_path),
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
    }


def run(
    bundle: Path,
    playground: Path,
    assets: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    if work.exists():
        raise FileExistsError(f"single-run no-retry work root exists: {work}")
    for path in (output_json, output_archive):
        if path.exists():
            raise FileExistsError(f"single-run output exists: {path}")
    validation = validate_inputs(bundle, playground, assets)
    work.mkdir(parents=True)
    started = time.monotonic()
    payload: dict[str, Any] = {
        "schema_version": "winner_v102.response_conditioned_hosted_curriculum.v1",
        "status": "RUNNING_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM",
        "checks": {},
        "failed_checks": [],
        "validation": validation,
        "process_id": os.getpid(),
        "stages": [],
        "formal_behavior_cells_executed": 0,
        "training_reward_selection_weight": "NONE",
        "max_wall_seconds": MAX_WALL_SECONDS,
        "authority": {
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
        },
    }
    run_state = work / "run_state.json"
    run_state.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    checkpointer = ocp.PyTreeCheckpointer()
    try:
        source_root = work / "protected_source"
        source_root.mkdir()
        with tarfile.open(assets / SOURCE_ARCHIVE_NAME, "r:gz") as archive:
            members = [
                member
                for member in archive
                if member.name == SOURCE_MEMBER.as_posix()
                or member.name.startswith(SOURCE_MEMBER.as_posix() + "/")
            ]
            archive.extractall(source_root, members=members, filter="data")
        source_checkpoint = source_root / SOURCE_MEMBER
        expected_source_hash = json.loads(
            (bundle / PREREGISTRATION_NAME).read_text(encoding="utf-8")
        )["source_checkpoint_directory_sha256"]
        if directory_sha256(source_checkpoint) != expected_source_hash:
            raise ValueError("Winner-v102 source checkpoint directory changed")

        sys.path.insert(0, str(playground))
        sys.path.insert(0, str(bundle))
        from brax.training.acme import running_statistics
        from playground.common.reference_residual_ppo_networks import (
            make_reference_residual_ppo_networks,
        )
        from playground.common.winner_v98_response_conditioned_ppo_networks import (
            make_response_conditioned_ppo_networks,
        )
        import winner_v96_response_conditioned_networks as v96

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
        source = checkpointer.restore(
            str(source_checkpoint),
            item=template,
            restore_args=orbax_utils.restore_args_from_target(template),
        )
        expanded = expand_checkpoint(source, response_networks, v96)
        expanded_path = work / "expanded_checkpoint"
        checkpointer.save(
            str(expanded_path),
            expanded,
            save_args=orbax_utils.save_args_from_target(expanded),
        )
        expanded_roundtrip = checkpointer.restore(str(expanded_path))
        structure_exact, roundtrip_error = tree_error(expanded, expanded_roundtrip)
        if not structure_exact or roundtrip_error != 0.0 or not tree_finite(
            expanded_roundtrip
        ):
            raise ValueError(
                f"Winner-v102 expansion round trip failed: "
                f"{structure_exact}, {roundtrip_error}"
            )
        initial_actor = flax.core.unfreeze(expanded_roundtrip[1])["params"]
        payload["expanded_checkpoint"] = {
            "directory_sha256": directory_sha256(expanded_path),
            "roundtrip_max_abs_error": roundtrip_error,
            "tree_structure_exact": structure_exact,
            "all_leaves_finite": True,
        }

        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(playground)
        restore = expanded_path
        prior_final: Any | None = None
        full_log = work / "training.log"
        with full_log.open("w", encoding="utf-8") as log_stream:
            for stage_index, stage in enumerate(STAGES, start=1):
                if time.monotonic() - started > MAX_WALL_SECONDS:
                    raise TimeoutError("Winner-v102 wall ceiling exceeded")
                output = work / f"stage{stage_index}_{stage['id'].lower()}"
                output.mkdir()
                command = runner_command(playground, output, restore, stage, assets)
                stage_started = time.monotonic()
                log_stream.write(
                    f"WINNER_V102_STAGE_START={stage['id']} "
                    f"scale={stage['deviation_scale']} steps={stage['steps']}\n"
                )
                log_stream.flush()
                completed = subprocess.run(
                    command,
                    cwd=playground,
                    env=environment,
                    text=True,
                    stdout=log_stream,
                    stderr=subprocess.STDOUT,
                    timeout=MAX_WALL_SECONDS - (time.monotonic() - started),
                    check=False,
                )
                if completed.returncode != 0:
                    raise RuntimeError(
                        f"Winner-v102 stage failed: {stage['id']} rc={completed.returncode}"
                    )
                row = inspect_stage(stage, output, checkpointer)
                row["wall_seconds"] = time.monotonic() - stage_started
                if prior_final is not None:
                    current_initial = checkpointer.restore(
                        str(row["initial_checkpoint"])
                    )
                    continuity_structure, continuity_error = tree_error(
                        prior_final, current_initial
                    )
                    row["restore_continuity"] = {
                        "tree_structure_exact": continuity_structure,
                        "max_abs_error": continuity_error,
                    }
                    if not continuity_structure or continuity_error != 0.0:
                        raise ValueError(
                            f"Winner-v102 stage continuity failed: {stage['id']}"
                        )
                prior_final = checkpointer.restore(str(row["final_checkpoint"]))
                restore = row["final_checkpoint"]
                row["initial_checkpoint"] = str(row["initial_checkpoint"])
                row["final_checkpoint"] = str(row["final_checkpoint"])
                payload["stages"].append(row)
                payload["status"] = f"COMPLETED_{stage['id']}"
                payload["wall_seconds"] = time.monotonic() - started
                run_state.write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n"
                )
                log_stream.write(
                    f"WINNER_V102_STAGE_COMPLETE={stage['id']} "
                    f"wall={row['wall_seconds']:.3f}\n"
                )
                log_stream.flush()
                gc.collect()

        if prior_final is None:
            raise RuntimeError("Winner-v102 produced no final checkpoint")
        final_actor = flax.core.unfreeze(prior_final[1])["params"]
        deltas = leaf_deltas(initial_actor, final_actor)
        protected_names = (*BASE_KEYS, "protected_obs_mean", "protected_obs_std")
        family_deltas = {
            "protected": max(
                (
                    value
                    for name, value in deltas.items()
                    if any(token in name for token in protected_names)
                ),
                default=0.0,
            ),
            "adapter_state": max(
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
            ),
            "adapter_context": max(
                (
                    value
                    for name, value in deltas.items()
                    if "adapter_context" in name
                ),
                default=0.0,
            ),
            "adapter_action": max(
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
            ),
        }
        payload["actor_leaf_max_deltas"] = deltas
        payload["update_family_max_delta"] = family_deltas
        payload["training_log"] = {
            "path": str(full_log),
            "sha256": sha256(full_log),
        }
        payload["checks"] = {
            "gpu_only": bool(jax.devices())
            and all(device.platform == "gpu" for device in jax.devices()),
            "single_jax_process": jax.process_count() == 1,
            "all_three_stages_completed": len(payload["stages"]) == 3,
            "stage_restore_continuity_exact": all(
                row.get("restore_continuity", {}).get("max_abs_error") == 0.0
                for row in payload["stages"][1:]
            ),
            "exports_exact": all(
                row["checkpoint_steps"] == stage["expected_steps"]
                and row["onnx_steps"] == stage["expected_steps"]
                for row, stage in zip(payload["stages"], STAGES, strict=True)
            ),
            "protected_actor_exact": family_deltas["protected"] == 0.0,
            "adapter_state_updated": family_deltas["adapter_state"] > 0.0,
            "adapter_context_updated": family_deltas["adapter_context"] > 0.0,
            "adapter_action_updated": family_deltas["adapter_action"] > 0.0,
            "all_checkpoint_leaves_finite": all(
                all(item["all_leaves_finite"] for item in row["checkpoints"])
                for row in payload["stages"]
            ),
            "all_graph_contracts_pass": all(
                all(
                    item["abi_exact"]
                    and item["initializers_finite"]
                    and item["x0_action_exact_zero"]
                    and item["x0_previous_action_out_exact_zero"]
                    and item["x0_hidden_finite"]
                    for item in row["onnx"]
                )
                for row in payload["stages"]
            ),
            "within_wall_ceiling": time.monotonic() - started <= MAX_WALL_SECONDS,
            "formal_behavior_cells_zero": True,
        }
        failed = sorted(name for name, passed in payload["checks"].items() if not passed)
        if failed:
            raise ValueError(f"Winner-v102 training artifact checks failed: {failed}")
        payload["status"] = "PASS_WINNER_V102_RESPONSE_CONDITIONED_TRAINING_ARTIFACT"
        payload["failed_checks"] = []
        payload["wall_seconds"] = time.monotonic() - started
        run_state.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        payload["artifact"] = make_artifact(work, output_archive)
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(payload["status"], flush=True)
        print(f"sha256={sha256(output_json)}", flush=True)
        return 0
    except BaseException as exc:
        payload["status"] = "HOLD_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["traceback"] = traceback.format_exc()
        payload["wall_seconds"] = time.monotonic() - started
        run_state.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("Winner-v102 requires --hosted-gpu-authorized")
    bundle = args.bundle_root.resolve()
    return run(
        bundle,
        bundle / "playground",
        bundle / "assets",
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
