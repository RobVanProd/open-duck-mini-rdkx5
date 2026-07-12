#!/usr/bin/env python3
"""One-shot preregistered Colab job for the hardware-vector PPO route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


CONTENT = Path("/content")
RDK = CONTENT / "open-duck-mini-rdkx5"
PLAYGROUND = CONTENT / "Open_Duck_Playground"
OUT = CONTENT / "hardware_vector_constrained_ppo"


def run(command: list[str], cwd: Path | None = None, timeout: int = 7200) -> None:
    print("RUN", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True, timeout=timeout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (RDK, PLAYGROUND, OUT):
        shutil.rmtree(path, ignore_errors=True)
    run(["tar", "-xzf", "/content/open-duck-mini-rdkx5.tar.gz", "-C", "/content"])
    run(["tar", "-xzf", "/content/Open_Duck_Playground.tar.gz", "-C", "/content"])
    OUT.mkdir(parents=True)

    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=600)
    run([
        sys.executable, "-m", "pip", "install", "-q",
        "jax[cuda12]==0.7.2", "jaxlib==0.7.2", "playground==0.0.5",
        "mujoco==3.9.0", "mujoco-mjx==3.9.0", "onnxruntime==1.27.0",
        "ml-collections==1.1.0", "numpy==2.0.2", "tensorflow==2.20.0",
        "protobuf==5.29.6", "onnx==1.22.0",
    ], timeout=1800)
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(PLAYGROUND)])
    run([sys.executable, "-c", "import jax; assert jax.default_backend()=='gpu'; print(jax.devices())"])

    command = [
        sys.executable, "playground/open_duck_mini_v2/runner.py",
        "--task", "rough_terrain_backlash", "--env", "joystick",
        "--output_dir", str(OUT), "--export_min_step", "1",
        "--num_timesteps", "245760", "--ppo_num_envs", "256",
        "--ppo_num_evals", "4", "--ppo_episode_length", "600",
        "--ppo_unroll_length", "10", "--ppo_batch_size", "256",
        "--ppo_num_minibatches", "4", "--ppo_num_updates_per_batch", "4",
        "--restore_checkpoint_path", str(RDK / "outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint"),
        "--ppo_learning_rate", "0.00003", "--ppo_entropy_cost", "0.001",
        "--ppo_clipping_epsilon", "0.08", "--ppo_max_grad_norm", "0.2",
        "--restore_policy_kl_scale", "0.05", "--tracking_lin_vel_scale", "3",
        "--forward_progress_scale", "2", "--command_progress_scale", "1",
        "--command_progress_shortfall_scale", "-2", "--command_progress_required_ratio", "0.35",
        "--command_progress_warmup_steps", "30", "--target_rate_scale", "-0.04",
        "--target_rate_huber_delta", "0.08", "--target_rate_limit_scale", "-1.1830617141938795",
        "--target_rate_limit_joint_indices", "2,3,4,11,12,13",
        "--target_rate_limit_values", "1.5,1.5,1.75,1.25,1.0,1.25",
        "--target_rate_limit_huber_delta", "0.05", "--actuator_tracking_scale", "-0.03",
        "--actuator_tracking_huber_delta", "0.04", "--action_rate_scale", "-0.12",
        "--action_rate_huber_delta", "0.05", "--action_magnitude_scale", "-0.01",
        "--base_height_scale", "-0.3", "--forward_pitch_scale", "-0.4",
        "--forward_pitch_rate_scale", "-0.08", "--alive_scale", "2", "--imitation_scale", "0",
        "--lin_vel_x_min", "0.06", "--lin_vel_x_max", "0.1", "--lin_vel_y_min", "0",
        "--lin_vel_y_max", "0", "--ang_vel_yaw_min", "0", "--ang_vel_yaw_max", "0",
        "--command_resample_steps", "600", "--zero_command_probability", "0.15",
        "--noise_level", "0.5", "--noise_hip_pos", "0.01", "--noise_knee_pos", "0.01",
        "--noise_ankle_pos", "0.01", "--noise_joint_vel", "1", "--noise_gravity", "0.05",
        "--noise_gyro", "0.05", "--noise_accelerometer", "0.025", "--no-push_enable",
        "--enable_behavior_prior", "--behavior_prior_mlp_npz",
        str(RDK / "outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate_mlp.npz"),
        "--behavior_prior_scale", "-0.08", "--behavior_prior_huber_delta", "0.05",
        "--enable_actuator_bridge", "--actuator_bridge_delay_min_ticks", "2",
        "--actuator_bridge_delay_max_ticks", "3", "--actuator_bridge_tau_min_s", "0.005",
        "--actuator_bridge_tau_max_s", "0.12", "--actuator_bridge_velocity_limit_min_rad_s", "1.0",
        "--actuator_bridge_velocity_limit_max_rad_s", "5.24", "--actuator_bridge_per_joint_variation", "0",
        "--actuator_bridge_delay_ticks", "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--actuator_bridge_tau_s", ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005",
        "--actuator_bridge_velocity_limits_rad_s", "5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25",
    ]
    manifest = {"status": "RUNNING", "command": command}
    (OUT / "frozen_job_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    run(command, cwd=PLAYGROUND, timeout=10800)

    files = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(OUT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest.update(status="COMPLETE", files=files)
    (OUT / "frozen_job_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    archive = shutil.make_archive("/content/hardware_vector_constrained_ppo_result", "zip", OUT)
    print("RESULT_ARCHIVE", archive, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
