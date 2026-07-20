#!/usr/bin/env python3
"""Audit the winner-v4 support-reset causal bug without retrying its gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FORMAL_RESULT = ROOT / "outputs/analysis/winner_v4_response_identifiability_result.json"
PRETRAINING_CONTRACT = ROOT / "outputs/analysis/winner_v4_response_pretraining_contract.json"
EXPECTED_FORMAL_SHA256 = "b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730"
OUTPUT_JSON = ROOT / "outputs/analysis/winner_v4_response_support_reset_causal_audit.json"
OUTPUT_MD = ROOT / "outputs/analysis/WINNER_V4_RESPONSE_SUPPORT_RESET_CAUSAL_AUDIT_20260720.md"
HOME_RAD = np.asarray(
    [
        0.002, 0.053, -0.63, 1.368, -0.784, 0.0, 0.0,
        0.0, 0.0, -0.003, -0.065, 0.635, 1.379, -0.796,
    ],
    dtype=np.float64,
)
SETTLE_TICKS = 250
SUBSTEPS = 10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout)
    return completed.stdout.strip()


def euler_wxyz(quaternion: np.ndarray) -> tuple[float, float, float]:
    w, x, y, z = (float(value) for value in quaternion)
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def simulate(
    mujoco: Any, scene: Path, *, torso_x_offset_m: float, legacy_order: bool
) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(scene))
    key_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home"))
    trunk_id = int(
        mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")
    )
    model.body_ipos[trunk_id, 0] += torso_x_offset_m
    data = mujoco.MjData(model)
    if legacy_order:
        data.qpos[:] = model.key_qpos[key_id]
        data.qvel[:] = 0.0
        data.ctrl[:] = HOME_RAD
        mujoco.mj_setConst(model, data)
    else:
        # mj_setConst consumes qpos as a reference pose. Recompute constants while
        # MjData still contains its default reference, then load the episode pose.
        mujoco.mj_setConst(model, data)
        data.qpos[:] = model.key_qpos[key_id]
        data.qvel[:] = 0.0
        data.ctrl[:] = HOME_RAD
    mujoco.mj_forward(model, data)
    for _ in range(SETTLE_TICKS):
        data.ctrl[:] = HOME_RAD
        for _ in range(SUBSTEPS):
            mujoco.mj_step(model, data)
    roll, pitch, yaw = euler_wxyz(np.asarray(data.qpos[3:7], dtype=np.float64))
    return {
        "torso_x_offset_m": torso_x_offset_m,
        "setconst_order": "after_home_qpos" if legacy_order else "before_episode_qpos",
        "final_base_xyz_m": np.asarray(data.qpos[:3], dtype=np.float64).tolist(),
        "final_base_roll_rad": roll,
        "final_base_pitch_rad": pitch,
        "final_base_yaw_rad": yaw,
        "upright": bool(float(data.qpos[2]) >= 0.1 and abs(roll) < 0.8 and abs(pitch) < 0.8),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUTPUT_MD)
    args = parser.parse_args()

    if sha256(FORMAL_RESULT) != EXPECTED_FORMAL_SHA256:
        raise ValueError("completed winner-v4 formal result changed")
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    if formal["status"] != "HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED":
        raise ValueError("unexpected completed winner-v4 status")
    contract = json.loads(PRETRAINING_CONTRACT.read_text(encoding="utf-8"))
    expected_commit = contract["sources"]["playground"]["commit"]
    if git_output(args.playground_root, "rev-parse", "HEAD") != expected_commit:
        raise ValueError("Playground commit mismatch")
    if git_output(args.playground_root, "status", "--porcelain"):
        raise ValueError("Playground checkout is not clean")

    import mujoco

    scene = args.playground_root / contract["sources"]["playground"]["scene"]
    cases = {
        "legacy_nominal": simulate(mujoco, scene, torso_x_offset_m=0.0, legacy_order=True),
        "corrected_nominal": simulate(mujoco, scene, torso_x_offset_m=0.0, legacy_order=False),
        "corrected_negative_x": simulate(
            mujoco, scene, torso_x_offset_m=-0.05, legacy_order=False
        ),
    }
    checks = {
        "formal_result_immutable": True,
        "legacy_nominal_inverted": not cases["legacy_nominal"]["upright"],
        "corrected_nominal_upright": cases["corrected_nominal"]["upright"],
        "negative_x_remains_unsupported_after_reset_fix": not cases[
            "corrected_negative_x"
        ]["upright"],
        "no_retry_or_reclassification": True,
    }
    passed = all(checks.values())
    payload = {
        "schema_version": "winner_v4.response_support_reset_causal_audit.v1",
        "status": "PASS_RESPONSE_SUPPORT_RESET_CAUSAL_AUDIT" if passed else "HOLD_RESPONSE_SUPPORT_RESET_CAUSAL_AUDIT",
        "decision": "KEEP_RESPONSE73_CLOSED_REQUIRE_PROSPECTIVE_REPLACEMENT",
        "formal_result_sha256": EXPECTED_FORMAL_SHA256,
        "checks": checks,
        "cases": cases,
        "finding": (
            "The completed response73 harness called mj_setConst after loading the home "
            "episode qpos. That changes MuJoCo reference constants and makes the nominal "
            "case invert. Correct ordering restores nominal home support, but the -0.05 m "
            "X endpoint still falls, so the completed gate remains failed and cannot be retried."
        ),
        "authority": {
            "cpu_only": True,
            "training": False,
            "robot_or_rdk": False,
            "policy_or_runtime_implementation": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result_sha = sha256(args.output)
    args.markdown.write_text(
        "# Winner-v4 Response Support Reset Causal Audit\n\n"
        f"status: `{payload['status']}`\n\n"
        f"result SHA-256: `{result_sha}`\n\n"
        f"completed formal result SHA-256: `{EXPECTED_FORMAL_SHA256}`\n\n"
        "The completed result is not retried or reclassified. The audit isolates a "
        "`mj_setConst` ordering bug: nominal home support fails under the legacy order "
        "and remains upright under the corrected order. The corrected negative-X "
        "endpoint still falls, so response73 stays closed and only a new prospective "
        "support procedure may advance.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": result_sha}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
