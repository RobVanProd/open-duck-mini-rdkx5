#!/usr/bin/env python3
"""Freeze one Winner-v39 response-Jacobian COM_X_NEG screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v39_response_jacobian_feasibility_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY_PREREGISTRATION_20260722.md"
V38_RESULT = ANALYSIS / "winner_v38_mirrored_pitch_shooting_feasibility_result.json"

SOURCES = {
    "builder": Path("tools/build_winner_v39_response_jacobian_feasibility_preregistration.py"),
    "runner": Path("tools/run_winner_v39_response_jacobian_feasibility.py"),
    "runner_tests": Path("tests/test_winner_v39_response_jacobian_feasibility.py"),
    "preregistration_tests": Path("tests/test_winner_v39_response_jacobian_feasibility_preregistration.py"),
    "result_importer": Path("tools/import_winner_v39_response_jacobian_feasibility.py"),
    "result_importer_tests": Path("tests/test_winner_v39_response_jacobian_feasibility_import.py"),
    "workflow": Path(".github/workflows/winner-v39-response-jacobian-feasibility.yml"),
    "winner_v38_result": Path("outputs/analysis/winner_v38_mirrored_pitch_shooting_feasibility_result.json"),
    "winner_v38_runner": Path("tools/run_winner_v38_mirrored_pitch_shooting_feasibility.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v39 preregistration")
    v38 = json.loads(V38_RESULT.read_text(encoding="utf-8"))
    if (
        v38.get("status") != "HOLD_WINNER_V38_MIRRORED_PITCH_SHOOTING_FEASIBILITY"
        or v38.get("classification") != "MIRRORED_PITCH_SUBSPACE_NOT_FULL_HORIZON_FEASIBLE"
        or v38.get("decision") != "CLOSE_MIRRORED_PITCH_SHOOTING_MECHANISM"
        or v38.get("summary", {}).get("support_passes") != 0
        or v38.get("summary", {}).get("terminal_ticks") != [69, 161]
        or v38.get("execution", {}).get("optimizer_updates") != 0
        or v38.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v38 does not support a new controller family")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v39.response_jacobian_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_RESPONSE_JACOBIAN_COM_X_NEG_SCREEN",
        "question": (
            "Can deterministic local model-based feedback hold COM_X_NEG by measuring the "
            "exact eight-tick pitch/pitch-rate response Jacobian of the reviewed mirrored "
            "pitch coordinates and applying one minimum-norm correction per tick?"
        ),
        "evidence_basis": {
            "v36_v37_v38_full_support_passes": [0, 0, 0],
            "v38_terminal_ticks": [69, 161],
            "v38_failure_check": "pitch-led roll_pitch only",
            "closed_family": (
                "cold, warm-started, and mirrored stochastic CEM shooting did not yield a "
                "full-horizon teacher"
            ),
            "new_family": (
                "deterministic finite-difference local response inversion; no stochastic "
                "population, elite selection, CEM objective, or proposal state"
            ),
        },
        "screen": {
            "configuration_ids": ["COM_X_NEG"],
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "controlled_action_indices": [2, 3, 4, 11, 12, 13],
            "response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"],
            "control_dimensions": ["hip_pitch_magnitude", "knee", "ankle"],
            "duration_ticks": 250,
            "response_horizon_ticks": 8,
            "finite_difference_scale": (
                "minimum paired graph action delta per mirrored axis"
            ),
            "solver": "numpy.linalg.lstsq(rcond=None), minimum-norm correction",
            "correction_bound": "one finite-difference step per mirrored axis",
            "expected_cells": 2,
            "constraints": (
                "Every response rollout and selected action uses the exact graph action "
                "boundary and unchanged P30 or P31/34 actuator bridge."
            ),
        },
        "pass_rule": {
            "both_plants_pass_full_250_tick_support_gate": True,
            "all_response_jacobians_full_row_rank": True,
            "all_selected_actions_graph_bounded": True,
            "all_cells_use_nonzero_control": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "A bounded local response-Jacobian teacher exists at COM_X_NEG; authorize "
                "only a separate teacher-contract preregistration."
            ),
            "hold": (
                "Close this exact local response-Jacobian controller. Do not tune its finite "
                "difference scale, horizon, response coordinates, solver, or correction bound."
            ),
        },
        "execution_now": {
            "response_jacobian_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v38_result_lf_sha256": lf_sha256(V38_RESULT),
            "repository_attribution": v38["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_oracle_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen response-Jacobian teacher contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v39 response-Jacobian feasibility preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Anchor / plants / ticks: `COM_X_NEG / 2 / 250`",
            "- Response: signed base pitch + body pitch rate at tick `8`",
            "- Control basis: mirrored hip-pitch magnitude / knee / ankle",
            "- Perturbation: exact minimum paired graph delta",
            "- Solver: deterministic minimum-norm least squares; one-step correction bound",
            "- Optimizer updates / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This is a simulator-oracle controller-family test, not a deployable controller.",
            "A pass can authorize only a teacher contract; a hold closes the exact controller.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
