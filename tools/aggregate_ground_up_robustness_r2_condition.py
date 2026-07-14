#!/usr/bin/env python3
"""Aggregate one strictly ordered R2 isolated-dynamics condition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aggregate_ground_up_robustness_r1 import summarize


STEPS = (512000, 1024000)
FITS = ("p30", "p31_34")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value_matches(key: str, expected, actual) -> bool:
    if key == "joint_qpos0_offset_rad" and isinstance(expected, (int, float)):
        return isinstance(actual, list) and len(actual) == 14 and all(float(item) == float(expected) for item in actual)
    return actual == expected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition-id", required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--evaluator-contract", type=Path, required=True)
    parser.add_argument("--reporting-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    evaluator_contract = json.loads(args.evaluator_contract.read_text())
    reporting_contract = json.loads(args.reporting_contract.read_text())
    condition_index = next(
        index for index, item in enumerate(prereg["conditions_in_strict_order"])
        if item["id"] == args.condition_id
    )
    condition = prereg["conditions_in_strict_order"][condition_index]
    key, expected_value = next(iter(condition["override"].items()))
    seed = prereg["seeds"][0]
    x0_gate = {
        "samples": 600, "termination_reason": "duration_complete",
        "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
        "maximum_absolute_mean_local_velocity_m_s": 0.02,
        "maximum_body_pitch_p95_rad": 0.25, "minimum_base_height_m": 0.12,
        "maximum_pitch_tracking_p95_rad": 0.20,
        "maximum_action_saturation_pct": 0.0, "maximum_rate_excess_rad_s": 0.0,
    }
    matrices = {}
    evidence_rows = []
    for fit in FITS:
        matrices[fit] = {}
        for step in STEPS:
            path = args.eval_root / f"ground_up_robustness_r2_{args.condition_id}_{fit}_T2_EQUAL_{step}_eval.json"
            payload = json.loads(path.read_text())
            report_ok = payload["inputs"].get("eval_dynamics_override") == condition["override"]
            reports = []
            for run in payload["runs"]:
                report = run.get("dynamics_override") or {}
                run_ok = (
                    report.get("enabled") is True
                    and report.get("key") == key
                    and value_matches(key, expected_value, report.get("value"))
                    and isinstance(report.get("readback"), dict)
                    and bool(report["readback"])
                )
                reports.append(run_ok)
            report_ok = report_ok and len(reports) == 4 and all(reports)
            summary = summarize(path, x0_gate, seed)
            summary["override_and_all_readbacks_exact"] = report_ok
            summary["matrix_pass"] = summary["matrix_pass"] and report_ok
            matrices[fit][str(step)] = summary
            evidence_rows.append(summary)
    checks = {
        "preregistration_valid": prereg["status"] == "PREREGISTERED_CONTRACT_REQUIRED_CPU_ONLY",
        "evaluator_contract_passed": evaluator_contract["status"] == "PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT",
        "reporting_contract_passed": reporting_contract["status"] == "PASS_ROBUSTNESS_R2_REPORTING_CONTRACT",
        "condition_in_frozen_order": prereg["conditions_in_strict_order"][condition_index]["id"] == args.condition_id,
        "all_16_cells_present": len(evidence_rows) == 4 and all(item["complete"] for item in evidence_rows),
        "all_cpu_only": all(item["execution_platform"] == "cpu" for item in evidence_rows),
        "all_requested_overrides_and_readbacks_exact": all(item["override_and_all_readbacks_exact"] for item in evidence_rows),
    }
    failed = [name for name, passed in checks.items() if not passed]
    condition_pass = not failed and all(item["matrix_pass"] for item in evidence_rows)
    next_condition = (
        prereg["conditions_in_strict_order"][condition_index + 1]["id"]
        if condition_index + 1 < len(prereg["conditions_in_strict_order"])
        else None
    )
    if failed:
        status, decision = "FAIL_ROBUSTNESS_R2_CONDITION_EVIDENCE_CONTRACT", "INVALID_EVIDENCE"
    elif condition_pass and next_condition:
        status, decision = "PASS_ROBUSTNESS_R2_CONDITION", f"AUTHORIZE_{next_condition}_ONLY"
    elif condition_pass:
        status, decision = "PASS_ROBUSTNESS_R2_COMPLETE", "AUTHORIZE_R3_CONTRACT_ONLY"
    else:
        status, decision = "PASS_ROBUSTNESS_R2_CONDITION_NO_ADVANCE", "STOP_R2_AT_FIRST_FAILED_CONDITION"
    payload = {
        "schema_version": "ground_up_robustness_r2_condition_result.v1",
        "status": status, "decision": decision, "condition_id": args.condition_id,
        "condition_index": condition_index, "condition": condition,
        "checks": checks, "failed_checks": failed, "condition_pass": condition_pass,
        "next_condition": next_condition if condition_pass else None,
        "matrices": matrices,
        "authority": {
            "run_next_condition": condition_pass and next_condition is not None,
            "run_r3_contract": condition_pass and next_condition is None,
            "training": False, "colab": False, "local_gpu": False, "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Robustness R2 Condition Result", "", f"condition: `{args.condition_id}`", f"status: `{status}`", f"decision: `{decision}`", "", "| fit | step | x=0 | nominal | tracking | min vx | readback | pass |", "|---|---:|---|---|---:|---:|---|---|"]
    for fit, steps in matrices.items():
        for step, item in steps.items():
            lines.append(f"| `{fit}` | {step} | `{item['x0_pass']}` | `{item['nominal_pass']}` | {item['worst_nominal_tracking_p95_rad']:.9f} | {item['minimum_nominal_vx_m_s']:.9f} | `{item['override_and_all_readbacks_exact']}` | `{item['matrix_pass']}` |")
    lines.extend(["", "Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "condition_pass": condition_pass}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
