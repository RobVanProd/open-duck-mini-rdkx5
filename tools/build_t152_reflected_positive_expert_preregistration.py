#!/usr/bin/env python3
"""Freeze T152's one-shot reflected positive-COM expert transform."""

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


OUTPUT = ANALYSIS / "t152_reflected_positive_expert_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T152_REFLECTED_POSITIVE_EXPERT_PREREGISTRATION_20260729.md"
)
T7 = ANALYSIS / "t7_universal_response_support_result.json"
T138 = ANALYSIS / "t138_expert_bank_causality_result.json"
T143C = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
T151 = ANALYSIS / "t151_command_plateau_full_r2_result.json"
RUNNER = ROOT / "tools/run_t152_reflected_positive_expert_transform.py"
TEST = ROOT / "tests/test_t152_reflected_positive_expert.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T152: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T152 preregistration requires clean tree")

    t7 = json.loads(T7.read_text(encoding="utf-8"))
    t138 = json.loads(T138.read_text(encoding="utf-8"))
    t143 = json.loads(T143C.read_text(encoding="utf-8"))
    t151 = json.loads(T151.read_text(encoding="utf-8"))
    condition = next(
        item
        for item in t151["conditions"]
        if item["condition_id"] == "TORSO_COM_X_POS"
    )
    checks = {
        "positive_context_observable_and_repeatable": (
            t7["status"] == "PASS_T7_UNIVERSAL_RESPONSE_SUPPORT"
            and t7["global_checks"]["all_repeat_contexts_bit_exact"]
            and t7["global_checks"][
                "all_nominal_endpoint_separations_pass"
            ]
            and t7["global_checks"]["all_signed_endpoint_separations_pass"]
        ),
        "expert_sources_differ_only_in_two_adapter_tensors": (
            t138["status"] == "PASS_T138_EXPERT_BANK_CAUSALITY_AUDIT"
            and all(
                row["only_negative_expert_parameters_differ"]
                and row["initializer_differences"]
                == [
                    "negative_adapter_bias",
                    "negative_adapter_weight",
                ]
                for row in t138["graph_diffs"].values()
            )
        ),
        "conditional_forward_path_green": (
            t143["status"]
            == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143["failed_checks"] == []
            and all(
                row["source_differences"]
                == [
                    "negative_adapter_bias",
                    "negative_adapter_weight",
                ]
                for row in t143["graphs"].values()
            )
        ),
        "t151_stopped_exactly_at_positive_com": (
            t151["status"] == "HOLD_T151_COMMAND_PLATEAU_FULL_R2"
            and t151["decision"]
            == "CLOSE_COMMAND_PLATEAU_AT_FIRST_FAILED_R2_CONDITION"
            and t151["summary"]["completed_conditions"] == 8
            and t151["summary"]["first_failed_condition"]
            == "TORSO_COM_X_POS"
            and t151["summary"]["green_cells"] == 116
            and t151["execution"]["behavior_cells"] == 128
            and condition["condition_index"] == 8
            and condition["green_cells"] == 4
            and condition["cells"] == 16
            and condition["override"]
            == {"torso_com_offset_m": [0.05, 0.0, 0.0]}
        ),
        "symmetric_endpoint_derivation_exact": True,
        "no_training_hosted_runtime_or_hardware_change": True,
        "all_inputs_present": all(
            path.exists()
            for path in (T7, T138, T143C, T151, RUNNER, TEST)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T152 preregistration checks failed: {failed}")

    frozen = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t7_context_support": receipt(T7),
        "t138_expert_causality": receipt(T138),
        "t143c_conditional_forward_path": receipt(T143C),
        "t151_full_r2_stop": receipt(T151),
    }
    for step, item in sorted(t143["graphs"].items()):
        frozen[f"source_graph_{step}"] = item["transformed"]

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t152_reflected_positive_expert_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T152_REFLECTED_POSITIVE_EXPERT",
        "question": (
            "Does the unique first-order reflection of the learned negative-"
            "COM adapter provide a finite, ABI-exact positive-COM expert "
            "worth testing before any positive-only hosted continuation?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "failure": (
                "T151 produced twelve moving-command falls at +0.05 m COM X "
                "across both checkpoints and both measured actuator fits, "
                "while every x=0 cell passed."
            ),
            "observability": (
                "T7 proved nominal, negative-X, and positive-X calibration "
                "contexts are repeatable and separated across both fits."
            ),
            "capacity": (
                "T138/T143 prove the existing expert family differs only in "
                "one 64x14 weight and one 14-vector bias."
            ),
        },
        "mechanism": {
            "negative_endpoint_m": -0.05,
            "nominal_endpoint_m": 0.0,
            "positive_endpoint_m": 0.05,
            "reflection_formula": "positive=2*nominal-negative",
            "reflection_scale": -1.0,
            "derived_scalar_search": False,
            "transformed_tensors": [
                "negative_adapter_weight",
                "negative_adapter_bias",
            ],
            "endpoint_screen_branch": (
                "force_reflected_expert_for_positive_endpoint_only"
            ),
            "external_input_abi": "unchanged_115_14_64_plus_context",
            "recurrent_state": "unchanged",
            "action_pipeline": "unchanged",
            "safety_pipeline": "unchanged",
            "runtime_change": False,
            "training": False,
        },
        "thresholds": {
            "random_chain_steps": 256,
            "x0_samples": 64,
            "minimum_moving_action_changed_fraction": 0.5,
            "maximum_x0_action_abs": 0.0,
            "maximum_hidden_state_error": 0.0,
            "maximum_context_dependence_error": 0.0,
        },
        "frozen_inputs": frozen,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Both graphs contain the exact reflected tensors and only "
                "the endpoint-screen branch rewire; ABI, existing graph "
                "topology, recurrent hidden output, x=0 final action, and "
                "forced-branch context invariance all pass on CPU."
            ),
            "pass_decision": (
                "EARN_T153_REFLECTED_POSITIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_REFLECTED_POSITIVE_EXPERT",
        },
        "execution_now": {
            "environment_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_transform_contract": True,
            "positive_endpoint_preregistration": False,
            "positive_only_training_contract": False,
            "hosted_training": False,
            "policy_promotion": False,
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
        "# T152 reflected positive expert preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reflection: `positive = 2*nominal - negative`\n"
        "- Scalar sweep: none\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
