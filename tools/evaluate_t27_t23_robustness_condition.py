#!/usr/bin/env python3
"""Evaluate one T27 R2 condition with T23's exact support handoff."""

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

import t27_state_coherent_eval_adapter as adapter  # noqa: E402
from evaluate_ground_up_policy import emergence_evidence  # noqa: E402


FORMAL_COMMANDS = (0.0, 0.074, 0.077, 0.08)
FORMAL_SEED = 167931544
CALIBRATION_TICKS = 250
HOME_RETURN_TICKS = 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_commands(text: str) -> tuple[float, ...]:
    return tuple(
        float(item.strip()) for item in text.split(",") if item.strip()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--calibrator-sha256", required=True)
    parser.add_argument("--override-json", required=True)
    parser.add_argument("--commands", default="0.0,0.074,0.077,0.08")
    parser.add_argument("--seed", type=int, default=FORMAL_SEED)
    parser.add_argument("--duration-s", type=float, default=12.0)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--formal", action="store_true")
    args = parser.parse_args()

    commands = parse_commands(args.commands)
    if args.formal and (
        commands != FORMAL_COMMANDS
        or args.seed != FORMAL_SEED
        or args.duration_s != 12.0
    ):
        raise ValueError("formal T27 commands, seed, or duration changed")
    if not commands or args.duration_s <= 0.0:
        raise ValueError("commands and duration must be nonempty and positive")

    override = json.loads(args.override_json)
    if not isinstance(override, dict) or len(override) != 1:
        raise ValueError("T27 requires exactly one R2 override axis")
    policy = args.policy.resolve()
    calibrator = args.calibrator.resolve()
    if sha256(policy) != args.policy_sha256:
        raise ValueError("T27 policy hash changed")
    if sha256(calibrator) != args.calibrator_sha256:
        raise ValueError("T27 calibrator hash changed")
    fit = json.loads(args.fit.resolve().read_text(encoding="utf-8"))
    module = adapter.load_module()
    args.trace_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, Any]] = []
    for command_x in commands:
        trace_path = (
            args.trace_dir
            / f"x{command_x:.3f}_seed{args.seed}_{policy.stem}.jsonl"
        )
        result = module.run_closed_loop_sim(
            module.ClosedLoopConfig(
                policy_path=policy,
                fit=fit,
                playground_root=args.playground_root.resolve(),
                command_x=command_x,
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
                trace_jsonl=trace_path,
                trace_full_obs=True,
                reference_feature_table_path=(
                    args.reference_feature_table.resolve()
                ),
                reference_start_phase=0,
            )
        )
        runs.append(
            {
                "command_x": command_x,
                "seed": args.seed,
                "status": result.get("status"),
                "candidate_gate": result.get("candidate_gate"),
                "emergence": emergence_evidence(
                    result,
                    command_x,
                    args.duration_s,
                    min(1.08, args.duration_s),
                ),
                "modes": result.get("modes"),
                "dynamics_override": (
                    (result.get("insertion_point") or {}).get(
                        "dynamics_override"
                    )
                ),
                "policy_io": result.get("policy_io"),
                "response_calibration": result.get(
                    "response_calibration"
                ),
                "error": result.get("error"),
                "trace_jsonl": str(trace_path),
            }
        )

    payload = {
        "schema_version": (
            "open_duck.t27_t23_robustness_condition_evaluation.v1"
        ),
        "status": "COMPLETE_T27_T23_ROBUSTNESS_CONDITION_BLOCK",
        "formal": bool(args.formal),
        "inputs": {
            "policy": str(policy),
            "policy_sha256": args.policy_sha256,
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
            "commands_x_m_s": list(commands),
            "seed": args.seed,
            "duration_s": args.duration_s,
        },
        "execution": {
            "platform": "cpu",
            "formal_behavior_cells": len(runs) if args.formal else 0,
            "contract_smoke_runs": 0 if args.formal else len(runs),
        },
        "runs": runs,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"formal={payload['formal']}")
    print(f"runs={len(runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
