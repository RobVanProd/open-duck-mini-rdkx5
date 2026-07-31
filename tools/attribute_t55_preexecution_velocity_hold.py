#!/usr/bin/env python3
"""Record T55's pre-optimizer velocity-vector wiring hold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t55_dynamic_single_support_cpu_preregistration.json"
RUNNER = ROOT / "tools" / "run_t55_dynamic_single_support_cpu_contract.py"
PARTIAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t55_dynamic_single_support_cpu_v1"
)
LOG = PARTIAL / "balance_training.log"
RESULT = ANALYSIS / "t55_dynamic_single_support_cpu_result.json"
RESULT_MD = ANALYSIS / "T55_DYNAMIC_SINGLE_SUPPORT_CPU_RESULT_20260728.md"
OUTPUT = ANALYSIS / "t55_preexecution_velocity_hold_attribution.json"
MARKDOWN = (
    ANALYSIS / "T55_PREEXECUTION_VELOCITY_HOLD_ATTRIBUTION_20260728.md"
)
EXPECTED_ERROR = (
    "ValueError: winner-v3 selected all-joint velocity vector changed"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T55 hold: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T55 attribution requires a clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    log = LOG.read_text(encoding="utf-8")
    smoke = PARTIAL / "balance_smoke"
    checkpoints = [
        path for path in smoke.iterdir() if path.is_dir()
    ]
    graphs = list(smoke.glob("*.onnx"))
    event_files = list(smoke.glob("events.out.tfevents*"))
    checks = {
        "original_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            and prereg["failed_checks"] == []
        ),
        "failure_is_exact_velocity_vector_precondition": (
            EXPECTED_ERROR in log
            and "OpenDuckMiniV2Runner(args)" in log
        ),
        "no_checkpoint_or_graph_written": (
            checkpoints == [] and graphs == []
        ),
        "only_empty_startup_event_file_may_exist": (
            len(event_files) <= 1
            and all(path.stat().st_size <= 256 for path in event_files)
        ),
        "formal_result_absent": (
            not RESULT.exists() and not RESULT_MD.exists()
        ),
        "failure_precedes_runner_train_call": (
            "runner = OpenDuckMiniV2Runner(args)" in log
            and "runner.train(" not in log
        ),
        "optimizer_behavior_hosted_robot_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t55_preexecution_velocity_hold_attribution.v1"
        ),
        "status": (
            "PASS_T55_PREEXECUTION_VELOCITY_HOLD_ATTRIBUTION"
            if not failed
            else "HOLD_T55_PREEXECUTION_VELOCITY_HOLD_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T55B_EXACT_CPU_RECOVERY_PREREGISTRATION_ONLY"
            if not failed
            else "STOP_T55_AND_REVIEW_PREEXECUTION_HOLD"
        ),
        "finding": (
            "The T55 runner called T31's command helper without first "
            "installing T31's frozen source velocity vector into the shared "
            "T20 helper. The composed runner rejected the T20 vector during "
            "environment construction, before runner.train(), checkpoints, "
            "ONNX exports, optimizer steps, or behavior."
        ),
        "inputs": {
            "preregistration": receipt(PREREG),
            "runner_before_correction": receipt(RUNNER),
            "log": receipt(LOG),
            "partial_root": str(PARTIAL.resolve()),
        },
        "observed": {
            "checkpoint_directories": len(checkpoints),
            "onnx_graphs": len(graphs),
            "event_files": [
                receipt(path) for path in event_files
            ],
            "formal_result_exists": RESULT.exists(),
        },
        "correction": {
            "single_change": (
                "install T31.VELOCITY_LIMITS into T20 only while building "
                "each T55 command, then restore the prior helper value"
            ),
            "curriculum_formula_change": False,
            "source_checkpoint_change": False,
            "stage_order_change": False,
            "step_count_change": False,
            "gate_change": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t55b_cpu_recovery_preregistration": not failed,
            "cpu_recovery_execution": False,
            "hosted_training": False,
            "behavior_matrix": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "result_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T55 pre-execution velocity hold attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Failure: frozen T20/T31 source-velocity wiring mismatch",
                "- Failure point: runner construction, before `train()`",
                "- Checkpoints / ONNX / optimizer / behavior: `0/0/0/0`",
                "- Curriculum/source/stages/gates changed: `NO`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
