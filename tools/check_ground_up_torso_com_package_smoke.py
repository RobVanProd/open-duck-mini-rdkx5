#!/usr/bin/env python3
"""Verify the preregistered torso-COM package and 1,024-step CPU smoke."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path

import jax
import numpy as np
import onnx
import onnxruntime as ort

from check_ground_up_hard_vector_continuation_smoke import (
    read_metrics,
    restore_and_compare,
    sha256_file,
)


VELOCITY_LIMITS = np.asarray(
    [5.24, 5.24, 1.50, 1.50, 1.50, 5.24, 5.24, 5.24, 5.24,
     5.24, 5.24, 1.25, 1.00, 1.25],
    dtype=np.float32,
)
TAIL_TAG = "eval/episode_cost/tracking_tail_exceedance"


def load_job(path: Path):
    spec = importlib.util.spec_from_file_location("torso_com_job", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def value_after(command: list[str], flag: str) -> str:
    index = command.index(flag)
    return command[index + 1]


def inspect_onnx(path: Path) -> dict:
    model = onnx.load(path)
    onnx.checker.check_model(model)
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inputs = [item.name for item in model.graph.input]
    outputs = [item.name for item in model.graph.output]
    obs_size = int(session.get_inputs()[0].shape[-1])
    obs = np.zeros((1, obs_size), dtype=np.float32)
    previous = np.zeros((1, 14), dtype=np.float32)
    maximum_delta = VELOCITY_LIMITS * 0.02 / 0.25
    excess = []
    state_error = []
    finite = True
    for tick in range(8):
        obs[:, -14:] = 0.8 if tick % 2 == 0 else -0.8
        action, previous_out = session.run(
            outputs, {"obs": obs, "previous_action": previous}
        )
        finite &= bool(np.all(np.isfinite(action)))
        excess.append(float(np.max(np.abs(action - previous) - maximum_delta)))
        state_error.append(float(np.max(np.abs(previous_out - action))))
        previous = previous_out
    checks = {
        "interface_exact": inputs == ["obs", "previous_action"]
        and outputs == ["continuous_actions", "previous_action_out"],
        "actions_finite": finite,
        "conservative_eight_tick_bound_excess_at_most_1e_6": max(excess) <= 1e-6,
        "state_output_exact": max(state_error) <= 1e-7,
    }
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "checks": checks,
        "max_bound_excess": max(excess),
        "max_state_error": max(state_error),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--randomizer-contract", type=Path, required=True)
    parser.add_argument("--remap-report", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-checkpoint", type=Path, required=True)
    parser.add_argument("--final-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--final-onnx", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--composed-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    job = load_job(args.job.resolve())
    prereg = json.loads(args.preregistration.read_text())
    randomizer = json.loads(args.randomizer_contract.read_text())
    remap = json.loads(args.remap_report.read_text())
    assets = args.asset_root.resolve()
    composed = args.composed_root.resolve()

    asset_hashes = {
        name: sha256_file(assets / name) for name in job.EXPECTED_HASHES
    }
    asset_hashes_exact = asset_hashes == job.EXPECTED_HASHES
    checkpoint = restore_and_compare(
        args.source_checkpoint.resolve(),
        args.step_zero_checkpoint.resolve(),
        args.final_checkpoint.resolve(),
    )
    step_zero_onnx = inspect_onnx(args.step_zero_onnx.resolve())
    final_onnx = inspect_onnx(args.final_onnx.resolve())
    metrics = read_metrics(args.event_file.resolve())
    tail_values = metrics["scalars"].get(TAIL_TAG, [])

    commands = []
    for arm_name, stages in job.ARMS.items():
        restore = Path("/protected/source")
        for stage_index, stage in enumerate(stages, start=1):
            command = job.training_command(
                assets, Path(f"/output/{arm_name}/stage{stage_index}"), restore, stage
            )
            commands.append((arm_name, stage_index, stage, command))
            restore = Path(f"/output/{arm_name}/stage{stage_index}/final")

    commands_exact = all(
        "--nominal_reference_bootstrap" in command
        and "--ground_up_torso_com_randomization" in command
        and value_after(command, "--ground_up_torso_com_distribution") == stage["distribution"]
        and float(value_after(command, "--ground_up_torso_com_x_min_m")) == stage["min_x_m"]
        and float(value_after(command, "--ground_up_torso_com_x_max_m")) == stage["max_x_m"]
        and int(value_after(command, "--num_timesteps")) == stage["timesteps"]
        and value_after(command, "--ground_up_action_velocity_limits_rad_s").split(",")[4] == "1.50"
        and "--ground_up_applied_target_observation" in command
        and "--ground_up_measured_actuator_bridge" in command
        for _, _, stage, command in commands
    )
    expected_arm_names = [item["name"] for item in prereg["arms"]]
    composed_hashes = {
        "randomize_py": sha256_file(composed / "playground/common/randomize.py"),
        "runner_py": sha256_file(composed / "playground/open_duck_mini_v2/runner.py"),
    }
    contract_hashes = {
        "randomize_py": randomizer["inputs"]["randomize_py"]["sha256"],
        "runner_py": randomizer["inputs"]["runner_py"]["sha256"],
    }
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
        and os.environ.get("CUDA_VISIBLE_DEVICES") == "",
        "preregistration_status_exact": prereg["status"]
        == "PREREGISTERED_CPU_PACKAGE_CONTRACT_REQUIRED",
        "randomizer_contract_passed": randomizer["status"]
        == "PASS_GROUND_UP_TORSO_COM_RANDOMIZER_CONTRACT"
        and not randomizer["failed_checks"],
        "checkpoint_remap_passed": remap["status"] == "PASS_CPU_CHECKPOINT_REMAP"
        and remap["max_save_restore_error"] == 0.0,
        "all_uploaded_asset_hashes_exact": asset_hashes_exact,
        "source_archive_and_member_exact": (
            job.SOURCE_ARCHIVE == "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
            and str(job.SOURCE_CHECKPOINT_RELATIVE)
            == prereg["source"]["checkpoint_member"]
            and asset_hashes[job.SOURCE_ARCHIVE] == prereg["source"]["archive_sha256"]
        ),
        "fresh_composed_sources_match_contract": composed_hashes == contract_hashes,
        "three_arms_and_stage_schedules_exact": list(job.ARMS) == expected_arm_names
        and len(commands) == 5,
        "all_training_commands_preserve_recipe_and_target_only_com": commands_exact,
        "hosted_wall_ceiling_fixed": job.MAX_HOSTED_SECONDS == 14_400,
        **checkpoint["checks"],
        "all_actor_leaves_changed": checkpoint["changed_policy_leaf_count"]
        == checkpoint["policy_leaf_count"],
        **{f"step_zero_onnx_{name}": passed for name, passed in step_zero_onnx["checks"].items()},
        **{f"final_onnx_{name}": passed for name, passed in final_onnx["checks"].items()},
        **metrics["checks"],
        "tail_metric_finite_nonzero_at_zero_and_1024": (
            {entry["step"] for entry in tail_values} >= {0, 1024}
            and all(np.isfinite(entry["value"]) for entry in tail_values)
            and any(entry["value"] > 0.0 for entry in tail_values)
        ),
        "uniform_com_spread_proven_nonzero": (
            randomizer["uniform"]["min_m"] < -0.049
            and randomizer["uniform"]["max_m"] > 0.049
            and randomizer["checks"]["uniform_exactly_one_field_axis"]
        ),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_GROUND_UP_TORSO_COM_PACKAGE_AND_CPU_SMOKE"
        if not failed
        else "FAIL_GROUND_UP_TORSO_COM_PACKAGE_AND_CPU_SMOKE"
    )
    payload = {
        "schema_version": "ground_up_torso_com_package_cpu_smoke.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "asset_hashes": asset_hashes,
        "composed_hashes": composed_hashes,
        "checkpoint": checkpoint,
        "step_zero_onnx": step_zero_onnx,
        "final_onnx": final_onnx,
        "metrics": metrics,
        "tail_metric": {"tag": TAIL_TAG, "values": tail_values},
        "failed_preinit_invocation": {
            "updated_policy": False,
            "reason": "runner launched outside composed checkout; relative reference-motion asset was not found before environment construction",
        },
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "local_gpu": False,
            "colab": False,
            "rdk_or_robot": False,
        },
        "authority": {
            "launch_preregistered_hosted_search": not failed,
            "maximum_colab_compute_units": 8.0,
            "local_gpu": False,
            "condition_8_or_later": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Package and CPU Smoke",
        "",
        f"status: `{status}`",
        "",
        *(f"- {name}: `{passed}`" for name, passed in checks.items()),
        "",
        f"source-to-step-zero max error: `{checkpoint['max_source_to_step_zero_error']}`",
        f"changed actor leaves: `{checkpoint['changed_policy_leaf_count']}` / `{checkpoint['policy_leaf_count']}`",
        f"final conservative bound excess: `{final_onnx['max_bound_excess']}`",
        "",
        "Passing authorizes only the frozen sequential hosted search within its 8-compute-unit ceiling. It does not authorize local GPU, later robustness stages, RDK-X5, or robot access.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
