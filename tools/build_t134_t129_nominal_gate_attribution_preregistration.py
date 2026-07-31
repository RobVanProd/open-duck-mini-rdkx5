#!/usr/bin/env python3
"""Freeze read-only attribution of T129's sole nominal failure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T132 = ANALYSIS / "t132b_interrupted_nominal_recovery_result.json"
T102 = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T130 = ANALYSIS / "t130_t129_recovered_training_validation.json"
T97 = ANALYSIS / "t97_hidden_gate_preregistration.json"
HALF = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t131_t129_deployments_v1/1003520/hard_gate/raw_hard_gate.onnx"
)
FINAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t131_t129_deployments_v1/2007040/hard_gate/raw_hard_gate.onnx"
)
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_023820_1003520.onnx"
)
OUTPUT = ANALYSIS / "t134_t129_nominal_gate_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T134_T129_NOMINAL_GATE_ATTRIBUTION_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t134_t129_nominal_gate_attribution.py"
TEST = ROOT / "tests" / "test_t134_t129_nominal_gate_attribution.py"


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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T134: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T134 preregistration requires clean worktree")

    t132 = json.loads(T132.read_text(encoding="utf-8"))
    t102 = json.loads(T102.read_text(encoding="utf-8"))
    t130 = json.loads(T130.read_text(encoding="utf-8"))
    sources = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t132_result": T132,
        "t102_source_nominal": T102,
        "t130_training_validation": T130,
        "t97_population": T97,
    }
    graphs = {
        "t129_half_hard": HALF,
        "t129_final_hard": FINAL,
        "t100c_half_hard": SOURCE,
    }
    checks = {
        "t132_is_single_nominal_hold": (
            t132["status"] == "HOLD_T132B_T129_NOMINAL_MATRIX"
            and t132["condition"]["green_cells"] == 15
            and t132["decision"]
            == "CLOSE_T129_NEGATIVE_ONLY_EXPERT_TRAINTHROUGH"
        ),
        "source_nominal_was_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
        ),
        "only_negative_expert_changed": (
            t130["checks"]["both_exports_only_update_expert_and_critic"]
            and all(
                row["every_mature_actor_leaf_exact"]
                and row["normalizer_exact"]
                for row in t130["exports"]["updates"]
            )
        ),
        "sources_and_graphs_present": all(
            path.is_file() for path in (*sources.values(), *graphs.values())
        ),
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T134 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t134_t129_nominal_gate_attribution_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T134_T129_NOMINAL_GATE_ATTRIBUTION"
        ),
        "question": (
            "Did a gait-state-dependent false-positive hard gate expose the "
            "new negative-only expert in nominal motion, while the frozen "
            "early condition signal remains separable?"
        ),
        "thresholds": {
            "minimum_gate_active_source_delta": 0.1,
            "minimum_early_score_margin": 0.5,
        },
        "sources": {name: receipt(path) for name, path in sources.items()},
        "graphs": {name: receipt(path) for name, path in graphs.items()},
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "NO_NEW_POLICY_MECHANISM",
        },
        "execution_now": {
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_trace_attribution": True,
            "calibration_context_router_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
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
        "# T134 T129 nominal-gate attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen: 16 T132 traces plus 72-row T97 early population\n"
        "- No simulator, optimizer, hosted compute, or robot\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
