#!/usr/bin/env python3
"""Freeze the isolated Winner-v13 normalized-response Stage-1 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v13_normalized_response_stage1_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_20260721.md"
CPU_RESULT = ANALYSIS / "winner_v13_normalized_response_cpu_contract_result.json"
EXPECTED_CHECKS = [
    "exact_100_optimizer_updates",
    "exact_100_immutable_snapshots",
    "half_and_final_evaluated",
    "both_checkpoints_pass_heldout_gate",
    "action_head_bit_exact",
]
CHECKPOINT_CHECKS = [
    "exact_32_heldout_cells",
    "heldout_repeat_bit_exact",
    "learned_prediction_beats_constant_per_plant",
    "all_16_plant_contexts_separate",
    "checker_onnx_action_exact_zero",
    "checker_onnx_hidden_at_most_1e_7",
    "deployable_onnx_abi_exact",
    "deployable_onnx_training_only_tensors_absent",
    "deployable_onnx_chain_at_most_1e_7",
]
STATIC_SOURCES = {
    "builder": Path(
        "tools/build_winner_v13_normalized_response_stage1_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v13_normalized_response_stage1.py"),
    "tests": Path("tests/test_winner_v13_normalized_response_stage1.py"),
    "workflow": Path(
        ".github/workflows/winner-v13-normalized-response-stage1.yml"
    ),
    "v13_cpu_result": Path(
        "outputs/analysis/winner_v13_normalized_response_cpu_contract_result.json"
    ),
    "v13_cpu_contract": Path(
        "outputs/analysis/winner_v13_normalized_response_cpu_contract.json"
    ),
    "v13_training_primitives": Path(
        "patches/winner_v13_normalized_calibrator_training.py"
    ),
    "v12_training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def source_manifest() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in STATIC_SOURCES.items()
    }


def validate_cpu_authorization(value: dict[str, Any]) -> None:
    if (
        value.get("status")
        != "PASS_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
        or value.get("execution")
        != {
            "cpu_contract_optimizer_updates": 1,
            "full_training_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v13 CPU proof does not authorize this gate")
    proof = value.get("objective_evidence", {})
    graph = value.get("graph_contract", {})
    if not (
        proof.get("v13_normalized_coordinate_initial_loss", float("inf")) < 1.0
        and proof.get("v13_normalized_coordinate_post_update_loss", float("inf"))
        < proof.get("v13_normalized_coordinate_initial_loss", float("-inf"))
        and proof.get("v12_raw_coordinate_initial_loss", 0.0) > 1.0e9
        and graph.get("abi_exact") is True
        and graph.get("inputs")
        == [
            {"name": "obs", "shape": [1, 115]},
            {"name": "previous_action", "shape": [1, 14]},
            {"name": "h_in", "shape": [1, 64]},
        ]
        and graph.get("outputs")
        == [
            {"name": "calibration_actions", "shape": [1, 14]},
            {"name": "previous_action_out", "shape": [1, 14]},
            {"name": "h_out", "shape": [1, 64]},
        ]
    ):
        raise ValueError("Winner-v13 CPU proof payload changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v13 Stage-1: {path}")
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    validate_cpu_authorization(cpu_result)
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v13.normalized_response_stage1_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1",
        "decision": "AUTHORIZE_ONE_100_UPDATE_STAGE1_RUN_ONLY",
        "causal_hypothesis": (
            "Winner-v12 failed because its auxiliary response head was trained in a "
            "numerically broken raw-coordinate objective. Predicting the same 50 response "
            "fields directly in frozen normalized coordinates should make the recurrent "
            "state configuration-sensitive before any support action is learned."
        ),
        "frozen_training": {
            "stage": "response encoder only",
            "optimizer_updates": 100,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "training_episode_slots": 2_000_000,
            "parameter_seed": 60720,
            "training_root_seed": 120120,
            "learning_rate": 0.0003,
            "trainable_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "action_head": "initialized at exact zero and bit-exact frozen",
            "normalization": (
                "target mean/std frozen from update-0 training population; auxiliary "
                "head predicts normalized targets directly"
            ),
            "persistent_snapshots": "atomic readback-verified snapshot after every update",
            "persistent_checkpoints": {"half": 50, "final": 100},
        },
        "heldout_gate": {
            "population": "exact 16 HELDOUT configurations x P30/P31_34",
            "checkpoints": ["half", "final"],
            "ticks_per_cell": 250,
            "cells": 64,
            "deterministic_repeat_cells": 64,
            "root_seed": 131313,
            "required_per_checkpoint_checks": CHECKPOINT_CHECKS,
            "predictor_rule": (
                "Learned all-50 normalized MSE must be strictly below the exact zero "
                "normalized-coordinate predictor independently for P30 and P31_34."
            ),
            "observability_rule": (
                "At the final valid tick, h_out(P30) and h_out(P31_34) must differ by "
                "L-infinity > 1e-7 for every one of the 16 heldout configurations."
            ),
            "repeat_rule": "batch arrays, episode receipts, and rollout evidence bit-exact",
            "onnx_rule": (
                "Action remains exact zero; 115/14/64 ABI and JAX/ONNX recurrent chain "
                "agree within 1e-7; training-only tensors remain absent."
            ),
        },
        "required_run_checks": EXPECTED_CHECKS,
        "pass_rule": (
            "Every run-level and checkpoint-level check must pass at both half and final. "
            "No nearest or best checkpoint may be promoted."
        ),
        "stop_rules": [
            "A HOLD does not authorize parameter tuning or Stage-2 support training.",
            "A PASS authorizes only a separately preregistered support-controller run.",
            "No formal support, locomotion, checkpoint selection, robot, or RDK access.",
        ],
        "execution_now": {
            "stage1_optimizer_updates": 0,
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate automatic support-controller preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v13 normalized-response Stage-1 preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Training: `100` encoder-only CPU updates (`2,000,000` episode slots)",
                "- Heldout gate: half/final x 16 configurations x 2 measured plants",
                "- Repeat: all `64` evaluation cells repeated exactly",
                "- Stage-2 / formal support / locomotion / robot access: `0 / 0 / 0 / 0`",
                "",
                "The action head is frozen at exact zero. Both checkpoints must beat the",
                "zero normalized predictor under each actuator plant, separate all hidden",
                "plant pairs, reproduce bit-exactly, and preserve the deployable ONNX ABI.",
                "A pass authorizes only a separate support-controller preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
