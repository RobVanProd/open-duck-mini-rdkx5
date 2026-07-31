#!/usr/bin/env python3
"""Run T186's read-only failure-exchange autopsy."""

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
    cross_replay,
    load_rows,
    make_session,
    paired_dynamics,
    replay_trace,
    terminal_summary,
)


PREREG = ANALYSIS / "t191_t186_failure_exchange_autopsy_preregistration.json"
RESULT = ANALYSIS / "t191_t186_failure_exchange_autopsy_result.json"
MARKDOWN = ANALYSIS / "T191_T186_FAILURE_EXCHANGE_AUTOPSY_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{checkpoint}_{item['fit_id']}_x{command}"


def support_summary(
    rows: list[dict[str, Any]],
    terminal_window: int,
) -> dict[str, Any]:
    single = [
        index
        for index, row in enumerate(rows)
        if list(row["foot_contacts"]) in ([True, False], [False, True])
    ]
    last_index = single[-1] if single else None
    side = None
    if last_index is not None:
        side = (
            "left"
            if list(rows[last_index]["foot_contacts"]) == [True, False]
            else "right"
        )
    tail = rows[-terminal_window:]
    tail_single = sum(
        list(row["foot_contacts"]) in ([True, False], [False, True])
        for row in tail
    )
    return {
        "last_single_support_tick": (
            int(rows[last_index]["tick"]) if last_index is not None else None
        ),
        "last_single_support_side": side,
        "ticks_from_last_single_support_to_terminal": (
            int(rows[-1]["tick"] - rows[last_index]["tick"])
            if last_index is not None
            else None
        ),
        "terminal_contact": list(rows[-1]["foot_contacts"]),
        "terminal_window_rows": len(tail),
        "terminal_window_single_support_fraction": (
            float(tail_single / len(tail)) if tail else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T191 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T191 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T191 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for name, item in prereg["graphs"].items():
        verify(item, f"graphs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    started = time.time()
    sessions = {
        name: make_session(Path(item["path"]))
        for name, item in prereg["graphs"].items()
    }
    contexts = {
        fit: np.asarray(item["context"], np.float32).reshape(1, 64)
        for fit, item in prereg["contexts"].items()
    }
    trace_rows = {
        label(item): load_rows(item) for item in prereg["traces"]
    }
    recorded = {}
    for item in prereg["traces"]:
        name = label(item)
        graph_name = (
            "half" if item["checkpoint_id"].endswith("HALF") else "final"
        )
        recorded[name] = replay_trace(
            trace_rows[name],
            sessions[graph_name],
            contexts[item["fit_id"]],
        )
    cross = {
        name: cross_replay(
            trace_rows[name],
            sessions,
            contexts["p31_34"],
            prereg["analysis"]["joint_order"],
        )
        for name in ("half_p31_34_x0p080", "final_p31_34_x0p080")
    }
    dynamics = paired_dynamics(
        trace_rows["half_p31_34_x0p080"],
        trace_rows["final_p31_34_x0p080"],
    )
    terminals = {
        name: terminal_summary(rows)
        for name, rows in trace_rows.items()
    }
    supports = {
        name: support_summary(
            rows,
            int(prereg["analysis"]["terminal_window_ticks"]),
        )
        for name, rows in trace_rows.items()
    }
    failure_support = supports["half_p31_34_x0p080"]
    support_proximal = (
        failure_support["ticks_from_last_single_support_to_terminal"]
        is not None
        and failure_support["ticks_from_last_single_support_to_terminal"]
        <= int(prereg["analysis"]["gait_period_ticks"])
    )
    state_compatible = (
        cross["half_p31_34_x0p080"]["changed_rows"] > 0
        and cross["half_p31_34_x0p080"]["maximum_hidden_delta"] == 0.0
        and cross["half_p31_34_x0p080"]["all_outputs_finite"]
    )
    last_tick = terminals["half_p31_34_x0p080"]["last_tick"]
    switch_tick = last_tick - (
        int(prereg["analysis"]["gait_period_ticks"]) - 1
    )
    checks = {
        "four_trace_row_counts_exact": all(
            row["rows"]
            == next(
                item["samples"]
                for item in prereg["traces"]
                if label(item) == name
            )
            for name, row in recorded.items()
        ),
        "all_recorded_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in recorded.values()
        ),
        "all_recorded_and_cross_outputs_finite": (
            all(row["all_outputs_finite"] for row in recorded.values())
            and all(row["all_outputs_finite"] for row in cross.values())
        ),
        "head_difference_changes_failing_trace_actions": (
            cross["half_p31_34_x0p080"]["changed_rows"] > 0
        ),
        "head_difference_does_not_change_hidden_state": all(
            row["maximum_hidden_delta"] == 0.0 for row in cross.values()
        ),
        "new_failed_trace_is_547_rows_and_done": (
            terminals["half_p31_34_x0p080"]["rows"] == 547
            and terminals["half_p31_34_x0p080"]["done"]
        ),
        "three_new_comparators_are_full_duration": all(
            terminals[name]["rows"] == 600
            for name in (
                "final_p31_34_x0p080",
                "half_p30_x0p080",
                "final_p30_x0p080",
            )
        ),
        "derived_switch_tick_is_nonnegative": switch_tick >= 0,
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in sessions.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and support_proximal and state_compatible
    decision = (
        prereg["decision_rule"]["support_proximal_and_state_compatible"]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t191_t186_failure_exchange_autopsy_result.v1"
        ),
        "status": (
            "PASS_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
            if not failed
            else "HOLD_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
        ),
        "classification": (
            "RESET_SUPPORT_CURRICULUM_SHIFTED_BUT_DID_NOT_ELIMINATE_"
            "LOCOMOTION_SUPPORT_COLLAPSE"
            if support_proximal
            else "FAILURE_NOT_SUPPORT_PROXIMAL"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "prior_t170_failure": {
            "checkpoint": "final",
            "fit_id": "p30",
            "command_x_m_s": 0.080,
            "rows": 281,
        },
        "new_t186_failure": {
            "checkpoint": "half",
            "fit_id": "p31_34",
            "command_x_m_s": 0.080,
            "rows": 547,
            "support_proximal": support_proximal,
            "state_compatible_head_change": state_compatible,
            "derived_one_period_switch_tick": switch_tick,
        },
        "replay": {
            "recorded": recorded,
            "cross_checkpoint": cross,
        },
        "paired_dynamics": dynamics,
        "terminal_summaries": terminals,
        "support_summaries": supports,
        "execution": {
            "inference_rows": (
                sum(row["rows"] for row in recorded.values())
                + 2 * sum(row["rows"] for row in cross.values())
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "head_switch_preregistration": earned,
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
    top = cross["half_p31_34_x0p080"]["joints"][:3]
    MARKDOWN.write_text(
        "# T191 T186 failure-exchange autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- New failure rows: `547`; derived switch tick: `{switch_tick}`\n"
        f"- Last single support to terminal: "
        f"`{failure_support['ticks_from_last_single_support_to_terminal']}` "
        "ticks\n"
        f"- Highest half/final RMS action-delta joints: "
        f"`{[row['joint'] for row in top]}`\n"
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
