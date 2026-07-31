#!/usr/bin/env python3
"""Aggregate the preregistered dual-fit conservative-envelope repair."""

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    contract = json.loads(args.transform_contract.read_text())
    seed = prereg["behavior_matrix"]["seeds"][0]
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
    matrices = {
        fit: {
            str(step): summarize(
                args.eval_root / f"ground_up_dual_fit_conservative_envelope_{fit}_T2_EQUAL_{step}_eval.json",
                x0_gate,
                seed,
            ) for step in STEPS
        } for fit in FITS
    }
    flat = [item for fit in matrices.values() for item in fit.values()]
    checks = {
        "preregistration_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "transform_contract_passed": contract["status"] == "PASS_DUAL_FIT_CONSERVATIVE_ENVELOPE_TRANSFORM_CONTRACT",
        "all_16_cells_present": len(flat) == 4 and all(item["complete"] for item in flat),
        "all_cpu_only": all(item["execution_platform"] == "cpu" for item in flat),
    }
    failed = [key for key, value in checks.items() if not value]
    repair_pass = not failed and all(item["matrix_pass"] for item in flat)
    if failed:
        status, decision = "FAIL_DUAL_FIT_CONSERVATIVE_ENVELOPE_EVIDENCE_CONTRACT", "INVALID_EVIDENCE"
    elif repair_pass:
        status, decision = "PASS_DUAL_FIT_CONSERVATIVE_ENVELOPE_REPAIR", "REENTER_R1_PASS_AND_AUTHORIZE_R2_CONTRACT_ONLY"
    else:
        status, decision = "PASS_DUAL_FIT_CONSERVATIVE_ENVELOPE_NO_ADVANCE", "CLOSE_REPAIR_AND_PREREGISTER_DUAL_FIT_TRAINING_SEARCH"
    payload = {
        "schema_version": "ground_up_dual_fit_conservative_envelope_repair_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "repair_pass": repair_pass,
        "matrices": matrices,
        "preregistration": {"path": str(args.preregistration.resolve()), "sha256": sha256(args.preregistration)},
        "transform_contract": {"path": str(args.transform_contract.resolve()), "sha256": sha256(args.transform_contract)},
        "authority": {
            "contract_r2": repair_pass,
            "run_r2_before_contract": False,
            "run_r3_or_later": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
        "interpretation": (
            "The componentwise conservative measured envelope removes the P31/34 left-ankle violation while preserving both checkpoints under both hardware fits."
            if repair_pass else
            "The single conservative left-ankle bound does not preserve the complete dual-fit R1 gate."
        ),
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Dual-Fit Conservative-Envelope Repair Result", "", f"status: `{status}`", f"decision: `{decision}`", "", "| fit | step | x=0 | nominal | worst tracking | min vx | pass |", "|---|---:|---|---|---:|---:|---|"]
    for fit, steps in matrices.items():
        for step, item in steps.items():
            lines.append(f"| `{fit}` | {step} | `{item['x0_pass']}` | `{item['nominal_pass']}` | {item['worst_nominal_tracking_p95_rad']:.9f} | {item['minimum_nominal_vx_m_s']:.9f} | `{item['matrix_pass']}` |")
    lines.extend(["", payload["interpretation"], "", "Passing authorizes only the R2 evaluator contract. It does not authorize R2 behavior, training, RDK-X5, or robot access.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "repair_pass": repair_pass}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
