#!/usr/bin/env python3
"""Compose T228 exports with frozen repairs and command plateau."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi as model_abi,
    canonical_sha256,
    receipt,
    verify,
)
import run_t172_t170_postexport_composition as t172
import run_t222_global_command_plateau_transform as t222


PREREG = (
    ANALYSIS / "t230_t228_deployment_composition_preregistration.json"
)
RESULT = ANALYSIS / "t230_t228_deployment_composition_result.json"
MARKDOWN = ANALYSIS / "T230_T228_DEPLOYMENT_COMPOSITION_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t230_t228_deployment_composition_v1"
)


def path_aware_abi(value: Any) -> dict[str, Any]:
    model = onnx.load(value) if isinstance(value, (str, Path)) else value
    return model_abi(model)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T230 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T230 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T230_T228_DEPLOYMENT_COMPOSITION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T230 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, graph in enumerate(prereg["graphs"]):
        verify(graph["raw"], f"graphs[{index}].raw")
        verify(graph["base"], f"graphs[{index}].base")

    t222.abi = path_aware_abi
    WORK.mkdir(parents=True)
    outputs = []
    started = time.time()
    for graph_index, graph in enumerate(prereg["graphs"]):
        step_value = int(graph["step"])
        composed = WORK / str(step_value) / "t228_composed.onnx"
        plateau = WORK / str(step_value) / "t228_global_plateau.onnx"
        composition = t172.transform(
            Path(graph["raw"]["path"]),
            Path(graph["base"]["path"]),
            composed,
        )
        composition_inference = t172.inference_contract(
            composed,
            Path(graph["base"]["path"]),
            prereg["contexts"],
            int(prereg["inference"]["seed"]) + step_value,
        )
        plateau_structure = t222.transform(
            composed,
            plateau,
            float(prereg["composition"]["global_command_cap_m_s"]),
        )
        plateau_inference = t222.random_equivalence(
            composed,
            plateau,
            prereg["contexts"],
            int(prereg["inference"]["seed"]) + 10_000 + graph_index,
            int(prereg["inference"]["samples_per_context_command"]),
        )
        outputs.append(
            {
                "step": step_value,
                "role": graph["role"],
                "composed": receipt(composed),
                "plateau": receipt(plateau),
                "composition": composition,
                "composition_inference": composition_inference,
                "plateau_structure": plateau_structure,
                "plateau_inference": plateau_inference,
            }
        )

    expected_new_nodes = [
        "t222_slice_prefix",
        "t222_slice_command",
        "t222_cap_command",
        "t222_slice_suffix",
        "t222_rebuild_policy_obs",
    ]
    allowed = sorted(t172.DESTINATION_NAMES)
    checks = {
        "three_graphs": (
            [row["step"] for row in outputs]
            == [0, 1_003_520, 2_007_040]
        ),
        "composition_changes_only_nominal_pair": all(
            row["composition"]["changed_initializers"] == allowed
            and row["composition"]["expected_changed_initializers"]
            == allowed
            and row["composition"]["all_source_bindings_exact"]
            and row["composition"]["nodes_byte_exact"]
            and row["composition"]["all_other_initializers_exact"]
            and row["composition"]["initializer_names_exact"]
            and row["composition"]["all_initializers_finite"]
            for row in outputs
        ),
        "composition_inactive_routes_and_x0_exact": all(
            row["composition_inference"]["all_inactive_routes_bit_exact"]
            and row["composition_inference"]["all_x0_outputs_bit_exact"]
            and row["composition_inference"][
                "both_y_negative_contexts_route_nominal"
            ]
            and row["composition_inference"]["all_outputs_finite"]
            and row["composition_inference"]["provider"]
            == "CPUExecutionProvider"
            for row in outputs
        ),
        "plateau_stateful_abi_exact": all(
            row["plateau_structure"]["source_abi"]
            == row["plateau_structure"]["transformed_abi"]
            for row in outputs
        ),
        "plateau_only_expected_nodes_and_rewires": all(
            row["plateau_structure"]["new_node_names"]
            == expected_new_nodes
            and row["plateau_structure"]["unchanged_old_nodes"]
            == row["plateau_structure"]["expected_unchanged_old_nodes"]
            and row["plateau_structure"]["exact_rewired_nodes"]
            == row["plateau_structure"]["expected_exact_rewired_nodes"]
            == 3
            and row["plateau_structure"]["rewired_node_names"]
            == sorted(t222.REWIRED_NODES)
            for row in outputs
        ),
        "plateau_preserves_old_initializers_and_adds_only_expected": all(
            row["plateau_structure"]["all_old_initializers_exact"]
            and row["plateau_structure"][
                "only_expected_initializers_added"
            ]
            and row["plateau_structure"]["onnx_checker_pass"]
            for row in outputs
        ),
        "plateau_cap_exact_float32_0077": all(
            abs(
                row["plateau_structure"]["cap_float32_m_s"]
                - 0.07699999958276749
            )
            == 0.0
            for row in outputs
        ),
        "plateau_lower_commands_and_x008_mapping_exact": all(
            row["plateau_inference"]["all_lower_commands_exact"]
            and row["plateau_inference"][
                "all_x008_maps_exactly_to_x0077"
            ]
            and row["plateau_inference"]["all_outputs_finite"]
            and row["plateau_inference"]["provider"]
            == "CPUExecutionProvider"
            for row in outputs
        ),
        "zero_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t230_t228_deployment_composition_result.v1"
        ),
        "status": (
            "PASS_T230_T228_DEPLOYMENT_COMPOSITION"
            if not failed
            else "HOLD_T230_T228_DEPLOYMENT_COMPOSITION"
        ),
        "decision": (
            "EARN_T231_T228_NOMINAL_BEHAVIOR_MATRIX_PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_T228_BEHAVIOR_AND_AUDIT_COMPOSITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "onnx_transforms": len(outputs) * 2,
            "onnx_inferences": sum(
                row["composition_inference"]["samples"]
                + row["plateau_inference"]["samples"]
                for row in outputs
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "nominal_behavior_preregistration": not failed,
            "behavior_matrix": False,
            "training": False,
            "decisive_condition_matrices": False,
            "gate5": False,
            "robot_or_rdk": False,
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
        "# T230 T228 deployment composition result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- T164 repair graph plus retained global x=.080 to .077 plateau\n"
        "- Lower commands, inactive routes, x=0, state and ABI exact\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
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
