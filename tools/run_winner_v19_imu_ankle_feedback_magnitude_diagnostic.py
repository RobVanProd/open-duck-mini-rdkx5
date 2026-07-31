#!/usr/bin/env python3
"""Run the preregistered Winner-v19 feedback-magnitude feasibility screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v18_imu_ankle_feedback_diagnostic as v18
import winner_v19_imu_ankle_feedback_magnitude as magnitude


PREREGISTRATION = (
    ANALYSIS / "winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.json"
)
HOLD_ATTRIBUTION = ANALYSIS / "winner_v18_imu_ankle_feedback_hold_attribution.json"
FAILURE_IDS = v18.FAILURE_IDS
INTERVENTIONS = tuple(
    {"id": mode, "mode": mode, "maximum_target_offset_rad": maximum}
    for mode, maximum in (
        ("BASELINE", 0.0),
        ("CONSTANT_003", 0.03),
        ("CONSTANT_006", 0.06),
        ("CONSTANT_009", 0.09),
        ("TILT_RATE_003", 0.03),
        ("TILT_RATE_006", 0.06),
        ("TILT_RATE_009", 0.09),
    )
)


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v19.imu_ankle_feedback_magnitude_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_FEEDBACK_MAGNITUDE_FEASIBILITY_SCREEN"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v19 preregistration changed")
    if value.get("frozen_screen") != {
        "checkpoint_labels": ["half", "final"],
        "failure_configuration_ids": list(FAILURE_IDS),
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "interventions": list(INTERVENTIONS),
        "maximum_target_offsets_rad": [0.03, 0.06, 0.09],
        "tilt_boundary_rad": 0.35,
        "rate_reference_rad_s": 1.75,
        "duration_ticks": 250,
        "cells_per_checkpoint_intervention": 12,
        "total_cells": 168,
        "optimizer_updates": 0,
    }:
        raise ValueError("Winner-v19 frozen screen changed")
    if value.get("baseline_reproduction") != {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": v18.v2.DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }:
        raise ValueError("Winner-v19 baseline contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v19 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v19 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v19 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", type=Path, required=True)
    known, _ = parser.parse_known_args()

    v18.PREREGISTRATION = PREREGISTRATION
    v18.HOLD_ATTRIBUTION = HOLD_ATTRIBUTION
    v18.INTERVENTIONS = INTERVENTIONS
    v18.validate_preregistration = validate_preregistration
    v18.feedback = magnitude
    return_code = v18.main()

    result = json.loads(known.output.read_text(encoding="utf-8"))
    if result["status"] == "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC":
        result["status"] = "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
    elif result["status"] == "INVALID_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC":
        result["status"] = "INVALID_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
    else:
        raise ValueError("Winner-v19 base result status changed")
    result["schema_version"] = (
        "winner_v19.imu_ankle_feedback_magnitude_diagnostic_result.v1"
    )
    summaries = result["intervention_summary"]
    for name, summary in summaries.items():
        summary["maximum_target_offset_rad"] = next(
            row["maximum_target_offset_rad"]
            for row in INTERVENTIONS
            if row["id"] == name
        )
    candidates = [
        name
        for name, summary in summaries.items()
        if name != "BASELINE" and summary["passes_both_checkpoints"]
    ]
    order = {row["id"]: index for index, row in enumerate(INTERVENTIONS)}
    selected = None
    if candidates:
        selected = min(
            candidates,
            key=lambda name: (
                summaries[name]["maximum_target_offset_rad"],
                summaries[name]["mean_squared_action_delta_from_source"],
                order[name],
            ),
        )
    result["full_pass_candidates"] = candidates
    result["selected_direction"] = selected
    result["decision"] = (
        "AUTHORIZE_SELECTED_FEEDBACK_MAGNITUDE_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if not result["failed_validity_checks"] and selected is not None
        else (
            "INSUFFICIENT_FEEDBACK_AUTHORITY_FALSIFIED_STOP_WITH_ATTRIBUTION"
            if not result["failed_validity_checks"]
            else "DO_NOT_INTERPRET_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
        )
    )
    result["authority"] = {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate CPU-only selected-magnitude contract preregistration"
        ),
    }
    result["sources"]["feedback_base_runner_lf_sha256"] = result["sources"].pop(
        "runner_lf_sha256"
    )
    result["sources"]["runner_lf_sha256"] = lf_sha256(Path(__file__))
    result["sources"]["hold_attribution_lf_sha256"] = lf_sha256(
        HOLD_ATTRIBUTION
    )
    known.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"DECISION={result['decision']}")
    print(f"SELECTED={selected}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
