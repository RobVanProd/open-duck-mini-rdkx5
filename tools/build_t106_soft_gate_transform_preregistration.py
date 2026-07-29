#!/usr/bin/env python3
"""Freeze T106's exact continuous hidden-expert gate transform."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T101_RESULT = ANALYSIS / "t101_t100c_postexport_result.json"
T104_PREREG = ANALYSIS / "t104_t100c_gate_dynamics_preregistration.json"
T104_RESULT = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
T105_RESULT = ANALYSIS / "t105_two_frame_gate_result.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t106_soft_gate_transform.py"
TEST = ROOT / "tests" / "test_t106_soft_gate_transform.py"
OUTPUT = ANALYSIS / "t106_soft_gate_transform_preregistration.json"
MARKDOWN = ANALYSIS / "T106_SOFT_GATE_TRANSFORM_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T106 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T106 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T106 preregistration requires a clean worktree")

    t101 = json.loads(T101_RESULT.read_text(encoding="utf-8"))
    t104_prereg = json.loads(T104_PREREG.read_text(encoding="utf-8"))
    t104 = json.loads(T104_RESULT.read_text(encoding="utf-8"))
    t105 = json.loads(T105_RESULT.read_text(encoding="utf-8"))
    policies = {
        step: t101["deployments"][step]["wrapped"]
        for step in ("0", "1003520", "2007040")
    }
    repository_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t101_result": T101_RESULT,
        "t104_preregistration": T104_PREREG,
        "t104_result": T104_RESULT,
        "t105_result": T105_RESULT,
    }
    checks = {
        "t101_deployment_chain_green": (
            t101["status"] == "PASS_T101_T100C_POSTEXPORT_TRANSFORM"
            and t101["failed_checks"] == []
        ),
        "t104_proves_hard_gate_instability": (
            t104["status"] == "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
            and t104["classification"]
            == "HARD_GATE_DYNAMICS_INCONSISTENT"
        ),
        "t105_closes_stateless_two_frame_classification": (
            t105["status"] == "CLOSE_T105_TWO_FRAME_GATE_FALSIFIER"
            and t105["decision"]
            == "CLOSE_TWO_FRAME_STATELESS_GATE_STABILIZATION"
        ),
        "exact_three_deployment_graphs": len(policies) == 3,
        "all_policy_receipts_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies.values()
        ),
        "frozen_trace_population_available": (
            len(t104_prereg["traces"]) == 32
            and all(
                Path(item["trace"]["path"]).is_file()
                for item in t104_prereg["traces"]
            )
        ),
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t106_soft_gate_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T106_SOFT_GATE_TRANSFORM"
            if not failed
            else "HOLD_T106_SOFT_GATE_TRANSFORM_PREREGISTRATION"
        ),
        "question": (
            "Can T100C's learned negative expert be converted from an "
            "unstable classification branch into a continuous residual "
            "mixture without training or changing the policy ABI?"
        ),
        "policies": policies,
        "trace_population": t104_prereg["traces"],
        "transform": {
            "replace": (
                "Where(hidden_gate_score >= 0, "
                "negative_adapter_location, 0)"
            ),
            "with": (
                "negative_adapter_location * Sigmoid(hidden_gate_score)"
            ),
            "temperature": 1.0,
            "temperature_source": (
                "identity logistic map in the frozen standardized ridge "
                "score coordinate; no fitted or searched scalar"
            ),
            "reason": (
                "T105 proves the nominal and negative-COM score "
                "distributions overlap. The candidate therefore treats "
                "score ambiguity as continuous mixture weight rather than "
                "trying another classifier threshold."
            ),
            "new_input_or_output": False,
            "new_recurrent_state": False,
            "initializer_change": False,
            "action_protection_order_change": False,
            "scalar_search": False,
        },
        "contract": {
            "source_node_pattern": [
                {
                    "op_type": "GreaterOrEqual",
                    "input": ["hidden_gate_score", "hidden_gate_zero"],
                    "output": ["negative_com_gate"],
                },
                {
                    "op_type": "Where",
                    "input": [
                        "negative_com_gate",
                        "negative_adapter_location",
                        "zero_adapter_location",
                    ],
                    "output": ["conditional_adapter_location"],
                },
            ],
            "replacement_node_pattern": [
                {
                    "op_type": "Sigmoid",
                    "input": ["hidden_gate_score"],
                    "output": ["soft_negative_com_weight"],
                },
                {
                    "op_type": "Mul",
                    "input": [
                        "negative_adapter_location",
                        "soft_negative_com_weight",
                    ],
                    "output": ["conditional_adapter_location"],
                },
            ],
            "sample_ticks": [0, 8, 16, 32, 64, "last"],
            "maximum_formula_error": 1.0e-6,
            "maximum_step0_output_error": 1.0e-7,
            "maximum_x0_hard_vs_soft_output_error": 1.0e-7,
            "minimum_moving_postupdate_action_delta": 1.0e-6,
        },
        "decision_rule": {
            "pass": (
                "All three graph edits match the exact topology; graph ABI, "
                "initializers, recurrent output, deployment protections, "
                "step-0 behavior, x=0 behavior, and the analytic sigmoid "
                "mixture contract pass on the frozen trace sample; both "
                "postupdate graphs change moving actions materially."
            ),
            "pass_decision": (
                "EARN_T107_SOFT_GATE_NOMINAL_MATRIX_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T100C_CONTINUOUS_GATE_TRANSFORM",
            "training_selection_weight": 0,
            "no_behavior_or_training": True,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "graphs_transformed": 0,
            "behavior_cells": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_graph_transform": not failed,
            "nominal_preregistration": False,
            "behavior": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T106 continuous gate transform preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Exact transform: hard `Where` -> `head * sigmoid(score)`",
                "- Temperature/search/new state/new ABI: `1 / 0 / 0 / 0`",
                "- Behavior / training / Colab / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
