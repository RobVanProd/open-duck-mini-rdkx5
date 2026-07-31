#!/usr/bin/env python3
"""Build and verify T78's exact half/final adapter midpoint graph."""

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


PREREG = ANALYSIS / "t81_t78_midpoint_preregistration.json"
RESULT = ANALYSIS / "t81_t78_midpoint_result.json"
MARKDOWN = ANALYSIS / "T81_T78_MIDPOINT_RESULT_20260728.md"


def graph_without_initializers(model: onnx.ModelProto) -> bytes:
    value = copy.deepcopy(model)
    del value.graph.initializer[:]
    return value.SerializeToString()


def initializer_arrays(
    model: onnx.ModelProto,
) -> dict[str, np.ndarray]:
    return {
        value.name: numpy_helper.to_array(value)
        for value in model.graph.initializer
    }


def verify_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"]
        != "PREREGISTERED_T81_T78_EXACT_ADAPTER_MIDPOINT"
        or value["failed_checks"] != []
        or t20.canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise ValueError("T81 preregistration changed")
    for name, item in value["sources"].items():
        path = Path(item["path"])
        if t20.sha256(path) != item["sha256"]:
            raise ValueError(f"T81 source changed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T81 midpoint transform requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T81: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    work = args.work_root.resolve()
    work.mkdir(parents=True)
    half_path = Path(prereg["sources"]["half_raw"]["path"])
    final_path = Path(prereg["sources"]["final_raw"]["path"])
    half = onnx.load(str(half_path))
    final = onnx.load(str(final_path))
    half_arrays = initializer_arrays(half)
    final_arrays = initializer_arrays(final)
    structure_exact = (
        graph_without_initializers(half)
        == graph_without_initializers(final)
    )
    inventory_exact = list(half_arrays) == list(final_arrays)
    shape_dtype_exact = all(
        half_arrays[name].shape == final_arrays[name].shape
        and half_arrays[name].dtype == final_arrays[name].dtype
        for name in half_arrays
    )
    differing = sorted(
        name
        for name in half_arrays
        if not np.array_equal(half_arrays[name], final_arrays[name])
    )
    expected = prereg["transform"]["initializers"]
    if not (structure_exact and inventory_exact and shape_dtype_exact):
        raise ValueError("T81 source graph structure or inventory changed")
    if differing != expected:
        raise ValueError(
            f"T81 differing initializers changed: {differing}"
        )

    midpoint_arrays = {
        name: (
            (
                half_arrays[name].astype(np.float64)
                + final_arrays[name].astype(np.float64)
            )
            * 0.5
        ).astype(half_arrays[name].dtype)
        for name in differing
    }
    midpoint = copy.deepcopy(half)
    by_name = {
        value.name: index
        for index, value in enumerate(midpoint.graph.initializer)
    }
    for name, array in midpoint_arrays.items():
        midpoint.graph.initializer[by_name[name]].CopyFrom(
            numpy_helper.from_array(array, name=name)
        )
    midpoint_path = work / "raw_midpoint.onnx"
    onnx.checker.check_model(midpoint)
    onnx.save(midpoint, str(midpoint_path))
    observed = initializer_arrays(onnx.load(str(midpoint_path)))
    midpoint_exact = all(
        np.array_equal(observed[name], midpoint_arrays[name])
        for name in differing
    )
    unchanged_exact = all(
        np.array_equal(observed[name], half_arrays[name])
        for name in half_arrays
        if name not in differing
    )
    deployment = t31.deployment_graph(
        midpoint_path,
        work / "deployment",
    )
    checks = {
        "source_graph_structure_exact": structure_exact,
        "initializer_inventory_exact": inventory_exact,
        "initializer_shape_dtype_exact": shape_dtype_exact,
        "exact_five_expected_initializers_differ": differing == expected,
        "midpoint_formula_exact": midpoint_exact,
        "every_other_initializer_bit_exact": unchanged_exact,
        "midpoint_onnx_checker_passed": True,
        "source_deployment_contract_pass": (
            deployment["source_deployment"]["inference"]["pass"]
            and deployment["source_deployment"]["node_counts"]
            == {
                "raw": 29,
                "guarded": 42,
                "deadbanded": 47,
                "deployed": 56,
            }
        ),
        "context_parity_contract_pass": (
            deployment["context_parity"]["all_outputs_bit_exact"]
            and deployment["context_parity"]["context_is_diagnostic_only"]
            and deployment["context_parity"][
                "zero_command_actions_exact_zero"
            ]
        ),
        "physical_wrapper_contract_pass": (
            deployment["verification"]["outputs_exact"]
            and deployment["verification"][
                "previous_action_out_equals_action_bit_exact"
            ]
            and deployment["verification"][
                "x0_output_equals_support_action_bit_exact"
            ]
            and deployment["verification"]["output_bounds_exact"]
            and deployment["verification"][
                "maximum_normalized_rate_excess"
            ]
            <= 1e-7
        ),
        "margin_contract_pass": deployment["margin_contract"]["pass"],
        "formal_behavior_cells_zero": True,
        "training_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t81_t78_midpoint_result.v1",
        "status": (
            "PASS_T81_T78_EXACT_ADAPTER_MIDPOINT"
            if not failed
            else "HOLD_T81_T78_EXACT_ADAPTER_MIDPOINT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if not failed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "sources": {
            "half": t20.receipt(half_path),
            "final": t20.receipt(final_path),
        },
        "midpoint": {
            "raw": t20.receipt(midpoint_path),
            "differing_initializers": differing,
            "initializer_deltas": {
                name: {
                    "half_to_final_max_abs": float(
                        np.max(
                            np.abs(
                                final_arrays[name].astype(np.float64)
                                - half_arrays[name].astype(np.float64)
                            )
                        )
                    ),
                    "half_to_final_rms": float(
                        np.sqrt(
                            np.mean(
                                (
                                    final_arrays[name].astype(np.float64)
                                    - half_arrays[name].astype(np.float64)
                                )
                                ** 2
                            )
                        )
                    ),
                }
                for name in differing
            },
            "deployment": deployment,
            "wrapped": deployment["wrapped"],
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "onnx_graphs_built": 1,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "two_cell_behavior_preregistration": not failed,
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
                "# T81 T78 exact adapter midpoint result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                f"- Differing initializers: `{differing}`",
                "- Behavior/training/Colab/Gate5/robot: `0/0/0/0/0`",
                "- Candidate status: `diagnostic only`",
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
