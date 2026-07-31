#!/usr/bin/env python3
"""Run the read-only T173 sole-failure trace autopsy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t174_t173_failure_autopsy_preregistration.json"
RESULT = ANALYSIS / "t174_t173_failure_autopsy_result.json"
MARKDOWN = ANALYSIS / "T174_T173_FAILURE_AUTOPSY_RESULT_20260729.md"
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]


def make_session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def load_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in Path(item["trace"]["path"]).read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    if len(rows) != int(item["samples"]):
        raise RuntimeError(
            f"trace row count changed: {item['trace']['path']}"
        )
    return rows


def feed(row: dict[str, Any], context: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "obs": np.asarray(row["obs_state"], np.float32)[None, :],
        "previous_action": np.asarray(
            row["policy_state_input"]["previous_action"], np.float32
        ),
        "h_in": np.asarray(
            row["policy_state_input"]["h_in"], np.float32
        ),
        "calibration_context": context,
    }


def recorded_outputs(row: dict[str, Any]) -> list[np.ndarray]:
    state = row["policy_state_output"]
    return [
        np.asarray(row["policy_raw_action"], np.float32)[None, :],
        np.asarray(state["h_out"], np.float32),
        np.asarray(state["previous_action_out"], np.float32),
    ]


def replay_trace(
    rows: list[dict[str, Any]],
    session: ort.InferenceSession,
    context: np.ndarray,
) -> dict[str, Any]:
    exact = 0
    maximum_delta = 0.0
    finite = True
    for row in rows:
        actual = session.run(OUTPUT_NAMES, feed(row, context))
        expected = recorded_outputs(row)
        is_exact = all(
            np.array_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
        exact += int(is_exact)
        maximum_delta = max(
            maximum_delta,
            max(
                float(
                    np.max(
                        np.abs(
                            left.astype(np.float64)
                            - right.astype(np.float64)
                        )
                    )
                )
                for left, right in zip(actual, expected, strict=True)
            ),
        )
        finite &= all(np.all(np.isfinite(value)) for value in actual)
    return {
        "rows": len(rows),
        "bit_exact_rows": exact,
        "all_outputs_bit_exact": exact == len(rows),
        "maximum_recorded_output_delta": maximum_delta,
        "all_outputs_finite": bool(finite),
    }


def cross_replay(
    rows: list[dict[str, Any]],
    sessions: dict[str, ort.InferenceSession],
    context: np.ndarray,
    joint_order: list[str],
) -> dict[str, Any]:
    action_deltas = []
    hidden_maximum = 0.0
    previous_action_maximum = 0.0
    changed_rows = 0
    finite = True
    first_changed_tick = None
    for row in rows:
        values = {
            name: session.run(OUTPUT_NAMES, feed(row, context))
            for name, session in sessions.items()
        }
        delta = (
            values["final"][0].astype(np.float64)
            - values["half"][0].astype(np.float64)
        ).reshape(-1)
        action_deltas.append(delta)
        changed = bool(np.any(delta != 0.0))
        changed_rows += int(changed)
        if changed and first_changed_tick is None:
            first_changed_tick = int(row["tick"])
        hidden_maximum = max(
            hidden_maximum,
            float(
                np.max(
                    np.abs(
                        values["final"][1].astype(np.float64)
                        - values["half"][1].astype(np.float64)
                    )
                )
            ),
        )
        previous_action_maximum = max(
            previous_action_maximum,
            float(
                np.max(
                    np.abs(
                        values["final"][2].astype(np.float64)
                        - values["half"][2].astype(np.float64)
                    )
                )
            ),
        )
        finite &= all(
            np.all(np.isfinite(output))
            for outputs in values.values()
            for output in outputs
        )
    matrix = np.asarray(action_deltas, dtype=np.float64)
    joint_rows = [
        {
            "joint": joint,
            "maximum_abs_action_delta": float(
                np.max(np.abs(matrix[:, index]))
            ),
            "rms_action_delta": float(
                np.sqrt(np.mean(np.square(matrix[:, index])))
            ),
            "mean_signed_action_delta": float(np.mean(matrix[:, index])),
            "changed_rows": int(np.count_nonzero(matrix[:, index])),
        }
        for index, joint in enumerate(joint_order)
    ]
    return {
        "rows": len(rows),
        "changed_rows": changed_rows,
        "first_changed_tick": first_changed_tick,
        "maximum_abs_action_delta": float(np.max(np.abs(matrix))),
        "rms_action_delta": float(np.sqrt(np.mean(np.square(matrix)))),
        "maximum_hidden_delta": hidden_maximum,
        "maximum_previous_action_delta": previous_action_maximum,
        "all_outputs_finite": bool(finite),
        "joints": sorted(
            joint_rows,
            key=lambda item: item["rms_action_delta"],
            reverse=True,
        ),
    }


def first_vector_difference(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    field: str,
) -> int | None:
    for index, (a, b) in enumerate(zip(left, right, strict=False)):
        x = np.asarray(a[field])
        y = np.asarray(b[field])
        if not np.array_equal(x, y):
            return index
    return None


def paired_dynamics(
    half_rows: list[dict[str, Any]],
    final_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    count = min(len(half_rows), len(final_rows))
    left = half_rows[:count]
    right = final_rows[:count]
    vector_fields = [
        "action",
        "sent_target_rad",
        "applied_target_rad",
        "actual_position_rad",
        "actuator_force_nm",
        "foot_contacts",
    ]
    first = {
        field: first_vector_difference(left, right, field)
        for field in vector_fields
    }
    scalar_fields = [
        "body_pitch_rad",
        "body_pitch_rate_rad_s",
        "body_roll_rad",
        "body_roll_rate_rad_s",
        "base_height_m",
    ]
    scalar = {}
    for field in scalar_fields:
        a = np.asarray([row[field] for row in left], np.float64)
        b = np.asarray([row[field] for row in right], np.float64)
        difference = np.abs(a - b)
        indices = np.flatnonzero(difference != 0.0)
        scalar[field] = {
            "first_exact_difference_tick": (
                int(indices[0]) if len(indices) else None
            ),
            "maximum_abs_difference": float(np.max(difference)),
        }
    return {
        "tick_aligned_prefix_rows": count,
        "first_vector_difference_tick": first,
        "scalar_differences": scalar,
    }


def terminal_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pitch = np.asarray([row["body_pitch_rad"] for row in rows], np.float64)
    roll = np.asarray([row["body_roll_rad"] for row in rows], np.float64)
    height = np.asarray([row["base_height_m"] for row in rows], np.float64)
    last = rows[-1]
    return {
        "rows": len(rows),
        "last_tick": int(last["tick"]),
        "done": bool(last["done"]),
        "maximum_abs_pitch_rad": float(np.max(np.abs(pitch))),
        "maximum_abs_roll_rad": float(np.max(np.abs(roll))),
        "minimum_base_height_m": float(np.min(height)),
        "last_pitch_rad": float(last["body_pitch_rad"]),
        "last_roll_rad": float(last["body_roll_rad"]),
        "last_base_height_m": float(last["base_height_m"]),
        "last_local_velocity_m_s": last["local_linvel_m_s"],
    }


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    command = f"{float(item['command_x_m_s']):.3f}".replace(".", "p")
    return f"{checkpoint}_{item['fit_id']}_x{command}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T174 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T174 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T174_T173_FAILURE_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T174 preregistration changed")
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
            contexts["p30"],
            prereg["analysis"]["joint_order"],
        )
        for name in ("final_p30_x0p080", "half_p30_x0p080")
    }
    dynamics = paired_dynamics(
        trace_rows["half_p30_x0p080"],
        trace_rows["final_p30_x0p080"],
    )
    terminals = {
        name: terminal_summary(rows)
        for name, rows in trace_rows.items()
    }
    checks = {
        "four_trace_row_counts_exact": all(
            row["rows"] == next(
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
        "head_difference_changes_action_on_both_shared_traces": all(
            row["changed_rows"] > 0 for row in cross.values()
        ),
        "head_difference_does_not_change_hidden_state": all(
            row["maximum_hidden_delta"] == 0.0 for row in cross.values()
        ),
        "failed_trace_is_short_and_done": (
            terminals["final_p30_x0p080"]["rows"] == 281
            and terminals["final_p30_x0p080"]["done"]
        ),
        "three_comparators_are_full_duration": all(
            terminals[name]["rows"] == 600
            for name in (
                "half_p30_x0p080",
                "final_p31_34_x0p080",
                "final_p30_x0p077",
            )
        ),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in sessions.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t174_t173_failure_autopsy_result.v1",
        "status": (
            "PASS_T174_T173_FAILURE_AUTOPSY"
            if not failed
            else "HOLD_T174_T173_FAILURE_AUTOPSY"
        ),
        "decision": (
            "FILE_T174_CAUSAL_AUTOPSY_FOR_MECHANISM_SELECTION"
            if not failed
            else "HOLD_MECHANISM_SELECTION_AND_AUDIT_TRACE_INTEGRITY"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "replay": {
            "recorded": recorded,
            "all_recorded_outputs_bit_exact": checks[
                "all_recorded_outputs_bit_exact"
            ],
            "cross_checkpoint": cross,
        },
        "paired_dynamics": dynamics,
        "terminal_summaries": terminals,
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
            "mechanism_selection": not failed,
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
    top = cross["final_p30_x0p080"]["joints"][:3]
    MARKDOWN.write_text(
        "# T174 T173 failure autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Recorded ONNX replay: bit-exact on every stored row\n"
        f"- Failing-trace head delta: max "
        f"`{cross['final_p30_x0p080']['maximum_abs_action_delta']:.9f}`, "
        f"RMS `{cross['final_p30_x0p080']['rms_action_delta']:.9f}`\n"
        f"- Highest RMS joints: `{[row['joint'] for row in top]}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
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
