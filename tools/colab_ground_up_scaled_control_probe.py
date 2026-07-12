#!/usr/bin/env python3
"""Self-cleaning T4 throughput probe for the scaled canonical control."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path("/content/ground_up_control")
OUT = Path("/content/ground_up_scaled_probe")
COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
TIMESTEPS = 1_000_000


def run(command, *, cwd=None, timeout=900, capture=False):
    return subprocess.run(command, cwd=cwd, check=True, timeout=timeout, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None)


def apply_scale_patch() -> None:
    runner = ROOT / "playground/open_duck_mini_v2/runner.py"
    text = runner.read_text()
    anchor = '    parser.add_argument("--num_timesteps", type=int, default=150000000)\n'
    addition = anchor + """    parser.add_argument("--ppo_num_envs", type=int, default=8192)
    parser.add_argument("--ppo_num_evals", type=int, default=15)
    parser.add_argument("--ppo_episode_length", type=int, default=1000)
    parser.add_argument("--ppo_unroll_length", type=int, default=20)
    parser.add_argument("--ppo_batch_size", type=int, default=256)
    parser.add_argument("--ppo_num_minibatches", type=int, default=32)
    parser.add_argument("--ppo_num_updates_per_batch", type=int, default=4)
"""
    if text.count(anchor) != 1:
        raise SystemExit("runner scale anchor mismatch")
    runner.write_text(text.replace(anchor, addition))

    common = ROOT / "playground/common/runner.py"
    text = common.read_text()
    anchor = "        self.ppo_training_params = dict(self.ppo_params)\n"
    addition = anchor + """        for config_key, arg_name in (
            ("num_envs", "ppo_num_envs"),
            ("num_evals", "ppo_num_evals"),
            ("episode_length", "ppo_episode_length"),
            ("unroll_length", "ppo_unroll_length"),
            ("batch_size", "ppo_batch_size"),
            ("num_minibatches", "ppo_num_minibatches"),
            ("num_updates_per_batch", "ppo_num_updates_per_batch"),
        ):
            self.ppo_training_params[config_key] = getattr(self.args, arg_name)
"""
    if text.count(anchor) != 1:
        raise SystemExit("common runner scale anchor mismatch")
    common.write_text(text.replace(anchor, addition))


def main() -> int:
    started = time.monotonic()
    shutil.rmtree(ROOT, ignore_errors=True); shutil.rmtree(OUT, ignore_errors=True)
    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(ROOT)])
    run(["git", "checkout", "-q", COMMIT], cwd=ROOT)
    apply_scale_patch()
    run([sys.executable, "-m", "pip", "install", "-q", "-U", "pip"], timeout=300)
    run([sys.executable, "-m", "pip", "install", "-q", "jax[cuda12]==0.8.2", "jaxlib==0.8.2",
         "mujoco==3.9.0", "playground==0.0.5", "onnxruntime>=1.20.1",
         "tensorflow==2.20.0", "onnx", "tensorboardX"], timeout=900)
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "tf2onnx==1.17.0"])
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(ROOT)])
    OUT.mkdir(parents=True)
    command = [sys.executable, "playground/open_duck_mini_v2/runner.py", "--task", "flat_terrain_backlash",
               "--num_timesteps", str(TIMESTEPS), "--output_dir", str(OUT),
               "--ppo_num_envs", "256", "--ppo_num_evals", "2",
               "--ppo_episode_length", "600", "--ppo_unroll_length", "10",
               "--ppo_batch_size", "256", "--ppo_num_minibatches", "4",
               "--ppo_num_updates_per_batch", "4"]
    training_started = time.monotonic()
    training = run(command, cwd=ROOT, timeout=900, capture=True)
    training_s = time.monotonic() - training_started
    exported = sorted(OUT.glob("*.onnx"))
    checkpoints = sorted(path for path in OUT.iterdir() if path.is_dir())
    result = {"status": "PASS_SCALED_CONTROL_T4_PROBE", "timesteps": TIMESTEPS,
              "training_seconds": training_s, "steps_per_second": TIMESTEPS / training_s,
              "total_wall_seconds": time.monotonic() - started, "onnx_export_count": len(exported),
              "checkpoint_count": len(checkpoints), "training_tail": training.stdout.splitlines()[-100:]}
    print("GROUND_UP_SCALED_PROBE_RESULT=" + json.dumps(result, sort_keys=True), flush=True)
    if not exported or not checkpoints:
        raise SystemExit("probe completed without checkpoint and ONNX export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
