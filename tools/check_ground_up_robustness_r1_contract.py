#!/usr/bin/env python3
"""Check the preregistered R1 measured-actuator-fit A/B contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import onnxruntime as ort


PITCH_JOINTS = (
    "left_hip_pitch", "left_knee", "left_ankle",
    "right_hip_pitch", "right_knee", "right_ankle",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    r1 = prereg["stages"][0]
    policy_rows = []
    for spec in prereg["candidate_policies"]:
        path = Path(spec["path"])
        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        rng = np.random.default_rng(20260714 + int(spec["step"]))
        finite = True
        correct_shapes = True
        for command_x in prereg["common_behavior_contract"]["commands_x"]:
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = command_x
            previous = rng.uniform(-1, 1, size=(1, 14)).astype(np.float32)
            action, state = session.run(None, {"obs": obs, "previous_action": previous})
            finite &= bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
            correct_shapes &= action.shape == (1, 14) and state.shape == (1, 14)
        policy_rows.append({
            "step": spec["step"],
            "path": str(path.resolve()),
            "expected_sha256": spec["sha256"],
            "actual_sha256": sha256(path),
            "provider": session.get_providers()[0],
            "finite": finite,
            "correct_shapes": correct_shapes,
            "inputs": [item.name for item in session.get_inputs()],
            "outputs": [item.name for item in session.get_outputs()],
        })
    fit_rows = []
    for spec in r1["fits"]:
        path = Path(spec["path"])
        fit = json.loads(path.read_text())
        joints = fit["primary"]["joints"]
        combined = {joint: joints[joint]["combined"] for joint in PITCH_JOINTS}
        values_finite = all(
            np.isfinite(float(item[key]))
            for item in combined.values()
            for key in ("delay_ticks", "tau_s", "velocity_limit_rad_s", "p95_abs_error")
        )
        fit_rows.append({
            "path": str(path.resolve()),
            "expected_sha256": spec["sha256"],
            "actual_sha256": sha256(path),
            "pitch_joint_set_exact": set(joints) == set(PITCH_JOINTS),
            "combined_values_finite": bool(values_finite),
            "combined": combined,
        })
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_SEQUENTIAL_CPU_ONLY",
        "r1_is_first_and_exact": r1["id"] == "R1_MEASURED_ACTUATOR_FIT_AB" and r1["cells"] == 16,
        "matrix_exact": (
            len(policy_rows) == 2 and len(fit_rows) == 2
            and prereg["common_behavior_contract"]["commands_x"] == [0.0, 0.074, 0.077, 0.08]
            and len(r1["seeds"]) == 1
            and 2 * 2 * 4 * 1 == r1["cells"]
        ),
        "all_policy_hashes_exact": all(row["expected_sha256"] == row["actual_sha256"] for row in policy_rows),
        "all_fit_hashes_exact": all(row["expected_sha256"] == row["actual_sha256"] for row in fit_rows),
        "all_policy_interfaces_exact": all(
            row["inputs"] == ["obs", "previous_action"]
            and row["outputs"] == ["continuous_actions", "previous_action_out"]
            and row["correct_shapes"] for row in policy_rows
        ),
        "all_policy_cpu_inference_finite": all(
            row["provider"] == "CPUExecutionProvider" and row["finite"] for row in policy_rows
        ),
        "both_fit_schemas_valid": all(
            row["pitch_joint_set_exact"] and row["combined_values_finite"] for row in fit_rows
        ),
        "fits_are_independently_distinct": fit_rows[0]["actual_sha256"] != fit_rows[1]["actual_sha256"],
        "accelerators_disabled": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
    }
    failed = [key for key, value in checks.items() if not value]
    status = "PASS_ROBUSTNESS_R1_CONTRACT" if not failed else "FAIL_ROBUSTNESS_R1_CONTRACT"
    payload = {
        "schema_version": "ground_up_robustness_r1_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "policies": policy_rows,
        "fits": fit_rows,
        "matrix": {
            "steps": [row["step"] for row in policy_rows],
            "fit_paths": [row["path"] for row in fit_rows],
            "commands_x": prereg["common_behavior_contract"]["commands_x"],
            "seeds": r1["seeds"],
            "duration_ticks": prereg["common_behavior_contract"]["duration_ticks"],
            "cells": r1["cells"],
        },
        "authority": {
            "run_r1_cpu_behavior": not failed,
            "run_r2_or_later": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False
        }
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Robustness R1 Contract", "", f"status: `{status}`", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in checks.items())
    lines.extend(["", "Passing authorizes only the preregistered 16-cell R1 CPU behavior matrix.", "No R2+, training, Colab, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
