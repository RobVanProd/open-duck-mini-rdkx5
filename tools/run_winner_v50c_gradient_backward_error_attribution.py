#!/usr/bin/env python3
"""Run the zero-update Winner-v50c scale-aware gradient attribution."""

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

import run_winner_v50b_gradient_composition_ulp_attribution as v50b  # noqa: E402


CONTRACT = ANALYSIS / "winner_v50c_gradient_backward_error_attribution_contract.json"
V50_RESULT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_result.json"
V50B_CONTRACT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_contract.json"
V50B_RESULT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_result.json"
FLOAT32_EPSILON = float(np.finfo(np.float32).eps)
RELATIVE_ERROR_BOUND = math.sqrt(FLOAT32_EPSILON)
EXPECTED_ABSOLUTE_ERROR = 4.76837158203125e-6


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


def tree_backward_error_evidence(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, dict[str, int | float | bool]]:
    if set(left) != set(right):
        raise ValueError("Winner-v50c gradient tree keys changed")
    evidence: dict[str, dict[str, int | float | bool]] = {}
    for key in sorted(left):
        left_array = np.asarray(left[key])
        right_array = np.asarray(right[key])
        if (
            left_array.dtype != np.float32
            or right_array.dtype != np.float32
            or left_array.shape != right_array.shape
            or not np.all(np.isfinite(left_array))
            or not np.all(np.isfinite(right_array))
        ):
            raise ValueError("Winner-v50c requires equal finite float32 arrays")
        left64 = left_array.astype(np.float64)
        right64 = right_array.astype(np.float64)
        difference = left64 - right64
        maximum_reference = max(
            float(np.max(np.abs(left64))) if left64.size else 0.0,
            float(np.max(np.abs(right64))) if right64.size else 0.0,
        )
        rms_reference = max(
            float(np.sqrt(np.mean(np.square(left64)))) if left64.size else 0.0,
            float(np.sqrt(np.mean(np.square(right64)))) if right64.size else 0.0,
        )
        maximum_error = (
            float(np.max(np.abs(difference))) if difference.size else 0.0
        )
        rms_error = (
            float(np.sqrt(np.mean(np.square(difference)))) if difference.size else 0.0
        )
        if maximum_reference == 0.0:
            maximum_relative = 0.0 if maximum_error == 0.0 else math.inf
            sign_envelope = 0.0
        else:
            maximum_relative = maximum_error / maximum_reference
            sign_envelope = RELATIVE_ERROR_BOUND * maximum_reference
        if rms_reference == 0.0:
            rms_relative = 0.0 if rms_error == 0.0 else math.inf
        else:
            rms_relative = rms_error / rms_reference
        sign_difference = np.signbit(left_array) != np.signbit(right_array)
        material = sign_difference & (
            np.maximum(np.abs(left64), np.abs(right64)) > sign_envelope
        )
        evidence[key] = {
            "elements": int(left_array.size),
            "maximum_reference_magnitude": maximum_reference,
            "rms_reference_magnitude": rms_reference,
            "maximum_absolute_error": maximum_error,
            "rms_error": rms_error,
            "maximum_relative_error": maximum_relative,
            "rms_relative_error": rms_relative,
            "sign_change_count": int(np.count_nonzero(sign_difference)),
            "material_sign_change_count": int(np.count_nonzero(material)),
            "zero_reference_bit_exact": maximum_reference != 0.0 or maximum_error == 0.0,
        }
    return evidence


def validate_contract(value: Mapping[str, Any]) -> None:
    rule = value.get("attribution_rule", {})
    if (
        value.get("schema_version")
        != "winner_v50c.gradient_backward_error_attribution_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_SCALE_AWARE_GRADIENT_RECOMPUTATION_ONLY"
        or rule.get("float32_epsilon") != FLOAT32_EPSILON
        or rule.get("relative_error_bound") != RELATIVE_ERROR_BOUND
        or rule.get("bound_formula") != "sqrt(float32 epsilon)"
        or value.get("execution_now", {}).get("optimizer_updates") != 0
        or value.get("authority", {}).get("one_update_authorized") is not False
    ):
        raise ValueError("Winner-v50c contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v50c source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v50c source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v50c source-manifest digest changed")


