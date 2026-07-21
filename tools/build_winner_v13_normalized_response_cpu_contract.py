#!/usr/bin/env python3
"""Freeze the Winner-v13 normalized-response zero-cell CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v13_normalized_response_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT_20260721.md"
DIAGNOSTIC = ANALYSIS / "winner_v12_calibrator_hold_diagnostic_result.json"
EXPECTED_CHECKS = [
    "exact_80_episode_training_population",
    "valid_transition_count_nonzero",
    "contact_targets_exactly_one",
    "contact_targets_normalize_to_exact_zero",
    "zero_contact_prediction_has_exact_zero_error",
    "normalized_initial_loss_below_raw_initial_loss",
    "one_update_reduces_same_batch_normalized_loss",
    "all_stage1_gradients_nonzero",
    "one_adam_update_exact",
    "action_head_bit_exact",
    "exported_action_exact_zero",
    "onnx_abi_exact",
    "onnx_training_only_tensors_absent",
    "onnx_jax_error_at_most_1e_7",
    "onnx_previous_action_chain_exact",
]
STATIC_SOURCES = {
    "builder": Path("tools/build_winner_v13_normalized_response_cpu_contract.py"),
    "runner": Path("tools/run_winner_v13_normalized_response_cpu_contract.py"),
    "tests": Path("tests/test_winner_v13_normalized_response_cpu_contract.py"),
    "workflow": Path(
        ".github/workflows/winner-v13-normalized-response-cpu-contract.yml"
    ),
    "hold_diagnostic_result": Path(
        "outputs/analysis/winner_v12_calibrator_hold_diagnostic_result.json"
    ),
    "formal_support_result": Path(
        "outputs/analysis/winner_v12_calibrator_support_gate_result.json"
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


def validate_selected_evidence(value: dict[str, Any]) -> None:
    findings = value.get("findings", {})
    if (
        value.get("status") != "PASS_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
        or value.get("decision") != "DIAGNOSTIC_ONLY_DO_NOT_TRAIN_OR_DEPLOY"
        or findings.get("contact_floor_dominates_all_predictor_aggregates") is not True
        or findings.get("noncontact_predictor_beats_constant_all_aggregates") is not False
        or findings.get("graph_fail_zero_pass_count") != 10
        or findings.get("graph_fail_zero_fail_count") != 20
        or value.get("execution", {}).get("training_steps") != 0
        or value.get("execution", {}).get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v12 HOLD diagnosis no longer selects this correction")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v13 CPU contract: {path}")
    diagnostic = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
    validate_selected_evidence(diagnostic)
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v13.normalized_response_cpu_contract.v1",
        "status": "FROZEN_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_CELL_CPU_UPDATE_ONLY",
        "evidence_selected_change": {
            "only_objective_change": (
                "The auxiliary head predicts normalized response coordinates directly; "
                "the recurrent state equation, deployable action head, 115/14/64 ABI, "
                "action bounds, observation fields, and simulator remain unchanged."
            ),
            "contact_mechanism": (
                "For obs[97:99], raw target=mean=1 and std=float32(1e-6), so the "
                "normalized target is exact zero and zero prediction has exact zero error."
            ),
            "why_not_drop_contacts_only": (
                "The frozen diagnostic found 48-D learned MSE 58-59 versus constant "
                "0.17, so the correction must repair the whole coordinate system rather "
                "than merely omit the two dominant fields."
            ),
            "support_controller_deferred": (
                "Twenty formal failures also failed under zero action. No Stage-2 "
                "controller is trained until this representation contract passes."
            ),
        },
        "frozen_cpu_proof": {
            "population": "the exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "optimizer_updates": 1,
            "seed": 60720,
            "rollout_seed": 120120,
            "required_checks": EXPECTED_CHECKS,
            "forbidden": [
                "full Stage-1 training",
                "Stage-2 support training",
                "heldout or formal support evaluation",
                "locomotion training",
                "checkpoint selection",
                "robot or RDK access",
            ],
        },
        "pass_rule": (
            "Every required check must pass. A pass authorizes only a separate "
            "normalized-response Stage-1 training preregistration."
        ),
        "execution_now": {
            "cpu_contract_optimizer_updates": 0,
            "full_training_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate normalized-response Stage-1 preregistration",
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
                "# Winner-v13 normalized-response CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Optimizer updates now: `0`",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "The contract changes only the training-only response coordinate",
                "system and requires one CPU update plus an unchanged deployable ABI",
                "before any full encoder training may be preregistered.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
