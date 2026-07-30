#!/usr/bin/env python3
"""Run T203's read-only roll-risk persistence autopsy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
from run_t174_t173_failure_autopsy import (
    load_rows,
    make_session,
    replay_trace,
)
from run_t201_t194_predicted_roll_risk import predicted_roll_risk


PREREG = ANALYSIS / "t208_t203_persistence_autopsy_preregistration.json"
RESULT = ANALYSIS / "t208_t203_persistence_autopsy_result.json"
MARKDOWN = ANALYSIS / "T208_T203_PERSISTENCE_AUTOPSY_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{checkpoint}_{item['fit_id']}_x{command}"


def risk_summary(
    rows: list[dict[str, Any]],
    *,
    horizon_s: float,
    envelope_rad: float,
    scale: float,
    cell_green: bool,
) -> dict[str, Any]:
    roll = np.asarray([row["body_roll_rad"] for row in rows], np.float64)
    roll_rate = np.asarray(
        [row["body_roll_rate_rad_s"] for row in rows], np.float64
    )
    risk = predicted_roll_risk(roll, roll_rate, horizon_s)
    excess = np.maximum(0.0, risk - envelope_rad)
    indices = np.flatnonzero(excess > 0.0)
    force = np.asarray(
        [row["actuator_force_nm"] for row in rows], np.float64
    )
    last_tick = len(rows) - 1
    return {
        "cell_green": cell_green,
        "rows": len(rows),
        "risk_finite": bool(np.all(np.isfinite(risk))),
        "maximum_risk_rad": float(np.max(risk)),
        "exceedance_rows": int(len(indices)),
        "first_exceedance_tick": (
            int(indices[0]) if len(indices) else None
        ),
        "lead_ticks_to_terminal": (
            int(last_tick - indices[0]) if len(indices) else None
        ),
        "maximum_excess_rad": float(np.max(excess)),
        "squared_excess_integral": float(np.sum(np.square(excess))),
        "scaled_cost_integral": float(scale * np.sum(np.square(excess))),
        "maximum_abs_actuator_force_nm": float(np.max(np.abs(force))),
        "terminal_roll_rad": float(roll[-1]),
        "terminal_roll_rate_rad_s": float(roll_rate[-1]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T208 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T208 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T208_T203_PERSISTENCE_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T208 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for name, item in prereg["graphs"].items():
        verify(item, f"graphs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")
    verify(prereg["old_t194_failure"]["trace"], "old_t194_failure.trace")

    started = time.time()
    sessions = {
        name: make_session(Path(item["path"]))
        for name, item in prereg["graphs"].items()
    }
    contexts = {
        fit: np.asarray(item["context"], np.float32).reshape(1, 64)
        for fit, item in prereg["contexts"].items()
    }
    rows_by_trace = {
        label(item): load_rows(item) for item in prereg["traces"]
    }
    metadata = {label(item): item for item in prereg["traces"]}
    replay = {}
    for item in prereg["traces"]:
        name = label(item)
        graph_name = (
            "half" if item["checkpoint_id"].endswith("HALF") else "final"
        )
        replay[name] = replay_trace(
            rows_by_trace[name],
            sessions[graph_name],
            contexts[item["fit_id"]],
        )

    analysis = prereg["analysis"]
    horizon_s = float(analysis["prediction_horizon_s"])
    envelope = float(analysis["passing_envelope_rad"])
    scale = float(analysis["fixed_cost_scale"])
    summaries = {
        name: risk_summary(
            rows,
            horizon_s=horizon_s,
            envelope_rad=envelope,
            scale=scale,
            cell_green=bool(metadata[name]["cell_green"]),
        )
        for name, rows in rows_by_trace.items()
    }
    old_rows = load_rows(prereg["old_t194_failure"])
    old_summary = risk_summary(
        old_rows,
        horizon_s=horizon_s,
        envelope_rad=envelope,
        scale=scale,
        cell_green=False,
    )
    failure_names = [
        name for name, row in summaries.items() if not row["cell_green"]
    ]
    passing_names = [
        name for name, row in summaries.items() if row["cell_green"]
    ]
    failure_name = failure_names[0]
    failure = summaries[failure_name]
    signal_rule = analysis["signal_retention_rule"]
    signal_retained = (
        all(
            summaries[name]["exceedance_rows"]
            == int(signal_rule["all_15_passing_exceedance_rows"])
            for name in passing_names
        )
        and failure["exceedance_rows"]
        >= int(signal_rule["failure_minimum_exceedance_rows"])
        and failure["lead_ticks_to_terminal"] is not None
        and failure["lead_ticks_to_terminal"]
        >= int(signal_rule["minimum_failure_lead_ticks"])
        and failure["squared_excess_integral"]
        > max(
            summaries[name]["squared_excess_integral"]
            for name in passing_names
        )
    )
    hosted_cost = [float(value) for value in analysis["hosted_cost"]]
    hosted_excess = [float(value) for value in analysis["hosted_excess"]]
    fixed_price_drifted = (
        hosted_cost[1] < hosted_cost[0]
        and hosted_cost[2] > hosted_cost[1]
        and hosted_excess[1] < hosted_excess[0]
        and hosted_excess[2] > hosted_excess[1]
        and summaries["half_p31_34_x0p077"]["cell_green"]
        and not summaries["final_p31_34_x0p077"]["cell_green"]
    )
    checks = {
        "sixteen_traces_exact_15_pass_one_failure": (
            len(rows_by_trace) == 16
            and len(passing_names) == 15
            and failure_names == ["final_p31_34_x0p077"]
        ),
        "all_trace_row_counts_exact": all(
            len(rows_by_trace[name]) == int(metadata[name]["samples"])
            for name in rows_by_trace
        ),
        "all_ticks_contiguous": all(
            np.array_equal(
                np.asarray([row["tick"] for row in rows], np.int64),
                np.arange(len(rows)),
            )
            for rows in rows_by_trace.values()
        ),
        "all_recorded_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in replay.values()
        ),
        "all_recorded_outputs_finite": all(
            row["all_outputs_finite"] for row in replay.values()
        ),
        "all_risks_finite": (
            all(row["risk_finite"] for row in summaries.values())
            and old_summary["risk_finite"]
        ),
        "new_failure_is_363_rows_and_done": (
            failure["rows"] == 363
            and bool(rows_by_trace[failure_name][-1]["done"])
        ),
        "paired_half_trace_is_full_duration": (
            summaries["half_p31_34_x0p077"]["rows"] == 600
        ),
        "old_failure_is_308_rows_and_done": (
            old_summary["rows"] == 308 and bool(old_rows[-1]["done"])
        ),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in sessions.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and signal_retained and fixed_price_drifted
    decision = (
        prereg["decision_rule"][
            "signal_retained_and_fixed_price_drifted"
        ]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t208_t203_persistence_autopsy_result.v1"
        ),
        "status": (
            "PASS_T208_T203_PERSISTENCE_AUTOPSY"
            if not failed
            else "HOLD_T208_T203_PERSISTENCE_AUTOPSY"
        ),
        "classification": (
            "ROLL_SIGNAL_RETAINED_FIXED_PRICE_LOST_PERSISTENCE"
            if signal_retained and fixed_price_drifted
            else "T203_FAILURE_DOES_NOT_EARN_DUAL_ROLL_COST"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "signal_retention_rule_passed": signal_retained,
        "fixed_price_drift_rule_passed": fixed_price_drifted,
        "prediction_horizon_s": horizon_s,
        "passing_envelope_rad": envelope,
        "fixed_cost_scale": scale,
        "failure_trace": failure_name,
        "failure": failure,
        "old_t194_failure": old_summary,
        "terminal_delay_vs_t194_ticks": (
            failure["rows"] - old_summary["rows"]
        ),
        "hosted_metrics": {
            "order": analysis["hosted_metric_order"],
            "cost": hosted_cost,
            "excess": hosted_excess,
        },
        "trace_summaries": summaries,
        "replay": replay,
        "execution": {
            "inference_rows": sum(
                row["rows"] for row in replay.values()
            ),
            "trace_rows": (
                sum(len(rows) for rows in rows_by_trace.values())
                + len(old_rows)
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "cpu_contract_preregistration": earned,
            "behavior": False,
            "training": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T208 T203 persistence autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- New failure first exceedance / lead / rows: "
        f"`{failure['first_exceedance_tick']}` / "
        f"`{failure['lead_ticks_to_terminal']}` / "
        f"`{failure['exceedance_rows']}`\n"
        f"- New versus old terminal delay: "
        f"`{value['terminal_delay_vs_t194_ticks']}` ticks\n"
        f"- Hosted fixed cost step0/half/final: `{hosted_cost}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
