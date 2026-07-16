#!/usr/bin/env python3
"""Run the preregistered byte/numeric default-off oracle-controller contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def flatten_numeric(value: Any, prefix: str = "") -> dict[str, float]:
    output: dict[str, float] = {}
    if isinstance(value, bool):
        output[prefix] = float(value)
    elif isinstance(value, (int, float)):
        output[prefix] = float(value)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            output.update(flatten_numeric(item, f"{prefix}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key == "oracle_state":
                continue
            output.update(flatten_numeric(item, f"{prefix}.{key}" if prefix else key))
    return output


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def main() -> int:
    fit = json.loads(FIT.read_text())
    rows = []
    with tempfile.TemporaryDirectory(prefix="oracle_default_off_") as temp:
        temp_root = Path(temp)
        for policy in POLICIES:
            for command_x in (0.0, 0.077):
                traces = []
                results = []
                for label, trace_oracle in (("baseline", False), ("instrumented", True)):
                    trace = temp_root / f"{policy.stem}_{command_x:.3f}_{label}.jsonl"
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
                            seed=167931544,
                            eval_role="candidate",
                            reset_mode="home-support",
                            reference_feature_table_path=REFERENCE,
                            reference_start_phase=0,
                            policy_state_input_names=("previous_action",),
                            policy_state_output_names=("previous_action_out",),
                            policy_applied_target_observation=True,
                            trace_jsonl=trace,
                            trace_full_obs=True,
                            trace_oracle_state=trace_oracle,
                        )
                    )
                    if not trace.exists():
                        raise RuntimeError(
                            f"evaluator did not write {trace}: "
                            f"{json.dumps(result, sort_keys=True, default=str)}"
                        )
                    traces.append(read_trace(trace))
                    results.append(result)
                left, right = traces
                common_numeric_exact = True
                maximum_difference = 0.0
                mismatch = None
                if len(left) != len(right):
                    common_numeric_exact = False
                    mismatch = "trace_length"
                else:
                    for tick, (a, b) in enumerate(zip(left, right, strict=True)):
                        fa, fb = flatten_numeric(a), flatten_numeric(b)
                        if set(fa) != set(fb):
                            common_numeric_exact = False
                            mismatch = f"numeric_schema_tick_{tick}"
                            break
                        for key in fa:
                            difference = abs(fa[key] - fb[key])
                            maximum_difference = max(maximum_difference, difference)
                            if not np.isfinite(difference) or difference > 1e-7:
                                common_numeric_exact = False
                                mismatch = f"{key}_tick_{tick}"
                                break
                        if not common_numeric_exact:
                            break
                instrumented_zero_residual = all(
                    np.array_equal(
                        np.asarray(row["oracle_residual_action"], dtype=np.float32),
                        np.zeros(14, dtype=np.float32),
                    )
                    for row in right
                )
                rows.append(
                    {
                        "policy": policy.stem,
                        "policy_sha256": sha256(policy),
                        "command_x": command_x,
                        "baseline_status": results[0].get("status"),
                        "instrumented_status": results[1].get("status"),
                        "tick_count": len(left),
                        "common_numeric_exact_within_1e_7": common_numeric_exact,
                        "maximum_absolute_numeric_difference": maximum_difference,
                        "first_mismatch": mismatch,
                        "instrumented_residual_exact_zero": instrumented_zero_residual,
                    }
                )
    checks = {
        "four_cells_exact": len(rows) == 4,
        "all_600_ticks": all(row["tick_count"] == 600 for row in rows),
        "statuses_exact": all(
            row["baseline_status"] == row["instrumented_status"] for row in rows
        ),
        "common_numeric_exact_within_1e_7": all(
            row["common_numeric_exact_within_1e_7"] for row in rows
        ),
        "instrumented_residual_exact_zero": all(
            row["instrumented_residual_exact_zero"] for row in rows
        ),
        "cpu_environment": os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu",
    }
    failed = sorted(key for key, value in checks.items() if not value)
    payload = {
        "schema_version": "oracle_phase_com_default_off_contract.v1",
        "status": "PASS_ORACLE_PHASE_COM_DEFAULT_OFF" if not failed else "FAIL_ORACLE_PHASE_COM_DEFAULT_OFF",
        "checks": checks,
        "failed_checks": failed,
        "cells": rows,
        "source_hashes": {
            "plan": sha256(ROOT / "outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_PLAN.md"),
            "contract": sha256(ROOT / "outputs/analysis/oracle_phase_com_compensation_contract.json"),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py"),
            "controller_module": sha256(ROOT / "tools/oracle_phase_com_controller.py"),
        },
    }
    output = ROOT / "outputs/analysis/oracle_phase_com_default_off_contract.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
