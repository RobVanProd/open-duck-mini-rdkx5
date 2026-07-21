#!/usr/bin/env python3
"""Preregister the one Winner-v20 joint recurrent 100-update A/B arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v20_joint_recurrent_support_training_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_PREREGISTRATION_20260721.md"
)
CPU_RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_v2_result.json"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_attribution.json"
CPU_HOLD = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_hold_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v20_joint_recurrent_support_training_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v20_joint_recurrent_support_training.py"),
    "workflow": Path(
        ".github/workflows/winner-v20-joint-recurrent-support-training.yml"
    ),
    "tests": Path("tests/test_winner_v20_joint_recurrent_support_training.py"),
    "mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_result": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_cpu_v2_result.json"
    ),
    "cpu_result_importer": Path(
        "tools/import_winner_v20_joint_recurrent_support_cpu_v2_result.py"
    ),
    "cpu_result_tests": Path(
        "tests/test_winner_v20_joint_recurrent_support_cpu_v2_import.py"
    ),
    "cpu_contract": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_cpu_contract.json"
    ),
    "mechanism_attribution": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_attribution.json"
    ),
    "one_update_hold_attribution": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_cpu_hold_attribution.json"
    ),
    "winner_v15_training_preregistration": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_preregistration.json"
    ),
    "winner_v15_training_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_result.json"
    ),
    "winner_v15_hold": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_hold_attribution.json"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite training preregistration: {path}")
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    cpu_hold = json.loads(CPU_HOLD.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1.get("snapshot_manifest", [{}])[-1]
    if (
        cpu_result.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or cpu_result.get("decision")
        != "AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY"
        or cpu_result.get("failed_checks") != []
        or not all(cpu_result.get("checks", {}).values())
        or cpu_result.get("execution", {}).get("optimizer_updates") != 2
        or cpu_result.get("authority", {}).get("joint_recurrent_training_executed")
        is not False
        or attribution.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION"
        or cpu_hold.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_HOLD_ATTRIBUTION"
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v20 training source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v20.joint_recurrent_support_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_JOINT_RECURRENT_CAUSAL_AB_ONLY",
        "causal_hypothesis": (
            "Winner-v15's exact dense support reward reached only a linear action head "
            "while freezing the deployable recurrent encoder. The two-update proof shows "
            "the existing encoder becomes trainable as soon as the zero action head opens. "
            "Full-BPTT joint PPO can therefore learn the missing temporally integrated, "
            "multi-joint negative-X recovery without an output wrapper or ABI change."
        ),
        "causal_ab": {
            "reference": "Winner-v15 action-head-only 100-update arm",
            "same": [
                "Winner-v13 Stage-1 update-100 source snapshot",
                "40 configurations x 2 hidden plants per update",
                "250 ticks and training root seed 120120",
                "one-sided negative-pitch margin reward with no scalar",
                "learning rate 0.0001 and 100 updates",
                "half/final checkpoints at updates 50/100",
                "graph-authoritative action bounds and unchanged future 124-cell gate",
            ],
            "only_variable": (
                "recompute and differentiate through the existing 64-state recurrent "
                "core instead of consuming a frozen cached hidden tensor"
            ),
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
            "objective": "one_sided_negative_pitch_margin",
            "pitch_boundary_rad": 0.35,
            "objective_scale": None,
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
            ],
            "bit_exact_frozen_leaves": [
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "hidden_replay_population": "valid_mask == 1 sampled ticks only",
            "hidden_replay_max_abs_error": 1.0e-6,
            "persistent_snapshots": (
                "atomic readback-verified snapshot after every update"
            ),
            "persistent_checkpoints": {"half": 50, "final": 100},
        },
        "stop_rules": [
            "stop if sampled-tick hidden replay exceeds 1e-6",
            "stop if reward, action boundary, masks, population, or seeds differ",
            "stop if update 1 does not reproduce the zero-head chain-rule gate",
            "stop if update 2 does not open all recurrent gradients and deltas",
            "stop if any auxiliary predictor leaf changes",
            "do not run the formal support gate from this workflow",
            "do not select a checkpoint from training metrics",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "pass_authorizes_only": (
                "a separately preregistered unchanged 124-cell support/context gate "
                "over both half and final checkpoints"
            ),
            "checkpoint_rule": (
                "both checkpoints must pass all formal cells; no closest failure or "
                "single-checkpoint cherry-pick"
            ),
        },
        "not_selected": [
            "flat-transport kernel",
            "another post-policy wrapper",
            "reward or learning-rate search",
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
            "pass_authorizes_only": (
                "a separate unchanged 124-cell support/context gate preregistration"
            ),
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
                "# Winner-v20 joint recurrent support training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: identical Winner-v13 Stage-1 update-100 snapshot",
                "- Updates / checkpoint updates: `100 / 50,100`",
                "- Formal support / robot now: `0 / 0`",
                "",
                "This is a one-variable causal A/B against Winner-v15. Population, seed,",
                "reward, optimizer constants, horizon, action bounds, and checkpoints are",
                "unchanged. Only the existing recurrent core joins the PPO gradient through",
                "full 250-tick BPTT. The auxiliary predictor and ONNX ABI remain frozen.",
                "",
                "Training metrics cannot select a checkpoint. A passing artifact authorizes",
                "only a separately frozen unchanged 124-cell gate over both checkpoints.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
