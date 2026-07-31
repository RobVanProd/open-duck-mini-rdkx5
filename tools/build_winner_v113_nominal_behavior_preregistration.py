#!/usr/bin/env python3
"""Preregister the 16-cell V113 nominal physical gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v112_recovered_training_validation.json"
TRANSFORM = ANALYSIS / "winner_v113_postexport_transform_contract.json"
BASE = ANALYSIS / "winner_v110_pitch_guard_behavior_preregistration.json"
OUTPUT = ANALYSIS / "winner_v113_nominal_behavior_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V113_NOMINAL_BEHAVIOR_PREREGISTRATION_20260724.md"
EXPECTED = {
    "v112_validation": (
        "895c010a015da4dc43bec2bf3752767c7633859adef2f1b277ef7315e941d4a7"
    ),
    "transform_contract": (
        "6486d708254ac3b6b644656e075d7139598474816befa2bb862de65066fe32a5"
    ),
    "base_nominal_preregistration": (
        "7698a551fa88cf1b0ca09503f383242e8735ce30436c189876bf4bde4b11b6d0"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V113: {path}")
    policy_root = args.policy_root.resolve()
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    hashes = {
        "v112_validation": sha256(VALIDATION),
        "transform_contract": sha256(TRANSFORM),
        "base_nominal_preregistration": sha256(BASE),
    }
    policies = [
        {
            "id": (
                "V113_G3_DEADBAND_HALF"
                if row["step"] == 1_003_520
                else "V113_G3_DEADBAND_FINAL"
            ),
            "step": row["step"],
            "filename": Path(row["output_path"]).name,
            "path": row["output_path"],
            "sha256": row["output_sha256"],
            "bytes": row["output_bytes"],
        }
        for row in transform["policies"]
    ]
    checks = {
        "v112_validation_exact": (
            hashes["v112_validation"] == EXPECTED["v112_validation"]
            and validation.get("status")
            == "PASS_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
        ),
        "transform_contract_exact": (
            hashes["transform_contract"] == EXPECTED["transform_contract"]
            and transform.get("status")
            == "PASS_WINNER_V113_POSTEXPORT_TRANSFORM_CONTRACT"
            and transform.get("failed_checks") == []
            and transform.get("authority", {}).get(
                "nominal_behavior_preregistration_authorized"
            )
            is True
        ),
        "base_nominal_gate_exact": (
            hashes["base_nominal_preregistration"]
            == EXPECTED["base_nominal_preregistration"]
            and base.get("status")
            == "PREREGISTERED_WINNER_V110_PITCH_GUARD_BEHAVIOR"
        ),
        "two_policy_files_exact": all(
            (policy_root / row["filename"]).stat().st_size == row["bytes"]
            and sha256(policy_root / row["filename"]) == row["sha256"]
            for row in policies
        ),
        "both_postupdate_checkpoints_included": {
            row["step"] for row in policies
        }
        == {1_003_520, 2_007_040},
        "manufacturer_gate_unchanged": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    rows = []
    for policy in policies:
        for plant in (
            "P30_ALL_JOINT",
            "P31_34_PITCH_WITH_P30_NONPITCH",
        ):
            for command in (0.0, 0.074, 0.077, 0.080):
                rows.append(
                    {
                        "checkpoint_id": policy["id"],
                        "step": policy["step"],
                        "policy_sha256": policy["sha256"],
                        "plant": plant,
                        "command_x_m_s": command,
                        "seed": 167931544,
                        "duration_ticks": 600,
                        "configuration": None,
                        "calibration_ticks": 0,
                        "home_return_ticks": 0,
                        "transport": {
                            "additional_action_delay_ticks": 0,
                            "imu_delay_ticks": 0,
                            "native_quantization": False,
                            "sensor_noise_scales": None,
                        },
                    }
                )
    matrix_hash = canonical_sha256(rows)
    payload = {
        "schema_version": "winner_v113.nominal_behavior_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V113_NOMINAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V113_NOMINAL_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "policies": policies,
        "matrix": {
            "cells": len(rows),
            "rows": rows,
            "sha256": matrix_hash,
        },
        "gate": base["gate"],
        "decision_rule": {
            "both_checkpoints_all_eight_cells_pass": (
                "authorize a separate full frozen robustness-matrix "
                "preregistration"
            ),
            "only_one_checkpoint_passes": (
                "reject persistence; do not cherry-pick"
            ),
            "any_behavior_current_or_torque_failure": (
                "hold the policy and attribute before any further training"
            ),
            "reward_or_training_metric_selection": False,
        },
        "authority": {
            "formal_behavior_cells_authorized": (
                len(rows) if not failed else 0
            ),
            "cpu_only": True,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v113 nominal behavior preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Matrix SHA-256: `{matrix_hash}`\n\n"
        "The frozen 16 cells cover both post-update checkpoints, both measured "
        "actuator plants, and x=0/.074/.077/.080 for 600 ticks. Both "
        "checkpoints must pass every behavior, current, and torque check. No "
        "cherry-pick, full matrix, Gate 5, robot, torque, or motion authority "
        "is granted here.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"matrix_sha256={matrix_hash}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
