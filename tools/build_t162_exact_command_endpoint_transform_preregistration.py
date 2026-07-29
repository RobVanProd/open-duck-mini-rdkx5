#!/usr/bin/env python3
"""Freeze the T162 exact positive-context command endpoint transform."""

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


OUTPUT = ANALYSIS / "t162_exact_command_endpoint_transform_preregistration.json"


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError("refusing to overwrite T162 preregistration")
    t161_path = ANALYSIS / "t161_command_endpoint_replay_autopsy.json"
    t159_path = ANALYSIS / "t159_mechanics_sagittal_compensation_result.json"
    t135b_path = (
        ANALYSIS
        / "t135b_interrupted_calibration_context_router_recovery_result.json"
    )
    t156_path = ANALYSIS / "t156_three_way_positive_router_result.json"
    t161 = json.loads(t161_path.read_text(encoding="utf-8"))
    t159 = json.loads(t159_path.read_text(encoding="utf-8"))
    t135b = json.loads(t135b_path.read_text(encoding="utf-8"))
    t156 = json.loads(t156_path.read_text(encoding="utf-8"))

    contexts = [
        *[
            {
                "fit_id": row["fit_id"],
                "population": row["population"],
                "context": row["context"],
                "context_sha256": row["context_sha256"],
            }
            for row in t135b["runs"]
        ],
        *[
            {
                "fit_id": row["fit_id"],
                "population": row["population"],
                "context": row["context"],
                "context_sha256": row["context_sha256"],
            }
            for row in t156["positive_contexts"]
        ],
    ]
    source_graphs = [
        {
            **t159["graphs"][step]["transformed"],
            "step": int(step),
        }
        for step in ("1003520", "2007040")
    ]
    frozen_inputs = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t162_exact_command_endpoint_transform.py"
        ),
        "test": receipt(
            ROOT / "tests" / "test_t162_exact_command_endpoint_transform.py"
        ),
        "t161_result": receipt(t161_path),
        "t159_result": receipt(t159_path),
        "t135b_context_result": receipt(t135b_path),
        "t156_positive_context_result": receipt(t156_path),
    }
    endpoints = {
        "1003520": 0.080,
        "2007040": 0.074,
    }
    checks = {
        "t161_passed": (
            t161["status"]
            == "PASS_T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY"
            and not t161["failed_checks"]
        ),
        "t161_only_authorized_graph_contract": (
            t161["authority"]["graph_contract"]
            and not t161["authority"]["behavior_rerun"]
        ),
        "six_frozen_contexts": (
            len(contexts) == 6
            and {row["population"] for row in contexts}
            == {"nominal", "com_x_negative", "com_x_positive"}
            and {row["fit_id"] for row in contexts} == {"p30", "p31_34"}
        ),
        "two_t159_source_graphs": (
            len(source_graphs) == 2
            and all(Path(row["path"]).is_file() for row in source_graphs)
        ),
        "endpoint_rule_exact_from_t161": (
            endpoints
            == {
                str(step): endpoint
                for step, endpoint in (
                    (1003520, 0.080),
                    (2007040, 0.074),
                )
            }
        ),
        "no_scalar_search": True,
        "zero_behavior_cells_now": True,
        "zero_training_hosted_robot_now": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t162_exact_command_endpoint_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T162_EXACT_COMMAND_ENDPOINT_TRANSFORM"
        ),
        "question": (
            "Can a positive-context-only rewrite of the actor's command "
            "coordinate reproduce each checkpoint's already-green support "
            "endpoint exactly while preserving the external command, x=0, "
            "nonpositive contexts, ABI, guards, and feedback state?"
        ),
        "frozen_inputs": frozen_inputs,
        "source_graphs": source_graphs,
        "contexts": contexts,
        "endpoint_command_by_step_x_m_s": endpoints,
        "transform": {
            "external_command_unchanged": True,
            "actor_command_observation_index": 6,
            "positive_context_only": True,
            "positive_moving_only": True,
            "x0_unchanged": True,
            "deadband_guard_and_action_feedback_use_external_command": True,
            "scalar_search": False,
            "new_runtime_inputs": 0,
            "new_runtime_outputs": 0,
        },
        "inference": {
            "provider": "CPUExecutionProvider",
            "seed": 20260729,
            "commands_x_m_s": [-0.08, 0.0, 0.074, 0.077, 0.08],
            "samples_per_context_command": 32,
            "required_exactness": "bit_exact_all_outputs",
        },
        "decision_rule": {
            "pass": (
                "EARN_T163_COMMAND_ENDPOINT_POSITIVE_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_COMMAND_ENDPOINT_REPLAY_REPAIR",
            "no_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "inference_samples": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_transform": not failed,
            "behavior_matrix": False,
            "full_r2": False,
            "training": False,
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
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
