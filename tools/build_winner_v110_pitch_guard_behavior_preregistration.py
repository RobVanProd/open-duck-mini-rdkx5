#!/usr/bin/env python3
"""Preregister the G3-repaired recurrent-source behavior and physical gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = ANALYSIS / "winner_v109_peak_failure_attribution.json"
TRANSFORM = ANALYSIS / "winner_v110_pitch_guard_transform_contract.json"
CURRENT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
OUTPUT = ANALYSIS / "winner_v110_pitch_guard_behavior_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V110_PITCH_GUARD_BEHAVIOR_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "attribution": "128afe8af8d84b6fccb05487c9555250e01f60e83e37a49672966ede1e97bebd",
    "transform": "d48a2c6766f4e0fbd1771e686970d19c3ba93c618c2c8d3b2f64af836b318f5b",
    "current": "17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb",
}
POLICIES = (
    {
        "id": "R64_G3_REPAIRED_HALF",
        "step": 1_003_520,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_1003520.onnx",
        "sha256": "fd1d3b8ad42b99e92803133ee21da1a1092f9f86977a846fbbabf0db80c74c39",
        "bytes": 957_344,
    },
    {
        "id": "R64_G3_REPAIRED_FINAL",
        "step": 2_007_040,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_2007040.onnx",
        "sha256": "58373ef4d7656c5f1c3a6834aef2ecd4d9ccd0fb86a3c18593c891a70909a8ed",
        "bytes": 957_344,
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite: {path}")

    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    policy_root = args.policy_root.resolve()
    policies = []
    for spec in POLICIES:
        path = policy_root / spec["filename"]
        policies.append(
            {
                **spec,
                "path": str(path),
                "observed_sha256": sha256(path),
                "observed_bytes": path.stat().st_size,
            }
        )
    gate = current["prospective_offline_candidate_gate"]
    checks = {
        "attribution_exact": sha256(ATTRIBUTION)
        == EXPECTED["attribution"]
        and attribution.get("status")
        == "PASS_WINNER_V109_PEAK_FAILURE_ATTRIBUTION"
        and attribution.get("decision", {}).get("status")
        == "SELECT_FROZEN_G3_GUARD_FEASIBILITY_SCREEN",
        "transform_exact": sha256(TRANSFORM) == EXPECTED["transform"]
        and transform.get("status")
        == "PASS_WINNER_V110_PITCH_GUARD_TRANSFORM_CONTRACT",
        "current_contract_exact": sha256(CURRENT) == EXPECTED["current"]
        and current.get("status")
        == "PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT",
        "policy_hashes_exact": all(
            row["observed_sha256"] == row["sha256"] for row in policies
        ),
        "policy_sizes_exact": all(
            row["observed_bytes"] == row["bytes"] for row in policies
        ),
        "transform_policy_hashes_exact": {
            row["output_sha256"] for row in transform["policies"]
        }
        == {row["sha256"] for row in policies},
        "g3_repair_exact": transform["repair"]["source_margin_rad"]
        == 0.20000000298023224
        and transform["repair"]["repaired_margin_rad"]
        == 0.16500000655651093
        and transform["repair"]["pitch_action_indices"]
        == [2, 3, 4, 11, 12, 13],
        "manufacturer_gate_complete": (
            gate["per_joint_peak_current_a_max"] == 2.5
            and gate["per_joint_peak_torque_nm_max"] == 1.91229675
            and gate["strict_overcurrent_threshold_a"] == 2.0
            and gate["strict_overcurrent_max_consecutive_ticks"] == 99
            and gate["rated_current_p95"]["candidate_pass_fail"] is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    matrix = [
        {
            "checkpoint_id": policy["id"],
            "step": policy["step"],
            "policy_sha256": policy["sha256"],
            "plant": plant,
            "command_x_m_s": command,
            "seed": 167_931_544,
            "configuration": None,
            "transport": {
                "sensor_noise_scales": None,
                "native_quantization": False,
                "additional_action_delay_ticks": 0,
                "imu_delay_ticks": 0,
            },
            "duration_ticks": 600,
            "calibration_ticks": 0,
            "home_return_ticks": 0,
        }
        for policy in policies
        for plant in ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
        for command in (0.0, 0.074, 0.077, 0.08)
    ]
    value = {
        "schema_version": "winner_v110.pitch_guard_behavior_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V110_PITCH_GUARD_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V110_PITCH_GUARD_BEHAVIOR"
        ),
        "failed_checks": failed,
        "checks": checks,
        "causal_question": (
            "Does the already-frozen G3 full-tick actual-centered pitch guard "
            "remove the isolated peak-current and peak-torque failures while "
            "preserving both recurrent checkpoints' nominal behavior?"
        ),
        "policies": policies,
        "matrix": {
            "cells": len(matrix),
            "sha256": canonical_sha256(matrix),
            "rows": matrix,
        },
        "gate": {
            "conversion_nm_per_a": 0.784532,
            "per_joint_peak_current_a_max": 2.5,
            "per_joint_peak_torque_nm_max": 1.91229675,
            "strict_overcurrent_threshold_a": 2.0,
            "strict_overcurrent_max_consecutive_ticks": 99,
            "rated_current_p95_a": 0.65,
            "rated_current_p95_role": "reported diagnostic only",
            "noncurrent_behavior": (
                "unchanged 600-tick candidate, gait, forward-motion, tracking, "
                "saturation, rate, envelope, x=0, trace, readback, and CPU checks"
            ),
        },
        "decision_rule": {
            "both_checkpoints_all_eight_cells_pass": (
                "Select the G3-repaired recurrent actor as the protected "
                "source for the minimal response-conditioned extension."
            ),
            "only_one_checkpoint_passes": (
                "Reject persistence; do not cherry-pick a checkpoint."
            ),
            "any_noncurrent_failure": (
                "Reject the static repair and attribute before training."
            ),
            "any_peak_or_duration_failure": (
                "Reject the static repair; current-aware continuation remains "
                "a separate preregistration decision."
            ),
            "no_training_or_checkpoint_selection_in_this_screen": True,
        },
        "input_hashes": EXPECTED,
        "authority": {
            "formal_behavior_cells_authorized": 16 if not failed else 0,
            "cpu_only": True,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v110 G3 pitch-guard behavior preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "The exact two repaired recurrent checkpoints will run 16 CPU cells "
        "across both measured actuator plants and x=0/.074/.077/.080. Every "
        "behavior gate is unchanged. Physical pass/fail includes both peak "
        "current <=2.5 A and peak torque <=1.91229675 N.m, plus at most 99 "
        "consecutive ticks strictly above 2 A. The 0.65-A p95 is diagnostic "
        "only. This screen cannot authorize training, selection for deployment, "
        "Gate 5, robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"matrix_sha256={value['matrix']['sha256']}")
    print(f"output_sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
