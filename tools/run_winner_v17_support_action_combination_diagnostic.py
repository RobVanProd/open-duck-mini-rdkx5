#!/usr/bin/env python3
"""Run the preregistered Winner-v17 sign-consistent combination diagnostic."""

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

import run_winner_v14_support_action_diagnostic as v14
import run_winner_v16_support_action_direction_diagnostic as base
import run_winner_v16_support_action_direction_diagnostic_v2 as v2
import winner_v16_support_action_direction as direction_module
import winner_v17_support_action_combination as combination


PREREGISTRATION = (
    ANALYSIS / "winner_v17_support_action_combination_diagnostic_preregistration.json"
)
HOLD_ATTRIBUTION = (
    ANALYSIS / "winner_v16_support_action_direction_hold_attribution.json"
)
DERIVED_FLOAT_ABS_TOLERANCE = v2.DERIVED_FLOAT_ABS_TOLERANCE
FAILURE_IDS = base.FAILURE_IDS
INTERVENTIONS = (
    {"id": "BASELINE", "axis": None, "direction": 0},
    {"id": "HIP_MAG_NEG", "axis": ["HIP_MAG_NEG"], "direction": 1},
    {"id": "KNEE_POS", "axis": ["KNEE_POS"], "direction": 1},
    {"id": "ANKLE_POS", "axis": ["ANKLE_POS"], "direction": 1},
    {
        "id": "HIP_NEG_KNEE_POS",
        "axis": ["HIP_MAG_NEG", "KNEE_POS"],
        "direction": 1,
    },
    {
        "id": "HIP_NEG_ANKLE_POS",
        "axis": ["HIP_MAG_NEG", "ANKLE_POS"],
        "direction": 1,
    },
    {
        "id": "KNEE_POS_ANKLE_POS",
        "axis": ["KNEE_POS", "ANKLE_POS"],
        "direction": 1,
    },
    {
        "id": "HIP_NEG_KNEE_POS_ANKLE_POS",
        "axis": ["HIP_MAG_NEG", "KNEE_POS", "ANKLE_POS"],
        "direction": 1,
    },
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
        != "winner_v17.support_action_combination_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v17 preregistration changed")
    if value.get("frozen_screen") != {
        "checkpoint_labels": ["half", "final"],
        "failure_configuration_ids": list(FAILURE_IDS),
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "interventions": list(INTERVENTIONS),
        "target_offset_per_active_axis_rad": 0.03,
        "normalized_offset_per_active_axis": 0.12,
        "duration_ticks": 250,
        "cells_per_checkpoint_intervention": 12,
        "total_cells": 192,
        "optimizer_updates": 0,
    }:
        raise ValueError("Winner-v17 frozen screen changed")
    if value.get("baseline_reproduction") != {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }:
        raise ValueError("Winner-v17 baseline reproduction contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v17 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v17 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v17 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", type=Path, required=True)
    known, _ = parser.parse_known_args()

    base.PREREGISTRATION = PREREGISTRATION
    base.validate_preregistration = validate_preregistration
    base.INTERVENTIONS = INTERVENTIONS
    v14.scale_one_matches_formal = v2.baseline_matches_formal
    direction_module.intervene = combination.intervene
    base_return_code = base.main()

    result = json.loads(known.output.read_text(encoding="utf-8"))
    if (
        base_return_code != 1
        or result["failed_validity_checks"] != ["exact_168_cells"]
        or result["execution"]["diagnostic_cells"] != 192
        or result["validity_checks"].pop("exact_168_cells") is not False
        or not all(result["validity_checks"].values())
    ):
        raise ValueError("Winner-v17 base-adapter accounting changed")
    result["validity_checks"]["exact_192_cells"] = True
    result["failed_validity_checks"] = []

    summaries = result["intervention_summary"]
    order = {row["id"]: index for index, row in enumerate(INTERVENTIONS)}
    for name, summary in summaries.items():
        intervention = summary["intervention"]
        summary["active_axis_count"] = (
            0 if intervention["axis"] is None else len(intervention["axis"])
        )
    candidates = [
        name
        for name, summary in summaries.items()
        if name != "BASELINE" and summary["passes_both_checkpoints"]
    ]
    selected = None
    if candidates:
        selected = min(
            candidates,
            key=lambda name: (
                summaries[name]["active_axis_count"],
                summaries[name]["maximum_abs_action_delta_from_source"],
                summaries[name]["mean_squared_action_delta_from_source"],
                order[name],
            ),
        )

    result["schema_version"] = (
        "winner_v17.support_action_combination_diagnostic_result.v1"
    )
    result["status"] = "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
    result["decision"] = (
        "AUTHORIZE_SELECTED_SUPPORT_COMBINATION_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if selected is not None
        else "NO_SIGN_CONSISTENT_COMBINATION_PASSES_CLOSE_CONSTANT_OFFSET_CLASS"
    )
    result["full_pass_candidates"] = candidates
    result["selected_direction"] = selected
    result["baseline_reproduction"] = {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }
    result["authority"] = {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate CPU-only selected-combination contract preregistration"
        ),
    }
    result["sources"]["base_runner_lf_sha256"] = result["sources"].pop(
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
