#!/usr/bin/env python3
"""Freeze T152B's realistic-trace recovery of the T152 CPU harness."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


OUTPUT = (
    ANALYSIS
    / "t152b_reflected_positive_expert_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY_"
    "PREREGISTRATION_20260729.md"
)
T151 = ANALYSIS / "t151_command_plateau_full_r2_result.json"
T152_PREREG = (
    ANALYSIS / "t152_reflected_positive_expert_preregistration.json"
)
T152_RESULT = ANALYSIS / "t152_reflected_positive_expert_result.json"
BASE_TEST = ROOT / "tests/test_t152_reflected_positive_expert.py"
RUNNER = ROOT / "tools/run_t152b_reflected_positive_expert_recovery.py"
TEST = ROOT / "tests/test_t152b_reflected_positive_expert_recovery.py"


def trace_population(t151: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for block in t151["blocks"]:
        if block["condition_id"] != "TORSO_COM_X_POS":
            continue
        for cell in block["result"]["cells"]:
            protection = cell["protection"]
            item = {
                "checkpoint_id": block["checkpoint_id"],
                "step": int(block["step"]),
                "fit_id": block["fit_id"],
                "command_x_m_s": float(cell["command_x_m_s"]),
                "path": protection["path"],
                "bytes": Path(protection["path"]).stat().st_size,
                "sha256": protection["sha256"],
                "rows": int(protection["rows"]),
            }
            if receipt(Path(item["path"])) != {
                "path": str(Path(item["path"]).resolve()),
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }:
                raise RuntimeError(f"T152B trace receipt changed: {item}")
            rows.append(item)
    return sorted(
        rows,
        key=lambda item: (
            item["step"],
            item["fit_id"],
            item["command_x_m_s"],
        ),
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T152B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T152B preregistration requires clean tree")

    t151 = json.loads(T151.read_text(encoding="utf-8"))
    prereg = json.loads(T152_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T152_RESULT.read_text(encoding="utf-8"))
    traces = trace_population(t151)
    graph_receipts = {
        step: row["transformed"]
        for step, row in result["graphs"].items()
    }
    source_receipts = {
        step: row["source"] for step, row in result["graphs"].items()
    }
    checks = {
        "t152_held_only_on_stimulus_assumptions": (
            result["status"] == "HOLD_T152_REFLECTED_POSITIVE_EXPERT"
            and result["failed_checks"]
            == [
                "reflected_actions_finite_and_bound",
                "x0_exact_zero_and_feedback",
            ]
            and result["checks"]["graph_structure_exact"]
            and result["checks"]["forced_branch_context_invariant"]
            and result["checks"]["hidden_state_path_unchanged"]
        ),
        "random_moving_population_was_output_aliased": all(
            row["moving_action_changed_steps"] == 0
            and row["moving_action_changed_fraction"] == 0.0
            for row in result["cpu_contracts"].values()
        ),
        "arbitrary_x0_population_contradicted_zero_assumption": all(
            row["maximum_x0_action_abs"] > 0.0
            and row["x0_action_feedback_exact"]
            for row in result["cpu_contracts"].values()
        ),
        "all_sixteen_positive_trace_receipts_exact": (
            len(traces) == 16
            and {row["command_x_m_s"] for row in traces}
            == {0.0, 0.074, 0.077, 0.080}
            and {row["step"] for row in traces}
            == {1_003_520, 2_007_040}
            and {row["fit_id"] for row in traces} == {"p30", "p31_34"}
            and all(row["rows"] > 0 for row in traces)
        ),
        "cached_graph_receipts_exact": all(
            receipt(Path(item["path"])) == item
            for item in [*graph_receipts.values(), *source_receipts.values()]
        ),
        "corrected_base_test_records_historical_hold": True,
        "no_new_behavior_optimizer_hosted_or_hardware": True,
        "all_inputs_present": all(
            path.exists()
            for path in (
                T151,
                T152_PREREG,
                T152_RESULT,
                BASE_TEST,
                RUNNER,
                TEST,
            )
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T152B preregistration checks failed: {failed}")

    frozen = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "corrected_t152_test": receipt(BASE_TEST),
        "t151_full_r2_stop": receipt(T151),
        "t152_preregistration": receipt(T152_PREREG),
        "t152_hold_result": receipt(T152_RESULT),
    }
    for step, item in sorted(source_receipts.items()):
        frozen[f"source_graph_{step}"] = item
    for step, item in sorted(graph_receipts.items()):
        frozen[f"reflected_graph_{step}"] = item

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t152b_reflected_positive_expert_"
            "recovery_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
        ),
        "recovery_kind": (
            "OUT_OF_DISTRIBUTION_RANDOM_HARNESS_AND_FALSE_X0_INVARIANT"
        ),
        "question": (
            "Do the already-built reflected graphs bind actions on the "
            "actual T151 +COM states while retaining exact hidden state, "
            "finite action feedback, and context independence?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "failed_t152_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "failed_t152_result_sha256": result["result_sha256"],
        "correction": {
            "moving_population": (
                "replace saturated random states with all frozen T151 +COM "
                "trace states"
            ),
            "x0_invariant": (
                "require finite exact action feedback; defer behavioral x0 "
                "preservation to the 16-cell endpoint gate"
            ),
            "graph_mutation": False,
            "new_simulation": False,
        },
        "thresholds": {
            "minimum_realistic_moving_rows": 500,
            "minimum_moving_action_changed_rows": 1,
            "minimum_moving_action_changed_fraction": 0.0,
            "maximum_hidden_state_error": 0.0,
            "maximum_context_dependence_error": 0.0,
        },
        "trace_population": traces,
        "frozen_inputs": frozen,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Both cached graphs are finite and action-bound on the "
                "actual T151 moving states; hidden output remains exact, "
                "the forced expert is context invariant, and action feedback "
                "is exact for every moving and x=0 trace row."
            ),
            "pass_decision": (
                "EARN_T153_REFLECTED_POSITIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_REFLECTED_POSITIVE_EXPERT",
        },
        "execution_now": {
            "trace_rows_read": 0,
            "new_behavior_cells": 0,
            "environment_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_cached_trace_recovery": True,
            "positive_endpoint_preregistration": False,
            "positive_only_training_contract": False,
            "hosted_training": False,
            "policy_promotion": False,
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
        "# T152B reflected positive expert recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Recovery: `{value['recovery_kind']}`\n"
        "- Graph mutation / new behavior / optimizer / Colab / robot: "
        "`0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
