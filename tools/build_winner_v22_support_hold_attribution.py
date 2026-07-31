#!/usr/bin/env python3
"""Attribute the Winner-v22 support HOLD without running another simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v22_support_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V22_SUPPORT_HOLD_ATTRIBUTION_20260721.md"
RESULTS = {
    "winner_v15": ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json",
    "winner_v20": ANALYSIS / "winner_v20_joint_recurrent_support_gate_result.json",
    "winner_v21": ANALYSIS / "winner_v21_predictor_preserving_support_gate_result.json",
    "winner_v22": ANALYSIS / "winner_v22_normalized_predictor_support_gate_result.json",
}
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v22_support_hold_attribution.py"),
    "tests": Path("tests/test_winner_v22_support_hold_attribution.py"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "winner_v15_result": Path("outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"),
    "winner_v20_result": Path("outputs/analysis/winner_v20_joint_recurrent_support_gate_result.json"),
    "winner_v21_result": Path("outputs/analysis/winner_v21_predictor_preserving_support_gate_result.json"),
    "winner_v22_result": Path("outputs/analysis/winner_v22_normalized_predictor_support_gate_result.json"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v22_gate_preregistration": Path("outputs/analysis/winner_v22_normalized_predictor_support_gate_preregistration.json"),
    "normalized_coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def failed_cells(checkpoint: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        row
        for row in checkpoint["core_model_plant_cells"]
        if row["support_pass"] is False
    ]


def cell_key(row: Mapping[str, Any]) -> str:
    return f"{row['configuration_id']}|{row['plant']}"


def configuration_map(domain: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    matrix = domain["evaluation_matrix"]
    rows = [
        *matrix["fixed_anchors"],
        *matrix["discovery_samples"],
        *matrix["heldout_samples"],
    ]
    result = {str(row["id"]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError("variable-configuration IDs are not unique")
    return result


def summarize_checkpoint(
    checkpoint: Mapping[str, Any], configurations: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    failures = failed_cells(checkpoint)
    reasons = sorted(
        {
            name
            for row in failures
            for name, passed in row["terminal"]["checks"].items()
            if passed is False
        }
    )
    ids = sorted({str(row["configuration_id"]) for row in failures})
    offsets = {
        identifier: configurations[identifier]["torso_com_offset_m"] for identifier in ids
    }
    predictor = checkpoint["heldout_prediction"]
    return {
        "label": checkpoint["label"],
        "update": checkpoint["update"],
        "core_cells": len(checkpoint["core_model_plant_cells"]),
        "physical_support_failures": len(failures),
        "failed_cell_keys": sorted(cell_key(row) for row in failures),
        "failed_configuration_ids": ids,
        "failed_configuration_torso_com_offsets_m": offsets,
        "failure_reasons": reasons,
        "sensor_transport_failures": sum(
            row["support_pass"] is False
            for row in checkpoint["sensor_transport_plant_cells"]
        ),
        "heldout_repeat_failures": sum(
            row["bit_exact"] is False for row in checkpoint["heldout_repeatability"]
        ),
        "heldout_context_separation_failures": sum(
            row["separation_above_1e_7"] is False
            for row in checkpoint["heldout_context_separation"]
        ),
        "prediction_by_plant": predictor,
        "learned_prediction_beats_constant_both_plants": all(
            row["learned_strictly_below_constant"] is True
            for row in predictor.values()
        ),
        "all_physical_failures_have_negative_torso_com_x": all(
            float(configurations[str(row["configuration_id"])]["torso_com_offset_m"][0])
            < 0.0
            for row in failures
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v22 HOLD attribution")
    results = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in RESULTS.items()
    }
    if (
        results["winner_v15"].get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or results["winner_v20"].get("status") != "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_GATE"
        or results["winner_v21"].get("status") != "HOLD_WINNER_V21_PREDICTOR_PRESERVING_SUPPORT_GATE"
        or results["winner_v22"].get("status") != "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
        or results["winner_v22"].get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or results["winner_v22"].get("failed_checks") != ["all_248_main_cells_pass"]
    ):
        raise ValueError("support-lineage evidence changed")
    configurations = configuration_map(json.loads(DOMAIN.read_text(encoding="utf-8")))
    lineage: dict[str, list[dict[str, Any]]] = {}
    for name, result in results.items():
        lineage[name] = [
            summarize_checkpoint(checkpoint, configurations)
            for checkpoint in result["checkpoint_results"]
        ]
    half, final = lineage["winner_v22"]
    half_keys = set(half["failed_cell_keys"])
    final_keys = set(final["failed_cell_keys"])
    checks = {
        "winner_v22_gate_is_valid_hold_not_infrastructure_failure": True,
        "corrected_predictor_beats_constant_both_plants_both_checkpoints": all(
            row["learned_prediction_beats_constant_both_plants"]
            for row in lineage["winner_v22"]
        ),
        "only_physical_support_check_failed": all(
            row["sensor_transport_failures"] == 0
            and row["heldout_repeat_failures"] == 0
            and row["heldout_context_separation_failures"] == 0
            for row in lineage["winner_v22"]
        ),
        "all_winner_v22_failures_are_roll_pitch_only": all(
            row["failure_reasons"] == ["roll_pitch"]
            for row in lineage["winner_v22"]
        ),
        "all_winner_v22_failures_have_negative_torso_com_x": all(
            row["all_physical_failures_have_negative_torso_com_x"]
            for row in lineage["winner_v22"]
        ),
        "winner_v22_does_not_pass_or_improve_over_v15_failure_count": (
            [row["physical_support_failures"] for row in lineage["winner_v22"]]
            == [15, 14]
            and [row["physical_support_failures"] for row in lineage["winner_v15"]]
            == [12, 12]
        ),
        "no_response_conditioned_locomotion_or_robot_authority": (
            results["winner_v22"]["execution"]
            == {
                "formal_support_cells": 248,
                "heldout_repeat_cells": 64,
                "locomotion_training_steps": 0,
                "robot_or_rdk_access": 0,
            }
            and results["winner_v22"]["authority"]["robot_clearance"] is False
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v22.support_hold_attribution.v1",
        "status": (
            "PASS_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION"
            if not failed_checks
            else "HOLD_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION"
        ),
        "decision": (
            "AUTHORIZE_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_ONLY"
            if not failed_checks
            else "DO_NOT_ADVANCE_WINNER_V22"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "lineage": lineage,
        "winner_v22_delta": {
            "recovered_at_final": sorted(half_keys - final_keys),
            "new_at_final": sorted(final_keys - half_keys),
            "common_failures": len(half_keys & final_keys),
        },
        "causal_conclusion": (
            "Correcting normalized predictor semantics repaired the auxiliary evidence: "
            "learned prediction beats the constant baseline in all four checkpoint/plant "
            "comparisons. It did not repair support. Every remaining failure is a roll/pitch "
            "boundary crossing under a negative-X torso-COM domain configuration, and the "
            "v22 failure counts are not better than v15. Prediction accuracy is therefore "
            "necessary but not sufficient; the next question is whether recurrent response "
            "state becomes informative early enough and changes the control action in the "
            "required direction before the negative-X fall."
        ),
        "next_diagnostic": {
            "execution_now": False,
            "type": "offline_cpu_read_only_negative_x_response_use",
            "must_freeze_before_execution": [
                "matched negative-X and nonnegative-X configuration pairs",
                "both Winner-v22 checkpoints and both actuator plants",
                "per-tick hidden, prediction, action, pitch, and target-response traces",
                "same-input hidden-state action fork with no modified-physics rollout",
                "timing and pass/fail metrics decided before execution",
            ],
            "may_not": [
                "train or alter parameters",
                "select a checkpoint",
                "weaken the support gate",
                "use manual mass or COM measurements",
                "access the RDK or robot",
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
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": "a separate read-only negative-X response-use diagnostic preregistration",
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
                "# Winner-v22 support HOLD attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Learned predictor versus constant: `4/4 pass`",
                "- Physical support failures, half/final: `15/124`, `14/124`",
                "- Failure mechanism: `roll_pitch` only",
                "- Failed-domain sign: `negative torso COM X` in every failure",
                "- v15 physical-support failures, half/final: `12/124`, `12/124`",
                "- New simulation / optimization / robot: `0 / 0 / 0`",
                "- Manual mass/COM measurements: `not required`",
                "",
                "The normalization bug is fixed, but response prediction did not create",
                "robust negative-X support control. A pass here authorizes only a separately",
                "frozen read-only response-use diagnostic; it does not authorize training.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
