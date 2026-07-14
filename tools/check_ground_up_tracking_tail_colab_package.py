#!/usr/bin/env python3
"""Verify the fixed tracking-tail Colab package against its preregistration."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("tracking_tail_colab_job", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def option(command: list[str], name: str) -> str:
    index = command.index(name)
    return command[index + 1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-script", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--cpu-smoke", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    job = load_module(args.job_script.resolve())
    prereg = json.loads(args.preregistration.read_text())
    smoke = json.loads(args.cpu_smoke.read_text())
    hashes = job.validate_assets(args.asset_root.resolve())
    expected_arms = [(item["name"], item["scale"]) for item in prereg["arms"]]
    source = Path("/content/ground_up_tracking_tail_source") / job.SOURCE_CHECKPOINT_RELATIVE
    commands = [
        job.training_command(
            Path("/content/ground_up_tracking_tail_playground"),
            Path("/content"),
            Path("/content/ground_up_tracking_tail_outputs") / name,
            source,
            scale,
        )
        for name, scale in job.ARMS
    ]
    per_command = []
    for (name, scale), command in zip(job.ARMS, commands, strict=True):
        per_command.append(
            {
                "name": name,
                "scale": scale,
                "command": command,
                "checks": {
                    "one_million_requested_steps": option(command, "--num_timesteps")
                    == str(prereg["additional_steps_per_arm"]),
                    "three_evaluations": option(command, "--ppo_num_evals")
                    == str(prereg["num_evals"]),
                    "full_training_horizon": option(command, "--ppo_episode_length")
                    == str(prereg["full_horizon_ticks"]),
                    "independent_protected_restore": option(
                        command, "--restore_checkpoint_path"
                    )
                    == str(source),
                    "scale_exact": option(
                        command, "--ground_up_tracking_tail_exceedance_scale"
                    )
                    == repr(scale),
                    "threshold_exact": float(
                        option(command, "--ground_up_tracking_tail_threshold_rad")
                    )
                    == prereg["tail_contract"]["threshold_rad"],
                    "applied_target_enabled": "--ground_up_applied_target_observation"
                    in command,
                    "measured_bridge_enabled": "--ground_up_measured_actuator_bridge"
                    in command,
                    "hard_vector_enabled": "--ground_up_hard_vector_command_support"
                    in command,
                },
            }
        )
    checks = {
        "cpu_smoke_passed": smoke["status"]
        == "PASS_CPU_TRACKING_TAIL_CONTINUATION_SMOKE",
        "arms_match_preregistration_exactly": list(job.ARMS) == expected_arms,
        "half_and_final_steps_fixed": job.EXPECTED_STEPS == [0, 512000, 1024000],
        "one_session_wall_ceiling_under_compute_ceiling_at_reported_rate": (
            job.MAX_HOSTED_SECONDS / 3600 * 1.07
            <= prereg["hosted_compute_unit_ceiling"]
        ),
        "training_reward_not_in_selection": prereg["selection_uses_training_reward"]
        is False,
        "source_archive_hash_exact": hashes[job.SOURCE_ARCHIVE]
        == job.EXPECTED_HASHES[job.SOURCE_ARCHIVE],
        "tail_patch_hash_exact": hashes["ground_up_tracking_tail_exceedance.patch"]
        == prereg["tail_contract"]["patch_sha256"],
        "all_commands_match_contract": all(
            all(item["checks"].values()) for item in per_command
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_COLAB_PACKAGE_CONTRACT" if not failed else "FAIL_COLAB_PACKAGE_CONTRACT"
    payload = {
        "schema_version": "ground_up_tracking_tail_colab_package_check.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "job_script": str(args.job_script.resolve()),
        "input_hashes": hashes,
        "reported_compute_units_per_hour": 1.07,
        "maximum_hosted_seconds": job.MAX_HOSTED_SECONDS,
        "maximum_compute_units_at_reported_rate": job.MAX_HOSTED_SECONDS / 3600 * 1.07,
        "arms": per_command,
        "authority": {
            "hosted_training": not failed,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(
        "\n".join(
            [
                "# Ground-Up Tracking-Tail Colab Package Check",
                "",
                f"status: `{status}`",
                "",
                f"failed checks: `{', '.join(failed) if failed else 'none'}`",
                f"arms: `{expected_arms}`",
                f"expected exports per arm: `{job.EXPECTED_STEPS}`",
                f"maximum hosted wall time: `{job.MAX_HOSTED_SECONDS}` seconds",
                f"maximum compute at reported 1.07 CU/hour: `{payload['maximum_compute_units_at_reported_rate']}` CU",
                "",
                "Every arm independently restores the same protected 1M checkpoint. "
                "This check authorizes the fixed hosted package only; behavior remains "
                "unevaluated and no robot, RDK-X5, deployment, or local GPU access follows.",
                "",
            ]
        )
    )
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
