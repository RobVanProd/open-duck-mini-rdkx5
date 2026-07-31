#!/usr/bin/env python3
"""Evaluate one T9 x=0 command-aware prefix-bypass cell on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import t9_command_aware_eval_adapter as adapter  # noqa: E402
from evaluate_t8_state_coherent_handoff import (  # noqa: E402
    emergence_evidence,
)


SEED = 167931544


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--duration-s", type=float, default=12.0)
    parser.add_argument("--trace-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    if args.seed != SEED or args.duration_s != 12.0:
        raise ValueError("T9 seed or duration changed")
    policy = args.policy.resolve()
    playground = args.playground_root.resolve()
    fit_path = args.fit.resolve()
    reference = args.reference_feature_table.resolve()
    fit = json.loads(fit_path.read_text(encoding="utf-8"))
    module = adapter.load_module()
    args.trace_jsonl.parent.mkdir(parents=True, exist_ok=True)
    result = module.run_closed_loop_sim(
        module.ClosedLoopConfig(
            policy_path=policy,
            fit=fit,
            playground_root=playground,
            command_x=0.0,
            duration_s=args.duration_s,
            bridge_mode="fitted",
            expected_observation_dim=115,
            expected_action_dim=14,
            task="flat_terrain_backlash",
            seed=args.seed,
            eval_role="candidate",
            reset_mode="home-support",
            policy_state_input_names=("h_in", "previous_action"),
            policy_state_output_names=("h_out", "previous_action_out"),
            policy_context_input_name="calibration_context",
            policy_graph_authoritative_output=True,
            response_zero_context_bypass=True,
            policy_applied_target_observation=True,
            eval_dynamics_override={
                "torso_com_offset_m": [0.0, 0.0, 0.0]
            },
            trace_jsonl=args.trace_jsonl,
            trace_full_obs=True,
            reference_feature_table_path=reference,
            reference_start_phase=0,
        )
    )
    payload = {
        "schema_version": "open_duck.t9_x0_prefix_bypass_evaluation.v1",
        "status": "COMPLETE_T9_X0_PREFIX_BYPASS_CELL",
        "execution": {
            "platform": "cpu",
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "inputs": {
            "policy": str(policy),
            "policy_sha256": sha256(policy),
            "playground_root": str(playground),
            "fit": str(fit_path),
            "fit_sha256": sha256(fit_path),
            "reference_feature_table": str(reference),
            "reference_feature_table_sha256": sha256(reference),
            "command_x_m_s": 0.0,
            "seed": args.seed,
            "duration_s": args.duration_s,
            "calibration_ticks": 0,
            "home_return_ticks": 0,
            "zero_context_bypass": True,
            "expected_observation_dim": 115,
            "expected_action_dim": 14,
            "policy_state_input_names": ["h_in", "previous_action"],
            "policy_state_output_names": ["h_out", "previous_action_out"],
            "policy_context_input_name": "calibration_context",
            "policy_graph_authoritative_output": True,
            "policy_applied_target_observation": True,
            "reference_start_phase": 0,
            "eval_dynamics_override": {
                "torso_com_offset_m": [0.0, 0.0, 0.0]
            },
            "adapter": adapter.contract(),
        },
        "run": {
            "command_x": 0.0,
            "seed": args.seed,
            "status": result.get("status"),
            "candidate_gate": result.get("candidate_gate"),
            "emergence": emergence_evidence(result, 0.0, args.duration_s),
            "modes": result.get("modes"),
            "dynamics_override": (
                (result.get("insertion_point") or {}).get(
                    "dynamics_override"
                )
            ),
            "policy_io": result.get("policy_io"),
            "response_calibration": result.get("response_calibration"),
            "error": result.get("error"),
            "trace_jsonl": str(args.trace_jsonl),
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "sim_status": result.get("status"),
                "samples": (
                    ((result.get("modes") or {}).get("fitted") or {}).get(
                        "samples"
                    )
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
