#!/usr/bin/env python3
"""Run and aggregate the frozen 48-cell oracle phase-COM matrix on CPU."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim
from evaluate_ground_up_policy import emergence_evidence
from oracle_phase_com_controller import CORRECTED_JOINT_INDICES


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
CONTROLLER = ROOT / "outputs/analysis/oracle_phase_com_controller.json"
TRACE_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_traces/formal"
CELL_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_cells"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)
FITS = {
    "p30": ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
CONDITIONS = (("NOMINAL", 0.0), ("X_NEG", -0.05), ("X_POS", 0.05))
COMMANDS = (0.0, 0.074, 0.077, 0.08)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_readback(report: dict[str, Any], offset: float) -> bool:
    if offset == 0.0:
        return report.get("enabled") is False and report.get("key") is None
    readback = report.get("readback") or {}
    before, after = readback.get("before"), readback.get("after")
    expected = [offset, 0.0, 0.0]
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == expected
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and isinstance(before, list) and isinstance(after, list)
        and len(before) == len(after) == 3
        and all(abs(float(after[index]) - (float(before[index]) + expected[index])) <= 1e-12 for index in range(3))
    )


def summarize_cell(
    *, result: dict[str, Any], trace: Path, condition: str, offset: float,
    policy: Path, fit_name: str, fit_path: Path, command_x: float,
) -> dict[str, Any]:
    records = [json.loads(line) for line in trace.read_text().splitlines()]
    mode = (result.get("modes") or {}).get("fitted") or {}
    gate = result.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    emergence = emergence_evidence(result, command_x, 12.0, 1.08)
    residual = np.asarray([row["oracle_residual_action"] for row in records], dtype=float)
    corrected = np.asarray(CORRECTED_JOINT_INDICES, dtype=int)
    other = np.asarray([index for index in range(14) if index not in CORRECTED_JOINT_INDICES], dtype=int)
    saturation = max((sum(row["action_saturated"]) for row in records), default=0)
    rate_excess = max((max(row["sent_target_rate_excess_rad_s"]) for row in records), default=float("inf"))
    envelope_excess = max((float(row["oracle_envelope_excess_normalized"]) for row in records), default=float("inf"))
    tracking = max((max(row["tracking_error_rad"][index] for index in corrected) for row in records), default=float("inf"))
    tracking_p95 = float(np.percentile(np.asarray([row["tracking_error_rad"] for row in records])[:, corrected], 95)) if records else float("inf")
    readback = ((result.get("insertion_point") or {}).get("dynamics_override") or {})
    required_trace_fields = all(
        all(key in row for key in (
            "oracle_state", "oracle_residual_action", "action", "applied_target_rad",
            "foot_contacts", "tracking_error_rad", "action_saturated",
            "sent_target_rate_excess_rad_s", "oracle_envelope_excess_normalized",
        ))
        for row in records
    )
    bilateral = bool(
        command_x == 0.0
        or ((emergence.get("left_contact_transition_count") or 0) > 0
            and (emergence.get("right_contact_transition_count") or 0) > 0)
    )
    nominal_residual_zero = bool(
        condition != "NOMINAL" or np.array_equal(residual, np.zeros_like(residual))
    )
    residual_contract = bool(
        residual.shape == (len(records), 14)
        and (not records or float(np.max(np.abs(residual[:, corrected]))) <= 0.08 + 1e-12)
        and (not records or np.array_equal(residual[:, other], np.zeros((len(records), len(other)))))
        and nominal_residual_zero
    )
    mean_vx = ((mode.get("forward_motion") or {}).get("mean_velocity_x_m_s"))
    command_consistent = bool(
        command_x == 0.0
        or (isinstance(mean_vx, (int, float)) and float(mean_vx) > 0.0)
    )
    pass_cell = bool(
        len(records) == 600
        and mode.get("termination_reason") == "duration_complete"
        and gate.get("status") == "PASS_CANDIDATE_SIM_GATE"
        and (command_x == 0.0 or emergence.get("pass") is True)
        and bilateral and command_consistent
        and isinstance(metrics.get("max_pitch_tracking_p95_rad"), (int, float))
        and float(metrics["max_pitch_tracking_p95_rad"]) <= 0.20
        and tracking_p95 <= 0.20
        and saturation == 0
        and rate_excess == 0.0
        and metrics.get("max_sent_target_velocity_limit_excess_rad_s") == 0.0
        and metrics.get("max_sent_target_velocity_max_limit_excess_rad_s") == 0.0
        and envelope_excess == 0.0
        and exact_readback(readback, offset)
        and required_trace_fields and residual_contract
    )
    return {
        "schema_version": "oracle_phase_com_formal_cell.v1",
        "condition": condition, "offset_m": offset,
        "policy": policy.stem, "policy_path": str(policy), "policy_sha256": sha256(policy),
        "fit": fit_name, "fit_path": str(fit_path), "fit_sha256": sha256(fit_path),
        "command_x": command_x, "seed": 167931544, "requested_ticks": 600,
        "samples": len(records), "termination_reason": mode.get("termination_reason"),
        "candidate_gate_status": gate.get("status"), "emergence": emergence,
        "bilateral_transitions": bilateral, "command_consistent_forward": command_consistent,
        "mean_vx_m_s": mean_vx,
        "tracking_p95_rad_recomputed": tracking_p95,
        "tracking_max_rad_recomputed": tracking,
        "candidate_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "maximum_saturated_actions_per_tick": saturation,
        "maximum_rate_excess_rad_s": rate_excess,
        "maximum_envelope_excess_normalized": envelope_excess,
        "nominal_residual_exact_zero": nominal_residual_zero,
        "residual_contract_exact": residual_contract,
        "required_trace_fields_exact": required_trace_fields,
        "dynamics_readback": readback, "dynamics_readback_exact": exact_readback(readback, offset),
        "trace_path": str(trace), "trace_sha256": sha256(trace),
        "pass": pass_cell,
    }


def main() -> int:
    controller_sha = sha256(CONTROLLER)
    if controller_sha != "73bd9e647d18350b27feaa0220feb4167db187589d54d91859ac43973e1f5f1c":
        raise ValueError(f"frozen controller hash mismatch: {controller_sha}")
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    CELL_ROOT.mkdir(parents=True, exist_ok=True)
    cells = []
    ordinal = 0
    for condition, offset in CONDITIONS:
        for policy in POLICIES:
            for fit_name, fit_path in FITS.items():
                fit = json.loads(fit_path.read_text())
                for command_x in COMMANDS:
                    ordinal += 1
                    stem = f"{condition}_{policy.stem}_{fit_name}_x{command_x:.3f}_seed167931544"
                    trace = TRACE_ROOT / f"{stem}.jsonl"
                    result = run_closed_loop_sim(
                        ClosedLoopConfig(
                            policy_path=policy, fit=fit, playground_root=PLAYGROUND,
                            command_x=command_x, duration_s=12.0,
                            bridge_mode="fitted", expected_observation_dim=115,
                            expected_action_dim=14, task="flat_terrain_backlash",
                            seed=167931544, eval_role="candidate",
                            reset_mode="home-support",
                            reference_feature_table_path=REFERENCE,
                            reference_start_phase=0,
                            policy_state_input_names=("previous_action",),
                            policy_state_output_names=("previous_action_out",),
                            policy_applied_target_observation=True,
                            eval_dynamics_override=(None if offset == 0.0 else {"torso_com_offset_m": [offset, 0.0, 0.0]}),
                            oracle_phase_com_controller_json=CONTROLLER,
                            trace_jsonl=trace, trace_full_obs=True,
                            trace_oracle_state=True,
                        )
                    )
                    if not trace.exists():
                        raise RuntimeError(f"formal trace missing for {stem}: {result}")
                    cell = summarize_cell(
                        result=result, trace=trace, condition=condition, offset=offset,
                        policy=policy, fit_name=fit_name, fit_path=fit_path,
                        command_x=command_x,
                    )
                    cell_path = CELL_ROOT / f"{stem}.json"
                    cell_path.write_text(json.dumps(cell, indent=2, sort_keys=True) + "\n")
                    cell["cell_path"] = str(cell_path)
                    cell["cell_sha256"] = sha256(cell_path)
                    cells.append(cell)
                    print(f"[{ordinal}/48] {stem}: {'PASS' if cell['pass'] else 'FAIL'} {cell['samples']} ticks", flush=True)

    condition_results = {}
    for condition, _offset in CONDITIONS:
        subset = [cell for cell in cells if cell["condition"] == condition]
        condition_results[condition] = {
            "pass": all(cell["pass"] for cell in subset),
            "cells_passed": sum(cell["pass"] for cell in subset),
            "cells_total": len(subset),
            "worst_tracking_p95_rad": max(cell["tracking_p95_rad_recomputed"] for cell in subset),
            "minimum_mean_vx_m_s": min(float(cell["mean_vx_m_s"]) for cell in subset if isinstance(cell["mean_vx_m_s"], (int, float))),
        }
        markdown = ROOT / f"outputs/analysis/ORACLE_PHASE_COM_{condition}_RESULT.md"
        lines = [
            f"# Oracle Phase-COM {condition} Result", "",
            f"condition pass: `{condition_results[condition]['pass']}`", "",
            "| checkpoint | fit | command x | ticks | tracking p95 | mean vx | pass |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
        for cell in subset:
            lines.append(f"| {cell['policy']} | {cell['fit']} | {cell['command_x']:.3f} | {cell['samples']} | {cell['tracking_p95_rad_recomputed']:.9f} | {float(cell['mean_vx_m_s']):.9f} | `{cell['pass']}` |")
        lines.extend(["", "CPU simulation feasibility evidence only. Robot clearance remains `NO`.", ""])
        markdown.write_text("\n".join(lines))

    all_pass = all(cell["pass"] for cell in cells)
    if all_pass:
        decision = "PASS_ORACLE_DYNAMIC_COMPENSATION"
    else:
        decision = "HOLD_ORACLE_PARTIAL"
    checks = {
        "exact_48_cells": len(cells) == 48,
        "all_cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
        "all_policy_hashes_exact": all(cell["policy_sha256"] in {"99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de", "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece"} for cell in cells),
        "all_fit_hashes_exact": all(cell["fit_sha256"] in {"908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b", "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276"} for cell in cells),
        "all_per_run_readbacks_exact": all(cell["dynamics_readback_exact"] for cell in cells),
        "all_trace_contracts_exact": all(cell["required_trace_fields_exact"] for cell in cells),
        "nominal_residuals_exact_zero": all(cell["nominal_residual_exact_zero"] for cell in cells if cell["condition"] == "NOMINAL"),
    }
    failed_checks = sorted(key for key, value in checks.items() if not value)
    if failed_checks:
        raise RuntimeError(f"formal evidence contract failed: {failed_checks}")
    payload = {
        "schema_version": "oracle_phase_com_compensation_result.v1",
        "status": "PASS_ORACLE_PHASE_COM_MATRIX_COMPLETE",
        "decision": decision, "decision_token": decision,
        "checks": checks, "failed_checks": failed_checks,
        "controller_path": str(CONTROLLER), "controller_sha256": controller_sha,
        "condition_results": condition_results,
        "cells_passed": sum(cell["pass"] for cell in cells), "cells_total": len(cells),
        "cells": cells,
        "source_hashes": {
            "plan": sha256(ROOT / "outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_PLAN.md"),
            "contract": sha256(ROOT / "outputs/analysis/oracle_phase_com_compensation_contract.json"),
            "default_off": sha256(ROOT / "outputs/analysis/oracle_phase_com_default_off_contract.json"),
            "frozen_nominal": sha256(ROOT / "outputs/analysis/oracle_phase_com_frozen_nominal_contract.json"),
            "authority": sha256(ROOT / "outputs/analysis/oracle_phase_com_corrective_authority.json"),
            "controller_fit": sha256(ROOT / "outputs/analysis/oracle_phase_com_controller_fit.json"),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py"),
            "tool": sha256(Path(__file__)),
        },
        "selection_uses_training_reward": False,
        "execution": {"cpu_only": True, "training": False, "hosted": False, "robot_or_rdk": False, "gpu_or_igpu": False},
        "robot_clearance": "NO",
    }
    result_json = ROOT / "outputs/analysis/oracle_phase_com_compensation_result.json"
    result_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    result_md = ROOT / "outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_RESULT.md"
    lines = [
        "# Oracle Phase-Conditioned COM Compensation Result", "",
        f"status: `{payload['status']}`", f"decision: `{decision}`", "",
        "| condition | cells passed | worst tracking p95 | minimum mean vx | pass |",
        "|---|---:|---:|---:|---|",
    ]
    for condition, row in condition_results.items():
        lines.append(f"| {condition} | {row['cells_passed']}/{row['cells_total']} | {row['worst_tracking_p95_rad']:.9f} | {row['minimum_mean_vx_m_s']:.9f} | `{row['pass']}` |")
    lines.extend([
        "", f"Final explicit decision token: `{decision}`", "",
        "The result is CPU-only feasibility evidence. It does not authorize deployment, training, RDK-X5 or robot access. Robot clearance remains `NO`.", "",
    ])
    result_md.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "decision": decision, "cells_passed": payload["cells_passed"], "cells_total": payload["cells_total"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
