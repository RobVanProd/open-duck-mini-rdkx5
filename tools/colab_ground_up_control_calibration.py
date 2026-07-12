#!/usr/bin/env python3
"""Self-cleaning Colab T4 calibration for the pinned ground-up control."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path("/content/ground_up_control")
OUT = Path("/content/ground_up_calibration")
COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
TIMESTEPS = 1_000_000


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 600, capture: bool = False):
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def main() -> int:
    started = time.monotonic()
    shutil.rmtree(ROOT, ignore_errors=True)
    shutil.rmtree(OUT, ignore_errors=True)
    run(["git", "clone", "-q", "https://github.com/apirrone/Open_Duck_Playground.git", str(ROOT)])
    run(["git", "checkout", "-q", COMMIT], cwd=ROOT)
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
            "tensorflow>=2.18.0",
            "tf2onnx>=1.16.1",
            "tensorboardX",
        ],
        timeout=900,
    )
    run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "-e", str(ROOT)])

    contract_code = """
import importlib.metadata as m, jax, jax.numpy as jp
from playground.open_duck_mini_v2.joystick import Joystick
assert jax.default_backend() == 'gpu', (jax.default_backend(), jax.devices())
assert m.version('playground') == '0.0.5'
env=Joystick(task='flat_terrain_backlash')
assert env.observation_size == {'state': (101,), 'privileged_state': (212,)}
assert env.action_size == 14 and env.dt == 0.02
s=env.reset(jax.random.PRNGKey(0)); s=env.step(s,jp.zeros(14))
assert bool(jp.all(jp.isfinite(s.obs['state'])))
print('ACCELERATOR_CONTRACT_PASS',jax.devices(),flush=True)
"""
    contract_started = time.monotonic()
    contract = run([sys.executable, "-c", contract_code], cwd=ROOT, timeout=300, capture=True)
    contract_s = time.monotonic() - contract_started

    OUT.mkdir(parents=True)
    training_started = time.monotonic()
    training = run(
        [
            sys.executable,
            "playground/open_duck_mini_v2/runner.py",
            "--task",
            "flat_terrain_backlash",
            "--num_timesteps",
            str(TIMESTEPS),
            "--output_dir",
            str(OUT),
        ],
        cwd=ROOT,
        timeout=900,
        capture=True,
    )
    training_s = time.monotonic() - training_started
    exported = sorted(OUT.glob("*.onnx"))
    checkpoints = sorted(path for path in OUT.iterdir() if path.is_dir())
    result = {
        "status": "PASS_COLAB_GROUND_UP_CONTROL_CALIBRATION",
        "control_commit": COMMIT,
        "timesteps": TIMESTEPS,
        "contract_seconds": contract_s,
        "training_seconds": training_s,
        "steps_per_second": TIMESTEPS / training_s,
        "total_wall_seconds": time.monotonic() - started,
        "onnx_export_count": len(exported),
        "checkpoint_count": len(checkpoints),
        "contract_tail": contract.stdout.splitlines()[-20:],
        "training_tail": training.stdout.splitlines()[-80:],
    }
    print("GROUND_UP_CALIBRATION_RESULT=" + json.dumps(result, sort_keys=True), flush=True)
    if not exported or not checkpoints:
        raise SystemExit("calibration completed without checkpoint and ONNX export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
