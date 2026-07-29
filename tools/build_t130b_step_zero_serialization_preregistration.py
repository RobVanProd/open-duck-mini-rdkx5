#!/usr/bin/env python3
"""Freeze read-only attribution of T129's step-zero ONNX mismatch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T130 = ANALYSIS / "t130_t129_recovered_training_validation.json"
T128 = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
T129_PREREG = ANALYSIS / "t129_negative_only_expert_hosted_preregistration.json"
TRACE_POPULATION = ANALYSIS / "t97_hidden_gate_preregistration.json"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t129_colab_extracted_20260729/"
    "t129_negative_only_expert_continuation/training"
)
OUTPUT = ANALYSIS / "t130b_step_zero_serialization_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T130B_STEP_ZERO_SERIALIZATION_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t130b_step_zero_serialization_recovery.py"
TEST = ROOT / "tests" / "test_t130b_step_zero_serialization.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def graph_step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T130B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T130B preregistration requires clean worktree")
    t130 = json.loads(T130.read_text(encoding="utf-8"))
    t128 = json.loads(T128.read_text(encoding="utf-8"))
    prereg = json.loads(T129_PREREG.read_text(encoding="utf-8"))
    hosted_step_zero = next(
        path for path in RAW_ROOT.glob("*.onnx") if graph_step(path) == 0
    )
    cpu_step_zero = Path(
        t128["training"]["graphs"]["0"]["receipt"]["path"]
    )
    expected = Path(prereg["paths"]["expected_step_zero_raw"])
    sources = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t130_hold": T130,
        "t128_cpu": T128,
        "t129_preregistration": T129_PREREG,
        "trace_population": TRACE_POPULATION,
    }
    checks = {
        "t130_single_hold_exact": (
            t130["status"] == "HOLD_T130_T129_RECOVERED_TRAINING_VALIDATION"
            and t130["failed_checks"] == ["step_zero_raw_onnx_byte_exact"]
            and [
                name for name, passed in t130["checks"].items() if not passed
            ]
            == ["step_zero_raw_onnx_byte_exact"]
        ),
        "t128_cpu_contract_green": (
            t128["status"]
            == "PASS_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
            and t128["failed_checks"] == []
        ),
        "hosted_matches_cpu_exporter_hash": (
            sha256(hosted_step_zero) == sha256(cpu_step_zero)
            and sha256(hosted_step_zero)
            == t128["training"]["graphs"]["0"]["receipt"]["sha256"]
        ),
        "expected_transform_is_distinct": sha256(expected)
        != sha256(hosted_step_zero),
        "all_sources_present": all(path.is_file() for path in sources.values()),
        "no_optimizer_behavior_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T130B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t130b_step_zero_serialization_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
        ),
        "question": (
            "Is T130's sole byte mismatch exactly the known omission of the "
            "unused zero_adapter_location initializer, with hosted and CPU "
            "exporter graphs otherwise identical and behavior bit-exact?"
        ),
        "expected_difference": {
            "expected_only_initializers": ["zero_adapter_location"],
            "actual_only_initializers": [],
            "shared_initializers_bit_exact": True,
            "nodes_bit_exact": True,
            "abi_bit_exact": True,
            "trace_rows_bit_exact": 72,
            "random_chain_steps_bit_exact": 256,
        },
        "policies": {
            "expected_transform": receipt(expected),
            "cpu_exporter_step_zero": receipt(cpu_step_zero),
            "hosted_step_zero": receipt(hosted_step_zero),
        },
        "sources": {name: receipt(path) for name, path in sources.items()},
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "RECOVER_T130_VALIDATION_AND_EARN_T131_T129_HARD_GATE_"
                "POSTEXPORT_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "NO_BEHAVIOR_EVALUATION",
        },
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_recovery": True,
            "postexport_preregistration": False,
            "behavior_evaluation": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T130B step-zero serialization preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Read-only: expected transform vs CPU/hosted exporter\n"
        "- Optimizer / behavior / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
