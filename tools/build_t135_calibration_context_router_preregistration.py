#!/usr/bin/env python3
"""Freeze automatic calibration-context routing screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T134 = ANALYSIS / "t134_t129_nominal_gate_attribution_result.json"
T132_PREREG = ANALYSIS / "t132_t129_nominal_preregistration.json"
T132_RESULT = ANALYSIS / "t132b_interrupted_nominal_recovery_result.json"
T12_RESULT = ANALYSIS / "t12_response_prefix_com_result.json"
OUTPUT = ANALYSIS / "t135_calibration_context_router_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T135_CALIBRATION_CONTEXT_ROUTER_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t135_calibration_context_router_screen.py"
TEST = ROOT / "tests" / "test_t135_calibration_context_router.py"
EVALUATOR = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"


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


def block_contexts(result: dict[str, Any]) -> dict[str, str]:
    return {
        block["fit_id"]: block["cells"][0]["handoff"]["context_sha256"]
        for block in result["blocks"]
        if block["checkpoint_id"].endswith("HALF")
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T135: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T135 preregistration requires clean worktree")

    t134 = json.loads(T134.read_text(encoding="utf-8"))
    t132_prereg = json.loads(T132_PREREG.read_text(encoding="utf-8"))
    t132_result = json.loads(T132_RESULT.read_text(encoding="utf-8"))
    t12 = json.loads(T12_RESULT.read_text(encoding="utf-8"))
    nominal_hashes = {
        block["fit_id"]: block["result"]["cells"][0]["handoff"][
            "context_sha256"
        ]
        for block in t132_result["blocks"]
        if block["checkpoint_id"].endswith("HALF")
    }
    negative_hashes = {
        block["fit_id"]: block["cells"][0]["handoff"]["context_sha256"]
        for block in t12["blocks"]
        if block["checkpoint_id"].endswith("HALF")
    }
    expected_context_hashes = {
        fit_id: {
            "nominal": nominal_hashes[fit_id],
            "com_x_negative": negative_hashes[fit_id],
        }
        for fit_id in sorted(nominal_hashes)
    }
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "evaluator": EVALUATOR,
        "t134_result": T134,
        "t132_preregistration": T132_PREREG,
        "t132_result": T132_RESULT,
        "t12_negative_result": T12_RESULT,
    }
    checks = {
        "t134_selects_static_context_screen": (
            t134["status"]
            == "PASS_T134_T129_NOMINAL_GATE_ATTRIBUTION"
            and t134["decision"]
            == "EARN_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN_"
            "PREREGISTRATION_ONLY"
        ),
        "two_fits_have_distinct_condition_hashes": (
            set(nominal_hashes) == {"p30", "p31_34"}
            and set(negative_hashes) == {"p30", "p31_34"}
            and all(
                nominal_hashes[fit_id] != negative_hashes[fit_id]
                for fit_id in nominal_hashes
            )
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T135 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t135_calibration_context_router_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
        ),
        "question": (
            "Does the existing 250-tick automatic calibration context "
            "separate nominal from exact negative torso COM across both "
            "measured actuator fits without locomotion selection?"
        ),
        "fits": t132_prereg["fits"],
        "populations": [
            {
                "id": "nominal",
                "override": {"torso_com_offset_m": [0.0, 0.0, 0.0]},
            },
            {
                "id": "com_x_negative",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            },
        ],
        "expected_context_hashes": expected_context_hashes,
        "command_x_m_s": 0.074,
        "seed": t132_prereg["seed"],
        "calibrator": t132_prereg["calibrator"],
        "reference_feature_table": t132_prereg[
            "reference_feature_table"
        ],
        "playground": t132_prereg["playground"],
        "thresholds": {
            "minimum_full_margin": 0.0,
            "minimum_leave_one_fit_out_margin": 0.0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_STATIC_CALIBRATION_CONTEXT_ROUTER",
        },
        "execution_now": {
            "calibration_prefixes": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_calibration_context_screen": True,
            "static_router_transform_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T135 calibration-context router preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Four calibration-only prefixes: 2 fits x nominal/negative COM\n"
        "- Required: prior hashes and leave-one-fit-out separation\n"
        "- Formal locomotion / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
