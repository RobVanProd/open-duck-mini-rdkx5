#!/usr/bin/env python3
"""Preregister the bounded positive-router ONNX transform."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T234B = ANALYSIS / "t234b_abi_helper_recovery_result.json"
T238_PREREG = (
    ANALYSIS / "t238_home_offset_route_autopsy_preregistration.json"
)
T240 = ANALYSIS / "t240_bounded_positive_router_result.json"
OUTPUT = (
    ANALYSIS
    / "t241_bounded_positive_router_transform_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t241_bounded_positive_router_transform.py"
TEST = ROOT / "tests" / "test_t241_bounded_positive_router_transform.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T241: {path}")
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t234b = json.loads(T234B.read_text(encoding="utf-8"))
    t238_prereg = json.loads(T238_PREREG.read_text(encoding="utf-8"))
    t240 = json.loads(T240.read_text(encoding="utf-8"))
    graphs = [
        {
            "role": row["role"],
            "step": int(row["step"]),
            **receipt(Path(row["structure"]["transformed"]["path"])),
        }
        for row in t234b["graphs"]
    ]
    home_traces = [
        {
            "checkpoint_id": block["checkpoint_id"],
            "role": (
                "half"
                if block["checkpoint_id"].endswith("_HALF")
                else "final"
            ),
            "fit_id": block["fit_id"],
            "command_x_m_s": cell["command_x_m_s"],
            "trace": cell["trace"],
        }
        for block in t238_prereg["blocks"]
        if block["condition_id"] == "HOME_JOINT_OFFSET_NEG"
        for cell in block["cells"]
    ]
    checks = {
        "t240_earns_transform_only": (
            t240["status"] == "PASS_T240_BOUNDED_POSITIVE_ROUTER"
            and t240["decision"]
            == "EARN_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM_PREREGISTRATION_ONLY"
            and all(t240["checks"].values())
        ),
        "two_exact_graphs_and_forty_contexts": (
            {row["role"] for row in graphs} == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs)
            and len(t167["cells"]) == 40
        ),
        "twelve_frozen_home_offset_moving_traces": (
            len(home_traces) == 12
            and all(Path(row["trace"]["path"]).is_file() for row in home_traces)
        ),
        "read_only_no_behavior_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T241 preregistration checks failed: {failed}")

    upper = float(t240["combined"]["upper_bound"])
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t241_bounded_positive_router_transform_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
        ),
        "question": (
            "Can one uniform graph-internal upper bound remove the proven "
            "HOME_JOINT_OFFSET_NEG false-positive route while preserving "
            "every other frozen context, the recurrent ABI, and x=0 exactly?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t167_contexts": receipt(T167),
            "t234b_graphs": receipt(T234B),
            "t238_preregistration": receipt(T238_PREREG),
            "t240_result": receipt(T240),
        },
        "graphs": graphs,
        "home_offset_traces": home_traces,
        "transform": {
            "upper_bound_float32": upper,
            "existing_lower_gate": "positive_router_score >= 0",
            "new_gate": (
                "existing_lower_gate AND positive_router_score <= "
                "t241_positive_router_upper_bound"
            ),
            "gate_sites": [
                "t162_positive_router_gate",
                "t156_positive_router_gate",
            ],
            "expected_added_initializer": (
                "t241_positive_router_upper_bound"
            ),
            "expected_added_nodes": [
                "t241_t162_positive_upper_gate",
                "t241_t162_bounded_positive_gate",
                "t241_t156_positive_upper_gate",
                "t241_t156_bounded_positive_gate",
            ],
            "expected_changed_old_nodes": [
                "t162_positive_router_gate",
                "t156_positive_router_gate",
            ],
            "same_transform_both_checkpoints": True,
        },
        "cpu_contract": {
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "samples_per_context_command": 8,
            "random_seed": 241,
            "all_non_home_negative_context_outputs": (
                "bit-exact source for all outputs"
            ),
            "home_negative_x0": "bit-exact source for all outputs",
            "home_negative_moving": (
                "finite, route changed, and at least one action differs"
            ),
            "trace_replay": (
                "source output exact to all stored policy outputs; transformed "
                "output finite and different on every failed moving trace"
            ),
            "abi": "obs[1,115], previous_action[1,14], h_in[1,64], "
            "calibration_context[1,64] -> actions[1,14], "
            "previous_action_out[1,14], h_out[1,64]",
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T242_BOUNDED_ROUTER_HOME_OFFSET_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_BOUNDED_POSITIVE_ROUTER_WITHOUT_BEHAVIOR"
            ),
            "no_behavior_or_training_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_transform_and_cpu_contract": True,
            "home_offset_behavior_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T241 bounded positive-router transform preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Upper score bound: `{upper:.9f}` (frozen float32 midpoint)\n"
        "- Delta: two upper comparisons plus two AND gates in each graph\n"
        "- Proof: `40` contexts, four commands, random states, and all "
        "twelve failed traces\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
