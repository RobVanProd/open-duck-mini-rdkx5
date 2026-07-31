#!/usr/bin/env python3
"""Run the preregistered paired 64-tick warm-start startup screen."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v103_response_conditioned_behavior import REFERENCE  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v136_warm_start_startup_preregistration.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V135_CONTRACT = ANALYSIS / "winner_v135_phase_consistent_hidden_contract.json"
V135_VECTOR = ANALYSIS / "winner_v135_phase_consistent_hidden_vector.json"
OUTPUT = ANALYSIS / "winner_v136_warm_start_startup_result.json"
MARKDOWN = ANALYSIS / "WINNER_V136_WARM_START_STARTUP_RESULT_20260725.md"
TORQUE_LIMIT_NM = 1.91229675
CURRENT_LIMIT_A = 2.5
CURRENT_SCALE_NM_PER_A = 0.784532
STRICT_CURRENT_A = 2.0
PITCH_CHAIN = (2, 3, 4, 11, 12, 13)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v136_warm_start", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V136 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def longest_true_run(values: np.ndarray) -> int:
    best = 0
    current = 0
    for value in values.astype(bool):
        if value:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def trace_metrics(
    path: Path,
    *,
    initialization: str,
    warm: np.ndarray,
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    force = np.asarray(
        [row["actuator_force_nm"] for row in rows], dtype=np.float64
    )
    current = np.abs(force) / CURRENT_SCALE_NM_PER_A
    tracking = np.abs(
        np.asarray(
            [row["tracking_error_rad"] for row in rows], dtype=np.float64
        )[:, PITCH_CHAIN]
    )
    saturation = np.asarray(
        [row["action_saturated"] for row in rows], dtype=np.int64
    )
    conservative_excess = np.asarray(
        [row["conservative_rate_excess_rad_s"] for row in rows],
        dtype=np.float64,
    )
    sent_excess = np.asarray(
        [row["sent_target_rate_excess_rad_s"] for row in rows],
        dtype=np.float64,
    )
    first_h = np.asarray(
        rows[0]["policy_state_input"]["h_in"][0], dtype=np.float32
    )
    expected_h = (
        np.zeros(64, dtype=np.float32)
        if initialization == "zero"
        else warm
    )
    return {
        "rows": len(rows),
        "trace_sha256": sha256(path),
        "first_h_in_linf_error": float(
            np.max(np.abs(first_h - expected_h))
        ),
        "peak_abs_torque_nm": float(np.max(np.abs(force))),
        "torque_violation_joint_events": int(
            np.sum(np.abs(force) > TORQUE_LIMIT_NM)
        ),
        "peak_current_a": float(np.max(current)),
        "current_violation_joint_events": int(
            np.sum(current > CURRENT_LIMIT_A)
        ),
        "strict_current_longest_run_ticks": max(
            longest_true_run(current[:, joint] > STRICT_CURRENT_A)
            for joint in range(current.shape[1])
        ),
        "pitch_tracking_p95_rad": float(np.percentile(tracking, 95)),
        "action_saturation_joint_events": int(np.sum(saturation)),
        "conservative_rate_excess_max_rad_s": float(
            np.max(conservative_excess)
        ),
        "sent_target_rate_excess_max_rad_s": float(np.max(sent_excess)),
        "base_height_min_m": float(
            min(float(row["base_height_m"]) for row in rows)
        ),
        "body_pitch_abs_max_rad": float(
            max(abs(float(row["body_pitch_rad"])) for row in rows)
        ),
        "all_values_finite": bool(
            np.all(np.isfinite(force))
            and np.all(np.isfinite(current))
            and np.all(np.isfinite(tracking))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V136: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v135 = json.loads(V135_CONTRACT.read_text(encoding="utf-8"))
    vector_payload = json.loads(V135_VECTOR.read_text(encoding="utf-8"))
    warm = np.asarray(vector_payload["h_in"], dtype=np.float32)
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v135_contract": sha256(V135_CONTRACT),
        "v135_vector": sha256(V135_VECTOR),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "composer": sha256(
            ROOT / "tools/compose_winner_v136_warm_start_evaluator.py"
        ),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V136_WARM_START_STARTUP_SCREEN"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v135.get("decision")
        != "EARN_ONE_V136_WARM_START_STARTUP_SCREEN_PREREGISTRATION"
        or manifest.get("status")
        != "PASS_WINNER_V136_WARM_START_EVALUATOR_COMPOSITION"
    ):
        raise ValueError("V136 startup preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    policy_spec = next(
        item
        for item in v126["policies"]
        if item["id"] == "V121_TRAIN_MATCHED_FINAL"
    )
    policy = (
        Path(v126["external_inputs"]["policy_root"])
        / policy_spec["filename"]
    )
    if sha256(policy) != policy_spec["sha256"]:
        raise ValueError("V136 source policy changed")
    playground = Path(v126["external_inputs"]["playground"])
    rows = [
        row
        for row in v126["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
        and float(row["command_x_m_s"]) == 0.08
    ]
    if len(rows) != 2:
        raise ValueError("V136 requires two final x=.08 plant rows")
    run_root.mkdir(parents=True)
    cells = []
    for row in rows:
        for initialization in ("zero", "warm"):
            trace_path = run_root / (
                f"{str(row['plant']).lower()}_{initialization}.jsonl"
            )
            with contextlib.redirect_stdout(io.StringIO()):
                result = evaluator.run_closed_loop_sim(
                    evaluator.ClosedLoopConfig(
                        policy_path=policy,
                        fit=actuator_fit(base_prereg, str(row["plant"])),
                        playground_root=playground,
                        command_x=0.08,
                        duration_s=64 * 0.02,
                        bridge_mode="fitted",
                        expected_observation_dim=115,
                        task="flat_terrain_backlash",
                        seed=int(row["seed"]),
                        eval_role="candidate",
                        reset_mode="home-support",
                        policy_obs_input_name="obs",
                        policy_action_output_name="continuous_actions",
                        policy_state_input_names=("h_in", "previous_action"),
                        policy_state_output_names=(
                            "h_out",
                            "previous_action_out",
                        ),
                        policy_initial_h_in=(
                            None
                            if initialization == "zero"
                            else tuple(float(value) for value in warm)
                        ),
                        policy_graph_authoritative_output=True,
                        policy_applied_target_observation=True,
                        reference_feature_table_path=REFERENCE,
                        reference_start_phase=0,
                        trace_jsonl=trace_path,
                        trace_full_obs=True,
                        winner_v3_home_relative_actuator_gain=True,
                        exact_torque_oracle_enabled=False,
                    )
                )
            mode = ((result.get("modes") or {}).get("fitted") or {})
            metrics = trace_metrics(
                trace_path,
                initialization=initialization,
                warm=warm,
            )
            cells.append(
                {
                    "plant": str(row["plant"]),
                    "initialization": initialization,
                    "simulator_status": result.get("status"),
                    "samples": mode.get("samples"),
                    "termination_reason": mode.get("termination_reason"),
                    "trace_path": str(trace_path),
                    "metrics": metrics,
                }
            )
    keyed = {
        (row["plant"], row["initialization"]): row for row in cells
    }
    comparisons = []
    for row in rows:
        plant = str(row["plant"])
        baseline = keyed[(plant, "zero")]["metrics"]
        candidate = keyed[(plant, "warm")]["metrics"]
        comparisons.append(
            {
                "plant": plant,
                "baseline_peak_torque_nm": baseline[
                    "peak_abs_torque_nm"
                ],
                "warm_peak_torque_nm": candidate["peak_abs_torque_nm"],
                "peak_torque_delta_nm": (
                    candidate["peak_abs_torque_nm"]
                    - baseline["peak_abs_torque_nm"]
                ),
                "baseline_violation_events": baseline[
                    "torque_violation_joint_events"
                ],
                "warm_violation_events": candidate[
                    "torque_violation_joint_events"
                ],
                "baseline_tracking_p95_rad": baseline[
                    "pitch_tracking_p95_rad"
                ],
                "warm_tracking_p95_rad": candidate[
                    "pitch_tracking_p95_rad"
                ],
            }
        )
    warm_cells = [
        row for row in cells if row["initialization"] == "warm"
    ]
    zero_cells = [
        row for row in cells if row["initialization"] == "zero"
    ]
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "four_paired_cells_exact": len(cells) == 4,
        "all_cells_complete_64": all(
            row["samples"] == 64
            and row["termination_reason"] == "duration_complete"
            and row["metrics"]["rows"] == 64
            for row in cells
        ),
        "all_initial_states_exact": all(
            row["metrics"]["first_h_in_linf_error"] == 0.0
            for row in cells
        ),
        "zero_baseline_reproduces_startup_violation": all(
            row["metrics"]["torque_violation_joint_events"] > 0
            for row in zero_cells
        ),
        "warm_zero_torque_violations": all(
            row["metrics"]["torque_violation_joint_events"] == 0
            and row["metrics"]["peak_abs_torque_nm"] <= TORQUE_LIMIT_NM
            for row in warm_cells
        ),
        "warm_zero_current_violations": all(
            row["metrics"]["current_violation_joint_events"] == 0
            and row["metrics"]["peak_current_a"] <= CURRENT_LIMIT_A
            for row in warm_cells
        ),
        "warm_strict_current_run_below_100": all(
            row["metrics"]["strict_current_longest_run_ticks"] < 100
            for row in warm_cells
        ),
        "warm_tracking_below_point_two": all(
            row["metrics"]["pitch_tracking_p95_rad"] <= 0.20
            for row in warm_cells
        ),
        "warm_zero_saturation": all(
            row["metrics"]["action_saturation_joint_events"] == 0
            for row in warm_cells
        ),
        "warm_zero_rate_excess": all(
            row["metrics"]["conservative_rate_excess_max_rad_s"] == 0.0
            and row["metrics"]["sent_target_rate_excess_max_rad_s"] == 0.0
            for row in warm_cells
        ),
        "warm_peak_torque_no_worse_each_plant": all(
            row["peak_torque_delta_nm"] <= 0.0 for row in comparisons
        ),
        "all_values_finite": all(
            row["metrics"]["all_values_finite"] for row in cells
        ),
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v136.warm_start_startup_result.v1",
        "status": (
            "PASS_WINNER_V136_WARM_START_STARTUP_SCREEN"
            if not failed
            else "HOLD_WINNER_V136_WARM_START_STARTUP_SCREEN"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "limits": {
            "torque_nm": TORQUE_LIMIT_NM,
            "current_a": CURRENT_LIMIT_A,
            "current_scale_nm_per_a": CURRENT_SCALE_NM_PER_A,
            "strict_current_a": STRICT_CURRENT_A,
        },
        "cells": cells,
        "comparisons": comparisons,
        "decision": (
            "EARN_ONE_V137_DUAL_CHECKPOINT_WARM_START_PREREGISTRATION"
            if not failed
            else "CLOSE_PHASE_CONSISTENT_WARM_START"
        ),
        "authority": {
            "v137_dual_checkpoint_preregistration": not failed,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V136 warm-start startup screen\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Four paired 64-tick CPU cells; no formal behavior, training, "
        "Colab, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
