#!/usr/bin/env python3
"""Preregister one read-only residual-teacher diagnostic after Winner-v61."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v62_residual_teacher_causal_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V62_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md"
V61_RESULT = ANALYSIS / "winner_v61_integrated_support_gate_result.json"
V61_RESULT_SHA256 = "a238ea4511c2c507b32d00c4c898953ee5ed5617399079a3993bdf71a5257255"

SOURCES = {
    "builder": Path("tools/build_winner_v62_residual_teacher_causal_preregistration.py"),
    "runner": Path("tools/run_winner_v62_residual_teacher_causal.py"),
    "tests": Path("tests/test_winner_v62_residual_teacher_causal.py"),
    "v61_result": Path("outputs/analysis/winner_v61_integrated_support_gate_result.json"),
    "v61_preregistration": Path(
        "outputs/analysis/winner_v61_integrated_support_gate_preregistration.json"
    ),
    "v61_builder": Path("tools/build_winner_v61_integrated_support_gate_preregistration.py"),
    "v60_result": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"
    ),
    "v60_preregistration": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_preregistration.json"
    ),
    "intervention_mechanics": Path(
        "tools/run_winner_v48_static_teacher_causal_diagnostic.py"
    ),
    "prior_causal_result": Path(
        "outputs/analysis/winner_v54_residual_teacher_causal_result.json"
    ),
    "teacher_table": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_gate_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
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
            raise FileExistsError(f"refusing to overwrite Winner-v62 contract: {path}")
    formal = json.loads(V61_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V61_RESULT) != V61_RESULT_SHA256
        or formal.get("status") != "HOLD_WINNER_V61_INTEGRATED_SUPPORT_GATE"
        or formal.get("decision") != "DO_NOT_SELECT_WINNER_V60_DEPLOYMENT_POLICY"
        or formal.get("selected_checkpoint") is not None
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or formal.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v61 hold identity changed")
    final = next(row for row in formal["checkpoint_results"] if row["label"] == "final")
    failures = [row for row in final["core_model_plant_cells"] if not row["support_pass"]]
    pairs = [
        {"configuration_id": row["configuration_id"], "plant": row["plant"]}
        for row in failures
    ]
    expected_pairs = [
        {"configuration_id": "COM_X_NEG", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_X_NEG", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_00", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_00", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_01", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_01", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_03", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_03", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "DISCOVERY_03", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "DISCOVERY_03", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "HELDOUT_04", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "HELDOUT_09", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "HELDOUT_09", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
    ]
    if pairs != expected_pairs or any(row["terminal"] is None for row in failures):
        raise ValueError("Winner-v61 final failure population changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v62.residual_teacher_causal_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_52_CELL_CPU_DIAGNOSTIC_ONLY",
        "causal_question": (
            "After the integrated first-tick continuation, does the frozen full teacher "
            "still rescue every final Winner-v61 failure, and is the remaining mismatch "
            "localized to pitch output beyond tick zero?"
        ),
        "frozen_source": {
            "v61_result_sha256": V61_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 554,
            "snapshot_sha256": final["checkpoint_sha256"],
            "onnx_sha256": final["onnx_sha256"],
            "formal_failed_cells": 13,
            "failure_pairs": pairs,
        },
        "frozen_arms": {
            "graph": "unchanged Winner-v60 final graph",
            "full_teacher": "replace all 14 actor outputs with the frozen V42 target before the unchanged graph bound",
            "pitch_teacher": "replace indices [2,3,4,11,12,13] with the frozen V42 target before the unchanged graph bound",
            "nonpitch_zero": "replace indices [0,1,5,6,7,8,9,10] with zero before the unchanged graph bound",
            "response_state": "retain graph h_out exactly, matching reviewed V48/V54 intervention semantics",
        },
        "frozen_execution": {
            "checkpoint_count": 1,
            "failed_pair_count": 13,
            "arm_count": 4,
            "diagnostic_cells": 52,
            "ticks_per_cell": 250,
            "formal_graph_cells_must_match_v61_bit_exact": True,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "classification": {
            "teacher_insufficient": "full_teacher fails",
            "either_single_intervention_rescues": "pitch_teacher and nonpitch_zero both pass",
            "pitch_output_causal": "pitch_teacher passes and nonpitch_zero fails",
            "nonpitch_output_causal": "nonpitch_zero passes and pitch_teacher fails",
            "pitch_nonpitch_interaction": "full_teacher passes and both single interventions fail",
            "report_first_tick_and_post_first_tick_alignment_separately": True,
            "no_posthoc_threshold_or_arm_change": True,
        },
        "pass_rule": {
            "exact_52_cells": True,
            "all_13_graph_cells_bit_exact_to_v61": True,
            "exact_13_failed_pair_classifications": True,
            "all_previous_action_chains_exact": True,
            "all_jax_onnx_hidden_errors_at_most_1e_7": True,
            "all_values_finite": True,
        },
        "execution_now": {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "a separately preregistered mechanism chosen from the frozen classification"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v62 residual-teacher causal preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Population: `13 exact failed pairs x 4 arms = 52 cells`",
                "- Checkpoint: exact Winner-v60 final update `554`",
                "- Alignment: tick zero and post-tick-zero reported separately",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This is a read-only causal diagnostic, not a support-gate retry.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
