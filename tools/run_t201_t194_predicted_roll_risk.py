#!/usr/bin/env python3
"""Run T194's saved-trace predicted-roll risk diagnostic."""

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


PREREG = ANALYSIS / "t201_t194_predicted_roll_risk_preregistration.json"
RESULT = ANALYSIS / "t201_t194_predicted_roll_risk_result.json"
MARKDOWN = ANALYSIS / "T201_T194_PREDICTED_ROLL_RISK_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{checkpoint}_{item['fit_id']}_x{command}"


def load_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in Path(item["trace"]["path"]).read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    if len(rows) != int(item["samples"]):
        raise RuntimeError(f"trace row count changed: {item}")
    return rows


def predicted_roll_risk(
    roll: np.ndarray,
    roll_rate: np.ndarray,
    horizon_s: float,
) -> np.ndarray:
    return np.abs(roll + horizon_s * roll_rate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T201 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T201 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T201_T194_PREDICTED_ROLL_RISK"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T201 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    started = time.time()
    horizon_s = float(prereg["analysis"]["prediction_horizon_s"])
    rows_by_trace = {
        label(item): load_rows(item) for item in prereg["traces"]
    }
    metadata = {
        label(item): item for item in prereg["traces"]
    }
    risks = {}
    trace_checks = {}
    for name, rows in rows_by_trace.items():
        ticks = np.asarray([row["tick"] for row in rows], np.int64)
        roll = np.asarray(
            [row["body_roll_rad"] for row in rows], np.float64
        )
        roll_rate = np.asarray(
            [row["body_roll_rate_rad_s"] for row in rows],
            np.float64,
        )
        risks[name] = predicted_roll_risk(roll, roll_rate, horizon_s)
        trace_checks[name] = {
            "rows": len(rows),
            "ticks_contiguous": bool(
                np.array_equal(ticks, np.arange(len(rows)))
            ),
            "roll_and_rate_finite": bool(
                np.all(np.isfinite(roll))
                and np.all(np.isfinite(roll_rate))
            ),
            "risk_finite": bool(np.all(np.isfinite(risks[name]))),
        }
    passing_names = [
        name for name, item in metadata.items() if item["cell_green"]
    ]
    failure_names = [
        name for name, item in metadata.items() if not item["cell_green"]
    ]
    failure_name = failure_names[0]
    pass_maximum = max(
        float(np.max(risks[name])) for name in passing_names
    )
    envelope = float(np.nextafter(pass_maximum, np.inf))
    summaries = {}
    for name, risk in risks.items():
        excess = np.maximum(0.0, risk - envelope)
        indices = np.flatnonzero(excess > 0.0)
        last_tick = len(risk) - 1
        summaries[name] = {
            "cell_green": bool(metadata[name]["cell_green"]),
            "rows": len(risk),
            "maximum_risk_rad": float(np.max(risk)),
            "exceedance_rows": int(len(indices)),
            "first_exceedance_tick": (
                int(indices[0]) if len(indices) else None
            ),
            "lead_ticks_to_terminal": (
                int(last_tick - indices[0]) if len(indices) else None
            ),
            "maximum_excess_rad": float(np.max(excess)),
            "squared_excess_integral": float(
                np.sum(np.square(excess))
            ),
        }
    failure = summaries[failure_name]
    rule = prereg["analysis"]["separation_rule"]
    separation = (
        all(
            summaries[name]["exceedance_rows"]
            == int(rule["all_passing_exceedance_rows"])
            for name in passing_names
        )
        and failure["exceedance_rows"]
        >= int(rule["failure_minimum_exceedance_rows"])
        and failure["lead_ticks_to_terminal"] is not None
        and failure["lead_ticks_to_terminal"]
        >= int(rule["minimum_failure_lead_ticks"])
        and failure["maximum_risk_rad"] > envelope
    )
    checks = {
        "sixteen_traces_exact": (
            len(rows_by_trace) == 16
            and len(passing_names) == 15
            and len(failure_names) == 1
        ),
        "all_trace_row_counts_exact": all(
            trace_checks[name]["rows"] == metadata[name]["samples"]
            for name in rows_by_trace
        ),
        "all_ticks_contiguous": all(
            row["ticks_contiguous"] for row in trace_checks.values()
        ),
        "all_roll_rate_and_risk_finite": all(
            row["roll_and_rate_finite"] and row["risk_finite"]
            for row in trace_checks.values()
        ),
        "failure_is_exact_half_p31_x0077": (
            failure_name == "half_p31_34_x0p077"
            and failure["rows"] == 308
        ),
        "passing_envelope_is_nextafter_maximum": (
            envelope > pass_maximum
            and np.nextafter(pass_maximum, np.inf) == envelope
        ),
        "candidate_cost_nonnegative": all(
            row["squared_excess_integral"] >= 0.0
            for row in summaries.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and separation
    decision = (
        prereg["decision_rule"]["risk_is_early_dense_and_separable"]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t201_t194_predicted_roll_risk_result.v1"
        ),
        "status": (
            "PASS_T201_T194_PREDICTED_ROLL_RISK"
            if not failed
            else "HOLD_T201_T194_PREDICTED_ROLL_RISK"
        ),
        "classification": (
            "PREDICTED_ROLL_RISK_EARLY_DENSE_AND_PASS_SEPARABLE"
            if separation
            else "PREDICTED_ROLL_RISK_NOT_EARLY_DENSE_AND_SEPARABLE"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "separation_rule_passed": separation,
        "prediction_horizon_s": horizon_s,
        "passing_risk_maximum_rad": pass_maximum,
        "passing_envelope_rad": envelope,
        "failure_trace": failure_name,
        "failure": failure,
        "trace_summaries": summaries,
        "execution": {
            "trace_rows": sum(len(rows) for rows in rows_by_trace.values()),
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
        "# T201 T194 predicted-roll risk result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Passing envelope: `{envelope:.9f}` rad\n"
        f"- Failure first exceedance / lead / rows: "
        f"`{failure['first_exceedance_tick']}` / "
        f"`{failure['lead_ticks_to_terminal']}` / "
        f"`{failure['exceedance_rows']}`\n"
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
