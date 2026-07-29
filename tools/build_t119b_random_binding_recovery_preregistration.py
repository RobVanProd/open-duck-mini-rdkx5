#!/usr/bin/env python3
"""Freeze a read-only recovery for T119's auxiliary random-input hold."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT))

from tools import (  # noqa: E402
    build_t119_joint_soft_router_cpu_preregistration as common,
)
OUTPUT = ANALYSIS / "t119b_random_binding_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T119B_RANDOM_BINDING_RECOVERY_PREREGISTRATION_20260729.md"
)
T119_PREREG = ANALYSIS / "t119_joint_soft_router_cpu_preregistration.json"
T119_RESULT = ANALYSIS / "t119_joint_soft_router_cpu_result.json"
SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t119b_random_binding_recovery.py",
    "test": ROOT / "tests" / "test_t119b_random_binding_recovery.py",
    "t119_preregistration": T119_PREREG,
    "t119_result": T119_RESULT,
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T119B prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T119B preregistration requires clean tree")

    prereg = json.loads(T119_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T119_RESULT.read_text(encoding="utf-8"))
    initial_graph = Path(result["training"]["graphs"]["0"]["receipt"]["path"])
    final_graph = Path(
        result["training"]["graphs"]["1024"]["receipt"]["path"]
    )
    checks = {
        "original_contract_held_only_auxiliary_random_binding": (
            result["status"] == "HOLD_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT"
            and result["failed_checks"] == ["random_action_and_router_binding"]
        ),
        "primary_trace_populations_pass": (
            result["checks"]["nominal_population_action_and_router_binding"]
            and result["checks"][
                "negative_population_action_and_router_binding"
            ]
            and result["causal_contract"]["postupdate_trace"]["nominal"][
                "raw_changed_rows"
            ]
            == 36
            and result["causal_contract"]["postupdate_trace"]["negative_com"][
                "raw_changed_rows"
            ]
            == 36
        ),
        "router_changed_on_auxiliary_population": (
            result["causal_contract"]["postupdate_random"][
                "maximum_router_weight_delta"
            ]
            > prereg["thresholds"]["minimum_router_weight_delta"]
        ),
        "all_structural_training_checks_pass": all(
            result["checks"][name]
            for name in (
                "all_trainable_actor_leaves_changed",
                "protected_mature_actor_bit_exact",
                "normalizer_bit_exact",
                "every_critic_leaf_changed",
                "step_zero_trace_exact",
                "step_zero_random_chain_exact",
                "graph_abi_and_cpu_chain_exact",
            )
        ),
        "frozen_graphs_present": initial_graph.is_file()
        and final_graph.is_file(),
        "no_new_optimizer_simulator_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T119B preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t119b_random_binding_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T119B_READ_ONLY_BINDING_RECOVERY",
        "question": (
            "Did the auxiliary synthetic check miss a real learned route "
            "because unconstrained random observations drive the tanh policy "
            "outside the frozen trace support and into saturation?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "scope": {
            "immutable_t119_training": True,
            "same_256_random_feeds": True,
            "new_graph_outputs_only": [
                "anchored_location",
                "raw_continuous_actions",
                "soft_negative_com_weight",
            ],
            "trace_population": "same_frozen_72_rows",
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "thresholds": {
            "minimum_out_of_trace_support_random_row_fraction": 0.90,
            "raw_saturation_abs": 0.999999,
            "minimum_initial_raw_saturated_element_fraction": 0.90,
            "minimum_jointly_changed_random_rows": 1,
            "minimum_router_weight_delta": 1.0e-7,
            "minimum_anchored_location_delta": 1.0e-7,
        },
        "sources": {
            name: common.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "initial_graph": common.file_receipt(initial_graph),
            "final_graph": common.file_receipt(final_graph),
            "t97_preregistration": prereg["assets"][
                "t97_preregistration"
            ],
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "At least 90% of synthetic rows are outside the per-feature "
                "frozen trace envelope; at least 90% of initial raw-action "
                "elements are tanh-saturated; the learned router and "
                "pre-tanh anchored location both change on at least one of "
                "those same rows; and the already frozen nominal/negative "
                "trace checks remain green."
            ),
            "pass_decision": (
                "RECOVER_T119_CPU_CONTRACT_AND_EARN_T120_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CONFIRM_CLOSE_JOINT_SOFT_ROUTER_TRAINTHROUGH",
            "cannot_modify_original_t119_result": True,
        },
        "authority": {
            "execute_read_only_recovery": True,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = common.canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T119B read-only random-binding recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Original T119 result remains an immutable formal hold",
                "- Recovery reads the exact two frozen ONNX graphs",
                "- Optimizer / simulator / behavior / hosted / robot: "
                "`0/0/0/0/0`",
                "",
                "A pass can recover only the CPU-contract decision.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
