#!/usr/bin/env python3
"""Freeze the winner-v6 zero-PPO CPU software contract before execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6_ZERO_PPO_CPU_CONTRACT_PREREGISTRATION_20260720.md"
INTERFACE = ANALYSIS / "winner_v6_dynamic_calibration_interface_preregistration.json"
RUNTIME_RECEIPT = ANALYSIS / "winner_v6_runtime_schema_review_receipt.json"
NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
IMPORTER = ROOT / "tools/import_winner_v6_zero_ppo_cpu_contract.py"
PROTECTED = {
    "half": ROOT / (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/"
        "T2_EQUAL_512000.onnx"
    ),
    "final": ROOT / (
        "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/"
        "T2_EQUAL_1024000.onnx"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor(name: str, shape: list[int]) -> dict[str, object]:
    return {"name": name, "dtype": "float32", "shape": shape}


def main() -> int:
    receipt = json.loads(RUNTIME_RECEIPT.read_text(encoding="utf-8"))
    if sha256(INTERFACE) != "a66ff7138bdc474c5bd6d0a8899eba041d00305a3d3bd38fc13b0c00e4c3007e":
        raise ValueError("winner-v6 interface request changed after runtime review")
    if receipt["decision"] != "AUTHORIZE_POLICY_ZERO_PPO_CPU_SOFTWARE_CONTRACT_ONLY":
        raise ValueError("runtime has not authorized the zero-PPO CPU contract")
    if receipt["artifact_sha256"] != "f0b95db839cff0c0329ffb1d9458c06e1ec6e6432b2b3ef84ef5f451550547c8":
        raise ValueError("runtime review receipt does not identify the reviewed artifact")

    calibrator_abi = {
        "inputs": [
            tensor("obs", [1, 115]),
            tensor("previous_action", [1, 14]),
            tensor("h_in", [1, 64]),
        ],
        "outputs": [
            tensor("calibration_actions", [1, 14]),
            tensor("previous_action_out", [1, 14]),
            tensor("h_out", [1, 64]),
        ],
    }
    locomotion_abi = {
        "inputs": [
            tensor("obs", [1, 115]),
            tensor("previous_action", [1, 14]),
            tensor("h_in", [1, 64]),
            tensor("calibration_context", [1, 64]),
        ],
        "outputs": [
            tensor("continuous_actions", [1, 14]),
            tensor("previous_action_out", [1, 14]),
            tensor("h_out", [1, 64]),
        ],
    }
    protected_checkpoints = {
        label: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path),
            "role": f"protected persistent G1/T2 {label} checkpoint after x=0 and envelope repairs",
        }
        for label, path in PROTECTED.items()
    }
    input_hashes = {
        "network_source": sha256(NETWORK_SOURCE),
        "checker": sha256(CHECKER),
        "importer": sha256(IMPORTER),
        "interface_preregistration": sha256(INTERFACE),
        "runtime_review_receipt": sha256(RUNTIME_RECEIPT),
        "protected_half": protected_checkpoints["half"]["sha256"],
        "protected_final": protected_checkpoints["final"]["sha256"],
    }
    result = {
        "schema_version": "winner_v6.zero_ppo_cpu_software_contract_preregistration.v1",
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_CPU_ONLY_ZERO_PPO_CONTRACT_RUN",
        "hypothesis": (
            "The reviewed two-graph interface can be initialized without changing either "
            "protected persistent G1/T2 checkpoint, while a nontrivial recurrent response "
            "state remains trainable through deployable next-response self-supervision and "
            "the graph itself enforces the measured action vector."
        ),
        "input_hashes": input_hashes,
        "protected_checkpoints": protected_checkpoints,
        "expected_abi": {
            "calibrator": calibrator_abi,
            "locomotion": locomotion_abi,
        },
        "fixed_initialization": {
            "calibrator_seed": 60720,
            "locomotion_adapter_seed": 60721,
            "calibrator_action_head": "exact-zero float32 kernel and bias",
            "locomotion_context_and_action_heads": "exact-zero float32 kernels and bias",
            "hidden_state": "deterministic nonzero recurrent encoder, tanh bounded",
            "true_configuration_labels": [],
        },
        "test_population": {
            "step_zero_cases": 66,
            "step_zero_case_rule": (
                "two fixed plus 64 PCG64 observations; previous action exact zero; "
                "two zero and 64 pseudorandom hidden-state controls"
            ),
            "calibration_ticks": 250,
            "locomotion_ticks_per_checkpoint": 32,
            "protected_identity_cases_per_checkpoint": 66,
            "protected_checkpoint_count": 2,
            "nonzero_head_bound_stress_cases_per_graph": 256,
            "invalid_handoff_cases": [
                "wrong shape", "wrong dtype", "nonfinite", "below bound",
                "above bound", "249 ticks", "251 ticks", "invalid tick",
                "invalid support",
            ],
        },
        "numeric_tolerance": 1.0e-7,
        "pass_rule": [
            "all frozen hashes and both exact ABIs match",
            "JAX and ONNX use CPU only",
            "calibrator step-zero action and action state are exact zero in all 66 cases",
            "calibrator hidden state is finite, tanh bounded, evolves, and receives finite nonzero auxiliary gradients",
            "all 250 calibration ticks and both 32-tick locomotion handoff chains agree between JAX and ONNX within 1e-7",
            "both protected G1/T2 checkpoints retain bit-exact action and previous-action outputs for all 66 identity cases",
            "arbitrary calibration context has exact-zero effect before training",
            "initial and deliberately nonzero-head stress graphs obey absolute and measured per-joint slew bounds",
            "all nine invalid calibration handoffs fail before an armable context is returned",
            "neither exported graph nor the auxiliary target uses a true configuration label",
        ],
        "all_or_nothing": True,
        "no_retry_or_tuning": (
            "A failed formal run is recorded as a hold. Do not change seeds, populations, "
            "tolerance, weights, source, protected checkpoint, or pass rule and rerun."
        ),
        "pass_authorizes_only": (
            "write and review a separate, frozen CPU calibrator-training preregistration; "
            "it does not itself authorize any optimizer step"
        ),
        "authority": {
            "one_exact_local_cpu_run": True,
            "ppo_or_any_training": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_v2_implementation": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "gate5_deployment_or_robot_clearance": False,
        },
        "limitations": [
            "This test establishes software mechanics, not support or walking behavior.",
            "Temporary ONNX outputs from the contract are not candidate policies.",
            "The frozen runtime-v1 101x14 path is not altered or evaluated here.",
        ],
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v6 Zero-PPO CPU Contract Preregistration\n\n"
        f"Status: `{result['status']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "This freezes one CPU-only, zero-training contract run. It uses the actual "
        "persistent G1/T2 half and final repaired ONNX checkpoints, requires bit-exact "
        "default-off action/state identity, then checks the 250-tick calibrator and "
        "handoff against a JAX reference at `1e-7`. It also proves invalid calibration "
        "cannot return an armable context.\n\n"
        "A pass authorizes only a separate calibrator-training preregistration. No PPO "
        "step, Colab, GPU, runtime implementation, robot access, torque, motion, Gate 5, "
        "deployment, or robot clearance is authorized here.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
