#!/usr/bin/env python3
"""Run the preregistered peak-torque recurrent CPU restore/update/export smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
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

import jax
import numpy as np
import onnx
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v111_peak_torque_cpu_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
RESULT = ANALYSIS / "winner_v111_peak_torque_cpu_result.json"
MARKDOWN = ANALYSIS / "WINNER_V111_PEAK_TORQUE_CPU_RESULT_20260724.md"
PREREG_SHA256 = (
    "a79f0dfbb9ca11c194767f4f7bb91dfda200d1b1397654ed125495cad071c9bb"
)
VELOCITY_LIMITS = (
    "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"
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
        digest.update(
            str(child.relative_to(path)).replace("\\", "/").encode()
        )
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def tree_errors(before: Any, after: Any) -> tuple[bool, dict[str, float]]:
    before_rows, before_structure = jax.tree_util.tree_flatten_with_path(before)
    after_rows, after_structure = jax.tree_util.tree_flatten_with_path(after)
    if before_structure != after_structure:
        return False, {}
    deltas = {}
    for (before_path, left), (after_path, right) in zip(
        before_rows, after_rows, strict=True
    ):
        if before_path != after_path:
            return False, {}
        name = "/".join(
            str(getattr(item, "key", getattr(item, "idx", item)))
            for item in before_path
        )
        deltas[name] = float(
            np.max(np.abs(np.asarray(right) - np.asarray(left)))
        )
    return True, deltas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing to reuse work root: {work}")
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite Winner-v111 result")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("Winner-v111 preregistration changed")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
        or not prereg.get("authority", {}).get("cpu_smoke_authorized")
    ):
        raise ValueError("Winner-v111 CPU smoke is not authorized")
    if sha256_directory(source) != prereg["source"][
        "checkpoint_directory_sha256"
    ]:
        raise ValueError("source checkpoint changed")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("Winner-v111 execution requires a clean worktree")
    work.mkdir(parents=True)
    output = work / "smoke"
    output.mkdir()
    log = work / "training.log"

    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        default_config,
        ground_up_peak_torque_exceedance_cost,
    )

    threshold = prereg["objective"]["threshold_nm"]
    analytic_force = np.zeros(14, dtype=np.float32)
    analytic_force[3] = np.float32(threshold + 0.2)
    observed_cost = float(
        ground_up_peak_torque_exceedance_cost(
            jax.numpy.asarray(analytic_force), threshold
        )
    )
    expected_cost = float(np.mean(np.maximum(np.abs(analytic_force) - threshold, 0.0) ** 2))
    config = default_config()
    default_off = float(config.reward_config.scales.peak_torque_exceedance)

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
        "reference_residual_recurrent_adapter",
        "--recurrent_hidden_size",
        "64",
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
        "--ground_up_peak_torque_exceedance_scale",
        "-1000",
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(source),
    ]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(playground)
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
        check=False,
    )
    elapsed = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"CPU smoke failed rc={completed.returncode}; "
            f"tail={completed.stdout[-4000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    onnx_files = sorted(output.glob("*.onnx"))
    steps = sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints)
    onnx_steps = sorted(
        int(path.stem.rsplit("_", 1)[1]) for path in onnx_files
    )
    if steps != [0, 1024] or onnx_steps != [0, 1024]:
        raise ValueError(f"unexpected smoke exports: {steps}, {onnx_steps}")
    initial_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_0")
    )
    final_checkpoint = next(
        path for path in checkpoints if path.name.endswith("_1024")
    )
    final_onnx = next(path for path in onnx_files if path.stem.endswith("_1024"))
    checkpointer = ocp.PyTreeCheckpointer()
    source_tree = checkpointer.restore(str(source))
    initial_tree = checkpointer.restore(str(initial_checkpoint))
    final_tree = checkpointer.restore(str(final_checkpoint))
    initial_structure, initial_deltas = tree_errors(
        source_tree, initial_tree
    )
    trained_structure, trained_deltas = tree_errors(
        initial_tree, final_tree
    )
    policy_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("1/params/")
    }
    all_finite = all(
        np.all(np.isfinite(np.asarray(leaf)))
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )

    model = onnx.load(final_onnx)
    inputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.input
    }
    outputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.output
    }
    session = ort.InferenceSession(
        str(final_onnx), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    chain_finite = True
    for tick in range(256):
        obs = np.linspace(-0.2, 0.2, 115, dtype=np.float32)[None]
        obs = obs + np.float32(tick * 1.0e-5)
        action, previous, hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        chain_finite &= bool(
            np.all(np.isfinite(action))
            and np.all(np.isfinite(previous))
            and np.all(np.isfinite(hidden))
        )
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "analytic_hinge_exact": abs(observed_cost - expected_cost) <= 1.0e-8,
        "default_off_scale_exact_zero": default_off == 0.0,
        "exact_exports_0_and_1024": steps == [0, 1024]
        and onnx_steps == [0, 1024],
        "source_restore_structure_exact": initial_structure,
        "source_restore_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_structure_exact": trained_structure,
        "trained_tree_all_finite": bool(all_finite),
        "every_policy_leaf_updated": bool(policy_deltas)
        and all(value > 0.0 for value in policy_deltas.values()),
        "objective_metric_present": (
            "peak_torque_exceedance" in completed.stdout
        ),
        "onnx_abi_exact": inputs
        == {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        }
        and outputs
        == {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
        "onnx_cpu_provider_exact": session.get_providers()
        == ["CPUExecutionProvider"],
        "onnx_256_tick_chain_finite": chain_finite,
        "wall_seconds_at_most_1800": elapsed <= 1800.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v111.peak_torque_cpu_result.v1",
        "status": (
            "PASS_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
            if not failed
            else "HOLD_WINNER_V111_PEAK_TORQUE_CPU_SMOKE"
        ),
        "failed_checks": failed,
        "checks": checks,
        "analytic_objective": {
            "observed": observed_cost,
            "expected": expected_cost,
            "max_abs_error": abs(observed_cost - expected_cost),
            "default_off_scale": default_off,
        },
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "checkpoint_steps": steps,
            "onnx_steps": onnx_steps,
            "initial_checkpoint_sha256": sha256_directory(
                initial_checkpoint
            ),
            "final_checkpoint_sha256": sha256_directory(final_checkpoint),
            "final_onnx_sha256": sha256(final_onnx),
            "log_sha256": sha256(log),
            "policy_leaf_deltas": policy_deltas,
        },
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "source_checkpoint": sha256_directory(source),
            "playground_manifest": sha256(
                playground / "WINNER_V111_COMPOSED_SOURCE_MANIFEST.json"
            ),
        },
        "run_root": str(work),
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v111 peak-torque CPU smoke result\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        f"Wall time: `{elapsed}` s\n\n"
        "A pass authorizes only a separate hosted-run preregistration. It does "
        "not authorize hosted training by itself, behavior selection, Gate 5, "
        "robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
