#!/usr/bin/env python3
"""Preregister read-only recovery of T243B's synthetic sensitivity check."""

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


T243B = ANALYSIS / "t243b_abi_helper_recovery_result.json"
OUTPUT = (
    ANALYSIS
    / "t243c_random_sensitivity_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T243C_RANDOM_SENSITIVITY_RECOVERY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t243c_random_sensitivity_recovery.py"
TEST = ROOT / "tests/test_t243c_random_sensitivity_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T243C preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243C preregistration requires clean worktree")
    source = json.loads(T243B.read_text(encoding="utf-8"))
    trace = source["graphs"][0]["failed_trace_contract"]
    checks = {
        "t243b_sole_failure_is_random_sensitivity": (
            source["status"] == "HOLD_T243B_ABI_HELPER_RECOVERY"
            and source["failed_checks"] == ["random_contract_exact"]
            and all(
                passed
                for name, passed in source["checks"].items()
                if name != "random_contract_exact"
            )
        ),
        "random_mapping_equivalence_itself_is_exact": all(
            graph["inference"]["all_outputs_bit_exact"]
            and graph["inference"]["all_non_targets_exact_source"]
            and graph["inference"]["all_targets_exact_source_x0077"]
            and graph["inference"]["all_outputs_finite"]
            and graph["inference"]["provider"] == "CPUExecutionProvider"
            and graph["inference"]["target_rows"] == 2
            for graph in source["graphs"]
        ),
        "real_failed_state_population_is_fully_sensitive": (
            trace["rows"] == 281
            and trace["source_replay_exact"]
            and trace["transformed_exact_source_x0077"]
            and trace["continuous_action_changed_rows"] == 281
            and trace["maximum_continuous_action_delta"] > 0.0
            and trace["all_outputs_finite"]
        ),
        "graph_structure_and_abi_checks_green": all(
            source["checks"][name]
            for name in (
                "all_initializers_byte_exact",
                "exactly_one_partial_graph_reused",
                "only_expected_nodes_added",
                "only_expected_old_nodes_changed",
                "onnx_checker_passes",
                "partial_graph_receipt_unchanged",
                "stateful_abi_exact",
                "two_complete_graphs",
            )
        ),
        "zero_new_inference_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T243C preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t243c_random_sensitivity_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T243C_RANDOM_SENSITIVITY_RECOVERY",
        "question": (
            "Is T243B's sole failed assertion noncausal because its random "
            "rows already prove exact branch mapping while every one of the "
            "281 real failed-state rows changes action?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t243b_result": receipt(T243B),
        },
        "classification_rule": {
            "pass": (
                "sole failure is synthetic action sensitivity; exact "
                "mapping, structure, ABI, finite outputs, and all 281 real "
                "failed-state sensitivities are green"
            ),
            "fail": "close low-command floor without behavior",
            "selection_weight": 0,
            "new_inference": False,
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
            "read_only_classification": True,
            "targeted_behavior_preregistration": False,
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
        "# T243C random-sensitivity recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: read-only classification of one synthetic assertion\n"
        "- Real failed-state sensitivity: `281/281`\n"
        "- Inference/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
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
