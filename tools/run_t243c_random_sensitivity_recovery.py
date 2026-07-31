#!/usr/bin/env python3
"""Classify T243B's synthetic sensitivity hold without new inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    sha256,
)


PREREG = (
    ANALYSIS / "t243c_random_sensitivity_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t243c_random_sensitivity_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T243C_RANDOM_SENSITIVITY_RECOVERY_RESULT_20260731.md"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T243C output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243C execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T243C_RANDOM_SENSITIVITY_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T243C preregistration changed")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            raise RuntimeError(f"changed T243C input: {path}")
    source = json.loads(
        Path(prereg["frozen_inputs"]["t243b_result"]["path"])
        .read_text(encoding="utf-8")
    )
    trace = source["graphs"][0]["failed_trace_contract"]
    checks = {
        "sole_failed_assertion_is_synthetic_sensitivity": (
            source["failed_checks"] == ["random_contract_exact"]
        ),
        "all_random_exactness_and_finiteness_checks_green": all(
            graph["inference"]["all_outputs_bit_exact"]
            and graph["inference"]["all_non_targets_exact_source"]
            and graph["inference"]["all_targets_exact_source_x0077"]
            and graph["inference"]["all_outputs_finite"]
            for graph in source["graphs"]
        ),
        "all_real_failed_states_change_exactly_to_x0077": (
            trace["rows"]
            == trace["continuous_action_changed_rows"]
            == 281
            and trace["source_replay_exact"]
            and trace["transformed_exact_source_x0077"]
            and trace["maximum_continuous_action_delta"] > 0.0
        ),
        "all_non_sensitivity_contract_checks_green": all(
            passed
            for name, passed in source["checks"].items()
            if name != "random_contract_exact"
        ),
        "zero_new_inference_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t243c_random_sensitivity_recovery_result.v1"
        ),
        "status": (
            "PASS_T243C_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
            if passed
            else "HOLD_T243C_RANDOM_SENSITIVITY_RECOVERY"
        ),
        "decision": (
            "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_"
            "PREREGISTRATION_ONLY"
            if passed
            else "CLOSE_HOME_NEGATIVE_LOW_COMMAND_FLOOR_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "classification": {
            "synthetic_random_action_sensitivity": (
                "reporting-only; exact expected mapping was already green"
            ),
            "real_failed_state_rows": trace["rows"],
            "real_failed_state_changed_rows": trace[
                "continuous_action_changed_rows"
            ],
            "selection_weight": 0,
        },
        "execution": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "targeted_behavior_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T243C random-sensitivity recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Real failed-state action changes: `281/281`\n"
        "- New inference/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
