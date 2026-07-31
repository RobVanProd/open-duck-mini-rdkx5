#!/usr/bin/env python3
"""Attribute the held Winner-v30 replay checks from saved results only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v31_cross_worker_replay_attribution_preregistration.json"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
V30_HOLD = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"
MAX_ULP_DISTANCE = 8
MINIMUM_IMPROVEMENT_TO_REPLAY_DELTA_RATIO = 10_000.0
REPLAY_CHECKS = (
    "exact_v29_anchor_loss_gradient_and_scale_reproduced",
    "exact_v29_update_200_batch_reproduced",
)


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def float32_bits(value: float) -> int:
    return struct.unpack("!I", struct.pack("!f", float(value)))[0]


def float32_ulp_distance(left: float, right: float) -> int:
    if not math.isfinite(left) or not math.isfinite(right) or left < 0.0 or right < 0.0:
        raise ValueError("Winner-v31 ULP comparison requires finite nonnegative values")
    return abs(float32_bits(left) - float32_bits(right))


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v31.cross_worker_replay_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_SAVED_RESULT_ONLY_REPLAY_ATTRIBUTION"
        or value.get("execution_now")
        != {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("attribution_rule")
        != {
            "failed_checks_must_equal": list(REPLAY_CHECKS),
            "all_non_replay_checks_must_pass": True,
            "float32_loss_pairs": [
                "anchor_loss_before",
                "ppo_loss",
                "normalized_predictor_loss",
            ],
            "maximum_ulp_distance_each": MAX_ULP_DISTANCE,
            "minimum_anchor_improvement_to_cross_worker_delta_ratio": (
                MINIMUM_IMPROVEMENT_TO_REPLAY_DELTA_RATIO
            ),
            "same_failure_count_required": True,
            "same_selected_element_count_required": True,
            "same_maximum_selected_action_delta_required": True,
            "snapshot_graph_and_update_checks_must_pass": True,
            "old_hold_result_rewritten": False,
            "thresholds_in_old_contract_changed": False,
            "rerun_authorized": False,
        }
    ):
        raise ValueError("Winner-v31 preregistration changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v31 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            item.get("hash_mode") != "lf"
            or not path.is_file()
            or lf_sha256(path) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v31 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v31 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--saved-result-only-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.saved_result_only_attribution_authorized:
        raise PermissionError(
            "Winner-v31 requires --saved-result-only-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v31 evidence")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(prereg)
    v29 = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    v30 = json.loads(V30_HOLD.read_text(encoding="utf-8"))
    if (
        v29.get("status")
        != "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or v29.get("failed_checks") != []
        or v30.get("status")
        != "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or tuple(v30.get("failed_checks", ())) != REPLAY_CHECKS
        or v30.get("repository_attribution", {}).get("github_run_id") != 29889578085
        or v30.get("repository_attribution", {}).get("github_artifact_id") != 8517769530
    ):
        raise ValueError("Winner-v31 source evidence changed")
    non_replay_checks_pass = all(
        passed is True
        for name, passed in v30["checks"].items()
        if name not in REPLAY_CHECKS
    ) and sorted(name for name, passed in v30["checks"].items() if not passed) == list(
        REPLAY_CHECKS
    )
    pairs = {
        "anchor_loss_before": (
            float(v29["objective_evidence"]["raw_anchor_loss"]),
            float(v30["optimization"]["anchor_loss_before"]),
        ),
        "ppo_loss": (
            float(v29["objective_evidence"]["baseline_ppo_loss"]),
            float(v30["optimization"]["ppo_loss"]),
        ),
        "normalized_predictor_loss": (
            float(v29["objective_evidence"]["baseline_normalized_predictor_loss"]),
            float(v30["optimization"]["normalized_predictor_loss"]),
        ),
    }
    numeric = {
        name: {
            "winner_v29": left,
            "winner_v30": right,
            "absolute_delta": abs(right - left),
            "float32_ulp_distance": float32_ulp_distance(left, right),
        }
        for name, (left, right) in pairs.items()
    }
    anchor_cross_worker_delta = numeric["anchor_loss_before"]["absolute_delta"]
    anchor_improvement = float(v30["optimization"]["anchor_loss_before"]) - float(
        v30["optimization"]["anchor_loss_after"]
    )
    improvement_ratio = anchor_improvement / max(anchor_cross_worker_delta, 1.0e-30)
    same_failure_count = (
        v29["rollout_evidence"]["roll_pitch_failure_count"]
        == v30["rollout"]["roll_pitch_failure_count"]
    )
    same_selected_elements = (
        v29["rollout_evidence"]["selected_elements"]
        == v30["rollout"]["selected_anchor_elements"]
        == 384
    )
    same_maximum_delta = (
        v29["objective_evidence"]["maximum_selected_action_delta"]
        == v30["optimization"]["maximum_selected_action_delta_before"]
    )
    snapshot_graph_update_pass = all(
        v30["checks"].get(name) is True
        for name in (
            "all_12_combined_gradients_nonzero",
            "all_12_trainable_leaves_changed",
            "exactly_one_optimizer_update_200_to_201",
            "same_batch_anchor_loss_strictly_decreases",
            "snapshot_readback_exact",
            "onnx_abi_exact",
            "onnx_training_only_tensors_absent",
            "onnx_jax_chain_at_most_1e_7",
            "onnx_previous_action_chain_exact",
            "formal_support_locomotion_robot_zero",
        )
    )
    checks = {
        "exact_two_replay_checks_failed": tuple(v30["failed_checks"]) == REPLAY_CHECKS,
        "all_non_replay_checks_pass": non_replay_checks_pass,
        "all_three_loss_pairs_at_most_8_float32_ulps": all(
            row["float32_ulp_distance"] <= MAX_ULP_DISTANCE
            for row in numeric.values()
        ),
        "anchor_improvement_exceeds_cross_worker_delta_by_10000x": improvement_ratio
        >= MINIMUM_IMPROVEMENT_TO_REPLAY_DELTA_RATIO,
        "same_roll_pitch_failure_count": same_failure_count,
        "same_384_selected_elements": same_selected_elements,
        "same_maximum_selected_action_delta": same_maximum_delta,
        "snapshot_graph_and_update_checks_all_pass": snapshot_graph_update_pass,
        "old_hold_result_and_thresholds_unchanged": True,
        "new_simulation_optimizer_support_locomotion_robot_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    classification = (
        "CROSS_WORKER_FLOAT_REPLAY_ONLY"
        if not failed
        else "UNRESOLVED_WINNER_V30_REPLAY_MISMATCH"
    )
    decision = (
        "AUTHORIZE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_USING_PRESERVED_COUNT_201_ARTIFACT_ONLY"
        if not failed
        else "DO_NOT_USE_WINNER_V30_ARTIFACT_FOR_TRAINING"
    )
    result = {
        "schema_version": "winner_v31.cross_worker_replay_attribution_result.v1",
        "status": (
            "PASS_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
        ),
        "classification": classification,
        "decision": decision,
        "failed_checks": failed,
        "checks": checks,
        "numeric_attribution": numeric,
        "anchor_improvement": anchor_improvement,
        "anchor_improvement_to_cross_worker_delta_ratio": improvement_ratio,
        "source_artifacts": {
            "winner_v29_result_lf_sha256": lf_sha256(V29_RESULT),
            "winner_v30_hold_result_lf_sha256": lf_sha256(V30_HOLD),
            "winner_v30_snapshot_sha256": v30["snapshot"]["sha256"],
            "winner_v30_graph_sha256": v30["graph"]["sha256"],
        },
        "execution": {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": prereg["sources"],
        "source_manifest_sha256": prereg["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen prefix right-pitch anchor training preregistration "
                "using the preserved count-201 artifact"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(result["classification"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
