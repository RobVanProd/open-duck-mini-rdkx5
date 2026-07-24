#!/usr/bin/env python3
"""Audit how much of V115's intended linear torque price reward clipping removes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v126_exact_oracle_preregistration.json"
PREREG_SHA256 = (
    "6b9e0c45955753f17d78888f4b9004d8bfc73699342828b09d0725183887d307"
)
CONTRACT = ANALYSIS / "winner_v126_exact_oracle_cpu_contract.json"
CONTRACT_SHA256 = (
    "4c54d4178a70f09e85c727f7be2c06cb337640533b0138dd1269af4f6a602756"
)
V115_RESULT = ANALYSIS / "winner_v115_nominal_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v126_v115_linear_price_clipping_audit.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT_20260724.md"
)
THRESHOLD_NM = 1.91229675
SCALE = -307.48131091308585
DT_S = 0.02


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cell_identity(name: str) -> dict[str, Any]:
    checkpoint = "half" if "_half_" in name else "final"
    plant = (
        "P31_34_PITCH_WITH_P30_NONPITCH"
        if "p31_34_pitch_with_p30_nonpitch" in name
        else "P30_ALL_JOINT"
    )
    match = re.search(r"_x([0-9]+\.[0-9]+)_seed([0-9]+)", name)
    if match is None:
        raise ValueError(f"cannot parse V115 trace identity: {name}")
    return {
        "checkpoint": checkpoint,
        "plant": plant,
        "command_x_m_s": float(match.group(1)),
        "seed": int(match.group(2)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V115 price audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    v115_result = json.loads(V115_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or sha256(CONTRACT) != CONTRACT_SHA256
        or prereg.get("authority", {}).get("v115_read_only_audit") is not True
        or contract.get("status")
        != "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT"
        or contract.get("authority", {}).get("v115_read_only_audit") is not True
        or v115_result.get("status")
        != "PASS_WINNER_V115_NOMINAL_BEHAVIOR_VALID_RESULT"
    ):
        raise ValueError("V115 price audit authority or inputs changed")
    trace_root = Path(v115_result["run_root"]) / "traces"
    traces = sorted(trace_root.glob("*.jsonl"))
    if len(traces) != 16:
        raise ValueError(f"expected 16 V115 traces, found {len(traces)}")

    cells: list[dict[str, Any]] = []
    maximum_reward_reconstruction_error = 0.0
    all_rows = 0
    for trace in traces:
        rows = [
            json.loads(line)
            for line in trace.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(rows) != 600:
            raise ValueError(f"V115 trace is not 600 ticks: {trace.name}")
        intended = 0.0
        realized = 0.0
        event_ticks = 0
        zero_realized_event_ticks = 0
        peak_cost = 0.0
        for row in rows:
            force = np.abs(
                np.asarray(row["actuator_force_nm"], dtype=np.float64)
            )
            if force.shape != (14,) or not np.all(np.isfinite(force)):
                raise ValueError(f"invalid V115 force row: {trace.name}")
            cost = float(np.mean(np.maximum(force - THRESHOLD_NM, 0.0)))
            terms = row["reward_terms"]
            base_scaled_sum = sum(
                float(value)
                for key, value in terms.items()
                if str(key).startswith("reward/")
            ) - sum(
                float(value)
                for key, value in terms.items()
                if str(key).startswith("cost/")
            )
            reconstructed_base_reward = float(
                np.clip(base_scaled_sum * DT_S, 0.0, 10000.0)
            )
            observed_reward = float(row["reward"])
            reconstruction_error = abs(
                reconstructed_base_reward - observed_reward
            )
            maximum_reward_reconstruction_error = max(
                maximum_reward_reconstruction_error, reconstruction_error
            )
            intended_tick = abs(SCALE) * cost * DT_S
            with_linear = float(
                np.clip(
                    (base_scaled_sum + SCALE * cost) * DT_S,
                    0.0,
                    10000.0,
                )
            )
            realized_tick = reconstructed_base_reward - with_linear
            intended += intended_tick
            realized += realized_tick
            peak_cost = max(peak_cost, cost)
            if cost > 0.0:
                event_ticks += 1
                if realized_tick <= 1.0e-12:
                    zero_realized_event_ticks += 1
        if maximum_reward_reconstruction_error > 2.0e-6:
            raise ValueError(
                "V115 base reward reconstruction exceeds frozen tolerance"
            )
        removed = intended - realized
        cells.append(
            {
                **cell_identity(trace.name),
                "trace_path": str(trace),
                "trace_sha256": sha256(trace),
                "rows": len(rows),
                "event_ticks": event_ticks,
                "zero_realized_event_ticks": zero_realized_event_ticks,
                "peak_linear_mean_hinge_nm": peak_cost,
                "intended_price": intended,
                "realized_price": realized,
                "removed_price": removed,
                "removed_fraction": (
                    0.0 if intended == 0.0 else removed / intended
                ),
            }
        )
        all_rows += len(rows)
    intended_total = float(sum(cell["intended_price"] for cell in cells))
    realized_total = float(sum(cell["realized_price"] for cell in cells))
    removed_total = intended_total - realized_total
    event_ticks_total = int(sum(cell["event_ticks"] for cell in cells))
    zero_realized_total = int(
        sum(cell["zero_realized_event_ticks"] for cell in cells)
    )
    checks = {
        "sixteen_complete_traces": len(cells) == 16 and all_rows == 9600,
        "base_reward_reconstruction_exact": (
            maximum_reward_reconstruction_error <= 2.0e-6
        ),
        "all_prices_finite_nonnegative": all(
            math.isfinite(float(value)) and float(value) >= -1.0e-10
            for cell in cells
            for value in (
                cell["intended_price"],
                cell["realized_price"],
                cell["removed_price"],
            )
        ),
        "realized_never_exceeds_intended": all(
            float(cell["realized_price"])
            <= float(cell["intended_price"]) + 1.0e-8
            for cell in cells
        ),
        "read_only_training_steps_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "winner_v126.v115_linear_price_clipping_audit.v1",
        "status": (
            "PASS_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
            if not failed
            else "HOLD_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "definition": {
            "threshold_nm": THRESHOLD_NM,
            "scale": SCALE,
            "dt_s": DT_S,
            "cost": "mean_j max(0, abs(tau_j)-threshold)",
            "price_counterfactual": (
                "remove only the linear cost from the reconstructed scaled "
                "reward sum, then compare clipped reward with and without it"
            ),
        },
        "summary": {
            "cells": len(cells),
            "rows": all_rows,
            "event_ticks": event_ticks_total,
            "zero_realized_event_ticks": zero_realized_total,
            "zero_realized_event_fraction": (
                0.0
                if event_ticks_total == 0
                else zero_realized_total / event_ticks_total
            ),
            "intended_price": intended_total,
            "realized_price": realized_total,
            "removed_price": removed_total,
            "removed_fraction": (
                0.0
                if intended_total == 0.0
                else removed_total / intended_total
            ),
            "maximum_base_reward_reconstruction_error": (
                maximum_reward_reconstruction_error
            ),
        },
        "cells": cells,
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "cpu_contract": sha256(CONTRACT),
            "v115_result": sha256(V115_RESULT),
            "runner": sha256(Path(__file__).resolve()),
        },
        "authority": {
            "selection_weight": 0,
            "formal_oracle_screen_unchanged": True,
            "training": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "gate5": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = payload["summary"]
    MARKDOWN.write_text(
        "# Winner-v126 V115 linear-price clipping audit\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Torque-exceedance event ticks: `{summary['event_ticks']}`.\n\n"
        f"Intended price: `{summary['intended_price']:.9f}`.\n\n"
        f"Realized price after reward clipping: "
        f"`{summary['realized_price']:.9f}`.\n\n"
        f"Removed by clipping: `{summary['removed_fraction']:.6%}`.\n\n"
        f"Event ticks with zero realized price: "
        f"`{summary['zero_realized_event_ticks']}` "
        f"(`{summary['zero_realized_event_fraction']:.6%}`).\n\n"
        "This is a read-only counterfactual audit with zero selection weight. "
        "It authorizes no training, hosted compute, Gate 5, RDK-X5, robot, "
        "torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "summary": summary,
                "output_sha256": sha256(OUTPUT),
            }
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
