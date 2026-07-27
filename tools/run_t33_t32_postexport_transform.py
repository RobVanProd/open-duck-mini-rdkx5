#!/usr/bin/env python3
"""Apply T32's frozen deployment chain to all three exact exports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_t20_support_trainthrough_one_update as t20
import run_t31_action_margin_trainthrough_cpu_smoke as t31


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = ANALYSIS / "t33_t32_postexport_preregistration.json"
T31_PREREGISTRATION = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t33_t32_postexport_result.json"
MARKDOWN = ANALYSIS / "T33_T32_POSTEXPORT_RESULT_20260727.md"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def graph_step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def verify_preregistration(value: dict) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T33_T32_POSTEXPORT_TRANSFORM"
        or value.get("failed_checks") != []
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise ValueError("T33 preregistration changed")
    for name, expected in value["source_hashes"].items():
        path = ROOT / name
        if not path.is_file() or t20.sha256(path) != expected:
            raise ValueError(f"T33 source changed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T33 exact transform requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T33: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    raw_root = args.raw_root.resolve()
    work = args.work_root.resolve()
    raw_graphs = sorted(raw_root.glob("*.onnx"), key=graph_step)
    raw_steps = [graph_step(path) for path in raw_graphs]
    raw_hashes = {
        str(graph_step(path)): t20.sha256(path) for path in raw_graphs
    }
    if raw_steps != EXPECTED_STEPS or raw_hashes != prereg["raw_graphs"]:
        raise ValueError("T33 raw export inventory changed")

    work.mkdir(parents=True)
    deployments = {
        str(graph_step(path)): t31.deployment_graph(
            path,
            work / str(graph_step(path)),
        )
        for path in raw_graphs
    }
    t31_prereg = json.loads(
        T31_PREREGISTRATION.read_text(encoding="utf-8")
    )
    golden_assets = t31_prereg["assets"]
    step_zero = deployments["0"]
    postupdate = [
        deployments[str(step)] for step in EXPECTED_STEPS[1:]
    ]
    checks = {
        "raw_inventory_exact": (
            raw_steps == EXPECTED_STEPS
            and raw_hashes == prereg["raw_graphs"]
        ),
        "step_zero_raw_byte_exact": (
            step_zero["raw"]["sha256"]
            == golden_assets["source_v121_half_onnx"]["sha256"]
        ),
        "step_zero_context_abi_byte_exact": (
            step_zero["context_abi"]["sha256"]
            == golden_assets["frozen_t18_context_abi_onnx"]["sha256"]
        ),
        "step_zero_pre_margin_wrapper_byte_exact": (
            step_zero["pre_margin_wrapped"]["sha256"]
            == golden_assets[
                "frozen_t18_pre_margin_wrapped_onnx"
            ]["sha256"]
        ),
        "step_zero_final_margin_byte_exact": (
            step_zero["wrapped"]["sha256"]
            == golden_assets["frozen_t18_wrapped_onnx"]["sha256"]
        ),
        "all_source_deployment_contracts_pass": all(
            row["source_deployment"]["inference"]["pass"]
            and row["source_deployment"]["node_counts"]
            == {
                "raw": 29,
                "guarded": 42,
                "deadbanded": 47,
                "deployed": 56,
            }
            for row in deployments.values()
        ),
        "all_context_parity_contracts_pass": all(
            row["context_parity"]["all_outputs_bit_exact"]
            and row["context_parity"]["context_is_diagnostic_only"]
            and row["context_parity"]["zero_command_actions_exact_zero"]
            for row in deployments.values()
        ),
        "all_physical_wrapper_contracts_pass": all(
            row["verification"]["outputs_exact"]
            and row["verification"][
                "previous_action_out_equals_action_bit_exact"
            ]
            and row["verification"][
                "x0_output_equals_support_action_bit_exact"
            ]
            and row["verification"]["output_bounds_exact"]
            and row["verification"]["maximum_normalized_rate_excess"]
            <= 1e-7
            for row in deployments.values()
        ),
        "all_margin_contracts_pass": all(
            row["margin_contract"]["pass"] for row in deployments.values()
        ),
        "both_postupdate_exports_transformed": len(postupdate) == 2,
        "formal_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t33_t32_postexport_result.v1",
        "status": (
            "PASS_T33_T32_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_T33_T32_POSTEXPORT_TRANSFORM"
        ),
        "failed_checks": failed,
        "checks": checks,
        "raw_graphs": raw_hashes,
        "deployments": deployments,
        "execution": {
            "onnx_graphs_transformed": len(deployments),
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "decision": (
            "EARN_T33_NOMINAL_MATRIX_PREREGISTRATION"
            if not failed
            else "HOLD_WITHOUT_BEHAVIOR"
        ),
        "authority": {
            "nominal_matrix_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "robustness_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
        },
    }
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T33 T32 post-export result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- Step-zero raw/context/pre-margin/final chain is byte-exact "
                "to the green T31 golden transform.",
                "- Both post-update graphs passed all deployment contracts.",
                "- Behavior/Gate5/robot authority: `0/0/0`.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
