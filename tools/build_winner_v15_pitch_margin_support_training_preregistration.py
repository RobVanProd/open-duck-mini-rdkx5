#!/usr/bin/env python3
"""Preregister one finite Winner-v15 pitch-margin support-training arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v15_pitch_margin_support_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_PREREGISTRATION_20260721.md"
CPU_RESULT = ANALYSIS / "winner_v15_pitch_margin_cpu_result.json"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v15_pitch_margin_support_training_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v15_pitch_margin_support_training.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "tests": Path("tests/test_winner_v15_pitch_margin_support_training.py"),
    "workflow": Path(".github/workflows/winner-v15-pitch-margin-support-training.yml"),
    "cpu_result": Path("outputs/analysis/winner_v15_pitch_margin_cpu_result.json"),
    "cpu_contract": Path("outputs/analysis/winner_v15_pitch_margin_cpu_contract.json"),
    "objective_attribution": Path(
        "outputs/analysis/winner_v15_pitch_margin_objective_attribution.json"
    ),
    "winner_v14_result": Path(
        "outputs/analysis/winner_v14_support_action_diagnostic_result.json"
    ),
    "stage1_result": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"
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
    "configuration_domain": Path(
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite training preregistration: {path}")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        cpu.get("status") != "PASS_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
        or cpu.get("decision")
        != "AUTHORIZE_PITCH_MARGIN_SUPPORT_TRAINING_PREREGISTRATION_ONLY"
        or cpu.get("failed_checks") != []
        or cpu.get("execution")
        != {
            "stage2_optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or cpu.get("proof", {}).get("reward", {}).get("reward_formula_bit_exact")
        is not True
        or cpu.get("proof", {}).get("reward", {}).get("nonzero_penalty_count")
        != 5911
        or cpu.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v15 CPU result does not authorize preregistration")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v15.pitch_margin_support_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_PITCH_MARGIN_SUPPORT_RUN_ONLY",
        "causal_hypothesis": (
            "Replacing only the sparse flat valid-transition reward with the bounded "
            "one-sided negative-pitch margin gives the existing response-conditioned "
            "support head early credit on the persistent negative-COM-X pitch failures."
        ),
        "source_artifact": {
            "github_run_id": 29822834921,
            "github_run_attempt": 1,
            "github_artifact_id": 8492593761,
            "artifact_zip_sha256": "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680",
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
        },
        "frozen_training": {
            "source_stage1_snapshot_sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
            "source_stage1_snapshot_bytes": 189027,
            "optimizer_updates": 100,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "objective": "one_sided_negative_pitch_margin",
            "pitch_boundary_rad": 0.35,
            "objective_scale": None,
            "failure_transition_reward": 0.0,
            "settled_terminal_bonus": 250.0,
            "trainable_leaves": [
                "action_bias",
                "action_weight",
                "training_only_log_std",
                "training_only_value_bias",
                "training_only_value_weight",
            ],
            "frozen_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "persistent_snapshots": "atomic readback-verified snapshot after every update",
            "persistent_checkpoints": {"half": 50, "final": 100},
        },
        "single_change": {
            "from": "valid transition reward = 1.0",
            "to": "1 - square(clip(max(0, -next_pitch_rad) / 0.35, 0, 1))",
            "unchanged": (
                "Stage-1 snapshot, initialization, optimizer, population, seeds, "
                "dynamics, observation, action, graph, masks, failure reward, terminal "
                "bonus, checkpoint boundaries, and future gate"
            ),
            "no_scale_search": True,
        },
        "future_gate": {
            "cells_per_checkpoint": 124,
            "checkpoints": ["half", "final"],
            "heldout_repeats_per_checkpoint": 32,
            "executed_now": False,
            "pass_rule": "all unchanged cells at both checkpoints pass; no closest selection",
        },
        "training_success_rule": (
            "Exact 100 finite updates; every reward proof and action boundary exact; "
            "Stage-1 bit-exact; every Stage-2 leaf changes; all snapshots and both "
            "115/14/64 ONNX checkpoints validate. Training metrics do not select a checkpoint."
        ),
        "execution_now": {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate unchanged 124-cell support/context gate preregistration",
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
                "# Winner-v15 pitch-margin support-training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: exact passing normalized-response Stage-1 snapshot",
                "- Updates / environments / ticks: `100 / 80 / 250`",
                "- Objective scale search: `none`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "This is a one-arm causal A/B against Winner-v13. Only the valid-transition",
                "support reward changes to the bounded negative-pitch margin. A software",
                "pass authorizes only preregistration of the complete unchanged support gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
