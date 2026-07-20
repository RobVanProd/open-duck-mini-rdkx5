#!/usr/bin/env python3
"""Audit whether a partial rate vector caused winner-v7 protection failures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v7_full_measured_vector_attribution_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v7_full_measured_vector_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_FULL_MEASURED_VECTOR_ATTRIBUTION_20260720.md"

JOINT_NAMES = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll", "right_hip_yaw",
    "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def finite(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, list):
        return all(finite(item) for item in value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    return False


def iter_trace_specs(source: dict[str, Any]):
    for condition in source["conditions"]:
        for fit_name, fit in condition["matrices"].items():
            for checkpoint, evaluation in fit.items():
                for trace in evaluation["current"]["traces"]:
                    yield {
                        "condition": condition["id"],
                        "fit": fit_name,
                        "checkpoint": checkpoint,
                        "trace": trace,
                    }


def prior_distance(ticks: list[int], event_tick: int) -> int | None:
    prior = [tick for tick in ticks if tick <= event_tick]
    return event_tick - max(prior) if prior else None


def audit_trace(
    spec: dict[str, Any],
    *,
    graph_rates: list[float],
    full_rates: list[float],
    motor_constant_nm_per_a: float,
    current_limit_a: float,
    torque_limit_nm: float,
    tolerance: float,
) -> dict[str, Any]:
    trace_spec = spec["trace"]
    path = Path(trace_spec["path"])
    if sha256(path) != trace_spec["sha256"]:
        raise ValueError(f"trace hash mismatch: {path}")
    forces: list[list[float]] = []
    full_violation_ticks: list[list[int]] = [[] for _ in JOINT_NAMES]
    graph_field_error = 0.0
    full_field_error = 0.0
    graph_excess_max = 0.0
    full_excess_max = 0.0
    with path.open("r", encoding="utf-8") as stream:
        for line_index, line in enumerate(stream):
            row = json.loads(line)
            if int(row["tick"]) != line_index or not finite(row):
                raise ValueError(f"invalid trace row: {path}:{line_index}")
            velocity = [abs(float(value)) for value in row["sent_target_velocity_rad_s"]]
            force = [float(value) for value in row["actuator_force_nm"]]
            recorded_graph = [float(value) for value in row["sent_target_rate_excess_rad_s"]]
            recorded_full = [float(value) for value in row["conservative_rate_excess_rad_s"]]
            if not all(len(values) == len(JOINT_NAMES) for values in (velocity, force, recorded_graph, recorded_full)):
                raise ValueError(f"wrong vector width: {path}:{line_index}")
            expected_graph = [max(value - limit, 0.0) for value, limit in zip(velocity, graph_rates, strict=True)]
            expected_full = [max(value - limit, 0.0) for value, limit in zip(velocity, full_rates, strict=True)]
            graph_field_error = max(graph_field_error, *(abs(a - b) for a, b in zip(recorded_graph, expected_graph, strict=True)))
            full_field_error = max(full_field_error, *(abs(a - b) for a, b in zip(recorded_full, expected_full, strict=True)))
            graph_excess_max = max(graph_excess_max, *expected_graph)
            full_excess_max = max(full_excess_max, *expected_full)
            for joint_index, value in enumerate(expected_full):
                if value > tolerance:
                    full_violation_ticks[joint_index].append(line_index)
            forces.append(force)
    if len(forces) != int(trace_spec["rows"]):
        raise ValueError(f"trace row-count mismatch: {path}")
    if graph_field_error > tolerance or full_field_error > tolerance:
        raise ValueError(f"recorded rate-excess replay mismatch: {path}")

    per_joint_peak = [max(abs(row[index]) for row in forces) for index in range(len(JOINT_NAMES))]
    peak_ticks = [
        max(range(len(forces)), key=lambda tick: abs(forces[tick][index]))
        for index in range(len(JOINT_NAMES))
    ]
    current_fail_indices = [
        index for index, torque in enumerate(per_joint_peak)
        if torque / motor_constant_nm_per_a > current_limit_a
    ]
    torque_fail_indices = [
        index for index, torque in enumerate(per_joint_peak) if torque > torque_limit_nm
    ]
    failing_indices = sorted(set(current_fail_indices) | set(torque_fail_indices))
    failure_events = [
        {
            "joint": JOINT_NAMES[index],
            "tick": peak_ticks[index],
            "peak_torque_nm": per_joint_peak[index],
            "peak_current_a": per_joint_peak[index] / motor_constant_nm_per_a,
            "prior_full_vector_violation_distance_ticks": prior_distance(
                full_violation_ticks[index], peak_ticks[index]
            ),
            "full_vector_violation_count": len(full_violation_ticks[index]),
        }
        for index in failing_indices
    ]
    global_peak_index = max(range(len(JOINT_NAMES)), key=per_joint_peak.__getitem__)
    return {
        "identity": {
            "condition": spec["condition"],
            "fit": spec["fit"],
            "checkpoint": spec["checkpoint"],
            "command_x": float(trace_spec["command_x"]),
        },
        "trace_sha256": trace_spec["sha256"],
        "rows": len(forces),
        "rate_replay": {
            "graph_field_max_error": graph_field_error,
            "full_vector_field_max_error": full_field_error,
            "graph_vector_max_excess_rad_s": graph_excess_max,
            "full_vector_max_excess_rad_s": full_excess_max,
            "full_vector_violation_joints": [
                JOINT_NAMES[index] for index, ticks in enumerate(full_violation_ticks) if ticks
            ],
        },
        "protection": {
            "current_fail_joints": [JOINT_NAMES[index] for index in current_fail_indices],
            "torque_fail_joints": [JOINT_NAMES[index] for index in torque_fail_indices],
            "failure_events": failure_events,
            "global_peak_joint": JOINT_NAMES[global_peak_index],
            "global_peak_tick": peak_ticks[global_peak_index],
            "global_peak_torque_nm": per_joint_peak[global_peak_index],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("full measured-vector attribution already exists")
    prereg = load(PREREG)
    frozen = prereg["frozen_inputs"]
    resolved: dict[str, Path] = {}
    for name, item in frozen.items():
        if name == "audit_tool_sha256":
            if sha256(Path(__file__)) != item:
                raise ValueError("audit-tool hash mismatch")
            continue
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise ValueError(f"frozen input mismatch: {path}")
        resolved[name] = path

    source = load(resolved["winner_v7_result"])
    current_contract = load(resolved["current_gate_contract"])
    v5 = load(resolved["measured_all_joint_envelope"])
    policy_contract = load(resolved["runtime_policy_contract"])
    graph_rates = [float(value) for value in policy_contract["action_contract"]["measured_rate_limits_rad_s"]]
    full_rates = [
        float(v5["actuator_plants"]["per_joint"][joint]["conservative_velocity_limit_rad_s"])
        for joint in JOINT_NAMES
    ]
    tolerance = float(prereg["analysis_contract"]["numeric_tolerance"])
    mismatch_indices = [
        index for index, (graph, full) in enumerate(zip(graph_rates, full_rates, strict=True))
        if graph - full > tolerance
    ]
    gate = current_contract["prospective_offline_candidate_gate"]
    motor_constant = float(current_contract["conversion"]["manufacturer_motor_constant_nm_per_a"])
    traces = [
        audit_trace(
            spec,
            graph_rates=graph_rates,
            full_rates=full_rates,
            motor_constant_nm_per_a=motor_constant,
            current_limit_a=float(gate["per_joint_peak_current_a_max"]),
            torque_limit_nm=float(gate["per_joint_peak_torque_nm_max"]),
            tolerance=tolerance,
        )
        for spec in iter_trace_specs(source)
    ]
    moving = [row for row in traces if row["identity"]["command_x"] > 0.0]
    zero = [row for row in traces if row["identity"]["command_x"] == 0.0]
    all_failure_events = [event for row in moving for event in row["protection"]["failure_events"]]
    failure_joint_names = {event["joint"] for event in all_failure_events}
    mismatch_names = {JOINT_NAMES[index] for index in mismatch_indices}
    temporal_window = int(prereg["analysis_contract"]["causal_prior_window_ticks"])
    distances = [event["prior_full_vector_violation_distance_ticks"] for event in all_failure_events]
    within_window = [value for value in distances if value is not None and value <= temporal_window]
    temporal_fraction = len(within_window) / len(distances) if distances else 0.0
    checks = {
        "source_winner_v7_remains_closed": source["decision"] == "CLOSE_WINNER_V7_PROTECTED_BASE",
        "source_population_complete": len(traces) == 128 and len(moving) == 96 and len(zero) == 32,
        "recorded_rate_fields_replay_exactly": all(
            row["rate_replay"]["graph_field_max_error"] <= tolerance
            and row["rate_replay"]["full_vector_field_max_error"] <= tolerance
            for row in traces
        ),
        "partial_graph_vector_has_exactly_eight_relaxed_nonpitch_joints": mismatch_indices == [0, 1, 5, 6, 7, 8, 9, 10],
        "all_moving_traces_violate_full_measured_vector": all(row["rate_replay"]["full_vector_max_excess_rad_s"] > tolerance for row in moving),
        "no_zero_trace_violates_full_measured_vector": all(row["rate_replay"]["full_vector_max_excess_rad_s"] <= tolerance for row in zero),
        "graph_vector_reports_zero_excess_for_all_traces": all(row["rate_replay"]["graph_vector_max_excess_rad_s"] <= tolerance for row in traces),
        "all_moving_traces_fail_current_and_torque": all(
            row["protection"]["current_fail_joints"] and row["protection"]["torque_fail_joints"]
            for row in moving
        ),
        "no_zero_trace_fails_current_or_torque": all(
            not row["protection"]["current_fail_joints"] and not row["protection"]["torque_fail_joints"]
            for row in zero
        ),
        "every_gate_failing_joint_is_in_relaxed_vector_subset": failure_joint_names <= mismatch_names,
        "at_least_95pct_failure_peaks_follow_same_joint_violation_within_six_ticks": temporal_fraction >= 0.95,
    }
    selection_keys = prereg["selection_rule"]["all_checks_required"]
    selected = all(checks[key] for key in selection_keys)
    decision = (
        "SELECT_DISTINCT_FULL_MEASURED_VECTOR_GRAPH_CONTRACT"
        if selected else "CLOSE_FULL_MEASURED_VECTOR_CAUSAL_ROUTE"
    )
    failure_joint_counts = Counter(event["joint"] for event in all_failure_events)
    payload = {
        "schema_version": "open_duck_mini.winner_v7_full_measured_vector_attribution.v1",
        "status": "PASS_WINNER_V7_FULL_MEASURED_VECTOR_ATTRIBUTION" if selected else "HOLD_WINNER_V7_FULL_MEASURED_VECTOR_ATTRIBUTION",
        "decision": decision,
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_selection_checks": [key for key in selection_keys if not checks[key]],
        "vectors": {
            "joint_order": list(JOINT_NAMES),
            "graph_rate_limits_rad_s": graph_rates,
            "full_measured_conservative_rate_limits_rad_s": full_rates,
            "relaxed_joint_indices": mismatch_indices,
            "relaxed_joint_names": [JOINT_NAMES[index] for index in mismatch_indices],
        },
        "population": {
            "traces": len(traces),
            "moving": len(moving),
            "zero_command": len(zero),
            "failure_events": len(all_failure_events),
            "failure_joint_counts": dict(sorted(failure_joint_counts.items())),
            "same_joint_prior_violation_within_window": len(within_window),
            "temporal_fraction": temporal_fraction,
            "causal_prior_window_ticks": temporal_window,
        },
        "trace_audits": traces,
        "authority": {
            "winner_v7_reclassified_or_retried": False,
            "policy_graph_or_simulator_mutated": False,
            "behavior_training_gpu_colab": False,
            "robot_runtime_torque_motion_gate5": False,
            "distinct_zero_behavior_graph_contract_authorized_next": selected,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "# Winner-v7 Full Measured-Vector Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{decision}`\n\n"
        f"- graph vector: `{graph_rates}` rad/s\n"
        f"- full measured conservative vector: `{full_rates}` rad/s\n"
        f"- relaxed graph joints: `{[JOINT_NAMES[index] for index in mismatch_indices]}`\n"
        f"- moving traces with full-vector excess: `{sum(row['rate_replay']['full_vector_max_excess_rad_s'] > tolerance for row in moving)}/{len(moving)}`\n"
        f"- protection failure events: `{len(all_failure_events)}`\n"
        f"- failure events within `{temporal_window}` ticks of a same-joint measured-vector violation: `{len(within_window)}/{len(distances)}`\n\n"
        "This is a read-only causal audit. Winner-v7 remains closed; no graph transform, behavior run, training, runtime, deployment, robot access, torque, motion, or Gate 5 is authorized by the result itself.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"DECISION={decision}")
    print(f"OUTPUT_SHA256={sha256(OUTPUT_JSON)}")
    return 0 if selected else 2


if __name__ == "__main__":
    raise SystemExit(main())
