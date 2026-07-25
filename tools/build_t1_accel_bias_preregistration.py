#!/usr/bin/env python3
"""Freeze the CPU-only T1 observation-acceleration bias dose response."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t1_accel_bias_preregistration.json"
MARKDOWN = ANALYSIS / "T1_ACCEL_BIAS_PREREGISTRATION_20260725.md"
POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
FIT = ANALYSIS / "actuator_response_fit_corrected_knee.json"
PUBLISHED_AUDIT = ANALYSIS / "published_policy_propulsion_x008_straight_audit.json"
ORIGINAL_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval.py"
T1_EVALUATOR = ROOT / "tools" / "closed_loop_sim_eval_t1_accel_bias.py"
CONTRACT_RUNNER = ROOT / "tools" / "check_t1_accel_bias_contract.py"
MATRIX_RUNNER = ROOT / "tools" / "run_t1_accel_bias_dose_response.py"

EXPECTED = {
    "policy": "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067",
    "fit": "40d2aefbdaeac986fc856aade8170f2a9d72831613a7a30873bfff0846e4f1bb",
    "playground_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
}
COMMANDS = [0.0, 0.04, 0.074, 0.077, 0.08]
BIASES = [-2.0, -1.6, -1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
SEEDS = list(range(8))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def git_output(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--playground-root",
        type=Path,
        default=Path(r"D:\CodexProjects\Open_Duck_Playground-upstream-b9be205"),
    )
    args = parser.parse_args()
    playground = args.playground_root.resolve()

    paths = {
        "policy": POLICY,
        "fit": FIT,
        "published_x008_audit": PUBLISHED_AUDIT,
        "original_evaluator": ORIGINAL_EVALUATOR,
        "t1_evaluator": T1_EVALUATOR,
        "contract_runner": CONTRACT_RUNNER,
        "matrix_runner": MATRIX_RUNNER,
    }
    missing = sorted(name for name, path in paths.items() if not path.is_file())
    hashes = {
        name: None if not path.is_file() else sha256(path)
        for name, path in paths.items()
    }
    playground_commit = (
        git_output(playground, "rev-parse", "HEAD")
        if (playground / ".git").exists()
        else None
    )
    playground_status = (
        git_output(playground, "status", "--porcelain")
        if (playground / ".git").exists()
        else "missing"
    )
    failed_checks = []
    for name in ("policy", "fit"):
        if hashes[name] != EXPECTED[name]:
            failed_checks.append(f"hash:{name}")
    if playground_commit != EXPECTED["playground_commit"]:
        failed_checks.append("playground_commit")
    if playground_status:
        failed_checks.append("playground_not_clean")

    matrix = [
        {
            "bias_m_s2": bias,
            "command_x_m_s": command,
            "seed": seed,
        }
        for bias in BIASES
        for command in COMMANDS
        for seed in SEEDS
    ]
    status = (
        "PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE"
        if not missing and not failed_checks
        else "HOLD_T1_ACCEL_BIAS_PREREGISTRATION"
    )
    payload = {
        "schema_version": "open_duck.t1_accel_bias_preregistration.v1",
        "status": status,
        "missing_inputs": missing,
        "failed_checks": failed_checks,
        "input_paths": {name: str(path) for name, path in paths.items()},
        "input_sha256": hashes,
        "expected_sha256": {
            "policy": EXPECTED["policy"],
            "fit": EXPECTED["fit"],
        },
        "playground": {
            "path": str(playground),
            "commit": playground_commit,
            "expected_commit": EXPECTED["playground_commit"],
            "porcelain_status": playground_status,
        },
        "hypothesis": (
            "A constant +1.6 m/s^2 error in raw policy observation element 3 "
            "is a first-order cause of BEST_WALK's x=0.08 behavior mismatch."
        ),
        "insertion_contract": {
            "observation_index": 3,
            "quantity": "raw local-frame accelerometer x in m/s^2",
            "location": (
                "after all simulator observation construction, optional IMU "
                "delay, and native quantization; immediately before the "
                "unchanged ONNX input feed and embedded normalizer"
            ),
            "equation": "obs_for_policy[3]=float32(obs[3]+float32(bias_m_s2))",
            "other_observation_elements": "unchanged at the insertion point",
            "policy_graph": "unchanged",
        },
        "frozen_configuration": {
            "policy": "BEST_WALK_ONNX_2.onnx",
            "task": "flat_terrain_backlash",
            "bridge_mode": "vanilla",
            "duration_s": 5.0,
            "ticks_per_cell": 250,
            "commands_x_m_s": COMMANDS,
            "biases_m_s2": BIASES,
            "seeds": SEEDS,
            "cell_count": len(matrix),
            "expected_observation_dim": 101,
            "expected_action_dim": 14,
            "eval_role": "reproduction",
            "policy_or_normalizer_modification": False,
            "mjcf_or_gate_modification": False,
        },
        "matrix": matrix,
        "matrix_sha256": canonical_sha256(matrix),
        "reported_per_cell": [
            "mean_local_vx_m_s",
            "termination_reason",
            "fall",
            "command_tracking_ratio",
            "body_pitch_mean_rad",
            "body_pitch_max_rad",
            "body_pitch_abs_max_rad",
            "pitch_chain_target_velocity_p95_max_rad_s",
            "actuator_force_peak_nm",
        ],
        "decision_rule": {
            "primary_cell_group": {
                "command_x_m_s": 0.08,
                "baseline_bias_m_s2": 0.0,
                "test_bias_m_s2": 1.6,
                "aggregation": "arithmetic mean over seeds 0-7",
            },
            "first_order_support_if_any": {
                "mean_local_vx_relative_degradation_gte": 0.40,
                "fall_count_increase_gte": 2,
                "mean_body_pitch_forward_shift_rad_gte": 0.05235987755982989,
            },
            "pitch_sign": (
                "quat_wxyz_to_pitch is positive rotation about +Y; with "
                "Playground +X forward and +Z up, positive pitch is "
                "nose-forward/down. forward_shift=biased_mean-baseline_mean"
            ),
            "close_t1_only_if": (
                "for every bias at every nonzero command, each aggregated "
                "numeric metric changes by strictly less than 10% relative "
                "to its same-command zero-bias value, and no command/bias "
                "group adds a fall; zero-valued denominators make closure "
                "false unless the compared value is also exactly zero"
            ),
            "close_metrics": [
                "mean_local_vx_m_s",
                "command_tracking_ratio",
                "body_pitch_mean_rad",
                "body_pitch_max_rad",
                "body_pitch_abs_max_rad",
                "pitch_chain_target_velocity_p95_max_rad_s",
                "actuator_force_peak_nm",
            ],
            "otherwise": (
                "INCONCLUSIVE_T1; consult T2 only if its hash-frozen raw "
                "telemetry becomes available"
            ),
            "selection_weight": 0,
        },
        "execution_contract": {
            "required_pre_matrix_check": "PASS_T1_ACCEL_BIAS_CONTRACT",
            "zero_bias_equivalence": (
                "T1 evaluator and original evaluator must produce identical "
                "zero-bias trace and result payloads after removing only "
                "new provenance fields and nondeterministic wall-clock time"
            ),
            "positive_bias_check": (
                "every captured tick must satisfy post-pre=float32(1.6) and "
                "the ONNX-fed obs[3] must equal the recorded post-bias value"
            ),
            "resume": (
                "per-cell cache reuse is allowed only when the canonical "
                "cell contract and every preregistered input hash match; "
                "partial matrices carry no decision"
            ),
            "result_requires_all_cells": True,
        },
        "authority": {
            "offline_cpu_only": True,
            "robot_or_rdk_access": False,
            "policy_modification": False,
            "training_steps": 0,
            "hosted_compute": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(
        {
            "input_sha256": payload["input_sha256"],
            "playground": payload["playground"],
            "insertion_contract": payload["insertion_contract"],
            "frozen_configuration": payload["frozen_configuration"],
            "matrix_sha256": payload["matrix_sha256"],
            "decision_rule": payload["decision_rule"],
            "execution_contract": payload["execution_contract"],
        }
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T1 accelerometer-bias dose-response preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        f"- Matrix SHA-256: `{payload['matrix_sha256']}`\n"
        f"- Frozen cells: `{len(matrix)}` (11 biases x 5 commands x 8 seeds)\n"
        "- Primary decision: compare +1.6 m/s^2 against zero at x=0.08.\n"
        "- No policy, normalizer, simulator model, actuator bridge, or gate "
        "is changed.\n"
        "- The zero-bias equivalence contract must pass before the matrix.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
