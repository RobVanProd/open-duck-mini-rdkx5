#!/usr/bin/env python3
"""Freeze one zero-update Winner-v27 early-prefix source-recovery scan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v27_early_prefix_recovery_scan_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN_PREREGISTRATION_20260722.md"
V26_RESULT = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_result.json"
V26_PREREG = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v27_early_prefix_recovery_scan_preregistration.py"),
    "runner": Path("tools/run_winner_v27_early_prefix_recovery_scan.py"),
    "runner_tests": Path("tests/test_winner_v27_early_prefix_recovery_scan.py"),
    "preregistration_tests": Path("tests/test_winner_v27_early_prefix_recovery_scan_preregistration.py"),
    "result_importer": Path("tools/import_winner_v27_early_prefix_recovery_scan.py"),
    "result_importer_tests": Path("tests/test_winner_v27_early_prefix_recovery_scan_import.py"),
    "workflow": Path(".github/workflows/winner-v27-early-prefix-recovery-scan.yml"),
    "winner_v26_preregistration": Path("outputs/analysis/winner_v26_recurrent_credit_diagnostic_preregistration.json"),
    "winner_v26_result": Path("outputs/analysis/winner_v26_recurrent_credit_diagnostic_result.json"),
    "winner_v26_runner": Path("tools/run_winner_v26_recurrent_credit_diagnostic.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v22_support_result": Path("outputs/analysis/winner_v22_normalized_predictor_support_gate_result.json"),
    "winner_v24_support_result": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}
CONFIGURATION_IDS = [
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "DISCOVERY_03",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_09",
]


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
        raise FileExistsError("refusing to overwrite Winner-v27 preregistration")
    v26 = json.loads(V26_RESULT.read_text(encoding="utf-8"))
    v26_prereg = json.loads(V26_PREREG.read_text(encoding="utf-8"))
    if (
        v26.get("status") != "PASS_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        or v26.get("classification")
        != "NO_DOMINANT_POST_PREFIX_RECURRENT_REGRESSION"
        or v26.get("decision")
        != "AUTHORIZE_EARLY_PREFIX_DIVERGENCE_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or v26.get("execution")
        != {
            "base_trajectories": 20,
            "candidate_branches": 40,
            "branch_rollouts": 80,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v26 did not authorize Winner-v27 preregistration")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v27.early_prefix_recovery_scan_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_EARLY_PREFIX_RECOVERY_SCAN_ONLY",
        "question": (
            "At what point in the first 20 Winner-v24 ticks does the candidate physical "
            "state stop being recoverable by Winner-v22's source controller?"
        ),
        "diagnostic": {
            "source_checkpoint": {"label": "winner_v22_final", "update": 100},
            "candidate_checkpoints": [
                {"label": "half", "update": 150},
                {"label": "final", "update": 200},
            ],
            "configuration_ids": CONFIGURATION_IDS,
            "actuator_plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "candidate_prefix_ticks": 20,
            "fork_ticks": [0, 4, 8, 12, 16, 20],
            "absolute_end_tick": 52,
            "source_shadow_state": (
                "source hidden state is advanced on the candidate observation and previous-"
                "action history while its action output is ignored"
            ),
            "fork_semantics": (
                "candidate continuation and source recovery start from the same candidate "
                "physical/bridge/observer/history snapshot and captured policy observation; "
                "each uses its own history-consistent recurrent hidden state"
            ),
            "recovery_definition": (
                "source recovery survives to absolute tick 52 or terminates strictly later "
                "than the exact candidate continuation"
            ),
            "tick0_required_recovery_fraction": 1.0,
            "tick20_max_recovery_fraction_for_lock_in": 0.25,
            "action_delta_epsilon": 1.0e-6,
            "expected_candidate_prefixes": 40,
            "expected_forks": 240,
            "expected_branch_rollouts": 720,
            "branch_rule": (
                "classify early physical-state lock-in only if both checkpoints have exact "
                "1.0 source-recovery fraction at tick 0 and at most 0.25 at tick 20"
            ),
        },
        "decision_tree": {
            "early_state_lock_in": (
                "AUTHORIZE_PREFIX_JOINT_GROUP_ACTION_CAUSAL_SCREEN_PREREGISTRATION_ONLY"
            ),
            "state_remains_source_recoverable": (
                "AUTHORIZE_STATE_CONTROLLER_CROSS_SWAP_DIAGNOSTIC_PREREGISTRATION_ONLY"
            ),
            "invalid": "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        },
        "execution_now": {
            "candidate_prefixes": 0,
            "forks": 0,
            "branch_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v26_prereg["artifact_inputs"],
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
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v27 early-prefix recovery scan preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Candidate prefixes / forks / branch rollouts: `40 / 240 / 720`",
                "- Fork ticks: `0, 4, 8, 12, 16, 20`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "The result can select only a later CPU causal contract. It cannot",
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
