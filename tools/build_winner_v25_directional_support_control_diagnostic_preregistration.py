#!/usr/bin/env python3
"""Freeze one zero-update same-state directional support-control diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v25_directional_support_control_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_20260722.md"
ATTRIBUTION = ANALYSIS / "winner_v24_support_regression_attribution.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v25_directional_support_control_diagnostic_preregistration.py"),
    "runner": Path("tools/run_winner_v25_directional_support_control_diagnostic.py"),
    "runner_tests": Path("tests/test_winner_v25_directional_support_control_diagnostic.py"),
    "preregistration_tests": Path("tests/test_winner_v25_directional_support_control_diagnostic_preregistration.py"),
    "result_importer": Path("tools/import_winner_v25_directional_support_control_diagnostic.py"),
    "result_importer_tests": Path("tests/test_winner_v25_directional_support_control_diagnostic_import.py"),
    "workflow": Path(".github/workflows/winner-v25-directional-support-control-diagnostic.yml"),
    "support_regression_attribution": Path("outputs/analysis/winner_v24_support_regression_attribution.json"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v24_support_result": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "v22_gate_runner": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v24_gate_runner": Path("tools/run_winner_v24_baseline_anchored_support_gate.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v25 preregistration")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    if (
        attribution.get("status")
        != "PASS_WINNER_V24_SUPPORT_REGRESSION_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or attribution.get("failed_checks") != []
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v25 source evidence does not authorize preregistration")
    v22_attribution = v22.get("repository_attribution", {})
    v24_attribution = v24.get("repository_attribution", {})
    for label, value in (("Winner-v22", v22_attribution), ("Winner-v24", v24_attribution)):
        if (
            value.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
            or value.get("github_run_attempt") != 1
            or value.get("github_run_id", 0) <= 0
            or value.get("github_artifact_id", 0) <= 0
        ):
            raise ValueError(f"{label} training attribution changed")
    source_snapshot = v22["snapshot_manifest"][99]
    source_checkpoint = next(
        row for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    v24_snapshots = {row["completed_updates"]: row for row in v24["snapshot_manifest"]}
    v24_checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    diagnostic = {
        "source_checkpoint": {"label": "winner_v22_final", "update": 100},
        "candidate_checkpoints": [
            {"label": "half", "update": 150},
            {"label": "final", "update": 200},
        ],
        "configuration_ids": CONFIGURATION_IDS,
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "base_prefix_ticks": 20,
        "fork_horizon_ticks": 5,
        "same_policy_input": ["observation", "previous_action", "h_in"],
        "fork_action_hold": "hold the tick-t source or candidate action for all five fork ticks",
        "pitch_score": "abs(candidate_end_pitch)-abs(source_end_pitch)",
        "pitch_delta_epsilon_rad": 1.0e-6,
        "action_delta_epsilon": 1.0e-6,
        "destabilizing_fraction_threshold": 0.75,
        "expected_base_trajectories": 20,
        "expected_fork_points": 800,
        "expected_short_horizon_rollouts": 1600,
        "branch_rule": (
            "classify local destabilization only if both candidate checkpoints have "
            "destabilizing_fraction>=0.75 and median_abs_pitch_delta_rad>1e-6; otherwise "
            "classify no dominant local destabilization"
        ),
    }
    payload = {
        "schema_version": "winner_v25.directional_support_control_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_SAME_STATE_DIRECTIONAL_DIAGNOSTIC_ONLY",
        "causal_question": (
            "Did the failed symmetric terminal objective change the actor's action on an "
            "identical policy input in a direction that increases five-tick absolute torso "
            "pitch from the same cloned physical state?"
        ),
        "diagnostic": diagnostic,
        "artifact_inputs": {
            "winner_v22_training": {
                "repository_attribution": v22_attribution,
                "source_snapshot": source_snapshot,
                "source_graph": source_checkpoint["graph"],
            },
            "winner_v24_training": {
                "repository_attribution": v24_attribution,
                "half": {
                    "snapshot": v24_snapshots[150],
                    "graph": v24_checkpoints["half"]["graph"],
                },
                "final": {
                    "snapshot": v24_snapshots[200],
                    "graph": v24_checkpoints["final"]["graph"],
                },
            },
        },
        "decision_tree": {
            "same_state_action_change_locally_destabilizing": (
                "authorize only a separate directional-counterfactual-objective CPU contract"
            ),
            "no_dominant_same_state_local_destabilization": (
                "authorize only a separate longer-horizon recurrent-credit diagnostic preregistration"
            ),
            "invalid_or_failed_contract": "do not select a next policy mechanism",
            "closest_result_selection": False,
        },
        "execution_now": {
            "base_trajectories": 0,
            "fork_points": 0,
            "short_horizon_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
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
                "# Winner-v25 directional support-control diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Policies: Winner-v22 final source versus Winner-v24 half/final",
                "- Population: `10` negative-X configurations x `2` plants",
                "- Same-state forks: `800`; five-tick rollouts: `1,600`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                payload["causal_question"],
                "",
                "The result chooses only between two later CPU evidence contracts. It cannot",
                "authorize training, checkpoint selection, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
