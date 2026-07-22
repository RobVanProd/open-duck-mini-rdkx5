#!/usr/bin/env python3
"""Freeze the Winner-v50c scale-aware gradient attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v50c_gradient_backward_error_attribution_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION_CONTRACT_20260722.md"
V50_RESULT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_result.json"
V50B_CONTRACT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_contract.json"
V50B_RESULT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_result.json"
FLOAT32_EPSILON = float(np.finfo(np.float32).eps)
RELATIVE_ERROR_BOUND = math.sqrt(FLOAT32_EPSILON)
EXPECTED_V50B_RESULT_SHA256 = "55b3b8ce8f16bf10f9870732c951e5719cc115123ae16cb1b2b838f53db4469a"
SOURCES = {
    "builder": Path("tools/build_winner_v50c_gradient_backward_error_attribution.py"),
    "runner": Path("tools/run_winner_v50c_gradient_backward_error_attribution.py"),
    "tests": Path("tests/test_winner_v50c_gradient_backward_error_attribution.py"),
    "winner_v50_result": Path("outputs/analysis/winner_v50_full_action_teacher_source_gradient_result.json"),
    "winner_v50b_contract": Path("outputs/analysis/winner_v50b_gradient_composition_ulp_attribution_contract.json"),
    "winner_v50b_result": Path("outputs/analysis/winner_v50b_gradient_composition_ulp_attribution_result.json"),
    "winner_v50b_runner": Path("tools/run_winner_v50b_gradient_composition_ulp_attribution.py"),
    "winner_v50_runner": Path("tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"),
}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v50c contract: {path}")

    v50 = json.loads(V50_RESULT.read_text(encoding="utf-8"))
    v50b_contract = json.loads(V50B_CONTRACT.read_text(encoding="utf-8"))
    v50b = json.loads(V50B_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V50B_RESULT) != EXPECTED_V50B_RESULT_SHA256
        or v50.get("status")
        != "HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF"
        or v50b_contract.get("status")
        != "PREREGISTERED_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
        or v50b.get("status")
        != "HOLD_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION"
        or v50b.get("numeric_attribution", {}).get("old_maximum_ulp_distance")
        != 36_608
        or v50b.get("numeric_attribution", {}).get("new_maximum_ulp_distance")
        != 16_440
    ):
        raise ValueError("Winner-v50c upstream attribution evidence changed")

    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v50c.gradient_backward_error_attribution_contract.v1",
        "status": "PREREGISTERED_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_SCALE_AWARE_GRADIENT_RECOMPUTATION_ONLY",
        "frozen_holds": {
            "winner_v50_status": v50["status"],
            "winner_v50b_result": {
                "path": V50B_RESULT.relative_to(ROOT).as_posix(),
                "bytes": V50B_RESULT.stat().st_size,
                "sha256": sha256(V50B_RESULT),
            },
            "results_rewritten": False,
            "absolute_or_ulp_limits_changed": False,
        },
        "attribution_rule": {
            "rerun_exact_v50_rollout": True,
            "rollout_episode_slots": 80,
            "ticks_per_slot": 250,
            "source_update": 352,
            "float32_epsilon": FLOAT32_EPSILON,
            "relative_error_bound": RELATIVE_ERROR_BOUND,
            "bound_formula": "sqrt(float32 epsilon)",
            "per_leaf_max_absolute_error_over_leaf_max_magnitude_at_most_bound": True,
            "per_leaf_rms_error_over_leaf_rms_magnitude_at_most_bound": True,
            "sign_changes_allowed_only_inside_bound_times_leaf_max_magnitude": True,
            "zero_reference_leaves_must_be_bit_exact": True,
            "old_and_new_v50_absolute_errors_must_reproduce_bit_exact": True,
            "all_noncomposition_v50_checks_must_reproduce": True,
            "no_threshold_selected_from_unrecorded_leaf_scales": True,
        },
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_update_authorized": False,
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered CPU-only one-update proof",
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
                "# Winner-v50c gradient backward-error attribution contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Float32 epsilon: `{FLOAT32_EPSILON}`",
                f"- Relative bound, sqrt(epsilon): `{RELATIVE_ERROR_BOUND}`",
                "- Rerun: `80 x 250 ticks`, CPU-only, zero optimizer updates",
                "- Support / export / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                "V50 and V50b remain holds. This test asks whether every gradient leaf",
                "is backward-stable relative to its own magnitude; it does not widen or",
                "rewrite either prior absolute or ULP gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
