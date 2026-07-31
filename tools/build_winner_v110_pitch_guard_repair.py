#!/usr/bin/env python3
"""Apply the frozen G3 full-tick pitch guard to the recurrent checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT_JSON = ANALYSIS / "winner_v110_pitch_guard_transform_contract.json"
CONTRACT_MD = ANALYSIS / "WINNER_V110_PITCH_GUARD_TRANSFORM_CONTRACT_20260724.md"
SOURCE_POLICIES = (
    {
        "id": "R64_RECURRENT_HALF",
        "step": 1_003_520,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_1003520.onnx",
        "sha256": "c8e03dd4afed4e7a96507e5089116944a048ac1d682210408a68cca1b8b6af7c",
    },
    {
        "id": "R64_RECURRENT_FINAL",
        "step": 2_007_040,
        "filename": "R64_ZERO_INIT_RECURRENT_ADAPTER_2007040.onnx",
        "sha256": "dfdd01bf4563e3d377ffcbe70515681e75a0d87797f3b6b9e4486d1b40ad569c",
    },
)
PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13], dtype=np.int64)
SOURCE_MARGIN_RAD = np.float32(0.20)
REPAIRED_MARGIN_RAD = np.float32(0.165)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        value.name: numpy_helper.to_array(value).copy()
        for value in model.graph.initializer
    }


def replace_initializer(
    model: onnx.ModelProto, name: str, value: np.ndarray
) -> None:
    for initializer in model.graph.initializer:
        if initializer.name == name:
            initializer.CopyFrom(numpy_helper.from_array(value, name=name))
            return
    raise KeyError(name)


def repair_model(source_path: Path, output_path: Path) -> dict[str, Any]:
    source = onnx.load(source_path)
    repaired = onnx.ModelProto()
    repaired.CopyFrom(source)
    source_tensors = tensor_map(source)
    margin = source_tensors["guard_margin"]
    pitch_mask = source_tensors["guard_pitch_mask"].reshape(-1)
    expected_margin = np.full((1, 14), np.float32(1.0e6), dtype=np.float32)
    expected_margin.reshape(-1)[PITCH_INDICES] = SOURCE_MARGIN_RAD
    if margin.dtype != np.float32 or not np.array_equal(
        margin, expected_margin
    ):
        raise ValueError("source guard_margin is not the selected G1 contract")
    if not np.array_equal(
        np.flatnonzero(pitch_mask), PITCH_INDICES
    ):
        raise ValueError("source pitch mask changed")

    repaired_margin = margin.copy()
    repaired_margin.reshape(-1)[PITCH_INDICES] = REPAIRED_MARGIN_RAD
    replace_initializer(repaired, "guard_margin", repaired_margin)
    onnx.checker.check_model(repaired)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(repaired, output_path)
    observed = onnx.load(output_path)
    observed_tensors = tensor_map(observed)

    changed_initializers = sorted(
        name
        for name in source_tensors
        if not np.array_equal(source_tensors[name], observed_tensors[name])
    )
    graph_checks = {
        "graph_inputs_exact": [
            value.SerializeToString() for value in source.graph.input
        ]
        == [value.SerializeToString() for value in observed.graph.input],
        "graph_outputs_exact": [
            value.SerializeToString() for value in source.graph.output
        ]
        == [value.SerializeToString() for value in observed.graph.output],
        "nodes_bit_exact": [
            value.SerializeToString() for value in source.graph.node
        ]
        == [value.SerializeToString() for value in observed.graph.node],
        "initializer_names_exact": list(source_tensors)
        == list(observed_tensors),
        "only_guard_margin_changed": changed_initializers
        == ["guard_margin"],
        "source_margin_exact": np.array_equal(margin, expected_margin),
        "repaired_margin_exact": np.array_equal(
            observed_tensors["guard_margin"], repaired_margin
        ),
        "all_nonmargin_initializers_bit_exact": all(
            np.array_equal(source_tensors[name], observed_tensors[name])
            for name in source_tensors
            if name != "guard_margin"
        ),
    }

    source_session = ort.InferenceSession(
        str(source_path), providers=["CPUExecutionProvider"]
    )
    repaired_session = ort.InferenceSession(
        str(output_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260724)
    max_h_error = 0.0
    max_zero_action_error = 0.0
    max_zero_state_error = 0.0
    max_pitch_guard_excess = 0.0
    state_feedback_exact = True
    finite = True
    for index in range(256):
        obs = rng.normal(0.0, 0.35, (1, 115)).astype(np.float32)
        obs[:, 6] = np.float32(0.0 if index < 128 else 0.077)
        obs[:, source_tensors["guard_joint_obs_indices"]] = rng.uniform(
            -0.05, 0.05, (1, 14)
        ).astype(np.float32)
        previous_action = rng.uniform(-0.8, 0.8, (1, 14)).astype(
            np.float32
        )
        h_in = rng.normal(0.0, 0.2, (1, 64)).astype(np.float32)
        inputs = {
            "obs": obs,
            "previous_action": previous_action,
            "h_in": h_in,
        }
        source_outputs = source_session.run(None, inputs)
        repaired_outputs = repaired_session.run(None, inputs)
        finite &= all(np.all(np.isfinite(value)) for value in repaired_outputs)
        max_h_error = max(
            max_h_error,
            float(np.max(np.abs(source_outputs[2] - repaired_outputs[2]))),
        )
        state_feedback_exact &= np.array_equal(
            repaired_outputs[0], repaired_outputs[1]
        )
        if index < 128:
            max_zero_action_error = max(
                max_zero_action_error,
                float(
                    np.max(
                        np.abs(source_outputs[0] - repaired_outputs[0])
                    )
                ),
            )
            max_zero_state_error = max(
                max_zero_state_error,
                float(
                    np.max(
                        np.abs(source_outputs[1] - repaired_outputs[1])
                    )
                ),
            )
        if index >= 128:
            actual = source_tensors["guard_home"] + obs[
                :, source_tensors["guard_joint_obs_indices"]
            ]
            target = (
                source_tensors["guard_home"]
                + repaired_outputs[0]
                * source_tensors["guard_action_scale"]
            )
            max_pitch_guard_excess = max(
                max_pitch_guard_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(
                                target[:, PITCH_INDICES]
                                - actual[:, PITCH_INDICES]
                            )
                            - REPAIRED_MARGIN_RAD,
                            0.0,
                        )
                    )
                ),
            )
    runtime_checks = {
        "cpu_provider_exact": repaired_session.get_providers()
        == ["CPUExecutionProvider"],
        "all_256_outputs_finite": bool(finite),
        "h_out_bit_exact_all_cases": max_h_error == 0.0,
        "x0_action_bit_exact_128_cases": max_zero_action_error == 0.0,
        "x0_previous_action_bit_exact_128_cases": max_zero_state_error == 0.0,
        "previous_action_out_equals_action_all_cases": bool(
            state_feedback_exact
        ),
        "pitch_target_within_g3_margin_all_cases": (
            max_pitch_guard_excess <= 1.0e-7
        ),
    }
    return {
        "id": next(
            row["id"]
            for row in SOURCE_POLICIES
            if row["filename"] == source_path.name
        ),
        "step": next(
            row["step"]
            for row in SOURCE_POLICIES
            if row["filename"] == source_path.name
        ),
        "source_path": str(source_path),
        "source_sha256": sha256(source_path),
        "output_path": str(output_path),
        "output_sha256": sha256(output_path),
        "output_bytes": output_path.stat().st_size,
        "changed_initializers": changed_initializers,
        "graph_checks": graph_checks,
        "runtime_checks": runtime_checks,
        "numeric_audit": {
            "max_h_out_abs_error": max_h_error,
            "max_x0_action_abs_error": max_zero_action_error,
            "max_x0_previous_action_abs_error": max_zero_state_error,
            "max_pitch_guard_excess_rad": max_pitch_guard_excess,
        },
        "pass": all(graph_checks.values()) and all(runtime_checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=CONTRACT_JSON)
    parser.add_argument("--markdown", type=Path, default=CONTRACT_MD)
    args = parser.parse_args()
    for path in (args.output_root, args.contract, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite: {path}")

    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    policies = []
    for spec in SOURCE_POLICIES:
        source_path = source_root / spec["filename"]
        if sha256(source_path) != spec["sha256"]:
            raise ValueError(f"source hash changed: {spec['id']}")
        policies.append(
            repair_model(source_path, output_root / spec["filename"])
        )
    checks = {
        "two_policies_transformed": len(policies) == 2,
        "all_source_hashes_exact": all(
            row["source_sha256"] == spec["sha256"]
            for row, spec in zip(policies, SOURCE_POLICIES, strict=True)
        ),
        "all_policy_contracts_pass": all(row["pass"] for row in policies),
        "output_hashes_distinct_from_sources": all(
            row["output_sha256"] != row["source_sha256"] for row in policies
        ),
        "output_hashes_distinct_by_checkpoint": (
            len({row["output_sha256"] for row in policies}) == 2
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    contract = {
        "schema_version": "winner_v110.pitch_guard_transform_contract.v1",
        "status": (
            "PASS_WINNER_V110_PITCH_GUARD_TRANSFORM_CONTRACT"
            if not failed
            else "HOLD_WINNER_V110_PITCH_GUARD_TRANSFORM_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "repair": {
            "source_guard": "G1_EXACT_BOUNDARY",
            "source_margin_rad": float(SOURCE_MARGIN_RAD),
            "repaired_guard": "G3_FULL_TICK_BUFFER",
            "repaired_margin_rad": float(REPAIRED_MARGIN_RAD),
            "pitch_action_indices": PITCH_INDICES.tolist(),
            "changed_initializer": "guard_margin",
            "rationale": (
                "G3 is the already-preregistered one-full-tick buffer and "
                "previously preserved persistent gait. Winner-v109 isolated "
                "all 12 moving failures to peak current on the left knee and "
                "left ankle while every noncurrent behavior metric passed."
            ),
        },
        "policies": policies,
        "authority": {
            "cpu_transform_and_contract": not failed,
            "behavior_evaluation": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.contract.write_text(
        json.dumps(contract, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v110 G3 pitch-guard transform contract\n\n"
        f"Status: `{contract['status']}`\n\n"
        "This transform changes only the six pitch-chain entries of the "
        "existing `guard_margin` initializer from the selected G1 0.20-rad "
        "boundary to the already-preregistered G3 0.165-rad full-tick buffer. "
        "The graph, recurrent state, non-guard initializers, x=0 behavior, ABI, "
        "and state feedback remain exact. No behavior result, training, Gate 5, "
        "robot, torque, or motion is authorized by this contract.\n",
        encoding="utf-8",
    )
    print(contract["status"])
    for row in policies:
        print(f"{row['id']}={row['output_sha256']}")
    print(f"contract_sha256={sha256(args.contract)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
