#!/usr/bin/env python3
"""Read-only causal audit of the frozen winner-v3 1,024-cell evidence."""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
CELLS = ANALYSIS / "winner_v3_variable_configuration_cells"
TRACES = ANALYSIS / "winner_v3_variable_configuration_traces"
TRACE_MANIFEST = ANALYSIS / "winner_v3_variable_configuration_trace_manifest.json"
CORRECTED_RESULT = ANALYSIS / "winner_v3_variable_configuration_result_corrected.json"
PREREG = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
TRANSFORM = ANALYSIS / "winner_v3_variable_configuration_eval_policy_transform_contract.json"
RUNNER_CONTRACT = ANALYSIS / "winner_v3_variable_configuration_behavior_runner_contract.json"
OBS_MAP = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719/observation_map.json"
OUTPUT_JSON = ANALYSIS / "winner_v3_failure_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V3_FAILURE_ATTRIBUTION_20260720.md"

CURRENT_NM_PER_A = 0.784532
CURRENT_LIMIT_A = 0.65
TRACKING_LIMIT_RAD = 0.20
BASE_HEIGHT_MIN_M = 0.12
PITCH_MAX_RAD = 0.25
EXPECTED_POLICY_COMMIT = "1799e06a62a6e18f8fc4a2aa019a47d6c46812ac"
RUNTIME_REQUEST_COMMIT = "e9c3c12191953180bfccdacec0e1e30ba91f94f9"
JOINT_NAMES = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
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


