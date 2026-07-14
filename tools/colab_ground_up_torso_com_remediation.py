#!/usr/bin/env python3
"""Run the preregistered three-arm torso-COM remediation search on Colab."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time


CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
SOURCE_ARCHIVE = "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
SOURCE_CHECKPOINT_RELATIVE = Path(
    "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000"
)
PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
    "ground_up_stage1_mechanism_stack.patch",
    "ground_up_nominal_reference_bootstrap.patch",
    "ground_up_signed_progress_objective.patch",
    "ground_up_reference_residual_actor.patch",
    "ground_up_hard_vector_command_support.patch",
    "ground_up_measured_actuator_bridge.patch",
    "ground_up_applied_target_observation.patch",
    "ground_up_tracking_tail_exceedance.patch",
    "ground_up_torso_com_randomization.patch",
)
EXPECTED_HASHES = {
    "ground_up_search_runner.patch": "6a176589b766de65ac2746c66f3387bfca5384d6ce4adf3703c752d8103a5e55",
    "ground_up_reference_conditioned.patch": "4138ecddb9ffc0df468a2780522c1732bc4b0e1a0865d181da1112d1c16902fb",
    "ground_up_recipe_search.patch": "3f5d892f5ce531207de6c86b18c9f5dbea83bc131a3fc2e5085851c2e4e3e5f8",
    "ground_up_stage1_mechanism_stack.patch": "cf5155dfd54a4699865b9823e8bf090f9f54b0e53df5583eb448e315d60053dc",
    "ground_up_nominal_reference_bootstrap.patch": "0d89b85815eb570115ec5f35d677aba68299f977b3e36c60b10dfa869533ebba",
    "ground_up_signed_progress_objective.patch": "13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b",
    "ground_up_reference_residual_actor.patch": "57bcf2394fa47745e9c26c6933e58a06c3799aba35e7000762befc5fac2f7d3b",
    "ground_up_hard_vector_command_support.patch": "900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875",
    "ground_up_measured_actuator_bridge.patch": "133531963abea46cd0394526a2fa88b018fc21ca68c365863304e3e96d6ca0df",
    "ground_up_applied_target_observation.patch": "bdcac27115fcbe855079f5365ac046e863a9b302ff16f560d12a26cd492f2821",
    "ground_up_tracking_tail_exceedance.patch": "9f716243e0c4ef487ef4227ef0cb9f389ed43c0456435987ac0846e1b629811e",
    "ground_up_torso_com_randomization.patch": "524ff95a3d7018925e1ab958dfe067067e09f0cd718176c7cc46bb6b078d8e3a",
    "reference_residual_ppo_networks.py": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
    "ground_up_projected_reference_feature_table.npz": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    SOURCE_ARCHIVE: "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
}
ARMS = {
    "U05_DIRECT": (
        {"distribution": "uniform", "min_x_m": -0.05, "max_x_m": 0.05,
         "timesteps": 2_000_000, "evals": 3, "expected_steps": [0, 1_024_000, 2_048_000]},
    ),
    "A05_DIRECT": (
        {"distribution": "anchors", "min_x_m": -0.05, "max_x_m": 0.05,
         "timesteps": 2_000_000, "evals": 3, "expected_steps": [0, 1_024_000, 2_048_000]},
    ),
    "U_CURRICULUM": (
        {"distribution": "uniform", "min_x_m": -0.01, "max_x_m": 0.01,
         "timesteps": 500_000, "evals": 2, "expected_steps": [0, 512_000]},
        {"distribution": "uniform", "min_x_m": -0.03, "max_x_m": 0.03,
         "timesteps": 500_000, "evals": 2, "expected_steps": [0, 512_000]},
        {"distribution": "uniform", "min_x_m": -0.05, "max_x_m": 0.05,
         "timesteps": 1_000_000, "evals": 3, "expected_steps": [0, 512_000, 1_024_000]},
    ),
}
MAX_HOSTED_SECONDS = 14_400
SCHEMA_VERSION = "ground_up_torso_com_remediation_colab.v1"
RESULT_PREFIX = "GROUND_UP_TORSO_COM_REMEDIATION_RESULT="


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 1800,
        capture: bool = False, env: dict[str, str] | None = None):
    print("COM_COMMAND=" + json.dumps(command), flush=True)
    return subprocess.run(
        command, cwd=cwd, check=True, timeout=timeout, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None, env=env,
    )


def validate_assets(assets: Path) -> dict[str, str]:
    actual = {}
    for name, expected in EXPECTED_HASHES.items():
        path = assets / name
        if not path.is_file():
            raise SystemExit(f"missing uploaded asset: {path}")
        actual[name] = sha256(path)
        if actual[name] != expected:
            raise SystemExit(f"hash mismatch for {name}: {actual[name]} != {expected}")
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        suffix = str(SOURCE_CHECKPOINT_RELATIVE / "_METADATA")
        if not any(member.name == suffix for member in archive):
            raise SystemExit(f"source checkpoint member missing: {suffix}")
    return actual


def training_command(
    assets: Path,
    output: Path,
    restore: Path,
    stage: dict,
) -> list[str]:
    return [
        sys.executable, "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash", "--env", "joystick",
        "--output_dir", str(output),
        "--num_timesteps", str(stage["timesteps"]),
        "--ppo_seed", "100", "--ppo_num_envs", "256",
        "--ppo_num_evals", str(stage["evals"]),
        "--ppo_episode_length", "600", "--ppo_unroll_length", "20",
        "--ppo_batch_size", "256", "--ppo_num_minibatches", "4",
        "--ppo_num_updates_per_batch", "4", "--ppo_learning_rate", "0.0003",
        "--ppo_discounting", "0.97", "--ppo_entropy_cost", "0.005",
        "--policy_architecture", "reference_residual", "--imitation_scale", "1.0",
        "--reference_feature_table_path",
        str(assets / "ground_up_projected_reference_feature_table.npz"),
        "--nominal_reference_bootstrap",
        "--ground_up_torso_com_randomization",
        "--ground_up_torso_com_x_min_m", str(stage["min_x_m"]),
        "--ground_up_torso_com_x_max_m", str(stage["max_x_m"]),
        "--ground_up_torso_com_distribution", stage["distribution"],
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x", "0.074",
        "--ground_up_command_support_max_x", "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        "5.24,5.24,1.50,1.50,1.50,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25",
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale", "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad", "0.20",
        "--reference_start_phase", "0", "--ground_up_signed_progress_objective",
        "--critic_observation", "privileged_state",
        "--restore_checkpoint_path", str(restore),
    ]


def inspect_exports(output: Path, expected_steps: list[int]) -> dict:
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    onnx = sorted(output.glob("*.onnx"))
    checkpoint_steps = sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints)
    onnx_steps = sorted(int(path.stem.rsplit("_", 1)[1]) for path in onnx)
    if checkpoint_steps != expected_steps or onnx_steps != expected_steps:
        raise SystemExit(
            f"unexpected exports in {output}: checkpoints={checkpoint_steps}, onnx={onnx_steps}"
        )
    return {
        "checkpoint_steps": checkpoint_steps,
        "checkpoints": [{"name": path.name} for path in checkpoints],
        "onnx": [{"name": path.name, "sha256": sha256(path)} for path in onnx],
        "final_checkpoint": str(max(checkpoints, key=lambda p: int(p.name.rsplit("_", 1)[1]))),
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=Path("/content"))
    parser.add_argument("--validate-assets-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    assets = args.asset_root.resolve()
    hashes = validate_assets(assets)
    if args.validate_assets_only:
        print(json.dumps({"status": "PASS_ASSET_VALIDATION", "hashes": hashes}, sort_keys=True))
        return 0

    started = time.monotonic()
    root = assets / "ground_up_torso_com_playground"
    source_root = assets / "ground_up_torso_com_source"
    output_root = assets / "ground_up_torso_com_outputs"
    artifact = assets / "GROUND_UP_TORSO_COM_REMEDIATION_artifacts.tar.gz"
    manifest = assets / "GROUND_UP_TORSO_COM_REMEDIATION_manifest.json"
    shutil.rmtree(root, ignore_errors=True)
    shutil.rmtree(source_root, ignore_errors=True)
    if not args.resume:
        shutil.rmtree(output_root, ignore_errors=True)
    artifact.unlink(missing_ok=True)

    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(root)])
    run(["git", "checkout", "-q", CONTROL_COMMIT], cwd=root)
    for name in PATCHES:
        run(["git", "apply", "--check", str(assets / name)], cwd=root)
        run(["git", "apply", str(assets / name)], cwd=root)
    shutil.copy2(
        assets / "reference_residual_ppo_networks.py",
        root / "playground/common/reference_residual_ppo_networks.py",
    )
    run(["git", "diff", "--check"], cwd=root)
    run([
        sys.executable, "-m", "py_compile",
        "playground/common/randomize.py", "playground/common/runner.py",
        "playground/common/reference_residual_ppo_networks.py",
        "playground/open_duck_mini_v2/joystick.py",
        "playground/open_duck_mini_v2/runner.py",
    ], cwd=root)

    source_root.mkdir(parents=True)
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        members = [
            member for member in archive
            if member.name == str(SOURCE_CHECKPOINT_RELATIVE)
            or member.name.startswith(str(SOURCE_CHECKPOINT_RELATIVE) + "/")
        ]
        archive.extractall(source_root, members=members, filter="data")
    source_checkpoint = source_root / SOURCE_CHECKPOINT_RELATIVE
    if not source_checkpoint.is_dir():
        raise SystemExit(f"source checkpoint missing after extraction: {source_checkpoint}")

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run([
        sys.executable, "-m", "pip", "install", "-q",
        "jax[cuda12]==0.8.2", "jaxlib==0.8.2", "mujoco==3.9.0",
        "playground==0.0.5", "onnxruntime>=1.20.1", "tensorflow==2.20.0",
        "onnx", "tensorboardX",
    ], timeout=1200)
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(root)])
    devices = run([
        sys.executable, "-c",
        "import jax,jaxlib,mujoco; print(jax.__version__,jaxlib.__version__,mujoco.__version__); "
        "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))",
    ], capture=True).stdout
    if "HAS_GPU True" not in devices or "CudaDevice" not in devices:
        raise SystemExit("hosted search did not expose a JAX CUDA GPU")

    output_root.mkdir(parents=True, exist_ok=True)
    run_env = dict(os.environ)
    run_env["PYTHONPATH"] = str(root)
    results = []
    for arm_name, stages in ARMS.items():
        restore = source_checkpoint
        stage_results = []
        for stage_index, stage in enumerate(stages, start=1):
            if time.monotonic() - started >= MAX_HOSTED_SECONDS:
                raise SystemExit("hosted wall-time ceiling reached")
            output = output_root / arm_name / f"stage{stage_index}"
            command = training_command(assets, output, restore, stage)
            if args.resume and output.is_dir():
                export = inspect_exports(output, stage["expected_steps"])
                stage_results.append({"stage": stage_index, **stage, "command": command, **export, "resumed": True})
                restore = Path(export["final_checkpoint"])
                continue
            output.mkdir(parents=True)
            stage_started = time.monotonic()
            completed = run(
                command, cwd=root,
                timeout=max(1, int(MAX_HOSTED_SECONDS - (time.monotonic() - started))),
                capture=True, env=run_env,
            )
            (output / "training.log").write_text(completed.stdout)
            export = inspect_exports(output, stage["expected_steps"])
            stage_results.append({
                "stage": stage_index, **stage, "command": command, **export,
                "training_seconds": time.monotonic() - stage_started,
            })
            restore = Path(export["final_checkpoint"])
            write_json(manifest, {
                "schema_version": SCHEMA_VERSION,
                "status": "RUNNING_TRAINING_ARTIFACT_CONTRACT_ONLY",
                "completed_arms": results,
                "current_arm": {"name": arm_name, "stages": stage_results},
            })
        results.append({"name": arm_name, "stages": stage_results, "behavior_status": "UNEVALUATED"})

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "control_commit": CONTROL_COMMIT,
        "input_hashes": hashes,
        "source_checkpoint": str(source_checkpoint),
        "arms": results,
        "execution": {
            "versions_and_devices": devices.splitlines(),
            "total_seconds": time.monotonic() - started,
            "maximum_hosted_seconds": MAX_HOSTED_SECONDS,
        },
        "selection_uses_training_reward": False,
        "behavior_status": "UNEVALUATED",
        "local_gpu_access": False,
        "rdk_access": False,
        "robot_access": False,
    }
    write_json(output_root / "job_metadata.json", metadata)
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(output_root, arcname=output_root.name)
    final = {
        **metadata,
        "artifact": str(artifact),
        "artifact_sha256": sha256(artifact),
        "artifact_bytes": artifact.stat().st_size,
    }
    write_json(manifest, final)
    print(RESULT_PREFIX + json.dumps({
        "status": final["status"], "artifact": final["artifact"],
        "artifact_sha256": final["artifact_sha256"],
        "artifact_bytes": final["artifact_bytes"],
        "arms": list(ARMS), "total_seconds": final["execution"]["total_seconds"],
    }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
