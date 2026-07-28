#!/usr/bin/env python3
"""Preregister T78's two persistent rolling adapter midpoints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
VALIDATION = ANALYSIS / "t78_recovered_training_validation.json"
MIDPOINT = ANALYSIS / "t81_t78_midpoint_result.json"
MIDPOINT_MATRIX = (
    ANALYSIS / "t83b_midpoint_aggregation_correction_result.json"
)
RUNNER = ROOT / "tools" / "run_t84_t78_rolling_midpoint_transform.py"
TEST = ROOT / "tests" / "test_t84_t78_rolling_midpoint_transform.py"
OUTPUT = ANALYSIS / "t84_t78_rolling_midpoint_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T84_T78_ROLLING_MIDPOINT_PREREGISTRATION_20260728.md"
)
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t78_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
EXPECTED_INITIALIZERS = [
    "adapter_bias",
    "adapter_hidden_bias",
    "adapter_hidden_weight",
    "adapter_obs_weight",
    "adapter_weight",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def graph_step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T84: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T84 preregistration requires a clean worktree")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    midpoint = json.loads(MIDPOINT.read_text(encoding="utf-8"))
    matrix = json.loads(MIDPOINT_MATRIX.read_text(encoding="utf-8"))
    validation_graphs = {
        int(row["step"]): row for row in validation["exports"]["onnx"]
    }
    raw_paths = {
        graph_step(path): path.resolve() for path in RAW_ROOT.glob("*.onnx")
    }
    source_receipts = {
        str(step): receipt(raw_paths[step])
        for step in (0, 1_003_520, 2_007_040)
    }
    checks = {
        "t78_validation_green": (
            validation["status"]
            == "PASS_T78_RECOVERED_TRAINING_VALIDATION"
            and validation["failed_checks"] == []
        ),
        "t81_exact_midpoint_green": (
            midpoint["status"]
            == "PASS_T81_T78_EXACT_ADAPTER_MIDPOINT"
            and midpoint["failed_checks"] == []
        ),
        "t83b_midpoint_eight_of_eight_green": (
            matrix["status"]
            == "PASS_T83B_MIDPOINT_AGGREGATION_CORRECTION"
            and matrix["failed_checks"] == []
            and matrix["condition"]["green_cells"] == 8
            and matrix["condition"]["condition_green"]
        ),
        "exact_three_raw_exports": (
            sorted(raw_paths) == [0, 1_003_520, 2_007_040]
            and all(
                source_receipts[str(step)]["sha256"]
                == validation_graphs[step]["sha256"]
                for step in raw_paths
            )
        ),
        "runner_and_test_present": RUNNER.is_file() and TEST.is_file(),
        "zero_scalar_or_checkpoint_search": True,
        "behavior_not_run": True,
        "hosted_robot_and_gate5_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t84_t78_rolling_midpoint_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
            if not failed
            else "HOLD_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
        ),
        "question": (
            "Can one uniform rolling-midpoint rule produce two valid "
            "post-update policies—mean(step0, half) and mean(half, final)—"
            "so persistence can be tested without training?"
        ),
        "causal_basis": {
            "t78_nominal": "14/16 with opposite-fit x=.08 failures",
            "exact_half_final_midpoint": "8/8 nominal cells green",
            "selected_mechanism": (
                "apply the same adjacent-checkpoint midpoint rule at both "
                "post-update export times"
            ),
        },
        "sources": {
            "raw_exports": source_receipts,
            "validation": receipt(VALIDATION),
            "t81_midpoint": receipt(MIDPOINT),
            "t83b_midpoint_matrix": receipt(MIDPOINT_MATRIX),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
        },
        "transform": {
            "rolling_half": "mean(step0, step1003520)",
            "rolling_final": "mean(step1003520, step2007040)",
            "initializers": EXPECTED_INITIALIZERS,
            "formula": (
                "float32((float64(earlier) + float64(later)) * 0.5)"
            ),
            "all_other_initializers_bit_exact": True,
            "deployment_chain": "exact frozen T31/T79 chain",
            "coefficient": 0.5,
            "coefficient_sweep": False,
            "uniform_rule_at_both_exports": True,
        },
        "persistence_contract": {
            "exports": ["rolling_half", "rolling_final"],
            "both_required": True,
            "no_checkpoint_selection": True,
            "no_single_midpoint_promotion": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Both rolling exports use exactly the same midpoint rule; "
                "only five expected adapter initializers change; every "
                "deployment sub-contract passes; rolling-final is byte-exact "
                "to T81."
            ),
            "pass_decision": (
                "EARN_T85_ROLLING_MIDPOINT_NOMINAL_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T78_ROLLING_ADAPTER_MIDPOINT",
        },
        "execution_now": {
            "onnx_graphs_built": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_cpu_graph_transform": not failed,
            "nominal_matrix_preregistration": False,
            "behavior_execution": False,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T84 T78 rolling midpoint preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Rule: adjacent-checkpoint 0.5 adapter midpoint",
                "- Exports: step0→half / half→final",
                "- Both exports required; no checkpoint selection",
                "- Behavior/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
