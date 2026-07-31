#!/usr/bin/env python3
"""Select one training-side repair after the Winner-v19 wrapper hold."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V15_TRAINING = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
V15_HOLD = ANALYSIS / "winner_v15_pitch_margin_support_hold_attribution.json"
V19_HOLD = ANALYSIS / "winner_v19_imu_ankle_feedback_magnitude_hold_attribution.json"
OUTPUT = ANALYSIS / "winner_v20_joint_recurrent_support_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION_20260721.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")

    training = json.loads(V15_TRAINING.read_text(encoding="utf-8"))
    v15_hold = json.loads(V15_HOLD.read_text(encoding="utf-8"))
    v19_hold = json.loads(V19_HOLD.read_text(encoding="utf-8"))
    expected_stage2 = {
        "action_bias",
        "action_weight",
        "training_only_log_std",
        "training_only_value_bias",
        "training_only_value_weight",
    }
    if (
        training.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("checks", {}).get("pitch_margin_signal_nonzero_every_update")
        is not True
        or training.get("checks", {}).get("all_stage2_leaves_changed") is not True
        or training.get("checks", {}).get("stage1_tree_bit_exact_frozen") is not True
        or set(training.get("stage2_leaf_max_abs_delta", {})) != expected_stage2
        or training.get("execution", {}).get("stage2_optimizer_updates") != 100
        or v15_hold.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION"
        or v15_hold.get("physical_failure", {}).get("classification")
        != "PERSISTENT_NEGATIVE_X_EARLY_BACKWARD_PITCH_INSTABILITY"
        or v15_hold.get("comparison_to_v13", {}).get("v15_failure_counts")
        != {"half": 12, "final": 12}
        or v15_hold.get("physical_failure", {}).get("all_failures_have_negative_torso_com_x")
        is not True
        or v15_hold.get("physical_failure", {}).get("all_failures_are_roll_pitch_only")
        is not True
        or v19_hold.get("status")
        != "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_HOLD_ATTRIBUTION"
        or v19_hold.get("decision")
        != "CLOSE_POST_POLICY_ACTION_WRAPPERS_PREREGISTER_TRAINING_SIDE_CAUSAL_REPAIR"
    ):
        raise ValueError("Winner-v20 attribution source evidence changed")

    half = v15_hold["physical_failure"]["checkpoint_results"]["half"]
    final = v15_hold["physical_failure"]["checkpoint_results"]["final"]
    payload: dict[str, Any] = {
        "schema_version": "winner_v20.joint_recurrent_support_attribution.v1",
        "status": "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION",
        "decision": "PREREGISTER_ONE_JOINT_RECURRENT_PPO_CPU_CONTRACT",
        "causal_chain": {
            "reward_signal_present_every_v15_update": True,
            "v15_action_head_and_training_only_leaves_changed": sorted(expected_stage2),
            "v15_recurrent_encoder_bit_exact_frozen": True,
            "v15_persistent_failures_half_final": [12, 12],
            "persistent_failure_tick_ranges": {
                "half": half["terminal_tick_range"],
                "final": final["terminal_tick_range"],
            },
            "contexts_remained_separate": bool(
                half["all_16_contexts_separate"] and final["all_16_contexts_separate"]
            ),
            "post_policy_wrapper_class_closed": True,
        },
        "selected_mechanism": {
            "id": "JOINT_RECURRENT_PPO",
            "hypothesis": (
                "The frozen response encoder exposes distinct contexts but cannot rotate "
                "its recurrent state toward the negative-X recovery decision. Joint PPO "
                "through the existing recurrent core can learn a temporally integrated, "
                "multi-joint recovery without a post-policy correction wrapper."
            ),
            "source_snapshot": (
                "the identical Winner-v13 Stage-1 update-100 snapshot used to start Winner-v15"
            ),
            "trainable_existing_leaves": [
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
            "new_parameters": 0,
            "onnx_abi_change": False,
            "post_policy_wrapper": False,
            "reward_change_from_v15": False,
            "population_seed_budget_change_from_v15": False,
            "required_loss_change": (
                "recompute the 64-state hidden trajectory from the frozen 115-D observation "
                "and 14-D previous-action sequences inside the PPO gradient using full BPTT"
            ),
        },
        "causal_ab": {
            "reference": "Winner-v15 action-head-only PPO",
            "same": [
                "Winner-v13 Stage-1 source snapshot",
                "80-environment population per update",
                "250-tick horizon",
                "training root seed 120120",
                "one-sided negative-pitch reward with no scale",
                "learning rate 0.0001",
                "100 updates and half/final checkpoints",
                "graph-authoritative bounds and unchanged 124-cell gate",
            ],
            "only_variable": (
                "train and differentiate through the existing recurrent core instead of "
                "feeding a cached hidden tensor to an action-head-only PPO loss"
            ),
        },
        "flat_transport_kernel": {
            "selected": False,
            "reason": (
                "Failures occur by ticks 28-62 while all contexts remain separated; the "
                "evidence does not identify long-range information transport as causal."
            ),
        },
        "required_cpu_contract": {
            "optimizer_updates": 1,
            "requirements": [
                "source recurrent replay matches the cached rollout hidden trajectory",
                "all selected recurrent/action/value/log-std gradients are finite and nonzero",
                "all selected leaves change after one Adam update",
                "auxiliary predictor leaves remain bit-exact",
                "reward, rollout population, action bounds, and previous-action chain remain exact",
                "updated ONNX retains the frozen 115/14/64 stateful ABI and JAX agreement",
            ],
            "pass_authorizes_only": (
                "a separate preregistration for one 100-update joint-recurrent A/B arm"
            ),
        },
        "execution": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "joint_recurrent_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one separately frozen CPU mechanics contract",
        },
        "sources": {
            "winner_v15_training": {
                "path": str(V15_TRAINING.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(V15_TRAINING),
            },
            "winner_v15_hold": {
                "path": str(V15_HOLD.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(V15_HOLD),
            },
            "winner_v19_hold": {
                "path": str(V19_HOLD.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(V19_HOLD),
            },
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v20 joint-recurrent support attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- New parameters / ABI change: `0 / false`",
                "- Optimizer / robot access now: `0 / 0`",
                "",
                "Winner-v15 delivered a dense exact reward and changed every action-head",
                "leaf, yet held the deployable recurrent encoder bit-exact and retained",
                "the same twelve early negative-X failures at both checkpoints. Winner-v16",
                "through Winner-v19 then closed post-policy correction wrappers.",
                "",
                "The next causal A/B uses the identical source, population, seed, reward,",
                "and budget as Winner-v15. Its only variable is full-BPTT training of the",
                "existing recurrent core together with the action head. The auxiliary",
                "predictor stays bit-exact and the ONNX ABI does not change.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
