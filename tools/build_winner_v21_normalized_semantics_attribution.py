#!/usr/bin/env python3
"""Attribute the Winner-v21 HOLD from committed evidence, with no simulation."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
GATE_RESULT = ANALYSIS / "winner_v21_predictor_preserving_support_gate_result.json"
TRAINING_RESULT = ANALYSIS / "winner_v21_predictor_preserving_training_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
V13_MECHANICS = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
V13_EVALUATOR = ROOT / "tools/run_winner_v13_normalized_response_stage1.py"
V21_MECHANICS = ROOT / "patches/winner_v21_predictor_preserving_joint_support.py"
V21_TRAINER = ROOT / "tools/run_winner_v21_predictor_preserving_training.py"
V12_GATE = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
V21_GATE = ROOT / "tools/run_winner_v21_predictor_preserving_support_gate.py"
OUTPUT_JSON = ANALYSIS / "winner_v21_normalized_semantics_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION_20260721.md"
SOURCES = {
    "gate_result": GATE_RESULT,
    "training_result": TRAINING_RESULT,
    "stage1_result": STAGE1_RESULT,
    "v13_mechanics": V13_MECHANICS,
    "v13_evaluator": V13_EVALUATOR,
    "v21_mechanics": V21_MECHANICS,
    "v21_trainer": V21_TRAINER,
    "v12_gate": V12_GATE,
    "v21_gate": V21_GATE,
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


def require_semantic_evidence() -> None:
    v13 = V13_MECHANICS.read_text(encoding="utf-8")
    v13_eval = V13_EVALUATOR.read_text(encoding="utf-8")
    v21 = V21_MECHANICS.read_text(encoding="utf-8")
    v21_trainer = V21_TRAINER.read_text(encoding="utf-8")
    v12_gate = V12_GATE.read_text(encoding="utf-8")
    v21_gate = V21_GATE.read_text(encoding="utf-8")
    required = {
        "v13 head meaning": (
            "normalized_prediction = (" in v13
            and "target = normalized_target(batch[\"targets\"], target_mean, target_std)" in v13
            and "jnp.square(prediction - target)" in v13
        ),
        "v13 evaluator meaning": (
            "target_normalized = (" in v13_eval
            and "learned_sq = np.square(prediction.astype(np.float64) - target_normalized)" in v13_eval
        ),
        "v21 raw-coordinate loss": (
            "def predictor_loss(" in v21
            and "target_mean" not in v21[v21.index("def predictor_loss("):v21.index("def _tree_rms(")]
            and "normalized_error = (predictions - targets) / target_std" in v21
        ),
        "v21 trainer consumes wrong loss": (
            "return v21.predictor_loss(values, data, target_std)" in v21_trainer
        ),
        "v12 gate raw-coordinate evaluator": (
            "np.square((prediction_np - target) / target_std)" in v12_gate
        ),
        "v21 gate binds v12 semantics": (
            "import winner_v12_calibrator_training as training_module" in v21_gate
            and "import run_winner_v12_calibrator_support_gate as reviewed_gate_module" in v21_gate
        ),
    }
    failed = [name for name, passed in required.items() if not passed]
    if failed:
        raise ValueError(f"normalized-semantics source evidence changed: {failed}")


def checkpoint_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    cells = list(row["core_model_plant_cells"]) + list(
        row["sensor_transport_plant_cells"]
    )
    failed = [cell for cell in cells if not cell["support_pass"]]
    reasons: Counter[str] = Counter()
    for cell in failed:
        terminal = cell.get("terminal")
        if not isinstance(terminal, Mapping):
            raise ValueError("failed Winner-v21 cell lacks terminal evidence")
        reasons.update(name for name, passed in terminal["checks"].items() if not passed)
    predictor = {}
    for plant, values in row["heldout_prediction"].items():
        learned = float(values["learned_normalized_prediction_mse"])
        constant = float(values["constant_normalized_prediction_mse"])
        predictor[plant] = {
            "reported_learned_mse": learned,
            "reported_constant_mse": constant,
            "reported_learned_to_constant_ratio": learned / constant,
            "reported_learned_strictly_below_constant": bool(
                values["learned_strictly_below_constant"]
            ),
            "classification_valid_for_v13_normalized_head": False,
        }
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
        "predictor": predictor,
        "all_heldout_contexts_separate": bool(
            row["checks"]["all_16_heldout_contexts_separate"]
        ),
        "all_heldout_repeats_bit_exact": bool(
            row["checks"]["all_32_heldout_repeats_bit_exact"]
        ),
    }


def build_payload() -> dict[str, Any]:
    gate = load(GATE_RESULT)
    training = load(TRAINING_RESULT)
    stage1 = load(STAGE1_RESULT)
    if (
        gate.get("status") != "HOLD_WINNER_V21_PREDICTOR_PRESERVING_SUPPORT_GATE"
        or gate.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or gate.get("failed_checks") != ["all_248_main_cells_pass"]
        or training.get("status")
        != "PASS_WINNER_V21_PREDICTOR_PRESERVING_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
    ):
        raise ValueError("Winner-v21 attribution source decision changed")
    require_semantic_evidence()
    checkpoints = [checkpoint_summary(row) for row in gate["checkpoint_results"]]
    if [row["label"] for row in checkpoints] != ["half", "final"]:
        raise ValueError("Winner-v21 checkpoint order changed")
    if any(
        row["terminal_failed_check_counts"] != {"roll_pitch": row["failing_support_cells"]}
        for row in checkpoints
    ):
        raise ValueError("Winner-v21 physical failure is not tilt-only")
    metrics = training["metrics"]
    if len(metrics) != 100 or [int(row["update"]) for row in metrics] != list(range(1, 101)):
        raise ValueError("Winner-v21 training metric sequence changed")
    source_final = stage1["checkpoint_results"][1]
    if source_final.get("label") != "final" or not all(
        row["learned_strictly_below_constant"]
        for row in source_final["predictor_by_plant"].values()
    ):
        raise ValueError("Winner-v13 normalized predictor source changed")
    sources = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(path),
        }
        for name, path in SOURCES.items()
    }
    return {
        "schema_version": "winner_v21.normalized_semantics_attribution.v1",
        "status": "PASS_WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION",
        "decision": "AUTHORIZE_CORRECT_NORMALIZED_PREDICTOR_CPU_CONTRACT_ONLY",
        "support_gate": {
            "result_status": gate["status"],
            "result_decision": gate["decision"],
            "formal_support_cells": gate["execution"]["formal_support_cells"],
            "heldout_repeat_cells": gate["execution"]["heldout_repeat_cells"],
            "checkpoints": checkpoints,
        },
        "training_loss_reported_under_raw_coordinate_formula": {
            "update_1": float(metrics[0]["predictor_loss"]),
            "update_50": float(metrics[49]["predictor_loss"]),
            "update_100": float(metrics[99]["predictor_loss"]),
            "classification_valid_for_v13_normalized_head": False,
        },
        "source_stage1_normalized_predictor": {
            "snapshot_sha256": source_final["snapshot"]["sha256"],
            "predictor_by_plant": source_final["predictor_by_plant"],
        },
        "findings": {
            "v13_auxiliary_head_outputs_normalized_coordinates": True,
            "v21_training_compared_normalized_output_as_if_raw": True,
            "v21_gate_compared_normalized_output_as_if_raw": True,
            "v21_predictor_metric_is_invalid_for_its_frozen_v13_head": True,
            "v21_physical_support_still_fails_independently_of_predictor_metric": True,
            "all_physical_failures_are_roll_pitch_only": True,
            "completed_v21_result_remains_a_hold": True,
            "flat_transport_equation_selected": False,
        },
        "selected_next_contract": {
            "name": "normalized_predictor_preserving_joint_recurrent_support",
            "required_formula": (
                "prediction_normalized - ((next_response_raw - target_mean) / target_std)"
            ),
            "required_evaluator_formula": (
                "square(prediction_normalized - normalized_target); constant = square(normalized_target)"
            ),
            "must_preserve": [
                "identical Stage-1 source snapshot",
                "identical 115-D observation, 14-D action, 64-state and previous_action ABI",
                "identical PPO objective, population, seeds, action boundary and support matrix",
                "no true configuration or plant label input",
                "both half and final must pass; no closest-checkpoint selection",
            ],
            "first_step_only": (
                "a separately hash-frozen zero-update formula/evaluator contract; no training"
            ),
        },
        "authority": {
            "new_simulation_cells": 0,
            "optimizer_updates_authorized_now": 0,
            "locomotion_training_authorized": False,
            "robot_clearance": False,
            "robot_or_rdk_access": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separately hash-frozen zero-update normalized-semantics CPU contract"
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
        raise FileExistsError("refusing to overwrite Winner-v21 attribution")
    payload = build_payload()
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    half, final = payload["support_gate"]["checkpoints"]
    losses = payload["training_loss_reported_under_raw_coordinate_formula"]
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v21 normalized-semantics failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                (
                    "- Physical support pass, half/final: "
                    f"`{half['passing_support_cells']}/124` / "
                    f"`{final['passing_support_cells']}/124`; every failure is roll/pitch"
                ),
                (
                    "- Reported predictor loss, updates 1/50/100: "
                    f"`{losses['update_1']:.6g}` / `{losses['update_50']:.6g}` / "
                    f"`{losses['update_100']:.6g}`"
                ),
                "- Root cause: the inherited head outputs normalized coordinates, but Winner-v21 training and its gate treated those values as raw physical responses",
                "- Completed Winner-v21 classification: remains `HOLD` because physical support also fails",
                "- Flat-transport equation: `not selected`",
                "- New simulation / optimizer updates / robot access: `0 / 0 / 0`",
                "",
                "The next authorized work is only a zero-update contract for the corrected",
                "normalized-coordinate predictor formula and matching evaluator. No policy",
                "training, response-conditioned locomotion, deployment, or hardware is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
