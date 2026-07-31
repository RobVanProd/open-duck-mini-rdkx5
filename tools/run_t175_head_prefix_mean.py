#!/usr/bin/env python3
"""Build and verify T170's two-leaf cumulative head means."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
    verify,
)
from run_t172_t170_postexport_composition import inference_contract


PREREG = ANALYSIS / "t175_head_prefix_mean_preregistration.json"
RESULT = ANALYSIS / "t175_head_prefix_mean_result.json"
MARKDOWN = ANALYSIS / "T175_HEAD_PREFIX_MEAN_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t175_head_prefix_mean_v1"
)


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


def prefix_mean(values: list[np.ndarray]) -> np.ndarray:
    return np.mean(
        np.stack(values).astype(np.float64),
        axis=0,
    ).astype(np.float32)


def build_graph(
    source_path: Path,
    member_paths: list[Path],
    names: list[str],
    destination: Path,
) -> dict[str, Any]:
    source = onnx.load(source_path)
    source_values = arrays(source)
    members = [arrays(onnx.load(path)) for path in member_paths]
    expected = {
        name: prefix_mean([value[name] for value in members])
        for name in names
    }
    for name in names:
        replace(source, name, expected[name])
    onnx.checker.check_model(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(source, destination)
    actual = arrays(source)
    changed = sorted(
        name
        for name in source_values
        if not np.array_equal(source_values[name], actual[name])
    )
    return {
        "members": [receipt(path) for path in member_paths],
        "transformed": receipt(destination),
        "changed_initializers": changed,
        "head_arithmetic_exact": all(
            np.array_equal(actual[name], expected[name]) for name in names
        ),
        "all_other_initializers_exact": all(
            np.array_equal(source_values[name], actual[name])
            for name in source_values
            if name not in names
        ),
        "initializer_names_exact": set(source_values) == set(actual),
        "nodes_byte_exact": all(
            left.SerializeToString() == right.SerializeToString()
            for left, right in zip(
                onnx.load(source_path).graph.node,
                source.graph.node,
                strict=True,
            )
        ),
        "all_initializers_finite": all(
            np.all(np.isfinite(value)) for value in actual.values()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or WORK.exists():
        raise FileExistsError("refusing to overwrite T175 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T175 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T175_HEAD_PREFIX_MEAN"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T175 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for name, item in prereg["graphs"].items():
        verify(item, f"graphs.{name}")

    WORK.mkdir(parents=True)
    source = Path(prereg["graphs"]["source"]["path"])
    outputs = []
    started = time.time()
    for checkpoint_id, member_names in (
        ("T175_HEAD_MEAN_HALF", ["source", "half"]),
        ("T175_HEAD_MEAN_FINAL", ["source", "half", "final"]),
    ):
        destination = WORK / checkpoint_id / "head_prefix_mean.onnx"
        members = [
            Path(prereg["graphs"][name]["path"]) for name in member_names
        ]
        structure = build_graph(
            source,
            members,
            prereg["transform"]["head_initializers"],
            destination,
        )
        inference = inference_contract(
            destination,
            source,
            prereg["contexts"],
            int(prereg["inference"]["seed"])
            + (1 if checkpoint_id.endswith("HALF") else 2),
        )
        outputs.append(
            {
                "checkpoint_id": checkpoint_id,
                "member_names": member_names,
                "structure": structure,
                "inference": inference,
            }
        )

    head_names = sorted(prereg["transform"]["head_initializers"])
    checks = {
        "two_prefix_mean_graphs": len(outputs) == 2,
        "all_head_arithmetic_exact": all(
            row["structure"]["head_arithmetic_exact"] for row in outputs
        ),
        "all_changed_initializers_are_head_only": all(
            row["structure"]["changed_initializers"] == head_names
            for row in outputs
        ),
        "all_other_initializers_exact": all(
            row["structure"]["all_other_initializers_exact"]
            for row in outputs
        ),
        "all_initializer_names_exact": all(
            row["structure"]["initializer_names_exact"] for row in outputs
        ),
        "all_nodes_byte_exact": all(
            row["structure"]["nodes_byte_exact"] for row in outputs
        ),
        "all_initializers_finite": all(
            row["structure"]["all_initializers_finite"] for row in outputs
        ),
        "all_inactive_routes_bit_exact": all(
            row["inference"]["all_inactive_routes_bit_exact"]
            for row in outputs
        ),
        "all_x0_outputs_bit_exact": all(
            row["inference"]["all_x0_outputs_bit_exact"] for row in outputs
        ),
        "both_y_negative_contexts_route_nominal": all(
            row["inference"]["both_y_negative_contexts_route_nominal"]
            for row in outputs
        ),
        "all_outputs_finite": all(
            row["inference"]["all_outputs_finite"] for row in outputs
        ),
        "cpu_only": all(
            row["inference"]["provider"] == "CPUExecutionProvider"
            for row in outputs
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t175_head_prefix_mean_result.v1",
        "status": (
            "PASS_T175_HEAD_PREFIX_MEAN"
            if not failed
            else "HOLD_T175_HEAD_PREFIX_MEAN"
        ),
        "decision": (
            "EARN_T176_HEAD_PREFIX_MEAN_TARGETED_MATRIX_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_HEAD_PREFIX_MEAN_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "graphs": outputs,
        "execution": {
            "inference_samples": sum(
                row["inference"]["samples"] for row in outputs
            ),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "targeted_matrix_preregistration": not failed,
            "behavior": False,
            "training": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T175 head-prefix-mean result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Only the two nominal adapter-head tensors changed.\n"
        "- Inactive routes and x=0 remain bit-exact to T164 final.\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
