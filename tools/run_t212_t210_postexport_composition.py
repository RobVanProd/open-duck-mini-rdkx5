#!/usr/bin/env python3
"""Compose T210 nominal heads into the frozen T164-final graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
import run_t172_t170_postexport_composition as t172


PREREG = (
    ANALYSIS / "t212_t210_postexport_composition_preregistration.json"
)
RESULT = ANALYSIS / "t212_t210_postexport_composition_result.json"
MARKDOWN = ANALYSIS / "T212_T210_POSTEXPORT_COMPOSITION_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t212_t210_postexport_composition_v1"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T212 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T212 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T212_T210_POSTEXPORT_COMPOSITION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T212 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, graph in enumerate(prereg["graphs"]):
        verify(graph["raw"], f"graphs[{index}].raw")
        verify(graph["base"], f"graphs[{index}].base")

    WORK.mkdir(parents=True)
    outputs = []
    started = time.time()
    for graph in prereg["graphs"]:
        step_value = int(graph["step"])
        destination = WORK / str(step_value) / "t210_composed.onnx"
        structure = t172.transform(
            Path(graph["raw"]["path"]),
            Path(graph["base"]["path"]),
            destination,
        )
        inference = t172.inference_contract(
            destination,
            Path(graph["base"]["path"]),
            prereg["contexts"],
            int(prereg["inference"]["seed"]) + step_value,
        )
        outputs.append(
            {
                "step": step_value,
                "role": graph["role"],
                "structure": structure,
                "inference": inference,
            }
        )

    allowed = sorted(t172.DESTINATION_NAMES)
    checks = {
        "three_graphs": (
            [row["step"] for row in outputs] == [0, 1_003_520, 2_007_040]
        ),
        "all_graphs_change_only_nominal_pair": all(
            row["structure"]["changed_initializers"] == allowed
            and row["structure"]["expected_changed_initializers"] == allowed
            for row in outputs
        ),
        "all_source_bindings_exact": all(
            row["structure"]["all_source_bindings_exact"] for row in outputs
        ),
        "all_nodes_byte_exact": all(
            row["structure"]["nodes_byte_exact"] for row in outputs
        ),
        "all_other_initializers_exact": all(
            row["structure"]["all_other_initializers_exact"]
            for row in outputs
        ),
        "all_initializer_names_exact": all(
            row["structure"]["initializer_names_exact"] for row in outputs
        ),
        "all_initializers_finite": all(
            row["structure"]["all_initializers_finite"] for row in outputs
        ),
        "all_inactive_routes_bit_exact": all(
            row["inference"]["all_inactive_routes_bit_exact"]
            for row in outputs
        ),
        "all_x0_outputs_bit_exact": all(
            row["inference"]["all_x0_outputs_bit_exact"]
            for row in outputs
        ),
        "both_y_negative_contexts_route_nominal": all(
            row["inference"]["both_y_negative_contexts_route_nominal"]
            for row in outputs
        ),
        "all_outputs_finite": all(
            row["inference"]["all_outputs_finite"] for row in outputs
        ),
        "cpu_only": all(
            row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    diagnostics = {
        "both_y_negative_fits_exercise_changed_moving_action": [
            {
                "step": row["step"],
                "value": row["inference"][
                    "both_y_negative_fits_bind_changed_moving_action"
                ],
            }
            for row in outputs
        ],
        "selection_weight": 0,
    }
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t212_t210_postexport_composition_result.v1"
        ),
        "status": (
            "PASS_T212_T210_POSTEXPORT_COMPOSITION"
            if not failed
            else "HOLD_T212_T210_POSTEXPORT_COMPOSITION"
        ),
        "decision": (
            "EARN_T213_T210_NOMINAL_BEHAVIOR_MATRIX_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "HOLD_T210_BEHAVIOR_AND_AUDIT_COMPOSITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "diagnostics": diagnostics,
        "graphs": outputs,
        "execution": {
            "inference_samples": sum(
                row["inference"]["samples"] for row in outputs
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
        "# T212 T210 post-export composition result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- All three graphs replace only the allowed nominal adapter pair.\n"
        "- Inactive routes and x=0 outputs remain bit-exact.\n"
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
