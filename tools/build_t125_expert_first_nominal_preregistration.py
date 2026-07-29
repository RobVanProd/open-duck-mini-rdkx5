#!/usr/bin/env python3
"""Freeze the post-hoc expert-first nominal mechanism screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T122 = ANALYSIS / "t122_t120_postexport_result.json"
T124 = ANALYSIS / "t124_t120_leaf_factorial_result.json"
BASIS = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t125_expert_first_nominal.py"
TEST = ROOT / "tests" / "test_t125_expert_first_nominal.py"
OUTPUT = ANALYSIS / "t125_expert_first_nominal_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T125_EXPERT_FIRST_NOMINAL_PREREGISTRATION_20260729.md"
)
ASSET_DIR = Path(
    "D:/CodexArtifacts/open-duck-policy/t125_expert_first_screen_v1"
)
HF_POLICY = ASSET_DIR / "half_router_final_expert.onnx"
EXPERT = ["negative_adapter_weight", "negative_adapter_bias"]
ROUTER = ["hidden_gate_coefficient", "hidden_gate_intercept"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def replace(model: onnx.ModelProto, name: str, value: np.ndarray) -> None:
    matches = [item for item in model.graph.initializer if item.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"T125 missing initializer: {name}")
    matches[0].CopyFrom(numpy_helper.from_array(value, name=name))


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def build_asset(half_path: Path, final_path: Path) -> dict[str, Any]:
    if ASSET_DIR.exists():
        raise FileExistsError(f"refusing to overwrite T125 assets: {ASSET_DIR}")
    ASSET_DIR.mkdir(parents=True)
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    half_arrays = arrays(half)
    final_arrays = arrays(final)
    if set(half_arrays) != set(final_arrays):
        raise RuntimeError("T125 initializer topology changed")
    changed = sorted(
        name
        for name in half_arrays
        if not np.array_equal(half_arrays[name], final_arrays[name])
    )
    if changed != sorted(EXPERT + ROUTER):
        raise RuntimeError(f"T125 actor scope changed: {changed}")
    for name in EXPERT:
        replace(half, name, final_arrays[name])
    onnx.checker.check_model(half)
    onnx.save(half, HF_POLICY)
    saved = arrays(onnx.load(HF_POLICY))
    checks = {
        "expert_is_final_exact": all(
            np.array_equal(saved[name], final_arrays[name]) for name in EXPERT
        ),
        "router_is_half_exact": all(
            np.array_equal(saved[name], half_arrays[name]) for name in ROUTER
        ),
        "all_other_initializers_half_exact": all(
            np.array_equal(saved[name], half_arrays[name])
            for name in saved
            if name not in EXPERT
        ),
        "cpu_provider": session(HF_POLICY).get_providers()
        == ["CPUExecutionProvider"],
    }
    return {
        "receipt": receipt(HF_POLICY),
        "changed_half_to_final_initializers": changed,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T125 requires --read-only-authorized")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T125: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T125 preregistration requires clean worktree")
    t122 = json.loads(T122.read_text(encoding="utf-8"))
    t124 = json.loads(T124.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    half = t122["deployments"]["1003520"]["wrapped"]
    final = t122["deployments"]["2007040"]["wrapped"]
    asset = build_asset(Path(half["path"]), Path(final["path"]))
    policies = [
        {
            "checkpoint_id": "T125_HALF_ROUTER_FINAL_EXPERT",
            "step": 1003520,
            **asset["receipt"],
        },
        {
            "checkpoint_id": "T125_FINAL_ROUTER_FINAL_EXPERT",
            "step": 2007040,
            **final,
        },
    ]
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t122_result": T122,
        "t124_result": T124,
        "basis": BASIS,
    }
    checks = {
        "t124_expert_dominant": (
            t124["status"] == "PASS_T124_T120_LEAF_FACTORIAL"
            and t124["classification"] == "EXPERT_DOMINANT"
            and t124["decision"] == "EARN_EXPERT_FIRST_CPU_SCREEN_ONLY"
        ),
        "asset_checks_green": all(asset["checks"].values()),
        "policies_exact": all(
            Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in policies
        ),
        "basis_is_frozen_nominal": (
            basis["status"]
            == "PREREGISTERED_T107_SOFT_GATE_NOMINAL_MATRIX"
            and basis["conditions"][0]["condition_index"] == 2
        ),
        "inputs_present": all(path.is_file() for path in inputs.values()),
        "screen_is_not_checkpoint_selection_or_candidate_promotion": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t125_expert_first_nominal_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T125_EXPERT_FIRST_NOMINAL_SCREEN"
            if not failed
            else "HOLD_T125_EXPERT_FIRST_NOMINAL_PREREGISTRATION"
        ),
        "question": (
            "Does applying the mature expert before the router matures recover "
            "the sole T120 nominal miss across the full frozen matrix?"
        ),
        "interpretation": (
            "This post-hoc factorial screen is an existence test for staged "
            "expert-first learning. It is not a deployable policy result and "
            "cannot satisfy checkpoint persistence."
        ),
        "asset": asset,
        "conditions": basis["conditions"],
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "policies": policies,
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": basis["repository_inputs"],
        "matrix": {
            "cells": 16,
            "both_factorial_endpoints_required": True,
            "training_selection_weight": 0,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T126_EXPERT_FIRST_NEGATIVE_ENDPOINT_SCREEN_ONLY"
            ),
            "fail_decision": "CLOSE_EXPERT_FIRST_STAGE_HYPOTHESIS",
            "no_hosted_training": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_nominal_screen": not failed,
            "negative_endpoint_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T125 expert-first nominal preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: `2 factorial endpoints x 2 fits x 4 commands = 16`\n"
        "- This is a mechanism screen, not a candidate or checkpoint selection\n"
        "- Training / Colab / robot: `0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
