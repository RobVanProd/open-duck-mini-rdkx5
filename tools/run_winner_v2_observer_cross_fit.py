#!/usr/bin/env python3
"""Run the preregistered 32-cell winner-v2 observer cross-fit matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from aggregate_ground_up_robustness_r1 import summarize
from evaluate_ground_up_policy import evaluate, write_markdown


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
OUT = ROOT / "outputs/analysis/winner_v2_observer_cross_fit"
TRACE_ROOT = OUT / "traces"
PREREG = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_preregistration.json"
CONTRACT = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_default_off_contract.json"
POLICIES = {
    512000: ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    1024000: ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
}
FITS = {
    "p30": ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
SEED = 167931544
COMMANDS = (0.0, 0.074, 0.077, 0.080)
X0_GATE = {
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def eval_args(
    policy: Path, plant_fit: Path, observer_fit: Path, trace_dir: Path
) -> argparse.Namespace:
    return argparse.Namespace(
        policy=str(policy),
        playground_root=str(PLAYGROUND),
        fit=str(plant_fit),
        policy_observer_fit=str(observer_fit),
        reference_feature_table=str(REFERENCE),
        reference_start_phase=0,
        expected_observation_dim=115,
        policy_state_input_names="previous_action",
        policy_state_output_names="previous_action_out",
        policy_applied_target_observation=True,
        policy_reset_com_estimator_input=False,
        trace_dir=trace_dir,
        trace_full_obs=False,
        trace_com_accelerometer_map_ticks="",
        commands=",".join(str(value) for value in COMMANDS),
        seeds=str(SEED),
        duration_s=12.0,
        minimum_emergence_duration_s=1.08,
        task="flat_terrain_backlash",
        eval_dynamics_override_json=None,
        reset_mode="home-support",
        policy_action_rate_limit_rad_s=None,
        policy_action_rate_limit_joint_indices="2,3,4,11,12,13",
        policy_action_rate_limit_values="",
    )


def trace_audit(trace_path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in trace_path.read_text().splitlines() if line]
    max_separation = 0.0
    finite = True
    contiguous = True
    for index, row in enumerate(rows):
        contiguous &= int(row["tick"]) == index
        plant = np.asarray(row["applied_target_rad"], dtype=float)
        observer = np.asarray(row["policy_observer_applied_target_rad"], dtype=float)
        finite &= bool(
            plant.shape == (14,)
            and observer.shape == (14,)
            and np.all(np.isfinite(plant))
            and np.all(np.isfinite(observer))
        )
        max_separation = max(max_separation, float(np.max(np.abs(plant - observer))))
    return {
        "path": str(trace_path.relative_to(ROOT)),
        "sha256": sha256(trace_path),
        "rows": len(rows),
        "ticks_contiguous": contiguous,
        "finite_14d_bridge_fields": finite,
        "max_plant_observer_separation_rad": max_separation,
    }


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    contract = json.loads(CONTRACT.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    matrices: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []

    for observer_name, observer_fit in FITS.items():
        for plant_name, plant_fit in FITS.items():
            for step, policy in POLICIES.items():
                stem = f"observer_{observer_name}_plant_{plant_name}_T2_EQUAL_{step}"
                trace_dir = TRACE_ROOT / stem
                trace_dir.mkdir(parents=True, exist_ok=True)
                payload = evaluate(eval_args(policy, plant_fit, observer_fit, trace_dir))
                output_json = OUT / f"{stem}.json"
                output_md = OUT / f"{stem}.md"
                output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
                write_markdown(payload, output_md)
                summary = summarize(output_json, X0_GATE, SEED)
                run_contracts = []
                for run in payload["runs"]:
                    trace_path = Path(run["trace_jsonl"])
                    audit = trace_audit(trace_path)
                    trace_rows.append(audit)
                    run_contracts.append(
                        run.get("policy_observer_fit_enabled") is True
                        and run.get("policy_observer_fit_sha256") == sha256(observer_fit)
                        and audit["ticks_contiguous"]
                        and audit["finite_14d_bridge_fields"]
                    )
                matrices.append(
                    {
                        "observer_fit": observer_name,
                        "observer_fit_sha256": sha256(observer_fit),
                        "plant_fit": plant_name,
                        "plant_fit_sha256": sha256(plant_fit),
                        "step": step,
                        "policy_sha256": sha256(policy),
                        "eval_json": str(output_json.relative_to(ROOT)),
                        "eval_json_sha256": sha256(output_json),
                        "summary": summary,
                        "run_contracts_pass": all(run_contracts),
                    }
                )

    p30 = [row for row in matrices if row["observer_fit"] == "p30"]
    p31 = [row for row in matrices if row["observer_fit"] == "p31_34"]
    evidence_checks = {
        "preregistration_exact": prereg["status"]
        == "PREREGISTERED_BEFORE_EVALUATOR_CHANGE_AND_OUTCOMES"
        and prereg["matrix"]["cells"] == 32,
        "default_off_contract_passed": contract["status"]
        == "PASS_WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT",
        "all_eight_matrices_present": len(matrices) == 8,
        "all_32_cells_present": all(row["summary"]["complete"] for row in matrices),
        "all_run_contracts_pass": all(row["run_contracts_pass"] for row in matrices),
        "all_cpu_only": all(
            json.loads((ROOT / row["eval_json"]).read_text())["execution"]["platform"]
            == "cpu"
            for row in matrices
        ),
        "all_trace_manifests_valid": len(trace_rows) == 32
        and all(row["ticks_contiguous"] and row["finite_14d_bridge_fields"] for row in trace_rows),
    }
    failed_checks = [name for name, passed in evidence_checks.items() if not passed]
    p30_pass = not failed_checks and len(p30) == 4 and all(
        row["summary"]["matrix_pass"] for row in p30
    )
    p31_pass = not failed_checks and len(p31) == 4 and all(
        row["summary"]["matrix_pass"] for row in p31
    )
    if failed_checks:
        status = decision = "INVALID_OBSERVER_CROSS_FIT_EVIDENCE"
    elif p30_pass:
        status = decision = "PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET"
    else:
        status = decision = "HOLD_P30_OBSERVER_CROSS_FIT_MISMATCH"

    all_summaries = [row["summary"] for row in matrices]
    result = {
        "schema_version": "winner_v2_observer_cross_fit_result.v1",
        "status": status,
        "decision": decision,
        "checks": evidence_checks,
        "failed_checks": failed_checks,
        "p30_observer_pass": p30_pass,
        "p31_34_observer_reporting_pass": p31_pass,
        "matrices": matrices,
        "traces": trace_rows,
        "measurements": {
            "matrix_count": len(matrices),
            "cell_count": len(trace_rows),
            "trace_row_count": sum(row["rows"] for row in trace_rows),
            "maximum_plant_observer_separation_rad": max(
                row["max_plant_observer_separation_rad"] for row in trace_rows
            ),
            "p30_observer_worst_nominal_tracking_p95_rad": max(
                row["summary"]["worst_nominal_tracking_p95_rad"] for row in p30
            ),
            "p30_observer_minimum_nominal_vx_m_s": min(
                row["summary"]["minimum_nominal_vx_m_s"] for row in p30
            ),
            "all_observer_worst_nominal_tracking_p95_rad": max(
                row["worst_nominal_tracking_p95_rad"] for row in all_summaries
            ),
        },
        "frozen": {
            "preregistration": str(PREREG.relative_to(ROOT)),
            "preregistration_sha256": sha256(PREREG),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "contract_sha256": sha256(CONTRACT),
            "playground_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
            "reference_sha256": sha256(REFERENCE),
        },
        "authority": {
            "pin_p30_observer_offline": p30_pass,
            "hardware_health_claim": False,
            "gate5_deployment_robot_rdk": False,
            "training_gpu_igpu_hosted": False,
        },
    }
    out_json = ROOT / "outputs/analysis/winner_v2_observer_cross_fit_result.json"
    out_md = ROOT / "outputs/analysis/WINNER_V2_OBSERVER_CROSS_FIT_RESULT_20260717.md"
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v2 Observer Cross-Fit Result",
        "",
        f"Status: `{status}`",
        "",
        f"Decision: `{decision}`",
        "",
        "| observer | plant | step | x=0 | moving | worst tracking | min vx | matrix pass |",
        "|---|---|---:|---|---|---:|---:|---|",
    ]
    for row in matrices:
        summary = row["summary"]
        lines.append(
            f"| `{row['observer_fit']}` | `{row['plant_fit']}` | {row['step']} | "
            f"`{summary['x0_pass']}` | `{summary['nominal_pass']}` | "
            f"{summary['worst_nominal_tracking_p95_rad']:.9f} | "
            f"{summary['minimum_nominal_vx_m_s']:.9f} | "
            f"`{summary['matrix_pass']}` |"
        )
    lines.extend(
        [
            "",
            f"- Formal cells: {len(trace_rows)}/32",
            f"- Trace rows: {result['measurements']['trace_row_count']}",
            f"- Maximum plant/observer separation: {result['measurements']['maximum_plant_observer_separation_rad']:.9f} rad",
            f"- P30-observer worst tracking p95: {result['measurements']['p30_observer_worst_nominal_tracking_p95_rad']:.9f} rad",
            f"- P30-observer minimum vx: {result['measurements']['p30_observer_minimum_nominal_vx_m_s']:.9f} m/s",
            "",
            "A pass pins only the P30 observer artifact for the offline winner-v2 configuration. It does not claim current hardware health or authorize Gate 5, deployment, RDK-X5 or robot use.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "p30_pass": p30_pass, "p31_reporting_pass": p31_pass}, sort_keys=True))
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
