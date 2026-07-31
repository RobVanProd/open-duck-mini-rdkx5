#!/usr/bin/env python3
"""Build the single evidence-derived T181 head interpolation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t181_count_weighted_head_interpolation_preregistration.json"
)
RESULT = ANALYSIS / "t181_count_weighted_head_interpolation_result.json"
MARKDOWN = (
    ANALYSIS / "T181_COUNT_WEIGHTED_HEAD_INTERPOLATION_RESULT_20260730.md"
)
WORK = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t181_count_weighted_head_interpolation_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t172_t170_postexport_composition import inference_contract  # noqa: E402
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
    verify_receipt,
)


class T181Error(RuntimeError):
    """The frozen T181 graph contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T181Error(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def replace(model: onnx.ModelProto, name: str, value: np.ndarray) -> None:
    for index, item in enumerate(model.graph.initializer):
        if item.name == name:
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(value, name=name)
            )
            return
    raise KeyError(name)


def interpolate(
    source: np.ndarray,
    transformed: np.ndarray,
    alpha: float,
) -> np.ndarray:
    return (
        source.astype(np.float64)
        + float(alpha)
        * (transformed.astype(np.float64) - source.astype(np.float64))
    ).astype(np.float32)


def build_graph(
    source_path: Path,
    transformed_path: Path,
    destination: Path,
    *,
    head_initializers: list[str],
    alpha: float,
) -> dict[str, Any]:
    source_model = onnx.load(source_path)
    transformed_model = onnx.load(transformed_path)
    source_values = arrays(source_model)
    transformed_values = arrays(transformed_model)
    _require(
        set(source_values) == set(transformed_values),
        "source/transformed initializer names differ",
    )
    expected = {
        name: interpolate(source_values[name], transformed_values[name], alpha)
        for name in head_initializers
    }
    for name, value in expected.items():
        replace(source_model, name, value)
    onnx.checker.check_model(source_model)
    destination.parent.mkdir(parents=True, exist_ok=False)
    onnx.save(source_model, destination)
    actual = arrays(source_model)
    changed = sorted(
        name
        for name in source_values
        if not np.array_equal(source_values[name], actual[name])
    )
    return {
        "source": receipt(source_path),
        "transformed_endpoint": receipt(transformed_path),
        "candidate": receipt(destination),
        "alpha": float(alpha),
        "changed_initializers": changed,
        "head_arithmetic_exact": all(
            np.array_equal(actual[name], expected[name])
            for name in head_initializers
        ),
        "all_other_initializers_source_exact": all(
            np.array_equal(actual[name], source_values[name])
            for name in source_values
            if name not in head_initializers
        ),
        "initializer_names_exact": set(actual) == set(source_values),
        "nodes_source_byte_exact": all(
            left.SerializeToString() == right.SerializeToString()
            for left, right in zip(
                onnx.load(source_path).graph.node,
                source_model.graph.node,
                strict=True,
            )
        ),
        "all_initializers_finite": all(
            np.all(np.isfinite(value)) for value in actual.values()
        ),
    }


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
    work_root: Path = WORK,
) -> dict[str, Any]:
    _require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    _require(not markdown_path.exists(), f"refusing to overwrite: {markdown_path}")
    _require(not work_root.exists(), f"refusing to overwrite: {work_root}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T181 execution requires committed clean preregistration",
    )
    prereg = _load_json(preregistration_path)
    _require(
        prereg.get("status")
        == "PREREGISTERED_T181_COUNT_WEIGHTED_HEAD_INTERPOLATION",
        "unexpected T181 preregistration status",
    )
    _require(
        _canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T181 preregistration hash differs",
    )
    for label, item in prereg["frozen_inputs"].items():
        verify_receipt(item, label)
    for pair in prereg["graph_pairs"]:
        verify_receipt(pair["source"], f"{pair['checkpoint_id']}:source")
        verify_receipt(
            pair["transformed_endpoint"],
            f"{pair['checkpoint_id']}:transformed",
        )
    alpha = float(prereg["interpolation"]["alpha"])
    outputs = []
    started = time.time()
    for index, pair in enumerate(prereg["graph_pairs"]):
        destination = (
            work_root / pair["checkpoint_id"] / "count_weighted_alpha_0p2.onnx"
        )
        structure = build_graph(
            Path(pair["source"]["path"]),
            Path(pair["transformed_endpoint"]["path"]),
            destination,
            head_initializers=prereg["interpolation"]["head_initializers"],
            alpha=alpha,
        )
        inference = inference_contract(
            destination,
            Path(pair["source"]["path"]),
            prereg["contexts"],
            int(prereg["inference_seed"]) + index,
        )
        outputs.append(
            {
                "checkpoint_id": pair["checkpoint_id"],
                "step": pair["step"],
                "structure": structure,
                "inference": inference,
            }
        )
    expected_head = sorted(prereg["interpolation"]["head_initializers"])
    checks = {
        "two_candidate_graphs": len(outputs) == 2,
        "alpha_exact": alpha == 0.2,
        "changed_initializers_head_only": all(
            item["structure"]["changed_initializers"] == expected_head
            for item in outputs
        ),
        "head_arithmetic_exact": all(
            item["structure"]["head_arithmetic_exact"] for item in outputs
        ),
        "other_initializers_source_exact": all(
            item["structure"]["all_other_initializers_source_exact"]
            for item in outputs
        ),
        "initializer_names_exact": all(
            item["structure"]["initializer_names_exact"] for item in outputs
        ),
        "nodes_source_byte_exact": all(
            item["structure"]["nodes_source_byte_exact"] for item in outputs
        ),
        "all_initializers_finite": all(
            item["structure"]["all_initializers_finite"] for item in outputs
        ),
        "all_outputs_finite": all(
            item["inference"]["all_outputs_finite"] for item in outputs
        ),
        "all_inactive_routes_bit_exact": all(
            item["inference"]["all_inactive_routes_bit_exact"]
            for item in outputs
        ),
        "all_x0_outputs_bit_exact": all(
            item["inference"]["all_x0_outputs_bit_exact"]
            for item in outputs
        ),
        "both_y_negative_contexts_route_nominal": all(
            item["inference"]["both_y_negative_contexts_route_nominal"]
            for item in outputs
        ),
        "cpu_only": all(
            item["inference"]["provider"] == "CPUExecutionProvider"
            for item in outputs
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t181_count_weighted_head_interpolation_result.v1"
        ),
        "status": (
            "PASS_T181_COUNT_WEIGHTED_HEAD_INTERPOLATION"
            if passed
            else "HOLD_T181_COUNT_WEIGHTED_HEAD_INTERPOLATION"
        ),
        "decision": (
            "EARN_T182_SHARED_FAILURE_SINGLE_CELL_PREREGISTRATION_ONLY"
            if passed
            else "CLOSE_COUNT_WEIGHTED_HEAD_INTERPOLATION_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "alpha": alpha,
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "inference_samples": sum(
                item["inference"]["samples"] for item in outputs
            ),
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    result_path.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        "# T181 count-weighted head interpolation\n\n"
        f"- Status: `{basis['status']}`\n"
        f"- Decision: `{basis['decision']}`\n"
        f"- Alpha: `{alpha:.6f}`\n"
        f"- Failed checks: `{failed}`\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    parser.add_argument("--work-root", type=Path, default=WORK)
    args = parser.parse_args()
    result = run(
        args.preregistration, args.result, args.markdown, args.work_root
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
