#!/usr/bin/env python3
"""Run the preregistered three-arm tracking-tail search on one Colab T4."""

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


DEFAULT_ASSETS = Path("/content")
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
SOURCE_ARCHIVE = "A2_APPLIED_TARGET_STATE_artifacts.tar.gz"
SOURCE_CHECKPOINT_RELATIVE = Path(
    "A2_APPLIED_TARGET_STATE/2026_07_14_173159_1003520"
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
    "reference_residual_ppo_networks.py": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
    "ground_up_projected_reference_feature_table.npz": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    SOURCE_ARCHIVE: "3b7457fe945a9d19d01616e77a28cd4f1175d8f81cf2f6eb12f30035ae52c9e7",
}
ARMS = (
    ("T1_QUARTER", -1643.0637410077638),
    ("T2_EQUAL", -6572.254964031055),
    ("T3_FOUR", -26289.01985612422),
)
EXPECTED_STEPS = [0, 501760, 1003520]
MAX_HOSTED_SECONDS = 14400
SCHEMA_VERSION = "ground_up_tracking_tail_colab_search.v1"
RESULT_PREFIX = "GROUND_UP_TRACKING_TAIL_RESULT="


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 1800,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print("TAIL_COMMAND=" + json.dumps(command), flush=True)
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        env=env,
    )


def validate_assets(assets: Path) -> dict[str, str]:
    actual_hashes = {}
    for name, expected in EXPECTED_HASHES.items():
        path = assets / name
        if not path.is_file():
            raise SystemExit(f"missing uploaded asset: {path}")
        actual = sha256(path)
        actual_hashes[name] = actual
        if actual != expected:
            raise SystemExit(f"hash mismatch for {name}: {actual} != {expected}")
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        expected_suffix = str(SOURCE_CHECKPOINT_RELATIVE / "_METADATA")
        if not any(member.name.endswith(expected_suffix) for member in archive):
            raise SystemExit(
                f"source checkpoint member missing from archive: {expected_suffix}"
            )
    return actual_hashes


def training_command(
    root: Path,
    assets: Path,
    output: Path,
    source_checkpoint: Path,
    scale: float,
) -> list[str]:
    return [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash",
        "--env", "joystick",
        "--output_dir", str(output),
        "--num_timesteps", "1000000",
        "--ppo_seed", "100",
        "--ppo_num_envs", "256",
        "--ppo_num_evals", "3",
        "--ppo_episode_length", "600",
        "--ppo_unroll_length", "20",
        "--ppo_batch_size", "256",
        "--ppo_num_minibatches", "4",
        "--ppo_num_updates_per_batch", "4",
        "--ppo_learning_rate", "0.0003",
        "--ppo_discounting", "0.97",
        "--ppo_entropy_cost", "0.005",
        "--policy_architecture", "reference_residual",
        "--imitation_scale", "1.0",
        "--reference_feature_table_path",
        str(assets / "ground_up_projected_reference_feature_table.npz"),
        "--nominal_reference_bootstrap",
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x", "0.074",
        "--ground_up_command_support_max_x", "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        "5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25",
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale", repr(scale),
        "--ground_up_tracking_tail_threshold_rad", "0.20",
        "--reference_start_phase", "0",
        "--ground_up_signed_progress_objective",
        "--critic_observation", "privileged_state",
        "--restore_checkpoint_path", str(source_checkpoint),
    ]


