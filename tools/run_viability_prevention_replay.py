#!/usr/bin/env python3
"""Run B2 full-gate comparator replay against the frozen viability metric."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
FIT_PATH = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
METRIC_PATH = ROOT / "outputs/analysis/viability_prevention_metric.json"
TRACE_ROOT = ROOT / "outputs/analysis/viability_prevention_replay_traces"
PROX_ROOT = ROOT / "outputs/analysis/viability_prevention_proximity"
CELL_ROOT = ROOT / "outputs/analysis/viability_prevention_replay_cells"
RESULT = ROOT / "outputs/analysis/viability_prevention_replay_result.json"
RESULT_MD = ROOT / "outputs/analysis/VIABILITY_PREVENTION_REPLAY_RESULT_20260716.md"
DOF_INDICES = (6, 8, 10, 12, 14, 16, 17, 18, 19, 20, 22, 24, 26, 28)
VELOCITY_SCALES = np.asarray([5.24, 5.24, 1.50, 1.50, 1.50, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25], dtype=float)
SCALES = np.asarray([*([0.25] * 14), *VELOCITY_SCALES, 0.20, 0.20, 0.05, 1.0, 1.0])
COMMANDS = (0.074, 0.077, 0.080)
SEEDS = (100, 101)

POLICIES = (
    {
        "name": "APPLIED_TARGET_1M",
        "path": Path("/home/lsd/robots/open-duck-mini-rdkx5/.tmp/ground_up_applied_target_colab_recovered/A2_APPLIED_TARGET_STATE/2026_07_14_173159_1003520.onnx"),
        "sha256": "bae176ffd2d7af4cfb85169c817a9b43bcbe4ac1e5d721dd16959e71aaaf51be",
        "obs_dim": 115, "stateful": True, "applied_target": True, "reference": True,
    },
    {
        "name": "TAIL_T2_EQUAL_1M",
        "path": Path("/home/lsd/robots/open-duck-mini-rdkx5/.tmp/ground_up_tracking_tail_colab_recovered/ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000.onnx"),
        "sha256": "2f059550a82e129bff3d58a2b9249cf1d5c1ea75dc18200f1e158928f67e38a6",
        "obs_dim": 115, "stateful": True, "applied_target": True, "reference": True,
    },
    {
        "name": "BEST_WALK_ONNX_2",
        "path": Path("/home/lsd/robots/open-duck-mini-rdkx5/policy/BEST_WALK_ONNX_2.onnx"),
        "sha256": "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067",
        "obs_dim": 101, "stateful": False, "applied_target": False, "reference": False,
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def quat_roll_pitch(q: list[float]) -> tuple[float, float]:
    w, x, y, z = (float(value) for value in q)
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    sinp = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
    return roll, math.asin(sinp)


def trace_vector(row: dict[str, Any]) -> np.ndarray:
    roll, pitch = quat_roll_pitch(row["base_quat_wxyz"])
    raw = np.asarray([
        *row["actual_position_rad"], *(row["qvel"][index] for index in DOF_INDICES),
        roll, pitch, row["base_height_m"], *row["foot_contacts"],
    ], dtype=float)
    if raw.shape != (33,):
        raise ValueError(f"trace vector shape {raw.shape}")
    return raw / SCALES


def main() -> int:
    metric = json.loads(METRIC_PATH.read_text())
    if metric["status"] != "PASS_VIABILITY_PREVENTION_METRIC_FROZEN":
        raise ValueError("B1 metric is not passed")
    radius = float(metric["radius"])
    centers = {
        sign: np.asarray([row["normalized_vector"] for row in metric["states"] if row["condition"] == sign], dtype=float)
        for sign in ("X_NEG", "X_POS")
    }
    input_checks = {
        "cpu_environment": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
        "metric_hash": sha256(METRIC_PATH) == "370d1334e6c7a98df5122cfcc3ae6aad16c14ea33ba3271065d6d7521c714f6e",
        "policy_hashes": all(sha256(item["path"]) == item["sha256"] for item in POLICIES),
        "fit_hash": sha256(FIT_PATH) == "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
        "reference_hash": sha256(REFERENCE) == "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    }
    if not all(input_checks.values()):
        raise RuntimeError(f"frozen input mismatch: {input_checks}")
    fit = json.loads(FIT_PATH.read_text())
    for path in (TRACE_ROOT, PROX_ROOT, CELL_ROOT):
        path.mkdir(parents=True, exist_ok=True)
    cells = []
    ordinal = 0
    for policy in POLICIES:
        for command_x in COMMANDS:
            for seed in SEEDS:
                ordinal += 1
                stem = f"{policy['name']}_x{command_x:.3f}_seed{seed}"
                trace_path = TRACE_ROOT / f"{stem}.jsonl"
                result = run_closed_loop_sim(ClosedLoopConfig(
                    policy_path=policy["path"], fit=fit, playground_root=PLAYGROUND,
                    command_x=command_x, duration_s=12.0, bridge_mode="fitted",
                    expected_observation_dim=policy["obs_dim"], expected_action_dim=14,
                    task="flat_terrain_backlash", seed=seed, eval_role="candidate",
                    reset_mode="home-support",
                    reference_feature_table_path=REFERENCE if policy["reference"] else None,
                    reference_start_phase=0 if policy["reference"] else None,
                    policy_state_input_names=("previous_action",) if policy["stateful"] else (),
                    policy_state_output_names=("previous_action_out",) if policy["stateful"] else (),
                    policy_applied_target_observation=policy["applied_target"],
                    trace_jsonl=trace_path, trace_full_obs=True,
                ))
                if not trace_path.exists():
                    raise RuntimeError(f"missing trace for {stem}: {result}")
                trace = [json.loads(line) for line in trace_path.read_text().splitlines()]
                vectors = np.asarray([trace_vector(row) for row in trace], dtype=float)
                distances = {
                    sign: np.sqrt(np.mean(np.square(vectors[:, None, :] - bank[None, :, :]), axis=2)).min(axis=1)
                    for sign, bank in centers.items()
                }
                proximity_path = PROX_ROOT / f"{stem}.jsonl"
                proximity_lines = []
                for tick in range(len(trace)):
                    dneg, dpos = float(distances["X_NEG"][tick]), float(distances["X_POS"][tick])
                    proximity_lines.append(json.dumps({
                        "tick": tick, "x_neg_distance": dneg, "x_pos_distance": dpos,
                        "x_neg_within": dneg <= radius, "x_pos_within": dpos <= radius,
                        "weighted_proximity": max(3.0 * max(0.0, 1.0 - dneg / radius), max(0.0, 1.0 - dpos / radius)),
                    }, sort_keys=True))
                proximity_path.write_text("\n".join(proximity_lines) + "\n")
                mode = (result.get("modes") or {}).get("fitted") or {}
                termination = mode.get("termination_reason")
                actual_fall = bool(len(trace) < 600 or (termination not in (None, "duration_complete")))
                lead_limit = max(0, len(trace) - 4)
                routed_ticks = [tick for tick in range(lead_limit) if distances["X_NEG"][tick] <= radius or distances["X_POS"][tick] <= radius]
                routed = bool(actual_fall and routed_ticks)
                gate = result.get("candidate_gate") or {}
                cell = {
                    "schema_version": "viability_prevention_replay_cell.v1",
                    "policy": policy["name"], "policy_sha256": policy["sha256"],
                    "command_x": command_x, "seed": seed, "samples": len(trace),
                    "termination_reason": termination, "actual_fall": actual_fall,
                    "routed_with_at_least_4_tick_lead": routed,
                    "first_routed_tick": routed_ticks[0] if routed_ticks else None,
                    "minimum_x_neg_distance": float(np.min(distances["X_NEG"])),
                    "minimum_x_pos_distance": float(np.min(distances["X_POS"])),
                    "ticks_within_x_neg": int(np.sum(distances["X_NEG"] <= radius)),
                    "ticks_within_x_pos": int(np.sum(distances["X_POS"] <= radius)),
                    "maximum_weighted_proximity": float(max(json.loads(line)["weighted_proximity"] for line in proximity_lines)),
                    "candidate_gate_status": gate.get("status"),
                    "candidate_gate_metrics": gate.get("metrics"),
                    "trace_path": str(trace_path), "trace_sha256": sha256(trace_path),
                    "proximity_path": str(proximity_path), "proximity_sha256": sha256(proximity_path),
                }
                cell_path = CELL_ROOT / f"{stem}.json"
                cell_path.write_text(json.dumps(cell, indent=2, sort_keys=True) + "\n")
                cell["cell_path"] = str(cell_path); cell["cell_sha256"] = sha256(cell_path)
                cells.append(cell)
                print(f"[{ordinal}/18] {stem}: samples={len(trace)} fall={actual_fall} routed={routed} min_neg={cell['minimum_x_neg_distance']:.6f} min_pos={cell['minimum_x_pos_distance']:.6f}", flush=True)

    falls = [cell for cell in cells if cell["actual_fall"]]
    falls_by_policy = {item["name"]: sum(cell["actual_fall"] for cell in cells if cell["policy"] == item["name"]) for item in POLICIES}
    positive = bool(
        all(count >= 1 for count in falls_by_policy.values())
        and falls
        and all(cell["routed_with_at_least_4_tick_lead"] for cell in falls)
    )
    decision = "ADVANCE_SINGLE_VIABILITY_PREVENTION_BRANCH" if positive else "CLOSE_VIABILITY_PREVENTION_NO_ROUTED_FALL_CORPUS"
    checks = {**input_checks, "exact_18_cells": len(cells) == 18, "all_proximity_logs": all(Path(cell["proximity_path"]).exists() for cell in cells)}
    failed = sorted(key for key, value in checks.items() if not value)
    payload = {
        "schema_version": "viability_prevention_replay_result.v1",
        "status": "PASS_VIABILITY_PREVENTION_REPLAY_COMPLETE" if not failed else "FAIL_VIABILITY_PREVENTION_REPLAY_EVIDENCE",
        "decision": decision, "b3_positive": positive,
        "checks": checks, "failed_checks": failed,
        "cells": cells, "cells_total": len(cells), "actual_falls": len(falls),
        "falls_by_policy": falls_by_policy,
        "routed_falls": sum(cell["routed_with_at_least_4_tick_lead"] for cell in falls),
        "radius": radius, "sign_weights": metric["sign_weights"],
        "branch_rule": "positive only if each policy has >=1 actual fall and every actual fall routes with >=4 tick lead",
        "source_hashes": {
            "tool": sha256(Path(__file__)), "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py"),
            "metric": sha256(METRIC_PATH),
            "preregistration_json": sha256(ROOT / "outputs/analysis/viability_prevention_replay_preregistration.json"),
            "preregistration_md": sha256(ROOT / "outputs/analysis/VIABILITY_PREVENTION_REPLAY_PREREGISTRATION_20260716.md"),
        },
        "execution": {"cpu_only": True, "training": False, "hosted": False, "robot_or_rdk": False, "gpu_or_igpu": False},
        "robot_clearance": "NO",
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Viability Prevention Replay Result", "", f"status: `{payload['status']}`", f"decision: `{decision}`", "",
        f"Actual falls: {len(falls)}/18. Routed falls: {payload['routed_falls']}/{len(falls)}.", "",
        "| policy | x | seed | ticks | gate | fall | routed | min X_NEG | min X_POS |", "|---|---:|---:|---:|---|---|---|---:|---:|",
    ]
    for cell in cells:
        lines.append(f"| {cell['policy']} | {cell['command_x']:.3f} | {cell['seed']} | {cell['samples']} | `{cell['candidate_gate_status']}` | `{cell['actual_fall']}` | `{cell['routed_with_at_least_4_tick_lead']}` | {cell['minimum_x_neg_distance']:.6f} | {cell['minimum_x_pos_distance']:.6f} |")
    lines.extend(["", f"Final B3 branch token: `{decision}`", "", "No reward selection. CPU-only replay; robot clearance remains `NO`.", ""])
    RESULT_MD.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "decision": decision, "actual_falls": len(falls), "routed_falls": payload["routed_falls"]}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
