#!/usr/bin/env python3
"""Freeze one Winner-v28 prefix joint-group causal screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN_PREREGISTRATION_20260722.md"
V27_RESULT = ANALYSIS / "winner_v27_early_prefix_recovery_scan_result.json"
V27_PREREG = ANALYSIS / "winner_v27_early_prefix_recovery_scan_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v28_prefix_joint_group_causal_screen_preregistration.py"),
    "runner": Path("tools/run_winner_v28_prefix_joint_group_causal_screen.py"),
    "runner_tests": Path("tests/test_winner_v28_prefix_joint_group_causal_screen.py"),
    "preregistration_tests": Path("tests/test_winner_v28_prefix_joint_group_causal_screen_preregistration.py"),
    "result_importer": Path("tools/import_winner_v28_prefix_joint_group_causal_screen.py"),
    "result_importer_tests": Path("tests/test_winner_v28_prefix_joint_group_causal_screen_import.py"),
    "workflow": Path(".github/workflows/winner-v28-prefix-joint-group-causal-screen.yml"),
    "winner_v27_preregistration": Path("outputs/analysis/winner_v27_early_prefix_recovery_scan_preregistration.json"),
    "winner_v27_result": Path("outputs/analysis/winner_v27_early_prefix_recovery_scan_result.json"),
    "winner_v27_runner": Path("tools/run_winner_v27_early_prefix_recovery_scan.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v24_support_result": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}
CONFIGURATION_IDS = [
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "DISCOVERY_03", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_09",
]
GROUPS = {
    "LEFT_LATERAL": [0, 1],
    "LEFT_PITCH_CHAIN": [2, 3, 4],
    "HEAD": [5, 6, 7, 8],
    "RIGHT_LATERAL": [9, 10],
    "RIGHT_PITCH_CHAIN": [11, 12, 13],
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
        raise FileExistsError("refusing to overwrite Winner-v28 preregistration")
    v27 = json.loads(V27_RESULT.read_text(encoding="utf-8"))
    v27_prereg = json.loads(V27_PREREG.read_text(encoding="utf-8"))
    if (
        v27.get("status") != "PASS_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        or v27.get("classification") != "EARLY_PREFIX_PHYSICAL_STATE_LOCK_IN"
        or v27.get("decision")
        != "AUTHORIZE_PREFIX_JOINT_GROUP_ACTION_CAUSAL_SCREEN_PREREGISTRATION_ONLY"
        or v27.get("execution")
        != {
            "candidate_prefixes": 40,
            "forks": 240,
            "branch_rollouts": 720,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v27 did not authorize Winner-v28 preregistration")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v28.prefix_joint_group_causal_screen_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_JOINT_GROUP_SCREEN_ONLY",
        "question": (
            "Does replacing exactly one anatomical action group with Winner-v22's action "
            "during ticks 0-7 prevent the tick-8 physical-state lock-in?"
        ),
        "diagnostic": {
            "source_checkpoint": {"label": "winner_v22_final", "update": 100},
            "candidate_checkpoints": [
                {"label": "half", "update": 150},
                {"label": "final", "update": 200},
            ],
            "configuration_ids": CONFIGURATION_IDS,
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "repair_ticks": 8,
            "absolute_end_tick": 52,
            "arms": {"CONTROL": [], **GROUPS},
            "repair_semantics": (
                "for ticks 0-7 only, replace the named candidate action indices with the "
                "Winner-v22 source action computed on the same branch observation and realized "
                "previous action; preserve all other candidate indices"
            ),
            "recovery_semantics": (
                "after tick 8, run Winner-v22 with its shadow hidden state from the repaired "
                "history and score survival against the unchanged candidate support terminal"
            ),
            "minimum_recovery_gain": 0.25,
            "action_delta_epsilon": 1.0e-6,
            "control_replay_pose_atol_rad": 1.0e-12,
            "expected_prefix_arms": 240,
            "expected_source_recovery_rollouts": 480,
            "selection_rule": (
                "select exactly one group only if its recovery-fraction gain is at least 0.25 "
                "for both checkpoints and its minimum checkpoint gain is strictly greater "
                "than every other group"
            ),
        },
        "decision_tree": {
            "single_group_selected": (
                "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "no_single_group": (
                "AUTHORIZE_PREFIX_GROUP_INTERACTION_DIAGNOSTIC_PREREGISTRATION_ONLY"
            ),
            "invalid": "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        },
        "execution_now": {
            "prefix_arms": 0,
            "source_recovery_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v27_prereg["artifact_inputs"],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen CPU diagnostic contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v28 prefix joint-group causal screen preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Arms: `CONTROL + 5 anatomical groups`",
                "- Prefix arms / recovery rollouts: `240 / 480`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "The result can select only a later CPU objective contract. It cannot",
                "authorize training, checkpoint selection, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
