#!/usr/bin/env python3
"""Freeze one Winner-v38 mirrored-pitch COM_X_NEG shooting screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v38_mirrored_pitch_shooting_feasibility_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY_PREREGISTRATION_20260722.md"
V36_RESULT = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_result.json"
V37_RESULT = ANALYSIS / "winner_v37_warm_started_shooting_feasibility_result.json"

SOURCES = {
    "builder": Path("tools/build_winner_v38_mirrored_pitch_shooting_feasibility_preregistration.py"),
    "runner": Path("tools/run_winner_v38_mirrored_pitch_shooting_feasibility.py"),
    "runner_tests": Path("tests/test_winner_v38_mirrored_pitch_shooting_feasibility.py"),
    "preregistration_tests": Path("tests/test_winner_v38_mirrored_pitch_shooting_feasibility_preregistration.py"),
    "result_importer": Path("tools/import_winner_v38_mirrored_pitch_shooting_feasibility.py"),
    "result_importer_tests": Path("tests/test_winner_v38_mirrored_pitch_shooting_feasibility_import.py"),
    "workflow": Path(".github/workflows/winner-v38-mirrored-pitch-shooting-feasibility.yml"),
    "winner_v36_result": Path("outputs/analysis/winner_v36_support_oracle_shooting_feasibility_result.json"),
    "winner_v36_runner": Path("tools/run_winner_v36_support_oracle_shooting_feasibility.py"),
    "winner_v37_result": Path("outputs/analysis/winner_v37_warm_started_shooting_feasibility_result.json"),
    "reviewed_mirror_basis": Path("patches/winner_v16_support_action_direction.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v38 preregistration")
    v36 = json.loads(V36_RESULT.read_text(encoding="utf-8"))
    v37 = json.loads(V37_RESULT.read_text(encoding="utf-8"))
    if (
        v36.get("status") != "HOLD_WINNER_V36_SUPPORT_ORACLE_SHOOTING_FEASIBILITY"
        or v36.get("summary", {}).get("terminal_ticks") != [55, 52]
        or v37.get("status") != "HOLD_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        or v37.get("classification") != "STATEFUL_PROPOSAL_NOT_FULL_HORIZON_FEASIBLE"
        or v37.get("decision") != "CLOSE_WARM_STARTED_SHOOTING_PROPOSAL_MECHANISM"
        or v37.get("summary", {}).get("terminal_ticks") != [46, 37]
        or v37.get("checks", {}).get("all_first_actions_match_v36") is not True
        or v37.get("execution", {}).get("optimizer_updates") != 0
        or v37.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v36/v37 do not support the mirrored-basis screen")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    mirror_basis = {
        "hip_pitch_magnitude": {"left_index_2": -1, "right_index_11": 1},
        "knee": {"left_index_3": 1, "right_index_12": 1},
        "ankle": {"left_index_4": 1, "right_index_13": 1},
    }
    value = {
        "schema_version": "winner_v38.mirrored_pitch_shooting_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_MIRRORED_PITCH_COM_X_NEG_SCREEN",
        "question": (
            "Can the unchanged cold-start bounded shooting controller hold the symmetric "
            "COM_X_NEG anchor when its six pitch-joint search is expressed in the reviewed "
            "three-dimensional bilateral mirror basis?"
        ),
        "evidence_basis": {
            "v36_terminal_ticks": [55, 52],
            "v37_terminal_ticks": [46, 37],
            "v37_terminal_roll_rad": [-0.07165295763618688, -0.15592441412373131],
            "source_mechanism": (
                "Independent left/right proposal memory worsened survival and introduced "
                "material roll under a symmetric fore-aft COM perturbation."
            ),
            "one_factor_change_from_v36": (
                "sample three mirrored pitch coordinates instead of six independent ones"
            ),
        },
        "screen": {
            "configuration_ids": ["COM_X_NEG"],
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "controlled_action_indices": [2, 3, 4, 11, 12, 13],
            "search_dimensions_per_block": 3,
            "mirror_basis": mirror_basis,
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
            "proposal_memory": "cold projected previous action on every tick",
            "objective": (
                "lexicographic(survival_ticks,-maximum_abs_tilt,+minimum_base_z,"
                "-final_abs_tilt,-final_gyro,-action_delta_energy,-action_energy)"
            ),
            "constraints": (
                "Every expanded candidate and selected action passes through the exact "
                "stateful graph absolute/rate boundary and unchanged actuator bridge."
            ),
        },
        "pass_rule": {
            "both_plants_pass_full_250_tick_support_gate": True,
            "all_plans_use_exact_3d_mirrored_basis": True,
            "all_selected_actions_graph_bounded": True,
            "all_cells_use_nonzero_control": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "The mirrored pitch subspace is a full-horizon support teacher at the pure "
                "negative-X anchor; authorize only a separate negative-X teacher contract."
            ),
            "hold": (
                "Close this exact mirrored-pitch shooting mechanism. Do not tune its basis, "
                "horizon, population, objective, covariance, or add another action axis."
            ),
        },
        "execution_now": {
            "oracle_support_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_results": {
            "winner_v36_result_lf_sha256": lf_sha256(V36_RESULT),
            "winner_v37_result_lf_sha256": lf_sha256(V37_RESULT),
            "winner_v37_repository_attribution": v37["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen negative-X mirrored teacher contract"
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
            "# Winner-v38 mirrored-pitch shooting feasibility preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`",
            "- Search: `3` mirrored coordinates expanded to the same `6` pitch joints",
            "- Frozen CEM population / elites / iterations: `64 / 8 / 4`",
            "- Frozen horizon / block: `8 / 2` ticks",
            "- Proposal: V36 cold start; no V37 plan memory",
            "- Optimizer updates / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This is a simulator-oracle subspace falsification, not a deployable controller.",
            "A pass can authorize only a negative-X teacher contract; a hold closes this route.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
