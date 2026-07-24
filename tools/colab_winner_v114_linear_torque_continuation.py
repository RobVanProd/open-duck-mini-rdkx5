#!/usr/bin/env python3
"""Run the one frozen Winner-v114 linear-torque GPU continuation."""

from __future__ import annotations

import argparse
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

import jax
import numpy as np
import onnx
import onnxruntime as ort


PREREGISTRATION_NAME = (
    "winner_v114_linear_torque_hosted_preregistration.json"
)
CPU_RESULT_NAME = "winner_v114_linear_torque_cpu_result.json"
COMPOSED_MANIFEST_NAME = "WINNER_V114_COMPOSED_SOURCE_MANIFEST.json"
REFERENCE_NAME = "ground_up_projected_reference_feature_table.npz"
SOURCE_CHECKPOINT_NAME = "source_checkpoint"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
MAX_WALL_SECONDS = 21_600
VELOCITY_LIMITS = (
    "1.0,.75,1.5,1.5,1.5,.5,.5,.5,.5,.5,.75,1.25,1.0,1.25"
)


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


def step_from_path(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def describe_onnx(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
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
    expected_inputs = {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
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
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    chain_finite = True
    for tick in range(256):
        obs = np.linspace(-0.2, 0.2, 115, dtype=np.float32)[None]
        obs += np.float32(tick * 1.0e-5)
        action, previous, hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        chain_finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(previous).all()
            and np.isfinite(hidden).all()
        )
    return {
        "step": step_from_path(path),
        "sha256": sha256(path),
        "inputs": inputs,
        "outputs": outputs,
        "abi_exact": inputs == expected_inputs and outputs == expected_outputs,
        "initializers_finite": bool(initializers_finite),
        "cpu_256_tick_chain_finite": chain_finite,
        "providers": session.get_providers(),
    }


def runner_command(
    playground: Path,
    output: Path,
    source: Path,
    reference: Path,
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
        "2007040",
        "--ppo_seed",
        "100",
        "--ppo_num_envs",
        "256",
        "--ppo_num_evals",
        "3",
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
        "reference_residual_recurrent_adapter",
        "--recurrent_hidden_size",
        "64",
        "--imitation_scale",
        "1.0",
        "--reference_feature_table_path",
        str(reference),
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
        "0",
        "--ground_up_linear_peak_torque_exceedance_scale",
        "-307.48131091308585",
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


def validate_inputs(bundle: Path) -> dict[str, Any]:
    prereg_path = bundle / PREREGISTRATION_NAME
    cpu_result_path = bundle / CPU_RESULT_NAME
    playground = bundle / "playground"
    source = bundle / "assets" / SOURCE_CHECKPOINT_NAME
    reference = bundle / "assets" / REFERENCE_NAME
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    cpu_result = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
        or cpu_result.get("status")
        != "PASS_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
        or cpu_result.get("failed_checks") != []
        or cpu_result.get("authority", {}).get(
            "hosted_preregistration_authorized"
        )
        is not True
    ):
        raise ValueError("Winner-v114 prerequisite status changed")
    observed = {
        "driver": sha256(Path(__file__).resolve()),
        "cpu_result": sha256(cpu_result_path),
        "composed_manifest": sha256(
            playground / COMPOSED_MANIFEST_NAME
        ),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(reference),
    }
    if observed != prereg["input_hashes"]:
        raise ValueError(
            f"Winner-v114 inputs changed: {observed} != "
            f"{prereg['input_hashes']}"
        )
    manifest = json.loads(
        (playground / COMPOSED_MANIFEST_NAME).read_text(encoding="utf-8")
    )
    for relative, expected in manifest["final_python_hashes"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"composed source changed: {relative}")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"Winner-v114 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(prereg_path),
    }


def make_artifact(work: Path, destination: Path) -> dict[str, Any]:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(
            work, arcname="winner_v114_linear_torque_continuation"
        )
    temporary.replace(destination)
    return {
        "path": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    for path in (work, output_json, output_archive):
        if path.exists():
            raise FileExistsError(f"Winner-v114 no-retry path exists: {path}")
    validation = validate_inputs(bundle)
    work.mkdir(parents=True)
    output = work / "training"
    output.mkdir()
    log = work / "training.log"
    playground = bundle / "playground"
    source = bundle / "assets" / SOURCE_CHECKPOINT_NAME
    reference = bundle / "assets" / REFERENCE_NAME
    command = runner_command(playground, output, source, reference)
    started = time.monotonic()
    payload: dict[str, Any] = {
        "schema_version": "winner_v114.linear_torque_hosted_result.v1",
        "status": "RUNNING_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION",
        "validation": validation,
        "command": command,
        "formal_behavior_cells_executed": 0,
        "authority": {
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
        },
    }
    run_state = work / "run_state.json"
    run_state.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    try:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(playground)
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(
                command,
                cwd=playground,
                env=environment,
                text=True,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=MAX_WALL_SECONDS,
                check=False,
            )
        if completed.returncode != 0:
            raise RuntimeError(
                f"Winner-v114 runner returned {completed.returncode}"
            )
        elapsed = time.monotonic() - started
        checkpoints = sorted(
            (path for path in output.iterdir() if path.is_dir()),
            key=step_from_path,
        )
        graphs = sorted(output.glob("*.onnx"), key=step_from_path)
        checkpoint_steps = [step_from_path(path) for path in checkpoints]
        onnx_steps = [step_from_path(path) for path in graphs]
        graph_rows = [describe_onnx(path) for path in graphs]
        checks = {
            "gpu_only": all(
                device.platform == "gpu" for device in jax.devices()
            ),
            "single_jax_process": jax.process_count() == 1,
            "exact_exports": checkpoint_steps == EXPECTED_STEPS
            and onnx_steps == EXPECTED_STEPS,
            "all_checkpoint_directories_nonempty": all(
                any(path.rglob("*")) for path in checkpoints
            ),
            "all_onnx_contracts_pass": all(
                row["abi_exact"]
                and row["initializers_finite"]
                and row["cpu_256_tick_chain_finite"]
                and row["providers"] == ["CPUExecutionProvider"]
                for row in graph_rows
            ),
            "within_wall_ceiling": elapsed <= MAX_WALL_SECONDS,
            "formal_behavior_cells_zero": True,
        }
        failed = sorted(
            name for name, passed in checks.items() if not passed
        )
        payload.update(
            {
                "status": (
                    "PASS_WINNER_V114_TRAINING_ARTIFACT_PENDING_CPU_TOPOLOGY_VALIDATION"
                    if not failed
                    else "HOLD_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
                ),
                "checks": checks,
                "failed_checks": failed,
                "wall_seconds": elapsed,
                "checkpoint_steps": checkpoint_steps,
                "onnx_steps": onnx_steps,
                "checkpoints": [
                    {
                        "step": step_from_path(path),
                        "directory_sha256": directory_sha256(path),
                    }
                    for path in checkpoints
                ],
                "onnx": graph_rows,
                "training_log_sha256": sha256(log),
                "cpu_topology_validation_required": True,
            }
        )
        run_state.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        if failed:
            raise ValueError(f"Winner-v114 artifact checks failed: {failed}")
        payload["artifact"] = make_artifact(work, output_archive)
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        print(payload["status"], flush=True)
        print(f"sha256={sha256(output_json)}", flush=True)
        return 0
    except BaseException as exc:
        payload["status"] = (
            "HOLD_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
        )
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["traceback"] = traceback.format_exc()
        payload["wall_seconds"] = time.monotonic() - started
        run_state.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        output_json.write_text(
            json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
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
        raise PermissionError("Winner-v114 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
