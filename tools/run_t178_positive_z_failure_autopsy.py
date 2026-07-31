#!/usr/bin/env python3
"""Run the preregistered saved-trace autopsy of T177 positive-Z failures."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t178_positive_z_failure_autopsy_preregistration.json"
)
RESULT = ANALYSIS / "t178_positive_z_failure_autopsy_result.json"
MARKDOWN = ANALYSIS / "T178_POSITIVE_Z_FAILURE_AUTOPSY_RESULT_20260730.md"

sys.path.insert(0, str(ROOT / "tools"))
from actuator_bridge_model import JOINT_NAMES  # noqa: E402
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


class T178AutopsyError(RuntimeError):
    """The frozen T178 saved-trace analysis contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T178AutopsyError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def _vector(value: Any, length: int, label: str) -> list[float]:
    _require(
        isinstance(value, list) and len(value) == length,
        f"{label} is not length {length}",
    )
    result = [float(item) for item in value]
    _require(all(math.isfinite(item) for item in result), f"{label} is nonfinite")
    return result


def _state_digest(value: Any) -> str:
    return canonical_sha256(value)


def _read_projection(
    trace: Mapping[str, Any],
    expected_command: float,
    expected_samples: int,
) -> dict[str, Any]:
    verify_receipt(trace, f"trace:{trace['checkpoint_id']}:{trace['fit_id']}:"
                   f"{expected_command:.3f}")
    path = Path(trace["path"])
    columns: dict[str, list[Any]] = {
        "action": [],
        "sent": [],
        "applied": [],
        "actual": [],
        "actual_pre": [],
        "tracking": [],
        "force": [],
        "rate_excess": [],
        "pitch": [],
        "roll": [],
        "pitch_rate": [],
        "roll_rate": [],
        "height": [],
        "contacts": [],
        "done": [],
    }
    first: dict[str, Any] | None = None
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise T178AutopsyError(
                    f"invalid trace JSON: {path}:{line_number}"
                ) from exc
            _require(
                int(row.get("tick", -1)) == line_number - 1,
                f"noncontiguous tick: {path}:{line_number}",
            )
            command = _vector(row.get("command"), 7, "command")
            _require(
                command == [expected_command, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                f"command differs: {path}:{line_number}",
            )
            if first is None:
                first = {
                    "policy_calibration_context_sha256": row.get(
                        "policy_calibration_context_sha256"
                    ),
                    "policy_state_input_sha256": _state_digest(
                        row.get("policy_state_input")
                    ),
                    "actual_position_pre_rad": _vector(
                        row.get("actual_position_pre_rad"),
                        14,
                        "actual_position_pre_rad",
                    ),
                    "applied_target_rad": _vector(
                        row.get("applied_target_rad"),
                        14,
                        "applied_target_rad",
                    ),
                    "qpos_sha256": _state_digest(row.get("qpos")),
                    "qvel_sha256": _state_digest(row.get("qvel")),
                    "obs_state_dim": len(row.get("obs_state") or []),
                    "obs_state_sha256": _state_digest(row.get("obs_state")),
                }
            columns["action"].append(_vector(row.get("action"), 14, "action"))
            columns["sent"].append(
                _vector(row.get("sent_target_rad"), 14, "sent_target_rad")
            )
            columns["applied"].append(
                _vector(row.get("applied_target_rad"), 14, "applied_target_rad")
            )
            columns["actual"].append(
                _vector(row.get("actual_position_rad"), 14, "actual_position_rad")
            )
            columns["actual_pre"].append(
                _vector(
                    row.get("actual_position_pre_rad"),
                    14,
                    "actual_position_pre_rad",
                )
            )
            columns["tracking"].append(
                _vector(row.get("tracking_error_rad"), 14, "tracking_error_rad")
            )
            columns["force"].append(
                _vector(row.get("actuator_force_nm"), 14, "actuator_force_nm")
            )
            columns["rate_excess"].append(
                _vector(
                    row.get("sent_target_rate_excess_rad_s"),
                    14,
                    "sent_target_rate_excess_rad_s",
                )
            )
            for name, source in (
                ("pitch", "body_pitch_rad"),
                ("roll", "body_roll_rad"),
                ("pitch_rate", "body_pitch_rate_rad_s"),
                ("roll_rate", "body_roll_rate_rad_s"),
                ("height", "base_height_m"),
            ):
                scalar = float(row.get(source))
                _require(
                    math.isfinite(scalar),
                    f"{source} is nonfinite: {path}:{line_number}",
                )
                columns[name].append(scalar)
            contacts = row.get("foot_contacts")
            _require(
                isinstance(contacts, list) and len(contacts) > 0,
                f"foot_contacts missing: {path}:{line_number}",
            )
            columns["contacts"].append(tuple(int(item) for item in contacts))
            columns["done"].append(bool(row.get("done")))

    _require(first is not None, f"empty trace: {path}")
    _require(
        len(columns["done"]) == expected_samples,
        f"sample count differs: {path}",
    )
    _require(first["obs_state_dim"] == 115, f"full 115-D obs missing: {path}")
    return {
        "checkpoint_id": trace["checkpoint_id"],
        "fit_id": trace["fit_id"],
        "command_x_m_s": expected_command,
        "cell_green": bool(trace["cell_green"]),
        "expected_termination_reason": trace["termination_reason"],
        "expected_samples": expected_samples,
        "first": first,
        "samples": expected_samples,
        **{
            key: (
                np.asarray(value, dtype=np.float64)
                if key != "contacts"
                else list(value)
            )
            for key, value in columns.items()
        },
    }


def midpoint_residual_summary(
    low: np.ndarray,
    middle: np.ndarray,
    high: np.ndarray,
    *,
    prefix_ticks: int,
    gait_period_ticks: int,
    joint_names: Sequence[str] = JOINT_NAMES,
) -> dict[str, Any]:
    _require(
        min(len(low), len(middle), len(high)) >= prefix_ticks,
        "midpoint inputs are shorter than frozen prefix",
    )
    residual = (
        middle[:prefix_ticks]
        - 0.5 * (low[:prefix_ticks] + high[:prefix_ticks])
    )
    _require(residual.ndim == 2, "midpoint joint signal is not rank two")
    per_joint_mean_abs = np.mean(np.abs(residual), axis=0)
    flat_index = int(np.argmax(np.abs(residual)))
    tick_index, joint_index = np.unravel_index(flat_index, residual.shape)
    phase_means = []
    for phase in range(gait_period_ticks):
        phase_rows = residual[
            np.arange(prefix_ticks) % gait_period_ticks == phase
        ]
        phase_means.append(np.mean(phase_rows, axis=0).tolist())
    return {
        "prefix_ticks": prefix_ticks,
        "l_inf": float(np.max(np.abs(residual))),
        "rms": float(np.sqrt(np.mean(np.square(residual)))),
        "per_joint_mean_abs": {
            str(joint): float(per_joint_mean_abs[index])
            for index, joint in enumerate(joint_names)
        },
        "maximum": {
            "tick": int(tick_index),
            "phase": int(tick_index % gait_period_ticks),
            "joint": str(joint_names[joint_index]),
            "signed_residual": float(residual[tick_index, joint_index]),
        },
        "phase_mean_residual": phase_means,
    }


def scalar_midpoint_summary(
    low: np.ndarray,
    middle: np.ndarray,
    high: np.ndarray,
    *,
    prefix_ticks: int,
) -> dict[str, float]:
    residual = (
        middle[:prefix_ticks]
        - 0.5 * (low[:prefix_ticks] + high[:prefix_ticks])
    )
    return {
        "l_inf": float(np.max(np.abs(residual))),
        "rms": float(np.sqrt(np.mean(np.square(residual)))),
        "signed_mean": float(np.mean(residual)),
    }


def failure_onset(
    trace: Mapping[str, Any],
    *,
    angle_threshold_rad: float,
    height_threshold_m: float,
) -> tuple[int, list[str]]:
    for tick, (pitch, roll, height, done) in enumerate(
        zip(
            trace["pitch"],
            trace["roll"],
            trace["height"],
            trace["done"],
            strict=True,
        )
    ):
        reasons = []
        if abs(float(pitch)) >= angle_threshold_rad:
            reasons.append("pitch")
        if abs(float(roll)) >= angle_threshold_rad:
            reasons.append("roll")
        if float(height) < height_threshold_m:
            reasons.append("height")
        if bool(done):
            reasons.append("done")
        if reasons:
            return tick, reasons
    return int(trace["samples"]) - 1, ["trace_end_without_threshold"]


def _dominant_tilt(trace: Mapping[str, Any], tick: int) -> str:
    pitch = float(trace["pitch"][tick])
    roll = float(trace["roll"][tick])
    if abs(pitch) >= abs(roll):
        return "pitch_positive" if pitch >= 0.0 else "pitch_negative"
    return "roll_positive" if roll >= 0.0 else "roll_negative"


def _contact_pattern(value: Iterable[int]) -> str:
    return "".join(str(int(item)) for item in value)


def failure_signature(
    failed: Mapping[str, Any],
    matched_x008: Mapping[str, Any],
    *,
    angle_threshold_rad: float,
    height_threshold_m: float,
    gait_period_ticks: int,
    phase_bucket_ticks: int,
    prefall_ticks: int,
    joint_names: Sequence[str] = JOINT_NAMES,
) -> dict[str, Any]:
    onset, onset_reasons = failure_onset(
        failed,
        angle_threshold_rad=angle_threshold_rad,
        height_threshold_m=height_threshold_m,
    )
    start = max(0, onset - prefall_ticks + 1)
    stop = onset + 1
    _require(
        len(matched_x008["action"]) >= stop,
        "matched x=.08 trace does not cover failure window",
    )
    deltas: dict[str, Any] = {}
    for name in ("action", "applied", "actual", "force", "tracking"):
        difference = (
            np.asarray(failed[name][start:stop], dtype=np.float64)
            - np.asarray(matched_x008[name][start:stop], dtype=np.float64)
        )
        per_joint = np.mean(np.abs(difference), axis=0)
        joint_index = int(np.argmax(per_joint))
        deltas[name] = {
            "largest_joint": str(joint_names[joint_index]),
            "largest_mean_abs": float(per_joint[joint_index]),
            "per_joint_mean_abs": {
                str(joint): float(per_joint[index])
                for index, joint in enumerate(joint_names)
            },
        }
    return {
        "checkpoint_id": failed["checkpoint_id"],
        "fit_id": failed["fit_id"],
        "command_x_m_s": float(failed["command_x_m_s"]),
        "samples": int(failed["samples"]),
        "onset_tick": int(onset),
        "onset_reasons": onset_reasons,
        "onset_phase": int(onset % gait_period_ticks),
        "onset_phase_bucket": int(
            (onset % gait_period_ticks) // phase_bucket_ticks
        ),
        "dominant_tilt": _dominant_tilt(failed, onset),
        "contact_pattern": _contact_pattern(failed["contacts"][onset]),
        "prefall_window": {"start_tick": int(start), "stop_tick_exclusive": int(stop)},
        "matched_x008_deltas": deltas,
    }


def replication_summary(
    signatures: Sequence[Mapping[str, Any]],
    *,
    minimum_replicates: int,
) -> dict[str, Any]:
    fields = {
        "dominant_tilt": [row["dominant_tilt"] for row in signatures],
        "onset_phase_bucket": [
            str(row["onset_phase_bucket"]) for row in signatures
        ],
        "contact_pattern": [row["contact_pattern"] for row in signatures],
        "action_precursor_joint": [
            row["matched_x008_deltas"]["action"]["largest_joint"]
            for row in signatures
        ],
    }
    result: dict[str, Any] = {}
    for name, values in fields.items():
        counts = Counter(values)
        value, count = counts.most_common(1)[0]
        result[name] = {
            "modal_value": value,
            "replicates": int(count),
            "threshold": int(minimum_replicates),
            "replicated": bool(count >= minimum_replicates),
            "counts": dict(sorted(counts.items())),
        }
    localized = bool(
        result["dominant_tilt"]["replicated"]
        and (
            result["onset_phase_bucket"]["replicated"]
            or result["contact_pattern"]["replicated"]
            or result["action_precursor_joint"]["replicated"]
        )
    )
    result["localized_shared_signature"] = localized
    return result


def _handoff_summary(
    traces: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    fields = (
        "policy_calibration_context_sha256",
        "policy_state_input_sha256",
        "actual_position_pre_rad",
        "applied_target_rad",
        "qpos_sha256",
        "qvel_sha256",
        "obs_state_dim",
    )
    checks = {
        field: len({_state_digest(trace["first"][field]) for trace in traces}) == 1
        for field in fields
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "note": (
            "Full obs hashes are intentionally excluded because command inputs "
            "differ; physical, recurrent, observer, and calibration handoff "
            "state must be exact."
        ),
    }


def _load_traces(preregistration: Mapping[str, Any]) -> list[dict[str, Any]]:
    traces = []
    for item in preregistration["trace_population"]:
        traces.append(
            _read_projection(
                item,
                float(item["command_x_m_s"]),
                int(item["samples"]),
            )
        )
    return traces


def _trace_lookup(
    traces: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str, float], Mapping[str, Any]]:
    return {
        (
            str(row["checkpoint_id"]),
            str(row["fit_id"]),
            float(row["command_x_m_s"]),
        ): row
        for row in traces
    }


def _markdown(value: Mapping[str, Any]) -> str:
    lines = [
        "# T178 positive-Z saved-trace causal autopsy",
        "",
        f"- Status: `{value['status']}`",
        f"- Classification: `{value['classification']}`",
        f"- Decision: `{value['decision']}`",
        f"- Trace contract: `{value['checks']['trace_contract_exact']}`",
        f"- Handoff exact: `{value['checks']['all_handoff_blocks_exact']}`",
        (
            "- Shared localized signature: "
            f"`{value['replication']['localized_shared_signature']}`"
        ),
        "- New simulation / optimizer / hosted compute / robot access: `0/0/0/0`",
        "",
        "## Replication",
        "",
        "| Signal | Modal value | Replicates | Frozen threshold |",
        "|---|---:|---:|---:|",
    ]
    for name in (
        "dominant_tilt",
        "onset_phase_bucket",
        "contact_pattern",
        "action_precursor_joint",
    ):
        row = value["replication"][name]
        lines.append(
            f"| {name} | `{row['modal_value']}` | {row['replicates']} | "
            f"{row['threshold']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "This result can earn only a separately preregistered, CPU-only "
                "source-versus-T175 positive-Z A/B. It does not authorize "
                "training, Colab, deployment, Gate 5, or robot access."
            ),
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
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip()
    _require(not dirty, "T178 execution requires committed clean preregistration")

    preregistration = _load_json(preregistration_path)
    _require(
        preregistration.get("status")
        == "PREREGISTERED_T178_POSITIVE_Z_FAILURE_AUTOPSY",
        "unexpected T178 preregistration status",
    )
    _require(
        _canonical_without(preregistration, "preregistered_contract_sha256")
        == preregistration.get("preregistered_contract_sha256"),
        "T178 preregistration hash differs",
    )
    for label, item in preregistration["frozen_inputs"].items():
        verify_receipt(item, label)
    _require(
        len(preregistration["trace_population"]) == 16,
        "T178 trace population is not 16",
    )

    traces = _load_traces(preregistration)
    lookup = _trace_lookup(traces)
    _require(len(lookup) == 16, "T178 trace keys are not unique")

    analysis = preregistration["analysis_contract"]
    prefix_ticks = int(analysis["common_prefix_ticks"])
    gait_period = int(analysis["gait_period_ticks"])
    handoffs = []
    midpoints = []
    for checkpoint_id in preregistration["matrix"]["checkpoint_ids"]:
        for fit_id in preregistration["matrix"]["fit_ids"]:
            group = [
                lookup[(checkpoint_id, fit_id, command)]
                for command in preregistration["matrix"]["commands_x_m_s"]
            ]
            handoffs.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "fit_id": fit_id,
                    **_handoff_summary(group),
                }
            )
            low = lookup[(checkpoint_id, fit_id, 0.074)]
            middle = lookup[(checkpoint_id, fit_id, 0.077)]
            high = lookup[(checkpoint_id, fit_id, 0.08)]
            midpoints.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "fit_id": fit_id,
                    "joint_signals": {
                        name: midpoint_residual_summary(
                            low[name],
                            middle[name],
                            high[name],
                            prefix_ticks=prefix_ticks,
                            gait_period_ticks=gait_period,
                        )
                        for name in (
                            "action",
                            "sent",
                            "applied",
                            "actual",
                            "force",
                            "tracking",
                        )
                    },
                    "body_signals": {
                        name: scalar_midpoint_summary(
                            low[name],
                            middle[name],
                            high[name],
                            prefix_ticks=prefix_ticks,
                        )
                        for name in ("pitch", "roll", "height")
                    },
                }
            )

    failures = [row for row in traces if not row["cell_green"]]
    _require(
        len(failures) == int(preregistration["matrix"]["failed_cells"]),
        "failed trace count differs from preregistration",
    )
    signatures = [
        failure_signature(
            failed,
            lookup[(failed["checkpoint_id"], failed["fit_id"], 0.08)],
            angle_threshold_rad=float(analysis["failure_onset"]["angle_rad"]),
            height_threshold_m=float(analysis["failure_onset"]["height_m"]),
            gait_period_ticks=gait_period,
            phase_bucket_ticks=int(analysis["phase_bucket_ticks"]),
            prefall_ticks=int(analysis["prefall_window_ticks"]),
        )
        for failed in failures
    ]
    replication = replication_summary(
        signatures,
        minimum_replicates=int(analysis["replication_threshold"]),
    )
    all_handoff = all(row["all_checks_pass"] for row in handoffs)
    trace_contract_exact = all(
        int(trace["samples"]) == int(trace["expected_samples"])
        for trace, item in zip(traces, preregistration["trace_population"], strict=True)
        for expected_samples in (item["samples"],)
    )
    if not trace_contract_exact:
        classification = "INVALID_TRACE_CONTRACT"
        decision = "NO_SUCCESSOR_AUTHORIZED"
    elif not all_handoff:
        classification = "HANDOFF_STATE_MISMATCH"
        decision = "EARN_CPU_ONLY_HANDOFF_CONTRACT_REPAIR_PREREGISTRATION_ONLY"
    elif replication["localized_shared_signature"]:
        classification = "LOCALIZED_SHARED_FAILURE_SIGNATURE"
        decision = (
            "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
            "PREREGISTRATION_ONLY"
        )
    else:
        classification = "DISTRIBUTED_CLOSED_LOOP_BALANCE_BIFURCATION"
        decision = (
            "EARN_T179_SOURCE_VS_T175_POSITIVE_Z_CPU_AB_"
            "PREREGISTRATION_ONLY"
        )

    basis: dict[str, Any] = {
        "schema_version": "open_duck.t178_positive_z_failure_autopsy_result.v1",
        "status": "COMPLETE_T178_POSITIVE_Z_FAILURE_AUTOPSY",
        "preregistered_contract_sha256": preregistration[
            "preregistered_contract_sha256"
        ],
        "classification": classification,
        "decision": decision,
        "checks": {
            "trace_contract_exact": trace_contract_exact,
            "all_handoff_blocks_exact": all_handoff,
            "all_receipts_verified": True,
            "only_saved_traces_read": True,
            "no_new_simulation": True,
            "no_optimizer_or_hosted_compute": True,
            "no_robot_or_rdk_access": True,
        },
        "handoff_blocks": handoffs,
        "command_midpoint_analysis": midpoints,
        "failure_signatures": signatures,
        "replication": replication,
        "execution": {
            "saved_traces_read": len(traces),
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
        _markdown(basis),
        encoding="utf-8",
        newline="\n",
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
    print(f"classification={result['classification']}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
