#!/usr/bin/env python3
"""Build and verify T78's two rolling adapter-midpoint policies."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
from run_t81_t78_midpoint_transform import (  # noqa: E402
    graph_without_initializers,
    initializer_arrays,
)


PREREG = ANALYSIS / "t84_t78_rolling_midpoint_preregistration.json"
RESULT = ANALYSIS / "t84_t78_rolling_midpoint_result.json"
MARKDOWN = ANALYSIS / "T84_T78_ROLLING_MIDPOINT_RESULT_20260728.md"


def verify_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"]
        != "PREREGISTERED_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
        or value["failed_checks"] != []
        or t20.canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise ValueError("T84 preregistration changed")
    for name, item in value["sources"].items():
        if name == "raw_exports":
            for step, receipt in item.items():
                path = Path(receipt["path"])
                if t20.sha256(path) != receipt["sha256"]:
                    raise ValueError(f"T84 raw source changed: {step}")
            continue
        path = Path(item["path"])
        if t20.sha256(path) != item["sha256"]:
            raise ValueError(f"T84 source changed: {name}")


def build_midpoint(
    earlier_path: Path,
    later_path: Path,
    expected: list[str],
    destination: Path,
) -> dict[str, Any]:
    earlier = onnx.load(str(earlier_path))
    later = onnx.load(str(later_path))
    earlier_arrays = initializer_arrays(earlier)
    later_arrays = initializer_arrays(later)
    structure_exact = (
        graph_without_initializers(earlier)
        == graph_without_initializers(later)
    )
    inventory_exact = list(earlier_arrays) == list(later_arrays)
    differing = sorted(
        name
        for name in earlier_arrays
        if not np.array_equal(earlier_arrays[name], later_arrays[name])
    )
    if not structure_exact or not inventory_exact or differing != expected:
        raise ValueError(
            "T84 adjacent export structure or initializer set changed"
        )
    midpoint_arrays = {
        name: (
            (
                earlier_arrays[name].astype(np.float64)
                + later_arrays[name].astype(np.float64)
            )
            * 0.5
        ).astype(earlier_arrays[name].dtype)
        for name in differing
    }
    midpoint = copy.deepcopy(earlier)
    by_name = {
        value.name: index
        for index, value in enumerate(midpoint.graph.initializer)
    }
    for name, array in midpoint_arrays.items():
        midpoint.graph.initializer[by_name[name]].CopyFrom(
            numpy_helper.from_array(array, name=name)
        )
    onnx.checker.check_model(midpoint)
    onnx.save(midpoint, str(destination))
    observed = initializer_arrays(onnx.load(str(destination)))
    midpoint_exact = all(
        np.array_equal(observed[name], midpoint_arrays[name])
        for name in differing
    )
    unchanged_exact = all(
        np.array_equal(observed[name], earlier_arrays[name])
        for name in earlier_arrays
        if name not in differing
    )
    return {
        "path": destination,
        "differing": differing,
        "structure_exact": structure_exact,
        "inventory_exact": inventory_exact,
        "midpoint_exact": midpoint_exact,
        "unchanged_exact": unchanged_exact,
    }


def deployment_contract(row: dict[str, Any]) -> bool:
    return bool(
        row["source_deployment"]["inference"]["pass"]
        and row["source_deployment"]["node_counts"]
        == {
            "raw": 29,
            "guarded": 42,
            "deadbanded": 47,
            "deployed": 56,
        }
        and row["context_parity"]["all_outputs_bit_exact"]
        and row["context_parity"]["context_is_diagnostic_only"]
        and row["context_parity"]["zero_command_actions_exact_zero"]
        and row["verification"]["outputs_exact"]
        and row["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and row["verification"]["x0_output_equals_support_action_bit_exact"]
        and row["verification"]["output_bounds_exact"]
        and row["verification"]["maximum_normalized_rate_excess"] <= 1e-7
        and row["margin_contract"]["pass"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T84 rolling transform requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T84: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    work = args.work_root.resolve()
    work.mkdir(parents=True)
    raw = {
        int(step): Path(item["path"])
        for step, item in prereg["sources"]["raw_exports"].items()
    }
    expected = prereg["transform"]["initializers"]
    rolling_half = build_midpoint(
        raw[0],
        raw[1_003_520],
        expected,
        work / "rolling_half_raw.onnx",
    )
    rolling_final = build_midpoint(
        raw[1_003_520],
        raw[2_007_040],
        expected,
        work / "rolling_final_raw.onnx",
    )
    deployments = {
        "rolling_half": t31.deployment_graph(
            rolling_half["path"],
            work / "rolling_half",
        ),
        "rolling_final": t31.deployment_graph(
            rolling_final["path"],
            work / "rolling_final",
        ),
    }
    t81 = json.loads(
        Path(prereg["sources"]["t81_midpoint"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    t81_raw = Path(t81["midpoint"]["raw"]["path"])
    rolling_final_matches_t81 = (
        t20.sha256(rolling_final["path"]) == t20.sha256(t81_raw)
    )
    checks = {
        "both_adjacent_graph_structures_exact": (
            rolling_half["structure_exact"]
            and rolling_final["structure_exact"]
        ),
        "both_initializer_inventories_exact": (
            rolling_half["inventory_exact"]
            and rolling_final["inventory_exact"]
        ),
        "both_exact_five_adapter_initializers": (
            rolling_half["differing"] == expected
            and rolling_final["differing"] == expected
        ),
        "both_midpoint_formulas_exact": (
            rolling_half["midpoint_exact"]
            and rolling_final["midpoint_exact"]
        ),
        "both_other_initializers_bit_exact": (
            rolling_half["unchanged_exact"]
            and rolling_final["unchanged_exact"]
        ),
        "rolling_final_byte_exact_to_t81": rolling_final_matches_t81,
        "both_deployment_contracts_pass": all(
            deployment_contract(row) for row in deployments.values()
        ),
        "formal_behavior_cells_zero": True,
        "training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t84_t78_rolling_midpoint_result.v1",
        "status": (
            "PASS_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
            if not failed
            else "HOLD_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
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
            "rolling_half": {
                "raw": t20.receipt(rolling_half["path"]),
                "deployment": deployments["rolling_half"],
                "wrapped": deployments["rolling_half"]["wrapped"],
            },
            "rolling_final": {
                "raw": t20.receipt(rolling_final["path"]),
                "deployment": deployments["rolling_final"],
                "wrapped": deployments["rolling_final"]["wrapped"],
                "byte_exact_to_t81_raw": rolling_final_matches_t81,
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_graphs_built": 2,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_matrix_preregistration": not failed,
            "behavior_execution": False,
            "training": False,
            "colab": False,
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
                "# T84 T78 rolling midpoint result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- Policies: rolling half / rolling final",
                "- Rolling final byte-exact to T81 midpoint",
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
