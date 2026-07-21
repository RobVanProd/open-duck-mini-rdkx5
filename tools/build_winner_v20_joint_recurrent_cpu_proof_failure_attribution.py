#!/usr/bin/env python3
"""Record the invalid first Winner-v20 CPU proof without changing its outcome."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_contract.json"
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_cpu_contract.py"
OUTPUT = ANALYSIS / "winner_v20_joint_recurrent_cpu_proof_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_CPU_PROOF_FAILURE_ATTRIBUTION_20260721.md"


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite failure attribution: {path}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner_source = RUNNER.read_text(encoding="utf-8")
    if (
        contract.get("status")
        != "FROZEN_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or contract.get("decision")
        != "AUTHORIZE_ONE_JOINT_RECURRENT_PPO_PROOF_UPDATE_ONLY"
        or '"stage": "joint_recurrent_stage2"' not in runner_source
        or "loaded = full.load_snapshot(snapshot)" not in runner_source
    ):
        raise ValueError("Winner-v20 failed-proof source changed")
    payload = {
        "schema_version": "winner_v20.joint_recurrent_cpu_proof_failure_attribution.v1",
        "status": "INVALID_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT_PROOF",
        "decision": "CORRECT_ONLY_JOINT_SNAPSHOT_READER_AND_FRESHLY_PREREGISTER",
        "failed_run": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": 29851858965,
            "github_run_attempt": 1,
            "github_run_head_sha": "39ae6045e0324d05632d2bc1c63d9c3b84c10830",
            "github_job_id": 88706461568,
            "github_artifact_id": 8503746957,
            "github_artifact_name": "winner-v20-joint-recurrent-cpu-29851858965",
            "artifact_zip_bytes": 121956,
            "artifact_zip_sha256": (
                "2a340086d940b3b134cdbc377a23fd075add1c93b7a4092f37831aee7e1a4134"
            ),
            "artifact_members": {
                "winner-v20-joint-recurrent-cpu-work/winner_v20_joint_recurrent_update_001.npz": {
                    "bytes": 78649,
                    "sha256": (
                        "7371e93671d52982bdbb913a32c9070226b3387403654e013cf48a0591f427f8"
                    ),
                },
                "winner-v20-joint-recurrent-cpu-work/winner_v20_joint_recurrent_update_001.onnx": {
                    "bytes": 54896,
                    "sha256": (
                        "b375ca14dc9c5417f6c006e07efa30ebdaff3d5d3fe7a6d0d6e8d5089139ab5f"
                    ),
                },
            },
            "formal_result_present": False,
        },
        "failure": {
            "step": "snapshot readback after rollout, gradient, Adam update, export, and save",
            "exception": "ValueError: snapshot stage is invalid",
            "cause": (
                "The inherited Winner-v12 loader accepts only stage1/stage2 labels and "
                "hard-codes their seven-leaf or five-leaf optimizer schemas. Winner-v20 "
                "honestly writes joint_recurrent_stage2 with the preregistered nine-leaf "
                "optimizer, so that inherited loader cannot validate this snapshot."
            ),
            "behavior_or_objective_semantics_change": False,
            "numerical_gate_relaxed": False,
            "proof_valid": False,
        },
        "correction_boundary": {
            "only_change": (
                "add a Winner-v20 readback loader that requires the exact "
                "joint_recurrent_stage2 label, all base parameter leaves, and the exact "
                "nine preregistered optimizer leaves; use it only for Winner-v20 snapshots"
            ),
            "preserve": [
                "rollout, population, seed, reward, masks, and action bounds",
                "trainable and frozen leaf sets",
                "all gradient, replay, ONNX, and snapshot equality thresholds",
                "one proof update and zero formal support/robot work",
            ],
            "fresh_run_required": True,
            "workflow_rerun_permitted": False,
        },
        "execution": {
            "invalid_proof_optimizer_updates": 1,
            "authorized_training_arm_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "joint_recurrent_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": (
                "the exact snapshot-reader correction and a freshly preregistered CPU proof"
            ),
        },
        "sources": {
            "failed_contract_lf_sha256": lf_sha256(CONTRACT),
            "failed_runner_lf_sha256": lf_sha256(RUNNER),
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v20 CPU proof failure attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Failed run / artifact: `29851858965 / 8503746957`",
                "- Formal result: absent",
                "- Training arm / support cells / robot: `0 / 0 / 0`",
                "",
                "The proof reached snapshot readback, then the inherited loader rejected",
                "the new stage label before it could encounter its also-incompatible",
                "five-leaf optimizer assumption. The correction adds an exact Winner-v20",
                "nine-leaf reader; it changes no rollout, objective, or threshold. A fresh",
                "run is required and the failed run remains invalid evidence.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
