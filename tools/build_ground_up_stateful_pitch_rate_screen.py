#!/usr/bin/env python3
"""Build and verify preregistered stateful pitch-rate ONNX variants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_source(text: str) -> tuple[str, Path]:
    label, separator, path = text.partition("=")
    if not separator or not label or not path:
        raise argparse.ArgumentTypeError("source must be LABEL=PATH")
    return label, Path(path)


def tensor_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: numpy_helper.to_array(item).copy() for item in model.graph.initializer}


def inspect_chain(path: Path, expected_delta: np.ndarray) -> dict:
    onnx.checker.check_model(onnx.load(path))
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inputs = [item.name for item in session.get_inputs()]
    outputs = [item.name for item in session.get_outputs()]
    obs_size = session.get_inputs()[0].shape[-1]
    obs = np.zeros((1, obs_size), dtype=np.float32)
    previous = np.zeros((1, 14), dtype=np.float32)
    excess = []
    state_errors = []
    finite = True
    for tick in range(8):
        obs[:, -14:] = 0.9 if tick % 2 == 0 else -0.9
        action, state = session.run(
            outputs, {"obs": obs, "previous_action": previous}
        )
        finite &= bool(np.all(np.isfinite(action)))
        excess.append(float(np.max(np.abs(action - previous) - expected_delta)))
        state_errors.append(float(np.max(np.abs(state - action))))
        previous = state
    return {
        "inputs": inputs,
        "outputs": outputs,
        "max_bound_excess": max(excess),
        "max_state_output_error": max(state_errors),
        "checks": {
            "interface_exact": inputs == ["obs", "previous_action"]
            and outputs == ["continuous_actions", "previous_action_out"],
            "actions_finite": finite,
            "eight_tick_bound_excess_at_most_1e_6": max(excess) <= 1.0e-6,
            "state_output_exact": max(state_errors) <= 1.0e-7,
        },
    }


def build(source: Path, destination: Path, multiplier: float) -> dict:
    model = onnx.load(source)
    original = tensor_map(model)
    if "max_action_delta" not in original:
        raise ValueError(f"{source} has no max_action_delta initializer")
    original_delta = original["max_action_delta"]
    if original_delta.shape != (1, 14):
        raise ValueError(f"unexpected max_action_delta shape: {original_delta.shape}")
    expected = original_delta.copy()
    expected[:, PITCH_INDICES] *= multiplier
    for index, initializer in enumerate(model.graph.initializer):
        if initializer.name == "max_action_delta":
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(expected.astype(np.float32), name="max_action_delta")
            )
            break
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    rebuilt = onnx.load(destination)
    transformed = tensor_map(rebuilt)
    non_delta_exact = all(
        np.array_equal(value, transformed[name])
        for name, value in original.items()
        if name != "max_action_delta"
    )
    non_pitch_exact = np.array_equal(
        original_delta[:, np.setdiff1d(np.arange(14), PITCH_INDICES)],
        transformed["max_action_delta"][:, np.setdiff1d(np.arange(14), PITCH_INDICES)],
    )
    pitch_error = float(
        np.max(
            np.abs(
                transformed["max_action_delta"][:, PITCH_INDICES]
                - expected[:, PITCH_INDICES]
            )
        )
    )
    graph_contract = {
        "nodes_exact": [node.SerializeToString() for node in model.graph.node]
        == [node.SerializeToString() for node in rebuilt.graph.node],
        "inputs_exact": [item.SerializeToString() for item in model.graph.input]
        == [item.SerializeToString() for item in rebuilt.graph.input],
        "outputs_exact": [item.SerializeToString() for item in model.graph.output]
        == [item.SerializeToString() for item in rebuilt.graph.output],
        "non_delta_initializers_exact": non_delta_exact,
        "non_pitch_delta_values_exact": non_pitch_exact,
        "pitch_delta_max_error_at_most_1e_8": pitch_error <= 1.0e-8,
    }
    chain = inspect_chain(destination, expected)
    return {
        "source": str(source.resolve()),
        "source_sha256": sha256(source),
        "output": str(destination.resolve()),
        "output_sha256": sha256(destination),
        "multiplier": multiplier,
        "original_max_action_delta": original_delta[0].tolist(),
        "transformed_max_action_delta": expected[0].tolist(),
        "graph_checks": graph_contract,
        "chain": chain,
        "passed": all(graph_contract.values()) and all(chain["checks"].values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=parse_source, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    sources = dict(args.source)
    variants = []
    for arm in prereg["arms"]:
        for label, source in sources.items():
            output = args.output_dir / arm["name"] / f"{label}.onnx"
            variants.append(build(source.resolve(), output, arm["multiplier"]))
    checks = {
        "twelve_variants_built": len(variants) == 12,
        "all_variants_pass_transform_contract": all(item["passed"] for item in variants),
        "all_sources_immutable": all(Path(item["source"]).is_file() for item in variants),
        "preregistered_pitch_indices_exact": prereg["pitch_chain_indices"]
        == PITCH_INDICES.tolist(),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_STATEFUL_PITCH_RATE_TRANSFORM_CONTRACT" if not failed else "FAIL_STATEFUL_PITCH_RATE_TRANSFORM_CONTRACT"
    payload = {
        "schema_version": "ground_up_stateful_pitch_rate_transform_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "preregistration": str(args.preregistration.resolve()),
        "preregistration_sha256": sha256(args.preregistration),
        "variants": variants,
        "execution": {
            "onnxruntime_providers": ort.get_available_providers(),
            "local_gpu_access": False,
            "training": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(
        "\n".join(
            [
                "# Ground-Up Stateful Pitch-Rate Transform Contract",
                "",
                f"status: `{status}`",
                f"failed checks: `{', '.join(failed) if failed else 'none'}`",
                f"variants built: `{len(variants)}`",
                f"maximum chain bound excess: `{max(item['chain']['max_bound_excess'] for item in variants)}`",
                f"maximum state-output error: `{max(item['chain']['max_state_output_error'] for item in variants)}`",
                "",
                "Only the six preregistered pitch-chain `max_action_delta` values change. "
                "This contract authorizes CPU behavior evaluation only.",
                "",
            ]
        )
    )
    print(json.dumps({"status": status, "failed": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
