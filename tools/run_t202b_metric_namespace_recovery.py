#!/usr/bin/env python3
"""Run T202B's immutable event-file metric-namespace recovery."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
from run_t55_dynamic_single_support_cpu_contract import all_scalar_events


PREREG = ANALYSIS / "t202b_metric_namespace_recovery_preregistration.json"
RESULT = ANALYSIS / "t202b_metric_namespace_recovery_result.json"
MARKDOWN = ANALYSIS / "T202B_METRIC_NAMESPACE_RECOVERY_RESULT_20260730.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T202B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T202B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T202B_METRIC_NAMESPACE_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T202B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    t202 = json.loads(
        Path(prereg["frozen_inputs"]["t202_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    event_path = Path(prereg["frozen_inputs"]["event_file"]["path"])
    events = all_scalar_events(event_path)
    tags = prereg["expected_tags"]
    values = {
        name: [float(row["value"]) for row in events.get(tag, [])]
        for name, tag in tags.items()
    }
    checks = {
        "all_four_actual_tags_have_two_events": all(
            len(item) == 2 for item in values.values()
        ),
        "all_actual_values_finite": all(
            math.isfinite(item)
            for rows in values.values()
            for item in rows
        ),
        "cost_and_excess_are_positive": (
            bool(values["cost"])
            and bool(values["excess"])
            and max(values["cost"]) > 0.0
            and max(values["excess"]) > 0.0
        ),
        "anticipated_reward_namespace_is_absent": all(
            tag not in events
            for tag in prereg["anticipated_but_absent_tags"]
        ),
        "t202_only_failed_reporting_check": (
            t202["failed_checks"]
            == ["training_roll_risk_metrics_finite"]
            and all(
                value
                for name, value in t202["checks"].items()
                if name != "training_roll_risk_metrics_finite"
            )
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    reporting_only = not failed
    decision = (
        prereg["decision_rule"]["reporting_only_decision"]
        if reporting_only
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t202b_metric_namespace_recovery_result.v1"
        ),
        "status": (
            "PASS_T202B_METRIC_NAMESPACE_RECOVERY"
            if reporting_only
            else "HOLD_T202B_METRIC_NAMESPACE_RECOVERY"
        ),
        "classification": (
            "T202_CPU_HOLD_WAS_REPORTING_NAMESPACE_ONLY"
            if reporting_only
            else "T202_CPU_HOLD_WAS_NOT_REPORTING_ONLY"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "tag_values": values,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "event_files_read": 1,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": reporting_only,
            "hosted_training": False,
            "behavior": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T202B metric-namespace recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Cost events: `{values['cost']}`\n"
        f"- Excess events: `{values['excess']}`\n"
        "- Simulator/optimizer/behavior/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if reporting_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
