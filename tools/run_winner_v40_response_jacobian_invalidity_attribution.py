#!/usr/bin/env python3
"""Attribute the frozen Winner-v39 INVALID result without rerunning simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import import_winner_v39_response_jacobian_feasibility as v39_import  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_preregistration.json"
)
V39_RESULT = ANALYSIS / "winner_v39_response_jacobian_feasibility_result.json"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
RESPONSE_HORIZON_TICKS = 8
MAXIMUM_TERMINAL_FRINGE_TICKS = 2


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("status")
        != "PREREGISTERED_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_SAVED_RESULT_ONLY_V39_INVALIDITY_ATTRIBUTION"
    ):
        raise ValueError("Winner-v40 is not preregistered")
    if value.get("audit") != {
        "source_status": "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY",
        "plants": list(PLANTS),
        "response_horizon_ticks": RESPONSE_HORIZON_TICKS,
        "maximum_terminal_fringe_ticks": MAXIMUM_TERMINAL_FRINGE_TICKS,
        "expected_source_cells": 2,
        "expected_source_support_passes": 0,
        "expected_source_terminal_ticks": [32, 31],
        "expected_v38_terminal_ticks": [69, 161],
    }:
        raise ValueError("Winner-v40 audit constants changed")
    if value.get("execution_now") != {
        "saved_result_audits": 0,
        "simulation_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v40 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v40 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v40 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v40 source manifest changed")


def analyze_cell(row: Mapping[str, Any], v38_terminal_tick: int) -> dict[str, Any]:
    trace = row["trace"]
    rank_loss = [item for item in trace if item["planning"]["jacobian_rank"] < 2]
    if not rank_loss:
        raise ValueError("Winner-v40 expected a recorded V39 rank loss")
    first_rank_loss_tick = int(rank_loss[0]["tick"])
    terminal_tick = int(row["terminal"]["tick"])
    events: list[dict[str, Any]] = []
    for item in rank_loss:
        planning = item["planning"]
        zero_axes: list[int] = []
        terminal_truncated_zero_axes: list[int] = []
        for perturbation in planning["perturbations"]:
            axis = int(perturbation["axis"])
            minus = perturbation["minus"]
            plus = perturbation["plus"]
            identical_response = minus["response"] == plus["response"]
            if identical_response:
                zero_axes.append(axis)
            terminal_truncated = (
                minus["terminal"] is not None
                and plus["terminal"] is not None
                and minus["valid_ticks"] < RESPONSE_HORIZON_TICKS
                and plus["valid_ticks"] < RESPONSE_HORIZON_TICKS
            )
            if identical_response and terminal_truncated:
                terminal_truncated_zero_axes.append(axis)
        minimum_zero_columns_for_rank = 3 - int(planning["jacobian_rank"])
        events.append(
            {
                "tick": int(item["tick"]),
                "jacobian_rank": int(planning["jacobian_rank"]),
                "singular_values": planning["singular_values"],
                "zero_response_axes": zero_axes,
                "terminal_truncated_zero_response_axes": terminal_truncated_zero_axes,
                "minimum_zero_columns_for_recorded_rank": minimum_zero_columns_for_rank,
                "terminal_truncation_accounts_for_rank_loss": (
                    len(terminal_truncated_zero_axes) >= minimum_zero_columns_for_rank
                ),
            }
        )
    return {
        "plant": row["plant"],
        "source_support_pass": row["support_pass"],
        "source_terminal_tick": terminal_tick,
        "v38_terminal_tick": v38_terminal_tick,
        "terminal_tick_delta_vs_v38": terminal_tick - v38_terminal_tick,
        "first_rank_loss_tick": first_rank_loss_tick,
        "rank_loss_ticks": [int(item["tick"]) for item in rank_loss],
        "ticks_from_first_rank_loss_to_terminal": terminal_tick - first_rank_loss_tick,
        "all_pre_loss_jacobians_full_row_rank": all(
            item["planning"]["jacobian_rank"] == 2
            for item in trace[:first_rank_loss_tick]
        ),
        "all_rank_losses_in_terminal_fringe": (
            0 <= terminal_tick - first_rank_loss_tick <= MAXIMUM_TERMINAL_FRINGE_TICKS
        ),
        "all_rank_losses_accounted_for_by_terminal_truncation": all(
            event["terminal_truncation_accounts_for_rank_loss"] for event in events
        ),
        "source_actions_graph_bounded": row["all_actions_bounded"],
        "source_used_nonzero_control": row["any_nonzero_action"],
        "source_terminated_earlier_than_v38": terminal_tick < v38_terminal_tick,
        "rank_loss_events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-saved-result-only", action="store_true")
    parser.add_argument("--invalidity-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_saved_result_only or not args.invalidity_attribution_authorized:
        raise PermissionError(
            "Winner-v40 requires --offline-saved-result-only "
            "--invalidity-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v40 result")

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v39 = json.loads(V39_RESULT.read_text(encoding="utf-8"))
    v39_import.validate_result(v39)
    if (
        v39.get("status") != "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        or v39.get("decision") != "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        or v39.get("failed_checks") != [
            "all_response_jacobians_full_row_rank",
            "both_plants_pass_full_250_tick_support_gate",
        ]
        or v39.get("summary", {}).get("support_passes") != 0
        or v39.get("summary", {}).get("terminal_ticks") != [32, 31]
        or v39.get("summary", {}).get("v38_terminal_ticks") != [69, 161]
    ):
        raise ValueError("Winner-v39 source result changed")

    rows = [
        analyze_cell(row, v38_tick)
        for row, v38_tick in zip(
            v39["cell_results"], v39["summary"]["v38_terminal_ticks"]
        )
    ]
    checks = {
        "exact_two_saved_source_cells": len(rows) == 2,
        "all_pre_loss_jacobians_full_row_rank": all(
            row["all_pre_loss_jacobians_full_row_rank"] for row in rows
        ),
        "all_rank_losses_in_final_two_tick_terminal_fringe": all(
            row["all_rank_losses_in_terminal_fringe"] for row in rows
        ),
        "all_rank_losses_accounted_for_by_terminal_truncated_identical_responses": all(
            row["all_rank_losses_accounted_for_by_terminal_truncation"] for row in rows
        ),
        "both_recorded_controllers_used_bounded_nonzero_actions": all(
            row["source_actions_graph_bounded"] and row["source_used_nonzero_control"]
            for row in rows
        ),
        "both_recorded_controllers_failed_support": all(
            not row["source_support_pass"] for row in rows
        ),
        "both_recorded_controllers_terminate_earlier_than_v38": all(
            row["source_terminated_earlier_than_v38"] for row in rows
        ),
    }
    passed = all(checks.values())
    if passed:
        status = "PASS_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        classification = "TERMINAL_TRUNCATION_EXPLAINS_RANK_INVALIDITY_NOT_SUPPORT_FAILURE"
        decision = "CLOSE_EXACT_V39_CONTROLLER_WITHOUT_RERUN"
    else:
        status = "HOLD_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION"
        classification = "V39_INVALIDITY_NOT_FULLY_ATTRIBUTED"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    result = {
        "schema_version": "winner_v40.response_jacobian_invalidity_attribution_result.v1",
        "status": status,
        "classification": classification,
        "decision": decision,
        "checks": checks,
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "cell_attribution": rows,
        "summary": {
            "source_support_passes": v39["summary"]["support_passes"],
            "source_terminal_ticks": v39["summary"]["terminal_ticks"],
            "v38_terminal_ticks": v39["summary"]["v38_terminal_ticks"],
            "first_rank_loss_ticks": [row["first_rank_loss_tick"] for row in rows],
            "rank_loss_tick_counts": [len(row["rank_loss_ticks"]) for row in rows],
            "terminal_tick_deltas_vs_v38": [
                row["terminal_tick_delta_vs_v38"] for row in rows
            ],
        },
        "execution": {
            "saved_result_audits": 1,
            "simulation_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "winner_v39_result_lf_sha256": lf_sha256(V39_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
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
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(status)
    print(f"FIRST_RANK_LOSS_TICKS={result['summary']['first_rank_loss_ticks']}")
    print(f"SOURCE_TERMINAL_TICKS={result['summary']['source_terminal_ticks']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
