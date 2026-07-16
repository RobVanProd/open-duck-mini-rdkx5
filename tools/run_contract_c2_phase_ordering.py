#!/usr/bin/env python3
"""Run the preregistered CPU-only phase ordering comparison."""

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


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FIT_PATH = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)
ORDERINGS = (
    ("OBSERVE_THEN_ADVANCE", False),
    ("ADVANCE_THEN_OBSERVE", True),
)
COMMANDS = (0.074, 0.077, 0.080)
SEEDS = (100, 101)
TRACE_ROOT = ROOT / "outputs/analysis/contract_c2_phase_ordering_traces"
CELL_ROOT = ROOT / "outputs/analysis/contract_c2_phase_ordering_cells"
RESULT_PATH = ROOT / "outputs/analysis/contract_c2_phase_ordering_result.json"
RESULT_MD = ROOT / "outputs/analysis/CONTRACT_C2_PHASE_ORDERING_RESULT_20260716.md"

EXPECTED = {
    "T2_EQUAL_512000.onnx": "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
    "T2_EQUAL_1024000.onnx": "0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece",
    "fit": "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b",
    "reference": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "joystick": "4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186",
    "runner": "e5ed1bac7ed181f02014487827f05f35fd421ff97ae50614de1b2ce8089f87a2",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def summarize(result: dict[str, Any], trace_path: Path, ordering: str,
              policy: Path, command_x: float, seed: int) -> dict[str, Any]:
    if not trace_path.exists():
        raise RuntimeError(f"evaluator returned without a trace: {result}")
    trace = load_trace(trace_path)
    mode = (result.get("modes") or {}).get("fitted") or {}
    gate = result.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    emergence = emergence_evidence(result, command_x, 12.0, 1.08)
    tracking = np.asarray([row["tracking_error_rad"] for row in trace], dtype=float)
    tracking_p95 = float(np.percentile(tracking[:, [2, 3, 4, 11, 12, 13]], 95)) if len(trace) else float("inf")
    saturation = max((sum(row["action_saturated"]) for row in trace), default=99)
    rate_excess = max((max(row["sent_target_rate_excess_rad_s"]) for row in trace), default=float("inf"))
    bilateral = bool(
        (emergence.get("left_contact_transition_count") or 0) > 0
        and (emergence.get("right_contact_transition_count") or 0) > 0
    )
    passed = bool(
        len(trace) == 600
        and mode.get("termination_reason") == "duration_complete"
        and gate.get("status") == "PASS_CANDIDATE_SIM_GATE"
        and emergence.get("pass") is True
        and bilateral
        and tracking_p95 <= 0.20
        and metrics.get("max_pitch_tracking_p95_rad", float("inf")) <= 0.20
        and saturation == 0
        and rate_excess == 0.0
        and metrics.get("max_sent_target_velocity_limit_excess_rad_s") == 0.0
        and metrics.get("max_sent_target_velocity_max_limit_excess_rad_s") == 0.0
    )
    return {
        "schema_version": "contract_c2_phase_ordering_cell.v1",
        "ordering": ordering,
        "policy": policy.stem,
        "policy_sha256": sha256(policy),
        "command_x": command_x,
        "seed": seed,
        "requested_ticks": 600,
        "samples": len(trace),
        "termination_reason": mode.get("termination_reason"),
        "candidate_gate_status": gate.get("status"),
        "emergence": emergence,
        "bilateral_transitions": bilateral,
        "tracking_p95_rad_recomputed": tracking_p95,
        "candidate_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "maximum_saturated_actions_per_tick": saturation,
        "maximum_rate_excess_rad_s": rate_excess,
        "phase_index_tick0": trace[0]["oracle_state"]["phase_index"] if trace else None,
        "phase_index_tick_last": trace[-1]["oracle_state"]["phase_index"] if trace else None,
        "mean_vx_m_s": (mode.get("forward_motion") or {}).get("mean_velocity_x_m_s"),
        "trace_path": str(trace_path),
        "trace_sha256": sha256(trace_path),
        "pass": passed,
    }


def main() -> int:
    input_checks = {
        "cpu_environment": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
        "fit_hash": sha256(FIT_PATH) == EXPECTED["fit"],
        "reference_hash": sha256(REFERENCE) == EXPECTED["reference"],
        "policy_hashes": all(sha256(path) == EXPECTED[path.name] for path in POLICIES),
        "joystick_hash": sha256(PLAYGROUND / "playground/open_duck_mini_v2/joystick.py") == EXPECTED["joystick"],
        "runner_hash": sha256(PLAYGROUND / "playground/open_duck_mini_v2/runner.py") == EXPECTED["runner"],
    }
    if not all(input_checks.values()):
        raise RuntimeError(f"frozen input mismatch: {input_checks}")

    fit = json.loads(FIT_PATH.read_text())
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    CELL_ROOT.mkdir(parents=True, exist_ok=True)
    cells: list[dict[str, Any]] = []
    ordinal = 0
    for ordering, advance_first in ORDERINGS:
        for policy in POLICIES:
            for command_x in COMMANDS:
                for seed in SEEDS:
                    ordinal += 1
                    stem = f"{ordering}_{policy.stem}_x{command_x:.3f}_seed{seed}"
                    trace_path = TRACE_ROOT / f"{stem}.jsonl"
                    result = run_closed_loop_sim(
                        ClosedLoopConfig(
                            policy_path=policy,
                            fit=fit,
                            playground_root=PLAYGROUND,
                            command_x=command_x,
                            duration_s=12.0,
                            bridge_mode="fitted",
                            expected_observation_dim=115,
                            expected_action_dim=14,
                            task="flat_terrain_backlash",
                            seed=seed,
                            eval_role="candidate",
                            reset_mode="home-support",
                            reference_feature_table_path=REFERENCE,
                            reference_start_phase=0,
                            policy_state_input_names=("previous_action",),
                            policy_state_output_names=("previous_action_out",),
                            policy_applied_target_observation=True,
                            policy_phase_advance_before_observation=advance_first,
                            trace_jsonl=trace_path,
                            trace_oracle_state=True,
                        )
                    )
                    cell = summarize(result, trace_path, ordering, policy, command_x, seed)
                    cell_path = CELL_ROOT / f"{stem}.json"
                    cell_path.write_text(json.dumps(cell, indent=2, sort_keys=True) + "\n")
                    cell["cell_path"] = str(cell_path)
                    cell["cell_sha256"] = sha256(cell_path)
                    cells.append(cell)
                    print(f"[{ordinal}/24] {stem}: {'PASS' if cell['pass'] else 'FAIL'} tracking={cell['tracking_p95_rad_recomputed']:.9f}", flush=True)

    paired = []
    for policy in POLICIES:
        for command_x in COMMANDS:
            for seed in SEEDS:
                left = next(row for row in cells if row["ordering"] == "OBSERVE_THEN_ADVANCE" and row["policy"] == policy.stem and row["command_x"] == command_x and row["seed"] == seed)
                right = next(row for row in cells if row["ordering"] == "ADVANCE_THEN_OBSERVE" and row["policy"] == policy.stem and row["command_x"] == command_x and row["seed"] == seed)
                tracking_delta = float(right["tracking_p95_rad_recomputed"] - left["tracking_p95_rad_recomputed"])
                material_reasons = []
                if left["pass"] != right["pass"]: material_reasons.append("pass_fail_changed")
                if left["termination_reason"] != right["termination_reason"] or left["samples"] != right["samples"]: material_reasons.append("survival_changed")
                if abs(tracking_delta) >= 0.01: material_reasons.append("tracking_p95_delta_ge_0.01_rad")
                if abs(float(right["maximum_rate_excess_rad_s"]) - float(left["maximum_rate_excess_rad_s"])) > 1e-5: material_reasons.append("rate_excess_delta_gt_1e-5_rad_s")
                paired.append({
                    "policy": policy.stem, "command_x": command_x, "seed": seed,
                    "observe_then_advance_pass": left["pass"], "advance_then_observe_pass": right["pass"],
                    "tracking_p95_delta_advance_minus_observe_rad": tracking_delta,
                    "material": bool(material_reasons), "material_reasons": material_reasons,
                })

    material = any(row["material"] for row in paired)
    checks = {
        **input_checks,
        "exact_24_cells": len(cells) == 24,
        "exact_12_pairs": len(paired) == 12,
        "ordering_tick0_contract": all(
            row["phase_index_tick0"] == (0 if row["ordering"] == "OBSERVE_THEN_ADVANCE" else 1)
            for row in cells
        ),
        "all_rate_excess_zero": all(row["maximum_rate_excess_rad_s"] == 0.0 for row in cells),
        "all_saturation_zero": all(row["maximum_saturated_actions_per_tick"] == 0 for row in cells),
    }
    failed = sorted(key for key, value in checks.items() if not value)
    payload = {
        "schema_version": "contract_c2_phase_ordering_result.v1",
        "status": "PASS_CONTRACT_C2_PHASE_ORDERING_COMPLETE" if not failed else "FAIL_CONTRACT_C2_PHASE_ORDERING_EVIDENCE",
        "effect_classification": "MATERIAL_PHASE_ORDERING_EFFECT" if material else "NEGLIGIBLE_PHASE_ORDERING_EFFECT",
        "deployed_ordering": "OBSERVE_THEN_ADVANCE",
        "training_ordering": "OBSERVE_THEN_ADVANCE",
        "runtime_action": "KEEP_DEPLOYED_ORDERING" if not material else "REVIEW_RUNTIME_AGAINST_TRAINING_MATCH",
        "checks": checks,
        "failed_checks": failed,
        "cells_passed": sum(row["pass"] for row in cells),
        "cells_total": len(cells),
        "material_pairs": sum(row["material"] for row in paired),
        "pairs": paired,
        "cells": cells,
        "source_hashes": {
            "tool": sha256(Path(__file__)),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py"),
            "preregistration_json": sha256(ROOT / "outputs/analysis/contract_c2_phase_ordering_preregistration.json"),
            "preregistration_md": sha256(ROOT / "outputs/analysis/CONTRACT_C2_PHASE_ORDERING_PREREGISTRATION_20260716.md"),
        },
        "execution": {"cpu_only": True, "training": False, "hosted": False, "robot_or_rdk": False, "gpu_or_igpu": False},
        "robot_clearance": "NO",
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Contract C2 Phase Ordering Result", "",
        f"status: `{payload['status']}`", f"effect: `{payload['effect_classification']}`", "",
        f"Cells passed: {payload['cells_passed']}/24. Material pairs: {payload['material_pairs']}/12.", "",
        "| policy | x | seed | observe→advance | advance→observe | tracking delta rad | material |",
        "|---|---:|---:|---|---|---:|---|",
    ]
    for row in paired:
        lines.append(f"| {row['policy']} | {row['command_x']:.3f} | {row['seed']} | `{row['observe_then_advance_pass']}` | `{row['advance_then_observe_pass']}` | {row['tracking_p95_delta_advance_minus_observe_rad']:.9f} | `{row['material']}` |")
    lines.extend(["", f"Runtime disposition: `{payload['runtime_action']}`.", "", "CPU-only evidence; robot clearance remains `NO`.", ""])
    RESULT_MD.write_text("\n".join(lines))
    print(json.dumps({"status": payload["status"], "effect": payload["effect_classification"], "cells_passed": payload["cells_passed"], "material_pairs": payload["material_pairs"]}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
