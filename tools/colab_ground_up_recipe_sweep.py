#!/usr/bin/env python3
"""Run a preregistered ground-up recipe matrix in one Colab environment.

The script installs the frozen stack once, trains candidates sequentially, and
writes one recoverable tarball per completed candidate plus a sweep manifest.
It never evaluates on or connects to robot hardware.
"""

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


ROOT = Path("/content/ground_up_recipe_playground")
ASSETS = Path("/content")
OUT_ROOT = Path("/content/ground_up_recipe_outputs")
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
BASE_PATCHES = (
    "ground_up_search_runner.patch",
    "ground_up_reference_conditioned.patch",
    "ground_up_recipe_search.patch",
)


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 1800,
        capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("SWEEP_COMMAND=" + json.dumps(command), flush=True)
    return subprocess.run(
        command, cwd=cwd, check=True, timeout=timeout, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def archive_candidate(output: Path) -> dict[str, object]:
    artifact = ASSETS / f"{output.name}_ground_up_recipe_artifacts.tar.gz"
    artifact.unlink(missing_ok=True)
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(output, arcname=output.name)
    result = {
        "artifact": str(artifact),
        "artifact_sha256": sha256(artifact),
        "artifact_bytes": artifact.stat().st_size,
    }
    print("SWEEP_CANDIDATE_ARTIFACT=" + json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> int:
    config_path = ASSETS / "ground_up_stage1_recipe_local_search_matrix.json"
    config = json.loads(config_path.read_text())
    patches = (*BASE_PATCHES, *tuple(config["shared"]["extra_patches"]))
    for name in patches:
        if not (ASSETS / name).is_file():
            raise SystemExit(f"missing uploaded patch: {name}")

    started = time.monotonic()
    shutil.rmtree(ROOT, ignore_errors=True)
    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(ROOT)])
    run(["git", "checkout", "-q", CONTROL_COMMIT], cwd=ROOT)
    for name in patches:
        run(["git", "apply", "--check", str(ASSETS / name)], cwd=ROOT)
        run(["git", "apply", str(ASSETS / name)], cwd=ROOT)

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run([
        sys.executable, "-m", "pip", "install", "-q",
        "jax[cuda12]==0.8.2", "jaxlib==0.8.2", "mujoco==3.9.0",
        "playground==0.0.5", "onnxruntime>=1.20.1", "tensorflow==2.20.0",
        "onnx", "tensorboardX",
    ], timeout=1200)
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(ROOT)])

    device_contract = run([
        sys.executable, "-c",
        "import importlib.metadata as md; import jax,jaxlib,mujoco; "
        "print(jax.__version__,jaxlib.__version__,mujoco.__version__,md.version('playground')); "
        "print(jax.devices()); print('HAS_GPU',any(d.platform=='gpu' for d in jax.devices()))",
    ], capture=True).stdout
    print("SWEEP_DEVICE_CONTRACT=" + device_contract, flush=True)
    if "HAS_GPU True" not in device_contract:
        raise SystemExit("Colab sweep did not expose a JAX GPU")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    completed: list[dict[str, object]] = []
    for candidate in config["candidates"]:
        candidate_started = time.monotonic()
        output = OUT_ROOT / candidate["id"]
        shutil.rmtree(output, ignore_errors=True)
        output.mkdir(parents=True)
        command = [
            sys.executable, "playground/open_duck_mini_v2/runner.py",
            "--task", "flat_terrain_backlash",
            "--num_timesteps", str(config["timesteps"]),
            "--output_dir", str(output),
            "--ppo_seed", str(config["training_seed"]),
            "--ppo_num_envs", "256",
            "--ppo_num_evals", str(config["num_evals"]),
            "--ppo_episode_length", "600",
            "--ppo_unroll_length", str(candidate.get(
                "unroll_length", config["shared"]["unroll_length"]
            )),
            "--ppo_batch_size", "256",
            "--ppo_num_minibatches", "4",
            "--ppo_num_updates_per_batch", "4",
            "--ppo_learning_rate", str(candidate["learning_rate"]),
            "--ppo_discounting", str(candidate.get(
                "discounting", config["shared"]["discounting"]
            )),
            "--ppo_entropy_cost", str(candidate["entropy_cost"]),
            "--imitation_scale", str(candidate["imitation_scale"]),
            "--critic_observation", candidate.get(
                "critic_observation", "privileged_state"
            ),
        ]
        if candidate.get("policy_architecture"):
            command.extend([
                "--policy_architecture", candidate["policy_architecture"]
            ])
        if candidate.get("recurrent_hidden_size"):
            command.extend([
                "--recurrent_hidden_size", str(candidate["recurrent_hidden_size"])
            ])
        if candidate.get("reference_feature_table_path"):
            reference_table = ASSETS / candidate["reference_feature_table_path"]
            if not reference_table.is_file():
                raise SystemExit(f"missing reference table: {reference_table}")
            command.extend([
                "--reference_feature_table_path", str(reference_table)
            ])
        if candidate.get("nominal_reference_bootstrap"):
            command.append("--nominal_reference_bootstrap")
            command.extend([
                "--nominal_reference_command_x",
                str(candidate.get("nominal_reference_command_x", 0.074)),
                "--reference_start_phase",
                str(candidate.get("reference_start_phase", 0)),
            ])
        if candidate.get("ground_up_signed_progress_objective"):
            command.append("--ground_up_signed_progress_objective")
        if config["shared"]["ground_up_command_curriculum"]:
            command.append("--ground_up_command_curriculum")
        training = run(command, cwd=ROOT, timeout=7200, capture=True)
        (output / "training.log").write_text(training.stdout)
        onnx_files = sorted(output.glob("*.onnx"))
        checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
        if len(onnx_files) < 2 or len(checkpoints) < 2:
            raise SystemExit(f"{candidate['id']} completed without expected exports")
        metadata = {
            "schema_version": "ground_up_colab_recipe_sweep_candidate.v1",
            "status": "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
            "candidate": candidate,
            "shared": config["shared"],
            "control_commit": CONTROL_COMMIT,
            "patches": {name: sha256(ASSETS / name) for name in patches},
            "training_seed": config["training_seed"],
            "timesteps": config["timesteps"],
            "training_seconds": time.monotonic() - candidate_started,
            "onnx": [{"name": path.name, "sha256": sha256(path)} for path in onnx_files],
            "checkpoints": [path.name for path in checkpoints],
            "selection_uses_training_reward": False,
            "behavior_status": "UNEVALUATED",
        }
        (output / "job_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        completed.append({**metadata, **archive_candidate(output)})
        manifest = {
            "schema_version": "ground_up_colab_recipe_sweep.v1",
            "status": "RUNNING",
            "device_contract": device_contract.splitlines(),
            "completed": completed,
            "elapsed_seconds": time.monotonic() - started,
            "selection_uses_training_reward": False,
        }
        (ASSETS / "ground_up_recipe_sweep_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )

    manifest["status"] = "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY"
    (ASSETS / "ground_up_recipe_sweep_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print("GROUND_UP_RECIPE_SWEEP_RESULT=" + json.dumps({
        "status": manifest["status"],
        "completed_candidates": [item["candidate"]["id"] for item in completed],
        "elapsed_seconds": manifest["elapsed_seconds"],
    }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
