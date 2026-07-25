#!/usr/bin/env python3
"""Run the one frozen V127 constrained continuation on a hosted GPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
from typing import Any

import jax
import onnx


EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
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


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def graph_io(path: Path) -> dict[str, dict[str, list[int]]]:
    model = onnx.load(path)
    return {
        field: {
            item.name: [
                int(dim.dim_value)
                for dim in item.type.tensor_type.shape.dim
            ]
            for item in getattr(model.graph, field)
        }
        for field in ("input", "output")
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
        "0",
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
        "--winner_v119_train_transition_match",
        "--winner_v127_constrained_cost",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(source),
    ]


def validate_bundle(bundle: Path) -> dict[str, Any]:
    prereg_candidates = (
        bundle / "winner_v127d_hosted_preregistration.json",
        bundle / "winner_v127c_hosted_preregistration.json",
        bundle / "winner_v127_hosted_preregistration.json",
    )
    prereg_path = next(
        (path for path in prereg_candidates if path.is_file()),
        prereg_candidates[-1],
    )
    cpu_result_path = bundle / "winner_v127_constrained_cpu_result.json"
    cpu_prereg_path = (
        bundle / "winner_v127_constrained_cpu_preregistration.json"
    )
    playground = bundle / "playground"
    source = bundle / "assets/source_checkpoint"
    reference = (
        bundle / "assets/ground_up_projected_reference_feature_table.npz"
    )
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    cpu_result = json.loads(cpu_result_path.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        not in (
            "PREREGISTERED_WINNER_V127_HOSTED_CONTINUATION",
            "PREREGISTERED_WINNER_V127C_HOSTED_CONTINUATION",
            "PREREGISTERED_WINNER_V127D_HOSTED_CONTINUATION",
        )
        or prereg.get("failed_checks") != []
        or cpu_result.get("status")
        != "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
        or cpu_result.get("failed_checks") != []
    ):
        raise ValueError("V127 hosted prerequisites are not green")
    observed = {
        "driver": sha256(Path(__file__).resolve()),
        "cpu_result": sha256(cpu_result_path),
        "cpu_preregistration": sha256(cpu_prereg_path),
        "composed_manifest": sha256(
            playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(reference),
    }
    correction = bundle / "winner_v127_pretraining_launch_correction.json"
    if correction.is_file():
        observed["pretraining_launch_correction"] = sha256(correction)
    archive_root_correction = (
        bundle / "winner_v127_archive_root_correction.json"
    )
    if archive_root_correction.is_file():
        observed["archive_root_correction"] = sha256(
            archive_root_correction
        )
    if observed != prereg["input_hashes"]:
        raise ValueError(f"V127 bundle inputs changed: {observed}")
    manifest = json.loads(
        (
            playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )
    for relative, expected in manifest["final_python_hashes"].items():
        if sha256(playground / relative) != expected:
            raise ValueError(f"V127 composed source changed: {relative}")
    devices = [str(device) for device in jax.devices()]
    if (
        not devices
        or not all(device.platform == "gpu" for device in jax.devices())
        or jax.process_count() != 1
    ):
        raise RuntimeError(f"V127 requires one GPU process: {devices}")
    return {
        "input_hashes": observed,
        "devices": devices,
        "process_count": jax.process_count(),
        "preregistration_sha256": sha256(prereg_path),
    }


def make_archive(work: Path, destination: Path) -> dict[str, Any]:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz") as archive:
        archive.add(work, arcname="winner_v127_constrained_continuation")
    temporary.replace(destination)
    return {
        "path": str(destination),
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
    }


def run(
    bundle: Path,
    work: Path,
    output_json: Path,
    output_archive: Path,
) -> int:
    for path in (work, output_json, output_archive):
        if path.exists():
            raise FileExistsError(f"V127 no-retry path exists: {path}")
    validation = validate_bundle(bundle)
    work.mkdir(parents=True)
    output = work / "training"
    output.mkdir()
    log = work / "training.log"
    playground = bundle / "playground"
    source = bundle / "assets/source_checkpoint"
    reference = (
        bundle / "assets/ground_up_projected_reference_feature_table.npz"
    )
    command = runner_command(playground, output, source, reference)
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
        timeout=21_600,
        check=False,
    )
    elapsed = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        failure = {
            "schema_version": "winner_v127.hosted_result.v1",
            "status": "HOLD_WINNER_V127_HOSTED_CONTINUATION",
            "returncode": completed.returncode,
            "elapsed_seconds": elapsed,
            "validation": validation,
            "command": command,
            "log_sha256": sha256(log),
            "tail": completed.stdout[-5000:],
            "retry_authorized": False,
        }
        output_json.write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        make_archive(work, output_archive)
        return 1

    policy_dirs = [
        path
        for path in output.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    ]
    cost_dirs = list(output.glob("*_v127_cost_value"))
    graphs = list(output.glob("*.onnx"))
    aux_paths = list(output.glob("*_v127_aux.json"))
    policy_by_step = {
        int(path.name.rsplit("_", 1)[1]): path for path in policy_dirs
    }
    cost_by_step = {
        int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
        for path in cost_dirs
    }
    graph_by_step = {
        int(path.stem.rsplit("_", 1)[1]): path for path in graphs
    }
    aux_by_step = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in aux_paths
    }
    all_steps = (
        sorted(policy_by_step)
        == sorted(cost_by_step)
        == sorted(graph_by_step)
        == sorted(aux_by_step)
        == EXPECTED_STEPS
    )
    aux = {
        str(step): json.loads(path.read_text(encoding="utf-8"))
        for step, path in aux_by_step.items()
    }
    aux_finite = all(
        all(
            math.isfinite(float(row[key]))
            for key in ("lambda", "eta", "initial_cost")
        )
        for row in aux.values()
    )
    graph_rows = {
        str(step): {
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "io": graph_io(path),
        }
        for step, path in graph_by_step.items()
    }
    checks = {
        "runner_returncode_zero": completed.returncode == 0,
        "wall_seconds_at_most_21600": elapsed <= 21_600,
        "exports_exact": all_steps,
        "all_aux_scalars_finite": aux_finite,
        "dual_initialized_by_half": bool(aux["1003520"]["initialized"]),
        "dual_lambda_positive_by_half": float(aux["1003520"]["lambda"]) > 0.0,
        "all_graphs_valid": all(
            onnx.checker.check_model(onnx.load(path)) is None
            for path in graph_by_step.values()
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    archive = make_archive(work, output_archive)
    result = {
        "schema_version": "winner_v127.hosted_result.v1",
        "status": (
            "PASS_WINNER_V127_HOSTED_CONTINUATION_ARTIFACT"
            if not failed
            else "HOLD_WINNER_V127_HOSTED_CONTINUATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "validation": validation,
        "command": command,
        "elapsed_seconds": elapsed,
        "log_sha256": sha256(log),
        "policy_checkpoint_sha256": {
            str(step): directory_sha256(path)
            for step, path in policy_by_step.items()
        },
        "cost_checkpoint_sha256": {
            str(step): directory_sha256(path)
            for step, path in cost_by_step.items()
        },
        "graphs": graph_rows,
        "dual": aux,
        "archive": archive,
        "decision": (
            "AUTHORIZE_CPU_TOPOLOGY_VALIDATION_ONLY"
            if not failed
            else "NO_RETRY"
        ),
        "authority": {
            "cpu_topology_validation": not failed,
            "behavior_evaluation": False,
            "retry_or_resume": False,
            "robot_or_rdk": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    output_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--hosted-gpu-authorized", action="store_true")
    args = parser.parse_args()
    if not args.hosted_gpu_authorized:
        raise PermissionError("V127 requires hosted GPU authorization")
    return run(
        args.bundle_root.resolve(),
        args.work_root.resolve(),
        args.output_json.resolve(),
        args.output_archive.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
