#!/usr/bin/env python3
"""Freeze the evidence-derived T156 positive-router boundary repair."""

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


T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T156 = ANALYSIS / "t156_three_way_positive_router_result.json"
OUTPUT = (
    ANALYSIS / "t156b_positive_router_gap_midpoint_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T156B_POSITIVE_ROUTER_GAP_MIDPOINT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t156b_positive_router_gap_midpoint.py"
TEST = ROOT / "tests" / "test_t156b_positive_router_gap_midpoint.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T156B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T156B preregistration requires clean worktree")

    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    t156 = json.loads(T156.read_text(encoding="utf-8"))
    source_graphs = {
        step: t156["graphs"][step]["transformed"]
        for step in ("1003520", "2007040")
    }
    references = {
        step: t156["positive_references"][step]["reference"]
        for step in ("1003520", "2007040")
    }
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t135b_result": T135B,
        "t156_result": T156,
    }
    checks = {
        "t156_hold_is_classifier_only": (
            t156["status"]
            == "HOLD_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
            and t156["decision"] == "CLOSE_POSITIVE_EXPERT_ROUTER"
            and set(t156["failed_checks"])
            == {
                "full_positive_classifier_exact",
                "leave_one_fit_out_classifier_exact",
            }
            and all(
                passed
                for name, passed in t156["checks"].items()
                if name not in t156["failed_checks"]
            )
        ),
        "strict_projected_class_gap_observed": (
            t156["classifier"][
                "positive_min_minus_nonpositive_max"
            ]
            > 0.0
        ),
        "two_positive_contexts_hash_exact": all(
            row["context_hash_exact"]
            for row in t156["positive_contexts"]
        ),
        "t135b_basis_green": (
            t135b["status"]
            == "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            and t135b["failed_checks"] == []
        ),
        "source_graphs_and_references_present": all(
            Path(item["path"]).is_file()
            for item in (*source_graphs.values(), *references.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen.values()
        ),
        "no_calibration_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T156B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t156b_positive_router_gap_midpoint_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
        ),
        "question": (
            "Does the unique midpoint of T156's strict projected "
            "class gap separate positive COM while changing only the "
            "router intercept?"
        ),
        "source_graphs": source_graphs,
        "positive_references": references,
        "boundary_rule": {
            "direction": (
                "unchanged T156 unit positive-centroid minus "
                "nonpositive-centroid direction"
            ),
            "maximum_nonpositive": (
                "maximum raw projection over four frozen "
                "nominal/negative contexts"
            ),
            "minimum_positive": (
                "minimum raw projection over two frozen +COM contexts"
            ),
            "boundary": (
                "(maximum_nonpositive + minimum_positive) / 2"
            ),
            "intercept": "-boundary cast once to float32",
            "required_full_labels": "all six exact",
            "required_leave_one_fit_out_labels": "all six exact",
            "scalar_search": False,
        },
        "graph_contract": {
            "only_initializer_allowed_to_change": (
                "positive_router_intercept"
            ),
            "all_nodes": "byte exact",
            "all_selected_source_outputs": "bit exact",
            "abi": "unchanged",
            "checkpoints": [1003520, 2007040],
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T157_POSITIVE_COM_ENDPOINT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_CALIBRATION_CONTEXT_POSITIVE_ROUTER"
            ),
        },
        "execution_now": {
            "calibration_prefixes": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_intercept_transform": True,
            "positive_endpoint_preregistration": False,
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
        "# T156B positive-router gap-midpoint preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Boundary: unique midpoint of T156's strict class gap\n"
        "- Allowed graph change: router intercept only\n"
        "- No scalar search or new calibration\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
