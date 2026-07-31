#!/usr/bin/env python3
"""Read-only attribution of the closed winner-v7 actuator-protection failure."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v7_actuator_force_limit_attribution_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v7_actuator_force_limit_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_ACTUATOR_FORCE_LIMIT_ATTRIBUTION_20260720.md"

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


def max_consecutive(flags: list[bool]) -> int:
    longest = 0
    current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        longest = max(longest, current)
    return longest


def model_contract(model_xml: Path, scene_xml: Path) -> dict[str, Any]:
    model_root = ET.parse(model_xml).getroot()
    defaults = [
        node
        for default in model_root.findall(".//default")
        if default.attrib.get("class") == "sts3215"
        for node in default.findall("position")
    ]
    if len(defaults) != 1:
        raise ValueError(f"expected one sts3215 position default, found {len(defaults)}")
    force_range = [float(value) for value in defaults[0].attrib["forcerange"].split()]
    actuators_parent = model_root.find("actuator")
    if actuators_parent is None:
        raise ValueError("model XML has no actuator section")
    actuators = list(actuators_parent.findall("position"))
    names = [node.attrib.get("name") for node in actuators]
    classes = [node.attrib.get("class") for node in actuators]
    scene_root = ET.parse(scene_xml).getroot()
    includes = [node.attrib.get("file") for node in scene_root.findall("include")]
    return {
        "actuator_count": len(actuators),
        "actuator_names": names,
        "all_actuators_use_sts3215_default": all(value == "sts3215" for value in classes),
        "force_range_nm": force_range,
        "force_limit_magnitude_nm": max(abs(value) for value in force_range),
        "range_is_symmetric": len(force_range) == 2 and force_range[0] == -force_range[1],
        "scene_includes_model": model_xml.name in includes,
    }


def iter_trace_specs(source: dict[str, Any]):
    for condition in source["conditions"]:
        for fit_name, fit in condition["matrices"].items():
            for checkpoint, evaluation in fit.items():
                for trace in evaluation["current"]["traces"]:
                    yield {
                        "condition": condition["id"],
                        "expected_condition_behavior": condition["expected"],
                        "condition_behavior_expectation_pass": condition[
                            "behavior_expectation_pass"
                        ],
                        "fit": fit_name,
                        "checkpoint": checkpoint,
                        "trace": trace,
                    }


def audit_trace(
    spec: dict[str, Any],
    *,
    motor_constant_nm_per_a: float,
    peak_current_a_max: float,
    peak_torque_nm_max: float,
    overcurrent_threshold_a: float,
    overcurrent_max_consecutive: int,
    model_force_limit_nm: float,
    ceiling_tolerance_nm: float,
) -> dict[str, Any]:
    trace_spec = spec["trace"]
    path = Path(trace_spec["path"])
    if not path.is_file():
        raise FileNotFoundError(path)
    if sha256(path) != trace_spec["sha256"]:
        raise ValueError(f"trace hash mismatch: {path}")

    rows: list[dict[str, Any]] = []
    forces: list[list[float]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_index, line in enumerate(stream):
            row = json.loads(line)
            if int(row["tick"]) != line_index:
                raise ValueError(f"noncontiguous trace tick: {path}:{line_index}")
            if not finite(row):
                raise ValueError(f"nonfinite trace row: {path}:{line_index}")
            force = [float(value) for value in row["actuator_force_nm"]]
            if len(force) != len(JOINT_NAMES):
                raise ValueError(f"wrong actuator-force width: {path}:{line_index}")
            forces.append(force)
            rows.append(row)
    if len(rows) != int(trace_spec["rows"]):
        raise ValueError(f"trace row-count mismatch: {path}")

    per_joint_peak = [
        max(abs(row[joint_index]) for row in forces)
        for joint_index in range(len(JOINT_NAMES))
    ]
    peak_joint_index = max(range(len(JOINT_NAMES)), key=per_joint_peak.__getitem__)
    peak_tick = max(
        range(len(forces)), key=lambda index: abs(forces[index][peak_joint_index])
    )
    peak_torque_nm = per_joint_peak[peak_joint_index]
    peak_current_a = peak_torque_nm / motor_constant_nm_per_a
    consecutive_by_joint = [
        max_consecutive(
            [
                abs(row[joint_index]) / motor_constant_nm_per_a
                > overcurrent_threshold_a
                for row in forces
            ]
        )
        for joint_index in range(len(JOINT_NAMES))
    ]
    ceiling_hits = [
        (tick, joint_index)
        for tick, row in enumerate(forces)
        for joint_index, value in enumerate(row)
        if abs(abs(value) - model_force_limit_nm) <= ceiling_tolerance_nm
    ]
    context: list[dict[str, Any]] = []
    for index in range(max(0, peak_tick - 3), min(len(rows), peak_tick + 4)):
        row = rows[index]
        context.append(
            {
                "tick": index,
                "action": float(row["action"][peak_joint_index]),
                "applied_target_rad": float(row["applied_target_rad"][peak_joint_index]),
                "sent_target_rad": float(row["sent_target_rad"][peak_joint_index]),
                "actual_position_rad": float(row["actual_position_rad"][peak_joint_index]),
                "actuator_force_nm": float(row["actuator_force_nm"][peak_joint_index]),
            }
        )

    reported_error = abs(
        peak_current_a - float(trace_spec["worst_peak_current_a"])
    )
    if reported_error > 1e-12:
        raise ValueError(f"reported peak-current replay mismatch: {path}: {reported_error}")

    return {
        "identity": {
            "condition": spec["condition"],
            "fit": spec["fit"],
            "checkpoint": spec["checkpoint"],
            "command_x": float(trace_spec["command_x"]),
        },
        "trace": {
            "path": str(path),
            "rows": len(rows),
            "sha256": trace_spec["sha256"],
        },
        "peak": {
            "joint": JOINT_NAMES[peak_joint_index],
            "tick": peak_tick,
            "torque_nm": peak_torque_nm,
            "current_a": peak_current_a,
            "hits_model_force_ceiling": abs(peak_torque_nm - model_force_limit_nm)
            <= ceiling_tolerance_nm,
        },
        "gates": {
            "peak_current_pass": peak_current_a <= peak_current_a_max,
            "peak_torque_pass": peak_torque_nm <= peak_torque_nm_max,
            "overcurrent_duration_pass": max(consecutive_by_joint)
            <= overcurrent_max_consecutive,
            "maximum_consecutive_ticks_above_2a": max(consecutive_by_joint),
        },
        "model_ceiling_hit_count": len(ceiling_hits),
        "model_ceiling_hit_joints": sorted(
            {JOINT_NAMES[joint_index] for _, joint_index in ceiling_hits}
        ),
        "peak_context": context,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-xml", type=Path, required=True)
    parser.add_argument("--scene-xml", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v7 actuator-force attribution already exists")

    prereg = load(PREREG)
    frozen = prereg["frozen_inputs"]
    source_path = ROOT / frozen["winner_v7_result"]["path"]
    current_contract_path = ROOT / frozen["current_gate_contract"]["path"]
    source_prereg_path = ROOT / frozen["winner_v7_preregistration"]["path"]
    for path, expected in (
        (source_path, frozen["winner_v7_result"]["sha256"]),
        (current_contract_path, frozen["current_gate_contract"]["sha256"]),
        (source_prereg_path, frozen["winner_v7_preregistration"]["sha256"]),
        (Path(__file__), frozen["audit_tool_sha256"]),
        (args.model_xml, frozen["model_xml_sha256"]),
        (args.scene_xml, frozen["scene_xml_sha256"]),
    ):
        if sha256(path) != expected:
            raise ValueError(f"frozen input mismatch: {path}")

    source = load(source_path)
    current_contract = load(current_contract_path)
    source_prereg = load(source_prereg_path)
    model = model_contract(args.model_xml, args.scene_xml)
    gate = current_contract["prospective_offline_candidate_gate"]
    motor_constant = float(current_contract["conversion"]["manufacturer_motor_constant_nm_per_a"])
    trace_audits = [
        audit_trace(
            spec,
            motor_constant_nm_per_a=motor_constant,
            peak_current_a_max=float(gate["per_joint_peak_current_a_max"]),
            peak_torque_nm_max=float(gate["per_joint_peak_torque_nm_max"]),
            overcurrent_threshold_a=float(gate["strict_overcurrent_threshold_a"]),
            overcurrent_max_consecutive=int(gate["strict_overcurrent_max_consecutive_ticks"]),
            model_force_limit_nm=float(model["force_limit_magnitude_nm"]),
            ceiling_tolerance_nm=float(prereg["analysis_contract"]["ceiling_tolerance_nm"]),
        )
        for spec in iter_trace_specs(source)
    ]
    moving = [row for row in trace_audits if row["identity"]["command_x"] > 0.0]
    zero = [row for row in trace_audits if row["identity"]["command_x"] == 0.0]
    physical_limit = min(
        float(gate["per_joint_peak_torque_nm_max"]),
        float(gate["per_joint_peak_current_a_max"]) * motor_constant,
    )
    checks = {
        "source_winner_v7_remains_closed": source["decision"] == "CLOSE_WINNER_V7_PROTECTED_BASE",
        "source_population_complete": len(trace_audits) == 128 and len(moving) == 96 and len(zero) == 32,
        "source_behavior_expectations_preserved": source["checks"]["all_conditions_match_frozen_behavior_expectation"] is True,
        "model_scene_binding_exact": model["scene_includes_model"] is True,
        "all_14_actuators_share_sts3215_force_range": model["actuator_count"] == 14
        and model["actuator_names"] == list(JOINT_NAMES)
        and model["all_actuators_use_sts3215_default"] is True
        and model["range_is_symmetric"] is True,
        "simulator_force_limit_exceeds_frozen_physical_limit": model["force_limit_magnitude_nm"] > physical_limit,
        "all_moving_traces_fail_peak_current": all(not row["gates"]["peak_current_pass"] for row in moving),
        "all_moving_traces_fail_peak_torque": all(not row["gates"]["peak_torque_pass"] for row in moving),
        "all_moving_trace_peaks_hit_model_force_ceiling": all(row["peak"]["hits_model_force_ceiling"] for row in moving),
        "all_moving_trace_peaks_are_head_roll": all(row["peak"]["joint"] == "head_roll" for row in moving),
        "all_zero_traces_pass_peak_current_and_torque": all(
            row["gates"]["peak_current_pass"] and row["gates"]["peak_torque_pass"]
            for row in zero
        ),
        "no_trace_reaches_duration_trip": all(row["gates"]["overcurrent_duration_pass"] for row in trace_audits),
        "source_runner_omitted_frozen_torque_gate": "per_joint_peak_torque_nm_max"
        not in source_prereg["current_gate"],
    }
    selection_keys = prereg["selection_rule"]["all_checks_required"]
    selected = all(checks[key] for key in selection_keys)
    decision = (
        "SELECT_DISTINCT_PHYSICAL_STS3215_FORCE_LIMIT_CONTRACT"
        if selected
        else "CLOSE_PHYSICAL_FORCE_LIMIT_ATTRIBUTION_ROUTE"
    )
    peak_joint_counts = Counter(row["peak"]["joint"] for row in trace_audits)
    failed_current = [row for row in trace_audits if not row["gates"]["peak_current_pass"]]
    failed_torque = [row for row in trace_audits if not row["gates"]["peak_torque_pass"]]
    worst = max(trace_audits, key=lambda row: row["peak"]["current_a"])
    payload = {
        "schema_version": "open_duck_mini.winner_v7_actuator_force_limit_attribution.v1",
        "status": "PASS_WINNER_V7_ACTUATOR_FORCE_LIMIT_ATTRIBUTION" if selected else "HOLD_WINNER_V7_ACTUATOR_FORCE_LIMIT_ATTRIBUTION",
        "decision": decision,
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_selection_checks": [key for key in selection_keys if not checks[key]],
        "model_contract": model,
        "physical_gate": {
            "motor_constant_nm_per_a": motor_constant,
            "peak_current_a_max": gate["per_joint_peak_current_a_max"],
            "peak_torque_nm_max": gate["per_joint_peak_torque_nm_max"],
            "selected_force_limit_nm": physical_limit,
            "selected_limit_current_equivalent_a": physical_limit / motor_constant,
        },
        "population": {
            "traces": len(trace_audits),
            "moving_traces": len(moving),
            "zero_command_traces": len(zero),
            "peak_current_failures": len(failed_current),
            "peak_torque_failures": len(failed_torque),
            "peak_joint_counts": dict(sorted(peak_joint_counts.items())),
            "maximum_consecutive_ticks_above_2a": max(
                row["gates"]["maximum_consecutive_ticks_above_2a"]
                for row in trace_audits
            ),
        },
        "gate_contract_correction": {
            "winner_v7_source_omitted_peak_torque_check": checks[
                "source_runner_omitted_frozen_torque_gate"
            ],
            "omission_changed_closed_result": False,
            "reason": "the peak-current rule already closed winner-v7; the distinct route must enforce both frozen peak-current and peak-torque limits",
        },
        "worst_trace": worst,
        "trace_audits": trace_audits,
        "authority": {
            "winner_v7_reclassified_or_retried": False,
            "simulator_or_policy_mutated": False,
            "behavior_rerun": False,
            "training_or_gpu": False,
            "robot_rdkx5_torque_motion_gate5": False,
            "distinct_zero_behavior_contract_authorized_next": selected,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "# Winner-v7 Actuator Force-Limit Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{decision}`\n\n"
        f"- traces replayed: `{len(trace_audits)}` (`{len(moving)}` moving, `{len(zero)}` x=0)\n"
        f"- peak-current failures: `{len(failed_current)}`\n"
        f"- peak-torque failures: `{len(failed_torque)}`\n"
        f"- simulator force limit: `{model['force_limit_magnitude_nm']}` N.m\n"
        f"- frozen physical force limit: `{physical_limit}` N.m\n"
        f"- worst peak: `{worst['peak']['current_a']}` A at `{worst['peak']['joint']}` tick `{worst['peak']['tick']}`\n\n"
        "The closed winner-v7 result is unchanged. This read-only audit may select only a distinct, default-off simulator force-limit contract; it does not authorize a behavior rerun, training, deployment, robot access, torque, motion, or Gate 5.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"DECISION={decision}")
    print(f"OUTPUT_SHA256={sha256(OUTPUT_JSON)}")
    return 0 if selected else 2


if __name__ == "__main__":
    raise SystemExit(main())
