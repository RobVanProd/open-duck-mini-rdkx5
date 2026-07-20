#!/usr/bin/env python3
"""Explain the completed winner-v4 support failure without rerunning its gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from run_winner_v4_response_identifiability_cpu import (
    HOME_RAD,
    SETTLE_TICKS,
    SUBSTEPS,
    contact_state,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "outputs/analysis/winner_v4_response_pretraining_contract.json"
RESULT_PATH = ROOT / "outputs/analysis/winner_v4_response_identifiability_result.json"
EXPECTED_RESULT_SHA256 = "b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730"
DEFAULT_OUTPUT = ROOT / "outputs/analysis/winner_v4_support_failure_diagnostic.json"
DEFAULT_MARKDOWN = ROOT / "outputs/analysis/WINNER_V4_SUPPORT_FAILURE_DIAGNOSTIC_20260720.md"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def quaternion_euler_wxyz(quaternion: np.ndarray) -> tuple[float, float, float]:
    w, x, y, z = (float(value) for value in quaternion)
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch_term = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
    pitch = math.asin(pitch_term)
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def simulate_settle(mujoco: Any, scene: Path, torso_x_offset_m: float) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(scene))
    key_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home"))
    if key_id < 0:
        raise ValueError("home keyframe is missing")
    home_ctrl = np.asarray(model.key_ctrl[key_id], dtype=np.float64)
    if not np.array_equal(home_ctrl, HOME_RAD):
        raise ValueError(f"home control mismatch: {home_ctrl.tolist()}")
    trunk_id = int(
        mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")
    )
    if trunk_id != 2:
        raise ValueError(f"trunk body ID changed: {trunk_id}")
    original_ipos = float(model.body_ipos[trunk_id, 0])
    model.body_ipos[trunk_id, 0] = original_ipos + torso_x_offset_m

    data = mujoco.MjData(model)
    data.qpos[:] = model.key_qpos[key_id]
    data.qvel[:] = 0.0
    data.ctrl[:] = HOME_RAD
    mujoco.mj_setConst(model, data)
    mujoco.mj_forward(model, data)

    contact_states: list[tuple[int, int]] = []
    for _tick in range(SETTLE_TICKS):
        data.ctrl[:] = HOME_RAD
        for _ in range(SUBSTEPS):
            mujoco.mj_step(model, data)
        contact_states.append(contact_state(mujoco, model, data))

    first_both_tick = next(
        (index for index, state in enumerate(contact_states) if state == (1, 1)), None
    )
    final_both_contact_streak = 0
    for state in reversed(contact_states):
        if state != (1, 1):
            break
        final_both_contact_streak += 1
    roll, pitch, yaw = quaternion_euler_wxyz(
        np.asarray(data.qpos[3:7], dtype=np.float64)
    )
    return {
        "torso_x_offset_m": torso_x_offset_m,
        "trunk_ipos_x_before_m": original_ipos,
        "trunk_ipos_x_after_m": float(model.body_ipos[trunk_id, 0]),
        "settle_ticks": SETTLE_TICKS,
        "both_contact_failure_ticks": sum(
            state != (1, 1) for state in contact_states
        ),
        "first_both_contact_tick_zero_based": first_both_tick,
        "final_both_contact_streak_ticks": final_both_contact_streak,
        "final_base_xyz_m": np.asarray(data.qpos[:3], dtype=np.float64).tolist(),
        "final_base_quaternion_wxyz": np.asarray(
            data.qpos[3:7], dtype=np.float64
        ).tolist(),
        "final_base_roll_rad": roll,
        "final_base_pitch_rad": pitch,
        "final_base_yaw_rad": yaw,
        "absolute_roll_distance_to_pi_rad": abs(math.pi - abs(roll)),
    }


def write_markdown(path: Path, result: dict[str, Any], result_sha256: str) -> None:
    negative, positive = result["endpoints"]
    text = f"""# Winner-v4 Support Failure Diagnostic — 2026-07-20

status: `{result['status']}`

diagnostic JSON SHA-256: `{result_sha256}`

completed formal result SHA-256: `{result['formal_result_sha256']}`

## Finding

This read-only diagnostic repeats only the 250-tick setup portion of the exact
frozen simulator scene. It runs no policy, PPO, behavior gate, runtime, or robot.
It does not retry or reclassify the completed response73 falsification.

At torso X = -0.05 m, the base finishes at Z =
`{negative['final_base_xyz_m'][2]:.12f}` m with roll
`{negative['final_base_roll_rad']:.12f}` rad. Its absolute roll is only
`{negative['absolute_roll_distance_to_pi_rad']:.12f}` rad from π. The model is
therefore inverted at the end of setup; its later two-foot contact and distinct
response73 values do not establish a valid standing calibration state.

At torso X = +0.05 m, the base finishes at Z =
`{positive['final_base_xyz_m'][2]:.12f}` m with roll
`{positive['final_base_roll_rad']:.12f}` rad.

## Decision

The frozen free-body support mode is invalid across its requested signed-X
domain. Keep `DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73`. Any replacement support or
sign-preserving response mechanism requires a new prospective contract and
runtime review; this diagnostic authorizes none.
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    if sha256_path(RESULT_PATH) != EXPECTED_RESULT_SHA256:
        raise ValueError("formal response73 result differs from the completed result")
    formal_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    if formal_result["status"] != "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED":
        raise ValueError("unexpected formal response73 result status")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    expected_commit = contract["sources"]["playground"]["commit"]
    actual_commit = git_output(args.playground_root, "rev-parse", "HEAD")
    if actual_commit != expected_commit:
        raise ValueError(f"Playground commit mismatch: {actual_commit}")
    if git_output(args.playground_root, "status", "--porcelain"):
        raise ValueError("Playground checkout is not clean")

    import mujoco

    if getattr(mujoco, "__version__", None) != "3.9.0":
        raise ValueError(f"MuJoCo version must be 3.9.0, got {mujoco.__version__}")
    scene = args.playground_root / contract["sources"]["playground"]["scene"]
    result = {
        "schema_version": "winner_v4_support_failure_diagnostic.v1",
        "status": "EXPLAINS_HOLD_NEGATIVE_ENDPOINT_INVERTED",
        "decision": "DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73",
        "formal_result_sha256": EXPECTED_RESULT_SHA256,
        "formal_result_status": formal_result["status"],
        "playground_commit": actual_commit,
        "scene": contract["sources"]["playground"]["scene"],
        "scene_sha256": sha256_path(scene),
        "mujoco_version": mujoco.__version__,
        "operation": "read_only_settle_reproduction_zero_policy_zero_ppo",
        "endpoints": [
            simulate_settle(mujoco, scene, -0.05),
            simulate_settle(mujoco, scene, 0.05),
        ],
        "authority": {
            "training": False,
            "runtime_implementation": False,
            "robot_or_hardware": False,
            "torque_or_motion": False,
            "gate5_or_deployment": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result_sha256 = sha256_path(args.output)
    write_markdown(args.markdown, result, result_sha256)
    print(json.dumps({"output": str(args.output), "sha256": result_sha256}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
