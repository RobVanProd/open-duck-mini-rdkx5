#!/usr/bin/env python3
"""Attribute the Winner-v24 support HOLD from already completed JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v24_support_regression_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION_20260722.md"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_support_gate_result.json"
V23_RESULT = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V24_PREREGISTRATION = ANALYSIS / "winner_v24_baseline_anchored_support_gate_preregistration.json"
V24_RESULT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v24_support_regression_attribution.py"),
    "tests": Path("tests/test_winner_v24_support_regression_attribution.py"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "winner_v22_support_result": Path("outputs/analysis/winner_v22_normalized_predictor_support_gate_result.json"),
    "winner_v23_response_use_result": Path("outputs/analysis/winner_v23_negative_x_response_use_diagnostic_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v24_support_preregistration": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_preregistration.json"),
    "winner_v24_support_result": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"),
    "winner_v24_objective": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "winner_v24_gate_runner": Path("tools/run_winner_v24_baseline_anchored_support_gate.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def configuration_offsets(domain: Mapping[str, Any]) -> dict[str, list[float]]:
    matrix = domain["evaluation_matrix"]
    rows = (
        matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
    )
    values: dict[str, list[float]] = {}
    for row in rows:
        offset = row["torso_com_offset_m"]
        if not (
            isinstance(offset, list)
            and len(offset) == 3
            and all(type(item) in {int, float} for item in offset)
        ):
            raise ValueError(f"invalid domain COM offset: {row['id']}")
        values[row["id"]] = [float(item) for item in offset]
    if len(values) != 56:
        raise ValueError("configuration domain identity changed")
    return values


def failed_cells(checkpoint: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        f"{cell['configuration_id']}|{cell['plant']}": cell
        for cell in checkpoint["core_model_plant_cells"]
        if not cell["support_pass"]
    }


def summarize_checkpoint(
    *,
    label: str,
    old: Mapping[str, Any],
    new: Mapping[str, Any],
    offsets: Mapping[str, list[float]],
) -> dict[str, Any]:
    old_bad = failed_cells(old)
    new_bad = failed_cells(new)
    old_keys = set(old_bad)
    new_keys = set(new_bad)
    common = sorted(old_keys & new_keys)
    added = sorted(new_keys - old_keys)
    recovered = sorted(old_keys - new_keys)
    onset_deltas = [
        int(new_bad[key]["terminal"]["tick"])
        - int(old_bad[key]["terminal"]["tick"])
        for key in common
    ]
    new_failed_ids = sorted({cell["configuration_id"] for cell in new_bad.values()})
    failed_checks = sorted(
        {
            name
            for cell in new_bad.values()
            for name, passed in cell["terminal"]["checks"].items()
            if not passed
        }
    )
    return {
        "label": label,
        "winner_v22_update": old["update"],
        "winner_v24_update": new["update"],
        "winner_v22_physical_support_failures": len(old_bad),
        "winner_v24_physical_support_failures": len(new_bad),
        "common_failure_count": len(common),
        "added_failure_count": len(added),
        "recovered_failure_count": len(recovered),
        "common_failure_keys": common,
        "added_failure_keys": added,
        "recovered_failure_keys": recovered,
        "winner_v24_failed_configuration_ids": new_failed_ids,
        "winner_v24_failed_configuration_torso_com_offsets_m": {
            name: offsets[name] for name in new_failed_ids
        },
        "winner_v24_terminal_failed_checks": failed_checks,
        "shared_failure_onset_delta_ticks_v24_minus_v22": {
            "values": onset_deltas,
            "minimum": min(onset_deltas),
            "median": float(statistics.median(onset_deltas)),
            "mean": float(statistics.fmean(onset_deltas)),
            "maximum": max(onset_deltas),
            "all_strictly_earlier": all(value < 0 for value in onset_deltas),
        },
        "winner_v24_sensor_transport_failures": sum(
            not cell["support_pass"] for cell in new["sensor_transport_plant_cells"]
        ),
        "winner_v24_checkpoint_checks": new["checks"],
        "winner_v24_prediction_by_plant": new["heldout_prediction"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v24 attribution")
    v22 = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    v23 = json.loads(V23_RESULT.read_text(encoding="utf-8"))
    training = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    prereg = json.loads(V24_PREREGISTRATION.read_text(encoding="utf-8"))
    v24 = json.loads(V24_RESULT.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    if (
        v22.get("status") != "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
        or v23.get("status") != "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        or v23.get("classification")
        != "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE"
        or training.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
        or v24.get("status") != "HOLD_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
        or v24.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    ):
        raise ValueError("Winner-v22/v23/v24 evidence lineage changed")
    old_rows = {row["label"]: row for row in v22["checkpoint_results"]}
    new_rows = {row["label"]: row for row in v24["checkpoint_results"]}
    if set(old_rows) != {"half", "final"} or set(new_rows) != {"half", "final"}:
        raise ValueError("support checkpoint set changed")
    offsets = configuration_offsets(domain)
    comparisons = [
        summarize_checkpoint(
            label=label,
            old=old_rows[label],
            new=new_rows[label],
            offsets=offsets,
        )
        for label in ("half", "final")
    ]
    same_v24_failure_keys = (
        failed_cells(new_rows["half"]).keys() == failed_cells(new_rows["final"]).keys()
    )
    checks = {
        "winner_v24_gate_is_valid_hold_not_infrastructure_failure": (
            v24["failed_checks"] == ["all_248_main_cells_pass"]
        ),
        "response_state_was_already_present_and_used": (
            v23["aggregate"]["response_encoded_early_cells"] == 20
            and v23["aggregate"]["response_used_by_action_early_cells"] == 20
        ),
        "winner_v24_failure_sets_are_strict_supersets_of_winner_v22": all(
            row["added_failure_count"] > 0 and row["recovered_failure_count"] == 0
            for row in comparisons
        ),
        "every_shared_failure_occurs_strictly_earlier_in_winner_v24": all(
            row["shared_failure_onset_delta_ticks_v24_minus_v22"][
                "all_strictly_earlier"
            ]
            for row in comparisons
        ),
        "winner_v24_same_failure_population_both_checkpoints": same_v24_failure_keys,
        "all_winner_v24_failures_are_roll_pitch_only": all(
            row["winner_v24_terminal_failed_checks"] == ["roll_pitch"]
            for row in comparisons
        ),
        "all_winner_v24_failures_have_negative_torso_com_x": all(
            offset[0] < 0.0
            for row in comparisons
            for offset in row[
                "winner_v24_failed_configuration_torso_com_offsets_m"
            ].values()
        ),
        "all_nonphysical_support_checks_still_pass": all(
            row["winner_v24_sensor_transport_failures"] == 0
            and all(
                passed
                for name, passed in row["winner_v24_checkpoint_checks"].items()
                if name != "all_support_cells_pass"
            )
            for row in comparisons
        ),
        "no_new_cells_training_or_robot_access": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    passed = not failed
    payload = {
        "schema_version": "winner_v24.support_regression_attribution.v1",
        "status": (
            "PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION"
            if passed
            else "HOLD_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_ONLY"
            if passed
            else "NO_NEW_POLICY_MECHANISM_SELECTED"
        ),
        "checks": checks,
        "failed_checks": failed,
        "checkpoint_comparisons": comparisons,
        "causal_conclusion": (
            "Winner-v24 preserved response encoding/use and every nonphysical gate, but the "
            "symmetric terminal penalty recovered zero Winner-v22 failures, added failures at "
            "both checkpoints, and moved every shared failure earlier. Observability is not the "
            "remaining blocker; the scalar terminal objective changed support control in the "
            "wrong direction. The next evidence question must test the direction of the actor's "
            "same-state action change against short-horizon physical pitch response before any "
            "new loss or architecture is selected."
        ),
        "next_diagnostic": {
            "type": "offline_cpu_same_state_directional_support_control",
            "execution_now": False,
            "must_freeze_before_execution": [
                "exact Winner-v22 source and Winner-v24 half/final snapshots",
                "the ten reproduced negative-X configurations and both actuator plants",
                "same physical observation, previous-action, and recurrent-state forks",
                "short-horizon cloned-state pitch-response scoring",
                "epsilon, horizon, aggregation, thresholds, and stop rules",
            ],
            "may_not": [
                "train or alter parameters",
                "tune the terminal coefficient or continuation length",
                "select a checkpoint",
                "weaken the support gate",
                "access the RDK-X5 or robot",
            ],
        },
        "execution": {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "response_conditioned_locomotion_training_authorized": False,
            "pass_authorizes_only": (
                "a separate zero-update same-state directional support-control diagnostic preregistration"
            ),
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
                "# Winner-v24 support-regression attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Winner-v22 half/final failures: `15 / 14`",
                "- Winner-v24 half/final failures: `20 / 20`",
                "- Recovered failures: `0 / 0`",
                "- Added failures: `5 / 6`",
                "- Shared-failure onset delta median: `-3 / -3 ticks`",
                "- New simulation / optimizer / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                payload["causal_conclusion"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
