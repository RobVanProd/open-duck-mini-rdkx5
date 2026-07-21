#!/usr/bin/env python3
"""Attribute the Winner-v15 pitch-margin support-gate HOLD."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
V13_ATTRIBUTION = ANALYSIS / "winner_v13_support_controller_hold_attribution.json"
V14_DIAGNOSTIC = ANALYSIS / "winner_v14_support_action_diagnostic_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
OUTPUT = ANALYSIS / "winner_v15_pitch_margin_support_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION_20260721.md"
EXPECTED_RESULT_SHA256 = "5f239afe0333eb9a9c42ad10eb6079c0cf5a4bf0ca63e122d07c47dd83c1e287"
FAILED_IDS = [
    "COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG",
    "DISCOVERY_03", "HELDOUT_04", "HELDOUT_09",
]
SOURCES = {
    "builder": Path("tools/build_winner_v15_pitch_margin_support_hold_attribution.py"),
    "formal_gate_result": Path("outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"),
    "formal_gate_importer": Path("tools/import_winner_v15_pitch_margin_support_gate_result.py"),
    "formal_gate_runner": Path("tools/run_winner_v15_pitch_margin_support_gate.py"),
    "reviewed_base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "pitch_margin_training_result": Path("outputs/analysis/winner_v15_pitch_margin_support_training_result.json"),
    "pitch_margin_training_runner": Path("tools/run_winner_v15_pitch_margin_support_training.py"),
    "pitch_margin_patch": Path("patches/winner_v15_pitch_margin_support.py"),
    "v13_hold_attribution": Path("outputs/analysis/winner_v13_support_controller_hold_attribution.json"),
    "v14_action_diagnostic": Path("outputs/analysis/winner_v14_support_action_diagnostic_result.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def configuration_index() -> dict[str, Mapping[str, Any]]:
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    rows = matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    return {row["id"]: row for row in rows}


def summarize(checkpoint: Mapping[str, Any], configurations: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    cells = checkpoint["core_model_plant_cells"] + checkpoint["sensor_transport_plant_cells"]
    failed = [cell for cell in cells if cell["support_pass"] is False]
    if len(cells) != 124 or len(failed) != 12:
        raise ValueError(f"Winner-v15 {checkpoint['label']} support population changed")
    if any(cell["condition"] is not None for cell in failed):
        raise ValueError("Winner-v15 has a sensor/transport failure")
    ids = sorted({cell["configuration_id"] for cell in failed})
    if ids != FAILED_IDS:
        raise ValueError(f"Winner-v15 failure set changed: {ids}")
    counts = Counter(cell["configuration_id"] for cell in failed)
    if counts != {name: 2 for name in FAILED_IDS}:
        raise ValueError("Winner-v15 failure plant coverage changed")
    terminal_checks = Counter(
        name for cell in failed for name, passed in cell["terminal"]["checks"].items() if not passed
    )
    if terminal_checks != {"roll_pitch": 12}:
        raise ValueError("Winner-v15 terminal mechanism changed")
    x_offsets = {
        name: float(configurations[name]["torso_com_offset_m"][0]) for name in ids
    }
    if not all(value < 0.0 for value in x_offsets.values()):
        raise ValueError("Winner-v15 failure escaped negative-X support")
    contexts = checkpoint["heldout_context_separation"]
    repeats = checkpoint["heldout_repeatability"]
    if len(contexts) != 16 or not all(row["separation_above_1e_7"] for row in contexts):
        raise ValueError("Winner-v15 context separation changed")
    if len(repeats) != 32 or not all(row["bit_exact"] for row in repeats):
        raise ValueError("Winner-v15 repeatability changed")
    return {
        "failure_count": 12,
        "failure_configuration_counts": dict(sorted(counts.items())),
        "failure_configuration_x_offsets_m": dict(sorted(x_offsets.items())),
        "sensor_transport_failure_count": 0,
        "failed_terminal_checks": dict(terminal_checks),
        "terminal_tick_range": [
            min(cell["terminal"]["tick"] for cell in failed),
            max(cell["terminal"]["tick"] for cell in failed),
        ],
        "terminal_pitch_rad_range": [
            min(cell["terminal"]["pitch_rad"] for cell in failed),
            max(cell["terminal"]["pitch_rad"] for cell in failed),
        ],
        "terminal_gyro_xy_norm_rad_s_range": [
            min(cell["terminal"]["gyro_xy_norm_rad_s"] for cell in failed),
            max(cell["terminal"]["gyro_xy_norm_rad_s"] for cell in failed),
        ],
        "all_16_contexts_separate": True,
        "minimum_context_linf_separation": min(row["final_h_out_linf_separation"] for row in contexts),
        "all_32_repeats_bit_exact": True,
        "legacy_reported_prediction_metrics": checkpoint["heldout_prediction"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite HOLD attribution: {path}")
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(FORMAL_RESULT) != EXPECTED_RESULT_SHA256
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or formal.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or formal.get("execution") != {
            "formal_support_cells": 248, "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0, "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v15 formal evidence changed")
    v13 = json.loads(V13_ATTRIBUTION.read_text(encoding="utf-8"))
    if v13.get("status") != "PASS_WINNER_V13_SUPPORT_CONTROLLER_HOLD_ATTRIBUTION":
        raise ValueError("Winner-v13 comparison changed")
    v14 = json.loads(V14_DIAGNOSTIC.read_text(encoding="utf-8"))
    if v14.get("status") != "PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC":
        raise ValueError("Winner-v14 corrected-scoring evidence changed")
    corrected_rows = [
        row for scale in v14["scale_summary"] if scale["scale"] == 1.0
        for row in scale["checkpoint_results"]
    ]
    if len(corrected_rows) != 2 or not all(
        row["checks"]["corrected_prediction_beats_constant_per_plant"] for row in corrected_rows
    ):
        raise ValueError("corrected predictor evidence changed")
    configs = configuration_index()
    summaries = {row["label"]: summarize(row, configs) for row in formal["checkpoint_results"]}
    baseline = v13["physical_failure"]["checkpoint_results"]
    persistent = sorted(
        set(summaries["half"]["failure_configuration_counts"])
        & set(summaries["final"]["failure_configuration_counts"])
        & set(baseline["half"]["failure_configuration_ids"])
        & set(baseline["final"]["failure_configuration_ids"])
    )
    expected_persistent = FAILED_IDS
    if persistent != expected_persistent:
        raise ValueError("persistent failure core changed")
    sources = {
        name: {"path": str(path).replace("\\", "/"), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v15.pitch_margin_support_hold_attribution.v1",
        "status": "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION",
        "decision": "CLOSE_PITCH_MARGIN_OBJECTIVE_PREREGISTER_ACTION_DIRECTION_DIAGNOSTIC",
        "formal_result": {
            "path": str(FORMAL_RESULT.relative_to(ROOT)).replace("\\", "/"),
            "sha256": EXPECTED_RESULT_SHA256,
            "status": formal["status"], "decision": formal["decision"],
        },
        "physical_failure": {
            "classification": "PERSISTENT_NEGATIVE_X_EARLY_BACKWARD_PITCH_INSTABILITY",
            "checkpoint_results": summaries,
            "persistent_failure_configuration_ids": persistent,
            "all_failures_are_roll_pitch_only": True,
            "all_failures_have_negative_torso_com_x": True,
            "sensor_transport_failures": 0,
            "formal_hold_remains_outcome_determining": True,
        },
        "comparison_to_v13": {
            "v13_failure_counts": {"half": baseline["half"]["failure_count"], "final": baseline["final"]["failure_count"]},
            "v15_failure_counts": {"half": 12, "final": 12},
            "half_delta": 12 - baseline["half"]["failure_count"],
            "final_delta": 12 - baseline["final"]["failure_count"],
            "persistent_core_removed": False,
            "persistence_pass": False,
        },
        "reporting_note": {
            "legacy_predictor_failure_is_reporting_only": True,
            "known_defect": "normalized prediction misread as raw response",
            "corrected_v14_source_predictor_passed_both_plants_at_both_checkpoints": True,
            "v15_predictor_recomputation_needed_for_any_future_predictor_dependent_claim": True,
            "outcome_effect": "NONE_SUPPORT_FAILURES_INDEPENDENTLY_HOLD_BOTH_CHECKPOINTS",
        },
        "objective_decision": {
            "one_sided_negative_pitch_margin_closed": True,
            "reason": (
                "The dense margin signal was nonzero and exact on every training update, yet the six-configuration persistent core remains at both checkpoints and neither checkpoint passes."
            ),
            "more_updates_or_reward_scale_search_selected": False,
        },
        "evidence_selected_next_step": {
            "flat_transport_kernel_selected": False,
            "reason_flat_transport_not_selected": (
                "All 16 heldout contexts remain separated and failures occur by ticks 28-62; no long-range context collapse is observed."
            ),
            "authorized": (
                "preregister one CPU-only negative-X support action-direction diagnostic on the fixed persistent failure core, with no optimizer updates"
            ),
            "not_authorized": [
                "additional pitch-margin training", "reward-scale search", "response-conditioned locomotion training",
                "checkpoint selection", "runtime deployment", "Gate 5", "robot or RDK-X5 access",
            ],
        },
        "execution": {"new_optimizer_updates": 0, "new_behavior_cells": 0, "locomotion_steps": 0, "robot_or_rdk_access": 0},
        "authority": {"robot_clearance": False, "rdkx5_robot_serial_gpio_i2c_torque_motion": False},
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join([
        "# Winner-v15 pitch-margin support HOLD attribution", "",
        f"- Status: `{payload['status']}`", f"- Decision: `{payload['decision']}`",
        "- Half/final physical failures: `12 / 12`", "- Sensor/transport failures: `0`",
        "- New training / behavior / robot access: `0 / 0 / 0`", "",
        "Both checkpoints remain held by 12 early backward-pitch exits in six negative-X configurations.",
        "All six configurations persist from the Winner-v13 failure set at both checkpoints.",
        "The exact dense pitch-margin signal therefore did not solve the mechanism, and the objective is closed without a scale or duration search.", "",
        "The legacy predictor score repeats the already-attributed normalized-vs-raw reporting defect.",
        "That score is not gate-setting here because the physical support failures independently hold both checkpoints.", "",
        "The next authorized step is a preregistered CPU-only action-direction diagnostic on the fixed persistent core.",
        "The flat-transport kernel remains unselected because contexts separate and failures occur by ticks 28-62.", "",
    ]), encoding="utf-8")
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
