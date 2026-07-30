#!/usr/bin/env python3
"""Run T213B's saved-trace support-continuity autopsy."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t213b_support_continuity_autopsy_preregistration.json"
RESULT = ANALYSIS / "t213b_support_continuity_autopsy_result.json"
MARKDOWN = ANALYSIS / "T213B_SUPPORT_CONTINUITY_AUTOPSY_RESULT_20260730.md"


def maximum_true_run(values: list[bool]) -> tuple[int, int | None]:
    maximum = 0
    maximum_start = None
    start = None
    for index, value in enumerate([*values, False]):
        if value and start is None:
            start = index
        elif not value and start is not None:
            length = index - start
            if length > maximum:
                maximum = length
                maximum_start = start
            start = None
    return maximum, maximum_start


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T213B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T213B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T213B_SUPPORT_CONTINUITY_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T213B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    loaded = []
    passing_risks = []
    for item in prereg["traces"]:
        rows = read_trace(Path(item["trace"]["path"]))
        ticks = [int(row["tick"]) for row in rows]
        risk = [
            abs(
                float(row["body_roll_rad"])
                + 0.08 * float(row["body_roll_rate_rad_s"])
            )
            for row in rows
        ]
        support_loss = [
            [int(value) for value in row["foot_contacts"]] == [0, 0]
            for row in rows
        ]
        run, run_start = maximum_true_run(support_loss)
        loaded.append(
            {
                **item,
                "rows": rows,
                "ticks_contiguous": ticks == list(range(len(rows))),
                "risk": risk,
                "maximum_support_loss_run_ticks": run,
                "maximum_support_loss_run_start_tick": run_start,
                "support_loss_ticks": sum(support_loss),
            }
        )
        if item["cell_green"]:
            passing_risks.extend(risk)
    current_envelope = math.nextafter(max(passing_risks), math.inf)
    frozen_envelope = float(
        prereg["signals"]["frozen_t201_envelope_rad"]
    )
    summaries = []
    for item in loaded:
        rows = item.pop("rows")
        risk = item.pop("risk")
        current_exceed = [
            index for index, value in enumerate(risk)
            if value > current_envelope
        ]
        frozen_exceed = [
            index for index, value in enumerate(risk)
            if value > frozen_envelope
        ]
        summaries.append(
            {
                **item,
                "maximum_roll_risk_rad": max(risk),
                "current_envelope_exceedance_rows": len(current_exceed),
                "current_envelope_first_exceedance_tick": (
                    current_exceed[0] if current_exceed else None
                ),
                "current_envelope_terminal_lead_ticks": (
                    len(rows) - 1 - current_exceed[0]
                    if current_exceed else None
                ),
                "frozen_envelope_exceedance_rows": len(frozen_exceed),
                "frozen_envelope_first_exceedance_tick": (
                    frozen_exceed[0] if frozen_exceed else None
                ),
                "frozen_envelope_terminal_lead_ticks": (
                    len(rows) - 1 - frozen_exceed[0]
                    if frozen_exceed else None
                ),
                "base_height_m": [float(row["base_height_m"]) for row in rows],
            }
        )
    failures = [row for row in summaries if not row["cell_green"]]
    passes = [row for row in summaries if row["cell_green"]]
    failure = failures[0]
    failure_start = int(failure["maximum_support_loss_run_start_tick"])
    failure_heights = failure.pop("base_height_m")
    post_support_heights = failure_heights[failure_start:]
    strict_height_collapse = all(
        right < left
        for left, right in zip(
            post_support_heights,
            post_support_heights[1:],
        )
    )
    for row in passes:
        row.pop("base_height_m")
    pass_support_maximum = max(
        row["maximum_support_loss_run_ticks"] for row in passes
    )
    terminal_tick = int(failure["samples"]) - 1
    support_lead = terminal_tick - failure_start
    current_first = int(
        failure["current_envelope_first_exceedance_tick"]
    )
    frozen_first = int(failure["frozen_envelope_first_exceedance_tick"])
    checks = {
        "all_trace_ticks_contiguous_and_sample_counts_exact": all(
            row["ticks_contiguous"]
            and row["samples"]
            == (
                600 if row["cell_green"] else failure["samples"]
            )
            for row in summaries
        ),
        "exactly_fifteen_passes_one_failure": (
            len(passes) == 15 and len(failures) == 1
        ),
        "failure_support_run_strictly_exceeds_every_pass": (
            failure["maximum_support_loss_run_ticks"]
            > pass_support_maximum
        ),
        "failure_support_run_at_least_two_ticks": (
            failure["maximum_support_loss_run_ticks"] >= 2
        ),
        "failure_support_loss_has_frozen_minimum_lead": (
            support_lead
            >= int(
                prereg["signals"][
                    "failure_support_lead_required_ticks"
                ]
            )
        ),
        "height_strictly_collapses_after_anomalous_support_loss": (
            strict_height_collapse
        ),
        "current_pass_envelope_crosses_after_support_loss": (
            current_first > failure_start
        ),
        "frozen_t201_envelope_crosses_after_support_loss": (
            frozen_first > failure_start
        ),
        "current_pass_envelope_is_terminal_late": (
            failure["current_envelope_terminal_lead_ticks"]
            <= int(prereg["signals"]["late_roll_lead_maximum_ticks"])
        ),
        "frozen_t201_envelope_is_terminal_late": (
            failure["frozen_envelope_terminal_lead_ticks"]
            <= int(prereg["signals"]["late_roll_lead_maximum_ticks"])
        ),
        "every_pass_stays_inside_current_envelope": all(
            row["current_envelope_exceedance_rows"] == 0 for row in passes
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    for row in summaries:
        row.pop("trace")
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t213b_support_continuity_autopsy_result.v1"
        ),
        "status": (
            "PASS_T213B_SUPPORT_CONTINUITY_AUTOPSY"
            if not failed
            else "HOLD_T213B_SUPPORT_CONTINUITY_AUTOPSY"
        ),
        "decision": (
            "EARN_T214B_SUPPORT_CONTINUITY_CURRICULUM_"
            "CPU_FALSIFIER_PREREGISTRATION_ONLY"
            if not failed
            else "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_CURRICULUM"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "current_pass_envelope_rad": current_envelope,
        "frozen_t201_envelope_rad": frozen_envelope,
        "pass_support_loss_maximum_run_ticks": pass_support_maximum,
        "failure": {
            **failure,
            "support_loss_terminal_lead_ticks": support_lead,
            "height_at_support_loss_start_m": post_support_heights[0],
            "terminal_height_m": post_support_heights[-1],
            "height_strictly_decreasing_to_terminal": strict_height_collapse,
        },
        "traces": summaries,
        "classification": (
            "SUPPORT_CONTINUITY_BREAK_PRECEDES_HEIGHT_AND_ROLL_COLLAPSE"
            if not failed
            else "UNRESOLVED_T210_NOMINAL_FAILURE"
        ),
        "execution": {
            "saved_trace_rows": sum(row["samples"] for row in summaries),
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "support_curriculum_cpu_preregistration": not failed,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T213B support-continuity autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Pass/failure maximum no-contact run: "
        f"`{pass_support_maximum}/"
        f"{failure['maximum_support_loss_run_ticks']}` ticks\n"
        f"- Failure support-loss / roll-risk first ticks: "
        f"`{failure_start}/{current_first}`\n"
        f"- Roll-risk terminal lead: "
        f"`{failure['current_envelope_terminal_lead_ticks']}` ticks\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
