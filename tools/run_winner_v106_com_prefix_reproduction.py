#!/usr/bin/env python3
"""Reproduce the V103 negative-X COM calibration-prefix failure on CPU."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
    matrix_plan,
)
from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    CALIBRATOR_SHA256,
    REFERENCE,
)


ANALYSIS = ROOT / "outputs/analysis"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
FORMAL_RESULT = ANALYSIS / "winner_v103_response_conditioned_result.json"
OUTPUT = ANALYSIS / "winner_v106_com_prefix_reproduction.json"
POLICY_SHA256 = (
    "86271b2bec3795df5f801ff640a78c409b69d26ba7c4c591e6329919e408292a"
)
FORMAL_RESULT_SHA256 = (
    "f3a0ed34d46b6013c0910afe29fcd9f424729c94b61b8abdb4f416457ad3922b"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (int, float)):
        return value == value and value not in (float("inf"), float("-inf"))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(
            f"refusing to overwrite Winner-v106 reproduction: {args.output}"
        )
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("JAX_PLATFORMS must be cpu")
    policy = args.policy.resolve()
    calibrator = args.calibrator.resolve()
    playground = args.playground.resolve()
    trace = args.trace.resolve()
    if trace.exists():
        raise FileExistsError(f"refusing to overwrite reproduction trace: {trace}")
    if (
        sha256(policy) != POLICY_SHA256
        or sha256(calibrator) != CALIBRATOR_SHA256
        or sha256(FORMAL_RESULT) != FORMAL_RESULT_SHA256
    ):
        raise ValueError("Winner-v106 reproduction inputs changed")

    prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    row = next(
        item
        for item in matrix_plan(prereg)
        if item["condition_id"] == "COM_X_NEG"
        and int(item["step"]) == 1_003_520
        and item["plant"] == "P30_ALL_JOINT"
        and float(item["command_x_m_s"]) == 0.0
    )
    trace.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(prereg, str(row["plant"])),
                playground_root=playground,
                command_x=0.0,
                duration_s=12.0,
                bridge_mode="fitted",
                expected_observation_dim=115,
                task="flat_terrain_backlash",
                seed=int(row["seed"]),
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
                winner_v3_configuration_override=row["configuration"],
                winner_v3_sensor_noise_scales=row["transport"][
                    "sensor_noise_scales"
                ],
                winner_v3_native_quantization=bool(
                    row["transport"]["native_quantization"]
                ),
                winner_v3_additional_action_delay_ticks=int(
                    row["transport"]["additional_action_delay_ticks"]
                ),
                winner_v3_imu_delay_ticks=int(
                    row["transport"]["imu_delay_ticks"]
                ),
                winner_v3_home_relative_actuator_gain=True,
            )
        )

    device_platforms = [device.platform for device in jax.devices()]
    checks = {
        "formal_result_exact": True,
        "policy_exact": True,
        "calibrator_exact": True,
        "cpu_backend_exact": jax.default_backend() == "cpu",
        "all_device_platforms_cpu": bool(device_platforms)
        and all(platform == "cpu" for platform in device_platforms),
        "expected_prefix_status": (
            result.get("status") == "HOLD_RESPONSE_CALIBRATION_PREFIX"
        ),
        "expected_prefix_error": (
            result.get("error") == "calibration prefix terminated early"
        ),
        "no_environment_readback": result.get("env") is None,
        "no_scored_trace_created": not trace.exists(),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v106.com_prefix_reproduction.v1",
        "status": (
            "PASS_WINNER_V106_COM_PREFIX_REPRODUCTION"
            if not failed
            else "HOLD_WINNER_V106_COM_PREFIX_REPRODUCTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "identity": row,
        "observed": {
            "simulator_status": result.get("status"),
            "simulator_error": result.get("error"),
            "result_keys": sorted(result),
            "environment_readback_present": result.get("env") is not None,
            "scored_trace_created": trace.exists(),
        },
        "cpu_environment": {
            "jax_backend": jax.default_backend(),
            "device_platforms": device_platforms,
            "device_strings": [str(device) for device in jax.devices()],
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "JAX_PLATFORMS": os.environ.get("JAX_PLATFORMS"),
        },
        "input_hashes": {
            "formal_result": sha256(FORMAL_RESULT),
            "policy": sha256(policy),
            "calibrator": sha256(calibrator),
            "base_preregistration": sha256(BASE_PREREG),
            "reference_features": sha256(REFERENCE),
        },
        "causal_boundary": {
            "policy_or_calibration_failure_present": True,
            "calibration_prefix_terminated_before_scored_tick_zero": True,
            "missing_environment_readback_is_expected_for_this_early_return": True,
            "readback_validator_exception_is_separate": True,
        },
        "authority": {
            "evaluator_correction_only": True,
            "training_authorized": False,
            "checkpoint_selection_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    if not finite_tree(payload):
        raise ValueError("Winner-v106 reproduction contains nonfinite values")
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