def write_manifest(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--validate-assets-only", action="store_true")
    args = parser.parse_args()
    assets = args.asset_root.resolve()
    actual_hashes = validate_assets(assets)
    if args.validate_assets_only:
        print(json.dumps({"status": "PASS_ASSET_VALIDATION", "hashes": actual_hashes}, sort_keys=True))
        return 0

    started = time.monotonic()
    root = assets / "ground_up_tracking_tail_playground"
    source_root = assets / "ground_up_tracking_tail_source"
    output_root = assets / "ground_up_tracking_tail_outputs"
    artifact = assets / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
    manifest = assets / "GROUND_UP_TRACKING_TAIL_manifest.json"
    shutil.rmtree(root, ignore_errors=True)
    shutil.rmtree(source_root, ignore_errors=True)
    shutil.rmtree(output_root, ignore_errors=True)
    artifact.unlink(missing_ok=True)
    manifest.unlink(missing_ok=True)

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
    run(
        [sys.executable, "-m", "py_compile",
         "playground/common/runner.py",
         "playground/common/reference_residual_ppo_networks.py",
         "playground/open_duck_mini_v2/joystick.py",
         "playground/open_duck_mini_v2/runner.py"],
        cwd=root,
    )

    source_root.mkdir(parents=True)
    with tarfile.open(assets / SOURCE_ARCHIVE, "r:gz") as archive:
        archive.extractall(source_root, filter="data")
    source_checkpoint = source_root / SOURCE_CHECKPOINT_RELATIVE
    if not source_checkpoint.is_dir():
        raise SystemExit(f"source checkpoint missing after extraction: {source_checkpoint}")

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run(
        [sys.executable, "-m", "pip", "install", "-q",
         "jax[cuda12]==0.8.2", "jaxlib==0.8.2", "mujoco==3.9.0",
         "playground==0.0.5", "onnxruntime>=1.20.1", "tensorflow==2.20.0",
         "onnx", "tensorboardX"],
        timeout=1200,
    )
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(root)])
    versions = run(
        [sys.executable, "-c",
         "import importlib.metadata as md; import jax,jaxlib,mujoco; "
         "print(jax.__version__,jaxlib.__version__,mujoco.__version__,md.version('playground')); "
         "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))"],
        capture=True,
    ).stdout
    print("TAIL_DEVICE_CONTRACT=" + versions, flush=True)
    if "HAS_GPU True" not in versions or "CudaDevice" not in versions:
        raise SystemExit("hosted search did not expose a JAX CUDA GPU")

    output_root.mkdir(parents=True)
    run_env = dict(os.environ)
    run_env["PYTHONPATH"] = str(root)
    arm_results = []
    for arm_name, scale in ARMS:
        elapsed = time.monotonic() - started
        remaining = MAX_HOSTED_SECONDS - elapsed
        if remaining <= 0:
            raise SystemExit("hosted wall-time ceiling reached before next arm")
        output = output_root / arm_name
        output.mkdir()
        command = training_command(root, assets, output, source_checkpoint, scale)
        arm_started = time.monotonic()
        try:
            completed = run(
                command,
                cwd=root,
                timeout=max(1, int(remaining)),
                capture=True,
                env=run_env,
            )
            log = completed.stdout
        except subprocess.CalledProcessError as error:
            log = error.stdout or ""
            (output / "training.log").write_text(log)
            raise
        (output / "training.log").write_text(log)
        checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
        onnx_files = sorted(output.glob("*.onnx"))
        checkpoint_steps = sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints)
        onnx_steps = sorted(int(path.stem.rsplit("_", 1)[1]) for path in onnx_files)
        if checkpoint_steps != EXPECTED_STEPS or onnx_steps != EXPECTED_STEPS:
            raise SystemExit(
                f"unexpected {arm_name} exports: checkpoints={checkpoint_steps}, onnx={onnx_steps}"
            )
        result = {
            "name": arm_name,
            "scale": scale,
            "command": command,
            "training_seconds": time.monotonic() - arm_started,
            "checkpoint_steps": checkpoint_steps,
            "onnx": [{"name": path.name, "sha256": sha256(path)} for path in onnx_files],
            "behavior_status": "UNEVALUATED",
        }
        arm_results.append(result)
        write_manifest(
            manifest,
            {
                "schema_version": SCHEMA_VERSION,
                "status": "RUNNING_TRAINING_ARTIFACT_CONTRACT_ONLY",
                "completed_arms": arm_results,
                "selection_uses_training_reward": False,
            },
        )

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "control_commit": CONTROL_COMMIT,
        "input_hashes": actual_hashes,
        "source_checkpoint": str(source_checkpoint),
        "arms": arm_results,
        "expected_steps": EXPECTED_STEPS,
        "execution": {
            "versions_and_devices": versions.splitlines(),
            "total_seconds": time.monotonic() - started,
            "maximum_hosted_seconds": MAX_HOSTED_SECONDS,
        },
        "selection_uses_training_reward": False,
        "behavior_status": "UNEVALUATED",
        "robot_access": False,
        "rdk_access": False,
        "local_gpu_access": False,
    }
    write_manifest(output_root / "job_metadata.json", metadata)
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(output_root, arcname=output_root.name)
    final_manifest = {
        **metadata,
        "artifact": str(artifact),
        "artifact_sha256": sha256(artifact),
        "artifact_bytes": artifact.stat().st_size,
    }
    write_manifest(manifest, final_manifest)
    print(
        RESULT_PREFIX
        + json.dumps(
            {
                "status": final_manifest["status"],
                "artifact": final_manifest["artifact"],
                "artifact_sha256": final_manifest["artifact_sha256"],
                "artifact_bytes": final_manifest["artifact_bytes"],
                "arms": [item["name"] for item in arm_results],
                "steps": EXPECTED_STEPS,
                "total_seconds": final_manifest["execution"]["total_seconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
