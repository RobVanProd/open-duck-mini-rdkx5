#!/usr/bin/env python3
"""Freeze the T178 positive-Z saved-trace causal autopsy."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T177_PREREGISTRATION = (
    ANALYSIS / "t177_head_prefix_mean_full_r2_preregistration.json"
)
T177_RESULT = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"
T177_VERIFIER = ROOT / "tools" / "verify_t177_terminal.py"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t178_positive_z_failure_autopsy.py"
TEST = ROOT / "tests" / "test_t178_positive_z_failure_autopsy.py"
OUTPUT = ANALYSIS / "t178_positive_z_failure_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T178_POSITIVE_Z_FAILURE_AUTOPSY_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
    verify_receipt,
)


EXPECTED_FAILURES = {
    ("T175_HEAD_MEAN_HALF", "p30", 0.077): 457,
    ("T175_HEAD_MEAN_HALF", "p31_34", 0.074): 192,
    ("T175_HEAD_MEAN_HALF", "p31_34", 0.077): 320,
    ("T175_HEAD_MEAN_FINAL", "p30", 0.074): 309,
    ("T175_HEAD_MEAN_FINAL", "p30", 0.077): 529,
}


def _require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T178: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T178 preregistration requires a clean worktree")

    t177_prereg = _load_json(T177_PREREGISTRATION)
    t177_result = _load_json(T177_RESULT)
    _require(
        t177_result.get("status") == "HOLD_T177_HEAD_PREFIX_MEAN_FULL_R2",
        "T177 terminal status differs",
    )
    _require(
        t177_result.get("result_sha256")
        == "59d0d3c73d808ff258e73f9cef0d0ff1734900776ab58c22d59e4ae8ae9219b2",
        "T177 terminal result identity differs",
    )
    _require(
        t177_result["summary"]["completed_conditions"] == 12
        and t177_result["summary"]["completed_cells"] == 192
        and t177_result["summary"]["green_cells"] == 187,
        "T177 terminal accounting differs",
    )

    blocks = [
        block
        for block in t177_result["blocks"]
        if block["condition_id"] == "TORSO_COM_Z_POS"
    ]
    _require(len(blocks) == 4, "positive-Z block population is not four")
    trace_population = []
    observed_failures: dict[tuple[str, str, float], int] = {}
    block_receipts = []
    for block in blocks:
        verify_receipt(
            block["manifest"],
            f"{block['checkpoint_id']}:{block['fit_id']}",
        )
        manifest = _load_json(Path(block["manifest"]["path"]))
        _require(len(manifest["traces"]) == 4, "block trace population is not four")
        cell_by_command = {
            float(cell["command_x_m_s"]): cell for cell in block["result"]["cells"]
        }
        _require(
            sorted(cell_by_command) == [0.0, 0.074, 0.077, 0.08],
            "block commands differ",
        )
        block_receipts.append(
            {
                "checkpoint_id": block["checkpoint_id"],
                "fit_id": block["fit_id"],
                "manifest": block["manifest"],
            }
        )
        for command, trace in zip(
            (0.0, 0.074, 0.077, 0.08),
            manifest["traces"],
            strict=True,
        ):
            verify_receipt(
                trace,
                f"{block['checkpoint_id']}:{block['fit_id']}:{command:.3f}",
            )
            cell = cell_by_command[command]
            behavior = cell["behavior"]
            sample_count = int(behavior["samples"])
            entry = {
                "checkpoint_id": block["checkpoint_id"],
                "fit_id": block["fit_id"],
                "command_x_m_s": command,
                "cell_green": bool(cell["cell_green"]),
                "samples": sample_count,
                "termination_reason": behavior["termination_reason"],
                **trace,
            }
            trace_population.append(entry)
            if not cell["cell_green"]:
                observed_failures[
                    (block["checkpoint_id"], block["fit_id"], command)
                ] = sample_count
    _require(
        observed_failures == EXPECTED_FAILURES,
        f"positive-Z failure matrix differs: {observed_failures}",
    )

    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t177_preregistration": T177_PREREGISTRATION,
        "t177_terminal_result": T177_RESULT,
        "t177_terminal_verifier": T177_VERIFIER,
    }
    _require(
        all(path.is_file() for path in frozen_paths.values()),
        "a frozen T178 input is missing",
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t178_positive_z_failure_autopsy_preregistration.v1"
        ),
        "status": "PREREGISTERED_T178_POSITIVE_Z_FAILURE_AUTOPSY",
        "repository_commit": _git_head(),
        "source_terminal_result_sha256": t177_result["result_sha256"],
        "source_terminal_contract_sha256": t177_result[
            "preregistered_contract_sha256"
        ],
        "matrix": {
            "condition_id": "TORSO_COM_Z_POS",
            "torso_com_offset_m": [0.0, 0.0, 0.05],
            "checkpoint_ids": [
                "T175_HEAD_MEAN_HALF",
                "T175_HEAD_MEAN_FINAL",
            ],
            "fit_ids": ["p30", "p31_34"],
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "trace_count": 16,
            "failed_cells": 5,
            "expected_failures": [
                {
                    "checkpoint_id": checkpoint,
                    "fit_id": fit,
                    "command_x_m_s": command,
                    "samples": samples,
                }
                for (checkpoint, fit, command), samples in sorted(
                    EXPECTED_FAILURES.items()
                )
            ],
        },
        "analysis_contract": {
            "questions": [
                "Are physical, observer, calibration, and recurrent handoff states "
                "exact across commands within every checkpoint/fit block?",
                "Does x=.077 depart nonlinearly from the exact midpoint of "
                "x=.074 and x=.080 over a fixed common stable prefix?",
                "Do the five failures share a tilt, phase, contact, or joint-action "
                "precursor relative to the matched x=.080 pass?",
            ],
            "common_prefix_ticks": 162,
            "common_prefix_basis": (
                "six complete 27-tick gait periods and shorter than the shortest "
                "192-sample failed trace"
            ),
            "gait_period_ticks": 27,
            "prefall_window_ticks": 54,
            "phase_bucket_ticks": 3,
            "failure_onset": {
                "angle_rad": 0.25,
                "height_m": 0.12,
                "rule": (
                    "earliest tick with abs(pitch)>=0.25, abs(roll)>=0.25, "
                    "base_height<0.12, or done; otherwise final recorded tick"
                ),
            },
            "replication_threshold": 4,
            "localized_signature_rule": (
                "dominant tilt/sign replicates in at least 4/5 failures and at "
                "least one of 3-tick phase bucket, exact contact vector, or "
                "largest mean-absolute action-delta joint also replicates 4/5"
            ),
            "matched_pass_command_x_m_s": 0.08,
            "middle_command_test": (
                "x=.077 minus 0.5*(x=.074+x=.080), fieldwise and without fitted "
                "thresholds"
            ),
            "no_threshold_tuning": True,
            "no_raw_trace_was_read_before_this_contract": True,
        },
        "decision_rule": {
            "invalid_trace_or_receipt": "NO_SUCCESSOR_AUTHORIZED",
            "handoff_mismatch": (
                "EARN_CPU_ONLY_HANDOFF_CONTRACT_REPAIR_PREREGISTRATION_ONLY"
            ),
            "handoff_exact_localized_signature": (
                "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
                "PREREGISTRATION_ONLY"
            ),
            "handoff_exact_distributed_signature": (
                "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
                "PREREGISTRATION_ONLY"
            ),
            "why_source_ab": (
                "It is the cheapest exact falsifier for whether the T175 "
                "head-prefix transform introduced the positive-Z regression or "
                "whether the unchanged source policies already contain it."
            ),
            "no_behavior_execution_in_this_task": True,
            "no_post_hoc_metric_or_threshold_selection": True,
        },
        "block_receipts": block_receipts,
        "trace_population": trace_population,
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "saved_traces_read": 16,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "source_vs_transform_cpu_ab_preregistration": True,
            "source_vs_transform_cpu_ab_execution": False,
            "additional_training": False,
            "colab": False,
            "deployment_contract_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T178 positive-Z saved-trace autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: `16` sealed T177 positive-Z JSONL traces\n"
        "- Common prefix: `162` ticks (`6 x 27`)\n"
        "- Pre-fall window: `54` ticks; phase buckets: `3` ticks\n"
        "- Replication rule: `4/5`\n"
        "- New simulation / optimizer / hosted compute / robot: `0/0/0/0`\n"
        "- Raw trace rows were not read before freezing this contract.\n"
        "- A valid exact-handoff result earns only a separately preregistered "
        "CPU source-versus-T175 A/B.\n"
        "- Training, deployment audit, Gate 5, and hardware remain unauthorized.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
