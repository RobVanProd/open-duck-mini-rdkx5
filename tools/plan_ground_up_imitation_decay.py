#!/usr/bin/env python3
"""Gate the imitation-decay family on consecutive gait-emergence evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_eval(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if payload.get("schema_version") != "ground_up_policy_eval.v1":
        raise ValueError(f"unsupported evaluator schema in {path}")
    return payload


def gait_pass(payload: dict[str, Any]) -> bool:
    aggregate = payload.get("aggregate") or {}
    return (
        payload.get("status") == "PASS_GAIT_EMERGENCE_CHECKPOINT"
        and aggregate.get("checkpoint_emergence_pass") is True
        and aggregate.get("moving_emergence_pass") is True
        and aggregate.get("zero_command_finite_recorded") is True
    )


def build_decision(args: argparse.Namespace) -> dict[str, Any]:
    eval_paths = [Path(item).resolve() for item in args.evaluations]
    evaluations = [load_eval(path) for path in eval_paths]
    evidence = [
        {
            "path": str(path),
            "sha256": sha256(path),
            "status": payload.get("status"),
            "checkpoint_emergence_pass": (payload.get("aggregate") or {}).get(
                "checkpoint_emergence_pass"
            ),
            "policy_sha256": (payload.get("inputs") or {}).get("policy_sha256"),
        }
        for path, payload in zip(eval_paths, evaluations, strict=True)
    ]
    distinct_policies = {
        item["policy_sha256"] for item in evidence if item["policy_sha256"]
    }
    restore_checkpoint = Path(args.restore_checkpoint).resolve()
    valid_scale = float(args.current_imitation_scale) > 0.0
    valid_timesteps = int(args.additional_timesteps) > 0
    ready = (
        len(evaluations) == 2
        and all(gait_pass(payload) for payload in evaluations)
        and len(distinct_policies) == 2
        and restore_checkpoint.exists()
        and valid_scale
        and valid_timesteps
    )

    current_scale = float(args.current_imitation_scale)
    next_scale = current_scale * 0.5
    command = None
    if ready:
        command = [
            "python",
            "-m",
            "playground.open_duck_mini_v2.runner",
            "--output_dir",
            str(Path(args.next_output_dir)),
            "--restore_checkpoint_path",
            str(restore_checkpoint),
            "--num_timesteps",
            str(int(args.additional_timesteps)),
            "--ppo_seed",
            str(int(args.seed)),
            "--ppo_num_envs",
            str(int(args.num_envs)),
            "--ppo_num_evals",
            str(int(args.num_evals)),
            "--ppo_unroll_length",
            str(int(args.unroll_length)),
            "--ppo_batch_size",
            str(int(args.batch_size)),
            "--ppo_num_minibatches",
            str(int(args.num_minibatches)),
            "--ppo_num_updates_per_batch",
            str(int(args.num_updates_per_batch)),
            "--imitation_scale",
            format(next_scale, ".17g"),
        ]
        if args.reference_feature_table:
            command.extend(
                [
                    "--reference_feature_table_path",
                    str(Path(args.reference_feature_table).resolve()),
                ]
            )

    reasons = []
    if len(evaluations) != 2:
        reasons.append("exactly_two_consecutive_evaluations_required")
    if not all(gait_pass(payload) for payload in evaluations):
        reasons.append("consecutive_gait_emergence_gate_not_passed")
    if len(distinct_policies) != 2:
        reasons.append("evaluations_do_not_identify_two_distinct_checkpoints")
    if not restore_checkpoint.exists():
        reasons.append("restore_checkpoint_missing")
    if not valid_scale:
        reasons.append("current_imitation_scale_must_be_positive")
    if not valid_timesteps:
        reasons.append("additional_timesteps_must_be_positive")

    return {
        "schema_version": "ground_up_imitation_decay_decision.v1",
        "status": "READY_IMITATION_DECAY_STAGE" if ready else "HOLD_IMITATION_DECAY_STAGE",
        "ready": ready,
        "reasons": reasons,
        "mechanism": {
            "current_imitation_scale": current_scale,
            "next_imitation_scale": next_scale,
            "decay_factor": 0.5,
            "trigger": "two_consecutive_distinct_checkpoint_gait_emergence_passes",
        },
        "evidence": evidence,
        "resume": {
            "checkpoint": str(restore_checkpoint),
            "additional_timesteps": int(args.additional_timesteps),
            "argv": command,
        },
        "hardware_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluations", nargs=2, required=True)
    parser.add_argument("--restore-checkpoint", required=True)
    parser.add_argument("--current-imitation-scale", type=float, required=True)
    parser.add_argument("--additional-timesteps", type=int, required=True)
    parser.add_argument("--next-output-dir", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--num-envs", type=int, default=256)
    parser.add_argument("--num-evals", type=int, default=5)
    parser.add_argument("--unroll-length", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--num-minibatches", type=int, default=32)
    parser.add_argument("--num-updates-per-batch", type=int, default=4)
    parser.add_argument("--reference-feature-table", default=None)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    payload = build_decision(args)
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "reasons": payload["reasons"]}))


if __name__ == "__main__":
    main()
