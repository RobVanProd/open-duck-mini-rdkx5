#!/usr/bin/env python3
"""Freeze the complete winner-v7 protected-base behavior revalidation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from compose_winner_v7_playground import NETWORK_HASH, PATCH_HASHES


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v7_full_behavior_revalidation_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_FULL_BEHAVIOR_REVALIDATION_PREREGISTRATION_20260720.md"
RUNNER = ROOT / "tools/run_winner_v7_full_behavior_revalidation.py"
COMPOSER = ROOT / "tools/compose_winner_v7_playground.py"
TRANSFORMER = ROOT / "tools/run_winner_v7_inward_projection_contract.py"
EVALUATOR = ROOT / "tools/evaluate_ground_up_policy.py"
CLOSED_LOOP = ROOT / "tools/closed_loop_sim_eval.py"
ACTUATOR_MODEL = ROOT / "tools/actuator_bridge_model.py"
AGGREGATOR = ROOT / "tools/aggregate_ground_up_robustness_r1.py"
V7_PREREGISTRATION = ANALYSIS / "winner_v7_inward_projection_preregistration.json"
V7_RESULT = ANALYSIS / "winner_v7_inward_projection_contract_result.json"
R2_PREREGISTRATION = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"
R2_EVALUATOR_CONTRACT = ANALYSIS / "ground_up_robustness_r2_evaluator_contract.json"
R2_REPORTING_CONTRACT = ANALYSIS / "ground_up_robustness_r2_reporting_contract.json"
CURRENT_CONTRACT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FITS = {
    "p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
}
PLAYGROUND_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
PLAYGROUND_FILE_HASHES = {
    "playground/common/phase_moe_networks.py": "e57f417358afd8fdc5daa0126da8d3216b6ac6c1c1871d46f92afbcb6f4a44e7",
    "playground/common/recurrent_ppo_networks.py": "e68d12fc01a89876930d35fd39f6c9da45345dbf1962f2ebbf11f89478881b8b",
    "playground/common/reference_residual_ppo_networks.py": NETWORK_HASH,
    "playground/common/rewards.py": "cfd5ba21a0f0c6fa98cb4485dd7bfc724693df1841fe4bd6dd7bf9023c5a997a",
    "playground/common/runner.py": "815658c9ba4a8e5d953540bba64e57095b1011dc3cfa728e2145df2b9b1d46f0",
    "playground/open_duck_mini_v2/custom_rewards.py": "f0ae6e50c379626d43c7eaa317c4395e219288456a50f6a8097bfd1ea2399b32",
    "playground/open_duck_mini_v2/joystick.py": "edcedfa787a48c4f1af4316a5140a87eca5072bf3b223f6d87a4a656630a6904",
    "playground/open_duck_mini_v2/runner.py": "d116dabf84a0623313ea63ef4cb4cad6347e7f94bfd2e70b15b4901889e7e8dc",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    v7_result = json.loads(V7_RESULT.read_text(encoding="utf-8"))
    if v7_result["status"] != "PASS_WINNER_V7_INWARD_PROJECTION_TRANSFORM_CONTRACT":
        raise ValueError("winner-v7 graph contract has not passed")
    if v7_result["decision"] != (
        "AUTHORIZE_SEPARATE_FULL_BEHAVIOR_REVALIDATION_PREREGISTRATION_ONLY"
    ):
        raise ValueError("winner-v7 result does not authorize this preregistration")

    r2 = json.loads(R2_PREREGISTRATION.read_text(encoding="utf-8"))
    conditions = [{"id": "NOMINAL", "override": None, "expected": "PASS"}]
    for row in r2["conditions_in_strict_order"][:6]:
        conditions.append({**row, "expected": "PASS"})
    boundary = r2["conditions_in_strict_order"][6]
    conditions.append({**boundary, "expected": "KNOWN_BOUNDARY_FAILURE"})

    frozen_paths = {
        "runner": RUNNER,
        "composer": COMPOSER,
        "transformer": TRANSFORMER,
        "evaluator": EVALUATOR,
        "closed_loop": CLOSED_LOOP,
        "actuator_model": ACTUATOR_MODEL,
        "aggregator": AGGREGATOR,
        "v7_preregistration": V7_PREREGISTRATION,
        "v7_result": V7_RESULT,
        "r2_preregistration": R2_PREREGISTRATION,
        "r2_evaluator_contract": R2_EVALUATOR_CONTRACT,
        "r2_reporting_contract": R2_REPORTING_CONTRACT,
        "current_contract": CURRENT_CONTRACT,
        "reference_feature_table": REFERENCE,
        "fit_p30": FITS["p30"],
        "fit_p31_34": FITS["p31_34"],
    }
    result = {
        "schema_version": "winner_v7.full_behavior_revalidation_preregistration.v2",
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_128_CELL_CPU_BEHAVIOR_REVALIDATION",
        "causal_question": (
            "Does the distinct inward-rounded protected base retain every established "
            "nominal and passed-R2 behavior gate, remain inside the prospective current "
            "protection envelope, and reproduce rather than hide the known first R2 boundary?"
        ),
        "playground": {
            "required_commit": PLAYGROUND_COMMIT,
            "patches_in_order": [
                {"name": name, "canonical_lf_sha256": digest}
                for name, digest in PATCH_HASHES.items()
            ],
            "copied_network_canonical_lf_sha256": NETWORK_HASH,
            "required_composed_file_hashes": PLAYGROUND_FILE_HASHES,
            "task": "flat_terrain_backlash",
            "reset_mode": "home-support",
        },
        "input_hashes": {
            name: sha256(path) for name, path in frozen_paths.items()
        },
        "policies": [
            {
                "label": row["label"],
                "source_sha256": row["source_sha256"],
                "transformed_sha256": row["output_sha256"],
            }
            for row in v7_result["policies"]
        ],
        "matrix": {
            "conditions_in_order": conditions,
            "fits": [
                {"id": name, "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
                for name, path in FITS.items()
            ],
            "commands_x": [0.0, 0.074, 0.077, 0.08],
            "seed": 167931544,
            "duration_ticks": 600,
            "frequency_hz": 50,
            "checkpoints": ["half", "final"],
            "cells_per_condition": 16,
            "total_cells": 128,
        },
        "behavior_gates": {
            "x0": {
                "samples": 600,
                "termination_reason": "duration_complete",
                "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
                "maximum_absolute_mean_local_velocity_m_s": 0.02,
                "maximum_body_pitch_p95_rad": 0.25,
                "minimum_base_height_m": 0.12,
                "maximum_pitch_tracking_p95_rad": 0.20,
                "maximum_action_saturation_pct": 0.0,
                "maximum_rate_excess_rad_s": 0.0,
            },
            "moving": {
                "samples": 600,
                "termination_reason": "duration_complete",
                "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
                "bilateral_transitions": True,
                "positive_mean_local_velocity": True,
                "maximum_pitch_tracking_p95_rad": 0.20,
                "maximum_action_saturation_pct": 0.0,
                "maximum_rate_excess_rad_s": 0.0,
            },
            "known_boundary": (
                "TORSO_COM_X_NEG must remain a non-pass across all four checkpoint/fit "
                "matrices; it has no advancement or closest-result role."
            ),
        },
        "current_gate": {
            "per_joint_peak_current_a_max": 2.5,
            "strict_overcurrent_threshold_a": 2.0,
            "strict_overcurrent_max_consecutive_ticks": 99,
            "sample_clock": "exact simulator 50 Hz ticks",
            "population": "every recorded tick, including early-terminated cells",
            "all_joints_must_pass": True,
            "rated_current_p95_a": 0.65,
            "rated_current_p95_role": "reported diagnostic only; not candidate pass/fail",
        },
        "pass_rule": [
            "all frozen hashes, transformed policy hashes, playground commit, and CPU-only attestations match",
            "all 128 cells and raw trace hashes are present with exact policy, fit, command, seed, duration, and dynamics readbacks",
            "nominal plus the six previously passed R2 conditions pass every unchanged x=0 and moving gate under both checkpoints and both actuator fits",
            "every recorded joint tick passes the 2.5 A peak and fewer-than-100-consecutive-ticks-above-2.0-A protection rule",
            "TORSO_COM_X_NEG remains a non-pass in all four checkpoint/fit matrices and cannot be promoted",
            "no training, reward selection, tolerance change, retry, or closest-result promotion occurs",
        ],
        "all_or_nothing": True,
        "no_retry_or_tuning": (
            "A failed formal run closes this exact winner-v7 protected base. Do not "
            "change the projection margin, current rule, gates, conditions, populations, "
            "seed, duration, fit, checkpoint, simulator revision, or tolerance."
        ),
        "pass_authorizes_only": (
            "design and runtime review of a distinct winner-v7 automatic-calibration "
            "interface preregistration; no optimizer or behavior training"
        ),
        "authority": {
            "one_exact_local_cpu_behavior_run": True,
            "raw_and_large_artifacts_external_to_repository": True,
            "training_ppo_colab_gpu_igpu": False,
            "runtime_implementation_or_gate5": False,
            "rdkx5_robot_torque_motion_deployment": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v7 Full Behavior Revalidation Preregistration\n\n"
        f"Status: `{result['status']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "The frozen CPU matrix contains 128 cells: nominal, six established R2 "
        "passes, and the known torso-COM boundary, each under both checkpoints, "
        "both measured actuator fits, and all four commands. Existing behavior "
        "thresholds are unchanged. The prospective 2.5 A peak / 2.0 A for 100 "
        "ticks protection rule applies to every recorded joint tick; 0.65 A p95 "
        "is diagnostic only.\n\n"
        "A pass authorizes only design and runtime review of a distinct winner-v7 "
        "automatic-calibration interface. No training, accelerator, runtime action, "
        "robot access, torque, motion, Gate 5, deployment, or clearance is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
