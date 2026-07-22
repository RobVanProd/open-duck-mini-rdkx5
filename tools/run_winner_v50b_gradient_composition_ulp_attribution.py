#!/usr/bin/env python3
"""Run the zero-update Winner-v50b gradient ULP attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import run_winner_v50_full_action_teacher_source_gradient_contract as v50  # noqa: E402


CONTRACT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_contract.json"
V50_CONTRACT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_contract.json"
V50_RESULT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_result.json"
MAX_ULP_DISTANCE = 8
EXPECTED_ABSOLUTE_ERROR = 4.76837158203125e-6
FAILED_V50_CHECKS = [
    "new_direct_composition_at_most_4e_6",
    "old_direct_composition_at_most_4e_6",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def ordered_float32_bits(values: Any) -> np.ndarray:
    array = np.ascontiguousarray(np.asarray(values, dtype=np.float32))
    bits = array.view(np.uint32)
    sign = np.uint32(0x80000000)
    return np.where((bits & sign) != 0, ~bits, bits | sign).astype(np.uint64)


def signed_float32_ulp_distance(left: Any, right: Any) -> np.ndarray:
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    if (
        left_array.dtype != np.float32
        or right_array.dtype != np.float32
        or left_array.shape != right_array.shape
        or not np.all(np.isfinite(left_array))
        or not np.all(np.isfinite(right_array))
    ):
        raise ValueError("Winner-v50b requires equal finite float32 arrays")
    left_ordered = ordered_float32_bits(left_array)
    right_ordered = ordered_float32_bits(right_array)
    return np.maximum(left_ordered, right_ordered) - np.minimum(
        left_ordered, right_ordered
    )


def tree_ulp_evidence(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, dict[str, int | float]]:
    if set(left) != set(right):
        raise ValueError("Winner-v50b gradient tree keys changed")
    evidence: dict[str, dict[str, int | float]] = {}
    for key in sorted(left):
        left_array = np.asarray(left[key])
        right_array = np.asarray(right[key])
        distances = signed_float32_ulp_distance(left_array, right_array)
        evidence[key] = {
            "elements": int(distances.size),
            "differing_elements": int(np.count_nonzero(distances)),
            "maximum_ulp_distance": int(np.max(distances)) if distances.size else 0,
            "maximum_absolute_error": float(
                np.max(np.abs(left_array.astype(np.float64) - right_array.astype(np.float64)))
            )
            if distances.size
            else 0.0,
        }
    return evidence


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v50b.gradient_composition_ulp_attribution_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_GRADIENT_ULP_RECOMPUTATION_ONLY"
        or value.get("attribution_rule", {}).get("maximum_ulp_distance_each")
        != MAX_ULP_DISTANCE
        or value.get("attribution_rule", {}).get("v50_absolute_threshold_changed")
        is not False
        or value.get("execution_now", {}).get("optimizer_updates") != 0
        or value.get("authority", {}).get("one_update_authorized") is not False
    ):
        raise ValueError("Winner-v50b contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v50b source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v50b source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v50b source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v46-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--ulp-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.ulp_attribution_authorized:
        raise PermissionError(
            "Winner-v50b requires --offline-cpu-only --ulp-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v50b result: {args.output}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v50_contract = json.loads(V50_CONTRACT.read_text(encoding="utf-8"))
    v50.validate_contract(v50_contract)
    frozen = json.loads(V50_RESULT.read_text(encoding="utf-8"))
    frozen_evidence = frozen.get("objective_evidence", {})
    if (
        sha256(V50_RESULT) != contract["frozen_hold"]["result"]["sha256"]
        or frozen.get("status")
        != "HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF"
        or frozen.get("failed_checks") != FAILED_V50_CHECKS
        or frozen_evidence.get("old_direct_composition_max_abs_error")
        != EXPECTED_ABSOLUTE_ERROR
        or frozen_evidence.get("new_direct_composition_max_abs_error")
        != EXPECTED_ABSOLUTE_ERROR
    ):
        raise ValueError("Winner-v50b frozen V50 hold changed")

    captured: list[tuple[dict[str, np.ndarray], dict[str, np.ndarray]]] = []
    original_delta = v50.tree_delta_max_abs
    original_tolerance = v50.COMPOSITION_TOLERANCE
    original_argv = sys.argv[:]

    def capture_delta(
        left: Mapping[str, Any], right: Mapping[str, Any]
    ) -> dict[str, float]:
        captured.append(
            (
                {key: np.asarray(value).copy() for key, value in left.items()},
                {key: np.asarray(value).copy() for key, value in right.items()},
            )
        )
        return original_delta(left, right)

    try:
        with tempfile.TemporaryDirectory(prefix="winner-v50b-") as temporary:
            recomputed_path = Path(temporary) / "v50_recomputed.json"
            v50.tree_delta_max_abs = capture_delta
            v50.COMPOSITION_TOLERANCE = math.inf
            sys.argv = [
                str(v50.__file__),
                "--playground-root", str(args.playground_root),
                "--canonical-fit", str(args.canonical_fit),
                "--v46-training-work-root", str(args.v46_training_work_root),
                "--v22-training-work-root", str(args.v22_training_work_root),
                "--output", str(recomputed_path),
                "--offline-cpu-only",
                "--source-gradient-proof-authorized",
            ]
            return_code = v50.main()
            recomputed = json.loads(recomputed_path.read_text(encoding="utf-8"))
    finally:
        v50.tree_delta_max_abs = original_delta
        v50.COMPOSITION_TOLERANCE = original_tolerance
        sys.argv = original_argv

    if return_code != 0 or len(captured) != 3:
        raise ValueError("Winner-v50b did not capture the exact three V50 tree comparisons")
    old_ulp = tree_ulp_evidence(*captured[0])
    new_ulp = tree_ulp_evidence(*captured[1])
    old_max = max(row["maximum_ulp_distance"] for row in old_ulp.values())
    new_max = max(row["maximum_ulp_distance"] for row in new_ulp.values())
    tolerance_checks = set(FAILED_V50_CHECKS)
    frozen_other_checks = {
        key: value for key, value in frozen["checks"].items() if key not in tolerance_checks
    }
    recomputed_other_checks = {
        key: value
        for key, value in recomputed["checks"].items()
        if key not in tolerance_checks
    }
    scalar_keys = (
        "ppo_loss",
        "normalized_predictor_loss",
        "prefix_anchor_loss",
        "old_pitch_teacher_loss",
        "full_action_teacher_loss",
        "old_pitch_teacher_scale",
        "full_action_teacher_scale",
        "old_selected_elements",
        "full_selected_elements",
        "old_direct_composition_max_abs_error",
        "new_direct_composition_max_abs_error",
    )
    checks = {
        "frozen_v50_hold_exact": True,
        "v50_absolute_threshold_unchanged": v50.COMPOSITION_TOLERANCE == 4.0e-6,
        "exact_three_tree_comparisons_captured": len(captured) == 3,
        "all_captured_values_finite_float32": all(
            value.dtype == np.float32 and np.all(np.isfinite(value))
            for pair in captured
            for tree in pair
            for value in tree.values()
        ),
        "old_composition_maximum_at_most_8_ulp": old_max <= MAX_ULP_DISTANCE,
        "new_composition_maximum_at_most_8_ulp": new_max <= MAX_ULP_DISTANCE,
        "old_absolute_error_reproduced_bit_exact": recomputed["objective_evidence"]
        ["old_direct_composition_max_abs_error"]
        == EXPECTED_ABSOLUTE_ERROR,
        "new_absolute_error_reproduced_bit_exact": recomputed["objective_evidence"]
        ["new_direct_composition_max_abs_error"]
        == EXPECTED_ABSOLUTE_ERROR,
        "all_noncomposition_v50_checks_pass_and_reproduce": frozen_other_checks
        == recomputed_other_checks
        and all(frozen_other_checks.values()),
        "scalar_objective_evidence_reproduced_bit_exact": all(
            recomputed["objective_evidence"][key] == frozen_evidence[key]
            for key in scalar_keys
        ),
        "source_and_rollout_evidence_reproduced_bit_exact": recomputed["source_identity"]
        == frozen["source_identity"]
        and recomputed["rollout_evidence"] == frozen["rollout_evidence"],
        "parameters_optimizer_transitions_unchanged": recomputed["checks"]
        ["parameters_and_optimizer_unchanged"]
        and recomputed["checks"]["transition_arrays_unchanged"],
        "optimizer_updates_zero": recomputed["execution"]["optimizer_updates"] == 0,
        "formal_support_cells_zero": recomputed["execution"]["formal_support_cells"] == 0,
        "locomotion_training_steps_zero": recomputed["execution"]
        ["locomotion_training_steps"]
        == 0,
        "deployable_graph_exports_zero": recomputed["execution"]
        ["deployable_graph_exports"]
        == 0,
        "robot_or_rdk_access_zero": recomputed["execution"]["robot_or_rdk_access"] == 0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result = {
        "schema_version": "winner_v50b.gradient_composition_ulp_attribution_result.v1",
        "status": (
            "PASS_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
            if passed
            else "HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "frozen_v50_result": contract["frozen_hold"]["result"],
        "numeric_attribution": {
            "maximum_allowed_ulp_distance": MAX_ULP_DISTANCE,
            "old_maximum_ulp_distance": old_max,
            "new_maximum_ulp_distance": new_max,
            "old_per_leaf": old_ulp,
            "new_per_leaf": new_ulp,
            "old_absolute_error": recomputed["objective_evidence"]
            ["old_direct_composition_max_abs_error"],
            "new_absolute_error": recomputed["objective_evidence"]
            ["new_direct_composition_max_abs_error"],
            "frozen_absolute_threshold": 4.0e-6,
        },
        "execution": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20_000,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "one_update_authorized": False,
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered CPU-only one-update proof",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    if failed:
        print(json.dumps(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
