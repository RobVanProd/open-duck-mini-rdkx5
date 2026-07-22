#!/usr/bin/env python3
"""Freeze one full-horizon static-equilibrium target feasibility screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v41_static_equilibrium_target_feasibility_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY_PREREGISTRATION_20260722.md"
)
V40_RESULT = ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_result.json"
CLOSED_LEDGER = ANALYSIS / "CLOSED_BRANCHES_LEDGER_20260716.md"

SOURCES = {
    "builder": Path(
        "tools/build_winner_v41_static_equilibrium_target_feasibility_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v41_static_equilibrium_target_feasibility.py"),
    "runner_tests": Path(
        "tests/test_winner_v41_static_equilibrium_target_feasibility.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v41_static_equilibrium_target_feasibility_preregistration.py"
    ),
    "result_importer": Path(
        "tools/import_winner_v41_static_equilibrium_target_feasibility.py"
    ),
    "result_importer_tests": Path(
        "tests/test_winner_v41_static_equilibrium_target_feasibility_import.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v41-static-equilibrium-target-feasibility.yml"
    ),
    "winner_v40_result": Path(
        "outputs/analysis/winner_v40_response_jacobian_invalidity_attribution_result.json"
    ),
    "closed_branches_ledger": Path("outputs/analysis/CLOSED_BRANCHES_LEDGER_20260716.md"),
    "reviewed_mirror_basis": Path("patches/winner_v16_support_action_direction.py"),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v41 preregistration")
    v40 = json.loads(V40_RESULT.read_text(encoding="utf-8"))
    if (
        v40.get("status")
        != "PASS_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        or v40.get("classification")
        != "TERMINAL_TRUNCATION_EXPLAINS_RANK_INVALIDITY_NOT_SUPPORT_FAILURE"
        or v40.get("decision") != "CLOSE_EXACT_V39_CONTROLLER_WITHOUT_RERUN"
        or v40.get("execution", {}).get("simulation_cells") != 0
        or v40.get("authority", {}).get("pass_authorizes_only")
        != "a separately frozen nonlocal support-controller feasibility design"
        or v40.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v40 does not authorize the V41 design")
    ledger = CLOSED_LEDGER.read_text(encoding="utf-8")
    for required in (
        "Fixed shooting MPC", "Lexicographic viability/command source",
        "Bounded six-joint receding horizon",
    ):
        if required not in ledger:
            raise ValueError("Winner-v41 closed-branch ledger changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    grid = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    value = {
        "schema_version": "winner_v41.static_equilibrium_target_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_FULL_HORIZON_STATIC_TARGET_SCREEN",
        "question": (
            "Does one time-invariant target in the reviewed bilateral pitch basis, "
            "ramped only by the unchanged graph boundary, hold COM_X_NEG for all 250 "
            "ticks under both actuator plants?"
        ),
        "material_difference_from_closed_routes": {
            "fixed_shooting_mpc": (
                "No receding horizon, sampled action sequence, short-horizon objective, "
                "or per-tick replanning; each candidate is one constant full-episode target."
            ),
            "bounded_six_joint_receding_horizon": (
                "Tests a global equilibrium posture from reset rather than composability "
                "of local pulses from already-failing states."
            ),
            "winner_v38_cem": (
                "Keeps the reviewed basis unchanged but removes population adaptation, "
                "covariance, elites, warm state, and changing plans; the finite grid is "
                "exhausted once with no refinement."
            ),
            "winner_v39_response_inversion": (
                "No local Jacobian, response target, least-squares inverse, or terminal-"
                "truncated probe; only direct full-horizon equilibrium evidence decides."
            ),
        },
        "screen": {
            "configuration_ids": ["COM_X_NEG"],
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "controlled_action_indices": [2, 3, 4, 11, 12, 13],
            "coordinate_order": ["hip_pitch_magnitude", "knee", "ankle"],
            "grid_values": grid,
            "grid_dimensions": 3,
            "candidate_count": 729,
            "duration_ticks": 250,
            "target_semantics": "one time-invariant raw action target for all 250 ticks",
            "plant_semantics": "one shared target must pass both measured actuator plants",
            "selection": (
                "Exhaust all 729 targets; pass only if at least one target passes both "
                "plants. A deterministic diagnostic best may be reported on HOLD but "
                "cannot be promoted."
            ),
        },
        "pass_rule": {
            "exact_729_static_targets": True,
            "exact_1458_candidate_plant_cells": True,
            "all_candidate_actions_graph_bounded": True,
            "selected_target_replay_exact": True,
            "at_least_one_shared_target_passes_both_plants": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "A shared static support target exists; authorize only a separately "
                "frozen static-target teacher contract."
            ),
            "hold": (
                "Close the exact nine-level static-equilibrium route without grid "
                "refinement, changed bounds, another basis, or closest promotion."
            ),
        },
        "execution_now": {
            "static_target_candidates": 0,
            "candidate_plant_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v40_result_lf_sha256": lf_sha256(V40_RESULT),
            "repository_attribution": v40["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen static-target teacher contract",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v41 static-equilibrium target feasibility preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Anchor / plants / duration: `COM_X_NEG / 2 / 250 ticks`",
            "- Grid: `9^3 = 729` fixed bilateral-pitch targets",
            "- Candidate plant cells: `1,458`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This is a full-horizon equilibrium feasibility screen, not receding-horizon",
            "MPC, a runtime wrapper, a checkpoint, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
