#!/usr/bin/env python3
"""Build context-ABI diagnostic wrappers for the T8 zero-training screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import t8_state_coherent_eval_adapter as adapter  # noqa: E402


DEFAULT_OUTPUT_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t8_state_coherent_handoff_assets_v2"
)
CONTEXT_NAME = "calibration_context"
CONTEXT_SHAPE = [1, 64]
PARITY_TICKS = 1024


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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def add_context_input(source: Path, destination: Path) -> None:
    import onnx
    from onnx import TensorProto, helper

    model = onnx.load(source)
    names = [item.name for item in model.graph.input]
    if names != ["obs", "previous_action", "h_in"]:
        raise RuntimeError(f"unexpected V121 source inputs: {names}")
    model.graph.input.append(
        helper.make_tensor_value_info(
            CONTEXT_NAME,
            TensorProto.FLOAT,
            CONTEXT_SHAPE,
        )
    )
    onnx.checker.check_model(model)
    onnx.save_model(model, destination)


def io_contract(session: Any) -> dict[str, Any]:
    return {
        "inputs": {item.name: item.shape for item in session.get_inputs()},
        "outputs": {item.name: item.shape for item in session.get_outputs()},
    }


def parity_contract(source: Path, wrapped: Path) -> dict[str, Any]:
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    source_session = ort.InferenceSession(
        str(source), sess_options=options, providers=["CPUExecutionProvider"]
    )
    wrapped_session = ort.InferenceSession(
        str(wrapped), sess_options=options, providers=["CPUExecutionProvider"]
    )
    source_io = io_contract(source_session)
    wrapped_io = io_contract(wrapped_session)
    expected_source_inputs = {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
    }
    expected_outputs = {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    }
    if source_io != {
        "inputs": expected_source_inputs,
        "outputs": expected_outputs,
    }:
        raise RuntimeError(f"V121 source ABI changed: {source_io}")
    if wrapped_io != {
        "inputs": {**expected_source_inputs, CONTEXT_NAME: CONTEXT_SHAPE},
        "outputs": expected_outputs,
    }:
        raise RuntimeError(f"T8 wrapper ABI changed: {wrapped_io}")

    rng = np.random.Generator(np.random.PCG64(803842))
    source_previous = np.zeros((1, 14), dtype=np.float32)
    source_hidden = np.zeros((1, 64), dtype=np.float32)
    wrapped_previous = source_previous.copy()
    wrapped_hidden = source_hidden.copy()
    maximum_errors = {
        "continuous_actions": 0.0,
        "previous_action_out": 0.0,
        "h_out": 0.0,
    }
    all_bit_exact = True
    zero_command_actions_exact_zero = True
    for tick in range(PARITY_TICKS):
        observation = rng.normal(0.0, 0.35, size=(1, 115)).astype(np.float32)
        if tick % 4 == 0:
            observation[:, 6:13] = 0.0
            observation[:, 99:101] = np.asarray([1.0, 0.0], dtype=np.float32)
            observation[:, 101:115] = 0.0
        context = rng.normal(0.0, 1.0, size=(1, 64)).astype(np.float32)
        source_outputs = source_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": source_previous,
                "h_in": source_hidden,
            },
        )
        wrapped_outputs = wrapped_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": wrapped_previous,
                "h_in": wrapped_hidden,
                CONTEXT_NAME: context,
            },
        )
        for name, left, right in zip(
            maximum_errors, source_outputs, wrapped_outputs, strict=True
        ):
            maximum_errors[name] = max(
                maximum_errors[name],
                float(np.max(np.abs(left.astype(float) - right.astype(float)))),
            )
            all_bit_exact &= np.array_equal(left, right)
        if tick % 4 == 0:
            zero_command_actions_exact_zero &= (
                np.count_nonzero(source_outputs[0]) == 0
            )
        source_previous = np.asarray(source_outputs[1], dtype=np.float32)
        source_hidden = np.asarray(source_outputs[2], dtype=np.float32)
        wrapped_previous = np.asarray(wrapped_outputs[1], dtype=np.float32)
        wrapped_hidden = np.asarray(wrapped_outputs[2], dtype=np.float32)
    return {
        "ticks": PARITY_TICKS,
        "source_io": source_io,
        "wrapped_io": wrapped_io,
        "all_outputs_bit_exact": bool(all_bit_exact),
        "maximum_abs_errors": maximum_errors,
        "zero_command_actions_exact_zero": bool(
            zero_command_actions_exact_zero
        ),
        "context_is_diagnostic_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T8 asset creation requires --execute")
    output_root = args.output_root.resolve()
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite T8 assets: {output_root}")
    policies_root = output_root / "policies"
    policies_root.mkdir(parents=True)

    t6 = json.loads(
        (ANALYSIS / "t6_corrected_robustness_screen_preregistration.json").read_text(
            encoding="utf-8"
        )
    )
    candidate = next(
        item for item in t6["candidate_pairs"] if item["candidate_id"] == "V121"
    )
    policies = []
    for checkpoint in candidate["checkpoints"]:
        source = Path(checkpoint["path"])
        if sha256(source) != checkpoint["sha256"]:
            raise RuntimeError(f"V121 source policy changed: {source}")
        destination = policies_root / f"{source.stem}_T8_CONTEXT_ABI.onnx"
        add_context_input(source, destination)
        parity = parity_contract(source, destination)
        if (
            not parity["all_outputs_bit_exact"]
            or not parity["zero_command_actions_exact_zero"]
            or any(value != 0.0 for value in parity["maximum_abs_errors"].values())
        ):
            raise RuntimeError(f"T8 wrapper parity failed: {checkpoint['checkpoint_id']}")
        policies.append(
            {
                "checkpoint_id": checkpoint["checkpoint_id"],
                "source": receipt(source),
                "wrapped": receipt(destination),
                "parity": parity,
            }
        )
    basis = {
        "schema_version": "open_duck.t8_state_coherent_handoff_assets.v1",
        "source_candidate": "V121",
        "policies": policies,
        "adapter": adapter.contract(),
        "context_contract": {
            "name": CONTEXT_NAME,
            "shape": CONTEXT_SHAPE,
            "use": "required ABI input but ignored by the diagnostic wrappers",
            "why": (
                "T8 tests physical/state handoff feasibility before any "
                "response-conditioned actor continuation"
            ),
        },
        "execution": {
            "optimizer_updates": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    manifest = {**basis, "manifest_sha256": canonical_sha256(basis)}
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("PASS_T8_STATE_COHERENT_HANDOFF_ASSETS")
    print(f"manifest={manifest_path}")
    print(f"manifest_sha256={manifest['manifest_sha256']}")
    print(f"file_sha256={sha256(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
