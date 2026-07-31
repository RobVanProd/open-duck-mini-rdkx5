#!/usr/bin/env python3
"""Run the frozen CPU-only signed torso-COM break-radius curve."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate, write_markdown


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
OUT = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius"
TRACE_ROOT = OUT / "traces"
POLICIES = {
    512000: ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    1024000: ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
}
POLICY_HASHES = {
    512000: "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
    1024000: "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece",
}
FITS = {
    "p30": ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
FIT_HASHES = {
    "p30": "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
    "p31_34": "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276",
}
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
REFERENCE_HASH = "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
SEED = 167931544
BISECTION_ITERATIONS = 6
ENDPOINT_M = 0.05
EXPECTED_WIDTH_M = 0.00078125

X0_GATE = {
    "samples": 600,
    "termination_reason": "duration_complete",
    "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
    "maximum_absolute_mean_local_velocity_m_s": 0.02,
    "maximum_body_pitch_p95_rad": 0.25,
    "minimum_base_height_m": 0.12,
    "maximum_pitch_tracking_p95_rad": 0.20,
    "maximum_action_saturation_pct": 0.0,
    "maximum_rate_excess_rad_s": 0.0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def offset_name(offset: float) -> str:
    if abs(offset) < 1e-15:
        return "ZERO_0p00000000"
    return ("NEG_" if offset < 0 else "POS_") + f"{abs(offset):.8f}".replace(".", "p")


def exact_readback(report: dict[str, Any], offset: float) -> bool:
    readback = report.get("readback") or {}
    before = readback.get("before") or []
    after = readback.get("after") or []
    if len(before) != 3 or len(after) != 3:
        return False
    delta = [float(after[i]) - float(before[i]) for i in range(3)]
    return (
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [offset, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and abs(delta[0] - offset) <= 1e-12
        and abs(delta[1]) <= 1e-12
        and abs(delta[2]) <= 1e-12
    )


def eval_args(policy: Path, fit: Path, offset: float, trace_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        policy=str(policy),
        playground_root=str(PLAYGROUND),
        fit=str(fit),
        reference_feature_table=str(REFERENCE),
        reference_start_phase=0,
        expected_observation_dim=115,
        policy_state_input_names="previous_action",
        policy_state_output_names="previous_action_out",
        policy_applied_target_observation=True,
        policy_reset_com_estimator_input=False,
        trace_dir=trace_dir,
        trace_full_obs=False,
        trace_com_accelerometer_map_ticks="",
        commands="0.0,0.074,0.077,0.080",
        seeds=str(SEED),
        duration_s=12.0,
        minimum_emergence_duration_s=1.08,
        task="flat_terrain_backlash",
        eval_dynamics_override_json=json.dumps(
            {"torso_com_offset_m": [offset, 0.0, 0.0]}, separators=(",", ":")
        ),
        reset_mode="home-support",
        policy_action_rate_limit_rad_s=None,
        policy_action_rate_limit_joint_indices="2,3,4,11,12,13",
        policy_action_rate_limit_values="",
    )


def run_offset(offset: float, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    name = offset_name(offset)
    if name in cache:
        return cache[name]
    matrices: list[dict[str, Any]] = []
    for fit_name, fit_path in FITS.items():
        for step, policy in POLICIES.items():
            stem = f"{name}_{fit_name}_T2_EQUAL_{step}"
            trace_dir = TRACE_ROOT / name / fit_name / f"T2_EQUAL_{step}"
            trace_dir.mkdir(parents=True, exist_ok=True)
            payload = evaluate(eval_args(policy, fit_path, offset, trace_dir))
            json_path = OUT / f"{stem}_eval.json"
            md_path = OUT / f"{stem}_EVAL.md"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            write_markdown(payload, md_path)
            summary = summarize(json_path, X0_GATE, SEED)
            readbacks = [exact_readback(run.get("dynamics_override") or {}, offset) for run in payload["runs"]]
            matrix = {
                "fit": fit_name,
                "step": step,
                "eval_json": str(json_path.relative_to(ROOT)),
                "eval_sha256": sha256(json_path),
                "readback_pass": len(readbacks) == 4 and all(readbacks),
                "summary": summary,
                "matrix_pass": bool(summary["matrix_pass"] and len(readbacks) == 4 and all(readbacks)),
            }
            matrices.append(matrix)
            print(json.dumps({"offset_m": offset, "fit": fit_name, "step": step, "pass": matrix["matrix_pass"]}), flush=True)
    result = {
        "offset_m": offset,
        "name": name,
        "matrices": matrices,
        "cell_count": 16,
        "pass": len(matrices) == 4 and all(item["matrix_pass"] for item in matrices),
    }
    cache[name] = result
    return result


def monotone(points: list[dict[str, Any]], sign: int) -> bool:
    signed = sorted(
        (abs(float(item["offset_m"])), bool(item["pass"]))
        for item in points
        if item["offset_m"] == 0.0 or (item["offset_m"] > 0) == (sign > 0)
    )
    seen_failure = False
    for _, passed in signed:
        if not passed:
            seen_failure = True
        elif seen_failure:
            return False
    return True


def main() -> None:
    if not PLAYGROUND.is_dir():
        raise SystemExit(f"missing composed CPU checkout: {PLAYGROUND}")
    exact_inputs = (
        all(sha256(path) == POLICY_HASHES[step] for step, path in POLICIES.items())
        and all(sha256(path) == FIT_HASHES[name] for name, path in FITS.items())
        and sha256(REFERENCE) == REFERENCE_HASH
    )
    if not exact_inputs:
        raise SystemExit("frozen input hash mismatch")

    cache: dict[str, dict[str, Any]] = {}
    zero = run_offset(0.0, cache)
    endpoints = {sign: run_offset(sign * ENDPOINT_M, cache) for sign in (-1, 1)}
    bounds: dict[str, dict[str, float]] = {}
    for sign in (-1, 1):
        inner = 0.0
        outer = ENDPOINT_M
        for _ in range(BISECTION_ITERATIONS):
            midpoint = (inner + outer) / 2.0
            result = run_offset(sign * midpoint, cache)
            if result["pass"]:
                inner = midpoint
            else:
                outer = midpoint
        bounds["negative" if sign < 0 else "positive"] = {
            "certified_inner_pass_m": sign * inner,
            "observed_outer_fail_m": sign * outer,
            "magnitude_inner_pass_m": inner,
            "magnitude_outer_fail_m": outer,
            "bracket_width_m": outer - inner,
        }

    points = list(cache.values())
    checks = {
        "frozen_inputs_exact": exact_inputs,
        "zero_matrix_passes": zero["pass"],
        "negative_endpoint_fails": not endpoints[-1]["pass"],
        "positive_endpoint_fails": not endpoints[1]["pass"],
        "all_points_have_16_cells": all(item["cell_count"] == 16 for item in points),
        "all_matrix_readbacks_pass": all(
            matrix["readback_pass"] for item in points for matrix in item["matrices"]
        ),
        "negative_samples_monotone": monotone(points, -1),
        "positive_samples_monotone": monotone(points, 1),
        "negative_width_exact": abs(bounds["negative"]["bracket_width_m"] - EXPECTED_WIDTH_M) <= 1e-15,
        "positive_width_exact": abs(bounds["positive"]["bracket_width_m"] - EXPECTED_WIDTH_M) <= 1e-15,
        "cpu_only": os.environ.get("JAX_PLATFORMS") == "cpu" and os.environ.get("CUDA_VISIBLE_DEVICES") == "",
    }
    evidence_checks = [
        "frozen_inputs_exact", "zero_matrix_passes", "negative_endpoint_fails",
        "positive_endpoint_fails", "all_points_have_16_cells",
        "all_matrix_readbacks_pass", "negative_width_exact",
        "positive_width_exact", "cpu_only",
    ]
    invalid = [name for name in evidence_checks if not checks[name]]
    nonmonotone = [name for name in ("negative_samples_monotone", "positive_samples_monotone") if not checks[name]]
    if invalid:
        status, decision = "HOLD_COM_CURVE_EVIDENCE_INVALID", "STOP_INVALID_COM_BREAK_RADIUS"
    elif nonmonotone:
        status, decision = "HOLD_COM_CURVE_NON_MONOTONIC", "STOP_NO_SINGLE_COM_BREAK_RADIUS"
    else:
        status, decision = "PASS_COM_BREAK_RADIUS_BRACKETED", "AUTHORIZE_REAL_BUILD_COM_COMPARISON_ONLY"
    result = {
        "schema_version": "composite_winner_torso_com_break_radius_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": invalid + nonmonotone,
        "bounds": bounds,
        "point_count": len(points),
        "cell_count": sum(item["cell_count"] for item in points),
        "points": sorted(points, key=lambda item: item["offset_m"]),
        "authority": {
            "compare_real_build_com": status == "PASS_COM_BREAK_RADIUS_BRACKETED",
            "model_correction": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk_x5": False,
        },
    }
    json_path = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
    md_path = ROOT / "outputs/analysis/COMPOSITE_WINNER_TORSO_COM_BREAK_RADIUS_RESULT_20260716.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Composite-Winner Torso-COM Break-Radius Result", "",
        f"Status: `{status}`", "", f"Decision: `{decision}`", "",
        f"Formal points: {len(points)}; formal cells: {result['cell_count']}", "",
        "| sign | certified inner pass | observed outer fail | width |", "|---|---:|---:|---:|",
    ]
    for name in ("negative", "positive"):
        item = bounds[name]
        lines.append(
            f"| {name} | {item['certified_inner_pass_m']:.8f} m | "
            f"{item['observed_outer_fail_m']:.8f} m | {item['bracket_width_m']:.8f} m |"
        )
    lines.extend([
        "", "The inner value is the largest sampled signed offset for which every one of the 16 frozen cells passes. The outer value is the nearest sampled aggregate failure. No interpolation beyond this bracket is claimed.",
        "", "This result permits comparison with the separately contracted real-build COM estimate only. Robot clearance remains NO.", "",
    ])
    md_path.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "bounds": bounds}), flush=True)
    if invalid:
        raise SystemExit(f"invalid evidence: {invalid}")


if __name__ == "__main__":
    main()
