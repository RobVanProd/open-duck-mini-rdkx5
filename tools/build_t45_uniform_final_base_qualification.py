#!/usr/bin/env python3
"""Freeze T45's uniform final-base transform and 48-cell qualification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T44_RESULT = ANALYSIS / "t44_corrected_forward_factorial_result.json"
T43_PREREG = (
    ANALYSIS / "t43_forward_actor_block_factorial_preregistration.json"
)
T39_PREREG = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
T41_PREREG = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
RUNNER = ROOT / "tools" / "run_t45_uniform_final_base_qualification.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = ANALYSIS / "t45_uniform_final_base_qualification_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T45_UNIFORM_FINAL_BASE_QUALIFICATION_PREREGISTRATION_20260728.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def graph_signature(model: onnx.ModelProto) -> dict[str, Any]:
    return {
        "nodes": [
            (
                node.op_type,
                node.domain,
                tuple(node.input),
                tuple(node.output),
            )
            for node in model.graph.node
        ],
        "inputs": [
            (item.name, str(item.type)) for item in model.graph.input
        ],
        "outputs": [
            (item.name, str(item.type)) for item in model.graph.output
        ],
        "initializers": [
            (item.name, tuple(item.dims), int(item.data_type))
            for item in model.graph.initializer
        ],
    }


def values(path: Path) -> tuple[onnx.ModelProto, dict[str, np.ndarray]]:
    model = onnx.load(str(path))
    onnx.checker.check_model(model)
    return model, {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def changed(
    source: dict[str, np.ndarray],
    target: dict[str, np.ndarray],
) -> list[str]:
    if set(source) != set(target):
        raise ValueError("T45 initializer inventory changed")
    return sorted(
        name
        for name in source
        if not np.array_equal(source[name], target[name])
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T45 prereg: {path}")
    t44 = json.loads(T44_RESULT.read_text(encoding="utf-8"))
    t43 = json.loads(T43_PREREG.read_text(encoding="utf-8"))
    t39 = json.loads(T39_PREREG.read_text(encoding="utf-8"))
    t41 = json.loads(T41_PREREG.read_text(encoding="utf-8"))
    selected_variant = next(
        item
        for item in t43["variants"]
        if item["variant_id"] == "HALF_WITH_FINAL_BASE"
    )
    half_source_path = Path(t39["policies"][0]["path"])
    final_source_path = Path(t39["policies"][1]["path"])
    half_target_path = Path(selected_variant["policy"]["path"])
    final_target_path = final_source_path
    half_source_model, half_source_values = values(half_source_path)
    final_source_model, final_source_values = values(final_source_path)
    half_target_model, half_target_values = values(half_target_path)
    final_target_model, final_target_values = values(final_target_path)
    half_changes = changed(half_source_values, half_target_values)
    final_changes = changed(final_source_values, final_target_values)
    endpoint_changes = changed(half_target_values, final_target_values)
    base_names = sorted(t43["groups"]["base"])
    adapter_names = sorted(t43["groups"]["adapter"])
    conditions = t41["conditions"][:3]
    policies = [
        {
            "checkpoint_id": "T45_UNIFORM_FINAL_BASE_HALF",
            "source_checkpoint": "T32_HALF",
            "step": 1_003_520,
            **receipt(half_target_path),
        },
        {
            "checkpoint_id": "T45_UNIFORM_FINAL_BASE_FINAL",
            "source_checkpoint": "T32_FINAL",
            "step": 2_007_040,
            **receipt(final_target_path),
        },
    ]
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            conditions,
            policies,
            t41["fits"],
            t41["commands_x_m_s"],
            int(t41["seed"]),
        )
    finally:
        sys.path.pop(0)
    repository_inputs = {
        "runner": RUNNER,
        "matrix_helper": MATRIX_HELPER,
        "worker": WORKER,
        "adapter": ADAPTER,
        "base_evaluator": BASE_EVALUATOR,
        "t6_helpers": T6_HELPERS,
        "t8_helpers": T8_HELPERS,
        "t44_result": T44_RESULT,
        "t43_preregistration": T43_PREREG,
        "t39_preregistration": T39_PREREG,
        "t41_preregistration": T41_PREREG,
    }
    checks = {
        "t44_selected_final_base_by_frozen_precedence": (
            t44["status"] == "PASS_T44_CORRECTED_FORWARD_ONE_BLOCK_CAUSE"
            and t44["decision"]
            == "EARN_T45_HALF_WITH_FINAL_BASE_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
            and t44["summary"]["selected_final_groups"] == ["base"]
        ),
        "half_target_changes_exactly_base": half_changes == base_names,
        "final_target_is_bit_exact_identity": (
            sha256(final_target_path) == sha256(final_source_path)
            and final_changes == []
        ),
        "target_endpoints_differ_exactly_adapter": (
            endpoint_changes == adapter_names
        ),
        "target_endpoints_are_not_duplicates": (
            sha256(half_target_path) != sha256(final_target_path)
        ),
        "graph_topology_exact_across_sources_and_targets": (
            graph_signature(half_source_model)
            == graph_signature(final_source_model)
            == graph_signature(half_target_model)
            == graph_signature(final_target_model)
        ),
        "normalizer_remains_uniform_half_values": all(
            np.array_equal(
                half_target_values[name], final_target_values[name]
            )
            for name in ("obs_mean", "obs_std")
        ),
        "conditions_are_exactly_r2_one_through_three": (
            [item["id"] for item in conditions]
            == [
                "FLOOR_FRICTION_LO",
                "FLOOR_FRICTION_HI",
                "JOINT_FRICTIONLOSS_LO",
            ]
        ),
        "condition_two_is_exact_nominal_boundary": (
            conditions[1]
            == {
                "condition_index": 2,
                "id": "FLOOR_FRICTION_HI",
                "override": {"floor_friction": 1.0},
            }
        ),
        "matrix_exactly_48_cells": len(plan) == 48,
        "all_repository_inputs_present": all(
            path.is_file() for path in repository_inputs.values()
        ),
        "behavior_cells_zero": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t45_uniform_final_base_qualification_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T45_UNIFORM_FINAL_BASE_QUALIFICATION"
            if not failed
            else "HOLD_T45_UNIFORM_FINAL_BASE_QUALIFICATION_PREREGISTRATION"
        ),
        "question": (
            "Does the uniform rule 'use final feed-forward base values at "
            "both checkpoints' preserve nominal behavior and pass R2 "
            "conditions 1-3 while retaining distinct recurrent adapters?"
        ),
        "mechanism": {
            "uniform_rule": (
                "Use exact T32-final base initializers at both checkpoints; "
                "preserve each checkpoint's recurrent adapter and the "
                "already-uniform T32-half observation normalizer."
            ),
            "half_changed_initializers": half_changes,
            "final_changed_initializers": final_changes,
            "endpoint_differing_initializers": endpoint_changes,
            "checkpoint_endpoints_distinct": True,
            "training_steps": 0,
            "hosted_compute_units": 0,
        },
        "policies": policies,
        "fits": t41["fits"],
        "calibrator": t41["calibrator"],
        "reference_feature_table": t41["reference_feature_table"],
        "playground": t41["playground"],
        "conditions": conditions,
        "commands_x_m_s": t41["commands_x_m_s"],
        "seed": t41["seed"],
        "support_handoff": t41["support_handoff"],
        "behavior_contract": t41["behavior_contract"],
        "protection_contract": t41["protection_contract"],
        "matrix": {
            "conditions": 3,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 48,
            "plan_sha256": hashlib.sha256(
                json.dumps(
                    plan,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            "strictly_sequential_conditions": True,
            "stop_after_first_failed_condition": True,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "condition_two_is_nominal_matrix": True,
        },
        "decision_rule": {
            "pass": (
                "All 48 cells across conditions 1-3 are green; this "
                "requalifies nominal through condition 2 and the first "
                "failed robustness boundary through condition 3."
            ),
            "pass_decision": (
                "EARN_T45_R2_CONDITIONS_4_TO_20_PREREGISTRATION"
            ),
            "fail_decision": (
                "CLOSE_T45_UNIFORM_FINAL_BASE_TRANSFORM"
            ),
            "no_retry": True,
            "no_checkpoint_selection": True,
        },
        "repository_inputs": {
            name: receipt(path)
            for name, path in repository_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_48_cell_cpu_qualification": not failed,
            "later_robustness_preregistration": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T45 uniform final-base qualification",
                "",
                f"- Status: `{value['status']}`",
                "- Uniform base: exact final-checkpoint values",
                "- Recurrent adapters: distinct half/final values",
                "- Observation normalizer: uniform half values",
                "- Qualification: conditions 1-3, 48-cell ceiling",
                "- Condition 2 is the exact nominal boundary",
                "- All 48 required; stop at first failed condition",
                "- Training/Colab/Gate 5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
