#!/usr/bin/env python3
"""Evaluate one locomotion tick after a shadow-recurrent response prefix."""

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

import t13_shadow_hidden_eval_adapter as adapter  # noqa: E402


COMMAND_X = 0.074
COM_X_M = -0.05
SEED = 167931544
CALIBRATION_TICKS = 250
CALIBRATOR_SHA256 = (
    "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
)


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
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--trace-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    policy = args.policy.resolve()
    playground = args.playground_root.resolve()
    fit_path = args.fit.resolve()
    reference = args.reference_feature_table.resolve()
    calibrator = args.calibrator.resolve()
    if sha256(calibrator) != CALIBRATOR_SHA256:
        raise RuntimeError("T13 calibrator changed")
    fit = json.loads(fit_path.read_text(encoding="utf-8"))
    module = adapter.load_module()
    args.trace_jsonl.parent.mkdir(parents=True, exist_ok=True)
    result = module.run_closed_loop_sim(
        module.ClosedLoopConfig(
            policy_path=policy,
            fit=fit,
            playground_root=playground,
            command_x=COMMAND_X,
            duration_s=0.02,
            bridge_mode="fitted",
            expected_observation_dim=115,
            expected_action_dim=14,
            task="flat_terrain_backlash",
            seed=SEED,
            eval_role="candidate",
            reset_mode="home-support",
            policy_state_input_names=("h_in", "previous_action"),
            policy_state_output_names=("h_out", "previous_action_out"),
            policy_context_input_name="calibration_context",
            policy_graph_authoritative_output=True,
            response_calibrator_path=calibrator,
            response_calibrator_sha256=CALIBRATOR_SHA256,
            response_calibration_ticks=CALIBRATION_TICKS,
            response_home_return_ticks=0,
            response_preserve_handoff_state=True,
            response_shadow_policy_hidden=True,
            policy_applied_target_observation=True,
            eval_dynamics_override={
                "torso_com_offset_m": [COM_X_M, 0.0, 0.0]
            },
            trace_jsonl=args.trace_jsonl.resolve(),
            trace_full_obs=True,
            reference_feature_table_path=reference,
            reference_start_phase=0,
        )
    )
    payload = {
        "schema_version": "open_duck.t13_shadow_hidden_block.v1",
        "status": "COMPLETE_T13_SHADOW_HIDDEN_BLOCK",
        "inputs": {
            "command_x_m_s": COMMAND_X,
            "seed": SEED,
            "duration_s": 0.02,
            "calibration_ticks": CALIBRATION_TICKS,
            "home_return_ticks": 0,
            "preserve_handoff_state": True,
            "shadow_policy_hidden": True,
            "expected_observation_dim": 115,
            "expected_action_dim": 14,
            "policy_state_input_names": ["h_in", "previous_action"],
            "policy_state_output_names": ["h_out", "previous_action_out"],
            "policy_context_input_name": "calibration_context",
            "policy_graph_authoritative_output": True,
            "policy_applied_target_observation": True,
            "reference_start_phase": 0,
            "eval_dynamics_override": {
                "torso_com_offset_m": [COM_X_M, 0.0, 0.0]
            },
        },
        "sources": {
            "policy": {"path": str(policy), "sha256": sha256(policy)},
            "fit": {"path": str(fit_path), "sha256": sha256(fit_path)},
            "calibrator": {
                "path": str(calibrator),
                "sha256": sha256(calibrator),
            },
            "reference": {
                "path": str(reference),
                "sha256": sha256(reference),
            },
        },
        "run": {
            "status": result.get("status"),
            "candidate_gate": result.get("candidate_gate"),
            "modes": result.get("modes"),
            "dynamics_override": (
                (result.get("insertion_point") or {}).get(
                    "dynamics_override"
                )
            ),
            "policy_io": result.get("policy_io"),
            "response_calibration": result.get("response_calibration"),
            "error": result.get("error"),
            "trace_jsonl": str(args.trace_jsonl.resolve()),
        },
        "execution": {
            "platform": "cpu",
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
