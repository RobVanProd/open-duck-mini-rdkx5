#!/usr/bin/env python3
"""Freeze a read-only attribution of T113's negative-COM failure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t118_routing_failure_attribution.py"
TEST = ROOT / "tests" / "test_t118_routing_failure_attribution.py"
OUTPUT = ANALYSIS / "t118_routing_failure_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "T118_ROUTING_FAILURE_ATTRIBUTION_PREREGISTRATION_20260729.md"
SOURCES = {
    "hard_gate": ANALYSIS / "t103_t100c_negative_endpoint_result.json",
    "gate_dynamics": ANALYSIS / "t104_t100c_gate_dynamics_result.json",
    "soft_gate": ANALYSIS / "t108_soft_gate_negative_endpoint_result.json",
    "always_on": ANALYSIS / "t111_always_on_negative_endpoint_result.json",
    "trainthrough": ANALYSIS / "t117_t113_negative_endpoint_result.json",
    "single_support_cpu": ANALYSIS / "t55_dynamic_single_support_cpu_result.json",
    "single_support_nominal": ANALYSIS / "t59_t56_nominal_matrix_result.json",
    "single_support_family": ANALYSIS / "t65_t62_midpoint_endpoint_screen_result.json",
}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T118 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T118: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T118 preregistration requires clean worktree")
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        **SOURCES,
    }
    source_values = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in SOURCES.items()
    }
    checks = {
        "t117_is_closed": (
            source_values["trainthrough"]["status"]
            == "HOLD_T117_T113_NEGATIVE_ENDPOINT"
            and source_values["trainthrough"]["decision"]
            == "CLOSE_T113_ALWAYS_ON_TRAINTHROUGH"
        ),
        "all_sources_present": all(path.is_file() for path in inputs.values()),
        "analysis_only": True,
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t118_routing_failure_attribution_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T118_ROUTING_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_T118_ROUTING_FAILURE_ATTRIBUTION_PREREGISTRATION"
        ),
        "question": (
            "Do T103/T104/T108/T111/T117 and the earlier balance-first "
            "evidence isolate untrained state-dependent expert routing, "
            "rather than a one-foot/one-phase mask or a universal residual?"
        ),
        "analysis_contract": {
            "pitch_boundary_abs_rad": 0.25,
            "moving_commands_only_for_failure_anatomy": True,
            "first_boundary_crossing_per_failed_trace": True,
            "backward_pitch_requires_negative_pitch": True,
            "backward_motion_requires_negative_local_vx": True,
            "support_categories": [[1, 0], [0, 1], [1, 1], [0, 0]],
            "phase_quadrants": 4,
            "simple_support_phase_mask_rejected_if": {
                "left_single_support_crossings_at_least": 2,
                "right_single_support_crossings_at_least": 2,
                "occupied_phase_quadrants_at_least": 3,
            },
            "routing_comparison_green_cells": {
                "hard_gate": 9,
                "soft_gate": 4,
                "always_on": 6,
                "always_on_trainthrough": 5,
            },
            "fixed_gate_dynamics_expected": {
                "negative_false_inactive_fraction_positive": True,
                "nominal_false_active_fraction_positive": True,
                "maximum_transitions_at_least": 20,
            },
            "single_support_family_must_be_closed": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T119_JOINT_SOFT_ROUTER_EXPERT_CPU_PREREGISTRATION_ONLY"
            ),
            "hold_decision": "HOLD_FOR_DISTINCT_MECHANISM_REVIEW",
            "hosted_training": False,
            "behavior_rerun": False,
            "gate5": False,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_read_only_attribution": not failed,
            "successor_cpu_preregistration": False,
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
        "# T118 routing failure attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Existing traces only; zero simulator or optimizer steps\n"
        "- Compares hard, soft, always-on, train-through, and balance-first evidence\n"
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
