#!/usr/bin/env python3
"""Attribute the Winner-v20 one-update CPU hold."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_result.json"
INITIALIZER = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
OUTPUT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_HOLD_ATTRIBUTION_20260721.md"


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite hold attribution: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    initializer_source = INITIALIZER.read_text(encoding="utf-8")
    recurrent = {"obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias"}
    gradients = result.get("optimization", {}).get("gradient_max_abs", {})
    deltas = result.get("optimization", {}).get("leaf_max_abs_delta", {})
    if (
        result.get("status")
        != "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or result.get("decision") != "DO_NOT_TRAIN_JOINT_RECURRENT_SUPPORT_ARM"
        or result.get("failed_checks")
        != [
            "all_joint_gradients_nonzero",
            "all_joint_leaves_changed",
            "source_hidden_replay_at_most_1e_6",
        ]
        or any(gradients.get(name) != 0.0 or deltas.get(name) != 0.0 for name in recurrent)
        or any(
            gradients.get(name, 0.0) <= 0.0 or deltas.get(name, 0.0) <= 0.0
            for name in ("action_weight", "action_bias")
        )
        or result.get("repository_attribution", {}).get("github_run_id") != 29852380511
        or '"action_weight": jnp.zeros((HIDDEN_SIZE, ACTION_SIZE)' not in initializer_source
        or '"action_bias": jnp.zeros((ACTION_SIZE,)' not in initializer_source
    ):
        raise ValueError("Winner-v20 CPU hold evidence changed")
    payload = {
        "schema_version": "winner_v20.joint_recurrent_support_cpu_hold_attribution.v1",
        "status": "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_HOLD_ATTRIBUTION",
        "decision": "PREREGISTER_EXACT_TWO_UPDATE_JOINT_RECURRENT_CPU_CONTRACT",
        "causal_interpretation": {
            "source_action_head_exact_zero": True,
            "update_1_action_head_gradients_nonzero": {
                name: gradients[name] for name in ("action_weight", "action_bias")
            },
            "update_1_action_head_deltas_nonzero": {
                name: deltas[name] for name in ("action_weight", "action_bias")
            },
            "update_1_recurrent_gradients_exact_zero": {
                name: gradients[name] for name in sorted(recurrent)
            },
            "update_1_recurrent_deltas_exact_zero": {
                name: deltas[name] for name in sorted(recurrent)
            },
            "classification": "ZERO_ACTION_HEAD_CHAIN_RULE_GATE",
            "reason": (
                "At the common source, action = tanh(hidden @ zero + zero), so the "
                "action loss has no derivative path into hidden on the first update. "
                "The first update makes both action-head leaves nonzero; the second is "
                "the earliest preregisterable update that can test recurrent gradients."
            ),
        },
        "replay_metric_correction": {
            "observed_unmasked_max_abs_error": result["rollout"][
                "source_hidden_replay_max_abs_error"
            ],
            "cause": (
                "the differentiable scan continues through zero-padded post-terminal "
                "slots while the cached rollout leaves those excluded slots at zero"
            ),
            "correct_population": "valid_mask == 1 sampled ticks only",
            "threshold": 1.0e-6,
            "threshold_change": False,
            "training_loss_change": False,
        },
        "next_contract": {
            "optimizer_updates": 2,
            "update_1_required": {
                "recurrent_gradients": "all exact zero",
                "recurrent_deltas": "all exact zero",
                "action_head_gradients": "all finite and nonzero",
                "action_head_deltas": "all finite and nonzero",
            },
            "update_2_required": {
                "all_nine_gradients": "finite and nonzero",
                "all_nine_deltas_from_update_1": "finite and nonzero",
            },
            "both_updates_required": [
                "sampled-tick hidden replay max abs error <= 1e-6",
                "exact Winner-v15 rollout/reward/action/mask semantics",
                "auxiliary predictor leaves bit-exact frozen",
                "snapshot readback and 115/14/64 ONNX contract exact",
            ],
            "selection_if_update_2_recurrent_gradient_is_zero": (
                "close existing recurrent-core joint training without further warmup"
            ),
            "optimizer_updates_authorized_now": 0,
        },
        "not_selected": [
            "relaxing the nonzero-gradient requirement",
            "changing the 1e-6 sampled-tick replay threshold",
            "more than two proof updates",
            "any 100-update training arm",
            "flat-transport kernel",
            "post-policy wrapper",
        ],
        "execution": {
            "new_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "joint_recurrent_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one separately frozen two-update CPU mechanics contract",
        },
        "sources": {
            "result_lf_sha256": lf_sha256(RESULT),
            "zero_action_initializer_lf_sha256": lf_sha256(INITIALIZER),
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v20 joint recurrent CPU hold attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Classification: `ZERO_ACTION_HEAD_CHAIN_RULE_GATE`",
                "- Training arm / support cells / robot: `0 / 0 / 0`",
                "",
                "The recurrent core is not shown dead. Its gradient is necessarily zero",
                "on update 1 because the shared action weight starts exactly zero. Update 1",
                "moves both action-head leaves; update 2 is the first causal test of recurrent",
                "trainability. Replay equality remains `<=1e-6`, but is correctly measured",
                "only on sampled ticks rather than excluded post-terminal padding.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
