#!/usr/bin/env python3
"""CPU-only hash, ABI, state-chain, deadband, and golden-vector verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import onnx
from onnx import TensorProto, numpy_helper
import onnxruntime as ort


EXPECTED_POLICIES = {
    "policies/T2_EQUAL_512000.onnx": (
        "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
    ),
    "policies/T2_EQUAL_1024000.onnx": (
        "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece"
    ),
}
EXPECTED_INPUTS = [
    ("obs", [1, 115], "tensor(float)"),
    ("previous_action", [1, 14], "tensor(float)"),
]
EXPECTED_OUTPUTS = [
    ("continuous_actions", [1, 14], "tensor(float)"),
    ("previous_action_out", [1, 14], "tensor(float)"),
]
TOLERANCE = 1.0e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_run(
    session: ort.InferenceSession, obs: np.ndarray, state: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    obs = np.asarray(obs, dtype=np.float32)
    state = np.asarray(state, dtype=np.float32)
    if obs.shape != (1, 115) or state.shape != (1, 14):
        raise ValueError(f"bad input shape: {obs.shape}/{state.shape}")
    if not np.all(np.isfinite(obs)) or not np.all(np.isfinite(state)):
        raise ValueError("nonfinite ONNX input rejected")
    action, next_state = session.run(
        ["continuous_actions", "previous_action_out"],
        {"obs": obs, "previous_action": state},
    )
    action = np.asarray(action, dtype=np.float32)
    next_state = np.asarray(next_state, dtype=np.float32)
    if action.shape != (1, 14) or next_state.shape != (1, 14):
        raise ValueError(f"bad output shape: {action.shape}/{next_state.shape}")
    if not np.all(np.isfinite(action)) or not np.all(np.isfinite(next_state)):
        raise ValueError("nonfinite ONNX output rejected")
    return action, next_state


def io_tuple(values: list[Any]) -> list[tuple[str, list[Any], str]]:
    return [(item.name, list(item.shape), item.type) for item in values]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-root", type=Path, default=Path(__file__).resolve().parent
    )
    args = parser.parse_args()
    root = args.artifact_root.resolve()
    failures: list[str] = []
    checks: dict[str, bool] = {}

    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    hash_failures = []
    for item in manifest["files"]:
        path = root / item["path"]
        if not path.is_file():
            hash_failures.append(f"missing:{item['path']}")
            continue
        actual = sha256(path)
        if actual != item["sha256"] or path.stat().st_size != item["bytes"]:
            hash_failures.append(f"hash_or_size:{item['path']}")
    repo_root = root.parents[2]
    for item in manifest["external_source_artifacts"]:
        path = repo_root / item["path"]
        if not path.is_file():
            hash_failures.append(f"missing_external:{item['path']}")
            continue
        if sha256(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            hash_failures.append(f"external_hash_or_size:{item['path']}")
    checks["all_manifest_hashes_and_sizes_match"] = not hash_failures
    failures.extend(hash_failures)

    contract = json.loads((root / "policy_contract.json").read_text())
    checks["disposition_requires_reviewed_115_v2"] = (
        contract["disposition"] == "REQUIRES_REVIEWED_115_RUNTIME_V2"
    )
    checks["no_posthoc_single_checkpoint_selection"] = (
        contract["selected_onnx_sha256"] == "NOT_READY"
        and contract["single_selected_deployment_checkpoint"] is None
    )
    checks["robot_clearance_false"] = contract["authority"]["robot_clearance"] is False

    policy_results = []
    for relative, expected_hash in EXPECTED_POLICIES.items():
        policy = root / relative
        model = onnx.load(str(policy))
        opsets = {(item.domain, int(item.version)) for item in model.opset_import}
        weights = {item.name: numpy_helper.to_array(item) for item in model.graph.initializer}
        session = ort.InferenceSession(
            str(policy), providers=["CPUExecutionProvider"]
        )
        inputs = io_tuple(session.get_inputs())
        outputs = io_tuple(session.get_outputs())
        local_failures = []
        if sha256(policy) != expected_hash:
            local_failures.append("policy_hash")
        if session.get_providers() != ["CPUExecutionProvider"]:
            local_failures.append("provider")
        if inputs != EXPECTED_INPUTS:
            local_failures.append("inputs")
        if outputs != EXPECTED_OUTPUTS:
            local_failures.append("outputs")
        if int(model.ir_version) != 10 or opsets != {("", 12)}:
            local_failures.append("onnx_version")
        if len(model.graph.node) != 40 or len(model.graph.initializer) != 24:
            local_failures.append("graph_shape")
        for required in [
            "obs_mean", "obs_std", "max_action_delta", "guard_margin",
            "deadband_abs_limit", "deadband_zero_action",
        ]:
            if required not in weights:
                local_failures.append(f"initializer:{required}")
        if weights.get("max_action_delta", np.zeros((1, 14))).shape != (1, 14):
            local_failures.append("max_action_delta_shape")
        elif float(weights["max_action_delta"][0, 4]) != 0.11999999731779099:
            local_failures.append("left_ankle_repair")
        if float(weights.get("deadband_abs_limit", [np.nan])[0]) != 0.009999999776482582:
            local_failures.append("deadband_threshold")

        step = int(policy.stem.rsplit("_", 1)[1])
        max_action_error = 0.0
        max_state_error = 0.0
        max_chain_error = 0.0
        for command in [0.0, 0.08]:
            pack_path = root / "golden" / f"T2_EQUAL_{step}_x{command:.3f}.npz"
            with np.load(pack_path) as pack:
                state = np.zeros((1, 14), dtype=np.float32)
                for tick in range(5):
                    expected_in = pack["previous_action_in"][tick][None]
                    max_chain_error = max(
                        max_chain_error,
                        float(np.max(np.abs(state - expected_in))),
                    )
                    action, next_state = checked_run(
                        session, pack["obs"][tick][None], state
                    )
                    max_action_error = max(
                        max_action_error,
                        float(np.max(np.abs(action[0] - pack["final_action"][tick]))),
                    )
                    max_state_error = max(
                        max_state_error,
                        float(
                            np.max(
                                np.abs(
                                    next_state[0] - pack["previous_action_out"][tick]
                                )
                            )
                        ),
                    )
                    state = next_state.copy()
                if command == 0.0:
                    if np.any(pack["final_action"] != 0.0):
                        local_failures.append("x0_action_not_bit_exact_zero")
                    if np.any(pack["previous_action_out"] != 0.0):
                        local_failures.append("x0_state_not_bit_exact_zero")
                if np.any(pack["external_5p24_limiter_changed"]):
                    local_failures.append("external_5p24_not_identity")
        if max_action_error > TOLERANCE:
            local_failures.append("golden_action")
        if max_state_error > TOLERANCE:
            local_failures.append("golden_state")
        if max_chain_error > TOLERANCE:
            local_failures.append("golden_chain")

        nan_rejected = False
        try:
            bad = np.zeros((1, 115), dtype=np.float32)
            bad[0, 0] = np.nan
            checked_run(session, bad, np.zeros((1, 14), dtype=np.float32))
        except ValueError:
            nan_rejected = True
        if not nan_rejected:
            local_failures.append("nan_rejection")

        policy_results.append(
            {
                "policy": relative,
                "inputs": inputs,
                "outputs": outputs,
                "max_action_error": max_action_error,
                "max_state_error": max_state_error,
                "max_chain_error": max_chain_error,
                "nan_rejected": nan_rejected,
                "failures": local_failures,
            }
        )
        failures.extend(f"{relative}:{item}" for item in local_failures)

    for name, passed in checks.items():
        if not passed:
            failures.append(name)
    result = {
        "status": (
            "PASS_CPU_HANDOFF_INSPECTION_BLOCKED_FOR_RUNTIME_REVIEW"
            if not failures
            else "HOLD_CPU_HANDOFF_INSPECTION_FAILED"
        ),
        "artifact_root": str(root),
        "manifest_sha256": sha256(manifest_path),
        "execution_provider": "CPUExecutionProvider",
        "tolerance": TOLERANCE,
        "checks": checks,
        "policies": policy_results,
        "failures": failures,
        "authority": {
            "robot_clearance": False,
            "gate5": False,
            "runtime_deployment": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
