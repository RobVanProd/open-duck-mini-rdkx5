#!/usr/bin/env python3
"""Preregister one read-only residual teacher causal diagnostic after V53."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v54_residual_teacher_causal_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V54_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md"
V53_RESULT = ANALYSIS / "winner_v53_full_action_teacher_support_gate_result.json"
V53_RESULT_SHA256 = "6fb272a5147dc67074a8196467504717ef7a70b422b355f5c6d7252c7ab41579"

SOURCES = {
    "builder": Path("tools/build_winner_v54_residual_teacher_causal_preregistration.py"),
    "runner": Path("tools/run_winner_v54_residual_teacher_causal.py"),
    "tests": Path("tests/test_winner_v54_residual_teacher_causal.py"),
    "v53_result": Path("outputs/analysis/winner_v53_full_action_teacher_support_gate_result.json"),
    "v53_preregistration": Path("outputs/analysis/winner_v53_full_action_teacher_support_gate_preregistration.json"),
    "v53_runner": Path("tools/run_winner_v53_full_action_teacher_support_gate.py"),
    "v52_result": Path("outputs/analysis/winner_v52_full_action_teacher_training_result.json"),
    "v52_preregistration": Path("outputs/analysis/winner_v52_full_action_teacher_training_preregistration.json"),
    "v48_intervention_mechanics": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
    "v48c_causal_scope_result": Path("outputs/analysis/winner_v48c_causal_population_scope_result.json"),
    "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
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
            raise FileExistsError(f"refusing to overwrite Winner-v54 contract: {path}")
    formal = json.loads(V53_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V53_RESULT) != V53_RESULT_SHA256
        or formal.get("status")
        != "HOLD_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
        or formal.get("decision") != "DO_NOT_SELECT_WINNER_V52_DEPLOYMENT_POLICY"
        or formal.get("selected_checkpoint") is not None
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or formal.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v53 hold identity changed")
    final = next(row for row in formal["checkpoint_results"] if row["label"] == "final")
    failures = [row for row in final["core_model_plant_cells"] if not row["support_pass"]]
    configuration_ids = list(dict.fromkeys(row["configuration_id"] for row in failures))
    expected_ids = [
        "COM_X_NEG",
        "COM_CORNER_01",
        "COM_CORNER_03",
        "DISCOVERY_03",
        "HELDOUT_04",
        "HELDOUT_09",
    ]
    if (
        configuration_ids != expected_ids
        or len(failures) != 12
        or {row["plant"] for row in failures}
        != {"P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"}
        or any(row["terminal"] is None for row in failures)
    ):
        raise ValueError("Winner-v53 final failure population changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v54.residual_teacher_causal_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_48_CELL_CPU_DIAGNOSTIC_ONLY",
        "causal_question": (
            "After the full-14D V52 continuation, does the frozen full teacher still "
            "rescue every final V53 failure, and is the residual mismatch localized to "
            "pitch output or pitch/non-pitch interaction?"
        ),
        "frozen_source": {
            "v53_result_sha256": V53_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 453,
            "snapshot_sha256": final["checkpoint_sha256"],
            "onnx_sha256": final["onnx_sha256"],
            "formal_failed_cells": 12,
            "configuration_ids": configuration_ids,
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        },
        "frozen_arms": {
            "graph": "unchanged V52 final graph",
            "full_teacher": "replace all 14 actor outputs with the frozen V42 target before the unchanged graph bound",
            "pitch_teacher": "replace indices [2,3,4,11,12,13] with the frozen V42 target before the unchanged graph bound",
            "nonpitch_zero": "replace indices [0,1,5,6,7,8,9,10] with zero before the unchanged graph bound",
            "response_state": "retain the graph h_out exactly, matching the reviewed V48 intervention semantics",
        },
        "frozen_execution": {
            "checkpoint_count": 1,
            "configuration_count": 6,
            "plant_count": 2,
            "arm_count": 4,
            "diagnostic_cells": 48,
            "ticks_per_cell": 250,
            "formal_graph_cells_must_match_v53_bit_exact": True,
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
            "no_posthoc_threshold_or_arm_change": True,
        },
        "pass_rule": {
            "exact_48_cells": True,
            "all_12_graph_cells_bit_exact_to_v53": True,
            "exact_12_failed_pair_classifications": True,
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
            "result_authorizes_only": "a separately preregistered mechanism chosen from the frozen classification",
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
                "# Winner-v54 residual-teacher causal preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Population: `6 configurations x 2 plants x 4 arms = 48 cells`",
                "- Checkpoint: exact V52 final update `453`",
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
