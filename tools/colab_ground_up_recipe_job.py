#!/usr/bin/env python3
"""Run one frozen ground-up PPO recipe job on an existing Colab GPU VM.

This file is sent with ``colab exec``. Patch assets must already be uploaded to
``/content``. It never accesses the robot or a local GPU.
"""

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


ROOT = Path("/content/ground_up_recipe_playground")
ASSETS = Path("/content")
OUT_ROOT = Path("/content/ground_up_recipe_outputs")
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
)


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 1800,
        capture: bool = False) -> subprocess.CompletedProcess:
    print("JOB_COMMAND=" + json.dumps(command), flush=True)
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    config_path = ASSETS / "ground_up_recipe_job_config.json"
    defaults = json.loads(config_path.read_text()) if config_path.is_file() else {}
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipe-id", default=defaults.get("recipe_id"), required="recipe_id" not in defaults)
    parser.add_argument("--timesteps", type=int, default=defaults.get("timesteps"), required="timesteps" not in defaults)
    parser.add_argument("--seed", type=int, default=defaults.get("seed"), required="seed" not in defaults)
    parser.add_argument("--learning-rate", type=float, default=defaults.get("learning_rate", 3e-4))
    parser.add_argument("--discounting", type=float, default=defaults.get("discounting", 0.97))
    parser.add_argument("--entropy-cost", type=float, default=defaults.get("entropy_cost", 0.005))
    parser.add_argument("--unroll-length", type=int, default=defaults.get("unroll_length", 20))
    parser.add_argument("--imitation-scale", type=float, default=defaults.get("imitation_scale", 1.0))
    parser.add_argument("--num-evals", type=int, default=defaults.get("num_evals", 3))
    args, _kernel_args = parser.parse_known_args()

    started = time.monotonic()
    for name in PATCHES:
        if not (ASSETS / name).is_file():
            raise SystemExit(f"missing uploaded patch: {name}")

    shutil.rmtree(ROOT, ignore_errors=True)
    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(ROOT)])
    run(["git", "checkout", "-q", CONTROL_COMMIT], cwd=ROOT)
    for name in PATCHES:
        run(["git", "apply", "--check", str(ASSETS / name)], cwd=ROOT)
        run(["git", "apply", str(ASSETS / name)], cwd=ROOT)

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run(
        [
            sys.executable, "-m", "pip", "install", "-q",
            "jax[cuda12]==0.8.2", "jaxlib==0.8.2", "mujoco==3.9.0",
            "playground==0.0.5", "onnxruntime>=1.20.1", "tensorflow==2.20.0",
            "onnx", "tensorboardX",
        ],
        timeout=1200,
    )
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(ROOT)])

    versions = run(
        [sys.executable, "-c", "import importlib.metadata as md; import jax,jaxlib,mujoco; "
         "print(jax.__version__,jaxlib.__version__,mujoco.__version__,md.version('playground')); "
         "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))"],
        capture=True,
    ).stdout
    print("JOB_DEVICE_CONTRACT=" + versions, flush=True)
    if "HAS_GPU True" not in versions:
        raise SystemExit("Colab job did not expose a JAX GPU device")

    output = OUT_ROOT / args.recipe_id
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    command = [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task", "flat_terrain_backlash",
        "--num_timesteps", str(args.timesteps),
        "--output_dir", str(output),
        "--ppo_seed", str(args.seed),
        "--ppo_num_envs", "256",
        "--ppo_num_evals", str(args.num_evals),
        "--ppo_episode_length", "600",
        "--ppo_unroll_length", str(args.unroll_length),
        "--ppo_batch_size", "256",
        "--ppo_num_minibatches", "4",
        "--ppo_num_updates_per_batch", "4",
        "--ppo_learning_rate", str(args.learning_rate),
        "--ppo_discounting", str(args.discounting),
        "--ppo_entropy_cost", str(args.entropy_cost),
        "--imitation_scale", str(args.imitation_scale),
        "--critic_observation", "privileged_state",
    ]
    training_started = time.monotonic()
    training = run(command, cwd=ROOT, timeout=7200, capture=True)
    training_seconds = time.monotonic() - training_started
    (output / "training.log").write_text(training.stdout)

    onnx_files = sorted(output.glob("*.onnx"))
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    if len(onnx_files) < 2 or len(checkpoints) < 2:
        raise SystemExit("training completed without expected checkpoints/ONNX exports")

    metadata = {
        "schema_version": "ground_up_colab_recipe_job.v1",
        "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "recipe_id": args.recipe_id,
        "control_commit": CONTROL_COMMIT,
        "patches": {name: sha256(ASSETS / name) for name in PATCHES},
        "recipe": vars(args),
        "execution": {
            "versions_and_devices": versions.splitlines(),
            "training_seconds": training_seconds,
            "total_seconds": time.monotonic() - started,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "artifacts": {
            "onnx": [{"name": path.name, "sha256": sha256(path)} for path in onnx_files],
            "checkpoints": [path.name for path in checkpoints],
        },
        "selection_uses_training_reward": False,
        "behavior_status": "UNEVALUATED",
    }
    (output / "job_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    artifact = Path(f"/content/{args.recipe_id}_ground_up_recipe_artifacts.tar.gz")
    artifact.unlink(missing_ok=True)
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(output, arcname=output.name)
    print("GROUND_UP_RECIPE_JOB_RESULT=" + json.dumps({
        "status": metadata["status"],
        "artifact": str(artifact),
        "artifact_sha256": sha256(artifact),
        "artifact_bytes": artifact.stat().st_size,
        "training_seconds": training_seconds,
        "onnx_count": len(onnx_files),
        "checkpoint_count": len(checkpoints),
    }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
