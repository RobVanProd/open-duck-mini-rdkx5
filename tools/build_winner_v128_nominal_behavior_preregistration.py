#!/usr/bin/env python3
"""Preregister the unchanged 16-cell V128 nominal physical gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
TRANSFORM = ANALYSIS / "winner_v128_deployment_transform_contract.json"
TRAINING = ANALYSIS / "winner_v127_recovered_training_validation.json"
BASE = ANALYSIS / "winner_v110_pitch_guard_behavior_preregistration.json"
OUTPUT = ANALYSIS / "winner_v128_nominal_behavior_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V128_NOMINAL_BEHAVIOR_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "v128_transform_contract": (
        "2dac89511e532156d3d4f589aa9b6defe7641fe6d73c221a5cdb72c34bf283e0"
    ),
    "v127_training_validation": (
        "d1936251394926a9bbc605e331158fd7a1cd49dbbea9e808093d1f688fec8a80"
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
            raise FileExistsError(f"refusing to overwrite V128: {path}")
    policy_root = args.policy_root.resolve()
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    training = json.loads(TRAINING.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    hashes = {
        "v128_transform_contract": sha256(TRANSFORM),
        "v127_training_validation": sha256(TRAINING),
        "base_nominal_preregistration": sha256(BASE),
    }
    policies = [
        {
            "id": row["id"],
            "step": row["step"],
            "filename": Path(row["output_path"]).name,
            "path": row["output_path"],
            "sha256": row["output_sha256"],
            "bytes": row["output_bytes"],
        }
        for row in transform["policies"]
    ]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "transform_contract_exact": (
            transform.get("status")
            == "PASS_WINNER_V128_DEPLOYMENT_TRANSFORM_CONTRACT"
            and transform.get("failed_checks") == []
            and transform.get("authority", {}).get(
                "nominal_behavior_preregistration_authorized"
            )
            is True
        ),
        "training_validation_exact": (
            training.get("status")
            == "PASS_WINNER_V127_RECOVERED_TRAINING_VALIDATION"
            and training.get("failed_checks") == []
        ),
        "base_nominal_gate_exact": (
            base.get("status")
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
        "training_steps_zero": True,
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
        "schema_version": "winner_v128.nominal_behavior_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V128_NOMINAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V128_NOMINAL_BEHAVIOR_PREREGISTRATION"
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
                "hold the policy and attribute before further policy work"
            ),
            "reward_or_training_metric_selection": False,
        },
        "execution_now": {
            "formal_behavior_cells": 0,
            "training_steps": 0,
            "colab_compute_units": 0,
            "rdk_or_robot_access": 0,
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V128 nominal behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Matrix SHA-256: `{matrix_hash}`\n"
        "- Both checkpoints, both measured plants, and four commands.\n"
        "- Both checkpoints must pass all behavior/current/torque checks.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"matrix_sha256={matrix_hash}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
