#!/usr/bin/env python3
"""Prove the frozen oracle controller is exactly default-off at nominal COM."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from check_oracle_phase_com_default_off import flatten_numeric, read_trace, sha256
from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
CONTROLLER = ROOT / "outputs/analysis/oracle_phase_com_controller.json"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)


def main() -> int:
    fit = json.loads(FIT.read_text())
    cells = []
    with tempfile.TemporaryDirectory(prefix="oracle_frozen_nominal_") as temp:
        root = Path(temp)
        for policy in POLICIES:
            for command_x in (0.0, 0.077):
                traces = []
                results = []
                for label, controller in (("baseline", None), ("frozen_controller", CONTROLLER)):
                    trace = root / f"{policy.stem}_{command_x:.3f}_{label}.jsonl"
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
                            trace_jsonl=trace, trace_full_obs=True,
                            trace_oracle_state=controller is not None,
                            oracle_phase_com_controller_json=controller,
                        )
                    )
                    if not trace.exists():
                        raise RuntimeError(f"missing trace: {result}")
                    traces.append(read_trace(trace))
                    results.append(result)
                baseline, controlled = traces
                maximum_difference = 0.0
                mismatch = None
                exact = len(baseline) == len(controlled)
                if exact:
                    for tick, (left, right) in enumerate(zip(baseline, controlled, strict=True)):
                        a, b = flatten_numeric(left), flatten_numeric(right)
                        if set(a) != set(b):
                            exact = False
                            mismatch = f"schema_tick_{tick}"
                            break
                        for key in a:
                            difference = abs(a[key] - b[key])
                            maximum_difference = max(maximum_difference, difference)
                            if not np.isfinite(difference) or difference > 1e-7:
                                exact = False
                                mismatch = f"{key}_tick_{tick}"
                                break
                        if not exact:
                            break
                zero_residual = all(
                    np.array_equal(np.asarray(row["oracle_residual_action"], dtype=np.float32), np.zeros(14, dtype=np.float32))
                    for row in controlled
                )
                cells.append({
                    "policy": policy.stem, "command_x": command_x,
                    "baseline_status": results[0].get("status"),
                    "controlled_status": results[1].get("status"),
                    "ticks": len(controlled), "numeric_exact_within_1e_7": exact,
                    "maximum_absolute_numeric_difference": maximum_difference,
                    "first_mismatch": mismatch, "residual_exact_zero": zero_residual,
                })
    checks = {
        "four_cells_exact": len(cells) == 4,
        "all_600_ticks": all(row["ticks"] == 600 for row in cells),
        "statuses_exact": all(row["baseline_status"] == row["controlled_status"] for row in cells),
        "numeric_exact_within_1e_7": all(row["numeric_exact_within_1e_7"] for row in cells),
        "residual_exact_zero": all(row["residual_exact_zero"] for row in cells),
    }
    failed = sorted(key for key, value in checks.items() if not value)
    payload = {
        "schema_version": "oracle_phase_com_frozen_nominal_contract.v1",
        "status": "PASS_ORACLE_PHASE_COM_FROZEN_NOMINAL" if not failed else "FAIL_ORACLE_PHASE_COM_FROZEN_NOMINAL",
        "checks": checks, "failed_checks": failed, "cells": cells,
        "controller_sha256": sha256(CONTROLLER),
        "source_hashes": {"tool": sha256(Path(__file__)), "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py")},
        "execution": {"cpu_only": True, "formal_matrix_cells": 0, "robot_or_rdk": False},
    }
    output = ROOT / "outputs/analysis/oracle_phase_com_frozen_nominal_contract.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
