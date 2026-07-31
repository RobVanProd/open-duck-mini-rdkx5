#!/usr/bin/env python3
"""Freeze the T4 BEST_WALK baseline-versus-current-gates matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t4_baseline_all_gates_preregistration.json"
MARKDOWN = ANALYSIS / "T4_BASELINE_ALL_GATES_PREREGISTRATION_20260725.md"
PATHS = {
    "policy": ROOT / "policy" / "BEST_WALK_ONNX_2.onnx",
    "fit": ANALYSIS / "actuator_response_fit_corrected_knee.json",
    "seed_sweep": ROOT / "tools" / "run_candidate_seed_sweep.py",
    "eval_driver": ROOT / "tools" / "eval_policy_with_actuator_bridge.py",
    "evaluator": ROOT / "tools" / "closed_loop_sim_eval.py",
    "t4_runner": ROOT / "tools" / "run_t4_baseline_all_gates.py",
    "gate_source": ROOT / "docs" / "EVALUATOR_RECONCILIATION.md",
    "step0_source": ROOT / "docs" / "DUCK_STATUS.md",
    "published_vanilla_x008": (
        ANALYSIS / "published_policy_propulsion_x008_straight_audit.json"
    ),
    "corrected_bridge_x008": (
        ANALYSIS / "corrected_bridge_best_walk_reroll_x008.json"
    ),
}
EXPECTED = {
    "policy": "3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067",
    "fit": "40d2aefbdaeac986fc856aade8170f2a9d72831613a7a30873bfff0846e4f1bb",
    "playground_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def git_output(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--playground-root",
        type=Path,
        default=Path(r"D:\CodexProjects\Open_Duck_Playground-upstream-b9be205"),
    )
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    missing = sorted(name for name, path in PATHS.items() if not path.is_file())
    hashes = {
        name: None if not path.is_file() else sha256(path)
        for name, path in PATHS.items()
    }
    commit = (
        git_output(playground, "rev-parse", "HEAD")
        if (playground / ".git").exists()
        else None
    )
    porcelain = (
        git_output(playground, "status", "--porcelain")
        if (playground / ".git").exists()
        else "missing"
    )
    failed_checks = []
    for name in ("policy", "fit"):
        if hashes[name] != EXPECTED[name]:
            failed_checks.append(f"hash:{name}")
    if commit != EXPECTED["playground_commit"]:
        failed_checks.append("playground_commit")
    if porcelain:
        failed_checks.append("playground_not_clean")

    conditions = [
        {
            "condition": f"x{command:.3f}_{bridge}",
            "command_x_m_s": command,
            "bridge_mode": bridge,
            "mode_name": bridge,
        }
        for command in (0.0, 0.08)
        for bridge in ("vanilla", "fitted")
    ]
    matrix = [
        {**condition, "seed": seed}
        for condition in conditions
        for seed in range(8)
    ]
    status = (
        "PREREGISTERED_T4_BASELINE_ALL_GATES"
        if not missing and not failed_checks
        else "HOLD_T4_BASELINE_ALL_GATES_PREREGISTRATION"
    )
    payload = {
        "schema_version": "open_duck.t4_baseline_all_gates_preregistration.v1",
        "status": status,
        "missing_inputs": missing,
        "failed_checks": failed_checks,
        "input_paths": {name: str(path) for name, path in PATHS.items()},
        "input_sha256": hashes,
        "expected_sha256": {
            "policy": EXPECTED["policy"],
            "fit": EXPECTED["fit"],
        },
        "playground": {
            "path": str(playground),
            "commit": commit,
            "expected_commit": EXPECTED["playground_commit"],
            "porcelain_status": porcelain,
        },
        "question": (
            "Does BEST_WALK_ONNX_2 pass every canonical feasibility gate used "
            "to reject later candidate policies?"
        ),
        "frozen_configuration": {
            "policy": "BEST_WALK_ONNX_2.onnx",
            "task": "flat_terrain_backlash",
            "duration_s": 15.0,
            "ticks_per_cell": 750,
            "commands_x_m_s": [0.0, 0.08],
            "bridge_modes": ["vanilla", "fitted"],
            "seeds": list(range(8)),
            "cell_count": len(matrix),
            "eval_role": "candidate",
            "reset_mode": "playground",
            "policy_action_gain": 1.0,
            "policy_or_normalizer_modification": False,
            "mjcf_or_gate_modification": False,
        },
        "conditions": conditions,
        "matrix": matrix,
        "matrix_sha256": canonical_sha256(matrix),
        "gate_contract": {
            "documented_promotion_x008": [
                {
                    "metric": "duration_complete_count",
                    "operator": "eq",
                    "threshold": 8,
                },
                {"metric": "fall_count", "operator": "eq", "threshold": 0},
                {
                    "metric": "mean_track_ratio",
                    "operator": "gte",
                    "threshold": 0.50,
                },
                {
                    "metric": "max_pitch_tracking_p95_rad",
                    "operator": "lte",
                    "threshold": 0.20,
                },
                {
                    "metric": "max_p95_velocity_limit_excess_rad_s",
                    "operator": "lte",
                    "threshold": 0.0,
                },
            ],
            "documented_semantic_x000": [
                {
                    "metric": "duration_complete_count",
                    "operator": "eq",
                    "threshold": 8,
                },
                {"metric": "fall_count", "operator": "eq", "threshold": 0},
                {
                    "metric": "mean_abs_vx_m_s",
                    "operator": "lte",
                    "threshold": 0.005,
                },
                {
                    "metric": "max_p95_velocity_limit_excess_rad_s",
                    "operator": "lte",
                    "threshold": 0.0,
                },
            ],
            "coded_candidate_gate": [
                {
                    "metric": "max_action_saturation_pct",
                    "operator": "lte",
                    "threshold": 1.0,
                },
                {
                    "metric": "max_pitch_tracking_p95_rad",
                    "operator": "lte",
                    "threshold": 0.20,
                },
                {
                    "metric": "max_p95_velocity_limit_excess_rad_s",
                    "operator": "lte",
                    "threshold": 0.0,
                },
                {
                    "metric": "max_instant_velocity_limit_excess_rad_s",
                    "operator": "lte",
                    "threshold": 0.0,
                },
                {
                    "metric": "max_abs_body_pitch_p95_rad",
                    "operator": "lte",
                    "threshold": 0.25,
                },
                {
                    "metric": "min_base_height_m",
                    "operator": "gte",
                    "threshold": 0.12,
                },
                {
                    "metric": "min_reward_mean",
                    "operator": "gte",
                    "threshold": 0.30,
                },
                {
                    "metric": "min_seed_track_ratio",
                    "operator": "gte",
                    "threshold": 0.25,
                    "applies_if_abs_command_gte": 0.02,
                },
            ],
            "velocity_limits_source": "corrected-knee fit, per pitch-chain joint",
            "coded_vs_documented_discrepancy": (
                "the documented x=0.08 promotion boundary uses mean track "
                "ratio >=0.50, while classify_candidate_gate uses minimum "
                "per-mode ratio >=0.25; both are reported without choosing "
                "between them after seeing results"
            ),
        },
        "decision_rule": {
            "failed_baseline_gate": (
                "must be relaxed to the measured baseline value or explicitly "
                "relabelled as a stretch goal rather than a feasibility boundary"
            ),
            "automatic_gate_changes": False,
            "table_scope": (
                "all four conditions and every documented/coded criterion; "
                "not only the first evaluator failure reason"
            ),
            "selection_weight": 0,
        },
        "required_context_note": (
            "DUCK_STATUS records that a step-0 random-initialization export "
            "passed x=0.0 while every trained checkpoint from step 153600 "
            "onward failed it; this is reported verbatim as an objective "
            "diagnostic, not used to alter the numeric result"
        ),
        "execution_contract": {
            "method": (
                "each cell invokes tools/run_candidate_seed_sweep.py with one "
                "explicit seed; results are aggregated only after all 32 exact "
                "cell contracts exist"
            ),
            "resume": (
                "a cell may be reused only when its canonical contract and "
                "raw seed-sweep JSON hash match"
            ),
            "partial_matrix_decision_weight": 0,
            "result_requires_all_cells": True,
        },
        "authority": {
            "offline_cpu_only": True,
            "robot_or_rdk_access": False,
            "policy_modification": False,
            "training_steps": 0,
            "hosted_compute": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(
        {
            "input_sha256": payload["input_sha256"],
            "playground": payload["playground"],
            "frozen_configuration": payload["frozen_configuration"],
            "matrix_sha256": payload["matrix_sha256"],
            "gate_contract": payload["gate_contract"],
            "decision_rule": payload["decision_rule"],
            "execution_contract": payload["execution_contract"],
        }
    )
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T4 baseline-versus-all-gates preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`\n"
        f"- Matrix SHA-256: `{payload['matrix_sha256']}`\n"
        "- Frozen matrix: `32` CPU-only cells (2 commands x 2 bridge modes "
        "x 8 seeds), 15 seconds each.\n"
        "- Both the documented promotion boundary and the evaluator's coded "
        "boundary are reported because their forward thresholds differ.\n"
        "- No threshold changes are made automatically.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PREREGISTERED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
