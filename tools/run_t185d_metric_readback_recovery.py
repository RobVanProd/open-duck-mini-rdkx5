#!/usr/bin/env python3
"""Run T185D's immutable-event metric-readback recovery."""

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
)
import run_t20_support_trainthrough_one_update as t20
import run_t55_dynamic_single_support_cpu_contract as t55


PREREG = (
    ANALYSIS / "t185d_metric_readback_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t185d_metric_readback_recovery_result.json"
MARKDOWN = ANALYSIS / "T185D_METRIC_READBACK_RECOVERY_RESULT_20260730.md"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def finite_values(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> list[float]:
    values = [float(row["value"]) for row in events.get(tag, [])]
    if not values or not all(math.isfinite(value) for value in values):
        return []
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-artifact-authorized", action="store_true")
    parser.add_argument("--preregistration", type=Path, default=PREREG)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if not args.saved_artifact_authorized:
        raise PermissionError("T185D requires --saved-artifact-authorized")
    preregistration_path = args.preregistration.resolve()
    result_path = args.result.resolve()
    markdown_path = args.markdown.resolve()
    for path in (result_path, markdown_path):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T185D: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T185D execution requires clean worktree")

    prereg = load(preregistration_path)
    if (
        prereg["status"]
        not in (
            "PREREGISTERED_T185D_METRIC_READBACK_RECOVERY",
            "PREREGISTERED_T185E_METRIC_RECEIPT_RECOVERY",
            "PREREGISTERED_T185F_METRIC_RUNNER_PATH_RECOVERY",
        )
        or canonical_without(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T185D preregistration identity changed")
    result_label = {
        "PREREGISTERED_T185D_METRIC_READBACK_RECOVERY": "T185D",
        "PREREGISTERED_T185E_METRIC_RECEIPT_RECOVERY": "T185E",
        "PREREGISTERED_T185F_METRIC_RUNNER_PATH_RECOVERY": "T185F",
    }[prereg["status"]]
    for name, item in prereg["sources"].items():
        t20.verify_receipt(item, name)
    source = load(Path(prereg["sources"]["t185c_result"]["path"]))
    event_path = Path(prereg["sources"]["event_file"]["path"])
    events = t55.all_scalar_events(event_path)
    contract = prereg["saved_artifact_contract"]
    support_values = {
        tag: finite_values(events, tag)
        for tag in contract["support_tags"]
    }
    prefix_values = finite_values(
        events, contract["terminal_prefix_tag"]
    )
    original_values = finite_values(
        events, contract["same_episode_reward_tag"]
    )
    substantive = {
        name: passed
        for name, passed in source["checks"].items()
        if name != "training_metrics_finite_and_prefix_exercised"
    }
    checks = {
        "source_result_hash_exact": (
            canonical_without(source, "result_sha256")
            == source["result_sha256"]
        ),
        "source_only_metric_readback_held": (
            source["failed_checks"]
            == ["training_metrics_finite_and_prefix_exercised"]
        ),
        "all_other_t185c_checks_true": all(substantive.values()),
        "support_metrics_finite_positive_at_both_evaluations": all(
            len(values) == 2 and min(values) > 0.0
            for values in support_values.values()
        ),
        "terminal_prefix_state_finite_zero_at_both_evaluations": (
            len(prefix_values) == 2
            and all(value == 0.0 for value in prefix_values)
        ),
        "original_reward_finite_positive_at_both_evaluations": (
            len(original_values) == 2 and min(original_values) > 0.0
        ),
        "incorrect_metric_tag_absent": (
            contract["incorrect_tag_must_be_absent"] not in events
        ),
        "no_new_simulator_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis: dict[str, Any] = {
        "schema_version": (
            (
                "open_duck.t185f_metric_runner_path_recovery_result.v1"
                if result_label == "T185F"
                else (
                    "open_duck.t185e_metric_receipt_recovery_result.v1"
                    if result_label == "T185E"
                    else "open_duck.t185d_metric_readback_recovery_result.v1"
                )
            )
        ),
        "status": (
            f"PASS_{result_label}_METRIC_READBACK_RECOVERY"
            if passed
            else f"HOLD_{result_label}_METRIC_READBACK_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_result_sha256": source["result_sha256"],
        "observed": {
            "support_metric_values": support_values,
            "terminal_prefix_values": prefix_values,
            "original_reward_values": original_values,
            "event_scalar_tag_count": len(events),
            "event_scalar_row_count": sum(
                len(values) for values in events.values()
            ),
        },
        "preserved_t185c_checks": substantive,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_event_files": 1,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    result_path.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        f"# {result_label} metric-readback recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- Terminal prefix values: `{prefix_values}`\n"
        "- New simulator / optimizer / behavior / hosted / robot: "
        "`0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
