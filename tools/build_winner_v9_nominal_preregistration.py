#!/usr/bin/env python3
"""Freeze the 16-cell winner-v9 nominal behavior/current/torque gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v9_nominal_behavior_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v9_nominal_behavior.py"
V9_RESULT = ANALYSIS / "winner_v9_stored_bound_contract_result.json"
CURRENT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_P30 = ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
FIT_P31 = ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"
REPO_INPUTS = {
    "runner": RUNNER,
    "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
    "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
    "actuator_model": ROOT / "tools/actuator_bridge_model.py",
    "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
    "v9_contract_result": V9_RESULT,
    "current_contract": CURRENT,
    "reference_feature_table": REFERENCE,
    "fit_p30": FIT_P30,
    "fit_p31_34": FIT_P31,
}
PLAYGROUND_FILES = [
    "playground/common/phase_moe_networks.py",
    "playground/common/recurrent_ppo_networks.py",
    "playground/common/reference_residual_ppo_networks.py",
    "playground/common/rewards.py",
    "playground/common/runner.py",
    "playground/open_duck_mini_v2/custom_rewards.py",
    "playground/open_duck_mini_v2/joystick.py",
    "playground/open_duck_mini_v2/runner.py",
    "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml",
    "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    import subprocess

    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    v9 = json.loads(V9_RESULT.read_text(encoding="utf-8"))
    if v9["decision"] != "AUTHORIZE_SEPARATE_WINNER_V9_NOMINAL_PREREGISTRATION_ONLY":
        raise ValueError("winner-v9 nominal preregistration is not authorized")
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    gate = current["prospective_offline_candidate_gate"]
    playground = args.playground_root.resolve()
    payload = {
        "schema_version": "open_duck_mini.winner_v9_nominal_behavior_preregistration.v1",
        "status": "FROZEN_WINNER_V9_NOMINAL_BEHAVIOR_NOT_RUN",
        "source_commit": args.source_commit,
        "causal_question": "Does the unchanged protected gait survive the jointly corrected full measured rate vector and physical torque-limited plant while passing every nominal behavior, current, torque, duration, and x=0 gate?",
        "input_hashes": {name: sha256(path) for name, path in REPO_INPUTS.items()},
        "policy_hashes": {"half": sha256(args.policy_half), "final": sha256(args.policy_final)},
        "playground": {
            "required_commit": git_head(playground),
            "required_file_hashes": {path: sha256(playground / path) for path in PLAYGROUND_FILES},
            "task": "flat_terrain_backlash",
            "reset_mode": "home-support",
        },
        "matrix": {
            "fits": ["p30", "p31_34"],
            "checkpoints": ["half", "final"],
            "commands_x": [0.0, 0.074, 0.077, 0.08],
            "seed": 167931544,
            "frequency_hz": 50,
            "duration_ticks": 600,
            "total_cells": 16,
        },
        "behavior_gates": {
            "x0": {
                "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
                "maximum_absolute_mean_local_velocity_m_s": 0.02,
                "maximum_action_saturation_pct": 0.0,
                "maximum_body_pitch_p95_rad": 0.25,
                "maximum_pitch_tracking_p95_rad": 0.2,
                "maximum_rate_excess_rad_s": 0.0,
                "minimum_base_height_m": 0.12,
                "samples": 600,
                "termination_reason": "duration_complete",
            },
            "moving": {
                "bilateral_transitions": True,
                "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
                "maximum_action_saturation_pct": 0.0,
                "maximum_pitch_tracking_p95_rad": 0.2,
                "maximum_rate_excess_rad_s": 0.0,
                "positive_mean_local_velocity": True,
                "samples": 600,
                "termination_reason": "duration_complete",
            },
        },
        "protection_gate": {
            "all_joints_must_pass": True,
            "per_joint_peak_current_a_max": gate["per_joint_peak_current_a_max"],
            "per_joint_peak_torque_nm_max": gate["per_joint_peak_torque_nm_max"],
            "strict_overcurrent_threshold_a": gate["strict_overcurrent_threshold_a"],
            "strict_overcurrent_max_consecutive_ticks": gate["strict_overcurrent_max_consecutive_ticks"],
            "full_measured_vector_excess_rad_s_max": 0.0,
            "rated_current_p95_a": gate["rated_current_p95"]["value_a"],
            "rated_current_p95_role": "diagnostic only",
            "population": "every recorded joint tick including early termination",
        },
        "pass_rule": [
            "all 16 hash-bound cells complete for both policies, both fits, and all four commands",
            "all x=0 and moving behavior gates pass at both persistence checkpoints",
            "every joint tick passes peak current, peak torque, full measured vector, and fewer-than-100-consecutive-ticks-above-2A",
            "the physical XML and composed 115-D Playground remain exact and no dynamics override is active",
            "CPU only and no training, reward selection, retry, tolerance change, GPU, runtime, or robot work",
        ],
        "pass_authorizes_only": "write a separate sequential R2 robustness preregistration starting from condition 1",
        "no_retry_or_tuning": "A failed run closes the exact winner-v9 policy route. Do not change policy, XML, fit, command, seed, duration, gate, tolerance, simulator, or population.",
        "authority": {"one_cpu_nominal_behavior_run": True, "training_gpu_colab_runtime_robot_torque_motion_gate5": False, "robot_clearance": False},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
