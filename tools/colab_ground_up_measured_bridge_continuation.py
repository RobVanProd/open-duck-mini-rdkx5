#!/usr/bin/env python3
"""Run the one preregistered measured-bridge-only continuation on Colab T4."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time


ASSETS = Path("/content")
ROOT = ASSETS / "ground_up_measured_bridge_playground"
SOURCE_ROOT = ASSETS / "ground_up_measured_bridge_source"
OUTPUT = ASSETS / "ground_up_measured_bridge_outputs" / "A1_MEASURED_BRIDGE_ONLY"
ARTIFACT = ASSETS / "A1_MEASURED_BRIDGE_ONLY_artifacts.tar.gz"
MANIFEST = ASSETS / "A1_MEASURED_BRIDGE_ONLY_manifest.json"
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
SOURCE_CHECKPOINT = (
    SOURCE_ROOT
    / "A1_HARD_VECTOR_COMMAND_SUPPORT"
    / "2026_07_14_155545_1003520"
)
SOURCE_ARCHIVE = "A1_HARD_VECTOR_COMMAND_SUPPORT_artifacts.tar.gz"
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
    "reference_residual_ppo_networks.py": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
    "ground_up_projected_reference_feature_table.npz": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "A1_HARD_VECTOR_COMMAND_SUPPORT_artifacts.tar.gz": "cfc895aca4ddf4ffb0eabf0ca338cd7dd03b19cc7d32125c53ad7ce36bb9ab83",
}
EXTRA_TRAINING_ARGS: tuple[str, ...] = ()
SCHEMA_VERSION = "ground_up_measured_bridge_only_colab.v1"
RESULT_PREFIX = "GROUND_UP_MEASURED_BRIDGE_RESULT="


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
    print("BRIDGE_COMMAND=" + json.dumps(command), flush=True)
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


def main() -> int:
    started = time.monotonic()
    actual_hashes = {}
    for name, expected in EXPECTED_HASHES.items():
        path = ASSETS / name
        if not path.is_file():
            raise SystemExit(f"missing uploaded asset: {path}")
        actual = sha256(path)
        actual_hashes[name] = actual
        if actual != expected:
            raise SystemExit(f"hash mismatch for {name}: {actual} != {expected}")

    shutil.rmtree(ROOT, ignore_errors=True)
    shutil.rmtree(SOURCE_ROOT, ignore_errors=True)
    shutil.rmtree(OUTPUT.parent, ignore_errors=True)
    ARTIFACT.unlink(missing_ok=True)
    MANIFEST.unlink(missing_ok=True)
    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(ROOT)])
    run(["git", "checkout", "-q", CONTROL_COMMIT], cwd=ROOT)
    for name in PATCHES:
        run(["git", "apply", "--check", str(ASSETS / name)], cwd=ROOT)
        run(["git", "apply", str(ASSETS / name)], cwd=ROOT)
    shutil.copy2(
        ASSETS / "reference_residual_ppo_networks.py",
        ROOT / "playground" / "common" / "reference_residual_ppo_networks.py",
    )
    run(["git", "diff", "--check"], cwd=ROOT)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "playground/common/runner.py",
            "playground/common/reference_residual_ppo_networks.py",
            "playground/open_duck_mini_v2/joystick.py",
            "playground/open_duck_mini_v2/runner.py",
        ],
        cwd=ROOT,
    )

    SOURCE_ROOT.mkdir(parents=True)
    with tarfile.open(
        ASSETS / SOURCE_ARCHIVE, "r:gz"
    ) as archive:
        archive.extractall(SOURCE_ROOT, filter="data")
    if not SOURCE_CHECKPOINT.is_dir():
        raise SystemExit(f"source checkpoint missing after extraction: {SOURCE_CHECKPOINT}")

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "jax[cuda12]==0.8.2",
            "jaxlib==0.8.2",
            "mujoco==3.9.0",
            "playground==0.0.5",
            "onnxruntime>=1.20.1",
            "tensorflow==2.20.0",
            "onnx",
            "tensorboardX",
        ],
        timeout=1200,
    )
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(ROOT)])
    versions = run(
        [
            sys.executable,
            "-c",
            "import importlib.metadata as md; import jax,jaxlib,mujoco; "
            "print(jax.__version__,jaxlib.__version__,mujoco.__version__,md.version('playground')); "
            "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))",
        ],
        capture=True,
    ).stdout
    print("BRIDGE_DEVICE_CONTRACT=" + versions, flush=True)
    if "HAS_GPU True" not in versions or "CudaDevice" not in versions:
        raise SystemExit("hosted continuation did not expose a JAX CUDA GPU")

    OUTPUT.mkdir(parents=True)
    command = [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash",
        "--env", "joystick",
        "--output_dir", str(OUTPUT),
        "--num_timesteps", "2000000",
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
        "--reference_feature_table_path", str(ASSETS / "ground_up_projected_reference_feature_table.npz"),
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
        "--reference_start_phase", "0",
        "--ground_up_signed_progress_objective",
        "--critic_observation", "privileged_state",
        "--restore_checkpoint_path", str(SOURCE_CHECKPOINT),
        *EXTRA_TRAINING_ARGS,
    ]
    run_env = dict(os.environ)
    run_env["PYTHONPATH"] = str(ROOT)
    training_started = time.monotonic()
    try:
        training = run(command, cwd=ROOT, timeout=7200, capture=True, env=run_env)
        training_log = training.stdout
    except subprocess.CalledProcessError as error:
        training_log = error.stdout or ""
        (OUTPUT / "training.log").write_text(training_log)
        raise
    training_seconds = time.monotonic() - training_started
    (OUTPUT / "training.log").write_text(training_log)

    checkpoints = sorted(path for path in OUTPUT.iterdir() if path.is_dir())
    onnx_files = sorted(OUTPUT.glob("*.onnx"))
    checkpoint_steps = sorted(int(path.name.rsplit("_", 1)[1]) for path in checkpoints)
    onnx_steps = sorted(int(path.stem.rsplit("_", 1)[1]) for path in onnx_files)
    expected_steps = [0, 1003520, 2007040]
    if checkpoint_steps != expected_steps or onnx_steps != expected_steps:
        raise SystemExit(
            f"unexpected export steps: checkpoints={checkpoint_steps}, onnx={onnx_steps}"
        )

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "control_commit": CONTROL_COMMIT,
        "input_hashes": actual_hashes,
        "source_checkpoint": str(SOURCE_CHECKPOINT),
        "command": command,
        "execution": {
            "versions_and_devices": versions.splitlines(),
            "training_seconds": training_seconds,
            "total_seconds": time.monotonic() - started,
        },
        "artifacts": {
            "checkpoints": [{"name": path.name, "directory": True} for path in checkpoints],
            "onnx": [{"name": path.name, "sha256": sha256(path)} for path in onnx_files],
        },
        "selection_uses_training_reward": False,
        "behavior_status": "UNEVALUATED",
        "robot_access": False,
        "rdk_access": False,
        "local_gpu_access": False,
    }
    (OUTPUT / "job_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    with tarfile.open(ARTIFACT, "w:gz") as archive:
        archive.add(OUTPUT, arcname=OUTPUT.name)
    final_manifest = {
        **metadata,
        "artifact": str(ARTIFACT),
        "artifact_sha256": sha256(ARTIFACT),
        "artifact_bytes": ARTIFACT.stat().st_size,
    }
    MANIFEST.write_text(json.dumps(final_manifest, indent=2, sort_keys=True) + "\n")
    print(
        RESULT_PREFIX
        + json.dumps(
            {
                "status": final_manifest["status"],
                "artifact": final_manifest["artifact"],
                "artifact_sha256": final_manifest["artifact_sha256"],
                "artifact_bytes": final_manifest["artifact_bytes"],
                "training_seconds": training_seconds,
                "steps": checkpoint_steps,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
