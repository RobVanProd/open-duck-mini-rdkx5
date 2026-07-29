#!/usr/bin/env python3
"""Freeze the model-derived +COM sagittal compensation transform."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T135 = ANALYSIS / "t135_calibration_context_router_preregistration.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T156 = ANALYSIS / "t156_three_way_positive_router_result.json"
T156B = ANALYSIS / "t156b_positive_router_gap_midpoint_result.json"
T158 = ANALYSIS / "t158_positive_expert_failure_autopsy_result.json"
OUTPUT = (
    ANALYSIS
    / "t159_mechanics_sagittal_compensation_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T159_MECHANICS_SAGITTAL_COMPENSATION_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t159_mechanics_sagittal_compensation.py"
TEST = ROOT / "tests" / "test_t159_mechanics_sagittal_compensation.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T159: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T159 preregistration requires clean worktree")
    t135 = json.loads(T135.read_text(encoding="utf-8"))
    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    t156 = json.loads(T156.read_text(encoding="utf-8"))
    t156b = json.loads(T156B.read_text(encoding="utf-8"))
    t158 = json.loads(T158.read_text(encoding="utf-8"))
    source_graphs = {
        step: t156b["graphs"][step]["transformed"]
        for step in ("1003520", "2007040")
    }
    playground = Path(t135["playground"]["path"])
    scene = (
        playground
        / "playground"
        / "open_duck_mini_v2"
        / "xmls"
        / "scene_flat_terrain_backlash.xml"
    )
    xml_files = sorted(scene.parent.glob("*.xml"))
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t135_preregistration": T135,
        "t135b_result": T135B,
        "t156_result": T156,
        "t156b_result": T156B,
        "t158_result": T158,
        "playground_manifest": Path(t135["playground"]["manifest"]["path"]),
        "scene_xml": scene,
    }
    checks = {
        "t158_selects_mechanics_screen": (
            t158["status"]
            == "PASS_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
            and t158["failed_checks"] == []
            and t158["decision"]
            == "EARN_T159_MECHANICS_DERIVED_SAGITTAL_"
            "COMPENSATION_PREREGISTRATION_ONLY"
        ),
        "t156b_sources_green": (
            t156b["status"]
            == "PASS_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
            and t156b["failed_checks"] == []
        ),
        "six_frozen_contexts_present": (
            len(t135b["runs"]) == 4
            and len(t156["positive_contexts"]) == 2
        ),
        "source_graphs_present": all(
            Path(item["path"]).is_file()
            for item in source_graphs.values()
        ),
        "scene_and_xml_dependency_set_present": (
            scene.is_file() and len(xml_files) >= 2
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T159 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t159_mechanics_sagittal_compensation_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T159_MECHANICS_SAGITTAL_COMPENSATION"
        ),
        "question": (
            "Does the unique symmetric hip/ankle posture that restores "
            "nominal whole-robot COM and average foot pose under the "
            "+0.05m torso inertial shift produce a valid zero-training "
            "positive-context action transform?"
        ),
        "source_graphs": source_graphs,
        "mechanics": {
            "scene": receipt(scene),
            "xml_dependency_receipts": [
                receipt(path) for path in xml_files
            ],
            "torso_body_name": "trunk_assembly",
            "torso_com_x_offset_m": 0.05,
            "home_keyframe": "home",
            "feet_sites": ["left_foot", "right_foot"],
            "variables": [
                "floating_base_x_m",
                "floating_base_pitch_rad",
                "mirrored_hip_pitch_delta_rad",
                "shared_ankle_pitch_delta_rad",
            ],
            "constraints": [
                "average foot x equals nominal home",
                "average foot z equals nominal home",
                "average foot pitch equals nominal home",
                "whole-robot COM x equals nominal home",
            ],
            "fixed": [
                "base z at nominal home",
                "both knees at nominal home",
                "all non-sagittal joints at nominal home",
            ],
            "left_right_signs": {
                "left_hip_pitch": 1.0,
                "right_hip_pitch": -1.0,
                "left_ankle": 1.0,
                "right_ankle": 1.0,
            },
            "central_difference_epsilon": 1e-05,
            "root_initialization": (
                "exact 4x4 linearized solve at shifted home"
            ),
            "root_method": "scipy.optimize.root(method='hybr')",
            "root_xtol": 1e-12,
            "maximum_constraint_residual": 1e-09,
            "maximum_absolute_action_bias": 1.0,
            "action_scale_rad": 0.25,
            "scalar_search": False,
        },
        "graph_transform": {
            "insertion": (
                "after raw tanh, before inherited rate projection"
            ),
            "selection": "existing T156B positive-context boolean",
            "x0_deadband": "downstream and unchanged",
            "rate_guard_and_deployment_chain": "downstream and unchanged",
            "action_clip": [-1.0, 1.0],
            "abi": "unchanged",
        },
        "contexts": {
            "nonpositive": t135b["runs"],
            "positive_source": (
                "t156_three_way_positive_router_result.json"
            ),
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T160_MECHANICS_COMPENSATED_POSITIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_MECHANICS_DERIVED_SAGITTAL_COMPENSATION"
            ),
        },
        "execution_now": {
            "mechanics_solves": 0,
            "graphs_transformed": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_mechanics_and_graph_contract": True,
            "positive_endpoint_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T159 mechanics sagittal compensation preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Unique 4-variable / 4-constraint home mechanics solve\n"
        "- Bias selected only by the frozen positive context gate\n"
        "- Inserted before inherited rate/safety/deadband chain\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
