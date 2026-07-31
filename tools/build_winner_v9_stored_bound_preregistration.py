#!/usr/bin/env python3
"""Freeze the distinct winner-v9 stored physical-boundary contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v9_stored_bound_contract_preregistration.json"
RUNNER = ROOT / "tools" / "run_winner_v9_stored_bound_contract.py"
HELPER = ROOT / "tools" / "run_winner_v8_physical_envelope_contract.py"
ATTRIBUTION = ANALYSIS / "winner_v8_numeric_hold_attribution.json"
ENVELOPE = ANALYSIS / "winner_v5_automatic_support_recovery_preregistration.json"
CURRENT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
JOINT_NAMES = [
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll", "right_hip_yaw",
    "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-half", type=Path, required=True)
    parser.add_argument("--source-final", type=Path, required=True)
    parser.add_argument("--model-xml", type=Path, required=True)
    parser.add_argument("--scene-xml", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if attribution["decision"] != "PREREGISTER_DISTINCT_WINNER_V9_STORED_BOUND_CONTRACT_ONLY":
        raise ValueError("winner-v9 is not authorized by numeric attribution")
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    rates = [
        float(envelope["actuator_plants"]["per_joint"][joint]["conservative_velocity_limit_rad_s"])
        for joint in JOINT_NAMES
    ]
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    force_limit = min(
        float(current["prospective_offline_candidate_gate"]["per_joint_peak_torque_nm_max"]),
        float(current["prospective_offline_candidate_gate"]["per_joint_peak_current_a_max"])
        * float(current["conversion"]["manufacturer_motor_constant_nm_per_a"]),
    )
    payload = {
        "schema_version": "open_duck_mini.winner_v9_stored_bound_contract_preregistration.v1",
        "status": "FROZEN_WINNER_V9_STORED_BOUND_CONTRACT",
        "source_commit": args.source_commit,
        "causal_hypothesis": "Analytically round the public full measured delta inward by one float32 step, retain separate fixed internal headroom, and assert final outputs against the public stored boundary rather than the private implementation boundary.",
        "frozen_inputs": {
            "runner_sha256": sha256(RUNNER),
            "helper_sha256": sha256(HELPER),
            "source_half": {"filename": args.source_half.name, "sha256": sha256(args.source_half)},
            "source_final": {"filename": args.source_final.name, "sha256": sha256(args.source_final)},
            "model_xml_sha256": sha256(args.model_xml),
            "scene_xml_sha256": sha256(args.scene_xml),
            "numeric_attribution": {"path": str(ATTRIBUTION.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(ATTRIBUTION)},
        },
        "expected_abi": {
            "inputs": [
                {"name": "obs", "dtype": "float32", "shape": [1, 115]},
                {"name": "previous_action", "dtype": "float32", "shape": [1, 14]},
            ],
            "outputs": [
                {"name": "continuous_actions", "dtype": "float32", "shape": [1, 14]},
                {"name": "previous_action_out", "dtype": "float32", "shape": [1, 14]},
            ],
        },
        "transform": {
            "joint_order": JOINT_NAMES,
            "full_measured_rate_limits_rad_s": rates,
            "stored_delta_equation": "nextafter(float32(rate*0.02/0.25), -infinity)",
            "internal_delta_equation": "nextafter(stored_delta - 4*float32_epsilon, -infinity)",
            "changed_initializers_only": ["max_action_delta", "v7_safe_max_action_delta"],
            "physical_force_limit_nm": force_limit,
        },
        "pass_rule": [
            "both 115+14 stateful ABIs and every unchanged node/initializer are exact",
            "both stored and internal delta tensors equal their analytic equations",
            "8192 arbitrary cases and both 256-tick moving chains obey the stored physical boundary with zero tolerance",
            "both 256-tick x=0 chains remain exact zero",
            "all 14 actuators inherit the exact physical torque range and scene bytes remain exact",
            "CPU only; no behavior, training, simulator rollout, GPU, runtime, or robot work",
        ],
        "pass_authorizes_only": "write a separate sequential nominal winner-v9 behavior/current/torque preregistration",
        "no_retry_or_tuning": "A failure closes winner-v9. Do not alter source graphs, analytic rounding, margins, limits, seeds, cases, chain length, zero tolerance, XML, or ABI.",
        "authority": {
            "zero_behavior_cpu_contract": True,
            "behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
