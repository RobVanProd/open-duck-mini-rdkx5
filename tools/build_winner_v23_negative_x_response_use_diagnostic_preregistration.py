#!/usr/bin/env python3
"""Freeze one read-only Winner-v23 negative-X response-use diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v22_support_hold_attribution.json"
TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PAIR_IDS = [
    ["COM_X_NEG", "COM_X_POS"],
    ["COM_CORNER_00", "COM_CORNER_04"],
    ["COM_CORNER_01", "COM_CORNER_05"],
    ["COM_CORNER_02", "COM_CORNER_06"],
    ["COM_CORNER_03", "COM_CORNER_07"],
]
SOURCES = {
    "builder": Path("tools/build_winner_v23_negative_x_response_use_diagnostic_preregistration.py"),
    "runner": Path("tools/run_winner_v23_negative_x_response_use_diagnostic.py"),
    "runner_tests": Path("tests/test_winner_v23_negative_x_response_use_diagnostic.py"),
    "preregistration_tests": Path("tests/test_winner_v23_negative_x_response_use_diagnostic_preregistration.py"),
    "importer": Path("tools/import_winner_v23_negative_x_response_use_diagnostic.py"),
    "importer_tests": Path("tests/test_winner_v23_negative_x_response_use_diagnostic_import.py"),
    "workflow": Path(".github/workflows/winner-v23-negative-x-response-use-diagnostic.yml"),
    "support_hold_attribution": Path("outputs/analysis/winner_v22_support_hold_attribution.json"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v22_support_result": Path("outputs/analysis/winner_v22_normalized_predictor_support_gate_result.json"),
    "winner_v22_training_importer": Path("tools/import_winner_v22_normalized_predictor_training.py"),
    "winner_v22_gate_runner": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def exact_pairs(domain: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = domain["evaluation_matrix"]
    rows = [
        *matrix["fixed_anchors"],
        *matrix["discovery_samples"],
        *matrix["heldout_samples"],
    ]
    lookup = {row["id"]: row for row in rows}
    result = []
    for negative_id, positive_id in PAIR_IDS:
        negative = lookup[negative_id]
        positive = lookup[positive_id]
        neg_com = negative["torso_com_offset_m"]
        pos_com = positive["torso_com_offset_m"]
        left = {key: value for key, value in negative.items() if key not in {"id", "torso_com_offset_m"}}
        right = {key: value for key, value in positive.items() if key not in {"id", "torso_com_offset_m"}}
        if (
            float(neg_com[0]) >= 0.0
            or float(pos_com[0]) <= 0.0
            or neg_com[1:] != pos_com[1:]
            or abs(float(neg_com[0]) + float(pos_com[0])) > 1.0e-12
            or left != right
        ):
            raise ValueError(f"not an exact X-sign pair: {negative_id}/{positive_id}")
        result.append(
            {
                "negative_id": negative_id,
                "positive_id": positive_id,
                "negative_configuration_sha256": canonical_sha256(negative),
                "positive_configuration_sha256": canonical_sha256(positive),
                "negative_torso_com_offset_m": neg_com,
                "positive_torso_com_offset_m": pos_com,
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v23 preregistration")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    training = json.loads(TRAINING.read_text(encoding="utf-8"))
    if (
        attribution.get("status") != "PASS_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_ONLY"
        or attribution.get("failed_checks") != []
        or training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v23 source evidence changed")
    pair_receipts = exact_pairs(json.loads(DOMAIN.read_text(encoding="utf-8")))
    checkpoints = training["persistent_checkpoints"]
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v23.negative_x_response_use_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_20_PAIR_CELL_DIAGNOSTIC_ONLY",
        "causal_question": (
            "Before the negative-X support boundary is crossed, does Winner-v22 encode the "
            "X-sign-dependent response early enough, and does changing only recurrent state "
            "change the action materially under an identical observation and previous action?"
        ),
        "training_artifact": {
            "repository_attribution": training["repository_attribution"],
            "half": {
                "snapshot": training["snapshot_manifest"][49],
                "graph": checkpoints[0]["graph"],
            },
            "final": {
                "snapshot": training["snapshot_manifest"][99],
                "graph": checkpoints[1]["graph"],
            },
        },
        "diagnostic": {
            "configuration_pairs": PAIR_IDS,
            "pair_receipts": pair_receipts,
            "checkpoint_labels": ["half", "final"],
            "actuator_plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "paired_cells": 20,
            "physics_rollouts": 40,
            "full_rollout_ticks": 250,
            "early_analysis_ticks": 25,
            "early_window_basis": (
                "the earliest frozen Winner-v22 negative-X failure is tick 27; ticks 0..24 "
                "leave a two-tick margin before every observed boundary crossing"
            ),
            "minimum_persistent_ticks": 5,
            "hidden_linf_threshold": 1.0e-7,
            "hidden_threshold_basis": "unchanged reviewed context-separation tolerance",
            "same_input_hidden_fork_action_linf_threshold": 1.0e-5,
            "fork_threshold_basis": "100x the unchanged 1e-7 JAX/ONNX agreement tolerance",
            "minimum_cells_for_branch": 16,
            "minimum_cells_basis": "80% of the exact 20 paired checkpoint/plant cells",
            "same_input_fork": (
                "use one negative-X observation and previous action twice, changing only h_in "
                "between the matched negative-X and positive-X recorded recurrent states; "
                "do not feed either fork back into physics"
            ),
        },
        "decision_tree": [
            {
                "when": "encoded>=16 and early_predictor_beats_constant>=16 and action_used>=16",
                "classification": "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE",
                "decision": "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY",
            },
            {
                "when": "encoded>=16 and early_predictor_beats_constant>=16 and action_used<16",
                "classification": "RESPONSE_STATE_PRESENT_ACTION_COUPLING_DEFICIT",
                "decision": "AUTHORIZE_RESPONSE_ACTION_COUPLING_CPU_CONTRACT_ONLY",
            },
            {
                "when": "otherwise",
                "classification": "EARLY_RESPONSE_INFERENCE_DEFICIT",
                "decision": "AUTHORIZE_EARLY_RESPONSE_INFERENCE_CPU_CONTRACT_ONLY",
            },
        ],
        "required_execution_checks": [
            "exactly 20 paired cells and 40 unchanged-physics rollouts",
            "all paired cells expose the frozen 25-tick early window",
            "all positive-X sign controls pass the unchanged support gate",
            "at least 16 negative-X cells reproduce the existing support failure",
            "all metrics are finite",
            "zero optimizer updates, locomotion steps, and robot/RDK access",
        ],
        "execution_now": {
            "paired_cells": 0,
            "physics_rollouts": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "manual_mass_com_inertia_measurements_required": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the one CPU contract selected by the frozen decision tree",
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
                "# Winner-v23 negative-X response-use diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Exact X-sign pairs / paired cells / physics rollouts: `5 / 20 / 40`",
                "- Checkpoints / actuator plants: `2 / 2`",
                "- Early window: ticks `0..24`, before the earliest tick-27 failure",
                "- Same-input fork changes only `h_in`; it is never applied to physics",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "- Manual mass/COM measurements: `not required`",
                "",
                "This diagnostic chooses among three predeclared CPU-contract branches.",
                "It cannot train, select a deployment checkpoint, weaken support gates,",
                "access the RDK, or clear a policy for the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
