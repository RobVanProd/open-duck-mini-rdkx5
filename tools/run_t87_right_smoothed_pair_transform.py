#!/usr/bin/env python3
"""Build and verify T87's exact right-smoothed adapter pair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
from run_t84_t78_rolling_midpoint_transform import (  # noqa: E402
    build_midpoint,
    deployment_contract,
)


PREREG = ANALYSIS / "t87_right_smoothed_pair_preregistration.json"
T84_RESULT = ANALYSIS / "t84_t78_rolling_midpoint_result.json"
RESULT = ANALYSIS / "t87_right_smoothed_pair_result.json"
MARKDOWN = ANALYSIS / "T87_RIGHT_SMOOTHED_PAIR_RESULT_20260728.md"


def verify_receipt(item: dict[str, Any], label: str) -> None:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(item["bytes"])
        or t20.sha256(path) != item["sha256"]
    ):
        raise ValueError(f"T87 frozen receipt changed: {label}")


def verify_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"]
        != "PREREGISTERED_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
        or value["failed_checks"] != []
        or t20.canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise ValueError("T87 preregistration changed")
    for name, item in value["sources"].items():
        verify_receipt(item, name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T87 transform requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T87: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    t84 = json.loads(T84_RESULT.read_text(encoding="utf-8"))
    work = args.work_root.resolve()
    work.mkdir(parents=True)

    source_half = t84["policies"]["rolling_half"]
    source_final = t84["policies"]["rolling_final"]
    half_raw = Path(source_half["raw"]["path"])
    final_raw = Path(source_final["raw"]["path"])
    verify_receipt(source_half["raw"], "t84:rolling_half_raw")
    verify_receipt(source_final["raw"], "t84:rolling_final_raw")
    verify_receipt(source_final["wrapped"], "t84:rolling_final_wrapped")

    smoothed_half = build_midpoint(
        half_raw,
        final_raw,
        prereg["transform"]["initializers"],
        work / "right_smoothed_half_raw.onnx",
    )
    half_deployment = t31.deployment_graph(
        smoothed_half["path"],
        work / "right_smoothed_half",
    )
    final_raw_exact = (
        t20.sha256(final_raw) == source_final["raw"]["sha256"]
    )
    final_wrapped = Path(source_final["wrapped"]["path"])
    final_wrapped_exact = (
        t20.sha256(final_wrapped) == source_final["wrapped"]["sha256"]
    )
    checks = {
        "source_graph_structure_exact": smoothed_half["structure_exact"],
        "initializer_inventory_exact": smoothed_half["inventory_exact"],
        "exact_five_adapter_initializers_differ": (
            smoothed_half["differing"]
            == prereg["transform"]["initializers"]
        ),
        "right_smoothed_half_formula_exact": (
            smoothed_half["midpoint_exact"]
        ),
        "every_other_initializer_bit_exact": (
            smoothed_half["unchanged_exact"]
        ),
        "right_smoothed_half_deployment_contract": deployment_contract(
            half_deployment
        ),
        "terminal_final_raw_byte_exact": final_raw_exact,
        "terminal_final_deployment_byte_exact": final_wrapped_exact,
        "terminal_edge_is_exact_replication": (
            prereg["transform"]["terminal_edge_rule"] == "replicate_last"
        ),
        "formal_behavior_cells_zero": True,
        "training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t87_right_smoothed_pair_result.v1",
        "status": (
            "PASS_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
            if not failed
            else "HOLD_T87_RIGHT_SMOOTHED_ADAPTER_PAIR"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "policies": {
            "right_smoothed_half": {
                "raw": t20.receipt(smoothed_half["path"]),
                "deployment": half_deployment,
                "wrapped": half_deployment["wrapped"],
                "source_series": [
                    source_half["raw"],
                    source_final["raw"],
                ],
            },
            "right_smoothed_final": {
                "raw": source_final["raw"],
                "deployment": source_final["deployment"],
                "wrapped": source_final["wrapped"],
                "terminal_edge_replication": True,
                "byte_exact_to_t84_rolling_final": (
                    final_raw_exact and final_wrapped_exact
                ),
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "new_onnx_graphs_built": 1,
            "reused_byte_exact_terminal_graphs": 1,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "targeted_behavior_preregistration": not failed,
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
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T87 right-smoothed adapter pair result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- New half: exact midpoint of both T84 rolling exports",
                "- Final: byte-exact T84 rolling-final terminal replicate",
                "- Behavior/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
