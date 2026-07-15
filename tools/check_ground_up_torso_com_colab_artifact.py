#!/usr/bin/env python3
"""Validate the recovered torso-COM Colab artifact without behavior selection."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import tarfile
import tempfile

import jax

from check_ground_up_torso_com_package_smoke import inspect_onnx
from check_ground_up_hard_vector_continuation_smoke import sha256_file


def load_job(path: Path):
    spec = importlib.util.spec_from_file_location("torso_com_job", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def value_after(command: list[str], flag: str) -> str:
    return command[command.index(flag) + 1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    job = load_job(args.job.resolve())
    manifest = json.loads(args.manifest.read_text())
    archive_hash = sha256_file(args.archive)
    archive_bytes = args.archive.stat().st_size

    with tempfile.TemporaryDirectory(prefix="torso_com_artifact_") as temporary:
        extracted = Path(temporary)
        with tarfile.open(args.archive, "r:gz") as bundle:
            members = bundle.getmembers()
            safe_members = all(
                not Path(member.name).is_absolute()
                and ".." not in Path(member.name).parts
                for member in members
            )
            bundle.extractall(extracted, filter="data")
        root = extracted / "ground_up_torso_com_outputs"

        observed_arms: dict[str, list[list[int]]] = {}
        onnx_evidence = []
        command_checks = []
        continuity_checks = []
        training_logs_nonempty = True
        event_files_present = True
        prior_curriculum_final = None

        for arm in manifest["arms"]:
            arm_name = arm["name"]
            observed_arms[arm_name] = []
            for stage in arm["stages"]:
                stage_index = stage["stage"]
                stage_dir = root / arm_name / f"stage{stage_index}"
                observed_arms[arm_name].append(stage["checkpoint_steps"])
                expected = job.ARMS[arm_name][stage_index - 1]
                command = stage["command"]
                command_checks.append(
                    stage["expected_steps"] == expected["expected_steps"]
                    and stage["checkpoint_steps"] == expected["expected_steps"]
                    and stage["timesteps"] == expected["timesteps"]
                    and stage["distribution"] == expected["distribution"]
                    and stage["min_x_m"] == expected["min_x_m"]
                    and stage["max_x_m"] == expected["max_x_m"]
                    and value_after(command, "--num_timesteps") == str(expected["timesteps"])
                    and value_after(command, "--ppo_seed") == "100"
                    and value_after(command, "--ground_up_torso_com_distribution")
                    == expected["distribution"]
                    and float(value_after(command, "--ground_up_torso_com_x_min_m"))
                    == expected["min_x_m"]
                    and float(value_after(command, "--ground_up_torso_com_x_max_m"))
                    == expected["max_x_m"]
                    and "--nominal_reference_bootstrap" in command
                    and "--ground_up_measured_actuator_bridge" in command
                    and "--ground_up_applied_target_observation" in command
                    and value_after(command, "--ground_up_action_velocity_limits_rad_s").split(",")[4]
                    == "1.50"
                )
                restore = value_after(command, "--restore_checkpoint_path")
                if arm_name != "U_CURRICULUM" or stage_index == 1:
                    continuity_checks.append(
                        restore.endswith(str(job.SOURCE_CHECKPOINT_RELATIVE))
                    )
                else:
                    continuity_checks.append(restore == prior_curriculum_final)
                prior_curriculum_final = (
                    stage["final_checkpoint"]
                    if arm_name == "U_CURRICULUM"
                    else prior_curriculum_final
                )

                training_logs_nonempty &= (
                    (stage_dir / "training.log").is_file()
                    and (stage_dir / "training.log").stat().st_size > 0
                )
                event_files_present &= len(list(stage_dir.glob("events.out.tfevents.*"))) == 1
                checkpoint_names = [entry["name"] for entry in stage["checkpoints"]]
                checkpoint_steps = sorted(int(name.rsplit("_", 1)[1]) for name in checkpoint_names)
                command_checks.append(checkpoint_steps == expected["expected_steps"])
                for entry in stage["onnx"]:
                    path = stage_dir / entry["name"]
                    evidence = inspect_onnx(path)
                    evidence["manifest_sha256"] = entry["sha256"]
                    evidence["hash_matches_manifest"] = evidence["sha256"] == entry["sha256"]
                    onnx_evidence.append(evidence)

    expected_observed = {
        name: [stage["expected_steps"] for stage in stages]
        for name, stages in job.ARMS.items()
    }
    checks = {
        "cpu_only_local_validation": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
        and os.environ.get("CUDA_VISIBLE_DEVICES") == "",
        "manifest_training_artifact_status_pass": manifest["status"]
        == "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "archive_sha256_exact": archive_hash == manifest["artifact_sha256"],
        "archive_bytes_exact": archive_bytes == manifest["artifact_bytes"],
        "archive_members_safe": safe_members,
        "control_commit_exact": manifest["control_commit"] == job.CONTROL_COMMIT,
        "all_input_hashes_exact": manifest["input_hashes"] == job.EXPECTED_HASHES,
        "hosted_device_contract_exact": manifest["execution"]["versions_and_devices"]
        == ["0.8.2 0.8.2 3.9.0", "[CudaDevice(id=0)]", "HAS_GPU True"],
        "hosted_wall_ceiling_respected": manifest["execution"]["total_seconds"]
        <= manifest["execution"]["maximum_hosted_seconds"]
        == job.MAX_HOSTED_SECONDS,
        "all_arm_stage_exports_exact": observed_arms == expected_observed,
        "all_commands_preserve_frozen_recipe": all(command_checks),
        "curriculum_restore_continuity_exact": all(continuity_checks),
        "all_training_logs_nonempty": training_logs_nonempty,
        "one_event_file_per_stage": event_files_present,
        "all_onnx_hashes_match_manifest": all(
            item["hash_matches_manifest"] for item in onnx_evidence
        ),
        "all_onnx_interfaces_and_bounds_pass": all(
            all(item["checks"].values()) for item in onnx_evidence
        ),
        "behavior_remains_unevaluated": manifest["behavior_status"] == "UNEVALUATED"
        and all(arm["behavior_status"] == "UNEVALUATED" for arm in manifest["arms"]),
        "training_reward_not_used_for_selection": manifest["selection_uses_training_reward"]
        is False,
        "no_local_gpu_rdk_or_robot": manifest["local_gpu_access"] is False
        and manifest["rdk_access"] is False
        and manifest["robot_access"] is False,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_TORSO_COM_COLAB_ARTIFACT_CONTRACT"
        if not failed
        else "FAIL_TORSO_COM_COLAB_ARTIFACT_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_colab_artifact_check.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "archive": {
            "path": str(args.archive.resolve()),
            "sha256": archive_hash,
            "bytes": archive_bytes,
        },
        "hosted_total_seconds": manifest["execution"]["total_seconds"],
        "arms": observed_arms,
        "onnx": onnx_evidence,
        "authority": {
            "run_preregistered_local_cpu_behavior_evaluation": not failed,
            "training_artifact_is_policy_winner": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Torso-COM Colab Artifact Contract",
        "",
        f"status: `{status}`",
        "",
        *(f"- {name}: `{passed}`" for name, passed in checks.items()),
        "",
        f"archive SHA-256: `{archive_hash}`",
        f"archive bytes: `{archive_bytes}`",
        f"hosted seconds: `{manifest['execution']['total_seconds']}`",
        f"validated ONNX exports: `{len(onnx_evidence)}`",
        "",
        "Passing authorizes only the preregistered local CPU behavior evaluation. It does not make any arm a winner or authorize local GPU, RDK-X5, or robot access.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
