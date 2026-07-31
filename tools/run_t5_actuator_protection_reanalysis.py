#!/usr/bin/env python3
"""Reclassify frozen nominal traces under the documented STS3215 protection timing."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t5_actuator_protection_reanalysis_preregistration.json"
RESULT = ANALYSIS / "t5_actuator_protection_reanalysis_result.json"
MARKDOWN = ANALYSIS / "T5_ACTUATOR_PROTECTION_REANALYSIS_RESULT_20260725.md"

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
OLD_INSTANTANEOUS_FAILURES = frozenset(
    {
        "current_peak_at_most_2p5",
        "torque_peak_at_most_1p91229675_nm",
    }
)


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def longest_true_run(values: Iterable[bool]) -> int:
    longest = 0
    current = 0
    for value in values:
        current = current + 1 if bool(value) else 0
        longest = max(longest, current)
    return longest


def duration_metrics(
    force_nm: np.ndarray,
    *,
    motor_constant_nm_per_a: float,
    overcurrent_threshold_a: float,
    overload_threshold_nm: float,
    trip_ticks: int,
) -> dict[str, Any]:
    absolute = np.abs(np.asarray(force_nm, dtype=np.float64))
    if absolute.ndim != 2 or absolute.shape[1] != len(JOINT_NAMES):
        raise ValueError("force matrix must have shape [ticks, 14]")
    if absolute.shape[0] == 0 or not np.all(np.isfinite(absolute)):
        raise ValueError("force matrix must be nonempty and finite")
    current = absolute / motor_constant_nm_per_a
    current_runs = [
        longest_true_run(current[:, joint] > overcurrent_threshold_a)
        for joint in range(len(JOINT_NAMES))
    ]
    overload_runs = [
        longest_true_run(absolute[:, joint] > overload_threshold_nm)
        for joint in range(len(JOINT_NAMES))
    ]
    worst_current_run = max(current_runs)
    worst_overload_run = max(overload_runs)
    return {
        "samples": int(absolute.shape[0]),
        "peak_torque_nm_by_joint": np.max(absolute, axis=0).tolist(),
        "peak_current_a_by_joint": np.max(current, axis=0).tolist(),
        "worst_peak_torque_nm": float(np.max(absolute)),
        "worst_peak_current_a": float(np.max(current)),
        "strict_overcurrent_run_ticks_by_joint": current_runs,
        "strict_overload_run_ticks_by_joint": overload_runs,
        "worst_strict_overcurrent_run_ticks": worst_current_run,
        "worst_strict_overload_run_ticks": worst_overload_run,
        "overcurrent_duration_pass": worst_current_run < trip_ticks,
        "overload_duration_pass": worst_overload_run < trip_ticks,
        "pass": worst_current_run < trip_ticks and worst_overload_run < trip_ticks,
    }


def corrected_failure_reasons(
    original: Iterable[str], duration: Mapping[str, Any]
) -> list[str]:
    failures = set(original) - OLD_INSTANTANEOUS_FAILURES
    if not duration["overcurrent_duration_pass"]:
        failures.add("overcurrent_gt_2a_reaches_100_consecutive_ticks")
    if not duration["overload_duration_pass"]:
        failures.add("overload_gt_80pct_stall_reaches_100_consecutive_ticks")
    return sorted(failures)


def clipping_metrics(
    rows: list[dict[str, Any]], model: Mapping[str, Any]
) -> dict[str, Any]:
    qpos_indices = np.asarray(model["qpos_indices"], dtype=int)
    qvel_indices = np.asarray(model["qvel_indices"], dtype=int)
    kp = np.asarray(model["kp_nm_per_rad"], dtype=np.float64)
    kv = np.asarray(model["kv_nm_s_per_rad"], dtype=np.float64)
    force_range = np.asarray(model["forcerange_nm"], dtype=np.float64)
    sim_dt_s = float(model["sim_dt_s"])
    tolerance = float(model["reconstruction_tolerance_nm"])

    qpos = np.asarray([row["qpos"] for row in rows], dtype=np.float64)
    qvel = np.asarray([row["qvel"] for row in rows], dtype=np.float64)
    applied = np.asarray(
        [row["applied_target_rad"] for row in rows], dtype=np.float64
    )
    actual_force = np.asarray(
        [row["actuator_force_nm"] for row in rows], dtype=np.float64
    )
    force_state = qpos[:, qpos_indices] - sim_dt_s * qvel[:, qvel_indices]
    unclipped = kp * (applied - force_state) - kv * qvel[:, qvel_indices]
    reconstructed = np.clip(unclipped, force_range[:, 0], force_range[:, 1])
    reconstruction_error = np.abs(reconstructed - actual_force)
    clipped = np.logical_or(
        unclipped < force_range[:, 0], unclipped > force_range[:, 1]
    )
    close = reconstruction_error <= tolerance
    return {
        "reconstruction_max_abs_error_nm": float(np.max(reconstruction_error)),
        "reconstruction_within_tolerance": bool(np.all(close)),
        "clipped_joint_ticks": int(np.count_nonzero(clipped)),
        "clipped_ticks": int(np.count_nonzero(np.any(clipped, axis=1))),
        "clipped_joints": [
            JOINT_NAMES[index]
            for index in range(len(JOINT_NAMES))
            if bool(np.any(clipped[:, index]))
        ],
        "unclipped_peak_torque_nm": float(np.max(np.abs(unclipped))),
        "actual_peak_torque_nm": float(np.max(np.abs(actual_force))),
    }


def read_trace(path: Path, *, expected_rows: int) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    forces: list[list[float]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_index, line in enumerate(stream):
            row = json.loads(line)
            if int(row["tick"]) != line_index:
                raise ValueError(f"noncontiguous tick in {path}:{line_index}")
            force = [float(value) for value in row["actuator_force_nm"]]
            if len(force) != len(JOINT_NAMES):
                raise ValueError(f"wrong force width in {path}:{line_index}")
            if not all(math.isfinite(value) for value in force):
                raise ValueError(f"nonfinite force in {path}:{line_index}")
            rows.append(row)
            forces.append(force)
    if len(rows) != expected_rows:
        raise ValueError(f"row count mismatch for {path}")
    return rows, np.asarray(forces, dtype=np.float64)


def verify_manifest(prereg: Mapping[str, Any]) -> None:
    for name, spec in prereg["repository_inputs"].items():
        path = Path(spec["path"])
        if not path.is_file() or sha256(path) != spec["sha256"]:
            raise ValueError(f"frozen repository input mismatch: {name}")
    for root_spec in prereg["external_run_manifests"].values():
        root = Path(root_spec["root"])
        for spec in root_spec["files"]:
            path = root / spec["relative_path"]
            if (
                not path.is_file()
                or path.stat().st_size != int(spec["bytes"])
                or sha256(path) != spec["sha256"]
            ):
                raise ValueError(f"frozen external input mismatch: {path}")


def audit_run(
    candidate_id: str,
    root_spec: Mapping[str, Any],
    *,
    protection: Mapping[str, Any],
    model: Mapping[str, Any],
    old_baseline_float32_nm: float,
    old_gate_nm: float,
) -> dict[str, Any]:
    root = Path(root_spec["root"])
    cell_specs = [
        spec
        for spec in root_spec["files"]
        if spec["relative_path"].startswith("cells/")
        and spec["relative_path"].endswith(".json")
    ]
    audits = []
    strict_between_sample_count = 0
    for spec in cell_specs:
        cell_path = root / spec["relative_path"]
        cell = load_json(cell_path)
        trace_path = Path(cell["trace"]["path"])
        if (
            not trace_path.is_file()
            or sha256(trace_path) != cell["trace"]["sha256"]
        ):
            raise ValueError(f"cell trace mismatch: {cell_path}")
        rows, force = read_trace(
            trace_path, expected_rows=int(cell["trace"]["rows"])
        )
        duration = duration_metrics(
            force,
            motor_constant_nm_per_a=float(
                protection["motor_constant_nm_per_a"]
            ),
            overcurrent_threshold_a=float(
                protection["overcurrent_threshold_a"]
            ),
            overload_threshold_nm=float(protection["overload_threshold_nm"]),
            trip_ticks=int(protection["trip_ticks"]),
        )
        failures = corrected_failure_reasons(cell["failure_reasons"], duration)
        cell_peak = float(np.max(np.abs(force)))
        strict_between_sample_count += int(
            np.count_nonzero(
                np.logical_and(
                    np.abs(force) > old_baseline_float32_nm,
                    np.abs(force) < old_gate_nm,
                )
            )
        )
        audits.append(
            {
                "identity": cell["identity"],
                "cell_sha256": spec["sha256"],
                "trace": {
                    "path": str(trace_path),
                    "sha256": cell["trace"]["sha256"],
                    "rows": int(cell["trace"]["rows"]),
                },
                "original": {
                    "pass": bool(cell["pass"]),
                    "failure_reasons": list(cell["failure_reasons"]),
                },
                "corrected": {
                    "pass": not failures,
                    "failure_reasons": failures,
                    "duration_protection": duration,
                },
                "simulator_force_clipping": clipping_metrics(rows, model),
                "cell_peak_strictly_between_old_baseline_and_gate": bool(
                    old_baseline_float32_nm < cell_peak < old_gate_nm
                ),
            }
        )

    checkpoint_ids = sorted(
        {row["identity"]["checkpoint_id"] for row in audits}
    )
    checkpoints = []
    for checkpoint_id in checkpoint_ids:
        selected = [
            row
            for row in audits
            if row["identity"]["checkpoint_id"] == checkpoint_id
        ]
        checkpoints.append(
            {
                "checkpoint_id": checkpoint_id,
                "cells": len(selected),
                "original_passing_cells": sum(
                    row["original"]["pass"] for row in selected
                ),
                "corrected_passing_cells": sum(
                    row["corrected"]["pass"] for row in selected
                ),
                "corrected_all_cells_pass": bool(selected)
                and all(row["corrected"]["pass"] for row in selected),
            }
        )
    expected_cells = int(root_spec["expected_cells"])
    corrected_complete_pass = (
        len(audits) == expected_cells
        and all(row["corrected"]["pass"] for row in audits)
    )
    return {
        "candidate_id": candidate_id,
        "expected_cells": expected_cells,
        "completed_cells": len(audits),
        "matrix_complete": len(audits) == expected_cells,
        "original_passing_cells": sum(
            row["original"]["pass"] for row in audits
        ),
        "corrected_passing_cells": sum(
            row["corrected"]["pass"] for row in audits
        ),
        "corrected_complete_pass": corrected_complete_pass,
        "checkpoints": checkpoints,
        "worst_strict_overcurrent_run_ticks": max(
            row["corrected"]["duration_protection"][
                "worst_strict_overcurrent_run_ticks"
            ]
            for row in audits
        ),
        "worst_strict_overload_run_ticks": max(
            row["corrected"]["duration_protection"][
                "worst_strict_overload_run_ticks"
            ]
            for row in audits
        ),
        "worst_peak_current_a_diagnostic": max(
            row["corrected"]["duration_protection"]["worst_peak_current_a"]
            for row in audits
        ),
        "worst_peak_torque_nm_diagnostic": max(
            row["corrected"]["duration_protection"]["worst_peak_torque_nm"]
            for row in audits
        ),
        "simulator_clipped_joint_ticks": sum(
            row["simulator_force_clipping"]["clipped_joint_ticks"]
            for row in audits
        ),
        "simulator_force_reconstruction_max_error_nm": max(
            row["simulator_force_clipping"][
                "reconstruction_max_abs_error_nm"
            ]
            for row in audits
        ),
        "strict_between_old_baseline_and_gate_samples": (
            strict_between_sample_count
        ),
        "cells": audits,
    }


def baseline_clamp_audit(
    contract: Mapping[str, Any], nominal: Mapping[str, Any], old_gate_nm: float
) -> dict[str, Any]:
    represented = float(contract["xml"]["represented_positive_float32_nm"])
    next_float32 = float(
        np.nextafter(np.float32(represented), np.float32(np.inf))
    )
    moving = []
    for plant in ("p30", "p31_34"):
        for checkpoint in ("half", "final"):
            for trace in nominal["matrices"][plant][checkpoint]["traces"]:
                if float(trace["command_x"]) > 0.0:
                    moving.append(trace)
    return {
        "represented_positive_float32_nm": represented,
        "old_decimal_gate_nm": old_gate_nm,
        "next_float32_nm": next_float32,
        "no_float32_value_strictly_between": (
            represented < old_gate_nm <= next_float32
        ),
        "moving_trace_count": len(moving),
        "all_moving_peaks_equal_model_force_limit": all(
            float(row["worst_peak_torque_nm"]) == represented for row in moving
        ),
        "all_moving_traces_report_force_limit_hits": all(
            int(row["force_limit_hit_ticks"]) > 0 for row in moving
        ),
        "moving_force_limit_hit_ticks": sum(
            int(row["force_limit_hit_ticks"]) for row in moving
        ),
        "conclusion": (
            "V10's baseline peak is the configured MuJoCo force clamp, not "
            "an independently measured natural policy peak."
        ),
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Candidate | Original | Corrected | Current run | Overload run | Status |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        status = (
            "PASS"
            if row["corrected_complete_pass"]
            else "REOPEN_INCOMPLETE"
            if not row["matrix_complete"]
            and row["corrected_passing_cells"] == row["completed_cells"]
            else "HOLD"
        )
        lines.append(
            f"| {row['candidate_id']} | "
            f"{row['original_passing_cells']}/{row['completed_cells']} | "
            f"{row['corrected_passing_cells']}/{row['completed_cells']} | "
            f"{row['worst_strict_overcurrent_run_ticks']} | "
            f"{row['worst_strict_overload_run_ticks']} | {status} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T5 result")
    prereg = load_json(PREREG)
    if (
        prereg["status"]
        != "PREREGISTERED_T5_ACTUATOR_PROTECTION_REANALYSIS"
        or prereg["failed_checks"]
    ):
        raise ValueError("T5 preregistration is not passing")
    verify_manifest(prereg)

    protection = prereg["corrected_protection_contract"]
    model = prereg["simulator_force_clipping_contract"]
    old_gate_nm = float(prereg["superseded_instantaneous_gate"]["torque_nm"])
    baseline_contract = load_json(
        Path(prereg["repository_inputs"]["v10_contract"]["path"])
    )
    baseline_nominal = load_json(
        Path(prereg["repository_inputs"]["v10_nominal"]["path"])
    )
    baseline = baseline_clamp_audit(
        baseline_contract, baseline_nominal, old_gate_nm
    )
    baseline_float32 = float(baseline["represented_positive_float32_nm"])

    candidate_rows = []
    for candidate_id in prereg["candidate_order"]:
        candidate_rows.append(
            audit_run(
                candidate_id,
                prereg["external_run_manifests"][candidate_id],
                protection=protection,
                model=model,
                old_baseline_float32_nm=baseline_float32,
                old_gate_nm=old_gate_nm,
            )
        )

    by_id = {row["candidate_id"]: row for row in candidate_rows}
    decision_population = prereg["decision_rule"][
        "previously_rejected_complete_candidates"
    ]
    corrected_passes = [
        candidate_id
        for candidate_id in decision_population
        if by_id[candidate_id]["corrected_complete_pass"]
    ]
    threshold = int(
        prereg["decision_rule"]["minimum_corrected_passes_to_reopen"]
    )
    reopen = len(corrected_passes) >= threshold
    partial_reopened = [
        row["candidate_id"]
        for row in candidate_rows
        if not row["matrix_complete"]
        and row["corrected_passing_cells"] == row["completed_cells"]
        and row["original_passing_cells"] < row["completed_cells"]
    ]
    all_reconstructions_close = all(
        row["simulator_force_reconstruction_max_error_nm"]
        <= float(model["reconstruction_tolerance_nm"])
        for row in candidate_rows
    )
    result_without_hash = {
        "schema_version": "open_duck.t5_actuator_protection_reanalysis.v1",
        "status": (
            "PASS_T5_MIS_SPECIFIED_INSTANTANEOUS_CONSTRAINT"
            if reopen and all_reconstructions_close
            else "HOLD_T5_ACTUATOR_PROTECTION_REANALYSIS"
        ),
        "decision": (
            "REOPEN_V121_V175_CAMPAIGN_CLOSURES"
            if reopen and all_reconstructions_close
            else "KEEP_V121_V175_CAMPAIGN_CLOSURES"
        ),
        "preregistration_sha256": sha256(PREREG),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "installed_variant": prereg["installed_variant"],
        "manufacturer_evidence": prereg["manufacturer_evidence"],
        "superseded_instantaneous_gate": prereg[
            "superseded_instantaneous_gate"
        ],
        "corrected_protection_contract": protection,
        "baseline_clamp_audit": baseline,
        "candidate_reanalysis": candidate_rows,
        "decision_summary": {
            "previously_rejected_complete_candidates": decision_population,
            "corrected_complete_passes": corrected_passes,
            "corrected_complete_pass_count": len(corrected_passes),
            "minimum_corrected_passes_to_reopen": threshold,
            "frozen_reopen_trigger_met": reopen,
            "partial_stop_rules_invalidated": partial_reopened,
            "post_handoff_v177_corrected_complete_pass": by_id["V177"][
                "corrected_complete_pass"
            ],
            "all_force_reconstructions_close": all_reconstructions_close,
            "strict_between_old_baseline_and_gate_samples": sum(
                row["strict_between_old_baseline_and_gate_samples"]
                for row in candidate_rows
            ),
        },
        "interpretation": {
            "instantaneous_stall_values": (
                "reported as actuator capability and saturation diagnostics; "
                "not used as one-tick protection trips"
            ),
            "simulated_force": (
                "MuJoCo actuator_force is a simulated actuator output/demand "
                "and does not prove a real servo delivered torque above stall"
            ),
            "temperature": (
                "not present in these simulation traces; runtime firmware "
                "protection and temperature telemetry remain mandatory"
            ),
            "partial_candidates": (
                "a corrected pass over every recorded prefix invalidates the "
                "old early-stop reason but cannot fill unrun cells"
            ),
        },
        "authority": {
            "offline_read_only": True,
            "simulation_cells_run": 0,
            "training_steps": 0,
            "policy_selected": False,
            "hosted_compute_authorized": False,
            "robot_rdkx5_gate5_torque_motion": False,
            "next_authorized_action": (
                "preregister a corrected-gate robustness revalidation of "
                "surviving frozen policies; do not train yet"
            ),
        },
    }
    result_without_hash["result_payload_sha256"] = canonical_sha256(
        result_without_hash
    )
    RESULT.write_text(
        json.dumps(
            result_without_hash,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T5 actuator-protection gate reanalysis\n\n"
        f"- Status: `{result_without_hash['status']}`\n"
        f"- Decision: `{result_without_hash['decision']}`\n"
        f"- Corrected full-matrix passes: `{len(corrected_passes)}/"
        f"{len(decision_population)}` (`{', '.join(corrected_passes)}`)\n"
        f"- V10 moving force-limit hits: "
        f"`{baseline['moving_force_limit_hit_ticks']}`\n"
        f"- Float32 values between V10 clamp and old decimal gate: `0`\n\n"
        + markdown_table(candidate_rows)
        + "\n\n"
        "The official [STS3215 A/0 specification](https://www.feetechrc.com/"
        "Data/feetechrc/upload/file/20200611/"
        "6372749961523760249976542.pdf) documents duration-triggered "
        "protection, not a one-tick trip at stall torque/current. This "
        "result reopens the affected offline closures but does not select a "
        "policy, authorize training, or open Gate 5.\n",
        encoding="utf-8",
    )
    print(result_without_hash["status"])
    print(f"decision={result_without_hash['decision']}")
    print(f"corrected_passes={','.join(corrected_passes)}")
    print(f"sha256={sha256(RESULT)}")
    return 0 if result_without_hash["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
