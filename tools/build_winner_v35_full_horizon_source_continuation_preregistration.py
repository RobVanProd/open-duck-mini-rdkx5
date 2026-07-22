#!/usr/bin/env python3
"""Freeze one Winner-v35 full-horizon source-continuation feasibility test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v35_full_horizon_source_continuation_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION_PREREGISTRATION_20260722.md"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V34_RESULT = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_TRAINING = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"

CONFIGURATION_IDS = [
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_07",
    "HELDOUT_09",
    "HELDOUT_15",
]

SOURCES = {
    "builder": Path("tools/build_winner_v35_full_horizon_source_continuation_preregistration.py"),
    "runner": Path("tools/run_winner_v35_full_horizon_source_continuation.py"),
    "runner_tests": Path("tests/test_winner_v35_full_horizon_source_continuation.py"),
    "preregistration_tests": Path("tests/test_winner_v35_full_horizon_source_continuation_preregistration.py"),
    "result_importer": Path("tools/import_winner_v35_full_horizon_source_continuation.py"),
    "result_importer_tests": Path("tests/test_winner_v35_full_horizon_source_continuation_import.py"),
    "workflow": Path(".github/workflows/winner-v35-full-horizon-source-continuation.yml"),
    "winner_v28_result": Path("outputs/analysis/winner_v28_prefix_joint_group_causal_screen_result.json"),
    "winner_v28_runner": Path("tools/run_winner_v28_prefix_joint_group_causal_screen.py"),
    "winner_v34_preregistration": Path("outputs/analysis/winner_v34_prefix_right_pitch_hard_intervention_preregistration.json"),
    "winner_v34_result": Path("outputs/analysis/winner_v34_prefix_right_pitch_hard_intervention_result.json"),
    "winner_v34_runner": Path("tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v32_training_result": Path("outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_result.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v35 preregistration")
    v28 = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    v34 = json.loads(V34_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v32 = json.loads(V32_TRAINING.read_text(encoding="utf-8"))
    if (
        v28.get("status") != "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        or v28.get("selected_group") != "RIGHT_PITCH_CHAIN"
        or v28.get("decision")
        != "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
    ):
        raise ValueError("Winner-v28 hybrid recovery source changed")
    if (
        v34.get("status") != "HOLD_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        or v34.get("classification") != "NO_FULL_DIRECT_PREFIX_SUPPORT_RECOVERY"
        or v34.get("decision") != "CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM"
        or v34.get("summary", {}).get("originally_failing_cells") != 55
        or v34.get("summary", {}).get("originally_passing_cells") != 5
        or v34.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v34 does not authorize the feasibility question")
    if (
        v22.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v32.get("status") != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or v32.get("failed_checks") != []
    ):
        raise ValueError("Winner-v35 training artifacts changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    value = {
        "schema_version": "winner_v35.full_horizon_source_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_FULL_HORIZON_SOURCE_CONTINUATION_ONLY",
        "question": (
            "Does the exact V28 hybrid recovery remain support-valid for the complete "
            "250-tick gate over the expanded Winner-v34 60-cell matrix?"
        ),
        "diagnostic": {
            "candidate_checkpoints": [
                {"label": "half", "update": 251},
                {"label": "final", "update": 301},
            ],
            "source_checkpoint": {
                "label": "winner_v22_final",
                "update": 100,
                "graph": source_graph,
            },
            "configuration_ids": CONFIGURATION_IDS,
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "prefix_ticks": list(range(8)),
            "prefix_replaced_action_indices": [11, 12, 13],
            "source_continuation_ticks": {"first": 8, "last": 249},
            "duration_ticks": 250,
            "expected_hybrid_cells": 60,
            "semantics": (
                "At ticks 0-7, run the Winner-v32 candidate while replacing only action "
                "indices 11/12/13 with Winner-v22 final actions computed on the shared "
                "observation and realized previous-action history. Winner-v22 keeps its own "
                "shadow recurrent state. From tick 8 through 249, Winner-v22 final controls "
                "all 14 actions from that shadow state. No candidate action is used after "
                "the handoff."
            ),
            "reference": (
                "The 60 Winner-v34 RIGHT_PITCH_REPLACED cells are the exact no-source-"
                "continuation comparator and are read from the verified result, not rerun."
            ),
            "action_delta_epsilon": 1.0e-6,
        },
        "pass_rule": {
            "all_60_hybrid_cells_pass_support": True,
            "all_55_v34_failures_recovered": True,
            "all_5_v34_passes_preserved": True,
            "every_tick8_handoff_changes_an_action": True,
            "all_actions_obey_graph_boundary": True,
            "closest_result_selection": False,
        },
        "decision_tree": {
            "full_horizon_feasible": "AUTHORIZE_HYBRID_TEACHER_REPRESENTATION_CPU_CONTRACT_PREREGISTRATION_ONLY",
            "not_full_horizon_feasible": "CLOSE_V28_HYBRID_TEACHER_ROUTE",
            "invalid": "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        },
        "execution_now": {
            "hybrid_support_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": {
            "winner_v22_training": v22["repository_attribution"],
            "winner_v32_training": v32["repository_attribution"],
        },
        "source_results": {
            "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
            "winner_v34_result_lf_sha256": lf_sha256(V34_RESULT),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_hybrid_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen CPU teacher-representation contract",
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
                "# Winner-v35 full-horizon source-continuation preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Hybrid support cells: `60`",
                "- Prefix: candidate with source right-pitch indices at ticks `0-7`",
                "- Continuation: all 14 Winner-v22 source actions at ticks `8-249`",
                "- Optimizer / locomotion training / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "A pass requires all 60 cells. It may authorize only a later CPU contract",
                "for representing a deployable single-policy teacher; the hybrid itself is",
                "not authorized as a runtime wrapper or deployment policy.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
