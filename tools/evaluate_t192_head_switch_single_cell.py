#!/usr/bin/env python3
"""Evaluate T192's one exact half-to-final head-switch cell."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import t192_head_switch_eval_adapter as adapter  # noqa: E402
from evaluate_ground_up_policy import emergence_evidence  # noqa: E402


FORMAL_COMMAND = 0.080
FORMAL_SEED = 167931544
FORMAL_DURATION_S = 12.0
CALIBRATION_TICKS = 250
HOME_RETURN_TICKS = 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--switch-policy", type=Path, required=True)
    parser.add_argument("--switch-policy-sha256", required=True)
    parser.add_argument("--switch-tick", type=int, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--calibrator-sha256", required=True)
    parser.add_argument("--override-json", required=True)
    parser.add_argument("--command", type=float, default=FORMAL_COMMAND)
    parser.add_argument("--seed", type=int, default=FORMAL_SEED)
    parser.add_argument("--duration-s", type=float, default=FORMAL_DURATION_S)
    parser.add_argument("--trace-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--formal", action="store_true")
    args = parser.parse_args()

    if not args.formal:
        raise ValueError("T192 requires --formal")
    if (
        args.command != FORMAL_COMMAND
        or args.seed != FORMAL_SEED
        or args.duration_s != FORMAL_DURATION_S
        or args.switch_tick != 520
    ):
        raise ValueError("formal T192 command, seed, duration, or switch changed")
    override = json.loads(args.override_json)
    if override != {"torso_com_offset_m": [0.0, -0.05, 0.0]}:
        raise ValueError("T192 requires exact Y-negative override")

    policy = args.policy.resolve()
    switch_policy = args.switch_policy.resolve()
    calibrator = args.calibrator.resolve()
    if sha256(policy) != args.policy_sha256:
        raise ValueError("T192 primary policy hash changed")
    if sha256(switch_policy) != args.switch_policy_sha256:
        raise ValueError("T192 switch policy hash changed")
    if sha256(calibrator) != args.calibrator_sha256:
        raise ValueError("T192 calibrator hash changed")
    fit = json.loads(args.fit.resolve().read_text(encoding="utf-8"))
    module = adapter.load_module()
    args.trace_jsonl.parent.mkdir(parents=True, exist_ok=True)
    result = module.run_closed_loop_sim(
        module.ClosedLoopConfig(
            policy_path=policy,
            fit=fit,
            playground_root=args.playground_root.resolve(),
            policy_switch_path=switch_policy,
            policy_switch_sha256=args.switch_policy_sha256,
            policy_switch_tick=args.switch_tick,
            command_x=args.command,
            duration_s=args.duration_s,
            bridge_mode="fitted",
            expected_observation_dim=115,
            expected_action_dim=14,
            task="flat_terrain_backlash",
            seed=args.seed,
            eval_role="candidate",
            reset_mode="home-support",
            policy_obs_input_name="obs",
            policy_action_output_name="continuous_actions",
            policy_state_input_names=("h_in", "previous_action"),
            policy_state_output_names=("h_out", "previous_action_out"),
            policy_context_input_name="calibration_context",
            policy_graph_authoritative_output=True,
            response_calibrator_path=calibrator,
            response_calibrator_sha256=args.calibrator_sha256,
            response_calibration_ticks=CALIBRATION_TICKS,
            response_home_return_ticks=HOME_RETURN_TICKS,
            response_preserve_handoff_state=True,
            policy_applied_target_observation=True,
            eval_dynamics_override=override,
            trace_jsonl=args.trace_jsonl,
            trace_full_obs=True,
            reference_feature_table_path=(
                args.reference_feature_table.resolve()
            ),
            reference_start_phase=0,
        )
    )
    run: dict[str, Any] = {
        "command_x": args.command,
        "seed": args.seed,
        "status": result.get("status"),
        "candidate_gate": result.get("candidate_gate"),
        "emergence": emergence_evidence(
            result,
            args.command,
            args.duration_s,
            min(1.08, args.duration_s),
        ),
        "modes": result.get("modes"),
        "dynamics_override": (
            (result.get("insertion_point") or {}).get("dynamics_override")
        ),
        "policy_io": result.get("policy_io"),
        "response_calibration": result.get("response_calibration"),
        "error": result.get("error"),
        "trace_jsonl": str(args.trace_jsonl),
    }
    payload = {
        "schema_version": (
            "open_duck.t192_head_switch_single_cell_evaluation.v1"
        ),
        "status": "COMPLETE_T192_HEAD_SWITCH_SINGLE_CELL",
        "formal": True,
        "inputs": {
            "policy": str(policy),
            "policy_sha256": args.policy_sha256,
            "switch_policy": str(switch_policy),
            "switch_policy_sha256": args.switch_policy_sha256,
            "switch_tick": args.switch_tick,
            "fit": str(args.fit.resolve()),
            "playground": str(args.playground_root.resolve()),
            "reference_feature_table": str(
                args.reference_feature_table.resolve()
            ),
            "calibrator": str(calibrator),
            "calibrator_sha256": args.calibrator_sha256,
            "calibration_ticks": CALIBRATION_TICKS,
            "home_return_ticks": HOME_RETURN_TICKS,
            "preserve_handoff_state": True,
            "expected_observation_dim": 115,
            "expected_action_dim": 14,
            "policy_state_input_names": ["h_in", "previous_action"],
            "policy_state_output_names": ["h_out", "previous_action_out"],
            "policy_context_input_name": "calibration_context",
            "policy_graph_authoritative_output": True,
            "policy_applied_target_observation": True,
            "reference_start_phase": 0,
            "eval_dynamics_override": override,
            "commands_x_m_s": [args.command],
            "seed": args.seed,
            "duration_s": args.duration_s,
            "adapter_contract": adapter.contract(),
        },
        "execution": {
            "platform": "cpu",
            "formal_behavior_cells": 1,
            "contract_smoke_runs": 0,
        },
        "runs": [run],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(payload["status"])
    print("formal=True")
    print("runs=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
