#!/usr/bin/env python3
"""Freeze the complete winner-v10 nominal behavior/protection gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v10_nominal_behavior_preregistration.json"
RUNNER = ROOT / "tools" / "run_winner_v10_nominal_behavior.py"
V9_HELPER = ROOT / "tools" / "run_winner_v9_nominal_behavior.py"
V9_PREREG = ANALYSIS / "winner_v9_nominal_behavior_preregistration.json"
V10_CONTRACT = ANALYSIS / "winner_v10_inward_torque_contract_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
FIT_P30 = ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
FIT_P31_34 = ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--physical-model-xml", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError("winner-v10 nominal preregistration already exists")
    previous = json.loads(V9_PREREG.read_text(encoding="utf-8"))
    contract = json.loads(V10_CONTRACT.read_text(encoding="utf-8"))
    if (
        contract["status"]
        != "PASS_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT"
    ):
        raise ValueError("winner-v10 representation contract is not passed")
    model_xml = args.physical_model_xml.resolve()
    if sha256(model_xml) != contract["xml"]["output_model_sha256"]:
        raise ValueError("winner-v10 physical XML does not match passed contract")
    required_files = dict(previous["playground"]["required_file_hashes"])
    required_files[
        "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml"
    ] = sha256(model_xml)
    policy_paths = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    input_paths = {
        "runner": RUNNER,
        "v9_nominal_helper": V9_HELPER,
        "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
        "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
        "actuator_model": ROOT / "tools/actuator_bridge_model.py",
        "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
        "v10_contract_result": V10_CONTRACT,
        "current_contract": ANALYSIS
        / "winner_v3_current_gate_application_contract.json",
        "reference_feature_table": REFERENCE,
        "fit_p30": FIT_P30,
        "fit_p31_34": FIT_P31_34,
    }
    payload = {
        "schema_version": "open_duck_mini.winner_v10_nominal_behavior_preregistration.v1",
        "status": "FROZEN_WINNER_V10_NOMINAL_BEHAVIOR_NOT_RUN",
        "causal_question": "Does the unchanged winner-v9 gait pass the complete nominal behavior and protection gate when the physical torque boundary is represented one float32 step inward?",
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "policy_hashes": {
            name: sha256(path) for name, path in policy_paths.items()
        },
        "playground": {
            **previous["playground"],
            "required_file_hashes": required_files,
        },
        "matrix": previous["matrix"],
        "behavior_gates": previous["behavior_gates"],
        "protection_gate": previous["protection_gate"],
        "pass_rule": [
            "all 16 hash-bound cells complete for both policies, both fits, and all four commands",
            "all x=0 and moving behavior gates pass at both persistence checkpoints",
            "every joint tick passes unchanged peak-current, decimal peak-torque, measured-rate-vector, and overcurrent-duration gates",
            "the one-step-inward physical XML, composed 115-D Playground, and both unchanged policy hashes remain exact",
            "CPU only and no training, reward selection, retry, tolerance change, GPU, runtime, or robot work",
        ],
        "no_retry_or_tuning": "A failed run closes the exact winner-v10 policy route. Do not change policy, XML, fit, command, seed, duration, gate, tolerance, simulator, or population.",
        "pass_authorizes_only": "write a separate sequential R2 robustness preregistration starting from condition 1",
        "authority": {
            "one_cpu_nominal_behavior_run": True,
            "training_gpu_colab_runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"PREREGISTRATION={OUTPUT}")
    print(f"PREREGISTRATION_SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
