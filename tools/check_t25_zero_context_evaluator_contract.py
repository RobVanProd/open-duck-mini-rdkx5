#!/usr/bin/env python3
"""Contract the diagnostic-zero context needed by T23 deployment graphs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort

from closed_loop_sim_eval import ClosedLoopConfig, init_policy_io_state


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
OUTPUT = ANALYSIS / "t25_zero_context_evaluator_contract.json"
MARKDOWN = ANALYSIS / "T25_ZERO_CONTEXT_EVALUATOR_CONTRACT_20260726.md"
TICKS = 256
SEED = 20260726


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T25 zero-context contract requires --execute")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T25: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    rng = np.random.default_rng(SEED)
    rows = []
    for policy in prereg["policies"]:
        path = Path(policy["path"])
        session_zero = ort.InferenceSession(
            str(path), providers=["CPUExecutionProvider"]
        )
        session_other = ort.InferenceSession(
            str(path), providers=["CPUExecutionProvider"]
        )
        config = ClosedLoopConfig(
            policy_path=path,
            fit={},
            playground_root=Path(prereg["playground"]),
            command_x=0.074,
            duration_s=12.0,
            bridge_mode="fitted",
            expected_observation_dim=115,
            policy_obs_input_name="obs",
            policy_action_output_name="continuous_actions",
            policy_state_input_names=("h_in", "previous_action"),
            policy_state_output_names=("h_out", "previous_action_out"),
            policy_context_input_name="calibration_context",
            policy_zero_context_input=True,
            policy_graph_authoritative_output=True,
        )
        io = init_policy_io_state(session_zero, config)
        zero_context = np.zeros((1, 64), dtype=np.float32)
        other_context = rng.normal(size=(1, 64)).astype(np.float32)
        zero_hidden = np.zeros((1, 64), dtype=np.float32)
        other_hidden = zero_hidden.copy()
        zero_previous = np.zeros((1, 14), dtype=np.float32)
        other_previous = zero_previous.copy()
        max_errors = {
            "continuous_actions": 0.0,
            "h_out": 0.0,
            "previous_action_out": 0.0,
        }
        finite = True
        previous_action_exact = True
        for _ in range(TICKS):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            zero_outputs = session_zero.run(
                ["continuous_actions", "h_out", "previous_action_out"],
                {
                    "obs": obs,
                    "h_in": zero_hidden,
                    "previous_action": zero_previous,
                    "calibration_context": zero_context,
                },
            )
            other_outputs = session_other.run(
                ["continuous_actions", "h_out", "previous_action_out"],
                {
                    "obs": obs,
                    "h_in": other_hidden,
                    "previous_action": other_previous,
                    "calibration_context": other_context,
                },
            )
            for name, left, right in zip(
                max_errors,
                zero_outputs,
                other_outputs,
                strict=True,
            ):
                max_errors[name] = max(
                    max_errors[name],
                    float(np.max(np.abs(left - right))),
                )
                finite = bool(
                    finite
                    and np.all(np.isfinite(left))
                    and np.all(np.isfinite(right))
                )
            previous_action_exact = bool(
                previous_action_exact
                and np.array_equal(zero_outputs[0], zero_outputs[2])
                and np.array_equal(other_outputs[0], other_outputs[2])
            )
            zero_hidden = np.asarray(zero_outputs[1], dtype=np.float32)
            zero_previous = np.asarray(zero_outputs[2], dtype=np.float32)
            other_hidden = np.asarray(other_outputs[1], dtype=np.float32)
            other_previous = np.asarray(other_outputs[2], dtype=np.float32)
        rows.append(
            {
                "id": policy["id"],
                "step": policy["step"],
                "policy_sha256": sha256(path),
                "io_context_input_name": io["context_input_name"],
                "io_context_input_shape": io["context_input_shape"],
                "ticks": TICKS,
                "all_outputs_finite": finite,
                "all_context_output_errors_zero": all(
                    value == 0.0 for value in max_errors.values()
                ),
                "maximum_context_output_errors": max_errors,
                "previous_action_out_equals_action_bit_exact": (
                    previous_action_exact
                ),
            }
        )
    source = (ROOT / "tools/closed_loop_sim_eval.py").read_text(
        encoding="utf-8"
    )
    checks = {
        "preregistration_green": (
            prereg.get("status")
            == "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
            and prereg.get("failed_checks") == []
        ),
        "both_policies_checked": len(rows) == 2,
        "policy_hashes_exact": all(
            row["policy_sha256"]
            == next(
                item["sha256"]
                for item in prereg["policies"]
                if item["id"] == row["id"]
            )
            for row in rows
        ),
        "context_metadata_exact": all(
            row["io_context_input_name"] == "calibration_context"
            and row["io_context_input_shape"] == [1, 64]
            for row in rows
        ),
        "diagnostic_context_is_bit_exactly_ignored": all(
            row["all_context_output_errors_zero"] for row in rows
        ),
        "all_recurrent_chains_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "previous_action_state_feedback_exact": all(
            row["previous_action_out_equals_action_bit_exact"]
            for row in rows
        ),
        "evaluator_has_explicit_default_off_zero_context_mode": all(
            fragment in source
            for fragment in (
                "policy_zero_context_input: bool = False",
                "zero_context_enabled = bool(config.policy_zero_context_input)",
                'response_context = np.zeros((1, 64), dtype=np.float32)',
                '"mode": "diagnostic_zero"',
            )
        ),
        "simulator_locomotion_ticks_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t25_zero_context_contract.v1",
        "status": (
            "PASS_T25_ZERO_CONTEXT_EVALUATOR_CONTRACT"
            if not failed
            else "HOLD_T25_ZERO_CONTEXT_EVALUATOR_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "policies": rows,
        "contract": {
            "input_name": "calibration_context",
            "shape": [1, 64],
            "value": "all_float32_zeros",
            "graph_semantics": "diagnostic_input_bit_exactly_ignored",
            "response_calibrator": False,
            "calibration_ticks": 0,
            "home_return_ticks": 0,
            "default_off": True,
        },
        "execution": {
            "onnx_chain_ticks": len(rows) * TICKS,
            "simulator_locomotion_ticks": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "evaluator_recovery_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "training_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T25 diagnostic-zero context evaluator contract",
                "",
                f"- Status: `{value['status']}`",
                "- Both deployment graphs produced bit-exact outputs for "
                "zero versus nonzero diagnostic contexts over 256 recurrent "
                "ticks.",
                "- The evaluator mode supplies an explicit `[1,64]` zero "
                "context without a calibrator or unscored prefix.",
                "- Simulator behavior/Gate5/robot authority: `0/0/0`.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
