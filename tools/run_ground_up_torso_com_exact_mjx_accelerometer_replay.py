#!/usr/bin/env python3
"""Run the preregistered eager-MJX torso-COM accelerometer replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
EVALUATOR = REPO / "tools/evaluate_ground_up_policy.py"
MATRIX_ROOT = REPO / "outputs/analysis/ground_up_torso_com_behavior_eval"
PRIOR_MANIFEST = REPO / "outputs/analysis/ground_up_torso_com_full_obs_replay_manifest.json"
INVALID_RESULT = REPO / "outputs/analysis/ground_up_torso_com_exact_mjx_accelerometer_map_result.json"
DIRECTION = np.asarray(
    [1.1654748916625977, 0.11948448419570923, 1.0919904708862305], dtype=float
)
TICKS = (0, 24, 32, 40)
COMMANDS = (0.074, 0.077, 0.08)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nominal_sources() -> list[Path]:
    paths = sorted(MATRIX_ROOT.glob("NOMINAL_*.json"))
    if len(paths) != 12:
        raise ValueError(f"expected 12 nominal matrices, got {len(paths)}")
    return paths


def matrix_identity(path: Path) -> tuple[str, int, str]:
    stem = path.stem
    for arm in ("A05_DIRECT", "U05_DIRECT", "U_CURRICULUM"):
        prefix = f"NOMINAL_{arm}_"
        if stem.startswith(prefix):
            rest = stem[len(prefix):]
            step_text, fit = rest.rsplit("_", 1)
            if fit == "34":
                step_text, fit_prefix = step_text.rsplit("_", 1)
                fit = f"{fit_prefix}_34"
            return arm, int(step_text), fit
    raise ValueError(f"unexpected nominal matrix name: {path.name}")


def command_for(source: dict[str, Any], output: Path, trace_dir: Path) -> list[str]:
    inputs = source["inputs"]
    command = [
        sys.executable, str(EVALUATOR),
        "--policy", inputs["policy"],
        "--playground-root", inputs["playground_root"],
        "--fit", inputs["fit"],
        "--reference-feature-table", inputs["reference_feature_table"],
        "--reference-start-phase", str(inputs["reference_start_phase"]),
        "--expected-observation-dim", str(inputs["expected_observation_dim"]),
        "--policy-state-input-names", ",".join(inputs["policy_state_input_names"]),
        "--policy-state-output-names", ",".join(inputs["policy_state_output_names"]),
        "--trace-dir", str(trace_dir), "--trace-full-obs",
        "--trace-com-accelerometer-map-ticks", ",".join(str(tick) for tick in TICKS),
        "--commands", ",".join(str(value) for value in COMMANDS),
        "--seeds", ",".join(str(value) for value in inputs["seeds"]),
        "--duration-s", str(inputs["duration_s"]),
        "--minimum-emergence-duration-s", str(inputs["minimum_emergence_duration_s"]),
        "--task", inputs["task"], "--reset-mode", inputs["reset_mode"],
        "--policy-action-rate-limit-joint-indices",
        ",".join(str(value) for value in inputs["policy_action_rate_limit_joint_indices"]),
        "--output-json", str(output),
    ]
    if inputs["policy_applied_target_observation"]:
        command.append("--policy-applied-target-observation")
    if inputs["policy_action_rate_limit_rad_s"] is not None:
        command.extend([
            "--policy-action-rate-limit-rad-s",
            str(inputs["policy_action_rate_limit_rad_s"]),
        ])
    if inputs["policy_action_rate_limit_values"]:
        command.extend([
            "--policy-action-rate-limit-values",
            ",".join(str(value) for value in inputs["policy_action_rate_limit_values"]),
        ])
    return command


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len(rows) != 600 or [row.get("tick") for row in rows] != list(range(600)):
        raise ValueError(f"trace row contract failed: {path}")
    return rows


def classify(norm_h: float, cosine: float | None, center_ratio: float | None) -> str:
    if norm_h < 0.25 * float(np.linalg.norm(DIRECTION)):
        return "WEAK_SIGNAL"
    if center_ratio is None or center_ratio > 0.25:
        return "NONLINEAR_CENTER"
    if cosine is None or cosine < 0.80:
        return "DIRECTION_ROTATED"
    return "FIXED_DIRECTION_COMPATIBLE"


def counts(cells: list[dict[str, Any]]) -> dict[str, int]:
    names = (
        "WEAK_SIGNAL", "NONLINEAR_CENTER", "DIRECTION_ROTATED",
        "FIXED_DIRECTION_COMPATIBLE",
    )
    return {name: sum(cell["classification"] == name for cell in cells) for name in names}


def exact_strip_compare(
    generated: list[dict[str, Any]], prior: list[dict[str, Any]]
) -> tuple[bool, int, list[dict[str, Any]]]:
    if len(generated) != len(prior):
        return False, abs(len(generated) - len(prior)), []
    mismatches = 0
    map_rows = []
    for new_row, old_row in zip(generated, prior, strict=True):
        stripped = dict(new_row)
        map_value = stripped.pop("torso_com_accelerometer_map", None)
        if stripped != old_row:
            mismatches += 1
        if map_value is not None:
            map_rows.append({"tick": int(new_row["tick"]), "map": map_value, "obs": new_row["obs_state"]})
    return mismatches == 0, mismatches, map_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("exact CPU environment required")
    contract = json.loads(args.contract.read_text())
    if contract.get("status") != "PASS_TORSO_COM_EAGER_MJX_ACCELEROMETER_CONTRACT":
        raise ValueError("passing eager-MJX accelerometer contract required")
    if contract["details"]["study_tool_sha256"] != sha256(Path(__file__)):
        raise ValueError("exact-MJX study tool changed after contract")
    if contract["details"]["evaluator_sha256"] != sha256(EVALUATOR):
        raise ValueError("evaluator changed after exact-MJX contract")
    closed_loop = REPO / "tools/closed_loop_sim_eval.py"
    if contract["details"]["closed_loop_sha256"] != sha256(closed_loop):
        raise ValueError("closed-loop evaluator changed after exact-MJX contract")

    output_root = args.output_root.resolve()
    if output_root.exists():
        raise ValueError(f"formal output root already exists: {output_root}")
    output_root.mkdir(parents=True)
    matrix_root = output_root / "matrices"
    trace_root = output_root / "traces"
    matrix_root.mkdir()
    trace_root.mkdir()

    prior_manifest = json.loads(PRIOR_MANIFEST.read_text())
    prior_index = {
        (
            row["arm"], int(row["step"]), row["fit"], round(float(row["command_x"]), 3)
        ): row
        for row in prior_manifest["traces"] if row["condition"] == "NOMINAL"
    }
    if len(prior_index) != 48:
        raise ValueError(f"prior nominal trace index mismatch: {len(prior_index)}")

    env = dict(os.environ)
    env.update({"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu"})
    cells: list[dict[str, Any]] = []
    trace_records: list[dict[str, Any]] = []
    total_baseline_mismatches = 0
    nominal_obs_error = 0.0

    source_paths = nominal_sources()
    for matrix_number, source_path in enumerate(source_paths, start=1):
        source = json.loads(source_path.read_text())
        arm, step, fit = matrix_identity(source_path)
        matrix_output = matrix_root / source_path.name
        matrix_trace_dir = trace_root / arm / str(step) / fit
        matrix_trace_dir.mkdir(parents=True)
        print(f"[{matrix_number}/12] {source_path.name}", flush=True)
        subprocess.run(
            command_for(source, matrix_output, matrix_trace_dir),
            cwd=REPO, env=env, check=True,
        )
        generated_matrix = json.loads(matrix_output.read_text())
        if len(generated_matrix.get("runs") or []) != 3:
            raise ValueError(f"generated run count mismatch: {source_path.name}")
        for run in generated_matrix["runs"]:
            command_x = round(float(run["command_x"]), 3)
            prior_meta = prior_index[(arm, step, fit, command_x)]
            prior_path = Path(prior_meta["path"])
            if sha256(prior_path) != prior_meta["sha256"]:
                raise ValueError(f"prior trace hash mismatch: {prior_path}")
            generated_path = Path(run["trace_jsonl"])
            generated_rows = load_rows(generated_path)
            prior_rows = load_rows(prior_path)
            exact, mismatches, map_rows = exact_strip_compare(generated_rows, prior_rows)
            total_baseline_mismatches += mismatches
            if len(map_rows) != 4 or [row["tick"] for row in map_rows] != list(TICKS):
                raise ValueError(f"map tick/cardinality mismatch: {generated_path}")
            trace_records.append({
                "arm": arm, "step": step, "fit": fit, "command_x": command_x,
                "path": str(generated_path), "sha256": sha256(generated_path),
                "bytes": generated_path.stat().st_size, "rows": len(generated_rows),
                "prior_path": str(prior_path), "prior_sha256": prior_meta["sha256"],
                "baseline_exact_after_stripping_map": exact,
                "baseline_row_mismatches": mismatches,
            })
            for row in map_rows:
                tick = row["tick"]
                value = row["map"]
                nominal = np.asarray(value["nominal_actor_accelerometer_m_s2"], dtype=float)
                negative = np.asarray(value["negative_accelerometer_m_s2"], dtype=float)
                positive = np.asarray(value["positive_accelerometer_m_s2"], dtype=float)
                obs = np.asarray(row["obs"][3:6], dtype=float)
                nominal_error = float(np.max(np.abs(nominal - obs)))
                nominal_obs_error = max(nominal_obs_error, nominal_error)
                half_direction = (positive - negative) / 2.0
                center = (positive + negative) / 2.0 - nominal
                norm_h = float(np.linalg.norm(half_direction))
                norm_center = float(np.linalg.norm(center))
                direction_norm = float(np.linalg.norm(DIRECTION))
                cosine = (
                    float(np.dot(half_direction, DIRECTION) / (norm_h * direction_norm))
                    if norm_h > 0.0 else None
                )
                center_ratio = norm_center / norm_h if norm_h > 0.0 else None
                cells.append({
                    "arm": arm, "policy": f"{arm}_{step}", "step": step,
                    "fit": fit, "command_x": command_x, "tick": tick,
                    "classification": classify(norm_h, cosine, center_ratio),
                    "accelerometer_nominal_m_s2": nominal.tolist(),
                    "accelerometer_negative_m_s2": negative.tolist(),
                    "accelerometer_positive_m_s2": positive.tolist(),
                    "physical_half_direction_m_s2": half_direction.tolist(),
                    "center_residual_m_s2": center.tolist(),
                    "half_direction_norm_m_s2": norm_h,
                    "center_residual_norm_m_s2": norm_center,
                    "direction_cosine_to_reset": cosine,
                    "magnitude_ratio_to_reset": norm_h / direction_norm,
                    "center_ratio": center_ratio,
                    "nominal_actor_obs_max_abs_error_m_s2": nominal_error,
                    "tick0_direction_max_abs_error_m_s2": (
                        float(np.max(np.abs(half_direction - DIRECTION)))
                        if tick == 0 else None
                    ),
                })

    if len(trace_records) != 36 or len(cells) != 144:
        raise ValueError(f"formal cardinality mismatch: traces={len(trace_records)}, cells={len(cells)}")
    tick0_error = max(
        cell["tick0_direction_max_abs_error_m_s2"]
        for cell in cells if cell["tick"] == 0
    )
    finite = all(
        math.isfinite(value)
        for cell in cells
        for key in (
            "accelerometer_nominal_m_s2", "accelerometer_negative_m_s2",
            "accelerometer_positive_m_s2", "physical_half_direction_m_s2",
            "center_residual_m_s2",
        )
        for value in cell[key]
    )
    validity = {
        "baseline_traces_exact_after_stripping_map": total_baseline_mismatches == 0,
        "baseline_row_mismatches": total_baseline_mismatches,
        "nominal_actor_observation_max_abs_error_m_s2": nominal_obs_error,
        "nominal_actor_observation_exact": nominal_obs_error == 0.0,
        "tick0_direction_max_abs_error_m_s2": tick0_error,
        "tick0_direction_tolerance_m_s2": 1e-3,
        "all_values_finite": finite,
    }
    validity["valid"] = (
        validity["baseline_traces_exact_after_stripping_map"]
        and validity["nominal_actor_observation_exact"]
        and tick0_error <= 1e-3 and finite
    )

    tick_summaries = {}
    for tick in TICKS:
        subset = [cell for cell in cells if cell["tick"] == tick]
        row_counts = counts(subset)
        fixed = (
            row_counts["FIXED_DIRECTION_COMPATIBLE"] >= 27
            and row_counts["WEAK_SIGNAL"] <= 3
            and row_counts["NONLINEAR_CENTER"] <= 3
            and row_counts["DIRECTION_ROTATED"] <= 3
        )
        tick_summaries[str(tick)] = {
            "cells": len(subset), "counts": row_counts,
            "classification": "FIXED_COMPATIBLE_TICK" if fixed else "NON_FIXED_TICK",
            "half_direction_norm_range_m_s2": [
                min(cell["half_direction_norm_m_s2"] for cell in subset),
                max(cell["half_direction_norm_m_s2"] for cell in subset),
            ],
            "direction_cosine_range": [
                min(cell["direction_cosine_to_reset"] for cell in subset),
                max(cell["direction_cosine_to_reset"] for cell in subset),
            ],
            "center_ratio_range": [
                min(cell["center_ratio"] for cell in subset),
                max(cell["center_ratio"] for cell in subset),
            ],
        }

    if not validity["valid"]:
        status = "INVALID_EAGER_MJX_ACCELEROMETER_REPLAY"
        decision = "INVALID_EAGER_MJX_ACCELEROMETER_REPLAY"
    else:
        status = "PASS_EAGER_MJX_ACCELEROMETER_MAP_COMPLETE"
        if all(tick_summaries[str(tick)]["classification"] == "FIXED_COMPATIBLE_TICK" for tick in TICKS):
            decision = "SUPPORT_PREREGISTERED_FINE_GRAINED_COUPLING_MAP"
        elif (
            tick_summaries["0"]["classification"] == "FIXED_COMPATIBLE_TICK"
            and all(tick_summaries[str(tick)]["counts"]["WEAK_SIGNAL"] >= 27 for tick in (24, 32, 40))
        ):
            decision = "SUPPORT_PREREGISTERED_TEMPORAL_SENSOR_INFORMATION_STUDY"
        elif (
            tick_summaries["0"]["classification"] == "FIXED_COMPATIBLE_TICK"
            and any(
                tick_summaries[str(tick)]["counts"]["DIRECTION_ROTATED"]
                + tick_summaries[str(tick)]["counts"]["NONLINEAR_CENTER"] >= 18
                for tick in (24, 32, 40)
            )
        ):
            decision = "SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY"
        else:
            decision = "EAGER_MJX_ACCELEROMETER_MAP_UNRESOLVED_NO_FAMILY_SELECTED"

    payload = {
        "schema_version": "ground_up_torso_com_eager_mjx_accelerometer_map.v1",
        "status": status, "decision": decision, "validity": validity,
        "aggregate_counts": counts(cells), "tick_summaries": tick_summaries,
        "cells": cells, "traces": trace_records,
        "sources": {
            "contract_sha256": sha256(args.contract),
            "prior_manifest_sha256": sha256(PRIOR_MANIFEST),
            "invalid_exact_mjx_result_sha256": sha256(INVALID_RESULT),
            "evaluator_sha256": sha256(EVALUATOR),
            "closed_loop_sha256": sha256(closed_loop),
        },
        "execution": {
            "cpu_only": True, "baseline_runs": 36, "baseline_ticks_each": 600,
            "formal_cells": 144, "com_branch_dynamic_steps": 0,
            "actor_counterfactual_calls": 0, "training": False,
            "robot_or_rdk": False, "p_value": None,
        },
        "authority": {
            "next_preregistration_only": True, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Torso-COM Eager-MJX Accelerometer-Replay Result", "",
        f"status: `{status}`", f"decision: `{decision}`", "",
        "| tick | fixed compatible | weak | nonlinear center | rotated | tick class |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for tick in TICKS:
        row = tick_summaries[str(tick)]
        c = row["counts"]
        lines.append(
            f"| {tick} | {c['FIXED_DIRECTION_COMPATIBLE']} | {c['WEAK_SIGNAL']} | "
            f"{c['NONLINEAR_CENTER']} | {c['DIRECTION_ROTATED']} | `{row['classification']}` |"
        )
    lines.extend([
        "", "Validity:", "",
        f"- baseline row mismatches after stripping map fields: {total_baseline_mismatches};",
        f"- nominal actor observation maximum error: {nominal_obs_error:.17g} m/s^2;",
        f"- tick-zero direction maximum error: {tick0_error:.17g} m/s^2;",
        f"- all values finite: {str(finite).lower()}.", "",
        "No p-value or training reward is used. The frozen result authorizes at most its named next preregistration.", "",
    ])
    args.markdown.write_text("\n".join(lines))
    print(json.dumps({
        "status": status, "decision": decision,
        "aggregate": payload["aggregate_counts"], "validity": validity,
    }, sort_keys=True))
    return 0 if status == "PASS_EAGER_MJX_ACCELEROMETER_MAP_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
