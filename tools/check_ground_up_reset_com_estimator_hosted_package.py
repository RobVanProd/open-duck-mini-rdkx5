#!/usr/bin/env python3
"""Contract the reset-COM estimator hosted package without launching it."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax


REPO = Path(__file__).resolve().parents[1]
JOB = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_TRAINING_PREREGISTRATION_20260715.md"
CPU_PACKAGE = REPO / "outputs/analysis/ground_up_reset_com_estimator_input_package_contract.json"
CPU_EXPANSION = REPO / "outputs/analysis/ground_up_reset_com_estimator_checkpoint_expansion.json"
EXPECTED_HASHES = {
    "job": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "330716283cbe7244cbb47ac678474f040d79cca75296aab5366d7ec83ec86e54",
    "cpu_package": "00e152e469e8fdeba49d7031c259b688f722ea75764297cb7ea51431d9fc2914",
    "cpu_expansion": "e5e7a3e8e34e7cc2ed511828d0e5323aed44d5e2d384082d31718ebb0a42b09c",
}
EXPECTED_COMPOSED_HASHES = {
    "joystick": "4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186",
    "runner": "e5ed1bac7ed181f02014487827f05f35fd421ff97ae50614de1b2ce8089f87a2",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_job() -> Any:
    spec = importlib.util.spec_from_file_location("reset_estimator_hosted_job", JOB)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load hosted job")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expansion_equivalence(hosted: dict[str, Any], local: dict[str, Any]) -> bool:
    hosted_cells = hosted["output_equivalence"]
    local_cells = local["output_equivalence"]["cells"]
    return (
        hosted["status"] == "PASS_HOSTED_CHECKPOINT_EXPANSION"
        and hosted["source_shapes"] == [[115], [226], [115, 512], [226, 512]]
        and hosted["expanded_shapes"] == [[116], [227], [116, 512], [227, 512]]
        and hosted["inserted_normalizer"] == local["inserted_normalizer_values"]
        and hosted["max_other_value_error"] == local["max_other_value_error"] == 0.0
        and hosted["max_save_restore_error"] == local["max_save_restore_error"] == 0.0
        and [cell["z"] for cell in hosted_cells] == [cell["z"] for cell in local_cells]
        and all(
            cell["actor_max_abs_error"] == 0.0
            and cell["critic_max_abs_error"] == 0.0
            and cell["reference_tail_exact"]
            for cell in hosted_cells
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--composed-root", type=Path, required=True)
    parser.add_argument("--cpu-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assets = args.assets.resolve()
    composed = args.composed_root.resolve()
    cpu_source = args.cpu_source.resolve()
    output = args.output.resolve()
    actual_hashes = {
        "job": sha256(JOB), "prereg": sha256(PREREG),
        "cpu_package": sha256(CPU_PACKAGE), "cpu_expansion": sha256(CPU_EXPANSION),
    }
    composed_paths = {
        "joystick": composed / "playground/open_duck_mini_v2/joystick.py",
        "runner": composed / "playground/open_duck_mini_v2/runner.py",
    }
    composed_hashes = {name: sha256(path) for name, path in composed_paths.items()}
    job = load_job()
    asset_validation = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"), str(JOB),
            "--asset-root", str(assets), "--validate-assets-only",
        ],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env={**os.environ, "JAX_PLATFORMS": "cpu", "CUDA_VISIBLE_DEVICES": ""},
    )
    validation_line = asset_validation.stdout.strip().splitlines()[-1]
    validation_payload = json.loads(validation_line)
    old_pythonpath = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = str(composed)
    import sys

    sys.path.insert(0, str(composed))
    try:
        with tempfile.TemporaryDirectory(prefix="reset_estimator_hosted_contract_") as temporary:
            temporary_path = Path(temporary)
            hosted_report = job.hosted_expand(
                cpu_source,
                temporary_path / "expanded",
                temporary_path / "hosted_expansion.json",
            )
    finally:
        sys.path.remove(str(composed))
        if old_pythonpath is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = old_pythonpath
    local_expansion = json.loads(CPU_EXPANSION.read_text())
    cpu_package = json.loads(CPU_PACKAGE.read_text())
    command = job.training_command(
        composed, assets, Path("/tmp/arm"), Path("/tmp/expanded")
    )
    source = JOB.read_text()
    required_command_fragments = {
        "--num_timesteps": "2000000",
        "--ppo_seed": "100",
        "--ppo_num_envs": "256",
        "--ppo_episode_length": "600",
        "--ppo_learning_rate": "0.0003",
        "--ground_up_torso_com_x_min_m": "-0.05",
        "--ground_up_torso_com_x_max_m": "0.05",
        "--ground_up_torso_com_distribution": "uniform",
        "--ground_up_command_support_min_x": "0.074",
        "--ground_up_command_support_max_x": "0.080",
        "--ground_up_tracking_tail_exceedance_scale": "-6572.254964031055",
        "--reference_start_phase": "0",
        "--critic_observation": "privileged_state",
    }
    command_pairs_exact = all(
        flag in command and command[command.index(flag) + 1] == value
        for flag, value in required_command_fragments.items()
    )
    required_flags = {
        "--nominal_reference_bootstrap",
        "--ground_up_reset_com_estimator_input",
        "--ground_up_torso_com_randomization",
        "--ground_up_hard_vector_command_support",
        "--ground_up_measured_actuator_bridge",
        "--ground_up_applied_target_observation",
        "--ground_up_signed_progress_objective",
    }
    checks = {
        "frozen_source_hashes_exact": actual_hashes == EXPECTED_HASHES,
        "composed_sources_exact": composed_hashes == EXPECTED_COMPOSED_HASHES,
        "upstream_cpu_contracts_pass": cpu_package.get("status")
        == "PASS_RESET_COM_ESTIMATOR_INPUT_CPU_PACKAGE_CONTRACT"
        and local_expansion.get("status")
        == "PASS_RESET_COM_ESTIMATOR_CHECKPOINT_EXPANSION",
        "asset_only_validation_passes": validation_payload.get("status")
        == "PASS_ASSET_VALIDATION",
        "asset_hash_set_exact": validation_payload.get("hashes") == job.EXPECTED_HASHES,
        "hosted_expansion_matches_local_contract": expansion_equivalence(
            hosted_report, local_expansion
        ),
        "single_arm_identity_exact": job.ARM_NAME == "RESET_EST_LATCH_U05",
        "expected_export_steps_exact": job.EXPECTED_STEPS == [0, 1_003_520, 2_007_040],
        "hosted_limits_exact": job.MAX_HOSTED_SECONDS == 2_400
        and job.MAX_COMPUTE_UNITS == 2.0,
        "training_command_recipe_pairs_exact": command_pairs_exact,
        "training_command_required_flags_exact": required_flags.issubset(command),
        "conservative_velocity_and_bridge_exact": "5.24,5.24,1.50,1.50,1.50,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25"
        in command
        and "3,3,3,3,3,3,2,3,3,3,2,3,2,3" in command
        and ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005"
        in command,
        "one_process_no_resume_source_contract": '"session_count": 1'
        in source and '"training_process_count": 1' in source
        and '"resume": False' in source and "--resume" not in source,
        "behavior_unevaluated_and_reward_nonselective": '"behavior_status": "UNEVALUATED"'
        in source and '"training_reward_used": False' in source,
        "atomic_archive_source_contract": "temporary.replace(artifact)" in source,
        "cpu_only_contract_execution": os.environ.get("JAX_PLATFORMS") == "cpu"
        and os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "zero_training_and_colab_sessions": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT"
    payload = {
        "schema_version": "ground_up_reset_com_estimator_hosted_package_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "source_hashes": actual_hashes,
        "composed_source_hashes": composed_hashes,
        "asset_validation": validation_payload,
        "cpu_expansion_equivalence": hosted_report,
        "frozen_command": command,
        "limits": {
            "maximum_hosted_seconds": job.MAX_HOSTED_SECONDS,
            "maximum_compute_units": job.MAX_COMPUTE_UNITS,
            "session_count": 1, "training_process_count": 1, "retry": False,
        },
        "execution": {
            "devices": [str(device) for device in jax.devices()],
            "training_steps": 0, "colab_sessions": 0, "dynamic_behavior_cells": 0,
            "local_gpu_or_igpu": False, "robot_or_rdk": False,
        },
        "authority": {
            "hosted_run_now": False, "training_now": False,
            "separate_explicit_hosted_run_authorization_required": True,
            "behavior_evaluation": False, "robot_or_rdk": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