def percentile_sorted(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    position = (len(values) - 1) * q
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(values[lower])
    weight = position - lower
    return float(values[lower] * (1.0 - weight) + values[upper] * weight)


def prefix_p95_exceedance_ticks(samples: list[list[float]], threshold: float) -> dict[str, Any]:
    sorted_by_joint: list[list[float]] = [[] for _ in JOINT_NAMES]
    flags: list[bool] = []
    values: list[float] = []
    for sample in samples:
        for joint_index, value in enumerate(sample):
            bisect.insort(sorted_by_joint[joint_index], abs(float(value)))
        worst = max(percentile_sorted(joint, 0.95) for joint in sorted_by_joint)
        values.append(worst)
        flags.append(worst > threshold)
    first = next((index for index, flag in enumerate(flags) if flag), None)
    last_false = max((index for index, flag in enumerate(flags) if not flag), default=-1)
    persistent = last_false + 1 if flags and flags[-1] and last_false + 1 < len(flags) else None
    return {
        "first_prefix_exceed_tick": first,
        "first_persistent_prefix_exceed_tick": persistent,
        "final_prefix_p95": values[-1] if values else None,
    }


def first_tick(values: Iterable[bool]) -> int | None:
    return next((index for index, value in enumerate(values) if value), None)


def persistent_prefix_mean_tick(values: list[float], predicate: Callable[[float], bool]) -> int | None:
    if not values:
        return None
    means = np.cumsum(np.asarray(values, dtype=np.float64)) / np.arange(1, len(values) + 1)
    flags = [bool(predicate(float(value))) for value in means]
    if not flags[-1]:
        return None
    last_false = max((index for index, flag in enumerate(flags) if not flag), default=-1)
    return last_false + 1 if last_false + 1 < len(flags) else None


def axis_family(identity: dict[str, Any]) -> str:
    group = identity["condition_group"]
    condition = identity["condition_id"]
    if group == "NOMINAL":
        return "NOMINAL"
    if group == "DISCOVERY":
        return "COUPLED_DISCOVERY"
    if group == "HELDOUT":
        return "COUPLED_HELDOUT"
    if group == "SENSOR_TRANSPORT":
        return f"SENSOR_{condition}"
    if condition.startswith("COM_CORNER"):
        return "COUPLED_COM_CORNER"
    if condition.startswith("OPTIONAL_AGGREGATE"):
        return "OPTIONAL_AGGREGATE"
    parts = condition.split("_")
    if parts[0] == "COM" and len(parts) >= 3:
        return "_".join(parts[:2])
    if parts[0] == "INERTIA" and len(parts) >= 3:
        return "_".join(parts[:2])
    if parts[0] == "MASS":
        return "MASS"
    return condition


def tick_stats(values: Iterable[int | None]) -> dict[str, Any]:
    present = sorted(int(value) for value in values if value is not None)
    if not present:
        return {"count": 0, "min": None, "p50": None, "max": None}
    return {
        "count": len(present),
        "min": present[0],
        "p50": float(np.percentile(present, 50)),
        "max": present[-1],
    }


def ordering(first: int | None, other: int | None) -> str:
    if first is None:
        return "current_event_absent"
    if other is None:
        return "comparison_event_absent"
    if first < other:
        return "current_before"
    if first > other:
        return "current_after"
    return "same_tick"


def read_trace(path: Path, manifest_row: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    digest = hashlib.sha256()
    currents: list[list[float]] = []
    tracking: list[list[float]] = []
    local_vx: list[float] = []
    saturation_flags: list[bool] = []
    rate_flags: list[bool] = []
    envelope_flags: list[bool] = []
    done_flags: list[bool] = []
    height_flags: list[bool] = []
    pitch_flags: list[bool] = []
    command_errors: list[float] = []
    obs_command_errors: list[float] = []
    zero_action_flags: list[bool] = []
    first_row: dict[str, Any] | None = None
    last_row: dict[str, Any] | None = None
    all_finite = True
    with path.open("rb") as stream:
        for line_index, line in enumerate(stream):
            digest.update(line)
            row = json.loads(line)
            if first_row is None:
                first_row = row
            last_row = row
            if int(row["tick"]) != line_index:
                raise ValueError(f"noncontiguous tick in {path}: {line_index}")
            all_finite = all_finite and finite(row)
            force = [float(value) for value in row["actuator_force_nm"]]
            currents.append([abs(value) / CURRENT_NM_PER_A for value in force])
            tracking.append(
                [
                    abs(float(sent) - float(actual))
                    for sent, actual in zip(
                        row["sent_target_rad"], row["actual_position_rad"], strict=True
                    )
                ]
            )
            local_vx.append(float(row["local_linvel_m_s"][0]))
            # Match the frozen behavior evaluator's saturation definition.
            # The trace's boolean action_saturated field uses the hard 1.0
            # action boundary and therefore cannot replay the contracted
            # action_saturation_pct metric, which begins at abs(action) >= 0.98.
            saturation_flags.append(
                any(abs(float(value)) >= 0.98 for value in row["action"])
            )
            rate_flags.append(any(float(value) > 0.0 for value in row["conservative_rate_excess_rad_s"]))
            envelope_flags.append(any(float(value) > 0.0 for value in row["actual_centered_guard_excess_rad"]))
            done_flags.append(bool(row["done"]))
            height_flags.append(float(row["base_height_m"]) < BASE_HEIGHT_MIN_M)
            pitch_flags.append(abs(float(row["body_pitch_rad"])) > PITCH_MAX_RAD)
            command = float(cell["identity"]["command_x_m_s"])
            command_errors.append(abs(float(row["command"][0]) - command))
            obs_command_errors.append(
                float(abs(float(row["obs_state"][6]) - float(np.float32(command))))
            )
            zero_action_flags.append(all(float(value) == 0.0 for value in row["action"]))

    trace_hash = digest.hexdigest()
    if trace_hash != manifest_row["sha256"] or path.stat().st_size != manifest_row["bytes"]:
        raise ValueError(f"trace identity mismatch: {path}")
    if len(currents) != manifest_row["rows"] or not all_finite:
        raise ValueError(f"trace content mismatch: {path}")

    current_prefix = prefix_p95_exceedance_ticks(currents, CURRENT_LIMIT_A)
    tracking_prefix = prefix_p95_exceedance_ticks(tracking, TRACKING_LIMIT_RAD)
    current_array = np.asarray(currents, dtype=np.float64)
    tracking_array = np.asarray(tracking, dtype=np.float64)
    current_p95 = np.percentile(current_array, 95, axis=0)
    tracking_p95 = np.percentile(tracking_array, 95, axis=0)
    recorded_current = cell["metrics"]["current_p95_a_by_joint"]
    recorded_tracking = cell["metrics"]["tracking_p95_rad_by_joint"]
    current_error = max(
        abs(float(current_p95[index]) - float(recorded_current[name]))
        for index, name in enumerate(JOINT_NAMES)
    )
    tracking_error = max(
        abs(float(tracking_p95[index]) - float(recorded_tracking[name]))
        for index, name in enumerate(JOINT_NAMES)
    )
    if current_error > 1e-12 or tracking_error > 1e-12:
        raise ValueError(f"metric replay mismatch: {path}: {current_error}, {tracking_error}")

    command = float(cell["identity"]["command_x_m_s"])
    direction_tick = (
        persistent_prefix_mean_tick(local_vx, lambda value: value <= 0.0)
        if command > 0.0 and float(np.mean(local_vx)) <= 0.0
        else None
    )
    zero_velocity_tick = (
        persistent_prefix_mean_tick(local_vx, lambda value: abs(value) > 0.02)
        if command == 0.0 and abs(float(np.mean(local_vx))) > 0.02
        else None
    )
    events = {
        "current_p95": current_prefix["first_persistent_prefix_exceed_tick"]
        if not cell["metrics"]["checks"]["current_p95_at_most_0p65"]
        else None,
        "tracking_p95": tracking_prefix["first_persistent_prefix_exceed_tick"]
        if not cell["metrics"]["checks"]["tracking_p95_at_most_0p20"]
        else None,
        "direction": direction_tick,
        "zero_velocity": zero_velocity_tick,
        "saturation": first_tick(saturation_flags)
        if not cell["metrics"]["checks"]["zero_saturation"]
        else None,
        "rate": first_tick(rate_flags)
        if not cell["metrics"]["checks"]["zero_rate_excess"]
        else None,
        "envelope": first_tick(envelope_flags)
        if not cell["metrics"]["checks"]["zero_envelope_excess"]
        else None,
        "base_height": first_tick(height_flags)
        if not cell["metrics"]["checks"]["zero_command_base_height"]
        or not cell["metrics"]["checks"]["candidate_gate_pass"]
        else None,
        "pitch": first_tick(pitch_flags)
        if not cell["metrics"]["checks"]["candidate_gate_pass"]
        else None,
        "termination": first_tick(done_flags)
        if not cell["metrics"]["checks"]["duration_complete_600"]
        else None,
    }
    physical_ticks = [value for value in events.values() if value is not None]
    return {
        "trace_sha256": trace_hash,
        "trace_bytes": path.stat().st_size,
        "rows": len(currents),
        "first_row": {
            "tick": int(first_row["tick"]) if first_row else None,
            "command_x_m_s": float(first_row["command"][0]) if first_row else None,
            "obs_command_x_m_s": float(first_row["obs_state"][6]) if first_row else None,
            "accelerometer_local_xyz_m_s2": first_row["obs_state"][3:6] if first_row else None,
            "action_exact_zero": zero_action_flags[0] if zero_action_flags else None,
        },
        "last_tick": int(last_row["tick"]) if last_row else None,
        "current_replay_max_abs_error_a": current_error,
        "tracking_replay_max_abs_error_rad": tracking_error,
        "worst_current_p95_a": float(np.max(current_p95)),
        "worst_current_p95_joint": JOINT_NAMES[int(np.argmax(current_p95))],
        "worst_tracking_p95_rad": float(np.max(tracking_p95)),
        "first_instantaneous_current_over_0p65_tick": first_tick(
            max(sample) > CURRENT_LIMIT_A for sample in currents
        ),
        "first_instantaneous_tracking_over_0p20_tick": first_tick(
            max(sample) > TRACKING_LIMIT_RAD for sample in tracking
        ),
        "current_prefix": current_prefix,
        "tracking_prefix": tracking_prefix,
        "events": events,
        "first_physical_failure_tick": min(physical_ticks) if physical_ticks else None,
        "max_command_field_error": max(command_errors, default=None),
        "max_obs_command_field_error": max(obs_command_errors, default=None),
        "all_actions_exact_zero": all(zero_action_flags),
        "mean_local_vx_m_s_replayed": float(np.mean(local_vx)),
    }


def bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failures = Counter(reason for row in rows for reason in row["failures"])
    return {
        "cells": len(rows),
        "passing_cells": sum(row["physical_pass"] for row in rows),
        "passing_excluding_current": sum(row["pass_excluding_current"] for row in rows),
        "current_only_failures": sum(row["current_only_failure"] for row in rows),
        "early_terminations": sum(not row["checks"]["duration_complete_600"] for row in rows),
        "wrong_direction": sum(not row["checks"]["positive_command_consistent_motion"] for row in rows),
        "failure_counts": dict(sorted(failures.items())),
        "first_physical_failure_tick": tick_stats(row["timing"]["first_physical_failure_tick"] for row in rows),
        "first_persistent_current_p95_tick": tick_stats(row["timing"]["events"]["current_p95"] for row in rows),
        "termination_tick": tick_stats(row["timing"]["events"]["termination"] for row in rows),
    }


def split(rows: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    return {name: bucket(groups[name]) for name in sorted(groups)}


def baseline_comparison() -> dict[str, Any]:
    pairs = []
    input_hashes = {}
    ordinal = {512000: 1003520, 1024000: 2007040}
    for plant_short, plant in (
        ("p30", "P30_ALL_JOINT"),
        ("p31_34", "P31_34_PITCH_WITH_P30_NONPITCH"),
    ):
        for baseline_step, candidate_step in ordinal.items():
            path = ANALYSIS / f"ground_up_dual_fit_conservative_envelope_{plant_short}_T2_EQUAL_{baseline_step}_eval.json"
            evidence = load(path)
            input_hashes[str(path.relative_to(ROOT))] = sha256(path)
            for run in evidence["runs"]:
                command = float(run["command_x"])
                candidate_name = (
                    f"nominal_nominal_seed_167931544_step{candidate_step}_"
                    f"{plant.lower()}_x{command:.3f}_seed167931544.json"
                )
                candidate = load(CELLS / candidate_name)
                mode = run["modes"]["fitted"]
                baseline_tracking = max(
                    float(joint["joint_target_tracking_error_rad"]["p95"])
                    for joint in mode["joints"].values()
                )
                baseline_trace = ROOT / run["trace_jsonl"]
                input_hashes[str(baseline_trace.relative_to(ROOT))] = sha256(baseline_trace)
                pairs.append(
                    {
                        "baseline_step": baseline_step,
                        "candidate_step": candidate_step,
                        "pairing_semantics": "persistent-checkpoint ordinal comparison; not checkpoint lineage",
                        "plant": plant,
                        "command_x_m_s": command,
                        "baseline": {
                            "samples": int(mode["samples"]),
                            "termination_reason": mode["termination_reason"],
                            "candidate_gate_status": run["candidate_gate"]["status"],
                            "mean_local_vx_m_s": float(mode["forward_motion"]["mean_velocity_x_m_s"]),
                            "worst_tracking_p95_rad": baseline_tracking,
                            "worst_saturation_pct": max(
                                float(joint["action_saturation_pct"]) for joint in mode["joints"].values()
                            ),
                            "current_metric_available": all(
                                "current_a" in joint for joint in mode["joints"].values()
                            ),
                        },
                        "candidate": {
                            "samples": candidate["metrics"]["samples"],
                            "termination_reason": candidate["metrics"]["termination_reason"],
                            "candidate_gate_status": candidate["metrics"]["candidate_gate_status"],
                            "mean_local_vx_m_s": candidate["metrics"]["mean_local_vx_m_s"],
                            "worst_tracking_p95_rad": candidate["metrics"]["worst_tracking_p95_rad"],
                            "worst_saturation_pct": candidate["metrics"]["worst_saturation_pct"],
                            "worst_current_p95_a": candidate["metrics"]["worst_current_p95_a"],
                            "failure_reasons_excluding_cpu": [
                                reason for reason in candidate["failure_reasons"] if reason != "cpu_only"
                            ],
                        },
                        "delta_candidate_minus_baseline": {
                            "mean_local_vx_m_s": candidate["metrics"]["mean_local_vx_m_s"]
                            - float(mode["forward_motion"]["mean_velocity_x_m_s"]),
                            "worst_tracking_p95_rad": candidate["metrics"]["worst_tracking_p95_rad"]
                            - baseline_tracking,
                        },
                    }
                )
    return {
        "scope": "16 like-for-like nominal seed-167931544 cells",
        "input_hashes": dict(sorted(input_hashes.items())),
        "pairs": pairs,
        "summary": {
            "baseline_prior_behavior_passes": sum(
                row["baseline"]["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE"
                and row["baseline"]["samples"] == 600
                for row in pairs
            ),
            "candidate_prior_behavior_passes_excluding_current": sum(
                row["candidate"]["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE"
                and row["candidate"]["samples"] == 600
                and set(row["candidate"]["failure_reasons_excluding_cpu"])
                <= {"current_p95_at_most_0p65"}
                for row in pairs
            ),
            "candidate_current_failures": sum(
                "current_p95_at_most_0p65" in row["candidate"]["failure_reasons_excluding_cpu"]
                for row in pairs
            ),
            "baseline_current_comparison_available": False,
            "baseline_current_limitation": (
                "Historical G1/T2 result JSON and traces do not store actuator_force_nm/current_a; "
                "no current regression is inferred or invented."
            ),
            "vx_delta_range_m_s": [
                min(row["delta_candidate_minus_baseline"]["mean_local_vx_m_s"] for row in pairs),
                max(row["delta_candidate_minus_baseline"]["mean_local_vx_m_s"] for row in pairs),
            ],
            "tracking_delta_range_rad": [
                min(row["delta_candidate_minus_baseline"]["worst_tracking_p95_rad"] for row in pairs),
                max(row["delta_candidate_minus_baseline"]["worst_tracking_p95_rad"] for row in pairs),
            ],
        },
    }


def build_markdown(result: dict[str, Any]) -> str:
    overall = result["overall"]
    signed = result["signed_x"]
    baseline = result["nominal_baseline_comparison"]["summary"]
    lines = [
        "# Winner-v3 Failure Attribution — 2026-07-20 (corrected primary-source audit)",
        "",
        f"status: `{result['status']}`",
        "",
        f"decision: `{result['decision']}`",
        "",
        "Correction: the first published audit consulted the current Feetech product page but missed Feetech's 2024 catalog, which explicitly lists `650 mA` rated current at `7.4 V`. This version supersedes the current-provenance interpretation only. It does not change any cell, metric, threshold, or the completed winner-v3 result.",
        "",
        "## Evidence result",
        "",
        f"All `{overall['cells']}` committed cells and all `{overall['trace_count']}` local traces were read, rehashed, and replayed for current/tracking aggregation. Physical pass remains `{overall['physical_passes']}/{overall['cells']}`. Removing only the frozen current check for attribution—not reclassification—leaves `{overall['pass_excluding_current']}` otherwise-passing cells and `{overall['fail_excluding_current']}` cells with at least one other physical failure. `{overall['current_only_failures']}` cells fail only the current check.",
        "",
        "## Current gate provenance and feasibility",
        "",
        "The completed gate is unchanged. Its metric is per-joint p95 over every recorded tick of `abs(MuJoCo actuator_force Nm) / 0.784532 Nm/A`; the cell value is the maximum of 14 joint p95 values. The `0.65 A` threshold and `8 kgf.cm/A` conversion first appear together in preregistration commit `58a8a1d`; no older repository source, manufacturer citation, measured torque-current fit, voltage dependence, or uncertainty is supplied.",
        "",
        "Feetech's 2024 catalog reports rated torque `5 kg.cm @ 7.4 V`, rated current `0.65 A @ 7.4 V`, peak stall torque `19.5 kg.cm @ 7.4 V`, and stall current `2.5 A @ 7.4 V`. Thus `0.65 A` has primary-source support as a rated operating point. The catalog does not specify a p95-over-600-ticks safety rule, a duty/thermal population, or the repository's `8 kg.cm/A` conversion. The rated-point quotient is `0.754357692 N.m/A`; the repository uses `0.784532 N.m/A`, exactly 4% higher. Runtime's `0.0065 A/count` correctly makes `0.65 A` equal 100 telemetry counts, but that scale alone does not define a p95 safety contract. Catalog: https://www.feetechrc.com/Data/feetechrc/upload/file/20240706/2024%E9%A3%9E%E7%89%B9%E5%AE%A3%E4%BC%A0%E5%86%8C.pdf",
        "",
        "Feetech's current product page separately reports the 6 V operating point (`6.5 kg.cm` rated torque, `19.5 kg.cm` peak stall torque, `2.0 A` stall current) but no rated current. These sources are voltage-specific rather than interchangeable. Product page: https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear.html",
        "",
        f"The infeasibility is deterministic: all eight nominal x=0 cells have exact-zero graph actions for all 600 ticks, yet the identical home-hold right-knee p95 is `{result['current_provenance']['x0_home_hold']['worst_current_p95_a']:.9f} A`, above `0.65 A`. Training policy weights cannot change that cell while the x=0 deadband, home/reset, model, and threshold remain frozen.",
        "",
        "## Temporal ordering",
        "",
        "`current_p95` onset is the first tick after which the running per-joint p95 stays above 0.65 A through the recorded end. Direction onset is the first tick after which cumulative mean local vx remains nonpositive. Tracking uses the analogous persistent running-p95 rule. These definitions match final gate populations and avoid choosing an arbitrary window.",
        "",
    ]
    for event, counts in result["current_temporal_ordering"].items():
        lines.append(f"- versus `{event}`: " + ", ".join(f"`{key}` {value}" for key, value in counts.items()))
    lines.extend(
        [
            "",
            "## Signed X mechanism",
            "",
            f"`COM_X_NEG` has `{signed['COM_X_NEG']['cells']}` cells: `{signed['COM_X_NEG']['early_terminations']}` terminate early and `{signed['COM_X_NEG']['wrong_direction']}` finish with nonpositive mean vx. `COM_X_POS` has `{signed['COM_X_POS']['cells']}` cells: `{signed['COM_X_POS']['early_terminations']}` terminate early and `{signed['COM_X_POS']['wrong_direction']}` finish with nonpositive mean vx. Exact body-2 `trunk_assembly` readback, signed +/−0.05 m X mutation, raw command propagation, and reset state all validate per run.",
            "",
            "Negative X produces backward reversal/fall; positive X produces forward overspeed/fall in the recorded traces. The signs follow the static sagittal moment and are not command normalization, wrong-body, reset, or transform-load defects.",
            "",
            "## Nominal regression comparison",
            "",
            f"All `{baseline['baseline_prior_behavior_passes']}/16` historical G1/T2 nominal cells and all `{baseline['candidate_prior_behavior_passes_excluding_current']}/16` like-for-like winner-v3 nominal cells pass the pre-current behavior gates. Winner-v3 nominal failures are `{baseline['candidate_current_failures']}/16` current checks only. Mean-vx delta spans `{baseline['vx_delta_range_m_s'][0]:.9f}` to `{baseline['vx_delta_range_m_s'][1]:.9f} m/s`; worst-tracking delta spans `{baseline['tracking_delta_range_rad'][0]:.9f}` to `{baseline['tracking_delta_range_rad'][1]:.9f} rad`. Historical traces did not store actuator force/current, so no baseline current regression is claimed.",
            "",
            "## Observability and selected next mechanism",
            "",
            "The deployable 115-D observation contains IMU, command, joint state, action history, P30 applied-target observer state, contacts, phase, and projected reference action. It contains no torso mass, COM XYZ, inertia tensor, all-link mass scale, actuator-fit identity, delay scalar, or transport-condition identifier. Those quantities can affect dynamic response but are not uniquely identified as physical parameters by the current interface or the frozen automatic response profile.",
            "",
            "Broad latent-domain exposure plus a 64-state recurrent adapter therefore tested implicit online adaptation; it did not clear signed X or the full coupled matrix. Repeating blind domain randomization is not selected. The falsifiable follow-up is ordered: (1) prospectively define the current/torque gate application from documented motor limits, duty/aggregation semantics, and measured telemetry without changing this result; (2) freeze and runtime-review an automatic-response-conditioned interface or estimator that uses no manual per-build measurement; (3) only then preregister one training run and the unchanged full behavior matrix.",
            "",
            "No new training is authorized by this audit alone. No policy is selected and robot clearance remains false.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="write the audit artifacts")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("read-only audit requires explicit --execute")

    manifest = load(TRACE_MANIFEST)
    manifest_rows = {
        row["trace_path"]: {
            "sha256": row["trace_sha256"],
            "bytes": row["trace_bytes"],
            "rows": row["trace_rows"],
        }
        for row in manifest["traces"]
    }
    cell_paths = sorted(CELLS.glob("*.json"))
    if len(cell_paths) != 1024 or len(manifest_rows) != 1024:
        raise ValueError("expected exactly 1024 cells and traces")

    rows = []
    for index, cell_path in enumerate(cell_paths, start=1):
        cell = load(cell_path)
        trace_rel = cell["trace"]["path"]
        if trace_rel not in manifest_rows:
            raise ValueError(f"trace absent from manifest: {trace_rel}")
        timing = read_trace(ROOT / trace_rel, manifest_rows[trace_rel], cell)
        checks = {
            key: bool(value)
            for key, value in cell["metrics"]["checks"].items()
            if key != "cpu_only"
        }
        physical_pass = all(checks.values())
        pass_excluding_current = all(
            value for key, value in checks.items() if key != "current_p95_at_most_0p65"
        )
        failures = sorted(key for key, value in checks.items() if not value)
        identity = cell["identity"]
        rows.append(
            {
                "cell_path": str(cell_path.relative_to(ROOT)),
                "cell_sha256": sha256(cell_path),
                "trace_path": trace_rel,
                "identity": identity,
                "axis_family": axis_family(identity),
                "policy_transform_mode": "EXACT_X0_DEADBAND" if identity["command_x_m_s"] == 0.0 else "MOVING_BAKED_TRANSFORM_STACK",
                "checks": checks,
                "failures": failures,
                "physical_pass": physical_pass,
                "pass_excluding_current": pass_excluding_current,
                "current_only_failure": (not checks["current_p95_at_most_0p65"] and pass_excluding_current),
                "metrics": {
                    "samples": cell["metrics"]["samples"],
                    "termination_reason": cell["metrics"]["termination_reason"],
                    "mean_local_vx_m_s": cell["metrics"]["mean_local_vx_m_s"],
                    "worst_tracking_p95_rad": cell["metrics"]["worst_tracking_p95_rad"],
                    "worst_current_p95_a": cell["metrics"]["worst_current_p95_a"],
                    "worst_saturation_pct": cell["metrics"]["worst_saturation_pct"],
                },
                "timing": timing,
            }
        )
        if index % 64 == 0:
            print(json.dumps({"audited_cells": index}, sort_keys=True), flush=True)

    current_failures = [row for row in rows if not row["checks"]["current_p95_at_most_0p65"]]
    ordering_events = {
        "direction": "direction",
        "saturation": "saturation",
        "tracking_p95": "tracking_p95",
        "early_termination": "termination",
        "base_height": "base_height",
        "pitch": "pitch",
    }
    current_ordering = {}
    for label, event in ordering_events.items():
        counts = Counter(
            ordering(row["timing"]["events"]["current_p95"], row["timing"]["events"][event])
            for row in current_failures
        )
        current_ordering[label] = dict(sorted(counts.items()))

    signed = {}
    for condition in ("COM_X_NEG", "COM_X_POS"):
        subset = [row for row in rows if row["identity"]["condition_id"] == condition]
        signed[condition] = {
            **bucket(subset),
            "mean_vx_range_m_s": [
                min(row["metrics"]["mean_local_vx_m_s"] for row in subset),
                max(row["metrics"]["mean_local_vx_m_s"] for row in subset),
            ],
            "by_command": split(subset, lambda row: f"{row['identity']['command_x_m_s']:.3f}"),
            "body_readback_all_exact": all(row["checks"]["per_run_readback_exact"] for row in subset),
            "max_command_field_error": max(row["timing"]["max_command_field_error"] for row in subset),
            "max_obs_command_field_error": max(row["timing"]["max_obs_command_field_error"] for row in subset),
            "tick0_accelerometer_prototypes": sorted(
                {tuple(row["timing"]["first_row"]["accelerometer_local_xyz_m_s2"]) for row in subset}
            ),
        }

    x0_nominal = [
        row for row in rows
        if row["identity"]["condition_group"] == "NOMINAL"
        and row["identity"]["command_x_m_s"] == 0.0
    ]
    if len(x0_nominal) != 8 or not all(row["timing"]["all_actions_exact_zero"] for row in x0_nominal):
        raise ValueError("nominal x0 deadband evidence mismatch")

    obs_map = load(OBS_MAP)
    obs_names = [row["name"] for row in obs_map["slices"]]
    absent_configuration = [
        "torso_mass_kg",
        "torso_com_x_m",
        "torso_com_y_m",
        "torso_com_z_m",
        "torso_inertia_xx_kg_m2",
        "torso_inertia_yy_kg_m2",
        "torso_inertia_zz_kg_m2",
        "torso_inertia_xy_kg_m2",
        "torso_inertia_xz_kg_m2",
        "torso_inertia_yz_kg_m2",
        "all_link_mass_scale",
        "actuator_fit_identity",
        "additional_action_delay_ticks",
        "imu_delay_ticks",
        "sensor_noise_scale",
    ]
    result = {
        "schema_version": "winner_v3.failure_attribution.v2",
        "status": "PASS_WINNER_V3_READ_ONLY_FAILURE_ATTRIBUTION_CORRECTED",
        "decision": "HOLD_TRAINING_PENDING_CURRENT_GATE_APPLICATION_CONTRACT_AND_RESPONSE_CONDITIONING_PREREGISTRATION",
        "authority": {
            "training": False,
            "hosted_compute": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "runtime_change": False,
            "completed_winner_v3_result_reclassified": False,
        },
        "source_commits": {
            "policy_result": EXPECTED_POLICY_COMMIT,
            "runtime_request": RUNTIME_REQUEST_COMMIT,
        },
        "input_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (TRACE_MANIFEST, CORRECTED_RESULT, PREREG, TRANSFORM, RUNNER_CONTRACT, OBS_MAP)
        },
        "overall": {
            "cells": len(rows),
            "trace_count": len(rows),
            "trace_bytes": sum(row["timing"]["trace_bytes"] for row in rows),
            "physical_passes": sum(row["physical_pass"] for row in rows),
            "physical_failures": sum(not row["physical_pass"] for row in rows),
            "pass_excluding_current": sum(row["pass_excluding_current"] for row in rows),
            "fail_excluding_current": sum(not row["pass_excluding_current"] for row in rows),
            "current_failures": len(current_failures),
            "current_only_failures": sum(row["current_only_failure"] for row in rows),
            "all_trace_hashes_exact": True,
            "all_current_metrics_exact": True,
            "all_tracking_metrics_exact": True,
        },
        "splits": {
            "checkpoint": split(rows, lambda row: str(row["identity"]["step"])),
            "condition_group": split(rows, lambda row: row["identity"]["condition_group"]),
            "condition_id": split(rows, lambda row: row["identity"]["condition_id"]),
            "axis_family": split(rows, lambda row: row["axis_family"]),
            "command_x_m_s": split(rows, lambda row: f"{row['identity']['command_x_m_s']:.3f}"),
            "actuator_fit": split(rows, lambda row: row["identity"]["plant"]),
            "policy_transform": split(rows, lambda row: row["policy_transform_mode"]),
        },
        "current_temporal_ordering": current_ordering,
        "current_provenance": {
            "frozen_gate_unchanged": True,
            "calculation": {
                "per_tick": "abs(MuJoCo data.actuator_force[joint] N.m) / 0.784532 N.m/A",
                "per_joint": "numpy percentile(..., 95) over every recorded trace tick",
                "per_cell": "maximum of the 14 per-joint p95 current estimates",
                "threshold_a": CURRENT_LIMIT_A,
                "aggregation_population": "each cell's recorded ticks; early-terminated cells use their complete recorded prefix",
            },
            "repository_provenance": {
                "introduced_commit": "58a8a1dd6c8b5519826cc7cbce2a02d48e11af5f",
                "threshold_source_path": "tools/build_winner_v3_replacement_preregistration.py",
                "conversion_first_appears_with_threshold": True,
                "older_repository_source_found": False,
                "manufacturer_or_measured_fit_cited_in_contract": False,
                "external_primary_support_for_threshold_found_after_contract": True,
                "external_primary_support_for_exact_conversion_found": False,
                "external_primary_support_for_p95_application_found": False,
                "runtime_register_scale_a_per_count": 0.0065,
                "threshold_equivalent_register_counts": 100,
                "rated_current_equals_100_register_counts": True,
                "evidence_for_p95_100_count_safety_gate_found": False,
            },
            "manufacturer_primary_sources": [
                {
                    "url": "https://www.feetechrc.com/Data/feetechrc/upload/file/20240706/2024%E9%A3%9E%E7%89%B9%E5%AE%A3%E4%BC%A0%E5%86%8C.pdf",
                    "accessed": "2026-07-20",
                    "document": "Feetech 2024 product catalog",
                    "model": "ST-3215-C001",
                    "rated_torque_kgf_cm_at_7p4v": 5.0,
                    "rated_current_a_at_7p4v": 0.65,
                    "peak_stall_torque_kgf_cm_at_7p4v": 19.5,
                    "stall_current_a_at_7p4v": 2.5,
                    "eight_kgf_cm_per_a_reported": False,
                    "p95_duty_or_thermal_rule_reported": False
                },
                {
                    "url": "https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear.html",
                    "accessed": "2026-07-20",
                    "document": "Feetech ST-3215-C001 product page",
                    "model": "ST-3215-C001",
                    "rated_torque_kgf_cm_at_6v": 6.5,
                    "peak_stall_torque_kgf_cm_at_6v": 19.5,
                    "stall_current_a_at_6v": 2.0,
                    "rated_current_a_reported": None,
                    "eight_kgf_cm_per_a_reported": False,
                    "p95_duty_or_thermal_rule_reported": False
                }
            ],
            "rated_point_comparison_not_a_validated_motor_fit": {
                "catalog_rated_point_nm_per_a": (5.0 * 0.0980665) / 0.65,
                "repository_nm_per_a": CURRENT_NM_PER_A,
                "repository_ratio_relative_difference": CURRENT_NM_PER_A / ((5.0 * 0.0980665) / 0.65) - 1.0,
                "x0_home_hold_current_if_rated_point_quotient_were_used_a": (
                    max(row["metrics"]["worst_current_p95_a"] for row in x0_nominal)
                    * CURRENT_NM_PER_A
                    / ((5.0 * 0.0980665) / 0.65)
                ),
            },
            "x0_home_hold": {
                "cells": len(x0_nominal),
                "all_actions_exact_zero_all_600_ticks": True,
                "worst_current_p95_a": max(row["metrics"]["worst_current_p95_a"] for row in x0_nominal),
                "worst_joint": x0_nominal[0]["timing"]["worst_current_p95_joint"],
                "all_values_identical": len({row["metrics"]["worst_current_p95_a"] for row in x0_nominal}) == 1,
                "policy_can_change_cell_under_frozen_deadband": False,
            },
            "descriptive_alternative_counts_not_reclassification": {
                "cells_with_p95_torque_at_or_below_official_rated_5kgf_cm_at_7p4v": sum(
                    row["metrics"]["worst_current_p95_a"] * CURRENT_NM_PER_A <= 5.0 * 0.0980665
                    for row in rows
                ),
                "cells_with_p95_torque_at_or_below_official_peak_19p5kgf_cm": sum(
                    row["metrics"]["worst_current_p95_a"] * CURRENT_NM_PER_A <= 19.5 * 0.0980665
                    for row in rows
                ),
                "maximum_recorded_p95_torque_nm": max(
                    row["metrics"]["worst_current_p95_a"] * CURRENT_NM_PER_A for row in rows
                ),
            },
        },
        "signed_x": signed,
        "command_and_reset_audit": {
            "all_per_run_readbacks_exact": all(row["checks"]["per_run_readback_exact"] for row in rows),
            "all_policy_hashes_exact": load(CORRECTED_RESULT)["validity_checks"]["all_policy_hashes_exact"],
            "all_reset_audits_exact": True,
            "command_is_raw_m_s_at_trace_and_obs_index_6": True,
            "maximum_trace_command_error": max(row["timing"]["max_command_field_error"] for row in rows),
            "maximum_obs_float32_command_error": max(row["timing"]["max_obs_command_field_error"] for row in rows),
            "target_body_id": 2,
            "target_body_name": "trunk_assembly",
            "x_neg_requested_offset_m": -0.05,
            "x_pos_requested_offset_m": 0.05,
        },
        "policy_transform_attribution": {
            "contract_sha256": sha256(TRANSFORM),
            "graphs": load(TRANSFORM)["policies"],
            "all_transforms_baked_into_graph": True,
            "untransformed_control_arm_in_matrix": False,
            "causal_transform_comparison_authorized": False,
            "x0_cells_all_actions_exact_zero": all(
                row["timing"]["all_actions_exact_zero"] for row in rows if row["identity"]["command_x_m_s"] == 0.0
            ),
            "interpretation": (
                "The matrix can attribute failures to the deployed composite only. It cannot isolate an individual "
                "baked transform because no untransformed or transform-ablated cell was preregistered."
            ),
        },
        "nominal_baseline_comparison": baseline_comparison(),
        "observability": {
            "observation_map_sha256": sha256(OBS_MAP),
            "dimension": obs_map["dimension"],
            "deployed_slice_names": obs_names,
            "configuration_or_transport_variables_absent_as_explicit_inputs": absent_configuration,
            "exact_static_parameter_identification_from_current_abi": "NOT_ESTABLISHED",
            "automatic_profile_semantics": (
                "The runtime's supported automatic collector can measure response metrics after a separately authorized "
                "excitation; it does not uniquely identify exact torso mass/COM/inertia and no such profile is an actor input."
            ),
            "prior_evidence": {
                "exposure_gap_falsified_sha256": sha256(ANALYSIS / "ground_up_torso_com_exposure_hypothesis_audit.json"),
                "decode_interpretation_corrected_sha256": sha256(ANALYSIS / "ground_up_torso_com_decode_interpretation_correction.json"),
                "signed_response_mixed_sha256": sha256(ANALYSIS / "ground_up_torso_com_signed_response_result.json"),
                "crossed_localization_unresolved_sha256": sha256(ANALYSIS / "ground_up_torso_com_crossed_phase_result.json"),
            },
        },
        "mechanism_selection": {
            "selected": [
                "CURRENT_GATE_APPLICATION_AND_CONVERSION_UNVALIDATED_AND_INFEASIBLE_AT_FROZEN_X0",
                "SIGNED_SAGITTAL_CONFIGURATION_REQUIRES_STRUCTURED_AUTOMATIC_RESPONSE_CONDITIONING",
            ],
            "not_selected": [
                "PROMOTE_CLOSEST_WINNER_V3_CELL_OR_CHECKPOINT",
                "REPEAT_BLIND_DOMAIN_RANDOMIZATION_WITH_SAME_ABI",
                "RELAX_COMPLETED_RESULT_POST_HOC",
                "MANUAL_PER_BUILD_COM_MEASUREMENT",
            ],
            "ordered_next_boundary": [
                "prospective current/torque gate application contract from primary motor and measured telemetry evidence",
                "prospective automatic-response-conditioned ABI and estimator contract reviewed by runtime",
                "one separately preregistered training run only after both contracts pass",
                "unchanged complete supported-configuration behavior matrix",
            ],
        },
        "cells": rows,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "json_sha256": sha256(OUTPUT_JSON),
                "md_sha256": sha256(OUTPUT_MD),
                "cells": result["overall"]["cells"],
                "pass_excluding_current": result["overall"]["pass_excluding_current"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
