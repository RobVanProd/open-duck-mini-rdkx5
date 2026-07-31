#!/usr/bin/env python3
"""Apply T113's frozen deployment chain to all three exports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402


PREREGISTRATION = ANALYSIS / "t115_t113_postexport_preregistration.json"
RESULT = ANALYSIS / "t115_t113_postexport_result.json"
MARKDOWN = ANALYSIS / "T115_T113_POSTEXPORT_RESULT_20260729.md"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def graph_step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T115 exact transform requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T115: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T115 transform requires clean worktree")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T115_T113_POSTEXPORT_TRANSFORM"
        or prereg["failed_checks"]
        or t20.canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise ValueError("T115 preregistration changed")
    for name, expected in prereg["source_hashes"].items():
        if t20.sha256(ROOT / name) != expected:
            raise ValueError(f"T115 source changed: {name}")

    raw_root = args.raw_root.resolve()
    work = args.work_root.resolve()
    raw_graphs = sorted(raw_root.glob("*.onnx"), key=graph_step)
    raw_steps = [graph_step(path) for path in raw_graphs]
    raw_hashes = {
        str(graph_step(path)): t20.sha256(path) for path in raw_graphs
    }
    if raw_steps != EXPECTED_STEPS or raw_hashes != prereg["raw_graphs"]:
        raise ValueError("T115 raw export inventory changed")

    work.mkdir(parents=True)
    deployments = {
        str(graph_step(path)): t31.deployment_graph(
            path, work / str(graph_step(path))
        )
        for path in raw_graphs
    }
    checks = {
        "raw_inventory_exact": (
            raw_steps == EXPECTED_STEPS
            and raw_hashes == prereg["raw_graphs"]
        ),
        "all_source_deployment_contracts_pass": all(
            row["source_deployment"]["inference"]["pass"]
            and row["source_deployment"]["node_counts"]
            == prereg["expected_source_node_counts"]
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
            and row["verification"]["x0_output_equals_support_action_bit_exact"]
            and row["verification"]["output_bounds_exact"]
            and row["verification"]["maximum_normalized_rate_excess"] <= 1e-7
            for row in deployments.values()
        ),
        "all_margin_contracts_pass": all(
            row["margin_contract"]["pass"] for row in deployments.values()
        ),
        "both_postupdate_exports_transformed": all(
            str(step_value) in deployments
            for step_value in EXPECTED_STEPS[1:]
        ),
        "formal_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value = {
        "schema_version": "open_duck.t115_t113_postexport_result.v1",
        "status": (
            "PASS_T115_T113_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_T115_T113_POSTEXPORT_TRANSFORM"
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
            "EARN_T116_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_WITHOUT_BEHAVIOR"
        ),
        "authority": {
            "nominal_matrix_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
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
                "# T115 T113 post-export result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- All three graphs use the frozen deployment chain",
                "- Behavior / Gate 5 / robot authority: 0 / 0 / 0",
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
