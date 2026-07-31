#!/usr/bin/env python3
"""Freeze one zero-update post-prefix recurrent-credit diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_20260722.md"
V25_PREREG = ANALYSIS / "winner_v25_directional_support_control_diagnostic_preregistration.json"
V25_RESULT = ANALYSIS / "winner_v25_directional_support_control_diagnostic_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v26_recurrent_credit_diagnostic_preregistration.py"),
    "runner": Path("tools/run_winner_v26_recurrent_credit_diagnostic.py"),
    "runner_tests": Path("tests/test_winner_v26_recurrent_credit_diagnostic.py"),
    "preregistration_tests": Path("tests/test_winner_v26_recurrent_credit_diagnostic_preregistration.py"),
    "result_importer": Path("tools/import_winner_v26_recurrent_credit_diagnostic.py"),
    "result_importer_tests": Path("tests/test_winner_v26_recurrent_credit_diagnostic_import.py"),
    "workflow": Path(".github/workflows/winner-v26-recurrent-credit-diagnostic.yml"),
    "winner_v25_preregistration": Path("outputs/analysis/winner_v25_directional_support_control_diagnostic_preregistration.json"),
    "winner_v25_result": Path("outputs/analysis/winner_v25_directional_support_control_diagnostic_result.json"),
    "winner_v25_runner": Path("tools/run_winner_v25_directional_support_control_diagnostic.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "actuator_bridge": Path("tools/actuator_bridge_model.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v26 preregistration")
    v25_prereg = json.loads(V25_PREREG.read_text(encoding="utf-8"))
    v25_result = json.loads(V25_RESULT.read_text(encoding="utf-8"))
    if (
        v25_result.get("status")
        != "PASS_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
        or v25_result.get("classification")
        != "NO_DOMINANT_SAME_STATE_LOCAL_DESTABILIZATION"
        or v25_result.get("decision")
        != "AUTHORIZE_LONGER_HORIZON_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or v25_result.get("execution")
        != {
            "base_trajectories": 20,
            "fork_points": 800,
            "short_horizon_rollouts": 1600,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v25 did not authorize Winner-v26 preregistration")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v26.recurrent_credit_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_POST_PREFIX_RECURRENT_DIAGNOSTIC_ONLY",
        "question": (
            "When all branches begin from the exact Winner-v22 tick-20 physical and "
            "recurrent state, do both Winner-v24 checkpoints still terminate earlier "
            "over the complete remaining negative-X failure window?"
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
            "base_prefix_ticks": 20,
            "recurrent_horizon_ticks": 32,
            "shared_fork_inputs": [
                "physical_state",
                "observation",
                "previous_action",
                "h_in",
            ],
            "branch_semantics": (
                "the captured tick-20 policy observation is supplied identically at the first "
                "branch tick; source and candidate then evolve their own observation, previous-"
                "action, and recurrent hidden-state chains"
            ),
            "regression_definition": (
                "candidate terminates before source; a source surviving 32 branch ticks is "
                "right-censored at absolute tick 52"
            ),
            "regression_fraction_threshold": 0.75,
            "minimum_median_lead_ticks": 1.0,
            "action_delta_epsilon": 1.0e-6,
            "pitch_delta_epsilon_rad": 1.0e-6,
            "expected_base_trajectories": 20,
            "expected_candidate_branches": 40,
            "expected_branch_rollouts": 80,
            "branch_rule": (
                "classify post-prefix recurrent closed-loop regression only if both candidate "
                "checkpoints regress on at least 75 percent of branches and have median "
                "candidate failure lead of at least one tick"
            ),
        },
        "decision_tree": {
            "post_prefix_recurrent_regression": (
                "AUTHORIZE_RECURRENT_PARAMETER_BLOCK_SWAP_CPU_CONTRACT_PREREGISTRATION_ONLY"
            ),
            "no_dominant_post_prefix_regression": (
                "AUTHORIZE_EARLY_PREFIX_DIVERGENCE_DIAGNOSTIC_PREREGISTRATION_ONLY"
            ),
            "invalid": "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        },
        "execution_now": {
            "base_trajectories": 0,
            "candidate_branches": 0,
            "branch_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v25_prereg["artifact_inputs"],
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
                "# Winner-v26 recurrent-credit diagnostic preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Shared source prefix: `20` ticks",
                "- Recurrent fork horizon: `32` ticks",
                "- Base / candidate / rollout counts: `20 / 40 / 80`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "The result can select only a later CPU attribution contract. It cannot",
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
