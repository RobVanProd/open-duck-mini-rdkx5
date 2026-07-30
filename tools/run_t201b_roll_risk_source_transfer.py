#!/usr/bin/env python3
"""Run the T170/T194 predicted-roll source-transfer audit."""

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
from run_t201_t194_predicted_roll_risk import predicted_roll_risk


PREREG = ANALYSIS / "t201b_roll_risk_source_transfer_preregistration.json"
RESULT = ANALYSIS / "t201b_roll_risk_source_transfer_result.json"
MARKDOWN = ANALYSIS / "T201B_ROLL_RISK_SOURCE_TRANSFER_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{item['family']}_{checkpoint}_{item['fit_id']}_x{command}"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T201B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T201B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T201B_ROLL_RISK_SOURCE_TRANSFER"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T201B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    started = time.time()
    horizon = float(prereg["analysis"]["prediction_horizon_s"])
    metadata = {label(item): item for item in prereg["traces"]}
    rows_by_trace = {
        label(item): load_rows(item) for item in prereg["traces"]
    }
    risks = {}
    finite = {}
    contiguous = {}
    for name, rows in rows_by_trace.items():
        ticks = np.asarray([row["tick"] for row in rows], np.int64)
        roll = np.asarray(
            [row["body_roll_rad"] for row in rows], np.float64
        )
        rate = np.asarray(
            [row["body_roll_rate_rad_s"] for row in rows],
            np.float64,
        )
        risks[name] = predicted_roll_risk(roll, rate, horizon)
        finite[name] = bool(np.all(np.isfinite(risks[name])))
        contiguous[name] = bool(
            np.array_equal(ticks, np.arange(len(rows)))
        )
    passing = [
        name for name, item in metadata.items() if item["cell_green"]
    ]
    failures = [
        name for name, item in metadata.items() if not item["cell_green"]
    ]
    pass_maximum = max(float(np.max(risks[name])) for name in passing)
    envelope = float(np.nextafter(pass_maximum, np.inf))
    summaries = {}
    for name, risk in risks.items():
        excess = np.maximum(0.0, risk - envelope)
        indices = np.flatnonzero(excess > 0.0)
        summaries[name] = {
            "family": metadata[name]["family"],
            "cell_green": bool(metadata[name]["cell_green"]),
            "rows": len(risk),
            "maximum_risk_rad": float(np.max(risk)),
            "exceedance_rows": int(len(indices)),
            "first_exceedance_tick": (
                int(indices[0]) if len(indices) else None
            ),
            "lead_ticks_to_terminal": (
                int(len(risk) - 1 - indices[0])
                if len(indices)
                else None
            ),
            "maximum_excess_rad": float(np.max(excess)),
            "squared_excess_integral": float(
                np.sum(np.square(excess))
            ),
        }
    rule = prereg["analysis"]["per_failure_rule"]
    per_failure = {
        name: (
            summaries[name]["exceedance_rows"]
            >= int(rule["minimum_exceedance_rows"])
            and summaries[name]["lead_ticks_to_terminal"] is not None
            and summaries[name]["lead_ticks_to_terminal"]
            >= int(rule["minimum_lead_ticks"])
            and summaries[name]["maximum_risk_rad"] > envelope
        )
        for name in failures
    }
    separation = (
        all(summaries[name]["exceedance_rows"] == 0 for name in passing)
        and all(per_failure.values())
    )
    checks = {
        "twenty_traces_eighteen_passes_two_failures": (
            len(risks) == 20
            and len(passing) == 18
            and len(failures) == 2
        ),
        "all_row_counts_exact": all(
            len(rows_by_trace[name]) == metadata[name]["samples"]
            for name in risks
        ),
        "all_ticks_contiguous": all(contiguous.values()),
        "all_risks_finite": all(finite.values()),
        "failures_span_t170_and_t194": (
            {metadata[name]["family"] for name in failures}
            == {"t170", "t194"}
        ),
        "combined_envelope_is_nextafter_pass_maximum": (
            envelope > pass_maximum
            and envelope == np.nextafter(pass_maximum, np.inf)
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
        prereg["decision_rule"]["both_failures_separable"]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t201b_roll_risk_source_transfer_result.v1"
        ),
        "status": (
            "PASS_T201B_ROLL_RISK_SOURCE_TRANSFER"
            if not failed
            else "HOLD_T201B_ROLL_RISK_SOURCE_TRANSFER"
        ),
        "classification": (
            "COMBINED_ROLL_RISK_EARLY_DENSE_AND_PASS_SEPARABLE"
            if separation
            else "COMBINED_ROLL_RISK_NOT_EARLY_DENSE_AND_SEPARABLE"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "separation_rule_passed": separation,
        "prediction_horizon_s": horizon,
        "combined_passing_risk_maximum_rad": pass_maximum,
        "combined_passing_envelope_rad": envelope,
        "failure_rules": per_failure,
        "failure_summaries": {
            name: summaries[name] for name in failures
        },
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
    failure_text = {
        name: {
            "first": summaries[name]["first_exceedance_tick"],
            "lead": summaries[name]["lead_ticks_to_terminal"],
            "rows": summaries[name]["exceedance_rows"],
        }
        for name in failures
    }
    MARKDOWN.write_text(
        "# T201B roll-risk source-transfer result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Combined passing envelope: `{envelope:.9f}` rad\n"
        f"- Failure first/lead/rows: `{failure_text}`\n"
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
