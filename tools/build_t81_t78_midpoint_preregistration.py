#!/usr/bin/env python3
"""Preregister the exact T78 half/final adapter midpoint falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T78_VALIDATION = ANALYSIS / "t78_recovered_training_validation.json"
T79_TRANSFORM = ANALYSIS / "t79_t78_postexport_result.json"
T80_RESULT = ANALYSIS / "t80_t78_nominal_matrix_result.json"
RUNNER = ROOT / "tools" / "run_t81_t78_midpoint_transform.py"
TEST = ROOT / "tests" / "test_t81_t78_midpoint_transform.py"
OUTPUT = ANALYSIS / "t81_t78_midpoint_preregistration.json"
MARKDOWN = ANALYSIS / "T81_T78_MIDPOINT_PREREGISTRATION_20260728.md"
EXPECTED_DIFFERING_INITIALIZERS = [
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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T81: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T81 preregistration requires a clean worktree")
    validation = json.loads(T78_VALIDATION.read_text(encoding="utf-8"))
    transform = json.loads(T79_TRANSFORM.read_text(encoding="utf-8"))
    nominal = json.loads(T80_RESULT.read_text(encoding="utf-8"))
    graphs = {
        int(row["step"]): row for row in validation["exports"]["onnx"]
    }
    half_path = Path(graphs[1_003_520]["path"])
    final_path = Path(graphs[2_007_040]["path"])
    failed_cells = []
    for block in nominal["blocks"]:
        for cell in block["result"]["cells"]:
            if not cell["cell_green"]:
                failed_cells.append(
                    {
                        "checkpoint_id": block["checkpoint_id"],
                        "fit_id": block["fit_id"],
                        "command_x_m_s": cell["command_x_m_s"],
                        "termination_reason": cell["behavior"][
                            "termination_reason"
                        ],
                        "samples": cell["behavior"]["samples"],
                    }
                )
    expected_failed = [
        {
            "checkpoint_id": "T78_JOINT_ADAPTER_HALF",
            "fit_id": "p31_34",
            "command_x_m_s": 0.08,
            "termination_reason": "fall_or_nan",
            "samples": 228,
        },
        {
            "checkpoint_id": "T78_JOINT_ADAPTER_FINAL",
            "fit_id": "p30",
            "command_x_m_s": 0.08,
            "termination_reason": "fall_or_nan",
            "samples": 502,
        },
    ]
    checks = {
        "t78_validation_green": (
            validation["status"]
            == "PASS_T78_RECOVERED_TRAINING_VALIDATION"
            and validation["failed_checks"] == []
        ),
        "t79_transform_green": (
            transform["status"] == "PASS_T79_T78_POSTEXPORT_TRANSFORM"
            and transform["failed_checks"] == []
        ),
        "t80_closed_at_exact_14_of_16": (
            nominal["status"] == "HOLD_T80_T78_NOMINAL_MATRIX"
            and nominal["decision"]
            == "CLOSE_T78_ENDPOINT_JOINT_ADAPTER_CONTINUATION"
            and nominal["condition"]["green_cells"] == 14
            and nominal["condition"]["cells"] == 16
        ),
        "complementary_x008_failure_pair_exact": (
            failed_cells == expected_failed
        ),
        "raw_half_and_final_exact": (
            sha256(half_path) == graphs[1_003_520]["sha256"]
            and sha256(final_path) == graphs[2_007_040]["sha256"]
        ),
        "runner_and_test_present": RUNNER.is_file() and TEST.is_file(),
        "zero_scalar_or_checkpoint_search": True,
        "behavior_not_run": True,
        "hosted_robot_and_gate5_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t81_t78_midpoint_preregistration.v1",
        "status": (
            "PREREGISTERED_T81_T78_EXACT_ADAPTER_MIDPOINT"
            if not failed
            else "HOLD_T81_T78_EXACT_ADAPTER_MIDPOINT"
        ),
        "question": (
            "Does the exact arithmetic midpoint of T78 half/final's five "
            "trainable adapter initializers form a valid deployment graph, "
            "justifying a two-cell crossover falsifier without training?"
        ),
        "causal_basis": {
            "green_cells": 14,
            "failed_cells": failed_cells,
            "interpretation": (
                "half and final fail only x=.08 under opposite actuator fits"
            ),
            "candidate_status": (
                "diagnostic only; midpoint does not satisfy persistence"
            ),
        },
        "sources": {
            "half_raw": receipt(half_path),
            "final_raw": receipt(final_path),
            "t78_validation": receipt(T78_VALIDATION),
            "t79_transform": receipt(T79_TRANSFORM),
            "t80_result": receipt(T80_RESULT),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
        },
        "transform": {
            "initializers": EXPECTED_DIFFERING_INITIALIZERS,
            "formula": (
                "float32((float64(half) + float64(final)) * 0.5)"
            ),
            "all_other_initializers_bit_exact": True,
            "graph_structure_bit_exact_to_half": True,
            "deployment_chain": "exact frozen T31/T79 chain",
            "coefficient": 0.5,
            "coefficient_selected_by": (
                "symmetry of the exact complementary endpoint failures"
            ),
            "coefficient_sweep": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Exactly five expected initializers differ; midpoint values "
                "match the frozen formula; every graph/deployment sub-contract "
                "passes with no behavior execution."
            ),
            "pass_decision": (
                "EARN_T82_TWO_CELL_MIDPOINT_CROSSOVER_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_EXACT_T78_ADAPTER_MIDPOINT",
            "candidate_promotion": False,
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
            "behavior_preregistration": False,
            "behavior_execution": False,
            "training": False,
            "colab": False,
            "checkpoint_selection": False,
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
                "# T81 T78 exact adapter midpoint preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Basis: `14/16`, complementary x=.08 crossover",
                "- Transform: exact 0.5 midpoint of five adapter initializers",
                "- Coefficient search: `none`",
                "- Behavior/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "- Candidate status: `diagnostic only`",
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
