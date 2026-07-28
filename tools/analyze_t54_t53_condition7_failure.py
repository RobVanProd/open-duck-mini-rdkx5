#!/usr/bin/env python3
"""Attribute T53's negative torso-COM failure without new behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T53_RESULT = ANALYSIS / "t53_uniform_half_head_r2_remainder_result.json"
T52_RESULT = ANALYSIS / "t52_uniform_half_head_qualification_result.json"
OUTPUT = ANALYSIS / "t54_t53_condition7_failure_attribution.json"
MARKDOWN = ANALYSIS / "T54_T53_CONDITION7_FAILURE_ATTRIBUTION_20260728.md"
XML_RELATIVE = Path(
    "playground/open_duck_mini_v2/xmls/"
    "scene_flat_terrain_backlash.xml"
)
CHECKPOINTS = (
    "T52_UNIFORM_HALF_HEAD_HALF",
    "T52_UNIFORM_HALF_HEAD_FINAL",
)
FITS = ("p30", "p31_34")
COMMANDS = (0.0, 0.074, 0.077, 0.08)
MOVING_COMMANDS = COMMANDS[1:]
SEED = 167931544
PITCH_ONSET_RAD = -0.25

PRIOR_CLOSURES = {
    "targeted_com_training": (
        ANALYSIS
        / "GROUND_UP_TORSO_COM_REMEDIATION_BEHAVIOR_DECISION_20260715.md"
    ),
    "exposure_gap": (
        ANALYSIS
        / "GROUND_UP_TORSO_COM_EXPOSURE_HYPOTHESIS_AUDIT_20260715.md"
    ),
    "response_use": (
        ANALYSIS
        / "WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_RESULT_20260721.md"
    ),
    "terminal_support_objective": (
        ANALYSIS
        / "WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE_RESULT_20260722.md"
    ),
    "response_prefix": ANALYSIS / "T12_RESPONSE_PREFIX_COM_RESULT_20260726.md",
    "shadow_hidden": ANALYSIS / "T13_SHADOW_HIDDEN_RESULT_20260726.md",
    "gradient_conflict": (
        ANALYSIS / "T14_DOMAIN_GRADIENT_GEOMETRY_RESULT_20260726.md"
    ),
    "support_coordinate": (
        ANALYSIS / "T16_SUPPORT_COORDINATE_RESULT_20260726.md"
    ),
    "support_homeomorphism": (
        ANALYSIS / "T17_SUPPORT_HOMEOMORPHISM_RESULT_20260726.md"
    ),
    "rate_coherent_support": (
        ANALYSIS / "T18_RATE_COHERENT_SUPPORT_RESULT_20260726.md"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluation_path(
    cache_root: Path,
    condition_directory: str,
    checkpoint: str,
    fit: str,
) -> Path:
    return cache_root / condition_directory / checkpoint / fit / "evaluation.json"


def trace_path(
    cache_root: Path,
    condition_directory: str,
    checkpoint: str,
    fit: str,
    command: float,
) -> Path:
    return (
        cache_root
        / condition_directory
        / checkpoint
        / fit
        / "traces"
        / f"x{command:.3f}_seed{SEED}_action_margin.jsonl"
    )


def evaluation_runs(path: Path) -> dict[float, dict[str, Any]]:
    value = read_json(path)
    return {
        round(float(run["command_x"]), 3): run for run in value["runs"]
    }


def percentile(values: Iterable[float], q: float) -> float | None:
    array = np.asarray(list(values), dtype=np.float64)
    if not array.size:
        return None
    return float(np.percentile(array, q))


def pairwise_discrimination(
    passing: Iterable[float],
    failing: Iterable[float],
    *,
    lower_is_more_adverse: bool,
) -> float:
    passed = list(passing)
    failed = list(failing)
    score = 0.0
    for failure in failed:
        for success in passed:
            adverse = (
                failure < success
                if lower_is_more_adverse
                else failure > success
            )
            score += 1.0 if adverse else 0.5 if failure == success else 0.0
    return score / (len(passed) * len(failed))


def ranges_overlap(first: Iterable[float], second: Iterable[float]) -> bool:
    left = list(first)
    right = list(second)
    return max(min(left), min(right)) <= min(max(left), max(right))


def rms_action_delta(
    first: list[dict[str, Any]],
    second: list[dict[str, Any]],
    rows: int,
) -> float:
    count = min(rows, len(first), len(second))
    delta = np.asarray(
        [
            np.asarray(first[index]["action"], dtype=np.float64)
            - np.asarray(second[index]["action"], dtype=np.float64)
            for index in range(count)
        ]
    )
    return float(np.sqrt(np.mean(np.square(delta))))


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


class SupportReconstructor:
    """Reconstruct whole-body COM and the sagittal foot support interval."""

    def __init__(self, xml: Path) -> None:
        import mujoco

        self.mujoco = mujoco
        self.model = mujoco.MjModel.from_xml_path(str(xml))
        self.data = mujoco.MjData(self.model)
        if self.model.nq != 31 or self.model.nv != 30:
            raise RuntimeError(
                f"unexpected backlash model state: "
                f"nq={self.model.nq}, nv={self.model.nv}"
            )
        body_id = mujoco.mj_name2id(
            self.model,
            mujoco.mjtObj.mjOBJ_BODY,
            "trunk_assembly",
        )
        self.model.body_ipos[body_id, 0] -= 0.05
        self.feet: list[tuple[str, int, np.ndarray]] = []
        for side, name in (
            ("left", "left_foot_bottom_tpu"),
            ("right", "right_foot_bottom_tpu"),
        ):
            geom_id = mujoco.mj_name2id(
                self.model,
                mujoco.mjtObj.mjOBJ_GEOM,
                name,
            )
            mesh_id = int(self.model.geom_dataid[geom_id])
            vertex_address = int(self.model.mesh_vertadr[mesh_id])
            vertex_count = int(self.model.mesh_vertnum[mesh_id])
            vertices = self.model.mesh_vert[
                vertex_address : vertex_address + vertex_count
            ].copy()
            self.feet.append((side, geom_id, vertices))
        self.foot_geom_ids = {
            geom_id: side for side, geom_id, _ in self.feet
        }

    def _world_vertices(
        self,
        geom_id: int,
        vertices: np.ndarray,
    ) -> np.ndarray:
        rotation = self.data.geom_xmat[geom_id].reshape(3, 3)
        return (
            vertices @ rotation.T + self.data.geom_xpos[geom_id]
        )

    def row(self, value: dict[str, Any]) -> dict[str, Any]:
        self.data.qpos[:] = value["qpos"]
        self.data.qvel[:] = value["qvel"]
        self.data.ctrl[:] = value["ctrl"]
        self.mujoco.mj_forward(self.model, self.data)
        com = np.asarray(self.data.subtree_com[0], dtype=np.float64)
        com_velocity_x = float(self.data.subtree_linvel[0, 0])
        omega = np.sqrt(9.81 / max(float(com[2]), 1e-6))
        capture_x = float(com[0] + com_velocity_x / omega)
        support_intervals: list[tuple[float, float]] = []
        for active, (_, geom_id, vertices) in zip(
            value["foot_contacts"],
            self.feet,
        ):
            if active:
                world = self._world_vertices(geom_id, vertices)
                support_intervals.append(
                    (
                        float(np.min(world[:, 0])),
                        float(np.max(world[:, 0])),
                    )
                )
        support_margin = None
        if support_intervals:
            low = min(interval[0] for interval in support_intervals)
            high = max(interval[1] for interval in support_intervals)
            support_margin = min(capture_x - low, high - capture_x)

        pressure_points: list[tuple[float, float]] = []
        active_pressure_sides: set[str] = set()
        for contact_index in range(self.data.ncon):
            contact = self.data.contact[contact_index]
            geom_ids = (int(contact.geom[0]), int(contact.geom[1]))
            foot_geom_id = next(
                (
                    geom_id
                    for geom_id in geom_ids
                    if geom_id in self.foot_geom_ids
                ),
                None,
            )
            if foot_geom_id is None:
                continue
            force = np.zeros(6, dtype=np.float64)
            self.mujoco.mj_contactForce(
                self.model,
                self.data,
                contact_index,
                force,
            )
            normal_force = max(0.0, float(force[0]))
            if normal_force > 1e-8:
                pressure_points.append(
                    (float(contact.pos[0]), normal_force)
                )
                active_pressure_sides.add(
                    self.foot_geom_ids[foot_geom_id]
                )
        capture_minus_pressure = None
        if pressure_points:
            center_of_pressure_x = sum(
                position * force for position, force in pressure_points
            ) / sum(force for _, force in pressure_points)
            capture_minus_pressure = capture_x - center_of_pressure_x
        actuator_force_error = float(
            np.max(
                np.abs(
                    np.asarray(value["actuator_force_nm"], dtype=np.float64)
                    - np.asarray(self.data.actuator_force, dtype=np.float64)
                )
            )
        )
        return {
            "capture_point_x_m": capture_x,
            "whole_body_com_x_m": float(com[0]),
            "whole_body_com_z_m": float(com[2]),
            "capture_point_support_margin_m": support_margin,
            "capture_minus_center_of_pressure_m": capture_minus_pressure,
            "pressure_support_sides": sorted(active_pressure_sides),
            "actuator_force_reconstruction_max_abs_error_nm": (
                actuator_force_error
            ),
        }


def rolling_minimum_mean(values: list[float], width: int) -> float | None:
    if not values:
        return None
    if len(values) <= width:
        return float(np.mean(values))
    return min(
        float(np.mean(values[start : start + width]))
        for start in range(len(values) - width + 1)
    )


def support_diagnostic(
    reconstructor: SupportReconstructor,
    values: list[dict[str, Any]],
    onset_index: int | None,
) -> dict[str, Any]:
    limit = len(values) if onset_index is None else onset_index
    reconstructed = [
        reconstructor.row(row) for row in values[: max(1, limit)]
    ]
    margins = [
        float(row["capture_point_support_margin_m"])
        for row in reconstructed
        if row["capture_point_support_margin_m"] is not None
    ]
    pressure_delta = [
        float(row["capture_minus_center_of_pressure_m"])
        for row in reconstructed
        if row["capture_minus_center_of_pressure_m"] is not None
    ]
    left_margins = [
        float(row["capture_point_support_margin_m"])
        for row, source in zip(reconstructed, values)
        if source["foot_contacts"] == [1, 0]
        and row["capture_point_support_margin_m"] is not None
    ]
    return {
        "window_definition": (
            "ticks before first body_pitch_rad <= -0.25, "
            "or all ticks when no crossing occurs"
        ),
        "window_rows": len(reconstructed),
        "capture_point_support_margin_p05_m": percentile(margins, 5),
        "capture_point_outside_support_fraction": float(
            np.mean(np.asarray(margins) < 0.0)
        ),
        "left_single_support_rows": len(left_margins),
        "left_single_support_capture_margin_p05_m": percentile(
            left_margins,
            5,
        ),
        "left_single_support_outside_fraction": (
            float(np.mean(np.asarray(left_margins) < 0.0))
            if left_margins
            else None
        ),
        "capture_minus_pressure_rolling32_minimum_mean_m": (
            rolling_minimum_mean(pressure_delta, 32)
        ),
        "actuator_force_reconstruction_max_abs_error_nm": max(
            row["actuator_force_reconstruction_max_abs_error_nm"]
            for row in reconstructed
        ),
    }


def summarize_cell(
    *,
    checkpoint: str,
    fit: str,
    command: float,
    negative_run: dict[str, Any],
    nominal_run: dict[str, Any],
    negative_trace_path: Path,
    nominal_trace_path: Path,
    reconstructor: SupportReconstructor | None,
) -> dict[str, Any]:
    negative = read_rows(negative_trace_path)
    nominal = read_rows(nominal_trace_path)
    onset_index = next(
        (
            index
            for index, row in enumerate(negative)
            if float(row["body_pitch_rad"]) <= PITCH_ONSET_RAD
        ),
        None,
    )
    first_height_below = next(
        (
            index
            for index, row in enumerate(negative)
            if float(row["base_height_m"]) < 0.12
        ),
        None,
    )
    context_negative = negative_run["modes"]["fitted"][
        "response_calibration"
    ]["context_sha256"]
    context_nominal = nominal_run["modes"]["fitted"][
        "response_calibration"
    ]["context_sha256"]
    action_tick0_delta = float(
        np.max(
            np.abs(
                np.asarray(negative[0]["action"], dtype=np.float64)
                - np.asarray(nominal[0]["action"], dtype=np.float64)
            )
        )
    )
    candidate_status = negative_run["candidate_gate"]["status"]
    green = candidate_status == "PASS_CANDIDATE_SIM_GATE"
    result: dict[str, Any] = {
        "checkpoint_id": checkpoint,
        "fit_id": fit,
        "command_x_m_s": command,
        "cell_green": green,
        "candidate_gate_status": candidate_status,
        "samples": len(negative),
        "termination_reason": negative_run["modes"]["fitted"][
            "termination_reason"
        ],
        "mean_local_vx_m_s": negative_run["modes"]["fitted"][
            "local_forward_velocity_m_s"
        ]["mean"],
        "tracking_p95_rad": negative_run["candidate_gate"]["metrics"][
            "max_pitch_tracking_p95_rad"
        ],
        "action_saturation_pct": negative_run["candidate_gate"]["metrics"][
            "max_action_saturation_pct"
        ],
        "rate_excess_rad_s": negative_run["candidate_gate"]["metrics"][
            "max_sent_target_velocity_max_limit_excess_rad_s"
        ],
        "first_negative_pitch_0p25_tick": onset_index,
        "first_height_below_0p12_tick": first_height_below,
        "onset_foot_contacts": (
            None
            if onset_index is None
            else negative[onset_index]["foot_contacts"]
        ),
        "last_body_pitch_rad": float(negative[-1]["body_pitch_rad"]),
        "last_body_roll_rad": float(negative[-1]["body_roll_rad"]),
        "last_base_height_m": float(negative[-1]["base_height_m"]),
        "negative_trace": receipt(negative_trace_path),
        "matched_nominal_trace": receipt(nominal_trace_path),
        "response_use": {
            "negative_context_sha256": context_negative,
            "nominal_context_sha256": context_nominal,
            "context_changed": context_negative != context_nominal,
            "tick0_action_delta_max_abs": action_tick0_delta,
            "first32_action_delta_rms": rms_action_delta(
                negative,
                nominal,
                32,
            ),
            "first64_action_delta_rms": rms_action_delta(
                negative,
                nominal,
                64,
            ),
        },
    }
    if reconstructor is not None:
        result["dynamic_support"] = support_diagnostic(
            reconstructor,
            negative,
            onset_index,
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--t53-cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t53_uniform_half_head_r2_remainder_v1"
        ),
    )
    parser.add_argument(
        "--t52-cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t52_uniform_half_head_qualification_v1"
        ),
    )
    parser.add_argument(
        "--playground",
        type=Path,
        default=Path(
            r"D:\CodexProjects\Open_Duck_Playground-composed-t19-v6"
        ),
    )
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T54 output: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T54 formal execution requires a clean worktree")

    t53 = read_json(T53_RESULT)
    t52 = read_json(T52_RESULT)
    xml = args.playground / XML_RELATIVE
    reconstructor = SupportReconstructor(xml)
    cells: list[dict[str, Any]] = []
    for checkpoint in CHECKPOINTS:
        for fit in FITS:
            negative_evaluation = evaluation_path(
                args.t53_cache_root,
                "07_TORSO_COM_X_NEG",
                checkpoint,
                fit,
            )
            nominal_evaluation = evaluation_path(
                args.t52_cache_root,
                "02_FLOOR_FRICTION_HI",
                checkpoint,
                fit,
            )
            negative_runs = evaluation_runs(negative_evaluation)
            nominal_runs = evaluation_runs(nominal_evaluation)
            for command in COMMANDS:
                cells.append(
                    summarize_cell(
                        checkpoint=checkpoint,
                        fit=fit,
                        command=command,
                        negative_run=negative_runs[round(command, 3)],
                        nominal_run=nominal_runs[round(command, 3)],
                        negative_trace_path=trace_path(
                            args.t53_cache_root,
                            "07_TORSO_COM_X_NEG",
                            checkpoint,
                            fit,
                            command,
                        ),
                        nominal_trace_path=trace_path(
                            args.t52_cache_root,
                            "02_FLOOR_FRICTION_HI",
                            checkpoint,
                            fit,
                            command,
                        ),
                        reconstructor=(
                            reconstructor if command in MOVING_COMMANDS else None
                        ),
                    )
                )
    moving = [cell for cell in cells if cell["command_x_m_s"] > 0]
    passing = [cell for cell in moving if cell["cell_green"]]
    failing = [cell for cell in moving if not cell["cell_green"]]
    onset_support_counts = {"left_only": 0, "right_only": 0, "double": 0}
    for cell in failing:
        support = cell["onset_foot_contacts"]
        key = {
            (1, 0): "left_only",
            (0, 1): "right_only",
            (1, 1): "double",
        }.get(tuple(support))
        if key is not None:
            onset_support_counts[key] += 1

    margin_passing = [
        cell["dynamic_support"]["capture_point_support_margin_p05_m"]
        for cell in passing
    ]
    margin_failing = [
        cell["dynamic_support"]["capture_point_support_margin_p05_m"]
        for cell in failing
    ]
    pressure_passing = [
        cell["dynamic_support"][
            "capture_minus_pressure_rolling32_minimum_mean_m"
        ]
        for cell in passing
    ]
    pressure_failing = [
        cell["dynamic_support"][
            "capture_minus_pressure_rolling32_minimum_mean_m"
        ]
        for cell in failing
    ]
    failures_all_contract_clean = all(
        cell["tracking_p95_rad"] <= 0.2
        and cell["rate_excess_rad_s"] == 0.0
        and cell["action_saturation_pct"] == 0.0
        for cell in failing
    )
    failure_onsets = [
        cell["first_negative_pitch_0p25_tick"] for cell in failing
    ]
    moving_action_deltas = [
        cell["response_use"]["first32_action_delta_rms"]
        for cell in moving
    ]
    checks = {
        "t53_stopped_at_condition7": (
            t53["status"] == "HOLD_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
            and t53["decision"]
            == "STOP_T53_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE"
            and t53["summary"]["first_failed_condition"]
            == "TORSO_COM_X_NEG"
        ),
        "t52_nominal_source_green": (
            t52["status"] == "PASS_T52_UNIFORM_HALF_HEAD_QUALIFICATION"
            and all(
                block["result"]["block_green"]
                for block in t52["blocks"]
                if block["condition_id"] == "FLOOR_FRICTION_HI"
            )
        ),
        "condition7_exact_cell_count": len(cells) == 16,
        "condition7_green_split_exact": (
            sum(cell["cell_green"] for cell in cells) == 8
            and sum(
                cell["cell_green"]
                for cell in cells
                if cell["command_x_m_s"] == 0
            )
            == 4
            and len(passing) == 4
            and len(failing) == 8
        ),
        "all_failures_are_delayed_negative_pitch_falls": (
            all(
                cell["termination_reason"] == "fall_or_nan"
                and cell["first_negative_pitch_0p25_tick"] is not None
                and cell["first_negative_pitch_0p25_tick"] >= 100
                and cell["last_body_pitch_rad"] < -1.0
                for cell in failing
            )
            and min(failure_onsets) == 139
            and max(failure_onsets) == 382
        ),
        "failure_quality_contracts_remain_green": (
            failures_all_contract_clean
        ),
        "failure_onset_support_distribution_exact": (
            onset_support_counts
            == {"left_only": 6, "right_only": 0, "double": 2}
        ),
        "all_passing_cells_exercise_left_single_support": all(
            cell["dynamic_support"]["left_single_support_rows"] > 0
            for cell in passing
        ),
        "response_context_changes_for_every_cell": all(
            cell["response_use"]["context_changed"] for cell in cells
        ),
        "moving_actions_respond_nontrivially": min(moving_action_deltas) > 0,
        "capture_margin_ranges_overlap": ranges_overlap(
            margin_passing,
            margin_failing,
        ),
        "capture_pressure_ranges_overlap": ranges_overlap(
            pressure_passing,
            pressure_failing,
        ),
        "prior_closure_receipts_present": all(
            path.is_file() for path in PRIOR_CLOSURES.values()
        ),
        "no_new_behavior_or_training": True,
        "robot_or_rdk_zero": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed_checks = sorted(
        key for key, value in checks.items() if not value
    )
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t54_t53_condition7_failure_attribution.v1"
        ),
        "status": (
            "PASS_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
            if not failed_checks
            else "HOLD_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T55_DYNAMIC_SINGLE_SUPPORT_CURRICULUM_"
            "CPU_CONTRACT_PREREGISTRATION_ONLY"
            if not failed_checks
            else "STOP_T54_AND_REVIEW_ATTRIBUTION"
        ),
        "classification": (
            "NEGATIVE_COM_DYNAMIC_SUPPORT_CONTROL_INADEQUATE"
        ),
        "finding": (
            "T53 observes and acts on the changed plant, but the response "
            "does not preserve dynamic balance under the negative torso-COM "
            "endpoint. Failures are delayed backward-pitch collapses, six "
            "of eight crossing the diagnostic pitch boundary in left-only "
            "support. Passing cells also use left-only support, and neither "
            "capture-point support margin nor reconstructed pressure "
            "separates pass from failure. This supports only a CPU contract "
            "for a symmetric, training-only single-support curriculum; it "
            "does not earn hosted training."
        ),
        "source": {
            "repository_commit": git_head(),
            "t53_result": receipt(T53_RESULT),
            "t52_result": receipt(T52_RESULT),
            "model_xml": receipt(xml),
            "t53_cache_root": str(args.t53_cache_root.resolve()),
            "t52_cache_root": str(args.t52_cache_root.resolve()),
            "torso_com_offset_m": [-0.05, 0.0, 0.0],
        },
        "summary": {
            "cells": len(cells),
            "green_cells": sum(cell["cell_green"] for cell in cells),
            "x0_green_cells": sum(
                cell["cell_green"]
                for cell in cells
                if cell["command_x_m_s"] == 0
            ),
            "moving_green_cells": len(passing),
            "moving_failed_cells": len(failing),
            "failure_onset_tick_min": min(failure_onsets),
            "failure_onset_tick_max": max(failure_onsets),
            "failure_onset_support_counts": onset_support_counts,
            "capture_point_support_margin_p05_m": {
                "passing_min": min(margin_passing),
                "passing_max": max(margin_passing),
                "failing_min": min(margin_failing),
                "failing_max": max(margin_failing),
                "ranges_overlap": ranges_overlap(
                    margin_passing,
                    margin_failing,
                ),
                "pairwise_failure_more_adverse_fraction": (
                    pairwise_discrimination(
                        margin_passing,
                        margin_failing,
                        lower_is_more_adverse=True,
                    )
                ),
            },
            "capture_minus_pressure_rolling32_minimum_mean_m": {
                "passing_min": min(pressure_passing),
                "passing_max": max(pressure_passing),
                "failing_min": min(pressure_failing),
                "failing_max": max(pressure_failing),
                "ranges_overlap": ranges_overlap(
                    pressure_passing,
                    pressure_failing,
                ),
                "pairwise_failure_more_adverse_fraction": (
                    pairwise_discrimination(
                        pressure_passing,
                        pressure_failing,
                        lower_is_more_adverse=True,
                    )
                ),
            },
            "first32_action_delta_rms_min": min(moving_action_deltas),
            "first32_action_delta_rms_max": max(moving_action_deltas),
            "maximum_contact_reconstruction_force_error_nm": max(
                cell["dynamic_support"][
                    "actuator_force_reconstruction_max_abs_error_nm"
                ]
                for cell in moving
            ),
        },
        "cells": cells,
        "closed_mechanisms": {
            key: receipt(path) for key, path in PRIOR_CLOSURES.items()
        },
        "successor_constraints": {
            "mechanism": (
                "training-only symmetric single-support balance curriculum"
            ),
            "must_be_distinct_from": [
                "direct torso-COM exposure only",
                "terminal roll/pitch penalty",
                "static support-coordinate action transforms",
                "capture-point hard projection",
            ],
            "automatic_sim_measurement_only": True,
            "manual_mass_or_com_measurement": False,
            "policy_abi_change": False,
            "runtime_or_rdk_change": False,
            "default_off_exactness_required": True,
            "both_support_sides_required": True,
            "hosted_training_authorized": False,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t55_cpu_contract_preregistration": not failed_checks,
            "t55_cpu_contract_execution": False,
            "hosted_training": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = result["summary"]
    capture_discrimination = summary[
        "capture_point_support_margin_p05_m"
    ]["pairwise_failure_more_adverse_fraction"]
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T54 T53 condition-7 failure attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Classification: `{result['classification']}`",
                "- Condition-7 cells: `8/16` green",
                "- x=0 / moving: `4/4` green / `4/12` green",
                "- Failed moving cells: eight delayed backward-pitch falls",
                (
                    "- Pitch -0.25-rad onset: ticks "
                    f"`{summary['failure_onset_tick_min']}-"
                    f"{summary['failure_onset_tick_max']}`"
                ),
                (
                    "- Onset support: "
                    f"`{summary['failure_onset_support_counts']}`"
                ),
                (
                    "- Capture-margin pass/fail pairwise discrimination: "
                    f"`{capture_discrimination:.5f}`"
                ),
                "- Capture-point and pressure ranges overlap pass/fail",
                "- Response context changes and moving actions respond",
                "- Tracking/rate/saturation remain green at every failed cell",
                "- New behavior/training/Colab/robot: `0/0/0/0`",
                "",
                "## Decision",
                "",
                (
                    "The evidence earns only a CPU software contract for a "
                    "symmetric training-only single-support curriculum. "
                    "It does not earn hosted training."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed_checks}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
