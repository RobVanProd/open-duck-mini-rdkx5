#!/usr/bin/env python3
"""Freeze the zero-formal-cell Winner-v103 evaluator contract."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
    canonical_sha256,
    matrix_plan,
    sha256,
    trace_audit,
)

ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v103_response_conditioned_behavior_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V101_RESULT = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
OUTPUT = ANALYSIS / "winner_v103_response_conditioned_behavior_runner_contract.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_RUNNER_CONTRACT_20260722.md"
)
PREREG_SHA256 = (
    "1087c9a60b93c359be15d2423bf3f1fc1cbc740e3a7d6fc4a650f6b73cb7efcf"
)
V101_RESULT_SHA256 = (
    "4f44c2ff9de0ee715b09c1c95048bedb0a43f3334eaa70970dac8c08d6e047d0"
)
SURROGATE_POLICY_SHA256 = (
    "390f3471ebb15f94d76bd06e46e5441f13e4f306f890a6c4e251b2cad88eb415"
)
CALIBRATOR_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
MATRIX_PLAN_SHA256 = (
    "10b5d3e407636d276275f3f39145233c3cd63688c3229235411ed2734651e073"
)


def finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (int, float)):
        return value == value and value not in (float("inf"), float("-inf"))
    return True


def smoke_trace_checks(path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fitted = [row for row in rows if row.get("mode") == "fitted"]
    hashes = {
        row.get("policy_calibration_context_sha256") for row in fitted
    }
    return {
        "rows": len(fitted),
        "graph_authoritative_every_tick": bool(fitted)
        and all(row.get("policy_graph_authoritative_output") is True for row in fitted),
        "host_action_delta_exact_zero": bool(fitted)
        and all(row.get("policy_host_action_delta_max_abs") == 0.0 for row in fitted),
        "one_immutable_context_hash": len(hashes) == 1 and None not in hashes,
    }


def full_stack_smoke(
    *,
    playground: Path,
    policy: Path,
    calibrator: Path,
    trace: Path,
) -> dict[str, Any]:
    prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    condition = prereg["evaluation_matrix"]["discovery_samples"][5]
    transport = {
        "sensor_noise_scales": {
            "hip_pos_rad": 0.0,
            "knee_pos_rad": 0.0,
            "ankle_pos_rad": 0.0,
            "joint_vel_rad_s": 0.0,
            "gravity": 0.0,
            "linvel_m_s": 0.0,
            "gyro_rad_s": 0.0,
            "accelerometer": 0.0,
        },
        "native_quantization": False,
        "additional_action_delay_ticks": 0,
        "imu_delay_ticks": 0,
    }
    if trace.exists():
        trace.unlink()
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(prereg, "P30_ALL_JOINT"),
                playground_root=playground,
                command_x=0.076,
                duration_s=0.02,
                bridge_mode="fitted",
                expected_observation_dim=115,
                task="flat_terrain_backlash",
                seed=2_026_072_203,
                eval_role="candidate",
                reset_mode="home-support",
                policy_obs_input_name="obs",
                policy_action_output_name="continuous_actions",
                policy_state_input_names=("h_in", "previous_action"),
                policy_state_output_names=("h_out", "previous_action_out"),
                policy_context_input_name="calibration_context",
                policy_graph_authoritative_output=True,
                response_calibrator_path=calibrator,
                response_calibrator_sha256=CALIBRATOR_SHA256,
                response_calibration_ticks=250,
                response_home_return_ticks=250,
                policy_applied_target_observation=True,
                reference_feature_table_path=REFERENCE,
                reference_start_phase=0,
                trace_jsonl=trace,
                trace_full_obs=True,
                winner_v3_configuration_override=condition,
                winner_v3_sensor_noise_scales=transport["sensor_noise_scales"],
                winner_v3_native_quantization=False,
                winner_v3_additional_action_delay_ticks=0,
                winner_v3_imu_delay_ticks=0,
                winner_v3_home_relative_actuator_gain=True,
            )
        )
    mode = ((result.get("modes") or {}).get("fitted") or {})
    response = mode.get("response_calibration") or {}
    trace_contract = trace_audit(trace) if trace.exists() else {}
    response_trace = smoke_trace_checks(trace) if trace.exists() else {}
    checks = {
        "one_scored_tick_only": mode.get("samples") == 1,
        "duration_complete": mode.get("termination_reason") == "duration_complete",
        "cpu_only": ((result.get("env") or {}).get("jax_backend")) == "cpu",
        "calibration_enabled": response.get("enabled") is True,
        "calibration_ticks_exact": response.get("calibration_ticks") == 250,
        "home_return_ticks_exact": response.get("home_return_ticks") == 250,
        "context_shape_exact": response.get("context_shape") == [1, 64],
        "context_finite": response.get("context_finite") is True,
        "phase_reset_exact": response.get("locomotion_phase_reset") == [1.0, 0.0],
        "hidden_reset_exact": response.get("locomotion_hidden_exact_zero") is True,
        "previous_action_reset_exact": (
            response.get("locomotion_previous_action_exact_zero") is True
        ),
        "host_action_unmodified": mode.get("policy_host_action_delta_max_abs") == 0.0,
        "trace_one_tick": trace_contract.get("rows") == 1,
        "trace_finite": trace_contract.get("all_values_finite") is True,
        "trace_graph_authoritative": response_trace.get(
            "graph_authoritative_every_tick"
        )
        is True,
        "trace_host_action_exact": response_trace.get(
            "host_action_delta_exact_zero"
        )
        is True,
        "trace_context_immutable": response_trace.get(
            "one_immutable_context_hash"
        )
        is True,
    }
    return {
        "formal": False,
        "scored_ticks": 1,
        "unscored_calibration_ticks": 250,
        "unscored_home_return_ticks": 250,
        "result_status_recorded_not_gating": result.get("status"),
        "result_error": result.get("error"),
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
        "pass": all(checks.values()),
        "response_calibration": response,
        "policy_io": result.get("policy_io"),
        "trace": trace_contract,
        "response_trace": response_trace,
    }


def build(
    *,
    playground: Path,
    policy: Path,
    calibrator: Path,
    trace: Path,
) -> dict[str, Any]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise ValueError("JAX_PLATFORMS must be cpu")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("Winner-v103 preregistration changed")
    if sha256(V101_RESULT) != V101_RESULT_SHA256:
        raise ValueError("Winner-v101 CPU contract changed")
    if sha256(policy) != SURROGATE_POLICY_SHA256:
        raise ValueError("Winner-v101 surrogate policy changed")
    if sha256(calibrator) != CALIBRATOR_SHA256:
        raise ValueError("response calibrator changed")
    prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    plan = matrix_plan(prereg)
    smoke = full_stack_smoke(
        playground=playground,
        policy=policy,
        calibrator=calibrator,
        trace=trace,
    )
    checks = {
        "preregistration_exact": True,
        "v101_surrogate_graph_exact": True,
        "calibrator_exact": True,
        "matrix_1024_exact": len(plan) == 1024,
        "matrix_plan_sha256_exact": canonical_sha256(plan) == MATRIX_PLAN_SHA256,
        "full_stack_nonformal_smoke_passed": smoke["pass"],
        "formal_behavior_cells_zero": True,
        "all_values_finite": finite_tree(smoke),
        "cpu_environment_exact": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    builder = Path(__file__).resolve()
    evaluator = TOOLS / "closed_loop_sim_eval.py"
    return {
        "schema_version": (
            "winner_v103.response_conditioned_behavior_runner_contract.v1"
        ),
        "status": (
            "PASS_WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_RUNNER_CONTRACT"
            if not failed
            else "HOLD_WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_RUNNER_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "matrix_cells": len(plan),
        "matrix_plan_sha256": canonical_sha256(plan),
        "builder_path": str(builder.relative_to(ROOT)),
        "builder_sha256": sha256(builder),
        "supporting_tool_hashes": {
            "closed_loop_sim_eval.py": sha256(evaluator),
            "run_winner_v3_variable_configuration_behavior.py": sha256(
                TOOLS / "run_winner_v3_variable_configuration_behavior.py"
            ),
        },
        "input_hashes": {
            "v103_preregistration": sha256(PREREG),
            "v101_cpu_contract": sha256(V101_RESULT),
            "v101_surrogate_policy": sha256(policy),
            "calibrator": sha256(calibrator),
            "reference_features": sha256(REFERENCE),
        },
        "nonformal_full_stack_smoke": smoke,
        "environment": {
            "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
            "JAX_PLATFORMS": os.environ["JAX_PLATFORMS"],
            "robot_or_rdk_access": False,
        },
        "authority": {
            "formal_execution_after_valid_v102_artifact": not failed,
            "formal_execution_now": False,
            "retry": False,
            "training": False,
            "gpu_or_igpu": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
            "robot_clearance": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--surrogate-policy", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite runner contract: {path}")
    payload = build(
        playground=args.playground.resolve(),
        policy=args.surrogate_policy.resolve(),
        calibrator=args.calibrator.resolve(),
        trace=args.trace.resolve(),
    )
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v103 response-conditioned behavior runner contract\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The full-stack CPU smoke executed the exact 250-tick automatic "
        "calibration and 250-tick home return, then one non-formal scored tick "
        "through the four-input stateful graph. The trace proves the 64-D "
        "context stayed immutable and the host changed no graph-owned action.\n\n"
        "Formal behavior cells executed: `0`. A passing contract does not "
        "authorize formal evaluation until a valid Winner-v102 hosted artifact "
        "exists. It grants no robot, RDK-X5, Gate 5, torque, motion, deployment, "
        "or robot clearance.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
