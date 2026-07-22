#!/usr/bin/env python3
"""Freeze the Winner-v50b gradient-composition ULP attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v50b_gradient_composition_ulp_attribution_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION_CONTRACT_20260722.md"
V50_CONTRACT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_contract.json"
V50_RESULT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_result.json"
V31_PREREGISTRATION = ANALYSIS / "winner_v31_cross_worker_replay_attribution_preregistration.json"
V31_RESULT = ANALYSIS / "winner_v31_cross_worker_replay_attribution_result.json"
MAX_ULP_DISTANCE = 8
EXPECTED_ABSOLUTE_ERROR = 4.76837158203125e-6
EXPECTED_V50_RESULT_SHA256 = "7f1a6ae01ba9aaf01766ccbdaa6246c0aa2629e04a2e695e1425a45e858b79b1"
FAILED_V50_CHECKS = [
    "new_direct_composition_at_most_4e_6",
    "old_direct_composition_at_most_4e_6",
]
SOURCES = {
    "builder": Path("tools/build_winner_v50b_gradient_composition_ulp_attribution.py"),
    "runner": Path("tools/run_winner_v50b_gradient_composition_ulp_attribution.py"),
    "tests": Path("tests/test_winner_v50b_gradient_composition_ulp_attribution.py"),
    "winner_v50_contract": Path("outputs/analysis/winner_v50_full_action_teacher_source_gradient_contract.json"),
    "winner_v50_result": Path("outputs/analysis/winner_v50_full_action_teacher_source_gradient_result.json"),
    "winner_v50_runner": Path("tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"),
    "winner_v31_preregistration": Path("outputs/analysis/winner_v31_cross_worker_replay_attribution_preregistration.json"),
    "winner_v31_result": Path("outputs/analysis/winner_v31_cross_worker_replay_attribution_result.json"),
    "winner_v31_runner": Path("tools/run_winner_v31_cross_worker_replay_attribution.py"),
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
            raise FileExistsError(f"refusing to overwrite Winner-v50b contract: {path}")

    v50_contract = json.loads(V50_CONTRACT.read_text(encoding="utf-8"))
    v50_result = json.loads(V50_RESULT.read_text(encoding="utf-8"))
    v31_prereg = json.loads(V31_PREREGISTRATION.read_text(encoding="utf-8"))
    v31_result = json.loads(V31_RESULT.read_text(encoding="utf-8"))
    evidence = v50_result.get("objective_evidence", {})
    if (
        sha256(V50_RESULT) != EXPECTED_V50_RESULT_SHA256
        or v50_contract.get("status")
        != "PREREGISTERED_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CONTRACT"
        or v50_result.get("status")
        != "HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF"
        or v50_result.get("decision") != "DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY"
        or v50_result.get("failed_checks") != FAILED_V50_CHECKS
        or evidence.get("old_direct_composition_max_abs_error")
        != EXPECTED_ABSOLUTE_ERROR
        or evidence.get("new_direct_composition_max_abs_error")
        != EXPECTED_ABSOLUTE_ERROR
        or v31_prereg.get("attribution_rule", {}).get("maximum_ulp_distance_each")
        != MAX_ULP_DISTANCE
        or v31_result.get("status")
        != "PASS_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
    ):
        raise ValueError("Winner-v50b upstream attribution authority changed")

    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v50b.gradient_composition_ulp_attribution_contract.v1",
        "status": "PREREGISTERED_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_GRADIENT_ULP_RECOMPUTATION_ONLY",
        "frozen_hold": {
            "result": {
                "path": V50_RESULT.relative_to(ROOT).as_posix(),
                "bytes": V50_RESULT.stat().st_size,
                "sha256": sha256(V50_RESULT),
            },
            "failed_checks": FAILED_V50_CHECKS,
            "old_absolute_error": EXPECTED_ABSOLUTE_ERROR,
            "new_absolute_error": EXPECTED_ABSOLUTE_ERROR,
            "old_threshold_unchanged": 4.0e-6,
            "result_rewritten": False,
        },
        "attribution_rule": {
            "rerun_exact_v50_rollout": True,
            "rollout_episode_slots": 80,
            "ticks_per_slot": 250,
            "source_update": 352,
            "compare_every_signed_float32_gradient_element": True,
            "maximum_ulp_distance_each": MAX_ULP_DISTANCE,
            "ulp_bound_origin": (
                "the existing preregistered Winner-v31 CPU replay bound; not selected "
                "from the unrecorded V50 elementwise ULP distances"
            ),
            "all_noncomposition_v50_checks_must_pass": True,
            "old_and_new_absolute_errors_must_reproduce_bit_exact": True,
            "v50_scalar_and_rollout_evidence_must_reproduce_bit_exact": True,
            "optimizer_parameters_and_transitions_must_remain_unchanged": True,
            "v50_absolute_threshold_changed": False,
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
                "# Winner-v50b gradient-composition ULP attribution contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Frozen V50 error / threshold: `4.76837158203125e-6 / 4e-6`",
                "- Existing campaign bound: `8 signed-float32 ULP per element`",
                "- Rerun: `80 x 250 ticks`, CPU-only, zero optimizer updates",
                "- Support / export / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                "V50 remains a hold. This separately tests whether its two equal absolute",
                "misses are bounded float32 evaluation-order variation under the already",
                "established Winner-v31 ULP rule. It does not change V50's threshold.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
