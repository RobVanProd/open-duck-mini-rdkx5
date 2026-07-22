#!/usr/bin/env python3
"""Freeze one zero-update Winner-v34 direct prefix intervention diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION_PREREGISTRATION_20260722.md"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
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
RIGHT_PITCH_INDICES = [11, 12, 13]

SOURCES = {
    "builder": Path("tools/build_winner_v34_prefix_right_pitch_hard_intervention_preregistration.py"),
    "runner": Path("tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"),
    "runner_tests": Path("tests/test_winner_v34_prefix_right_pitch_hard_intervention.py"),
    "preregistration_tests": Path("tests/test_winner_v34_prefix_right_pitch_hard_intervention_preregistration.py"),
    "result_importer": Path("tools/import_winner_v34_prefix_right_pitch_hard_intervention.py"),
    "result_importer_tests": Path("tests/test_winner_v34_prefix_right_pitch_hard_intervention_import.py"),
    "workflow": Path(".github/workflows/winner-v34-prefix-right-pitch-hard-intervention.yml"),
    "winner_v28_result": Path("outputs/analysis/winner_v28_prefix_joint_group_causal_screen_result.json"),
    "winner_v28_runner": Path("tools/run_winner_v28_prefix_joint_group_causal_screen.py"),
    "winner_v33_result": Path("outputs/analysis/winner_v33_prefix_right_pitch_anchor_support_gate_result.json"),
    "winner_v33_runner": Path("tools/run_winner_v33_prefix_right_pitch_anchor_support_gate.py"),
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


def _require_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    v28 = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    v33 = json.loads(V33_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v32 = json.loads(V32_TRAINING.read_text(encoding="utf-8"))
    if (
        v28.get("status") != "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        or v28.get("classification") != "SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
        or v28.get("selected_group") != "RIGHT_PITCH_CHAIN"
    ):
        raise ValueError("Winner-v28 did not localize the right-pitch prefix mechanism")
    if (
        v33.get("status") != "HOLD_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE"
        or v33.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or v33.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v33 does not support the direct diagnostic")
    if (
        v22.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v32.get("status") != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or v32.get("failed_checks") != []
    ):
        raise ValueError("Winner-v22/V32 artifact authority changed")
    return v28, v33, v22, v32


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v34 preregistration")
    v28, v33, v22, v32 = _require_sources()
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v34.prefix_right_pitch_hard_intervention_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_DIRECT_PREFIX_INTERVENTION_ONLY",
        "question": (
            "Does exact Winner-v22 right-pitch-chain action replacement during ticks 0-7 "
            "repair every Winner-v33 failure-union support cell when the Winner-v32 candidate "
            "then resumes unchanged?"
        ),
        "diagnostic": {
            "source_checkpoint": {
                "label": "winner_v22_final",
                "update": 100,
                "graph": next(
                    row["graph"]
                    for row in v22["persistent_checkpoints"]
                    if row["label"] == "final" and row["update"] == 100
                ),
            },
            "candidate_checkpoints": [
                {"label": "half", "update": 251},
                {"label": "final", "update": 301},
            ],
            "configuration_ids": CONFIGURATION_IDS,
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "arms": {"CONTROL": [], "RIGHT_PITCH_REPLACED": RIGHT_PITCH_INDICES},
            "replacement_ticks": list(range(8)),
            "duration_ticks": 250,
            "replacement_semantics": (
                "At ticks 0-7 only, replace candidate action indices 11/12/13 with "
                "Winner-v22 final deterministic bounded actions computed on the same candidate "
                "observation and realized previous-action history. Preserve candidate hidden "
                "state and every other candidate action. The source keeps a separate shadow "
                "hidden state. At tick 8 the candidate resumes unchanged."
            ),
            "expected_cells": 120,
            "expected_cells_per_arm": 60,
            "action_delta_epsilon": 1.0e-6,
            "control_scalar_float_atol": 1.0e-12,
            "control_replay": (
                "CONTROL must bit-exactly reproduce the corresponding Winner-v33 action and "
                "hidden trace hashes plus the terminal tick/reason and support outcome. "
                "Long full-duration MuJoCo observation bytes are not required to match across "
                "CPU executions when the entire action/hidden chain remains exact. Redundant "
                "continuous MuJoCo scalar summaries may differ by at most 1e-12; all discrete "
                "values and the policy-produced hashes remain exact."
            ),
        },
        "pass_rule": {
            "all_60_control_cells_replay_v33_exactly": True,
            "all_60_replacement_cells_pass_support": True,
            "all_originally_failing_cells_recovered": True,
            "all_originally_passing_cells_remain_passing": True,
            "every_replacement_cell_changes_a_named_action": True,
            "closest_result_selection": False,
        },
        "decision_tree": {
            "full_recovery": "AUTHORIZE_HARD_PREFIX_MECHANISM_OBJECTIVE_PREREGISTRATION_ONLY",
            "not_full_recovery": "CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM",
            "invalid": "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        },
        "execution_now": {
            "control_cells": 0,
            "replacement_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": {
            "winner_v22_training": v22["repository_attribution"],
            "winner_v32_training": v32["repository_attribution"],
            "winner_v32_checkpoints": [
                {
                    "label": row["label"],
                    "completed_updates": row["completed_updates"],
                    "graph": row["graph"],
                }
                for row in v32["persistent_checkpoints"]
            ],
        },
        "source_results": {
            "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
            "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen CPU objective contract",
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
                "# Winner-v34 direct right-pitch prefix intervention preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Checkpoints / configurations / plants / arms: `2 / 15 / 2 / 2`",
                "- Control / replacement cells: `60 / 60`",
                "- Duration: `250` ticks per cell; replacement only at ticks `0-7`",
                "- Optimizer / locomotion training / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "A pass requires all replacement cells to pass—not an average improvement—and",
                "can authorize only a separate CPU objective preregistration. It cannot select",
                "a checkpoint, implement a runtime wrapper, or clear the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
