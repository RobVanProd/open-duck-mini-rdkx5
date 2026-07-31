#!/usr/bin/env python3
"""Run T194's read-only support-credit autopsy."""

from __future__ import annotations

import argparse
import importlib.util
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


PREREG = ANALYSIS / "t199_t194_support_credit_autopsy_preregistration.json"
RESULT = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
MARKDOWN = ANALYSIS / "T199_T194_SUPPORT_CREDIT_AUTOPSY_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{checkpoint}_{item['fit_id']}_x{command}"


def load_reference_motion(
    module_path: Path,
    polynomial_path: Path,
) -> Any:
    spec = importlib.util.spec_from_file_location(
        "t199_poly_reference_motion_numpy",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PolyReferenceMotion(str(polynomial_path))


def support_class(contact: np.ndarray) -> str:
    pair = tuple(bool(value) for value in contact)
    return {
        (True, False): "left",
        (False, True): "right",
        (True, True): "double",
        (False, False): "flight",
    }[pair]


def maximum_run(values: list[bool]) -> int:
    best = 0
    current = 0
    for value in values:
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def support_profile(
    rows: list[dict[str, Any]],
    prm: Any,
    *,
    contact_slice: list[int],
    phase_slice: list[int],
    reference_slice: list[int],
    aligned_ticks: list[int],
    terminal_window: int,
) -> dict[str, Any]:
    contact_start, contact_stop = contact_slice
    phase_start, phase_stop = phase_slice
    ref_start, ref_stop = reference_slice
    phase_table = np.asarray(
        [
            [
                np.cos(index / prm.nb_steps_in_period * 2.0 * np.pi),
                np.sin(index / prm.nb_steps_in_period * 2.0 * np.pi),
            ]
            for index in range(prm.nb_steps_in_period)
        ],
        dtype=np.float64,
    )
    records = []
    maximum_phase_error = 0.0
    contacts_binary = True
    for row in rows:
        observation = np.asarray(row["obs_state"], np.float64)
        contact_values = observation[contact_start:contact_stop]
        contacts_binary &= bool(
            np.all((contact_values == 0.0) | (contact_values == 1.0))
        )
        observed = contact_values > 0.5
        phase = observation[phase_start:phase_stop]
        distances = np.max(np.abs(phase_table - phase[None, :]), axis=1)
        phase_index = int(np.argmin(distances))
        phase_error = float(distances[phase_index])
        maximum_phase_error = max(maximum_phase_error, phase_error)
        command = np.asarray(row["command"], np.float64)
        reference = np.asarray(
            prm.get_reference_motion(
                float(command[0]),
                float(command[1]),
                float(command[2]),
                phase_index,
            ),
            np.float64,
        )
        requested = reference[ref_start:ref_stop] > 0.5
        observed_class = support_class(observed)
        requested_class = support_class(requested)
        reference_single = requested_class in {"left", "right"}
        exact_match = reference_single and observed_class == requested_class
        mismatch = reference_single and not exact_match
        records.append(
            {
                "tick": int(row["tick"]),
                "phase_index": phase_index,
                "observed": observed_class,
                "requested": requested_class,
                "reference_single": reference_single,
                "exact_match_credit": exact_match,
                "zero_credit": not exact_match,
                "single_support_mismatch": mismatch,
            }
        )

    def census(selected: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(selected)
        zero = [row["zero_credit"] for row in selected]
        mismatch = [row["single_support_mismatch"] for row in selected]
        return {
            "rows": count,
            "zero_credit_rows": int(sum(zero)),
            "zero_credit_fraction": (
                float(sum(zero) / count) if count else None
            ),
            "maximum_contiguous_zero_credit_rows": maximum_run(zero),
            "reference_single_support_rows": int(
                sum(row["reference_single"] for row in selected)
            ),
            "single_support_mismatch_rows": int(sum(mismatch)),
            "maximum_contiguous_single_support_mismatch_rows": maximum_run(
                mismatch
            ),
            "exact_match_credit_rows": int(
                sum(row["exact_match_credit"] for row in selected)
            ),
            "observed_counts": {
                name: sum(row["observed"] == name for row in selected)
                for name in ("left", "right", "double", "flight")
            },
            "requested_counts": {
                name: sum(row["requested"] == name for row in selected)
                for name in ("left", "right", "double", "flight")
            },
        }

    lo, hi = aligned_ticks
    aligned = [row for row in records if lo <= row["tick"] <= hi]
    tail = records[-terminal_window:]
    return {
        "rows": len(records),
        "period_ticks": int(prm.nb_steps_in_period),
        "maximum_phase_reconstruction_error": maximum_phase_error,
        "policy_contacts_binary": contacts_binary,
        "all": census(records),
        "aligned_ticks_inclusive": [lo, hi],
        "aligned": census(aligned),
        "terminal_window_ticks": terminal_window,
        "terminal": census(tail),
        "terminal_contact": records[-1]["observed"],
        "terminal_reference_request": records[-1]["requested"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T199 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T199 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T199_T194_SUPPORT_CREDIT_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T199 preregistration changed")
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
        for name in (
            "half_p31_34_x0p077",
            "final_p31_34_x0p077",
        )
    }
    dynamics = {
        "half_vs_final_p31_34_x0p077": paired_dynamics(
            trace_rows["half_p31_34_x0p077"],
            trace_rows["final_p31_34_x0p077"],
        ),
        "half_p31_34_vs_p30_x0p077": paired_dynamics(
            trace_rows["half_p31_34_x0p077"],
            trace_rows["half_p30_x0p077"],
        ),
    }
    terminals = {
        name: terminal_summary(rows)
        for name, rows in trace_rows.items()
    }
    prm = load_reference_motion(
        Path(
            prereg["frozen_inputs"]["polynomial_module"]["path"]
        ),
        Path(
            prereg["frozen_inputs"]["polynomial_coefficients"]["path"]
        ),
    )
    profiles = {
        name: support_profile(
            rows,
            prm,
            contact_slice=prereg["analysis"]["policy_contact_slice"],
            phase_slice=prereg["analysis"]["policy_phase_slice"],
            reference_slice=prereg["analysis"]["reference_contact_slice"],
            aligned_ticks=prereg["analysis"][
                "aligned_comparison_ticks_inclusive"
            ],
            terminal_window=int(
                prereg["analysis"]["failure_terminal_window_ticks"]
            ),
        )
        for name, rows in trace_rows.items()
    }
    failure_name = "half_p31_34_x0p077"
    comparators = [
        name for name in profiles if name != failure_name
    ]
    failure_profile = profiles[failure_name]
    failure_aligned_zero = failure_profile["aligned"]["zero_credit_rows"]
    comparator_aligned_zero = {
        name: profiles[name]["aligned"]["zero_credit_rows"]
        for name in comparators
    }
    blindness = (
        failure_profile["terminal"][
            "maximum_contiguous_zero_credit_rows"
        ]
        >= int(
            prereg["analysis"]["blindness_rule"][
                "failure_maximum_contiguous_zero_credit_at_least_ticks"
            ]
        )
        and failure_aligned_zero > max(comparator_aligned_zero.values())
        and failure_profile["terminal"][
            "single_support_mismatch_rows"
        ]
        > 0
    )
    checks = {
        "five_trace_row_counts_exact": all(
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
        "all_phase_reconstructions_exact": all(
            row["maximum_phase_reconstruction_error"]
            <= float(prereg["analysis"]["phase_reconstruction_max_error"])
            for row in profiles.values()
        ),
        "all_policy_contacts_binary": all(
            row["policy_contacts_binary"] for row in profiles.values()
        ),
        "reference_period_is_frozen_27_ticks": all(
            row["period_ticks"]
            == int(prereg["analysis"]["gait_period_ticks"])
            for row in profiles.values()
        ),
        "failed_trace_is_308_rows_and_done": (
            terminals[failure_name]["rows"] == 308
            and terminals[failure_name]["done"]
        ),
        "four_comparators_are_full_duration": all(
            terminals[name]["rows"] == 600 for name in comparators
        ),
        "head_difference_changes_failing_trace_actions": (
            cross[failure_name]["changed_rows"] > 0
        ),
        "head_difference_does_not_change_hidden_state": all(
            row["maximum_hidden_delta"] == 0.0 for row in cross.values()
        ),
        "aligned_comparison_has_54_rows_each": all(
            row["aligned"]["rows"] == 54 for row in profiles.values()
        ),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in sessions.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and blindness
    decision = (
        prereg["decision_rule"]["positive_only_blindness_supported"]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t199_t194_support_credit_autopsy_result.v1"
        ),
        "status": (
            "PASS_T199_T194_SUPPORT_CREDIT_AUTOPSY"
            if not failed
            else "HOLD_T199_T194_SUPPORT_CREDIT_AUTOPSY"
        ),
        "classification": (
            "POSITIVE_ONLY_REFERENCE_SUPPORT_CREDIT_BLIND_TO_"
            "TERMINAL_MISMATCH_OCCUPANCY"
            if blindness
            else "T194_FAILURE_NOT_UNIQUELY_EXPLAINED_BY_"
            "SUPPORT_CREDIT_BLINDNESS"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "blindness_rule_passed": blindness,
        "failure": {
            "trace": failure_name,
            "rows": terminals[failure_name]["rows"],
            "aligned_zero_credit_rows": failure_aligned_zero,
            "terminal_zero_credit_maximum_run": failure_profile[
                "terminal"
            ]["maximum_contiguous_zero_credit_rows"],
            "terminal_single_support_mismatch_rows": failure_profile[
                "terminal"
            ]["single_support_mismatch_rows"],
        },
        "comparator_aligned_zero_credit_rows": comparator_aligned_zero,
        "replay": {
            "recorded": recorded,
            "cross_checkpoint": cross,
        },
        "paired_dynamics": dynamics,
        "terminal_summaries": terminals,
        "support_profiles": profiles,
        "execution": {
            "inference_rows": (
                sum(row["rows"] for row in recorded.values())
                + 2 * sum(row["rows"] for row in cross.values())
            ),
            "trace_rows": sum(len(rows) for rows in trace_rows.values()),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "diagnostic_preregistration": earned,
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
    top = cross[failure_name]["joints"][:3]
    MARKDOWN.write_text(
        "# T199 T194 support-credit autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failure aligned zero-credit rows: `{failure_aligned_zero}/54`\n"
        f"- Comparator aligned zero-credit rows: "
        f"`{comparator_aligned_zero}`\n"
        f"- Failure terminal maximum zero-credit run: "
        f"`{value['failure']['terminal_zero_credit_maximum_run']}` ticks\n"
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