def all_leaves_within_bound(evidence: Mapping[str, Mapping[str, Any]]) -> bool:
    return all(
        math.isfinite(float(row["maximum_relative_error"]))
        and math.isfinite(float(row["rms_relative_error"]))
        and float(row["maximum_relative_error"]) <= RELATIVE_ERROR_BOUND
        and float(row["rms_relative_error"]) <= RELATIVE_ERROR_BOUND
        and int(row["material_sign_change_count"]) == 0
        and bool(row["zero_reference_bit_exact"])
        for row in evidence.values()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v46-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--backward-error-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.backward_error_attribution_authorized:
        raise PermissionError(
            "Winner-v50c requires --offline-cpu-only "
            "--backward-error-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v50c result: {args.output}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v50b.validate_contract(json.loads(V50B_CONTRACT.read_text(encoding="utf-8")))
    frozen = json.loads(V50B_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V50B_RESULT) != contract["frozen_holds"]["winner_v50b_result"]["sha256"]
        or frozen.get("status")
        != "HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
    ):
        raise ValueError("Winner-v50c frozen V50b hold changed")

    captured: list[tuple[dict[str, np.ndarray], dict[str, np.ndarray]]] = []
    original_tree_ulp = v50b.tree_ulp_evidence
    original_argv = sys.argv[:]

    def capture_and_neutralize_ulp(
        left: Mapping[str, Any], right: Mapping[str, Any]
    ) -> dict[str, dict[str, int | float]]:
        captured.append(
            (
                {key: np.asarray(value).copy() for key, value in left.items()},
                {key: np.asarray(value).copy() for key, value in right.items()},
            )
        )
        evidence = original_tree_ulp(left, right)
        return {
            key: {**row, "maximum_ulp_distance": 0}
            for key, row in evidence.items()
        }

    try:
        with tempfile.TemporaryDirectory(prefix="winner-v50c-") as temporary:
            recomputed_path = Path(temporary) / "v50b_recomputed.json"
            v50b.tree_ulp_evidence = capture_and_neutralize_ulp
            sys.argv = [
                str(v50b.__file__),
                "--playground-root", str(args.playground_root),
                "--canonical-fit", str(args.canonical_fit),
                "--v46-training-work-root", str(args.v46_training_work_root),
                "--v22-training-work-root", str(args.v22_training_work_root),
                "--output", str(recomputed_path),
                "--offline-cpu-only",
                "--ulp-attribution-authorized",
            ]
            return_code = v50b.main()
            recomputed = json.loads(recomputed_path.read_text(encoding="utf-8"))
    finally:
        v50b.tree_ulp_evidence = original_tree_ulp
        sys.argv = original_argv

    if return_code != 0 or len(captured) != 2:
        raise ValueError("Winner-v50c did not capture the exact old/new gradient pairs")
    old_evidence = tree_backward_error_evidence(*captured[0])
    new_evidence = tree_backward_error_evidence(*captured[1])
    frozen_nonulp = {
        key: value
        for key, value in frozen["checks"].items()
        if key not in {
            "old_composition_maximum_at_most_8_ulp",
            "new_composition_maximum_at_most_8_ulp",
        }
    }
    checks = {
        "frozen_v50b_hold_exact": True,
        "exact_old_and_new_gradient_pairs_captured": len(captured) == 2,
        "old_all_leaves_within_sqrt_float32_epsilon": all_leaves_within_bound(
            old_evidence
        ),
        "new_all_leaves_within_sqrt_float32_epsilon": all_leaves_within_bound(
            new_evidence
        ),
        "all_nonulp_v50b_checks_pass": all(frozen_nonulp.values()),
        "v50_absolute_errors_reproduced_bit_exact": recomputed["numeric_attribution"]
        ["old_absolute_error"]
        == EXPECTED_ABSOLUTE_ERROR
        and recomputed["numeric_attribution"]["new_absolute_error"]
        == EXPECTED_ABSOLUTE_ERROR,
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
        "schema_version": "winner_v50c.gradient_backward_error_attribution_result.v1",
        "status": (
            "PASS_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION"
            if passed
            else "HOLD_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "numeric_attribution": {
            "float32_epsilon": FLOAT32_EPSILON,
            "relative_error_bound": RELATIVE_ERROR_BOUND,
            "old_per_leaf": old_evidence,
            "new_per_leaf": new_evidence,
            "old_maximum_relative_error": max(
                float(row["maximum_relative_error"])
                for row in old_evidence.values()
            ),
            "new_maximum_relative_error": max(
                float(row["maximum_relative_error"])
                for row in new_evidence.values()
            ),
            "old_maximum_rms_relative_error": max(
                float(row["rms_relative_error"]) for row in old_evidence.values()
            ),
            "new_maximum_rms_relative_error": max(
                float(row["rms_relative_error"]) for row in new_evidence.values()
            ),
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
