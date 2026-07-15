#!/usr/bin/env python3
"""Aggregate the frozen RESET_EST_LATCH_U05 behavior matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from aggregate_ground_up_robustness_r1 import summarize


STEPS = (1003520, 2007040)
FITS = ("p30", "p31_34")
CONDITIONS = {
    "NOMINAL": None,
    "TORSO_COM_X_NEG": [-0.05, 0.0, 0.0],
    "TORSO_COM_X_POS": [0.05, 0.0, 0.0],
}
SEED = 167931544


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1e-12)


def readback_exact(report: dict, expected: list[float]) -> bool:
    readback = report.get("readback")
    if not (report.get("enabled") is True and report.get("key") == "torso_com_offset_m" and report.get("value") == expected and isinstance(readback, dict)):
        return False
    before, after = readback.get("before"), readback.get("after")
    return bool(
        readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and close(readback.get("body_mass_kg"), 0.6985260248184204)
        and isinstance(before, list) and isinstance(after, list)
        and len(before) == len(after) == 3
        and all(close(after[index], before[index] + expected[index]) for index in range(3))
    )


def moving_cell_pass(row: dict) -> bool:
    return bool(
        row["samples"] == 600
        and row["termination_reason"] == "duration_complete"
        and row["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE"
        and row["emergence_pass"]
        and row["left_transitions"] > 0 and row["right_transitions"] > 0
        and row["tracking_p95"] <= 0.20
        and row["saturation_pct"] == 0.0
        and row["rate_excess"] == 0.0 and row["max_rate_excess"] == 0.0
    )


def matrix(path: Path, override: list[float] | None, x0_gate: dict, policy: dict, fit_path: Path, reference: Path) -> dict:
    payload = json.loads(path.read_text())
    item = summarize(path, x0_gate, SEED)
    inputs = payload["inputs"]
    item["policy_hash_exact"] = inputs.get("policy_sha256") == policy["output_sha256"] and inputs.get("policy") == policy["output_path"]
    item["cpu_contract_exact"] = payload.get("execution") == {"platform": "cpu", "cuda_visible_devices": "", "jax_platforms": "cpu"}
    item["evaluation_config_exact"] = bool(
        inputs.get("commands") == [0.0, 0.074, 0.077, 0.08]
        and inputs.get("seeds") == [SEED]
        and inputs.get("duration_s") == 12.0
        and inputs.get("minimum_emergence_duration_s") == 1.08
        and inputs.get("task") == "flat_terrain_backlash"
        and inputs.get("reset_mode") == "home-support"
        and inputs.get("expected_observation_dim") == 116
        and inputs.get("policy_state_input_names") == ["previous_action"]
        and inputs.get("policy_state_output_names") == ["previous_action_out"]
        and inputs.get("policy_applied_target_observation") is True
        and inputs.get("policy_reset_com_estimator_input") is True
        and inputs.get("reference_start_phase") == 0
        and inputs.get("fit") == str(fit_path.resolve())
        and inputs.get("fit_sha256") == sha256(fit_path)
        and inputs.get("reference_feature_table") == str(reference.resolve())
        and inputs.get("reference_feature_table_sha256") == sha256(reference)
    )
    if override is None:
        item["override_and_all_readbacks_exact"] = inputs.get("eval_dynamics_override") is None and all(run.get("dynamics_override", {}).get("enabled") is False for run in payload["runs"])
    else:
        item["override_and_all_readbacks_exact"] = inputs.get("eval_dynamics_override") == {"torso_com_offset_m": override} and len(payload["runs"]) == 4 and all(readback_exact(run.get("dynamics_override") or {}, override) for run in payload["runs"])
    item["matrix_pass"] = bool(item["matrix_pass"] and item["policy_hash_exact"] and item["cpu_contract_exact"] and item["evaluation_config_exact"] and item["override_and_all_readbacks_exact"])
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--arm-preregistration", type=Path, required=True)
    parser.add_argument("--evaluator-preregistration", type=Path, required=True)
    parser.add_argument("--artifact-contract", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--evaluator-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--condition-md-root", type=Path, required=True)
    args = parser.parse_args()

    arm_text = args.arm_preregistration.read_text()
    evaluator_text = args.evaluator_preregistration.read_text()
    artifact = json.loads(args.artifact_contract.read_text())
    transform = json.loads(args.transform_contract.read_text())
    evaluator = json.loads(args.evaluator_contract.read_text())
    selected = {int(row["step"]): row for row in transform["policies"]}
    analysis = args.eval_root.parent
    reference = analysis / "ground_up_projected_reference_feature_table.npz"
    x0_gate = {
        "samples": 600, "termination_reason": "duration_complete",
        "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
        "maximum_absolute_mean_local_velocity_m_s": 0.02,
        "maximum_body_pitch_p95_rad": 0.25, "minimum_base_height_m": 0.12,
        "maximum_pitch_tracking_p95_rad": 0.20,
        "maximum_action_saturation_pct": 0.0, "maximum_rate_excess_rad_s": 0.0,
    }
    matrices = {}
    for condition, override in CONDITIONS.items():
        matrices[condition] = {}
        for step in STEPS:
            matrices[condition][str(step)] = {}
            for fit in FITS:
                path = args.eval_root / f"{condition}_RESET_EST_LATCH_U05_{step}_{fit}.json"
                fit_path = analysis / f"fixed_target_{fit}_actuator_fit_20260712.json"
                matrices[condition][str(step)][fit] = matrix(path, override, x0_gate, selected[step], fit_path, reference)

    flat = [matrices[c][str(s)][f] for c in CONDITIONS for s in STEPS for f in FITS]
    checks = {
        "frozen_arm_selection_rule_present": all(fragment in arm_text for fragment in ("## Frozen eventual behavior evaluation", "both full-range checkpoints must pass every", "Training reward is never used for selection")),
        "frozen_behavior_authority_present": all(fragment in evaluator_text for fragment in ("## Frozen behavior matrix", "12 matrices / 48 cells", "both checkpoints pass all 48 cells")),
        "artifact_contract_passed": artifact.get("status") == "PASS_RESET_ESTIMATOR_HOSTED_ARTIFACT_CONTRACT",
        "transform_contract_passed": transform.get("status") == "PASS_RESET_ESTIMATOR_EVAL_POLICY_TRANSFORM_CONTRACT",
        "corrected_evaluator_contract_passed": evaluator.get("status") == "PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CONTRACT" and evaluator.get("execution") == {"formal_behavior_cells": 0, "platform": "cpu", "policy_steps": 0},
        "exact_two_selected_policies": set(selected) == set(STEPS) and len(selected) == 2,
        "all_48_cells_present": len(flat) == 12 and all(item["complete"] for item in flat),
        "all_cpu_only": all(item["execution_platform"] == "cpu" and item["cpu_contract_exact"] for item in flat),
        "all_policy_hashes_exact": all(item["policy_hash_exact"] for item in flat),
        "all_evaluation_configs_exact": all(item["evaluation_config_exact"] for item in flat),
        "all_override_and_per_run_readbacks_exact": all(item["override_and_all_readbacks_exact"] for item in flat),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    cells_passed = sum(int(item["x0"] is not None and item["x0"].get("pass", False)) + sum(moving_cell_pass(row) for row in item["moving"]) for item in flat)
    arm_pass = not failed and all(item["matrix_pass"] for item in flat)
    if failed:
        status, decision = "FAIL_RESET_ESTIMATOR_BEHAVIOR_EVIDENCE_CONTRACT", "INVALID_EVIDENCE"
    elif arm_pass:
        status, decision = "PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATION", "SELECT_RESET_EST_LATCH_U05_FOR_SEPARATE_NEXT_PREREGISTRATION"
    else:
        status, decision = "PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATION_NO_ADVANCE", "CLOSE_RESET_EST_LATCH_U05_NO_PASS"
    result = {
        "schema_version": "ground_up_reset_com_estimator_behavior_decision.v1",
        "status": status, "decision": decision, "selected_arm": "RESET_EST_LATCH_U05" if arm_pass else None,
        "checks": checks, "failed_checks": failed,
        "arm_result": {
            "pass": arm_pass, "matrices_passed": sum(item["matrix_pass"] for item in flat),
            "matrices_total": 12, "cells_passed": cells_passed, "cells_total": 48,
            "worst_endpoint_tracking_p95_rad": max(matrices[c][str(s)][f]["worst_nominal_tracking_p95_rad"] for c in ("TORSO_COM_X_NEG", "TORSO_COM_X_POS") for s in STEPS for f in FITS),
            "minimum_endpoint_mean_vx_m_s": min(matrices[c][str(s)][f]["minimum_nominal_vx_m_s"] for c in ("TORSO_COM_X_NEG", "TORSO_COM_X_POS") for s in STEPS for f in FITS),
            "worst_nominal_tracking_p95_rad": max(matrices["NOMINAL"][str(s)][f]["worst_nominal_tracking_p95_rad"] for s in STEPS for f in FITS),
        },
        "matrices": matrices, "selection_uses_training_reward": False,
        "authority": {"separate_preregistration_required_for_any_next_step": True, "training": False, "colab": False, "runtime_design": False, "local_gpu_or_igpu": False, "rdk_or_robot": False},
    }
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    args.condition_md_root.mkdir(parents=True, exist_ok=True)
    for condition in CONDITIONS:
        lines = [f"# Ground-Up Reset-Estimator {condition} Result", "", "execution: `CPU_ONLY`", "", "| step | fit | x=0 | moving | worst tracking | min vx | readback | pass |", "|---:|---|---|---|---:|---:|---|---|"]
        for step in STEPS:
            for fit in FITS:
                item = matrices[condition][str(step)][fit]
                lines.append(f"| {step} | `{fit}` | `{item['x0_pass']}` | `{item['nominal_pass']}` | {item['worst_nominal_tracking_p95_rad']:.9f} | {item['minimum_nominal_vx_m_s']:.9f} | `{item['override_and_all_readbacks_exact']}` | `{item['matrix_pass']}` |")
        lines.extend(["", "This is frozen selection evidence only; it is not robot clearance.", ""])
        (args.condition_md_root / f"GROUND_UP_TORSO_COM_RESET_ESTIMATOR_{condition}_RESULT_20260715.md").write_text("\n".join(lines))

    arm = result["arm_result"]
    lines = ["# Ground-Up Torso-COM Reset-Estimator Behavior Decision", "", f"status: `{status}`", f"decision: `{decision}`", f"selected arm: `{'RESET_EST_LATCH_U05' if arm_pass else 'NONE'}`", "training reward used for selection: `False`", "", "| arm | matrices | cells | endpoint tracking worst | endpoint min vx | nominal tracking worst | pass |", "|---|---:|---:|---:|---:|---:|---|", f"| `RESET_EST_LATCH_U05` | {arm['matrices_passed']}/12 | {arm['cells_passed']}/48 | {arm['worst_endpoint_tracking_p95_rad']:.9f} | {arm['minimum_endpoint_mean_vx_m_s']:.9f} | {arm['worst_nominal_tracking_p95_rad']:.9f} | `{arm_pass}` |", ""]
    lines.append("Both checkpoints do not pass every frozen cell; the reset-estimator arm is closed without retry or closest-checkpoint promotion." if not arm_pass else "The arm passes this frozen evaluation only; any continuation requires a separate preregistration.")
    lines.extend(["Training, Colab, runtime design, GPU/iGPU, RDK-X5, and robot access remain unauthorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "arm_pass": arm_pass, "cells_passed": cells_passed}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
