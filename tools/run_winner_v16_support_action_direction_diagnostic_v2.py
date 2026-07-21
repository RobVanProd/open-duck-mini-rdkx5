#!/usr/bin/env python3
"""Run the comparator-corrected Winner-v16 bilateral direction diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import run_winner_v14_support_action_diagnostic as v14
import run_winner_v16_support_action_direction_diagnostic as v1


PREREGISTRATION = (
    ANALYSIS
    / "winner_v16_support_action_direction_diagnostic_v2_preregistration.json"
)
INVALID_ATTRIBUTION = (
    ANALYSIS / "winner_v16_support_action_direction_invalid_attribution.json"
)
DERIVED_FLOAT_ABS_TOLERANCE = 1.0e-12
FAILURE_IDS = v1.FAILURE_IDS
INTERVENTIONS = v1.INTERVENTIONS


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def derived_values_equivalent(diagnostic: Any, formal: Any) -> bool:
    """Compare derived JSON values exactly except for bounded finite floats."""

    if type(diagnostic) is not type(formal):
        return False
    if isinstance(diagnostic, dict):
        return set(diagnostic) == set(formal) and all(
            derived_values_equivalent(diagnostic[name], formal[name])
            for name in diagnostic
        )
    if isinstance(diagnostic, list):
        return len(diagnostic) == len(formal) and all(
            derived_values_equivalent(left, right)
            for left, right in zip(diagnostic, formal, strict=True)
        )
    if type(diagnostic) is float:
        return (
            math.isfinite(diagnostic)
            and math.isfinite(formal)
            and abs(diagnostic - formal) <= DERIVED_FLOAT_ABS_TOLERANCE
        )
    return diagnostic == formal


def baseline_matches_formal(
    diagnostic: Mapping[str, Any], formal: Mapping[str, Any]
) -> bool:
    """Require exact baseline traces and gate fields plus bounded derived doubles."""

    exact_scalar_fields = (
        "configuration_id",
        "configuration_sha256",
        "plant",
        "condition",
        "support_pass",
        "maximum_jax_onnx_hidden_error",
        "final_h_out",
        "constant_normalized_prediction_mse",
    )
    if any(diagnostic[name] != formal[name] for name in exact_scalar_fields):
        return False
    if diagnostic["source_previous_action_out_exact"] is not True:
        return False
    if any(
        diagnostic["trace_hashes"][name] != formal["trace_hashes"][name]
        for name in ("observations", "actions", "predictions", "hidden")
    ):
        return False
    return derived_values_equivalent(
        diagnostic["terminal"], formal["terminal"]
    ) and derived_values_equivalent(diagnostic["episode"], formal["episode"])


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v16.support_action_direction_diagnostic_preregistration.v2"
        or value.get("status")
        != "PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
        or value.get("decision")
        != "AUTHORIZE_ONE_COMPARATOR_CORRECTED_CPU_ONLY_DIRECTION_DIAGNOSTIC"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v16 v2 preregistration changed")
    frozen = value.get("frozen_screen", {})
    if frozen != {
        "checkpoint_labels": ["half", "final"],
        "failure_configuration_ids": list(FAILURE_IDS),
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "interventions": list(INTERVENTIONS),
        "target_offset_rad": 0.03,
        "normalized_offset": 0.12,
        "duration_ticks": 250,
        "cells_per_checkpoint_intervention": 12,
        "total_cells": 168,
        "optimizer_updates": 0,
    }:
        raise ValueError("Winner-v16 v2 screen changed")
    if value.get("baseline_reproduction") != {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }:
        raise ValueError("Winner-v16 v2 baseline reproduction contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v16 v2 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v16 v2 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v16 v2 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", type=Path, required=True)
    known, _ = parser.parse_known_args()

    # Inject only the reviewed preregistration and baseline-equivalence correction.
    v1.PREREGISTRATION = PREREGISTRATION
    v1.validate_preregistration = validate_preregistration
    v14.scale_one_matches_formal = baseline_matches_formal
    return_code = v1.main()

    result = json.loads(known.output.read_text(encoding="utf-8"))
    result["schema_version"] = (
        "winner_v16.support_action_direction_diagnostic_result.v2"
    )
    if result["status"] == "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC":
        result["status"] = "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
    elif result["status"] == "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC":
        result["status"] = "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
    else:
        raise ValueError("Winner-v16 v1 result status changed")
    result["baseline_reproduction"] = {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }
    result["sources"]["base_runner_lf_sha256"] = result["sources"].pop(
        "runner_lf_sha256"
    )
    result["sources"]["runner_lf_sha256"] = lf_sha256(Path(__file__))
    result["sources"]["invalid_attribution_lf_sha256"] = lf_sha256(
        INVALID_ATTRIBUTION
    )
    known.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
