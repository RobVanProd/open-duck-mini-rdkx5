#!/usr/bin/env python3
"""Freeze the read-only diagnostic for the completed Winner-v12 HOLD."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v12_calibrator_hold_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC_PREREGISTRATION_20260721.md"
FORMAL_RESULT = ANALYSIS / "winner_v12_calibrator_support_gate_result.json"
FORMAL_LAUNCH = ANALYSIS / "winner_v12_calibrator_support_gate_launch.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
EXPECTED_FAILED_CONFIGURATION_IDS = [
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "COM_X_NEG",
    "DISCOVERY_03",
    "HELDOUT_04",
    "HELDOUT_09",
]
STATIC_SOURCES = {
    "builder": Path(
        "tools/build_winner_v12_calibrator_hold_diagnostic_preregistration.py"
    ),
    "diagnostic_runner": Path(
        "tools/run_winner_v12_calibrator_hold_diagnostic.py"
    ),
    "diagnostic_tests": Path(
        "tests/test_winner_v12_calibrator_hold_diagnostic.py"
    ),
    "diagnostic_workflow": Path(
        ".github/workflows/winner-v12-calibrator-hold-diagnostic.yml"
    ),
    "formal_support_result": Path(
        "outputs/analysis/winner_v12_calibrator_support_gate_result.json"
    ),
    "formal_support_runner": Path(
        "tools/run_winner_v12_calibrator_support_gate.py"
    ),
    "formal_support_launch": Path(
        "outputs/analysis/winner_v12_calibrator_support_gate_launch.json"
    ),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "applied_target_observation_patch": Path(
        "patches/ground_up_applied_target_observation.patch"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def failed_configuration_ids(result: Mapping[str, Any]) -> list[str]:
    return sorted(
        {
            cell["configuration_id"]
            for checkpoint in result["checkpoint_results"]
            for cell in checkpoint["core_model_plant_cells"]
            if cell["support_pass"] is False
        }
    )


def source_manifest() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in STATIC_SOURCES.items()
    }


def validate_formal_hold(result: Mapping[str, Any]) -> None:
    if (
        result.get("schema_version")
        != "winner_v12.calibrator_support_gate_result.v1"
        or result.get("status") != "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        or result.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or result.get("checks", {}).get("all_248_main_cells_pass") is not False
        or result.get("execution")
        != {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or failed_configuration_ids(result) != EXPECTED_FAILED_CONFIGURATION_IDS
    ):
        raise ValueError("formal Winner-v12 HOLD evidence changed")
    counts = {
        checkpoint["label"]: sum(
            not cell["support_pass"]
            for cell in checkpoint["core_model_plant_cells"]
        )
        for checkpoint in result["checkpoint_results"]
    }
    if counts != {"half": 16, "final": 14}:
        raise ValueError("formal Winner-v12 failure counts changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite HOLD diagnostic: {path}")

    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    validate_formal_hold(formal)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    heldout_ids = [
        row["id"] for row in domain["evaluation_matrix"]["heldout_samples"]
    ]
    if heldout_ids != [f"HELDOUT_{index:02d}" for index in range(16)]:
        raise ValueError("Winner-v12 heldout population changed")
    graph_ids = list(
        dict.fromkeys([*EXPECTED_FAILED_CONFIGURATION_IDS, *heldout_ids])
    )
    launch = json.loads(FORMAL_LAUNCH.read_text(encoding="utf-8"))
    if (
        launch.get("status")
        != "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE_LAUNCH_FROZEN"
        or set(launch.get("verified_checkpoints", {})) != {"half", "final"}
    ):
        raise ValueError("formal Winner-v12 launch evidence changed")
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v12.calibrator_hold_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_OFFLINE_HOLD_DIAGNOSTIC",
        "question": (
            "Does the constant-contact normalization dominate the frozen predictor "
            "failure, and do the graph's calibration actions cause the formal "
            "support failures relative to an otherwise identical zero-action hold?"
        ),
        "frozen_population": {
            "checkpoint_labels": ["half", "final"],
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "duration_ticks": 250,
            "failed_configuration_ids": EXPECTED_FAILED_CONFIGURATION_IDS,
            "heldout_configuration_ids": heldout_ids,
            "graph_configuration_ids": graph_ids,
            "graph_cells": len(graph_ids) * 2 * 2,
            "zero_action_cells": len(EXPECTED_FAILED_CONFIGURATION_IDS) * 2 * 2,
        },
        "predictor_diagnostic": {
            "auxiliary_observation_indices": (
                list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99))
            ),
            "groups": {
                "imu": {"auxiliary": [0, 6], "observation": [0, 6]},
                "joint_position": {"auxiliary": [6, 20], "observation": [13, 27]},
                "joint_velocity": {"auxiliary": [20, 34], "observation": [27, 41]},
                "applied_target": {"auxiliary": [34, 48], "observation": [83, 97]},
                "foot_contact": {"auxiliary": [48, 50], "observation": [97, 99]},
            },
            "adjacent_state_rule": (
                "Pair each retained prediction except the last with the next retained "
                "observation. This loses only the unavailable final target in a "
                "full-duration cell and loses no valid transition in a failed cell."
            ),
            "report": (
                "Per-dimension learned and constant normalized MSE over all 16 heldout "
                "configurations, separately by checkpoint and plant."
            ),
            "contact_floor_dominance_rule": (
                "Both contact targets remain exactly 1, both stored standard "
                "deviations equal float32(1e-6), and contact dimensions contribute "
                "at least 99% of learned normalized SSE in every checkpoint/plant aggregate."
            ),
            "noncontact_counterfactual": (
                "Report whether the learned 48-D noncontact normalized MSE is strictly "
                "below the identical constant baseline; this is diagnostic only and "
                "does not revise the completed 50-D formal gate."
            ),
        },
        "support_diagnostic": {
            "graph_arm": (
                "Rerun the frozen ONNX graph on the union of all failed and heldout "
                "configurations and require support outcome, terminal tick, and valid "
                "tick count to match the imported formal result."
            ),
            "zero_action_arm": (
                "On each of the eight failed configurations, retain the graph's hidden "
                "state transition but replace calibration_actions and previous_action_out "
                "with exact zeros before the same bridge, observer, and physics step."
            ),
            "classification": [
                "graph_fail_zero_pass: calibrator action is causal for that support failure",
                "graph_fail_zero_fail: the stressed home configuration also fails without calibration action",
                "graph_pass_zero_pass: both arms remain supported",
                "graph_pass_zero_fail: the calibrator stabilizes that cell",
            ],
            "no_tuning_or_selection": True,
        },
        "interpretation_rules": {
            "contact_objective_defect": (
                "The contact floor dominates every predictor aggregate under the "
                "predeclared 99% rule."
            ),
            "calibrator_action_instability": (
                "All 30 formal failed checkpoint/configuration/plant pairs pass in the "
                "zero-action arm."
            ),
            "mixed_support_cause": (
                "At least one formal failed pair also fails in the zero-action arm."
            ),
            "result_authorizes_only": (
                "A separate prospective automatic-calibration mechanism preregistration; "
                "never training, checkpoint selection, deployment, Gate 5, or robot access."
            ),
        },
        "training_artifact": launch["training_artifact"],
        "verified_checkpoints": launch["verified_checkpoints"],
        "execution_now": {
            "diagnostic_cells": 0,
            "training_steps": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one offline read-only causal diagnostic and a later separately reviewed preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator HOLD diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Graph cells: `{payload['frozen_population']['graph_cells']}`",
                f"- Zero-action cells: `{payload['frozen_population']['zero_action_cells']}`",
                "- Training / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This audit does not reopen or revise the completed formal gate. It",
                "separates the two observed failure mechanisms before any replacement",
                "calibrator is designed. No closest-checkpoint selection is permitted.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
