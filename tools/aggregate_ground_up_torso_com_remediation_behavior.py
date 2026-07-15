#!/usr/bin/env python3
"""Aggregate the frozen torso-COM remediation behavior evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from aggregate_ground_up_robustness_r1 import summarize


ARMS = {
    "U_CURRICULUM": (512000, 1024000),
    "A05_DIRECT": (1003520, 2007040),
    "U05_DIRECT": (1003520, 2007040),
}
FITS = ("p30", "p31_34")
CONDITIONS = {
    "NOMINAL": None,
    "TORSO_COM_X_NEG": [-0.05, 0.0, 0.0],
    "TORSO_COM_X_POS": [0.05, 0.0, 0.0],
}
TIEBREAK = ("U_CURRICULUM", "A05_DIRECT", "U05_DIRECT")
SEED = 167931544


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, tolerance: float = 1.0e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tolerance)


def readback_exact(report: dict, expected: list[float]) -> bool:
    if not (
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == expected
    ):
        return False
    readback = report.get("readback")
    if not isinstance(readback, dict):
        return False
    before = readback.get("before")
    after = readback.get("after")
    if not (
        readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and close(readback.get("body_mass_kg"), 0.6985260248184204)
        and isinstance(before, list)
        and isinstance(after, list)
        and len(before) == len(after) == 3
    ):
        return False
    return all(close(after[i], before[i] + expected[i]) for i in range(3))


def matrix(
    path: Path,
    expected_override: list[float] | None,
    x0_gate: dict,
    expected_policy_sha: str,
    expected_policy_path: str,
    expected_fit_path: Path,
    expected_reference_path: Path,
) -> dict:
    payload = json.loads(path.read_text())
    summary = summarize(path, x0_gate, SEED)
    policy_exact = (
        payload["inputs"].get("policy_sha256") == expected_policy_sha
        and payload["inputs"].get("policy") == expected_policy_path
    )
    inputs = payload["inputs"]
    cpu_exact = (
        payload.get("execution", {}).get("platform") == "cpu"
        and payload.get("execution", {}).get("jax_platforms") == "cpu"
        and payload.get("execution", {}).get("cuda_visible_devices") == ""
    )
    config_exact = (
        inputs.get("commands") == [0.0, 0.074, 0.077, 0.08]
        and inputs.get("seeds") == [SEED]
        and inputs.get("duration_s") == 12.0
        and inputs.get("minimum_emergence_duration_s") == 1.08
        and inputs.get("reset_mode") == "home-support"
        and inputs.get("task") == "flat_terrain_backlash"
        and inputs.get("expected_observation_dim") == 115
        and inputs.get("policy_state_input_names") == ["previous_action"]
        and inputs.get("policy_state_output_names") == ["previous_action_out"]
        and inputs.get("policy_applied_target_observation") is True
        and inputs.get("fit") == str(expected_fit_path.resolve())
        and inputs.get("fit_sha256") == sha256(expected_fit_path)
        and inputs.get("reference_feature_table") == str(expected_reference_path.resolve())
        and inputs.get("reference_feature_table_sha256") == sha256(expected_reference_path)
        and inputs.get("reference_start_phase") == 0
    )
    if expected_override is None:
        readback_ok = (
            payload["inputs"].get("eval_dynamics_override") is None
            and all(run.get("dynamics_override", {}).get("enabled") is False for run in payload["runs"])
        )
    else:
        requested = {"torso_com_offset_m": expected_override}
        readback_ok = (
            payload["inputs"].get("eval_dynamics_override") == requested
            and len(payload["runs"]) == 4
            and all(readback_exact(run.get("dynamics_override") or {}, expected_override) for run in payload["runs"])
        )
    summary["policy_hash_exact"] = policy_exact
    summary["cpu_contract_exact"] = cpu_exact
    summary["evaluation_config_exact"] = config_exact
    summary["override_and_all_readbacks_exact"] = readback_ok
    summary["matrix_pass"] = (
        summary["matrix_pass"]
        and policy_exact
        and cpu_exact
        and config_exact
        and readback_ok
    )
    return summary


def condition_markdown(condition: str, arms: dict) -> str:
    lines = [
        f"# Ground-Up Torso-COM Remediation {condition} Result",
        "",
        f"condition: `{condition}`",
        "execution: `CPU_ONLY`",
        "",
        "| arm | step | fit | x=0 | moving | worst tracking | min vx | readback | pass |",
        "|---|---:|---|---|---|---:|---:|---|---|",
    ]
    for arm in TIEBREAK:
        for step in ARMS[arm]:
            for fit in FITS:
                item = arms[arm][str(step)][fit]
                lines.append(
                    f"| `{arm}` | {step} | `{fit}` | `{item['x0_pass']}` | "
                    f"`{item['nominal_pass']}` | {item['worst_nominal_tracking_p95_rad']:.9f} | "
                    f"{item['minimum_nominal_vx_m_s']:.9f} | "
                    f"`{item['override_and_all_readbacks_exact']}` | `{item['matrix_pass']}` |"
                )
    condition_pass = all(
        arms[arm][str(step)][fit]["matrix_pass"]
        for arm in TIEBREAK for step in ARMS[arm] for fit in FITS
    )
    lines.extend([
        "",
        f"condition complete pass: `{condition_pass}`",
        "",
        "This result is evidence for the frozen remediation selection only. It does not authorize R2 resumption, R3+, training, runtime work, RDK-X5, or robot access.",
        "",
    ])
    return "\n".join(lines)


def moving_cell_pass(row: dict) -> bool:
    return (
        row["samples"] == 600
        and row["termination_reason"] == "duration_complete"
        and row["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE"
        and row["emergence_pass"]
        and row["left_transitions"] > 0
        and row["right_transitions"] > 0
        and row["tracking_p95"] <= 0.20
        and row["saturation_pct"] == 0.0
        and row["rate_excess"] == 0.0
        and row["max_rate_excess"] == 0.0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--artifact-contract", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--evaluator-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--condition-md-root", type=Path, required=True)
    args = parser.parse_args()

    prereg_text = args.preregistration.read_text()
    artifact = json.loads(args.artifact_contract.read_text())
    transform = json.loads(args.transform_contract.read_text())
    evaluator = json.loads(args.evaluator_contract.read_text())
    selected = {(item["arm"], int(item["step"])): item for item in transform["policies"]}
    analysis_root = args.eval_root.parent
    reference_path = analysis_root / "ground_up_projected_reference_feature_table.npz"
    x0_gate = {
        "samples": 600,
        "termination_reason": "duration_complete",
        "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
        "maximum_absolute_mean_local_velocity_m_s": 0.02,
        "maximum_body_pitch_p95_rad": 0.25,
        "minimum_base_height_m": 0.12,
        "maximum_pitch_tracking_p95_rad": 0.20,
        "maximum_action_saturation_pct": 0.0,
        "maximum_rate_excess_rad_s": 0.0,
    }

    matrices: dict[str, dict] = {}
    for condition, override in CONDITIONS.items():
        matrices[condition] = {}
        for arm in TIEBREAK:
            matrices[condition][arm] = {}
            for step in ARMS[arm]:
                matrices[condition][arm][str(step)] = {}
                expected_sha = selected[(arm, step)]["output_sha256"]
                expected_path = selected[(arm, step)]["output_path"]
                for fit in FITS:
                    path = args.eval_root / f"{condition}_{arm}_{step}_{fit}.json"
                    fit_path = analysis_root / f"fixed_target_{fit}_actuator_fit_20260712.json"
                    matrices[condition][arm][str(step)][fit] = matrix(
                        path,
                        override,
                        x0_gate,
                        expected_sha,
                        expected_path,
                        fit_path,
                        reference_path,
                    )

    flat = [
        matrices[condition][arm][str(step)][fit]
        for condition in CONDITIONS
        for arm in TIEBREAK
        for step in ARMS[arm]
        for fit in FITS
    ]
    evaluator_conditions = {item["id"]: item for item in evaluator.get("conditions", [])}
    xpos_contract = evaluator_conditions.get("TORSO_COM_X_POS", {})
    xneg_contract = evaluator_conditions.get("TORSO_COM_X_NEG", {})
    checks = {
        "frozen_preregistration_text_present": all(
            text in prereg_text
            for text in (
                "## Frozen evaluation and selection",
                "TORSO_COM_X_NEG",
                "TORSO_COM_X_POS",
                "Training reward is never used",
            )
        ),
        "artifact_contract_passed": artifact.get("status") == "PASS_TORSO_COM_COLAB_ARTIFACT_CONTRACT",
        "transform_contract_passed": transform.get("status") == "PASS_TORSO_COM_EVAL_POLICY_TRANSFORM_CONTRACT",
        "r2_evaluator_contract_passed": evaluator.get("status") == "PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT",
        "evaluator_default_off_model_and_600_tick_behavior_exact": (
            evaluator.get("checks", {}).get("default_off_model_exact") is True
            and evaluator.get("checks", {}).get("default_off_600_tick_behavior_exact") is True
        ),
        "xneg_one_axis_body_ipos_contract_exact": (
            xneg_contract.get("override") == {"torso_com_offset_m": [-0.05, 0.0, 0.0]}
            and xneg_contract.get("changed_model_fields") == ["body_ipos"]
            and xneg_contract.get("only_intended_fields_changed") is True
        ),
        "xpos_one_axis_body_ipos_contract_exact": (
            xpos_contract.get("override") == {"torso_com_offset_m": [0.05, 0.0, 0.0]}
            and xpos_contract.get("changed_model_fields") == ["body_ipos"]
            and xpos_contract.get("only_intended_fields_changed") is True
        ),
        "exact_six_selected_policies": len(selected) == 6 and set(selected) == {
            (arm, step) for arm in TIEBREAK for step in ARMS[arm]
        },
        "all_144_cells_present": len(flat) == 36 and all(item["complete"] for item in flat),
        "all_cpu_only": all(
            item["execution_platform"] == "cpu" and item["cpu_contract_exact"]
            for item in flat
        ),
        "all_policy_hashes_exact": all(item["policy_hash_exact"] for item in flat),
        "all_evaluation_configs_exact": all(item["evaluation_config_exact"] for item in flat),
        "all_override_and_readback_contracts_exact": all(
            item["override_and_all_readbacks_exact"] for item in flat
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    arm_results = {}
    for arm in TIEBREAK:
        arm_matrices = [
            matrices[condition][arm][str(step)][fit]
            for condition in CONDITIONS for step in ARMS[arm] for fit in FITS
        ]
        endpoints = [
            matrices[condition][arm][str(step)][fit]
            for condition in ("TORSO_COM_X_NEG", "TORSO_COM_X_POS")
            for step in ARMS[arm] for fit in FITS
        ]
        nominal = [
            matrices["NOMINAL"][arm][str(step)][fit]
            for step in ARMS[arm] for fit in FITS
        ]
        passes = not failed_checks and all(item["matrix_pass"] for item in arm_matrices)
        arm_results[arm] = {
            "pass": passes,
            "matrices_passed": sum(item["matrix_pass"] for item in arm_matrices),
            "matrices_total": len(arm_matrices),
            "cells_passed": sum(
                int(item["x0"] is not None and item["x0"].get("pass", False))
                + sum(moving_cell_pass(row) for row in item["moving"])
                for item in arm_matrices
            ),
            "cells_total": 48,
            "worst_endpoint_tracking_p95_rad": max(
                item["worst_nominal_tracking_p95_rad"] for item in endpoints
            ),
            "minimum_endpoint_mean_vx_m_s": min(
                item["minimum_nominal_vx_m_s"] for item in endpoints
            ),
            "worst_nominal_tracking_p95_rad": max(
                item["worst_nominal_tracking_p95_rad"] for item in nominal
            ),
        }

    advancing = [arm for arm in TIEBREAK if arm_results[arm]["pass"]]
    ranking = sorted(
        advancing,
        key=lambda arm: (
            arm_results[arm]["worst_endpoint_tracking_p95_rad"],
            -arm_results[arm]["minimum_endpoint_mean_vx_m_s"],
            arm_results[arm]["worst_nominal_tracking_p95_rad"],
            TIEBREAK.index(arm),
        ),
    )
    selected_arm = ranking[0] if ranking else None
    if failed_checks:
        status = "FAIL_TORSO_COM_REMEDIATION_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
    elif selected_arm is None:
        status = "PASS_TORSO_COM_REMEDIATION_EVALUATION_NO_ARM_ADVANCES"
        decision = "CLOSE_EXACT_TARGETED_COM_FORMULATION_NO_WINNER"
    else:
        status = "PASS_TORSO_COM_REMEDIATION_EVALUATION"
        decision = f"SELECT_{selected_arm}_FOR_SEPARATE_NEXT_PREREGISTRATION"

    payload = {
        "schema_version": "ground_up_torso_com_remediation_behavior_decision.v1",
        "status": status,
        "decision": decision,
        "selected_arm": selected_arm,
        "advancing_arms_ranked": ranking,
        "preregistration": {
            "path": str(args.preregistration.resolve()),
            "sha256": sha256(args.preregistration),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "arm_results": arm_results,
        "matrices": matrices,
        "selection_uses_training_reward": False,
        "authority": {
            "separate_preregistration_required_for_any_next_step": True,
            "resume_r2_condition_8_or_later": False,
            "run_r3_or_later": False,
            "training": False,
            "colab": False,
            "runtime_design": False,
            "local_gpu_or_igpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    args.condition_md_root.mkdir(parents=True, exist_ok=True)
    for condition in CONDITIONS:
        name = f"GROUND_UP_TORSO_COM_REMEDIATION_{condition}_RESULT_20260715.md"
        (args.condition_md_root / name).write_text(
            condition_markdown(condition, matrices[condition])
        )

    lines = [
        "# Ground-Up Torso-COM Remediation Behavior Decision",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        f"selected arm: `{'NONE' if selected_arm is None else selected_arm}`",
        "training reward used for selection: `False`",
        "",
        "| arm | matrices | cells | endpoint tracking worst | endpoint min vx | nominal tracking worst | pass |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for arm in TIEBREAK:
        item = arm_results[arm]
        lines.append(
            f"| `{arm}` | {item['matrices_passed']}/{item['matrices_total']} | "
            f"{item['cells_passed']}/{item['cells_total']} | "
            f"{item['worst_endpoint_tracking_p95_rad']:.9f} | "
            f"{item['minimum_endpoint_mean_vx_m_s']:.9f} | "
            f"{item['worst_nominal_tracking_p95_rad']:.9f} | `{item['pass']}` |"
        )
    lines.append("")
    if selected_arm is None:
        lines.append(
            "No arm passes both checkpoints across every frozen cell. The exact "
            "targeted-COM formulation is closed without promoting a closest arm."
        )
    else:
        lines.append(
            "Selection is limited to the frozen evaluation and is not robot clearance."
        )
    lines.extend([
        "R2 resumption, R3+, training, runtime design, RDK-X5, and robot access remain unauthorized. Every next step requires a separate preregistration.",
        "",
    ])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "selected_arm": selected_arm}))
    return 1 if failed_checks else 0


if __name__ == "__main__":
    raise SystemExit(main())
