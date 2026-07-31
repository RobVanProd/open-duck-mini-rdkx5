#!/usr/bin/env python3
"""Audit the frozen T15 x=0 deadband structural question."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t15_x0_deadband_structural_preregistration.json"
)
OUTPUT = ANALYSIS / "t15_x0_deadband_structural_result.json"
MARKDOWN = ANALYSIS / "T15_X0_DEADBAND_STRUCTURAL_RESULT_20260726.md"
EXPECTED_POLICY_FAMILIES = {"V121", "V123", "V128", "V177"}
EXPECTED_FITS = {"p30", "p31_34"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def behavior_signature(behavior: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "samples",
        "termination_reason",
        "mean_local_vx_m_s",
        "minimum_base_height_m",
        "body_pitch_p95_rad",
        "pitch_tracking_p95_rad",
        "left_contact_transitions",
        "right_contact_transitions",
        "action_saturation_pct",
        "p95_rate_excess_rad_s",
        "instant_rate_excess_rad_s",
    )
    return {key: behavior[key] for key in keys}


def trace_actions_are_zero(path: Path) -> tuple[bool, int, str]:
    actions: list[list[float]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            actions.append(row["action"])
    array = np.asarray(actions, dtype=np.float32)
    exact = bool(
        array.ndim == 2
        and array.shape[1] == 14
        and np.array_equal(array, np.zeros_like(array))
    )
    return exact, int(array.shape[0]), hashlib.sha256(array.tobytes()).hexdigest()


def audit() -> dict[str, Any]:
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    t6_path = ANALYSIS / "t6_corrected_robustness_screen_result.json"
    t7_path = ANALYSIS / "t7_universal_response_support_result.json"
    t6 = json.loads(t6_path.read_text(encoding="utf-8"))
    t7 = json.loads(t7_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    for candidate in t6["candidates"]:
        for block in candidate["blocks"]:
            cells = [
                cell
                for cell in block["result"]["cells"]
                if cell["behavior"]["command_x_m_s"] == 0.0
            ]
            if len(cells) != 1:
                raise ValueError("each T6 block must contain exactly one x=0 cell")
            cell = cells[0]
            trace_path = Path(cell["trace"]["path"])
            trace_hash_matches = (
                trace_path.is_file()
                and sha256(trace_path) == cell["trace"]["sha256"]
            )
            exact_zero = False
            action_rows = 0
            action_sha256 = ""
            if trace_hash_matches:
                exact_zero, action_rows, action_sha256 = (
                    trace_actions_are_zero(trace_path)
                )
            rows.append(
                {
                    "policy_family": candidate["candidate_id"],
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "cell_green": cell["cell_green"],
                    "behavior": behavior_signature(cell["behavior"]),
                    "trace_path": str(trace_path),
                    "trace_sha256": cell["trace"]["sha256"],
                    "trace_hash_matches": trace_hash_matches,
                    "action_rows": action_rows,
                    "actions_exact_zero": exact_zero,
                    "action_array_sha256": action_sha256,
                }
            )

    signatures = {
        json.dumps(
            row["behavior"],
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        for row in rows
    }
    per_checkpoint_fit_invariant = True
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(
            (row["policy_family"], row["checkpoint_id"]),
            [],
        ).append(row)
    for pair in grouped.values():
        if len(pair) != 2 or {
            row["fit_id"] for row in pair
        } != EXPECTED_FITS:
            per_checkpoint_fit_invariant = False
            continue
        first, second = pair
        per_checkpoint_fit_invariant &= (
            first["behavior"] == second["behavior"]
            and first["action_array_sha256"]
            == second["action_array_sha256"]
        )

    support_rows = [
        cell
        for cell in t7["cells"]
        if cell["configuration_id"] == "TORSO_COM_X_NEG"
    ]
    support_summary = [
        {
            "fit_id": cell["fit_id"],
            "repeat": cell["repeat"],
            "pass": cell["pass"],
            "mean_local_vx_m_s": cell["metrics"]["mean_local_vx_m_s"],
            "minimum_base_height_m": cell["metrics"]["minimum_base_height_m"],
            "body_pitch_p95_rad": cell["metrics"]["body_pitch_p95_rad"],
            "maximum_sent_rate_excess_rad_s": (
                cell["metrics"]["maximum_sent_rate_excess_rad_s"]
            ),
            "maximum_conservative_rate_excess_rad_s": (
                cell["metrics"]["maximum_conservative_rate_excess_rad_s"]
            ),
            "maximum_overcurrent_run_ticks": (
                cell["metrics"]["maximum_overcurrent_run_ticks"]
            ),
            "maximum_overload_run_ticks": (
                cell["metrics"]["maximum_overload_run_ticks"]
            ),
        }
        for cell in support_rows
    ]

    checks = {
        "preregistration_green": prereg["failed_checks"] == [],
        "bound_t6_result_hash_exact": (
            sha256(t6_path) == prereg["input_hashes"]["t6_result"]
        ),
        "bound_t7_result_hash_exact": (
            sha256(t7_path) == prereg["input_hashes"]["t7_result"]
        ),
        "all_16_t6_x0_cells_present": (
            len(rows) == 16
            and {row["policy_family"] for row in rows}
            == EXPECTED_POLICY_FAMILIES
            and {row["fit_id"] for row in rows} == EXPECTED_FITS
        ),
        "all_16_actions_exact_zero_on_every_recorded_tick": (
            all(
                row["actions_exact_zero"]
                and row["action_rows"] == row["behavior"]["samples"]
                for row in rows
            )
        ),
        "all_16_cells_fail_with_identical_behavior_metrics": (
            all(not row["cell_green"] for row in rows)
            and len(signatures) == 1
        ),
        "each_checkpoint_pair_is_fit_invariant": (
            per_checkpoint_fit_invariant
        ),
        "all_bound_trace_hashes_match_committed_receipts": all(
            row["trace_hash_matches"] for row in rows
        ),
        "all_four_t7_negative_com_support_cells_pass": (
            len(support_rows) == 4
            and all(cell["pass"] for cell in support_rows)
        ),
        "t7_support_mean_abs_vx_at_most_m_s": (
            len(support_rows) == 4
            and max(
                abs(cell["metrics"]["mean_local_vx_m_s"])
                for cell in support_rows
            )
            <= 0.001
        ),
        "t7_support_rate_excess_exact_zero": (
            len(support_rows) == 4
            and all(
                cell["metrics"]["maximum_sent_rate_excess_rad_s"] == 0.0
                and cell["metrics"][
                    "maximum_conservative_rate_excess_rad_s"
                ]
                == 0.0
                for cell in support_rows
            )
        ),
        "t7_support_duration_protection_green": (
            len(support_rows) == 4
            and all(
                cell["metrics"]["maximum_overcurrent_run_ticks"] < 100
                and cell["metrics"]["maximum_overload_run_ticks"] < 100
                for cell in support_rows
            )
        ),
        "new_behavior_cells_zero": True,
        "optimizer_steps_zero": True,
        "hosted_compute_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_T15_X0_DEADBAND_STRUCTURAL_CONTRADICTION"
        if not failed
        else "HOLD_T15_X0_DEADBAND_STRUCTURAL_AUDIT"
    )
    decision = (
        "REOPEN_X0_BRANCH_FOR_CONFIGURATION_AWARE_SUPPORT_RETENTION"
        if not failed
        else "KEEP_UNCONDITIONAL_X0_DEADBAND"
    )
    basis = {
        "schema_version": "open_duck.t15_x0_deadband_structural_result.v1",
        "status": status,
        "decision": decision,
        "failed_checks": failed,
        "checks": checks,
        "preregistered_contract_sha256": (
            prereg["preregistered_contract_sha256"]
        ),
        "t6_x0_rows": rows,
        "t6_unique_behavior_signatures": len(signatures),
        "t7_negative_com_support_rows": support_summary,
        "causal_conclusion": (
            "The negative-COM x=0 failure is invariant to policy family, "
            "checkpoint, and actuator fit because the unconditional deadband "
            "forces exact-zero action. The already-reviewed universal "
            "support action holds the same negative-COM condition. Therefore "
            "the x=0 clearance failure is caused by the branch contract, not "
            "by a missing optimizer objective."
            if not failed
            else "The preregistered structural contradiction was not proven."
        ),
        "scope": {
            "moving_command_mechanisms_reopened": False,
            "training_or_hosted_run_earned": False,
            "x0_cpu_contract_review_earned": not failed,
            "gate5_or_deployment_earned": False,
            "robot_access": False,
        },
        "execution": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    return {**basis, "result_sha256": canonical_sha256(basis)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite T15 result")

    result = audit()
    args.output.write_text(
        json.dumps(
            result,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# T15 x=0 deadband structural audit result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                (
                    "- T6 x=0 cells / unique behavior signatures: "
                    f"`{len(result['t6_x0_rows'])}` / "
                    f"`{result['t6_unique_behavior_signatures']}`"
                ),
                (
                    "- T7 negative-COM universal-support passes: "
                    f"`{sum(row['pass'] for row in result['t7_negative_com_support_rows'])}"
                    f"/{len(result['t7_negative_com_support_rows'])}`"
                ),
                "- New behavior cells / optimizer steps: `0 / 0`",
                "- Hosted compute / robot access: `0 / 0`",
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
                result["causal_conclusion"],
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(args.output.relative_to(ROOT))
    print(args.markdown.relative_to(ROOT))
    print(result["status"])
    print(result["result_sha256"])
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
