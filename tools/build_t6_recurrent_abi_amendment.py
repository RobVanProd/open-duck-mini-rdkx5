#!/usr/bin/env python3
"""Freeze the pre-outcome recurrent-ABI correction for T6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t6_corrected_robustness_screen_preregistration.json"
OUTPUT = ANALYSIS / "t6_corrected_robustness_screen_abi_amendment.json"
MARKDOWN = (
    ANALYSIS / "T6_CORRECTED_ROBUSTNESS_SCREEN_ABI_AMENDMENT_20260725.md"
)
RUNNER = ROOT / "tools/run_t6_corrected_robustness_screen.py"
RESULT = ANALYSIS / "t6_corrected_robustness_screen_result.json"
CACHE = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t6_corrected_robustness_screen_v1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def onnx_abi(path: Path) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(path),
        providers=["CPUExecutionProvider"],
    )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "inputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_inputs()
        ],
        "outputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_outputs()
        ],
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite the T6 ABI amendment")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    manifests = list(CACHE.rglob("t6_block_manifest.json"))
    failed_log = (
        CACHE
        / "V121"
        / "V121_TRAIN_MATCHED_HALF"
        / "p30"
        / "stdout.log"
    )
    if (
        RESULT.exists()
        or manifests
        or not failed_log.is_file()
        or "Required inputs (['h_in']) are missing"
        not in failed_log.read_text(encoding="utf-8")
    ):
        raise RuntimeError("T6 is not at the required zero-outcome ABI boundary")
    policies = [
        Path(checkpoint["path"])
        for candidate in prereg["candidate_pairs"]
        for checkpoint in candidate["checkpoints"]
    ]
    abi_rows = [onnx_abi(path) for path in policies]
    expected_inputs = [
        {"name": "obs", "shape": [1, 115], "type": "tensor(float)"},
        {
            "name": "previous_action",
            "shape": [1, 14],
            "type": "tensor(float)",
        },
        {"name": "h_in", "shape": [1, 64], "type": "tensor(float)"},
    ]
    expected_outputs = [
        {
            "name": "continuous_actions",
            "shape": [1, 14],
            "type": "tensor(float)",
        },
        {
            "name": "previous_action_out",
            "shape": [1, 14],
            "type": "tensor(float)",
        },
        {"name": "h_out", "shape": [1, 64], "type": "tensor(float)"},
    ]
    if not all(
        row["inputs"] == expected_inputs and row["outputs"] == expected_outputs
        for row in abi_rows
    ):
        raise RuntimeError("T6 policies do not share the corrected recurrent ABI")
    payload = {
        "schema_version": "open_duck.t6_recurrent_abi_amendment.v1",
        "status": "PREREGISTERED_T6_PREOUTCOME_RECURRENT_ABI_CORRECTION",
        "original_preregistration": {
            "path": str(PREREG.resolve()),
            "file_sha256": sha256(PREREG),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "runner_sha256": prereg["repository_inputs"]["runner"]["sha256"],
        },
        "preoutcome_evidence": {
            "result_exists": False,
            "completed_block_manifests": 0,
            "behavior_cells_with_decision_weight": 0,
            "failed_log_path": str(failed_log),
            "failed_log_sha256": sha256(failed_log),
            "failure": (
                "ONNX Runtime rejected the first inference before a behavior "
                "cell because h_in was absent"
            ),
        },
        "onnx_abi": {
            "policies_verified": len(abi_rows),
            "expected_inputs": expected_inputs,
            "expected_outputs": expected_outputs,
            "policies": abi_rows,
        },
        "authorized_change": {
            "old_state_inputs": ["previous_action"],
            "new_state_inputs": ["previous_action", "h_in"],
            "old_state_outputs": ["previous_action_out"],
            "new_state_outputs": ["previous_action_out", "h_out"],
            "initialization": (
                "the frozen evaluator initializes all declared recurrent "
                "states to zeros and feeds each named output to its paired "
                "input on the next tick"
            ),
        },
        "corrected_runner_sha256": sha256(RUNNER),
        "unchanged_contract": {
            "candidate_pairs": True,
            "policies_and_hashes": True,
            "condition": True,
            "matrix": True,
            "behavior_gates": True,
            "protection_gates": True,
            "selection_rule": True,
            "authority": True,
            "training_steps": 0,
        },
        "authority": {
            "resume_exact_t6_screen": True,
            "policy_or_simulator_change": False,
            "hosted_compute_or_training": False,
            "robot_rdkx5_gate5_torque_motion": False,
        },
    }
    basis = {
        key: payload[key]
        for key in (
            "original_preregistration",
            "preoutcome_evidence",
            "onnx_abi",
            "authorized_change",
            "corrected_runner_sha256",
            "unchanged_contract",
        )
    }
    payload["amendment_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T6 recurrent-ABI pre-outcome amendment\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Contract SHA-256: `{payload['amendment_contract_sha256']}`\n"
        "- Evidence boundary: `0` completed blocks, `0` behavior cells, no "
        "result artifact.\n"
        "- Failure: first inference rejected missing `h_in`; no policy output "
        "or behavior outcome was produced.\n"
        "- Correction: state inputs `previous_action,h_in`; state outputs "
        "`previous_action_out,h_out`.\n"
        "- All eight frozen ONNX files expose exact `[1,115]`, `[1,14]`, and "
        "`[1,64]` input/state shapes.\n"
        "- Candidate population, policies, dynamics condition, matrix, gates, "
        "selection rule, and authority are unchanged.\n"
        "- No training, hosted compute, robot access, Gate 5, torque, or "
        "motion is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"CONTRACT_SHA256={payload['amendment_contract_sha256']}")
    print(f"FILE_SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
