#!/usr/bin/env python3
"""Preregister the V169 read-only V128-final first-R2 anchor screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v169_v128_final_r2_anchor_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V169_V128_FINAL_R2_ANCHOR_PREREGISTRATION_20260725.md"
)
RUNNER = ROOT / "tools/run_winner_v169_v128_final_r2_anchor.py"
V128_NOMINAL = ANALYSIS / "winner_v128_nominal_behavior_result.json"
V10_PREREG = ANALYSIS / "winner_v10_nominal_behavior_preregistration.json"
R2_MATRIX = ANALYSIS / "ground_up_robustness_r2_matrix_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_paths() -> dict[str, Path]:
    return {
        "preregistration_builder": Path(__file__),
        "runner": RUNNER,
        "v10_condition1_runner": ROOT / "tools/run_winner_v10_r2_condition1.py",
        "v10_nominal_runner": ROOT / "tools/run_winner_v10_nominal_behavior.py",
        "v9_nominal_helper": ROOT / "tools/run_winner_v9_nominal_behavior.py",
        "v7_readback_helper": ROOT
        / "tools/run_winner_v7_full_behavior_revalidation.py",
        "evaluator": ROOT / "tools/evaluate_ground_up_policy.py",
        "closed_loop": ROOT / "tools/closed_loop_sim_eval.py",
        "actuator_model": ROOT / "tools/actuator_bridge_model.py",
        "aggregator": ROOT / "tools/aggregate_ground_up_robustness_r1.py",
        "v128_nominal_result": V128_NOMINAL,
        "v10_nominal_preregistration": V10_PREREG,
        "r2_matrix": R2_MATRIX,
        "r2_evaluator_contract": ANALYSIS
        / "ground_up_robustness_r2_evaluator_contract.json",
        "r2_reporting_contract": ANALYSIS
        / "ground_up_robustness_r2_reporting_contract.json",
        "current_contract": ANALYSIS
        / "winner_v3_current_gate_application_contract.json",
        "reference_feature_table": ANALYSIS
        / "ground_up_projected_reference_feature_table.npz",
        "fit_p30": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
        "fit_p31_34": ANALYSIS
        / "fixed_target_p31_34_actuator_fit_20260712.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite frozen V169 preregistration")
    nominal = json.loads(V128_NOMINAL.read_text(encoding="utf-8"))
    v10 = json.loads(V10_PREREG.read_text(encoding="utf-8"))
    r2 = json.loads(R2_MATRIX.read_text(encoding="utf-8"))
    policy = args.policy.resolve()
    playground = args.playground_root.resolve()
    condition = r2["conditions_in_strict_order"][0]
    final_row = next(
        row
        for row in nominal["per_checkpoint"]
        if row["checkpoint_id"] == "V128_CONSTRAINED_FINAL"
    )
    observed_playground = {
        name: sha256(playground / name)
        for name in v10["playground"]["required_file_hashes"]
    }
    checks = {
        "v128_result_valid_but_pair_rejected": (
            nominal["status"] == "PASS_WINNER_V128_NOMINAL_BEHAVIOR_VALID_RESULT"
            and not nominal["decision"]["persistent_both_checkpoint_pass"]
        ),
        "v128_final_exactly_eight_of_eight_nominal": (
            final_row["all_eight_cells_pass"]
            and final_row["passing_cells"] == 8
        ),
        "v128_final_margin_observed_not_assumed": (
            final_row["worst_peak_torque_nm"] == 1.8408489227294922
        ),
        "first_r2_condition_exact": (
            condition
            == {"id": "FLOOR_FRICTION_LO", "override": {"floor_friction": 0.5}}
        ),
        "policy_hash_exact": (
            sha256(policy)
            == "890c118b66c4cbf4ea173cb89354e30e9f628b6a401e48e9c432ae8bbefea4fe"
        ),
        "playground_files_exact": (
            observed_playground == v10["playground"]["required_file_hashes"]
        ),
        "one_policy_eight_cells_only": True,
        "selection_weight_zero": True,
        "no_training_hosted_compute_or_hardware": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v169.v128_final_r2_anchor_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V169_V128_FINAL_R2_ANCHOR_SCREEN"
            if not failed
            else "INVALID_WINNER_V169_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in frozen_paths().items()
        },
        "policy": {
            "path": str(policy),
            "sha256": sha256(policy),
            "checkpoint": "V128_CONSTRAINED_FINAL",
            "nominal_cells_passed": 8,
            "nominal_worst_peak_torque_nm": 1.8408489227294922,
        },
        "playground": v10["playground"],
        "condition": condition,
        "matrix": {
            "fits": ["p30", "p31_34"],
            "commands_x": [0.0, 0.074, 0.077, 0.080],
            "seed": 167931544,
            "duration_ticks": 600,
            "cells": 8,
        },
        "behavior_gates": v10["behavior_gates"],
        "protection_gate": v10["protection_gate"],
        "causal_question": (
            "Does the single nominal-safe V128 final checkpoint preserve the "
            "complete behavior and protection gate at the first frozen R2 "
            "dynamics endpoint?"
        ),
        "pass_rule": [
            "exactly eight complete 600-tick cells cover both fits and all four commands",
            "all x=0 and moving behavior gates pass",
            "every joint tick passes the unchanged current, torque, measured-rate, and duration gates",
            "every evaluation requests and reads back floor friction 0.5 exactly",
            "CPU only; the result has zero candidate-selection weight",
        ],
        "green_decision": (
            "earn only design of a new safe-source architecture contract; "
            "do not authorize a policy candidate, later R2 condition, or training"
        ),
        "stop_rule": (
            "if any cell fails, close V128-final as a robustness anchor; "
            "do not change the condition, gate, policy, fit, command, seed, "
            "duration, or evaluator"
        ),
        "authority": {
            "one_cpu_screen": not failed,
            "safe_source_architecture_design": False,
            "later_r2_condition": False,
            "training": False,
            "hosted_training": False,
            "candidate_selection": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V169 V128-final first-R2 anchor preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One unchanged policy, two fits, four commands, floor friction "
        "`0.5`: eight CPU cells.\n"
        "- This is a read-only source-quality diagnostic with zero candidate "
        "selection weight.\n"
        "- Green earns only architecture-contract design; no later condition, "
        "training, hardware, torque, motion, or Gate 5 authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
