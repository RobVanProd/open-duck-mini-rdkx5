#!/usr/bin/env python3
"""Preregister read-only recovery of T247's two reporting assertions."""

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


T247 = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
OUTPUT = ANALYSIS / "t247b_reporting_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T247B_REPORTING_RECOVERY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t247b_reporting_recovery.py"
TEST = ROOT / "tests/test_t247b_reporting_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T247B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T247B preregistration requires clean worktree")
    source = json.loads(T247.read_text(encoding="utf-8"))
    trace = source["failed_final_trace_contract"]
    checks = {
        "t247_failed_only_two_reporting_assertions": (
            source["status"] == "HOLD_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE"
            and source["failed_checks"]
            == ["only_nominal_dynamic_input_changed", "random_contract_exact"]
            and all(
                passed
                for name, passed in source["checks"].items()
                if name
                not in {
                    "only_nominal_dynamic_input_changed",
                    "random_contract_exact",
                }
            )
        ),
        "random_equivalence_itself_is_exact": all(
            graph["inference"]["all_outputs_bit_exact"]
            and graph["inference"]["all_non_tail_exact_source"]
            and graph["inference"]["all_tail_exact_half_source"]
            and graph["inference"]["all_outputs_finite"]
            for graph in source["graphs"]
        ),
        "real_failed_trace_is_causally_sensitive": (
            trace["rows"] == 231
            and trace["source_replay_exact"]
            and trace["transformed_exact_half_source"]
            and trace["continuous_action_changed_rows"] == 24
            and trace["maximum_continuous_action_delta"] > 0.0
        ),
        "graphs_present_for_output_key_structural_audit": all(
            Path(graph["structure"][kind]["path"]).is_file()
            for graph in source["graphs"]
            for kind in ("source", "transformed")
        ),
        "zero_new_inference_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T247B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t247b_reporting_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T247B_REPORTING_RECOVERY",
        "question": (
            "Do output-key node comparison and real-trace sensitivity prove "
            "that T247's two failed assertions are reporting-only?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t247_result": receipt(T247),
        },
        "classification_rule": {
            "node_check": (
                "compare old nodes by unique output tuple because the target "
                "Where node has an empty name"
            ),
            "sensitivity_check": (
                "exact expected mapping plus nonzero real failed-trace "
                "sensitivity supersedes clipped random final-action equality"
            ),
            "new_inference": False,
            "selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "read_only_recovery": True,
            "behavior_matrix_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T247B reporting recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: unnamed-node comparison and synthetic sensitivity only\n"
        "- Real failed-trace changed rows: `24/231`\n"
        "- New inference/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
