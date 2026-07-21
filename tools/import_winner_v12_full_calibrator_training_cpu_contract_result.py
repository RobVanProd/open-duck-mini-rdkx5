#!/usr/bin/env python3
"""Import and independently verify the Winner-v12 full-trainer CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract.json"
OUTPUT_JSON = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract_result.json"
OUTPUT_MD = (
    ANALYSIS / "WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_RESULT_20260721.md"
)
EXPECTED_RAW_SHA256 = "faf520ccf7a34e2da3cd3c86acadb66656dbcf99ce61f227116d8d5dbeba15c3"
EXPECTED_CONTRACT_LF_SHA256 = (
    "5795b079dfc47ab54a7d59faa217f282551fda0bb8c18f1857ceae9b79492eb6"
)
EXPECTED_RUN_ID = 29806824132
EXPECTED_RUN_COMMIT = "4c3cd478c41a18c3c06f4bac40d82837039431fd"
EXPECTED_ARTIFACT_ID = 8485829253
EXPECTED_ARTIFACT_DIGEST = (
    "sha256:f4f72120109d5db1a5360cf66b4589011e30ee63689924c8b66f907f34aa62c3"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate(raw: dict[str, Any]) -> None:
    if set(raw) != {
        "authority",
        "checks",
        "contract_lf_sha256",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "persistence_contract",
        "rollouts",
        "schema_version",
        "status",
    }:
        raise ValueError("raw full-training CPU result schema changed")
    if raw["schema_version"] != (
        "winner_v12.full_calibrator_training_cpu_contract_result.v1"
    ):
        raise ValueError("raw full-training CPU result version changed")
    if raw["status"] != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT":
        raise ValueError("full-training CPU contract did not pass")
    if raw["decision"] != (
        "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
    ):
        raise ValueError("full-training CPU result authority changed")
    if raw["contract_lf_sha256"] != EXPECTED_CONTRACT_LF_SHA256:
        raise ValueError("raw result is not bound to the frozen contract")
    if lf_sha256(CONTRACT) != EXPECTED_CONTRACT_LF_SHA256:
        raise ValueError("repository full-training CPU contract changed")

    checks = raw["checks"]
    if not isinstance(checks, dict) or not checks:
        raise ValueError("raw checks are absent")
    if not all(
        isinstance(name, str) and type(value) is bool for name, value in checks.items()
    ):
        raise ValueError("raw checks must be strict JSON booleans")
    observed_failed = sorted(name for name, passed in checks.items() if not passed)
    if raw["failed_checks"] != observed_failed or observed_failed:
        raise ValueError("raw PASS requires every check to pass")

    expected_versions = {
        "jax": "0.7.2",
        "jaxlib": "0.7.2",
        "mujoco": "3.9.0",
        "numpy": "2.0.2",
        "onnx": "1.22.0",
        "onnxruntime": "1.27.0",
        "python": "3.12.13",
    }
    versions = raw["environment"]["software_versions"]
    if versions != {
        "exact": True,
        "expected": expected_versions,
        "observed": expected_versions,
    } or raw["environment"]["jax_devices"] != ["TFRT_CPU_0"]:
        raise ValueError("formal CPU environment changed")
    if raw["execution"] != {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("zero-update CPU authority was exceeded")
    if raw["authority"] != {
        "formal_support_gate_executed": False,
        "full_calibrator_training_executed": False,
        "locomotion_training_or_behavior_executed": False,
        "pass_authorizes_only": "one frozen seed-120120 full calibrator training run",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("raw authority block changed")

    for stage in ("stage1", "stage2"):
        rollout = raw["rollouts"][stage]
        if rollout["environments"] != 80 or rollout["scheduled_tick_slots"] != 20_000:
            raise ValueError(f"{stage} rollout population changed")
        if not (
            0
            < rollout["valid_transitions"]
            <= rollout["attempted_transition_samples"]
            <= rollout["scheduled_tick_slots"]
        ):
            raise ValueError(f"{stage} rollout accounting changed")
        if len(rollout["receipt_sha256"]) != 64:
            raise ValueError(f"{stage} receipt hash is malformed")

    persistence = raw["persistence_contract"]
    if persistence["stage1_final"]["update"] != 100:
        raise ValueError("Stage-1 final checkpoint boundary changed")
    if persistence["half"]["update"] != 50:
        raise ValueError("Stage-2 half checkpoint boundary changed")
    graph = persistence["half"]["graph"]
    if graph["inputs"] != [
        {"name": "obs", "shape": [1, 115]},
        {"name": "previous_action", "shape": [1, 14]},
        {"name": "h_in", "shape": [1, 64]},
    ] or graph["outputs"] != [
        {"name": "calibration_actions", "shape": [1, 14]},
        {"name": "previous_action_out", "shape": [1, 14]},
        {"name": "h_out", "shape": [1, 64]},
    ]:
        raise ValueError("calibrator ONNX ABI changed")
    required_graph_checks = (
        graph["abi_exact"],
        graph["all_chain_outputs_finite"],
        graph["all_initializers_finite"],
        graph["jax_onnx_at_most_1e_7"],
        graph["previous_action_out_equals_action_bit_exact"],
        graph["training_only_tensors_absent"],
        graph["jax_onnx_max_abs_error"] <= 1.0e-7,
        not graph["forbidden_training_or_privileged_tokens"],
    )
    if not all(required_graph_checks):
        raise ValueError("calibrator ONNX proof changed")
    bank = persistence["half"]["onnx_observation_bank"]
    if (
        bank["shape"] != [250, 115]
        or not bank["all_finite"]
        or bank["nonzero_values"] <= 0
    ):
        raise ValueError("nonzero ONNX observation bank changed")
    if len(persistence["recovery"]["entries"]) != 4:
        raise ValueError("pending-artifact recovery proof changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("full-training CPU result is already imported")
    raw_path = args.raw_result.resolve()
    if sha256(raw_path) != EXPECTED_RAW_SHA256:
        raise ValueError("raw full-training CPU result hash changed")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    validate(raw)
    payload = dict(raw)
    payload["repository_attribution"] = {
        "github_artifact_digest": EXPECTED_ARTIFACT_DIGEST,
        "github_artifact_id": EXPECTED_ARTIFACT_ID,
        "github_run_commit": EXPECTED_RUN_COMMIT,
        "github_run_id": EXPECTED_RUN_ID,
        "raw_result_sha256": EXPECTED_RAW_SHA256,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 full-calibrator training CPU-contract result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run: `{EXPECTED_RUN_ID}`",
                f"- Raw result SHA-256: `{EXPECTED_RAW_SHA256}`",
                f"- Stage-1 attempted/valid: `{payload['rollouts']['stage1']['attempted_transition_samples']}` / `{payload['rollouts']['stage1']['valid_transitions']}`",
                f"- Stage-2 attempted/valid: `{payload['rollouts']['stage2']['attempted_transition_samples']}` / `{payload['rollouts']['stage2']['valid_transitions']}`",
                "- Optimizer updates: `0`",
                "- Formal support cells: `0`",
                "- Robot access/clearance: `0` / `false`",
                "",
                "Every frozen zero-update check passed in the exact CPU environment.",
                "This authorizes only one separately hash-bound seed-120120 full-calibrator",
                "training run. It does not authorize its 124-cell gate, locomotion training,",
                "deployment selection, Gate 5, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
