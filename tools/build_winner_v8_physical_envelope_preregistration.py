#!/usr/bin/env python3
"""Freeze the winner-v8 zero-behavior physical-envelope interaction contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v8_physical_envelope_contract_preregistration.json"
RUNNER = ROOT / "tools" / "run_winner_v8_physical_envelope_contract.py"
REPO_INPUTS = {
    "force_attribution": ANALYSIS / "winner_v7_actuator_force_limit_attribution.json",
    "full_vector_attribution": ANALYSIS / "winner_v7_full_measured_vector_attribution.json",
    "current_contract": ANALYSIS / "winner_v3_current_gate_application_contract.json",
    "measured_envelope": ANALYSIS / "winner_v5_automatic_support_recovery_preregistration.json",
}
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


def source(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}


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
    envelope = json.loads(REPO_INPUTS["measured_envelope"].read_text(encoding="utf-8"))
    rates = [float(envelope["actuator_plants"]["per_joint"][joint]["conservative_velocity_limit_rad_s"]) for joint in JOINT_NAMES]
    current = json.loads(REPO_INPUTS["current_contract"].read_text(encoding="utf-8"))
    torque_limit = float(current["prospective_offline_candidate_gate"]["per_joint_peak_torque_nm_max"])
    current_equivalent = float(current["prospective_offline_candidate_gate"]["per_joint_peak_current_a_max"]) * float(current["conversion"]["manufacturer_motor_constant_nm_per_a"])
    force_limit = min(torque_limit, current_equivalent)
    payload = {
        "schema_version": "open_duck_mini.winner_v8_physical_envelope_contract_preregistration.v1",
        "status": "FROZEN_WINNER_V8_PHYSICAL_ENVELOPE_CONTRACT",
        "source_commit": args.source_commit,
        "causal_hypothesis": "The two closed single-factor routes show that neither the overpowered XML ceiling nor the incomplete rate vector is sufficient alone. A distinct interaction applies both already-frozen physical constraints before any training and asks only whether the software/graph contract is exact.",
        "frozen_inputs": {
            "runner_sha256": sha256(RUNNER),
            "source_half": {"filename": args.source_half.name, "sha256": sha256(args.source_half)},
            "source_final": {"filename": args.source_final.name, "sha256": sha256(args.source_final)},
            "model_xml_sha256": sha256(args.model_xml),
            "scene_xml_sha256": sha256(args.scene_xml),
            **{name: source(path) for name, path in REPO_INPUTS.items()},
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
            "max_action_delta_equation": "float32(rate_rad_s * 0.02 / 0.25)",
            "safe_delta_equation": "max_action_delta - 4*float32_epsilon",
            "changed_graph_initializers_only": ["max_action_delta", "v7_safe_max_action_delta"],
            "physical_force_limit_nm": force_limit,
            "physical_limit_equation": "min(1.91229675 N.m stall torque, 2.5 A * 0.784532 N.m/A)",
            "xml_change": "only the active inherited sts3215 position forcerange; scene unchanged",
        },
        "pass_rule": [
            "all frozen hashes and both 115+14 stateful ABIs exact",
            "only max_action_delta and v7_safe_max_action_delta change and every node is exact",
            "all 8192 arbitrary CPU cases and both 256-tick moving chains obey the full measured vector with zero tolerance",
            "both 256-tick x=0 chains emit exact-zero action and state",
            "only the active XML force range changes; all 14 actuators inherit +/-1.91229675 N.m and the scene is byte-exact",
            "no simulator behavior, training, reward selection, GPU, runtime, or robot work runs",
        ],
        "pass_authorizes_only": "write and review a separate sequential nominal behavior/current/torque preregistration",
        "no_retry_or_tuning": "A failed contract closes this exact two-factor transform. Do not change limits, margins, graph source, XML source, seeds, cases, ticks, tolerance, or ABI.",
        "authority": {"zero_behavior_cpu_contract": True, "behavior_training_gpu_colab": False, "runtime_robot_torque_motion_gate5": False, "robot_clearance": False},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE={OUTPUT}")
    print(f"SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
