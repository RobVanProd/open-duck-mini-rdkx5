#!/usr/bin/env python3
"""Preregister the CPU-only T62 midpoint-endpoint causal screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t65_t62_midpoint_endpoint_screen_preregistration.json"
T63 = ANALYSIS / "t63_t62_postexport_result.json"
T64_PREREG = ANALYSIS / "t64_t62_nominal_matrix_preregistration.json"
T64_RESULT = ANALYSIS / "t64_t62_nominal_matrix_result.json"
RUNNER = ROOT / "tools" / "run_t65_t62_midpoint_endpoint_screen.py"
TEST = ROOT / "tests" / "test_t65_t62_midpoint_endpoint_screen.py"
POLICY = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t63_t62_deployments_20260728"
    / "0"
    / "action_margin.onnx"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite T65 prereg: {OUTPUT}")
    status = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip()
    if status:
        raise RuntimeError("formal T65 preregistration requires a clean worktree")

    t63 = json.loads(T63.read_text(encoding="utf-8"))
    t64_prereg = json.loads(T64_PREREG.read_text(encoding="utf-8"))
    t64_result = json.loads(T64_RESULT.read_text(encoding="utf-8"))
    deployment = t63["deployments"]["0"]["wrapped"]
    checks = {
        "t63_transform_green": (
            t63["status"] == "PASS_T63_T62_POSTEXPORT"
            and deployment["sha256"] == sha256(POLICY)
        ),
        "t64_midpoint_transfer_closed": (
            t64_result["status"] == "HOLD_T64_T62_NOMINAL_MATRIX"
            and t64_result["decision"]
            == "CLOSE_T62_MIDPOINT_GAIT_TRANSFER_CURRICULUM"
            and t64_result["condition"]["green_cells"] == 7
        ),
        "single_frozen_midpoint_endpoint": POLICY.is_file(),
        "exactly_two_measured_fits": len(t64_prereg["fits"]) == 2,
        "exactly_four_frozen_commands": (
            t64_prereg["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "cpu_only_diagnostic": True,
        "no_checkpoint_promotion": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T65 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t65_t62_midpoint_endpoint_screen_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T65_T62_MIDPOINT_ENDPOINT_SCREEN",
        "question": (
            "Did the fixed midpoint-objective stage itself produce a "
            "complete nominal policy before the full-transfer objective "
            "was reintroduced?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "frozen_inputs": {
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t63_transform": receipt(T63),
            "t64_preregistration": receipt(T64_PREREG),
            "t64_result": receipt(T64_RESULT),
        },
        "policy": {
            **receipt(POLICY),
            "checkpoint_id": "T62_MIDPOINT_FINAL",
            "stage": "midpoint_training",
            "step": 1_003_520,
            "selection_weight": 0,
            "promotion_eligible": False,
        },
        "fits": t64_prereg["fits"],
        "calibrator": t64_prereg["calibrator"],
        "reference_feature_table": t64_prereg["reference_feature_table"],
        "playground": t64_prereg["playground"],
        "commands_x_m_s": t64_prereg["commands_x_m_s"],
        "seed": t64_prereg["seed"],
        "conditions": t64_prereg["conditions"],
        "behavior_contract": t64_prereg["behavior_contract"],
        "protection_contract": t64_prereg["protection_contract"],
        "support_handoff": t64_prereg["support_handoff"],
        "matrix": {
            "cpu_only": True,
            "checkpoints": 1,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 8,
            "condition_must_complete": True,
            "diagnostic_only": True,
        },
        "decision_rule": {
            "pass": (
                "All 8 midpoint-endpoint cells pass the unchanged nominal "
                "behavior, tracking, rate, state-handoff, and duration "
                "contracts."
            ),
            "pass_decision": (
                "EARN_T66_FIXED_MIDPOINT_PERSISTENCE_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
            ),
            "no_checkpoint_selection": True,
            "no_policy_promotion": True,
            "no_hosted_training_authorization": True,
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "authority": {
            "execute_one_cpu_diagnostic": True,
            "t66_cpu_contract_preregistration": False,
            "training": False,
            "colab": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
