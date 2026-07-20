#!/usr/bin/env python3
"""Freeze the separately named winner-v6b zero-PPO CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V6B_ZERO_PPO_CPU_CONTRACT_PREREGISTRATION_20260720.md"
NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
BASE_CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
CHECKER = ROOT / "tools/check_winner_v6b_zero_ppo_cpu_contract.py"
IMPORTER = ROOT / "tools/import_winner_v6b_zero_ppo_cpu_contract.py"
RUNTIME_RECEIPT = ANALYSIS / "winner_v6_bound_semantics_review_receipt.json"
FAILED_RESULT = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_result.json"
ATTRIBUTION = ANALYSIS / "winner_v6_zero_ppo_contract_hold_attribution.json"
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
    failed_result = json.loads(FAILED_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if receipt["decision"] != "AUTHORIZE_POLICY_V6B_ZERO_PPO_CPU_CONTRACT_ONLY":
        raise ValueError("runtime has not authorized winner-v6b")
    if receipt["artifact_sha256"] != "5505308efc146146c3609fc7594eb4dfa4d27ad67d9336673cb38fc6692b895f":
        raise ValueError("runtime bound-semantics review receipt changed")
    if failed_result["status"] != "HOLD_WINNER_V6_ZERO_PPO_CPU_SOFTWARE_CONTRACT":
        raise ValueError("the completed winner-v6 result must remain held")
    if attribution["decision"] != "REQUEST_RUNTIME_BOUND_SEMANTICS_REVIEW_NO_RETRY":
        raise ValueError("winner-v6 hold attribution is not the reviewed one")

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
            "role": f"unchanged protected persistent G1/T2 {label} checkpoint",
        }
        for label, path in PROTECTED.items()
    }
    input_hashes = {
        "network_source": sha256(NETWORK_SOURCE),
        "base_checker": sha256(BASE_CHECKER),
        "v6b_checker": sha256(CHECKER),
        "importer": sha256(IMPORTER),
        "runtime_review_receipt": sha256(RUNTIME_RECEIPT),
        "failed_v6_result": sha256(FAILED_RESULT),
        "hold_attribution": sha256(ATTRIBUTION),
        "protected_half": protected_checkpoints["half"]["sha256"],
        "protected_final": protected_checkpoints["final"]["sha256"],
    }
    result = {
        "schema_version": "winner_v6b.zero_ppo_cpu_software_contract_preregistration.v1",
        "status": "PREREGISTERED_NOT_RUN",
        "decision": "AUTHORIZE_ONE_EXACT_CPU_ONLY_V6B_ZERO_PPO_CONTRACT_RUN",
        "not_a_retry": {
            "failed_v6_result_remains_held": True,
            "failed_v6_result_sha256": sha256(FAILED_RESULT),
            "new_name": "winner-v6b-bound-population-split",
            "only_change": (
                "separate default-off identity, enabled-adapter stress bounds, and "
                "protected physically chained full-action assertions"
            ),
        },
        "runtime_review": {
            "receipt_path": str(RUNTIME_RECEIPT.relative_to(ROOT)).replace("\\", "/"),
            "receipt_sha256": sha256(RUNTIME_RECEIPT),
            "runtime_artifact_sha256": receipt["artifact_sha256"],
            "runtime_commit": receipt["review_commit"],
        },
        "input_hashes": input_hashes,
        "protected_checkpoints": protected_checkpoints,
        "expected_abi": {
            "calibrator": calibrator_abi,
            "locomotion": locomotion_abi,
        },
        "unchanged_from_failed_v6": {
            "network_source_and_weights": True,
            "calibrator_seed": 60720,
            "locomotion_adapter_seed": 60721,
            "protected_identity_seeds": [60740, 60750],
            "physical_chain_seeds": [60742, 60752],
            "stress_parameter_seed": 60730,
            "stress_input_seed": 60731,
            "calibration_ticks": 250,
            "locomotion_ticks_per_checkpoint": 32,
            "step_zero_cases": 66,
            "protected_identity_cases_per_checkpoint": 66,
            "stress_cases_per_graph": 256,
            "invalid_handoff_case_count": 9,
            "numeric_tolerance": 1.0e-7,
        },
        "bound_populations": {
            "default_off_identity": {
                "population": "66 arbitrary finite ABI tensors per protected checkpoint",
                "rule": "action and previous-action state byte-for-byte protected identity; no adapter projection",
            },
            "enabled_adapter_stress": {
                "population": "256 arbitrary finite tensors for each deliberately nonzero-head graph",
                "rule": "absolute [-1,1] and protected winner-v2 per-joint delta projection",
            },
            "protected_physical_chain": {
                "population": "32 chained ticks per checkpoint using the unchanged seeds",
                "dependent_fields": (
                    "obs joint position, applied target, and three action-history slots "
                    "derive from prior confirmed output; no independent random pairing"
                ),
                "rule": "protected/expanded bit identity, finite output, and full final-action bounds",
            },
        },
        "numeric_tolerance": 1.0e-7,
        "all_or_nothing": True,
        "no_retry_or_tuning": (
            "A failed v6b formal run closes winner-v6 dynamic calibration. Do not "
            "change seeds, weights, populations, tolerance, checkpoint, ABI, or pass rule."
        ),
        "pass_rule": [
            "all hashes, ABIs, CPU-only assertions, and unchanged initialization checks pass",
            "all 66 step-zero actions are exact zero and recurrent response state evolves with finite auxiliary gradient",
            "the 250-tick calibration and both 32-tick JAX/ONNX handoff chains agree within 1e-7",
            "all nine invalid handoffs fail closed",
            "both default-off protected checkpoint identities are bit exact for all arbitrary-input cases",
            "both deliberately enabled stress graphs obey their graph-owned action projections",
            "both physically chained protected populations obey the complete final-action contract",
            "no true configuration label enters either graph or auxiliary target",
        ],
        "pass_authorizes_only": (
            "write and review a separate calibrator-training preregistration; no optimizer step"
        ),
        "authority": {
            "one_exact_local_cpu_v6b_run": True,
            "training_or_ppo": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_v2_implementation": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "gate5_deployment_or_robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result_sha = sha256(OUTPUT_JSON)
    OUTPUT_MD.write_text(
        "# Winner-v6b Zero-PPO CPU Contract Preregistration\n\n"
        f"Status: `{result['status']}`\n\n"
        f"JSON SHA-256: `{result_sha}`\n\n"
        "The held winner-v6 contract is not retried or reclassified. Runtime review "
        "authorized this separately named contract with one change only: disabled, "
        "enabled, and physically chained action-bound populations are evaluated under "
        "their correct semantics. All weights, seeds, checkpoints, ABIs, counts, the "
        "250-tick chain, fail-closed cases, and `1e-7` tolerance remain unchanged.\n\n"
        "A pass authorizes only a separate calibrator-training preregistration. No "
        "optimizer step, Colab, GPU, runtime implementation, robot access, torque, "
        "motion, Gate 5, deployment, or robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "sha256": result_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
