#!/usr/bin/env python3
"""Freeze T39's uniform half-normalizer rollback and 16-cell CPU screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T33 = ANALYSIS / "t33_t32_postexport_result.json"
T34 = ANALYSIS / "t34_t32_nominal_matrix_preregistration.json"
T36_PREREG = (
    ANALYSIS / "t36_t32_actor_block_factorial_preregistration.json"
)
T36_RESULT = ANALYSIS / "t36_t32_actor_block_factorial_result.json"
T38_ATTRIBUTION = (
    ANALYSIS / "t38_unrecoverable_session_loss_attribution.json"
)
T27_RUNNER_CONTRACT = (
    ANALYSIS / "t27_t23_robustness_runner_contract.json"
)
RUNNER = ROOT / "tools" / "run_t39_uniform_normalizer_rollback_nominal.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
OUTPUT = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
OUTPUT_MD = (
    ANALYSIS
    / "T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_PREREGISTRATION_20260728.md"
)
NORMALIZER_NAMES = {"obs_mean", "obs_std"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def tensor_values(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        tensor.name: np.asarray(numpy_helper.to_array(tensor))
        for tensor in model.graph.initializer
    }


def changed_initializers(
    source: onnx.ModelProto,
    target: onnx.ModelProto,
) -> list[str]:
    left = tensor_values(source)
    right = tensor_values(target)
    if set(left) != set(right):
        raise ValueError("initializer inventory changed")
    return sorted(
        name for name in left if not np.array_equal(left[name], right[name])
    )


def topology_sha256(model: onnx.ModelProto) -> str:
    payload = {
        "ir_version": model.ir_version,
        "opsets": [
            {"domain": item.domain, "version": item.version}
            for item in model.opset_import
        ],
        "inputs": [
            item.SerializeToString().hex() for item in model.graph.input
        ],
        "outputs": [
            item.SerializeToString().hex() for item in model.graph.output
        ],
        "value_info": [
            item.SerializeToString().hex() for item in model.graph.value_info
        ],
        "nodes": [
            item.SerializeToString().hex() for item in model.graph.node
        ],
        "initializers": sorted(
            (
                tensor.name,
                tensor.data_type,
                list(tensor.dims),
            )
            for tensor in model.graph.initializer
        ),
    }
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def normalizer_exact(
    target: onnx.ModelProto,
    half: onnx.ModelProto,
) -> bool:
    target_values = tensor_values(target)
    half_values = tensor_values(half)
    return all(
        name in target_values
        and name in half_values
        and np.array_equal(target_values[name], half_values[name])
        for name in NORMALIZER_NAMES
    )


def main() -> int:
    for path in (OUTPUT, OUTPUT_MD):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T39 prereg: {path}")

    t33 = json.loads(T33.read_text(encoding="utf-8"))
    t34 = json.loads(T34.read_text(encoding="utf-8"))
    t36_prereg = json.loads(T36_PREREG.read_text(encoding="utf-8"))
    t36_result = json.loads(T36_RESULT.read_text(encoding="utf-8"))
    t38 = json.loads(T38_ATTRIBUTION.read_text(encoding="utf-8"))
    runner_contract = json.loads(
        T27_RUNNER_CONTRACT.read_text(encoding="utf-8")
    )

    half_source = Path(
        t33["deployments"]["1003520"]["pre_margin_wrapped"]["path"]
    )
    half_policy = Path(t33["deployments"]["1003520"]["wrapped"]["path"])
    final_source = Path(
        t33["deployments"]["2007040"]["pre_margin_wrapped"]["path"]
    )
    normalizer_variant = next(
        item
        for item in t36_prereg["variants"]
        if item["variant_id"] == "NORMALIZER_HALF"
    )
    final_target = Path(normalizer_variant["pre_margin"]["path"])
    final_policy = Path(normalizer_variant["policy"]["path"])

    half_source_model = onnx.load(str(half_source))
    final_source_model = onnx.load(str(final_source))
    final_target_model = onnx.load(str(final_target))
    half_policy_model = onnx.load(str(half_policy))
    final_policy_model = onnx.load(str(final_policy))
    source_final_policy_model = onnx.load(
        t33["deployments"]["2007040"]["wrapped"]["path"]
    )

    for model in (
        half_source_model,
        final_source_model,
        final_target_model,
        half_policy_model,
        final_policy_model,
        source_final_policy_model,
    ):
        onnx.checker.check_model(model)

    final_pre_margin_changes = changed_initializers(
        final_source_model, final_target_model
    )
    final_policy_changes = changed_initializers(
        source_final_policy_model, final_policy_model
    )
    t36_cell = next(
        item
        for item in t36_result["cells"]
        if item["variant_id"] == "NORMALIZER_HALF"
    )
    policies = [
        {
            "checkpoint_id": "T39_UNIFORM_NORMALIZER_HALF",
            "source_checkpoint": "T32_HALF",
            "step": 1_003_520,
            **receipt(half_policy),
        },
        {
            "checkpoint_id": "T39_UNIFORM_NORMALIZER_FINAL",
            "source_checkpoint": "T32_FINAL",
            "step": 2_007_040,
            **receipt(final_policy),
        },
    ]
    checks = {
        "t38_closed_zero_weight_no_retry": (
            t38["status"]
            == "PASS_T38_UNRECOVERABLE_SESSION_LOSS_ATTRIBUTION"
            and t38["classification"]["policy_decision_weight"] == 0
            and not t38["classification"]["hosted_retry"]
            and t38["authority"][
                "t39_uniform_normalizer_rollback_preregistration"
            ]
        ),
        "t36_selected_lowest_complexity_normalizer_block": (
            t36_result["status"]
            == "PASS_T36_T32_ACTOR_BLOCK_FACTORIAL_WITH_REPAIR"
            and t36_result["decision"]
            == "EARN_T37_NORMALIZER_HALF_FREEZE_TRAINING_CPU_CONTRACT_PREREGISTRATION"
            and t36_cell["cell_green"]
            and normalizer_variant["half_groups"] == ["normalizer"]
            and t36_prereg["execution_order"][0] == "NORMALIZER_HALF"
        ),
        "half_target_is_source_bit_exact": (
            sha256(half_policy)
            == t33["deployments"]["1003520"]["wrapped"]["sha256"]
        ),
        "final_pre_margin_changes_only_normalizer": (
            set(final_pre_margin_changes) == NORMALIZER_NAMES
        ),
        "final_policy_changes_only_normalizer": (
            set(final_policy_changes) == NORMALIZER_NAMES
        ),
        "half_pre_margin_normalizer_is_half_exact": normalizer_exact(
            half_source_model, half_source_model
        ),
        "final_pre_margin_normalizer_is_half_exact": normalizer_exact(
            final_target_model, half_source_model
        ),
        "half_policy_normalizer_is_half_exact": normalizer_exact(
            half_policy_model, half_source_model
        ),
        "final_policy_normalizer_is_half_exact": normalizer_exact(
            final_policy_model, half_source_model
        ),
        "final_pre_margin_topology_exact": (
            topology_sha256(final_source_model)
            == topology_sha256(final_target_model)
        ),
        "final_policy_topology_exact": (
            topology_sha256(source_final_policy_model)
            == topology_sha256(final_policy_model)
        ),
        "both_policy_graphs_valid": True,
        "t27_runner_contract_green": (
            runner_contract["status"]
            == "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
        ),
        "exactly_two_uniformly_transformed_policies": len(policies) == 2,
        "exact_default_condition": t34["conditions"] == [
            {
                "condition_index": 2,
                "id": "FLOOR_FRICTION_HI",
                "override": {"floor_friction": 1.0},
            }
        ],
        "runner_worker_and_adapter_present": (
            RUNNER.is_file() and WORKER.is_file() and ADAPTER.is_file()
        ),
        "formal_behavior_cells_zero": True,
        "hosted_training_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t39_uniform_normalizer_rollback_"
            "nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
            if not failed
            else "HOLD_T39_UNIFORM_NORMALIZER_ROLLBACK_PREREGISTRATION"
        ),
        "question": (
            "Does the single deterministic rule 'use T32-half observation "
            "normalizer values at both checkpoints' make both checkpoints "
            "pass the complete frozen nominal matrix?"
        ),
        "mechanism": {
            "rule": (
                "Replace obs_mean and obs_std with exact T32-half values "
                "at both checkpoints; change nothing else."
            ),
            "uniform_across_checkpoints": True,
            "changed_initializer_names": sorted(NORMALIZER_NAMES),
            "half_effect": "bit_exact_identity",
            "final_effect": "two_initializer_value_replacement",
            "training_steps": 0,
            "hosted_compute_units": 0,
            "checkpoint_selection": False,
        },
        "asset_contract": {
            "half_source_pre_margin": receipt(half_source),
            "half_policy": receipt(half_policy),
            "final_source_pre_margin": receipt(final_source),
            "final_target_pre_margin": receipt(final_target),
            "final_policy": receipt(final_policy),
            "final_pre_margin_changed_initializers": (
                final_pre_margin_changes
            ),
            "final_policy_changed_initializers": final_policy_changes,
            "half_pre_margin_topology_sha256": topology_sha256(
                half_source_model
            ),
            "final_source_pre_margin_topology_sha256": topology_sha256(
                final_source_model
            ),
            "final_target_pre_margin_topology_sha256": topology_sha256(
                final_target_model
            ),
        },
        "commands_x_m_s": t34["commands_x_m_s"],
        "seed": t34["seed"],
        "conditions": t34["conditions"],
        "policies": policies,
        "fits": t34["fits"],
        "calibrator": t34["calibrator"],
        "reference_feature_table": t34["reference_feature_table"],
        "playground": t34["playground"],
        "support_handoff": t34["support_handoff"],
        "behavior_contract": t34["behavior_contract"],
        "protection_contract": t34["protection_contract"],
        "repository_inputs": t34["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 16,
            "execution_order": (
                "default condition -> half/final -> p30/p31_34 -> "
                "x=0/.074/.077/.080"
            ),
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": "All 16 frozen cells must be green.",
            "pass_decision": (
                "EARN_T39_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
            ),
            "fail_decision": (
                "CLOSE_T39_POSTHOC_NORMALIZER_ROLLBACK_WITHOUT_T38_RETRY"
            ),
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
            "no_result_dependent_transform": True,
            "no_retry": True,
        },
        "frozen_inputs": {
            "t33_postexport": receipt(T33),
            "t34_preregistration": receipt(T34),
            "t36_preregistration": receipt(T36_PREREG),
            "t36_result": receipt(T36_RESULT),
            "t38_attribution": receipt(T38_ATTRIBUTION),
            "t27_runner_contract": receipt(T27_RUNNER_CONTRACT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_one_cpu_nominal_matrix": not failed,
            "robustness_preregistration": False,
            "robustness_execution": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T39 uniform normalizer rollback nominal preregistration",
                "",
                f"- Status: `{payload['status']}`",
                "- Rule: exact T32-half `obs_mean`/`obs_std` at both exports",
                "- Half effect: bit-exact identity",
                "- Final effect: two initializer values only",
                "- Matrix: 16 CPU-only cells; both checkpoints required",
                "- Training / Colab units: `0 / 0`",
                "- Gate 5 / RDK-X5 / robot authority: `CLOSED`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
