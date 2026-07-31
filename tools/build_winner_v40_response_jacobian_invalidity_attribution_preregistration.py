#!/usr/bin/env python3
"""Freeze one saved-result-only attribution of the Winner-v39 INVALID result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION_PREREGISTRATION_20260722.md"
)
V39_RESULT = ANALYSIS / "winner_v39_response_jacobian_feasibility_result.json"

SOURCES = {
    "builder": Path(
        "tools/build_winner_v40_response_jacobian_invalidity_attribution_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v40_response_jacobian_invalidity_attribution.py"),
    "runner_tests": Path(
        "tests/test_winner_v40_response_jacobian_invalidity_attribution.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v40_response_jacobian_invalidity_attribution_preregistration.py"
    ),
    "result_importer": Path(
        "tools/import_winner_v40_response_jacobian_invalidity_attribution.py"
    ),
    "result_importer_tests": Path(
        "tests/test_winner_v40_response_jacobian_invalidity_attribution_import.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v40-response-jacobian-invalidity-attribution.yml"
    ),
    "winner_v39_result": Path(
        "outputs/analysis/winner_v39_response_jacobian_feasibility_result.json"
    ),
    "winner_v39_result_importer": Path(
        "tools/import_winner_v39_response_jacobian_feasibility.py"
    ),
    "winner_v39_preregistration": Path(
        "outputs/analysis/winner_v39_response_jacobian_feasibility_preregistration.json"
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
        raise FileExistsError("refusing to overwrite Winner-v40 preregistration")
    v39 = json.loads(V39_RESULT.read_text(encoding="utf-8"))
    if (
        v39.get("status") != "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        or v39.get("classification") != "INVALID_RESPONSE_JACOBIAN_SCREEN"
        or v39.get("decision") != "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        or v39.get("failed_checks") != [
            "all_response_jacobians_full_row_rank",
            "both_plants_pass_full_250_tick_support_gate",
        ]
        or v39.get("summary", {}).get("support_passes") != 0
        or v39.get("summary", {}).get("terminal_ticks") != [32, 31]
        or v39.get("summary", {}).get("v38_terminal_ticks") != [69, 161]
        or v39.get("execution", {}).get("simulation_cells", 0) != 0
        or v39.get("execution", {}).get("optimizer_updates") != 0
        or v39.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v39 does not support the saved-result attribution")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": (
            "winner_v40.response_jacobian_invalidity_attribution_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        ),
        "decision": "AUTHORIZE_ONE_SAVED_RESULT_ONLY_V39_INVALIDITY_ATTRIBUTION",
        "question": (
            "Is Winner-v39's rank invalidity confined to the final two-tick terminal "
            "fringe and accounted for by terminal-truncated identical-response finite-"
            "difference branches, while its recorded bounded controller independently "
            "fails both support cells earlier than Winner-v38?"
        ),
        "audit": {
            "source_status": "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY",
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "response_horizon_ticks": 8,
            "maximum_terminal_fringe_ticks": 2,
            "expected_source_cells": 2,
            "expected_source_support_passes": 0,
            "expected_source_terminal_ticks": [32, 31],
            "expected_v38_terminal_ticks": [69, 161],
        },
        "pass_rule": {
            "exact_two_saved_source_cells": True,
            "all_pre_loss_jacobians_full_row_rank": True,
            "all_rank_losses_in_final_two_tick_terminal_fringe": True,
            (
                "all_rank_losses_accounted_for_by_terminal_truncated_identical_responses"
            ): True,
            "both_recorded_controllers_used_bounded_nonzero_actions": True,
            "both_recorded_controllers_failed_support": True,
            "both_recorded_controllers_terminate_earlier_than_v38": True,
        },
        "interpretation": {
            "pass": (
                "Close only the exact V39 controller without rerun. The invalid rank gate "
                "is attributed, but no response-inversion family or physical "
                "controllability conclusion is authorized. Permit only a separately "
                "frozen nonlocal support-controller feasibility design."
            ),
            "hold": (
                "Keep DO_NOT_SELECT_NEXT_POLICY_MECHANISM. Do not rerun V39 or alter its "
                "rank, response, horizon, perturbation, solver, or bound."
            ),
        },
        "execution_now": {
            "saved_result_audits": 0,
            "simulation_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "source_result": {
            "winner_v39_result_lf_sha256": lf_sha256(V39_RESULT),
            "repository_attribution": v39["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "v39_rerun_authorized": False,
            "simulation_or_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separately frozen nonlocal support-controller feasibility design"
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
            "# Winner-v40 response-Jacobian invalidity attribution preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Input: committed Winner-v39 result only",
            "- Simulation / optimizer / locomotion / robot: `0 / 0 / 0 / 0`",
            "- No V39 rerun or rank-rule change", "",
            value["question"], "",
            "A pass closes only the exact recorded V39 controller and may authorize",
            "only a separate nonlocal feasibility design. It is not clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
