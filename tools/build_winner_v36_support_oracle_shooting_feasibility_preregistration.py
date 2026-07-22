#!/usr/bin/env python3
"""Freeze one Winner-v36 COM_X_NEG support-oracle shooting screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md"
V35_RESULT = ANALYSIS / "winner_v35_full_horizon_source_continuation_result.json"

SOURCES = {
    "builder": Path("tools/build_winner_v36_support_oracle_shooting_feasibility_preregistration.py"),
    "runner": Path("tools/run_winner_v36_support_oracle_shooting_feasibility.py"),
    "runner_tests": Path("tests/test_winner_v36_support_oracle_shooting_feasibility.py"),
    "preregistration_tests": Path("tests/test_winner_v36_support_oracle_shooting_feasibility_preregistration.py"),
    "result_importer": Path("tools/import_winner_v36_support_oracle_shooting_feasibility.py"),
    "result_importer_tests": Path("tests/test_winner_v36_support_oracle_shooting_feasibility_import.py"),
    "workflow": Path(".github/workflows/winner-v36-support-oracle-shooting-feasibility.yml"),
    "winner_v35_result": Path("outputs/analysis/winner_v35_full_horizon_source_continuation_result.json"),
    "winner_v35_runner": Path("tools/run_winner_v35_full_horizon_source_continuation.py"),
    "prior_oracle_shooting_probe": Path("tools/probe_ground_up_oracle_shooting_mpc.py"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v36 preregistration")
    v35 = json.loads(V35_RESULT.read_text(encoding="utf-8"))
    if (
        v35.get("status") != "HOLD_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        or v35.get("classification") != "HYBRID_TEACHER_NOT_FULL_HORIZON_FEASIBLE"
        or v35.get("decision") != "CLOSE_V28_HYBRID_TEACHER_ROUTE"
        or v35.get("execution", {}).get("optimizer_updates") != 0
        or v35.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v35 does not support a new control-feasibility screen")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v36.support_oracle_shooting_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_COM_X_NEG_SHOOTING_SCREEN",
        "question": (
            "Can a deterministic receding-horizon oracle keep the canonical -0.05 m "
            "torso-X anchor support-valid for all 250 ticks under the exact graph action "
            "bounds and both measured actuator plants?"
        ),
        "screen": {
            "configuration_ids": ["COM_X_NEG"],
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "controlled_action_indices": [2, 3, 4, 11, 12, 13],
            "duration_ticks": 250,
            "horizon_ticks": 8,
            "action_block_ticks": 2,
            "population": 64,
            "elites": 8,
            "iterations": 4,
            "initial_std": 0.20,
            "minimum_std": 0.03,
            "root_seed": 120120,
            "expected_cells": 2,
            "parameter_provenance": (
                "Reuse the prior reviewed oracle-shooting population/elites/iterations/"
                "horizon/block/std values without a search. Restrict control to the six "
                "pitch-chain indices selected by prior causal evidence."
            ),
            "objective": (
                "lexicographic(survival_ticks,-maximum_abs_tilt,+minimum_base_z,"
                "-final_abs_tilt,-final_gyro,-action_delta_energy,-action_energy)"
            ),
            "constraints": (
                "Every candidate and selected action passes through the exact stateful graph "
                "absolute/rate boundary and the unchanged P30 or P31/34 actuator bridge."
            ),
        },
        "pass_rule": {
            "both_plants_pass_full_250_tick_support_gate": True,
            "all_selected_actions_graph_bounded": True,
            "all_cells_use_nonzero_control": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "The anchor is controllable by this bounded oracle; authorize only a separate "
                "30-cell full-configuration feasibility preregistration."
            ),
            "hold": (
                "This exact shooting controller is not a teacher. A hold does not prove the "
                "physical system uncontrollable and does not authorize parameter tuning."
            ),
        },
        "execution_now": {
            "oracle_support_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v35_result_lf_sha256": lf_sha256(V35_RESULT),
            "repository_attribution": v35["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen full-configuration CPU oracle feasibility screen",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v36 support-oracle shooting feasibility preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`",
            "- CEM population / elites / iterations: `64 / 8 / 4`",
            "- Horizon / block: `8 / 2` ticks",
            "- Controlled joints: six bilateral pitch-chain actions",
            "- Optimizer updates / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This is a simulator-oracle controllability screen, not a deployable controller.",
            "A pass can only authorize the full configuration matrix; a hold cannot be tuned.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
