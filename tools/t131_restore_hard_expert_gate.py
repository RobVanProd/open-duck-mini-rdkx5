#!/usr/bin/env python3
"""Restore the frozen hard negative-COM gate to an always-on expert graph."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import onnx
from onnx import helper, numpy_helper


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initializer_map(model: onnx.ModelProto) -> dict[str, str]:
    return {
        item.name: hashlib.sha256(
            numpy_helper.to_array(item).tobytes()
        ).hexdigest()
        for item in model.graph.initializer
    }


def graph_abi(model: onnx.ModelProto) -> tuple[str, ...]:
    return tuple(
        f"{kind}:{item.name}:{item.type.tensor_type.elem_type}:"
        f"{','.join(str(dim.dim_value) for dim in item.type.tensor_type.shape.dim)}"
        for kind, items in (
            ("input", model.graph.input),
            ("output", model.graph.output),
        )
        for item in items
    )


def restore_hard_gate(
    source: Path,
    output: Path,
    *,
    reference: Path | None = None,
) -> dict[str, Any]:
    """Replace exactly one always-on Identity with the frozen hard Where."""
    model = onnx.load(source)
    original = copy.deepcopy(model)
    indices = [
        index
        for index, node in enumerate(model.graph.node)
        if node.op_type == "Identity"
        and list(node.input) == ["negative_adapter_location"]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(indices) != 1:
        raise RuntimeError(f"T131 always-on topology changed: {indices}")
    index = indices[0]
    model.graph.node[index].CopyFrom(
        helper.make_node(
            "Where",
            [
                "negative_com_gate",
                "negative_adapter_location",
                "zero_adapter_location",
            ],
            ["conditional_adapter_location"],
        )
    )
    onnx.checker.check_model(model)
    output.parent.mkdir(parents=True, exist_ok=False)
    onnx.save(model, output)
    reloaded = onnx.load(output)
    gate_consumers = [
        node
        for node in reloaded.graph.node
        if "negative_com_gate" in node.input
    ]
    value = {
        "source": {
            "path": str(source.resolve()),
            "bytes": source.stat().st_size,
            "sha256": sha256(source),
        },
        "output": {
            "path": str(output.resolve()),
            "bytes": output.stat().st_size,
            "sha256": sha256(output),
        },
        "node_index": index,
        "node_count_exact": len(original.graph.node)
        == len(reloaded.graph.node),
        "abi_exact": graph_abi(original) == graph_abi(reloaded),
        "initializers_exact": initializer_map(original)
        == initializer_map(reloaded),
        "replacement_exact": (
            reloaded.graph.node[index].op_type == "Where"
            and list(reloaded.graph.node[index].input)
            == [
                "negative_com_gate",
                "negative_adapter_location",
                "zero_adapter_location",
            ]
            and list(reloaded.graph.node[index].output)
            == ["conditional_adapter_location"]
        ),
        "negative_gate_consumer_count": len(gate_consumers),
        "reference": None,
    }
    if reference is not None:
        value["reference"] = {
            "path": str(reference.resolve()),
            "bytes": reference.stat().st_size,
            "sha256": sha256(reference),
            "byte_exact": output.read_bytes() == reference.read_bytes(),
        }
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    value = restore_hard_gate(
        args.source.resolve(),
        args.output.resolve(),
        reference=args.reference.resolve() if args.reference else None,
    )
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
