#!/usr/bin/env python3
"""Preregister one Winner-v21 predictor-preserving 100-update CPU arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v21_predictor_preserving_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_TRAINING_PREREGISTRATION_20260721.md"
CPU_RESULT = ANALYSIS / "winner_v21_predictor_preserving_two_update_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v21_predictor_preserving_training_preregistration.py"),
    "runner": Path("tools/run_winner_v21_predictor_preserving_training.py"),
    "workflow": Path(".github/workflows/winner-v21-predictor-preserving-training.yml"),
    "tests": Path("tests/test_winner_v21_predictor_preserving_training.py"),
    "importer": Path("tools/import_winner_v21_predictor_preserving_training.py"),
    "importer_tests": Path("tests/test_winner_v21_predictor_preserving_training_import.py"),
    "mechanics_v1": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "mechanics_v2": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "two_update_result": Path("outputs/analysis/winner_v21_predictor_preserving_two_update_cpu_result.json"),
    "two_update_importer": Path("tools/import_winner_v21_predictor_preserving_two_update_result.py"),
    "two_update_contract": Path("outputs/analysis/winner_v21_predictor_preserving_two_update_cpu_contract.json"),
    "winner_v20_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "winner_v15_objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "stage1_result": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v21 training preregistration")
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1["snapshot_manifest"][-1]
    if (
        cpu_result.get("status")
        != "PASS_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_PROOF"
        or cpu_result.get("decision")
        != "AUTHORIZE_SEPARATE_100_UPDATE_PREDICTOR_PRESERVING_TRAINING_PREREGISTRATION_ONLY"
        or cpu_result.get("failed_checks") != []
        or not all(cpu_result.get("checks", {}).values())
        or cpu_result.get("execution", {}).get("optimizer_updates") != 2
        or cpu_result.get("predictor_scale") != 8.393629541414427e-11
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v21 training source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v21.predictor_preserving_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V21_PREDICTOR_PRESERVING_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_PREDICTOR_PRESERVING_ARM_ONLY",
        "causal_hypothesis": (
            "Winner-v20 updated the recurrent policy while freezing the Stage-1 next-response "
            "predictor, destroying predictor compatibility and weakening context encoding. "
            "Updating the existing recurrent and auxiliary leaves together with one frozen "
            "head-gradient balance should preserve response observability while optimizing "
            "the unchanged support objective."
        ),
        "single_change": {
            "reference": "Winner-v20 100-update joint recurrent arm",
            "newly_trainable_existing_leaves": [
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "optimizer_gradient": (
                "per-leaf g_ppo + float32(8.393629541414427e-11) * g_predictor"
            ),
            "predictor_scale_recomputed": False,
            "predictor_scale_sweep": False,
            "new_parameters": 0,
            "onnx_abi_change": False,
            "rollout_reward_population_seed_horizon_action_bound_change": False,
            "flat_transport_equation_used": False,
        },
        "frozen_training": {
            "source_stage1_snapshot_sha256": final_snapshot["sha256"],
            "source_stage1_snapshot_bytes": final_snapshot["bytes"],
            "optimizer_updates": 100,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "objective": "one_sided_negative_pitch_margin_plus_existing_next_response_predictor",
            "pitch_boundary_rad": 0.35,
            "predictor_scale": 8.393629541414427e-11,
            "predictor_scale_evaluations": 0,
            "failure_transition_reward": 0.0,
            "settled_terminal_bonus": 250.0,
            "trainable_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "action_weight",
                "action_bias",
                "training_only_log_std",
                "training_only_value_weight",
                "training_only_value_bias",
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "stored_successor_rule": (
                "valid transition at t and valid sampled successor at t+1; terminal tick 249 excluded"
            ),
            "hidden_replay_max_abs_error": 1.0e-6,
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "persistent_checkpoints": {"half": 50, "final": 100},
        },
        "stop_rules": [
            "stop if sampled-tick hidden replay exceeds 1e-6",
            "stop if reward, action boundary, masks, population, or seeds differ",
            "stop if any of the twelve composed gradients or deltas is zero",
            "stop if any predictor successor mask is empty or disagrees with the stored batch",
            "stop if any digest-protected twelve-leaf snapshot fails readback",
            "do not run the formal support gate from this workflow",
            "do not select a checkpoint from training metrics",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "pass_authorizes_only": (
                "a separately preregistered unchanged support/context gate over both half and final checkpoints"
            ),
            "checkpoint_rule": (
                "both checkpoints must pass every unchanged support cell and learned predictor must beat the constant baseline"
            ),
        },
        "not_selected": [
            "flat-transport kernel",
            "another post-policy wrapper",
            "reward, scale, or learning-rate search",
            "new observation fields or ONNX ABI",
            "manual build measurements",
        ],
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate unchanged support/context gate preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v21 predictor-preserving training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: identical Winner-v13 Stage-1 update-100 snapshot",
                "- Updates / checkpoints: `100 / 50,100`",
                "- Frozen predictor scale evaluations: `0`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "- Flat-transport equation: `not used`",
                "",
                "This is one causal arm. It adds the existing three predictor leaves to",
                "Winner-v20's nine trainable leaves and consumes the frozen explicit",
                "per-leaf gradient sum proven by the two-update CPU contract. No scale",
                "recalculation, sweep, ABI change, support gate, or robot access occurs.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
