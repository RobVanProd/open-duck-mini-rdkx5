#!/usr/bin/env python3
"""Freeze T50's uniform half-core transform and 64-cell qualification."""

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
T49_RESULT = ANALYSIS / "t49_missing_combined_adapter_control_result.json"
T45_PREREG = (
    ANALYSIS
    / "t45_uniform_final_base_qualification_preregistration.json"
)
T41_PREREG = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
RUNNER = ROOT / "tools" / "run_t50_uniform_half_core_qualification.py"
MATRIX_HELPER = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
BASE_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T6_HELPERS = ROOT / "tools" / "run_t6_corrected_robustness_screen.py"
T8_HELPERS = ROOT / "tools" / "run_t8_state_coherent_handoff.py"
OUTPUT = (
    ANALYSIS / "t50_uniform_half_core_qualification_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T50_UNIFORM_HALF_CORE_QUALIFICATION_PREREGISTRATION_20260728.md"
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


def graph_signature(model: onnx.ModelProto) -> list[tuple[Any, ...]]:
    return [
        (
            node.op_type,
            node.domain,
            tuple(node.input),
            tuple(node.output),
        )
        for node in model.graph.node
    ]


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
        raise ValueError("T50 initializer inventory changed")
    return sorted(
        name
        for name in source
        if not np.array_equal(source[name], target[name])
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T50 prereg: {path}")
    t49 = json.loads(T49_RESULT.read_text(encoding="utf-8"))
    t45 = json.loads(T45_PREREG.read_text(encoding="utf-8"))
    t41 = json.loads(T41_PREREG.read_text(encoding="utf-8"))
    selected = next(
        item
        for item in t49["cells"]
        if item["variant_id"] == "FINAL_WITH_HALF_CORE"
    )
    half_source_path = Path(t45["policies"][0]["path"])
    final_source_path = Path(t45["policies"][1]["path"])
    half_target_path = half_source_path
    final_target_path = Path(selected["policy"]["path"])
    half_source_model, half_source_values = values(half_source_path)
    final_source_model, final_source_values = values(final_source_path)
    half_target_model, half_target_values = values(half_target_path)
    final_target_model, final_target_values = values(final_target_path)
    half_changes = changed(half_source_values, half_target_values)
    final_changes = changed(final_source_values, final_target_values)
    endpoint_changes = changed(half_target_values, final_target_values)
    core_names = [
        "adapter_hidden_bias",
        "adapter_hidden_weight",
        "adapter_obs_weight",
    ]
    head_names = ["adapter_bias", "adapter_weight"]
    conditions = t41["conditions"][:4]
    policies = [
        {
            "checkpoint_id": "T50_UNIFORM_HALF_CORE_HALF",
            "source_checkpoint": "T32_HALF",
            "step": 1_003_520,
            **receipt(half_target_path),
        },
        {
            "checkpoint_id": "T50_UNIFORM_HALF_CORE_FINAL",
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
            t45["fits"],
            t45["commands_x_m_s"],
            int(t45["seed"]),
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
        "t49_result": T49_RESULT,
        "t45_preregistration": T45_PREREG,
        "t41_r2_source": T41_PREREG,
    }
    checks = {
        "t49_selected_half_core_by_frozen_precedence": (
            t49["status"]
            == "PASS_T49_COMPLETED_ADAPTER_ONE_SUBBLOCK_CAUSE"
            and t49["decision"]
            == "EARN_T50_FINAL_WITH_HALF_CORE_"
            "UNIFORM_TRANSFORM_PREREGISTRATION"
            and t49["summary"]["selected_half_groups"] == ["core"]
        ),
        "half_target_is_bit_exact_identity": (
            sha256(half_target_path) == sha256(half_source_path)
            and half_changes == []
        ),
        "final_target_changes_exactly_core": (
            final_changes == core_names
        ),
        "target_endpoints_differ_exactly_head": (
            endpoint_changes == head_names
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
        "recurrent_core_is_uniform_half_values": all(
            np.array_equal(
                half_target_values[name], final_target_values[name]
            )
            for name in core_names
        ),
        "conditions_are_exactly_r2_one_through_four": (
            [item["condition_index"] for item in conditions]
            == [1, 2, 3, 4]
        ),
        "matrix_exactly_64_cells": len(plan) == 64,
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
            "open_duck.t50_uniform_half_core_qualification_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T50_UNIFORM_HALF_CORE_QUALIFICATION"
            if not failed
            else "HOLD_T50_UNIFORM_HALF_CORE_QUALIFICATION_PREREGISTRATION"
        ),
        "question": (
            "Does the uniform rule 'use half recurrent-adapter core values "
            "at both checkpoints' preserve conditions 1-3 and repair "
            "condition 4 while retaining distinct output heads?"
        ),
        "mechanism": {
            "uniform_rule": (
                "Use exact T32-half adapter recurrent-core initializers at "
                "both checkpoints; preserve each checkpoint's adapter "
                "output head, final feed-forward base, and half normalizer."
            ),
            "half_changed_initializers": half_changes,
            "final_changed_initializers": final_changes,
            "endpoint_differing_initializers": endpoint_changes,
            "checkpoint_endpoints_distinct": True,
            "training_steps": 0,
            "hosted_compute_units": 0,
        },
        "policies": policies,
        "fits": t45["fits"],
        "calibrator": t45["calibrator"],
        "reference_feature_table": t45["reference_feature_table"],
        "playground": t45["playground"],
        "conditions": conditions,
        "commands_x_m_s": t45["commands_x_m_s"],
        "seed": t45["seed"],
        "support_handoff": t45["support_handoff"],
        "behavior_contract": t45["behavior_contract"],
        "protection_contract": t45["protection_contract"],
        "matrix": {
            "conditions": 4,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 64,
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
                "All 64 cells across conditions 1-4 are green; this "
                "requalifies nominal and both encountered R2 boundaries."
            ),
            "pass_decision": (
                "EARN_T50_R2_CONDITIONS_5_TO_20_PREREGISTRATION"
            ),
            "fail_decision": (
                "CLOSE_T50_UNIFORM_HALF_CORE_TRANSFORM"
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
            "execute_one_64_cell_cpu_qualification": not failed,
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
                "# T50 uniform half-core qualification",
                "",
                f"- Status: `{value['status']}`",
                "- Recurrent core: exact half-checkpoint values",
                "- Output heads: distinct half/final values",
                "- Base: uniform final; normalizer: uniform half",
                "- Qualification: conditions 1-4, 64-cell ceiling",
                "- All 64 required; stop at first failed condition",
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
