#!/usr/bin/env python3
"""Preregister the current-corrected recurrent-source nominal screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CURRENT_CONTRACT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
FAILURE_ATTRIBUTION = ANALYSIS / "winner_v3_failure_attribution.json"
TRAINING_CHECK = (
    ANALYSIS / "winner_v3_recurrent_adapter_training_artifact_check.json"
)
TRANSFORM_CONTRACT = (
    ANALYSIS / "winner_v3_variable_configuration_eval_policy_transform_contract.json"
)
ARCHIVE = ANALYSIS / "winner_v3_recurrent_adapter_artifacts.tar.gz"
V108 = ANALYSIS / "winner_v108_prefix_handoff_result.json"
OUTPUT = ANALYSIS / "winner_v109_recurrent_source_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V109_RECURRENT_SOURCE_PREREGISTRATION_20260724.md"

EXPECTED = {
    "current_contract": "17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb",
    "failure_attribution": "6c010d2ac9d90ff039ba1a9426ecdaedc499d703f342e3ec0d210e88e2404586",
    "training_check": "3ec53048fbe48e8eb8effbea725940746e85845ee6b8731ce4131fa8e931e683",
    "transform_contract": "78a53a43065baaaf18aee12724cf4614ae65c70a5a5af9fd1fc0405a4c7339eb",
    "archive": "bee604f002df5082bce579734be5a7983f2b31a6026b1caaa34d64b26ce48d91",
    "v108": "a8e0026a566aa4bf01605692aa4cf1401442b1c3f9532dca40a701b81907b0c9",
}
POLICIES = (
    {
        "id": "R64_RECURRENT_HALF",
        "step": 1_003_520,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_1003520.onnx",
        "sha256": "c8e03dd4afed4e7a96507e5089116944a048ac1d682210408a68cca1b8b6af7c",
        "bytes": 957_344,
    },
    {
        "id": "R64_RECURRENT_FINAL",
        "step": 2_007_040,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_2007040.onnx",
        "sha256": "dfdd01bf4563e3d377ffcbe70515681e75a0d87797f3b6b9e4486d1b40ad569c",
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
            raise FileExistsError(
                f"refusing to overwrite Winner-v109 preregistration: {path}"
            )

    policy_root = args.policy_root.resolve()
    current = json.loads(CURRENT_CONTRACT.read_text(encoding="utf-8"))
    attribution = json.loads(FAILURE_ATTRIBUTION.read_text(encoding="utf-8"))
    training = json.loads(TRAINING_CHECK.read_text(encoding="utf-8"))
    transform = json.loads(TRANSFORM_CONTRACT.read_text(encoding="utf-8"))
    v108 = json.loads(V108.read_text(encoding="utf-8"))
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

    current_gate = current["prospective_offline_candidate_gate"]
    checks = {
        "current_contract_exact": sha256(CURRENT_CONTRACT)
        == EXPECTED["current_contract"]
        and current.get("status") == "PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT",
        "failure_attribution_exact": sha256(FAILURE_ATTRIBUTION)
        == EXPECTED["failure_attribution"]
        and attribution.get("status")
        == "PASS_WINNER_V3_READ_ONLY_FAILURE_ATTRIBUTION_CORRECTED",
        "training_artifact_exact": sha256(TRAINING_CHECK)
        == EXPECTED["training_check"]
        and training.get("status")
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK",
        "transform_contract_exact": sha256(TRANSFORM_CONTRACT)
        == EXPECTED["transform_contract"]
        and transform.get("status")
        == "PASS_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT",
        "archive_exact": sha256(ARCHIVE) == EXPECTED["archive"],
        "v108_exact": sha256(V108) == EXPECTED["v108"]
        and v108.get("decision", {}).get("status")
        == "BASELINE_CONTROL_DID_NOT_ISOLATE_PREFIX",
        "two_policy_hashes_exact": all(
            row["observed_sha256"] == row["sha256"] for row in policies
        ),
        "two_policy_sizes_exact": all(
            row["observed_bytes"] == row["bytes"] for row in policies
        ),
        "prospective_current_rule_exact": (
            current_gate["per_joint_peak_current_a_max"] == 2.5
            and current_gate["strict_overcurrent_threshold_a"] == 2.0
            and current_gate["strict_overcurrent_max_consecutive_ticks"] == 99
            and current_gate["rated_current_p95"]["candidate_pass_fail"] is False
        ),
        "historical_nominal_precurrent_pass_exact": (
            attribution["nominal_baseline_comparison"]["summary"][
                "baseline_prior_behavior_passes"
            ]
            == 16
            and attribution["nominal_baseline_comparison"]["summary"][
                "candidate_prior_behavior_passes_excluding_current"
            ]
            == 16
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
        "schema_version": "winner_v109.recurrent_source_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V109_RECURRENT_SOURCE_SCREEN"
            if not failed
            else "HOLD_WINNER_V109_RECURRENT_SOURCE_SCREEN"
        ),
        "failed_checks": failed,
        "checks": checks,
        "causal_question": (
            "Are both already-trained recurrent variable-configuration "
            "checkpoints valid persistent nominal sources under the prospective "
            "manufacturer-backed current rule that supersedes p95<=0.65 A?"
        ),
        "policies": policies,
        "matrix": {
            "cells": len(matrix),
            "sha256": canonical_sha256(matrix),
            "rows": matrix,
        },
        "current_gate": {
            "conversion_nm_per_a": 0.784532,
            "per_joint_peak_current_a_max": 2.5,
            "strict_overcurrent_threshold_a": 2.0,
            "strict_overcurrent_max_consecutive_ticks": 99,
            "rated_current_p95_a": 0.65,
            "rated_current_p95_role": "reported diagnostic only",
        },
        "decision_rule": {
            "both_checkpoints_all_eight_cells_pass": (
                "Select the recurrent actor as the protected source for a "
                "minimal response-conditioned extension."
            ),
            "only_one_checkpoint_passes": (
                "Reject persistence; do not cherry-pick the passing checkpoint."
            ),
            "either_checkpoint_has_noncurrent_behavior_failure": (
                "Do not use that recurrent actor as the protected source."
            ),
            "no_checkpoint_selection": True,
            "no_training_until_result": True,
        },
        "known_v108_trace_note": (
            "V108 applied the response-runner h-reset trace check to a source "
            "policy with no h input. That trace-only failure is non-applicable; "
            "every V108 cell independently failed at least one physical metric, "
            "so the prefix rejection is unchanged."
        ),
        "input_hashes": EXPECTED,
        "authority": {
            "recurrent_source_screen_authorized": not failed,
            "formal_behavior_cells_authorized": 16 if not failed else 0,
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
        "# Winner-v109 recurrent-source preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "This 16-cell CPU screen tests the two persistent winner-v3 recurrent "
        "checkpoints across both measured actuator fits and all four frozen "
        "commands. It applies the prospective manufacturer-backed current rule: "
        "peak <=2.5 A and fewer than 100 consecutive 50 Hz ticks strictly above "
        "2 A. The old p95<=0.65 A value is reported only, exactly as the frozen "
        "current-gate application contract requires. No policy is selected and "
        "no training, Gate 5, robot, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"matrix_sha256={value['matrix']['sha256']}")
    print(f"sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
