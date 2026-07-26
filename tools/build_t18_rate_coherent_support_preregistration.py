#!/usr/bin/env python3
"""Freeze T18's zero-training rate-coherent support screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from t18_rate_coherent_support_onnx import (
    ACTION_SCALE_RAD,
    CONTRACT_TOLERANCE,
    CONTROL_DT_S,
    MAX_ACTION_DELTA,
    RATE_LIMITS_RAD_S,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t18_rate_coherent_support_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T18_RATE_COHERENT_SUPPORT_PREREGISTRATION_20260726.md"
)
RUNNER = ROOT / "tools" / "run_t18_rate_coherent_support_screen.py"
TRANSFORM = ROOT / "tools" / "t18_rate_coherent_support_onnx.py"
TEST = ROOT / "tests" / "test_t18_rate_coherent_support.py"
T16_RUNNER = ROOT / "tools" / "run_t16_support_coordinate_screen.py"
T16_WORKER = ROOT / "tools" / "evaluate_t16_support_coordinate.py"
T17_TRANSFORM = ROOT / "tools" / "t17_support_homeomorphism_onnx.py"


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
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T18 preregistration")
    for path in (
        RUNNER,
        TRANSFORM,
        TEST,
        T16_RUNNER,
        T16_WORKER,
        T17_TRANSFORM,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    t17_prereg_path = (
        ANALYSIS / "t17_support_homeomorphism_preregistration.json"
    )
    t17_result_path = ANALYSIS / "t17_support_homeomorphism_result.json"
    rate_path = ANALYSIS / "t17_rate_anatomy.json"
    t17_prereg = json.loads(
        t17_prereg_path.read_text(encoding="utf-8")
    )
    t17 = json.loads(t17_result_path.read_text(encoding="utf-8"))
    rate = json.loads(rate_path.read_text(encoding="utf-8"))
    checks = {
        "t17_bounded_map_closed_on_rate": (
            t17["decision"] == "CLOSE_BOUNDED_SUPPORT_HOMEOMORPHISM"
            and t17["failed_checks"] == ["all_cells_green"]
            and t17["checks"]["wrapper_contract_green"]
            and t17["checks"]["all_eight_x0_cells_retain_support_exactly"]
        ),
        "t17_rate_failure_persistent": (
            rate["status"]
            == "PASS_T17_PERSISTENT_RATE_FAILURE_ATTRIBUTION"
            and rate["decision"]
            == "REQUIRE_RATE_COHERENT_TRANSITION_BEFORE_TRAIN_THROUGH"
            and rate["summary"]["moving_traces"] == 24
            and rate["summary"]["minimum_violating_ticks_per_trace"]
            >= 200
        ),
        "candidate_pair_exact": (
            len(t17_prereg["candidate"]["checkpoints"]) == 2
        ),
        "fit_pair_exact": (
            set(t17_prereg["candidate"]["fits"]) == {"p30", "p31_34"}
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "transform": receipt(TRANSFORM),
        "test": receipt(TEST),
        "shared_t16_runner_helpers": receipt(T16_RUNNER),
        "frozen_t16_worker": receipt(T16_WORKER),
        "t17_transform": receipt(T17_TRANSFORM),
        "t17_preregistration": receipt(t17_prereg_path),
        "t17_result": receipt(t17_result_path),
        "t17_rate_anatomy": receipt(rate_path),
        "t8_evaluator_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "frozen_closed_loop_evaluator": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
    }
    basis = {
        "schema_version": (
            "open_duck.t18_rate_coherent_support_preregistration.v1"
        ),
        "status": "PREREGISTERED_T18_RATE_COHERENT_SUPPORT_SCREEN",
        "question": (
            "Does composing T17's bounded support-centered map with the "
            "already-frozen full measured physical rate transition produce "
            "a zero-training candidate that passes the complete nominal and "
            "negative-COM matrix?"
        ),
        "causal_basis": {
            "t16": (
                "Affine support translation rescued every moving cell but "
                "created 57-69 percent saturation."
            ),
            "t17": (
                "The bounded map removed broad saturation and retained "
                "forward, bilateral, sub-0.2-rad behavior in almost every "
                "moving cell, but violated the frozen rate vector."
            ),
            "rate_anatomy": (
                "Every one of the 24 T17 moving traces violates the physical "
                "rate vector on 222-397 ticks, so this is a gait-wide state "
                "transition mismatch rather than a startup seam."
            ),
            "materially_distinct_mechanism": (
                "T18 does not alter T17's curve, support, observations, "
                "checkpoints, or thresholds. It composes the non-negotiable "
                "measured per-joint rate transition after the bounded map and "
                "feeds the realized final action back as previous_action_out. "
                "This is a stateful dynamical composition, not a new static "
                "homeomorphism or a selected scalar."
            ),
        },
        "sources": sources,
        "playground": t17_prereg["playground"],
        "candidate": t17_prereg["candidate"],
        "transition": {
            "base": t17_prereg["transform"],
            "rate_limits_rad_s": RATE_LIMITS_RAD_S.astype(float).tolist(),
            "control_dt_s": float(CONTROL_DT_S),
            "action_scale_rad": float(ACTION_SCALE_RAD),
            "maximum_action_delta": (
                MAX_ACTION_DELTA.astype(float).tolist()
            ),
            "equation": (
                "final=clip(mapped, previous_final-delta, "
                "previous_final+delta); bounds intersect [-1,1]"
            ),
            "state_feedback": (
                "previous_action_out equals realized final action bit-exact"
            ),
            "source_previous_action": (
                "T17 inverse maps external realized previous action before "
                "source inference"
            ),
            "free_scalar_count": 0,
            "contract_cases": 256,
            "contract_seed": 20260726,
            "contract_tolerance": CONTRACT_TOLERANCE,
            "external_abi": t17_prereg["transform"]["external_abi"],
        },
        "matrix": t17_prereg["matrix"],
        "handoff_contract": t17_prereg["handoff_contract"],
        "behavior_contract": t17_prereg["behavior_contract"],
        "protection_contract": t17_prereg["protection_contract"],
        "decision_rule": {
            "pass": (
                "Both wrapped checkpoints pass all 32 nominal and "
                "negative-COM cells under both measured fits and all four "
                "commands; all x=0 ticks equal exact support; every wrapper, "
                "ABI, handoff, readback, physical-rate, saturation, behavior, "
                "and manufacturer-duration protection check passes."
            ),
            "pass_next_action": (
                "Earn only a separately preregistered sequential full R2 "
                "screen of the exact two T18 graphs. No training, hardware, "
                "or Gate 5 is earned."
            ),
            "fail": (
                "Close the zero-training rate-coherent support composition. "
                "Do not alter the rate vector, map, support action, joint "
                "subset, checkpoint pair, threshold, or closest result."
            ),
            "partial_results_selection_weight": 0,
            "no_threshold_changes_after_execution": True,
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "checkpoint_selection": False,
            "deployment_or_gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "wrapped_policies": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    if failed:
        basis["status"] = "HOLD_T18_PREREGISTRATION_INPUTS"
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
        "failed_checks": failed,
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T18 rate-coherent support preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Mechanism: T17 bounded support map plus the frozen final physical "
        "rate transition and realized-action feedback.\n"
        "- Free scalars / optimizer steps: `0 / 0`\n"
        "- Matrix: 2 checkpoints x 2 fits x 2 COM conditions x 4 commands "
        "= `32` cells\n"
        "- CPU only; hosted/robot execution: `0/0`\n"
        "- Pass earns only a separately preregistered full R2 screen.\n"
        f"- Canonical SHA-256: "
        f"`{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT.relative_to(ROOT))
    print(MARKDOWN.relative_to(ROOT))
    print(value["status"])
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
