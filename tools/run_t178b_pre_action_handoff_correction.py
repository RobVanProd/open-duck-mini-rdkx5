#!/usr/bin/env python3
"""Correct T178 handoff attribution using only true pre-action fields."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t178b_pre_action_handoff_correction_preregistration.json"
)
RESULT = ANALYSIS / "t178b_pre_action_handoff_correction_result.json"
MARKDOWN = (
    ANALYSIS / "T178B_PRE_ACTION_HANDOFF_CORRECTION_RESULT_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


class T178BCorrectionError(RuntimeError):
    """The frozen T178B pre-action correction contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T178BCorrectionError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def _finite_vector(value: Any, length: int, label: str) -> list[float]:
    _require(
        isinstance(value, list) and len(value) == length,
        f"{label} is not length {length}",
    )
    result = [float(item) for item in value]
    _require(all(math.isfinite(item) for item in result), f"{label} is nonfinite")
    return result


def extract_pre_action_handoff(
    row: Mapping[str, Any],
    *,
    applied_target_slice: Sequence[int] = (83, 97),
) -> dict[str, Any]:
    start, stop = (int(item) for item in applied_target_slice)
    _require(int(row.get("tick", -1)) == 0, "handoff row is not tick zero")
    obs = _finite_vector(row.get("obs_state"), 115, "obs_state")
    actual_pre = _finite_vector(
        row.get("actual_position_pre_rad"), 14, "actual_position_pre_rad"
    )
    context = row.get("policy_calibration_context_sha256")
    _require(isinstance(context, str) and len(context) == 64, "context SHA missing")
    policy_state = row.get("policy_state_input")
    _require(isinstance(policy_state, dict), "policy_state_input is not an object")
    _require(stop - start == 14, "applied-target slice is not length 14")
    return {
        "policy_calibration_context_sha256": context,
        "policy_state_input_sha256": canonical_sha256(policy_state),
        "actual_position_pre_rad": actual_pre,
        "phase_observation": obs[0:2],
        "applied_target_observation_rad": obs[start:stop],
    }


def compare_handoff_group(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    fields = (
        "policy_calibration_context_sha256",
        "policy_state_input_sha256",
        "actual_position_pre_rad",
        "phase_observation",
        "applied_target_observation_rad",
    )
    checks = {
        field: len({canonical_sha256(row[field]) for row in rows}) == 1
        for field in fields
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "field_sha256": {
            field: sorted({canonical_sha256(row[field]) for row in rows})
            for field in fields
        },
    }


def _read_tick_zero(
    trace: Mapping[str, Any],
    *,
    applied_target_slice: Sequence[int],
) -> dict[str, Any]:
    verify_receipt(
        trace,
        f"trace:{trace['checkpoint_id']}:{trace['fit_id']}:"
        f"{float(trace['command_x_m_s']):.3f}",
    )
    path = Path(trace["path"])
    with path.open("r", encoding="utf-8") as stream:
        line = stream.readline()
    _require(bool(line), f"empty trace: {path}")
    try:
        row = json.loads(line)
    except json.JSONDecodeError as exc:
        raise T178BCorrectionError(f"invalid first row: {path}") from exc
    command = _finite_vector(row.get("command"), 7, "command")
    expected = float(trace["command_x_m_s"])
    _require(
        command == [expected, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        f"tick-zero command differs: {path}",
    )
    return {
        "checkpoint_id": trace["checkpoint_id"],
        "fit_id": trace["fit_id"],
        "command_x_m_s": expected,
        "trace_sha256": trace["sha256"],
        **extract_pre_action_handoff(
            row, applied_target_slice=applied_target_slice
        ),
    }


def _markdown(value: Mapping[str, Any]) -> str:
    lines = [
        "# T178B pre-action handoff field correction",
        "",
        f"- Status: `{value['status']}`",
        f"- Decision: `{value['decision']}`",
        f"- All four handoff blocks exact: `{value['all_blocks_exact']}`",
        "- Tick-zero rows read: `16`; all other rows read: `0`",
        "- New simulation / optimizer / hosted compute / robot: `0/0/0/0`",
        "",
        "| Checkpoint | Fit | Exact |",
        "|---|---|---:|",
    ]
    for block in value["blocks"]:
        lines.append(
            f"| {block['checkpoint_id']} | {block['fit_id']} | "
            f"{block['all_checks_pass']} |"
        )
    lines.extend(
        [
            "",
            "The original T178 handoff mismatch was an analyzer provenance "
            "error: current-action/post-step outputs were compared as though "
            "they were handoff inputs. T178B compares only true pre-action "
            "fields.",
            "",
            "A pass earns only a separately preregistered CPU-only "
            "source-versus-T175 positive-Z A/B. It does not authorize that "
            "execution, training, Colab, deployment, Gate 5, or hardware.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
) -> dict[str, Any]:
    _require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    _require(not markdown_path.exists(), f"refusing to overwrite: {markdown_path}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T178B execution requires committed clean preregistration",
    )
    preregistration = _load_json(preregistration_path)
    _require(
        preregistration.get("status")
        == "PREREGISTERED_T178B_PRE_ACTION_HANDOFF_CORRECTION",
        "unexpected T178B preregistration status",
    )
    _require(
        _canonical_without(preregistration, "preregistered_contract_sha256")
        == preregistration.get("preregistered_contract_sha256"),
        "T178B preregistration hash differs",
    )
    for label, item in preregistration["frozen_inputs"].items():
        verify_receipt(item, label)
    rows = [
        _read_tick_zero(
            trace,
            applied_target_slice=preregistration["field_contract"][
                "applied_target_observation_slice"
            ],
        )
        for trace in preregistration["trace_population"]
    ]
    _require(len(rows) == 16, "T178B did not read exactly sixteen tick-zero rows")
    blocks = []
    for checkpoint_id in preregistration["matrix"]["checkpoint_ids"]:
        for fit_id in preregistration["matrix"]["fit_ids"]:
            group = [
                row
                for row in rows
                if row["checkpoint_id"] == checkpoint_id
                and row["fit_id"] == fit_id
            ]
            _require(len(group) == 4, "T178B block does not contain four commands")
            blocks.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "fit_id": fit_id,
                    **compare_handoff_group(group),
                }
            )
    all_exact = all(block["all_checks_pass"] for block in blocks)
    if all_exact:
        status = "PASS_T178B_PRE_ACTION_HANDOFF_EXACT"
        decision = (
            "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
            "PREREGISTRATION_ONLY"
        )
    else:
        status = "HOLD_T178B_TRUE_PRE_ACTION_HANDOFF_MISMATCH"
        decision = "NO_BEHAVIOR_SUCCESSOR_AUTHORIZED"
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t178b_pre_action_handoff_correction_result.v1"
        ),
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": preregistration[
            "preregistered_contract_sha256"
        ],
        "all_blocks_exact": all_exact,
        "blocks": blocks,
        "preserved_t178_failure_classification": {
            "dominant_tilt": "pitch_positive",
            "dominant_tilt_replicates": 5,
            "localized_shared_signature": False,
            "classification": "DISTRIBUTED_CLOSED_LOOP_BALANCE_BIFURCATION",
        },
        "execution": {
            "tick_zero_rows_read": 16,
            "other_trace_rows_read": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": preregistration["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    result_path.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        _markdown(basis), encoding="utf-8", newline="\n"
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    result = run(args.preregistration, args.result, args.markdown)
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
