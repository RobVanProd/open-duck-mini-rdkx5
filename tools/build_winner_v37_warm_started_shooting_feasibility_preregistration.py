#!/usr/bin/env python3
"""Freeze one Winner-v37 warm-started COM_X_NEG shooting screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v37_warm_started_shooting_feasibility_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md"
V36_RESULT = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_result.json"

SOURCES = {
    "builder": Path("tools/build_winner_v37_warm_started_shooting_feasibility_preregistration.py"),
    "runner": Path("tools/run_winner_v37_warm_started_shooting_feasibility.py"),
    "runner_tests": Path("tests/test_winner_v37_warm_started_shooting_feasibility.py"),
    "preregistration_tests": Path("tests/test_winner_v37_warm_started_shooting_feasibility_preregistration.py"),
    "result_importer": Path("tools/import_winner_v37_warm_started_shooting_feasibility.py"),
    "result_importer_tests": Path("tests/test_winner_v37_warm_started_shooting_feasibility_import.py"),
    "workflow": Path(".github/workflows/winner-v37-warm-started-shooting-feasibility.yml"),
    "winner_v36_result": Path("outputs/analysis/winner_v36_support_oracle_shooting_feasibility_result.json"),
    "winner_v36_runner": Path("tools/run_winner_v36_support_oracle_shooting_feasibility.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v37 preregistration")
    v36 = json.loads(V36_RESULT.read_text(encoding="utf-8"))
    if (
        v36.get("status") != "HOLD_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        or v36.get("classification") != "THIS_SHOOTING_CONTROLLER_NOT_FULL_HORIZON_FEASIBLE"
        or v36.get("decision") != "DO_NOT_USE_V36_SHOOTING_CONTROLLER_AS_TEACHER"
        or v36.get("summary", {}).get("support_passes") != 0
        or v36.get("summary", {}).get("terminal_ticks") != [55, 52]
        or v36.get("execution", {}).get("optimizer_updates") != 0
        or v36.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v36 does not support the warm-start falsification")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    proposal_memory = {
        "first_tick": "exact Winner-v36 cold mean",
        "later_ticks": (
            "shift prior winning raw eight-tick plan left by one tick, repeat its "
            "terminal action, then average adjacent pairs into four two-tick blocks"
        ),
        "covariance": "reset every tick to the unchanged 0.20 initial standard deviation",
    }
    value = {
        "schema_version": "winner_v37.warm_started_shooting_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_WARM_STARTED_COM_X_NEG_SCREEN",
        "question": (
            "Does preserving the prior winning plan as the next CEM proposal mean repair "
            "V36's cold-start planning discontinuity without changing its controller "
            "authority, compute, objective, horizon, action set, or physical gate?"
        ),
        "evidence_basis": {
            "v36_support_passes": 0,
            "v36_terminal_ticks": [55, 52],
            "v36_failure_check": "roll_pitch only",
            "source_mechanism": (
                "V36 resets its CEM mean to the single previous action on every tick, "
                "discarding the remainder of the just-selected eight-tick plan."
            ),
            "one_factor_change": "proposal mean carries the shifted prior winning plan",
        },
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
            "proposal_memory": proposal_memory,
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
            "all_first_actions_match_v36": True,
            "all_later_ticks_use_warm_start": True,
            "all_cells_exercise_nontrivial_warm_mean": True,
            "all_selected_actions_graph_bounded": True,
            "all_cells_use_nonzero_control": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "Stateful proposal continuity is sufficient at the anchor; authorize only a "
                "separate 30-cell full-configuration warm-started feasibility preregistration."
            ),
            "hold": (
                "Close this exact stateful proposal mechanism. Do not tune V36/V37's horizon, "
                "population, pitch-joint set, objective, covariance, or warm-start transform."
            ),
        },
        "execution_now": {
            "oracle_support_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v36_result_lf_sha256": lf_sha256(V36_RESULT),
            "repository_attribution": v36["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen full-configuration CPU warm-started oracle screen"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v37 warm-started shooting feasibility preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`",
            "- V36 comparator terminal ticks: `55 / 52`",
            "- Frozen CEM population / elites / iterations: `64 / 8 / 4`",
            "- Frozen horizon / block / controlled joints: `8 / 2 / six pitch-chain`",
            "- One change: shift the previous winning plan into the next proposal mean",
            "- Optimizer updates / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This is a simulator-oracle mechanism falsification, not a deployable controller.",
            "A pass can authorize only a full configuration screen; a hold closes this route.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
