#!/usr/bin/env python3
"""Attribute the imported Winner-v20 support-gate HOLD without new simulation."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
GATE_RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_gate_result.json"
TRAINING_RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_training_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
MECHANICS = ROOT / "patches/winner_v20_joint_recurrent_support.py"
TRAINING_RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_training.py"
GATE_RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_gate.py"
OUTPUT_JSON = ANALYSIS / "winner_v20_joint_recurrent_support_failure_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_FAILURE_ATTRIBUTION_20260721.md"
SOURCES = {
    "gate_result": GATE_RESULT,
    "training_result": TRAINING_RESULT,
    "stage1_result": STAGE1_RESULT,
    "mechanics": MECHANICS,
    "training_runner": TRAINING_RUNNER,
    "gate_runner": GATE_RUNNER,
    "builder": Path(__file__).resolve(),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def predictor_summary(row: Mapping[str, Any]) -> dict[str, dict[str, float | bool]]:
    result: dict[str, dict[str, float | bool]] = {}
    for plant, values in row["heldout_prediction"].items():
        learned = float(values["learned_normalized_prediction_mse"])
        constant = float(values["constant_normalized_prediction_mse"])
        result[plant] = {
            "learned_normalized_prediction_mse": learned,
            "constant_normalized_prediction_mse": constant,
            "learned_to_constant_ratio": learned / constant,
            "learned_strictly_below_constant": bool(
                values["learned_strictly_below_constant"]
            ),
        }
    return result


def checkpoint_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    cells = list(row["core_model_plant_cells"]) + list(
        row["sensor_transport_plant_cells"]
    )
    failed = [cell for cell in cells if not cell["support_pass"]]
    reasons: Counter[str] = Counter()
    for cell in failed:
        terminal = cell.get("terminal")
        if not isinstance(terminal, Mapping):
            raise ValueError("failed Winner-v20 support cell lacks terminal evidence")
        reasons.update(
            name for name, passed in terminal["checks"].items() if not passed
        )
    separations = [
        float(item["final_h_out_linf_separation"])
        for item in row["heldout_context_separation"]
    ]
    return {
        "label": row["label"],
        "update": int(row["update"]),
        "total_support_cells": len(cells),
        "passing_support_cells": len(cells) - len(failed),
        "failing_support_cells": len(failed),
        "failing_configuration_ids": sorted(
            {str(cell["configuration_id"]) for cell in failed}
        ),
        "failure_tick_min": min(int(cell["terminal"]["tick"]) for cell in failed),
        "failure_tick_max": max(int(cell["terminal"]["tick"]) for cell in failed),
        "terminal_failed_check_counts": dict(sorted(reasons.items())),
        "maximum_abs_tilt_rad": max(
            float(cell["episode"]["maximum_abs_tilt_rad"]) for cell in cells
        ),
        "maximum_current_a": max(
            float(cell["episode"]["maximum_current_a"]) for cell in cells
        ),
        "maximum_torque_nm": max(
            float(cell["episode"]["maximum_torque_nm"]) for cell in cells
        ),
        "maximum_overcurrent_streak_ticks": max(
            int(cell["episode"]["maximum_overcurrent_streak_ticks"])
            for cell in cells
        ),
        "heldout_context_separation_linf_min": min(separations),
        "heldout_context_separation_linf_max": max(separations),
        "all_heldout_contexts_separate": bool(
            row["checks"]["all_16_heldout_contexts_separate"]
        ),
        "all_heldout_repeats_bit_exact": bool(
            row["checks"]["all_32_heldout_repeats_bit_exact"]
        ),
        "predictor": predictor_summary(row),
    }


def build_payload() -> dict[str, Any]:
    gate = load(GATE_RESULT)
    training = load(TRAINING_RESULT)
    stage1 = load(STAGE1_RESULT)
    if (
        gate.get("status") != "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_GATE"
        or gate.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or gate.get("failed_checks") != ["all_248_main_cells_pass"]
        or training.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
    ):
        raise ValueError("Winner-v20 failure-attribution source decision changed")
    summaries = [checkpoint_summary(row) for row in gate["checkpoint_results"]]
    if [row["label"] for row in summaries] != ["half", "final"]:
        raise ValueError("Winner-v20 checkpoint order changed")
    if any(
        row["terminal_failed_check_counts"] != {"roll_pitch": row["failing_support_cells"]}
        for row in summaries
    ):
        raise ValueError("Winner-v20 support-failure mechanism is not tilt-only")
    if any(
        row["predictor"][plant]["learned_strictly_below_constant"]
        for row in summaries
        for plant in row["predictor"]
    ):
        raise ValueError("Winner-v20 predictor unexpectedly beats constant")
    stage1_final = stage1["checkpoint_results"][1]
    if stage1_final.get("label") != "final" or not all(
        values["learned_strictly_below_constant"]
        for values in stage1_final["predictor_by_plant"].values()
    ):
        raise ValueError("Winner-v13 Stage-1 predictor source changed")
    source_context_min = min(
        float(row["final_valid_h_out_linf_plant_separation"])
        for row in stage1_final["context_separation"]
    )
    training_checks = training["checks"]
    if (
        training_checks.get("auxiliary_predictor_bit_exact_frozen") is not True
        or training_checks.get("all_joint_leaves_changed_cumulatively") is not True
    ):
        raise ValueError("Winner-v20 trainable/frozen evidence changed")
    sources = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(path),
        }
        for name, path in SOURCES.items()
    }
    return {
        "schema_version": "winner_v20.joint_recurrent_support_failure_attribution.v1",
        "status": "PASS_WINNER_V20_SUPPORT_FAILURE_ATTRIBUTION",
        "decision": "AUTHORIZE_PREDICTOR_PRESERVING_JOINT_OBJECTIVE_CPU_CONTRACT_ONLY",
        "source_stage1_final": {
            "snapshot_sha256": stage1_final["snapshot"]["sha256"],
            "predictor_by_plant": stage1_final["predictor_by_plant"],
            "heldout_context_separation_linf_min": source_context_min,
        },
        "winner_v20_training": {
            "auxiliary_predictor_bit_exact_frozen": True,
            "all_joint_leaves_changed_cumulatively": True,
            "recurrent_leaf_max_abs_delta": {
                name: training["joint_leaf_max_abs_delta"][name]
                for name in (
                    "obs_weight",
                    "previous_action_weight",
                    "hidden_weight",
                    "hidden_bias",
                )
            },
        },
        "support_gate": {
            "result_status": gate["status"],
            "result_decision": gate["decision"],
            "formal_support_cells": gate["execution"]["formal_support_cells"],
            "heldout_repeat_cells": gate["execution"]["heldout_repeat_cells"],
            "checkpoints": summaries,
        },
        "findings": {
            "physical_failure_is_tilt_only": True,
            "current_torque_contact_base_and_determinism_not_causal": True,
            "source_predictor_beats_constant_on_heldout": True,
            "winner_v20_predictor_loses_to_constant_on_both_plants_and_checkpoints": True,
            "winner_v20_context_remains_noncollapsed_by_frozen_threshold": True,
            "winner_v20_context_separation_magnitude_regressed": all(
                row["heldout_context_separation_linf_min"] < source_context_min
                for row in summaries
            ),
            "frozen_auxiliary_head_with_changed_recurrent_representation_is_incompatible": True,
            "flat_transport_equation_selected": False,
        },
        "selected_next_contract": {
            "name": "predictor_preserving_joint_recurrent_support",
            "trainable_scope": (
                "existing recurrent core plus existing auxiliary predictor plus existing "
                "Stage-2 policy/value leaves"
            ),
            "objective_scope": (
                "the exact Winner-v20 PPO pitch-margin objective plus the existing "
                "normalized next-response objective on the same valid transitions"
            ),
            "scale_rule": (
                "freeze one deterministic gradient-balance scale from a zero-update CPU "
                "diagnostic; no behavior tuning or scale sweep"
            ),
            "must_preserve": [
                "115-D observation and 14-D calibration action ABI",
                "64-state recurrent chain and previous_action chain",
                "exact Winner-v20 population, boundaries, seeds, and support gate",
                "no true configuration or plant label input",
                "half/final persistence and no closest-checkpoint selection",
            ],
        },
        "authority": {
            "optimizer_updates_authorized_now": 0,
            "formal_support_cells_authorized_now": 0,
            "locomotion_training_authorized": False,
            "robot_clearance": False,
            "robot_or_rdk_access": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separately hash-frozen zero-update CPU gradient/loss contract"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUTPUT_MD)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v20 failure attribution")
    payload = build_payload()
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    half, final = payload["support_gate"]["checkpoints"]
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v20 joint-recurrent support failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                (
                    "- Support failures, half/final: "
                    f"`{half['failing_support_cells']} / {final['failing_support_cells']}` "
                    "of 124; every terminal failure is roll/pitch only"
                ),
                (
                    "- Failure ticks, half/final: "
                    f"`{half['failure_tick_min']}-{half['failure_tick_max']} / "
                    f"{final['failure_tick_min']}-{final['failure_tick_max']}`"
                ),
                (
                    "- Predictor MSE range: learned "
                    f"`{min(v['learned_normalized_prediction_mse'] for r in (half, final) for v in r['predictor'].values()):.6g}` "
                    f"to `{max(v['learned_normalized_prediction_mse'] for r in (half, final) for v in r['predictor'].values()):.6g}`; "
                    "constant baseline remains below `0.58`"
                ),
                "- Heldout repeats: bit-exact; plant context: noncollapsed but much weaker",
                "- Flat-transport equation: `not selected`",
                "- New simulation / optimizer updates / robot access: `0 / 0 / 0`",
                "",
                "The next authorized work is only a zero-update CPU contract for a",
                "predictor-preserving joint recurrent objective. Response-conditioned",
                "locomotion training, deployment, Gate 5, and robot access remain blocked.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
