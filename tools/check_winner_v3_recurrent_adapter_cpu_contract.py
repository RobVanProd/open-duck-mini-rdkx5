#!/usr/bin/env python3
"""Run the preregistered winner-v3 recurrent-adapter CPU contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
from typing import Any

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
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
ADAPTER_SOURCE = ROOT / "patches/reference_residual_recurrent_adapter_ppo_networks.py"
INTEGRATION_PATCH = ROOT / "patches/ground_up_reference_residual_recurrent_adapter.patch"
SOURCE_MEMBER = Path("ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190026_512000")
OUTPUT_JSON = ANALYSIS / "winner_v3_recurrent_adapter_cpu_contract.json"
OUTPUT_MD = ANALYSIS / "WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT_20260719.md"
CPU_TEMPLATE = Path(
    "/home/lsd/robots/open-duck-mini-rdkx5/outputs/"
    "ground_up_torso_com_cpu_smoke/2026_07_14_180720_0"
)
CPU_TEMPLATE_SHA256 = "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a"
SOURCE_DIRECTORY_SHA256 = "311ce59807ad872795dd95e4a30c626f11d3d80f1b3f78c5b2b997639da4d67e"
EXPECTED = {
    "prereg": "79ed8e765be72b035d94958c106758d170cb740379abab88d5582ddd7735a96b",
    "archive": "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
    "reference": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "adapter_source": "9096e7c9c87d2d296a76b3144f4c65f196ab542ea97a2e101d2e152032b8917e",
    "integration_patch": "5adad79f763ec833d65250565a7551610ae2202db0a3c15c4471fdf3b04e9553",
}
BASE_KEYS = ("residual_trunk", "residual_location", "scale_logits")
ADAPTER_KEYS = (
    "adapter_obs_projection", "adapter_hidden_projection",
    "adapter_hidden_bias", "adapter_location",
)
VELOCITY_LIMITS = "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def normalizer_state(value: dict[str, Any]) -> Any:
    from brax.training import types
    from brax.training.acme import running_statistics

    return running_statistics.RunningStatisticsState(
        mean=value["mean"], std=value["std"],
        count=types.UInt64(hi=value["count"]["hi"], lo=value["count"]["lo"]),
        summed_variance=value["summed_variance"], std_eps=value["std_eps"],
    )


def tree_errors(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def expand_checkpoint(source: list[Any], networks: Any) -> list[Any]:
    initialized = flax.core.unfreeze(networks.policy_network.init(jax.random.PRNGKey(100)))
    source_policy = flax.core.unfreeze(source[1])
    for key in BASE_KEYS:
        initialized["params"][key] = copy.deepcopy(source_policy["params"][key])
    expanded = copy.deepcopy(source)
    expanded[1] = initialized
    count = float(np.asarray(source[0]["count"]["lo"]))
    expanded[0]["mean"]["policy_hidden"] = jnp.zeros((64,), dtype=jnp.float32)
    expanded[0]["std"]["policy_hidden"] = jnp.ones((64,), dtype=jnp.float32)
    expanded[0]["summed_variance"]["policy_hidden"] = jnp.full(
        (64,), count, dtype=jnp.float32
    )
    return expanded


def path_name(path: tuple[Any, ...]) -> str:
    parts = []
    for entry in path:
        parts.append(str(getattr(entry, "key", getattr(entry, "idx", entry))))
    return "/".join(parts)


def leaf_deltas(initial: Any, final: Any) -> dict[str, float]:
    initial_rows, structure = jax.tree_util.tree_flatten_with_path(initial)
    final_rows, final_structure = jax.tree_util.tree_flatten_with_path(final)
    if structure != final_structure:
        raise ValueError("trained actor tree structure changed")
    return {
        path_name(ipath): float(np.max(np.abs(np.asarray(after) - np.asarray(before))))
        for (ipath, before), (fpath, after) in zip(initial_rows, final_rows, strict=True)
        if ipath == fpath
    }


def run_training(playground: Path, expanded: Path, output: Path) -> dict[str, Any]:
    command = [
        sys.executable, "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash", "--env", "joystick",
        "--output_dir", str(output), "--num_timesteps", "1024",
        "--ppo_seed", "100", "--ppo_num_envs", "4", "--ppo_num_evals", "2",
        "--ppo_episode_length", "64", "--ppo_unroll_length", "8",
        "--ppo_batch_size", "4", "--ppo_num_minibatches", "1",
        "--ppo_num_updates_per_batch", "2", "--ppo_learning_rate", "0.0003",
        "--ppo_discounting", "0.97", "--ppo_entropy_cost", "0.005",
        "--policy_architecture", "reference_residual_recurrent_adapter",
        "--recurrent_hidden_size", "64", "--imitation_scale", "1.0",
        "--reference_feature_table_path", str(REFERENCE),
        "--nominal_reference_bootstrap", "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x", "0.074",
        "--ground_up_command_support_max_x", "0.080",
        "--ground_up_action_velocity_limits_rad_s", VELOCITY_LIMITS,
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks", "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s", ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale", "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad", "0.20",
        "--reference_start_phase", "0", "--ground_up_signed_progress_objective",
        "--critic_observation", "privileged_state",
        "--restore_checkpoint_path", str(expanded),
    ]
    environment = dict(os.environ)
    environment.update({
        "PYTHONPATH": str(playground), "CUDA_VISIBLE_DEVICES": "",
        "HIP_VISIBLE_DEVICES": "", "ROCR_VISIBLE_DEVICES": "",
        "JAX_PLATFORMS": "cpu", "JAX_PLATFORM_NAME": "cpu",
    })
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=playground, env=environment, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=1800, check=False,
    )
    elapsed = time.monotonic() - started
    log = output.parent / "winner_v3_recurrent_adapter_cpu_smoke.log"
    log.write_text(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(
            f"CPU smoke failed rc={completed.returncode}; log={log}; "
            f"tail={completed.stdout[-4000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    onnx_files = sorted(output.glob("*.onnx"))
    final_checkpoints = [path for path in checkpoints if path.name.endswith("_1024")]
    final_onnx = [path for path in onnx_files if path.stem.endswith("_1024")]
    if len(final_checkpoints) != 1 or len(final_onnx) != 1:
        raise RuntimeError(f"unexpected smoke exports: {checkpoints}, {onnx_files}")
    return {
        "command": command,
        "elapsed_seconds": elapsed,
        "log_path": str(log),
        "log_sha256": sha256(log),
        "final_checkpoint": final_checkpoints[0],
        "final_onnx": final_onnx[0],
        "all_checkpoint_steps": sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints),
        "all_onnx_steps": sorted(int(path.stem.rsplit("_", 1)[1]) for path in onnx_files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument(
        "--work-root", type=Path,
        default=Path("/tmp/winner_v3_recurrent_adapter_cpu_contract"),
    )
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"no retry/resume: work root exists: {work}")
    work.mkdir(parents=True)

    hashes = {
        "prereg": sha256(PREREG), "archive": sha256(ARCHIVE),
        "reference": sha256(REFERENCE), "adapter_source": sha256(ADAPTER_SOURCE),
        "integration_patch": sha256(INTEGRATION_PATCH),
    }
    if hashes != EXPECTED:
        raise ValueError(f"input hash mismatch: {hashes}")
    playground_adapter = playground / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    if sha256(playground_adapter) != EXPECTED["adapter_source"]:
        raise ValueError("composed playground adapter source mismatch")

    sys.path.insert(0, str(playground))
    from brax.training.acme import running_statistics
    from playground.common.reference_residual_ppo_networks import make_reference_residual_ppo_networks
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (
        HIDDEN_OBSERVATION_KEY,
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    devices = [str(device) for device in jax.devices()]
    cpu_only = bool(devices and all(device.platform == "cpu" for device in jax.devices()))
    source_root = work / "source"
    source_root.mkdir()
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        members = [
            member for member in archive
            if member.name == str(SOURCE_MEMBER)
            or member.name.startswith(str(SOURCE_MEMBER) + "/")
        ]
        archive.extractall(source_root, members=members, filter="data")
    source_path = source_root / SOURCE_MEMBER
    checkpointer = ocp.PyTreeCheckpointer()
    if sha256_directory(CPU_TEMPLATE) != CPU_TEMPLATE_SHA256:
        raise ValueError("established CPU restore template hash mismatch")
    if sha256_directory(source_path) != SOURCE_DIRECTORY_SHA256:
        raise ValueError("archive-extracted source directory hash mismatch")
    cpu_template = checkpointer.restore(str(CPU_TEMPLATE))
    restore_args = orbax_utils.restore_args_from_target(cpu_template)
    source_checkpoint = checkpointer.restore(
        str(source_path), item=cpu_template, restore_args=restore_args
    )
    processor = normalizer_state(source_checkpoint[0])
    observation_size = {
        "state": (115,), "privileged_state": (226,), HIDDEN_OBSERVATION_KEY: (64,),
    }
    base_networks = make_reference_residual_ppo_networks(
        observation_size, 14,
        preprocess_observations_fn=running_statistics.normalize,
    )
    adapter_networks = make_reference_residual_recurrent_adapter_ppo_networks(
        observation_size, 14,
        preprocess_observations_fn=running_statistics.normalize,
        recurrent_hidden_size=64,
    )
    expanded_checkpoint = expand_checkpoint(source_checkpoint, adapter_networks)
    expanded_path = work / "expanded_checkpoint"
    checkpointer.save(str(expanded_path), expanded_checkpoint)
    restored_expanded = checkpointer.restore(str(expanded_path))
    save_structure, save_error = tree_errors(expanded_checkpoint, restored_expanded)

    rng = np.random.Generator(np.random.PCG64(100))
    vectors = [
        np.zeros((1, 115), np.float32),
        np.linspace(-0.25, 0.25, 115, dtype=np.float32)[None],
    ]
    vectors.extend(rng.uniform(-0.5, 0.5, (1, 115)).astype(np.float32) for _ in range(62))
    equivalence = []
    hidden_changed = []
    for index, obs in enumerate(vectors):
        hidden = rng.uniform(-0.5, 0.5, (1, 64)).astype(np.float32)
        base_logits = base_networks.policy_network.apply(
            processor, source_checkpoint[1], {"state": jnp.asarray(obs)}
        )
        adapter_logits, next_hidden = adapter_networks.policy_network.apply_with_state(
            processor, restored_expanded[1],
            {"state": jnp.asarray(obs), HIDDEN_OBSERVATION_KEY: jnp.asarray(hidden)},
        )
        equivalence.append({
            "index": index,
            "logits_bit_exact": bool(np.array_equal(np.asarray(base_logits), np.asarray(adapter_logits))),
            "max_abs_error": float(np.max(np.abs(np.asarray(base_logits) - np.asarray(adapter_logits)))),
        })
        hidden_changed.append(not np.array_equal(hidden, np.asarray(next_hidden)))

    initial_params = flax.core.unfreeze(restored_expanded[1])["params"]
    source_params = flax.core.unfreeze(source_checkpoint[1])["params"]
    base_preserved = all(tree_errors(source_params[key], initial_params[key]) == (True, 0.0) for key in BASE_KEYS)
    adapter_head_zero = bool(
        np.count_nonzero(np.asarray(initial_params["adapter_location"]["kernel"])) == 0
        and np.count_nonzero(np.asarray(initial_params["adapter_location"]["bias"])) == 0
    )

    initial_onnx = work / "expanded_step_zero.onnx"
    initial_export = export_reference_residual_recurrent_adapter_onnx(
        (processor, restored_expanded[1]), 14, 115, 64, initial_onnx,
        (512, 256, 128),
        action_velocity_limits_rad_s=[float(value) for value in VELOCITY_LIMITS.split(",")],
    )
    smoke_output = work / "smoke"
    smoke_output.mkdir()
    training = run_training(playground, expanded_path, smoke_output)
    trained_checkpoint = checkpointer.restore(str(training["final_checkpoint"]))
    trained_params = flax.core.unfreeze(trained_checkpoint[1])["params"]
    deltas = leaf_deltas(initial_params, trained_params)
    base_delta = max((value for name, value in deltas.items() if any(key in name for key in BASE_KEYS)), default=0.0)
    adapter_state_delta = max((value for name, value in deltas.items() if any(key in name for key in ADAPTER_KEYS[:-1])), default=0.0)
    adapter_head_delta = max((value for name, value in deltas.items() if "adapter_location" in name), default=0.0)
    trained_finite = all(np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree_util.tree_leaves(trained_checkpoint))

    import onnx
    import onnxruntime as ort

    model = onnx.load(training["final_onnx"])
    abi_inputs = {item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim] for item in model.graph.input}
    abi_outputs = {item.name: [dim.dim_value for dim in item.type.tensor_type.shape.dim] for item in model.graph.output}
    session = ort.InferenceSession(str(training["final_onnx"]), providers=["CPUExecutionProvider"])
    hidden = np.zeros((1, 64), np.float32)
    previous = np.zeros((1, 14), np.float32)
    chained_finite = True
    for tick in range(256):
        obs = np.linspace(-0.2, 0.2, 115, dtype=np.float32)[None] + np.float32(tick * 1e-5)
        action, previous_out, hidden_out = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        chained_finite &= bool(np.isfinite(action).all() and np.isfinite(previous_out).all() and np.isfinite(hidden_out).all())
        previous, hidden = previous_out, hidden_out

    checks = {
        "input_hashes_exact": hashes == EXPECTED,
        "cpu_only_jax": cpu_only,
        "source_checkpoint_shape_exact": (
            np.asarray(source_checkpoint[0]["mean"]["state"]).shape == (115,)
            and np.asarray(source_checkpoint[0]["mean"]["privileged_state"]).shape == (226,)
        ),
        "established_cpu_restore_template_exact": (
            sha256_directory(CPU_TEMPLATE) == CPU_TEMPLATE_SHA256
            and jax.tree_util.tree_structure(cpu_template)
            == jax.tree_util.tree_structure(source_checkpoint)
        ),
        "remapped_source_leaves_cpu_only": all(
            getattr(leaf, "sharding", None) is None
            or all(device.platform == "cpu" for device in leaf.sharding.device_set)
            for leaf in jax.tree_util.tree_leaves(source_checkpoint)
        ),
        "expanded_save_restore_bit_exact": save_structure and save_error == 0.0,
        "expanded_hidden_normalizer_exact": (
            np.array_equal(
                np.asarray(restored_expanded[0]["mean"]["policy_hidden"]),
                np.zeros(64, dtype=np.float32),
            )
            and np.array_equal(
                np.asarray(restored_expanded[0]["std"]["policy_hidden"]),
                np.ones(64, dtype=np.float32),
            )
            and np.array_equal(
                np.asarray(restored_expanded[0]["summed_variance"]["policy_hidden"]),
                np.full(
                    64,
                    float(np.asarray(restored_expanded[0]["count"]["lo"])),
                    dtype=np.float32,
                ),
            )
        ),
        "protected_base_actor_bit_exact": base_preserved,
        "adapter_head_exact_zero": adapter_head_zero,
        "all_64_step_zero_logits_bit_exact": all(row["logits_bit_exact"] for row in equivalence),
        "hidden_state_evolves": all(hidden_changed),
        "initial_onnx_jax_within_1e_7": max(initial_export["max_action_error"], initial_export["max_hidden_error"]) <= 1e-7,
        "smoke_exact_steps": training["all_checkpoint_steps"] == [0, 1024] and training["all_onnx_steps"] == [0, 1024],
        "trained_tree_all_finite": trained_finite,
        "protected_base_actor_updated": base_delta > 0.0,
        "adapter_state_updated": adapter_state_delta > 0.0,
        "adapter_head_updated": adapter_head_delta > 0.0,
        "trained_onnx_abi_exact": abi_inputs == {"obs": [1, 115], "previous_action": [1, 14], "h_in": [1, 64]} and abi_outputs == {"continuous_actions": [1, 14], "previous_action_out": [1, 14], "h_out": [1, 64]},
        "trained_onnx_cpu_provider": session.get_providers() == ["CPUExecutionProvider"],
        "trained_onnx_256_tick_chain_finite": chained_finite,
        "smoke_wall_seconds_at_most_1800": training["elapsed_seconds"] <= 1800,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT" if not failed else "HOLD_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT"
    payload = {
        "schema_version": "winner_v3.recurrent_adapter_cpu_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": hashes,
        "devices": devices,
        "source_checkpoint_directory_sha256": sha256_directory(source_path),
        "cpu_restore_template": {
            "path": str(CPU_TEMPLATE),
            "directory_sha256": sha256_directory(CPU_TEMPLATE),
        },
        "expanded_checkpoint_directory_sha256": sha256_directory(expanded_path),
        "step_zero_equivalence": equivalence,
        "step_zero_max_abs_error": max(row["max_abs_error"] for row in equivalence),
        "initial_export": initial_export,
        "training": {
            key: value for key, value in training.items()
            if key not in ("final_checkpoint", "final_onnx")
        },
        "training_artifacts": {
            "final_checkpoint_path": str(training["final_checkpoint"]),
            "final_checkpoint_directory_sha256": sha256_directory(training["final_checkpoint"]),
            "final_onnx_path": str(training["final_onnx"]),
            "final_onnx_sha256": sha256(training["final_onnx"]),
        },
        "actor_leaf_max_deltas": deltas,
        "update_family_max_delta": {
            "protected_base": base_delta,
            "adapter_state": adapter_state_delta,
            "adapter_head": adapter_head_delta,
        },
        "trained_onnx_abi": {"inputs": abi_inputs, "outputs": abi_outputs},
        "authority": {
            "single_cpu_training_curriculum_after_pass": not failed,
            "hosted_or_colab": False, "gpu_or_igpu": False,
            "rdkx5_or_robot": False, "runtime_or_deployment": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    OUTPUT_MD.write_text(f"""# Winner-v3 Recurrent-Adapter CPU Contract — 2026-07-19

Status: `{status}`

- JAX devices: `{devices}`
- source checkpoint directory SHA-256: `{payload['source_checkpoint_directory_sha256']}`
- step-zero maximum base/adapter logits error: `{payload['step_zero_max_abs_error']}`
- initial ONNX action/hidden error: `{initial_export['max_action_error']}` / `{initial_export['max_hidden_error']}`
- CPU smoke exports: `{training['all_checkpoint_steps']}`
- CPU smoke wall seconds: `{training['elapsed_seconds']:.3f}`
- base/adapter-state/adapter-head maximum updates: `{base_delta}` / `{adapter_state_delta}` / `{adapter_head_delta}`
- trained ONNX SHA-256: `{payload['training_artifacts']['final_onnx_sha256']}`
- failed checks: `{failed}`

This is a plumbing and finite-update contract only. Training reward and the
1,024-step policy behavior have no selection weight and make no gait claim. A
pass authorizes only the single preregistered CPU curriculum and its later
frozen CPU evaluation. It does not authorize Colab/hosted allocation,
GPU/iGPU, RDK-X5, robot, serial, torque, motion, runtime execution, Gate 5,
deployment, or robot clearance.
""")
    print(status)
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
