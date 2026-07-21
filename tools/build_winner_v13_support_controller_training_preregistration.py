#!/usr/bin/env python3
"""Freeze the Winner-v13 100-update support-controller training contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v13_support_controller_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V13_SUPPORT_CONTROLLER_TRAINING_PREREGISTRATION_20260721.md"
CPU_RESULT = ANALYSIS / "winner_v13_support_controller_cpu_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v13_support_controller_training_preregistration.py"),
    "runner": Path("tools/run_winner_v13_support_controller_training.py"),
    "tests": Path("tests/test_winner_v13_support_controller_training.py"),
    "workflow": Path(".github/workflows/winner-v13-support-controller-training.yml"),
    "support_cpu_result": Path("outputs/analysis/winner_v13_support_controller_cpu_result.json"),
    "stage1_result": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"),
    "stage1_preregistration": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_preregistration.json"),
    "v12_training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "v13_training_primitives": Path("patches/winner_v13_normalized_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite support training contract: {path}")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        cpu.get("status") != "PASS_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
        or cpu.get("decision")
        != "AUTHORIZE_SUPPORT_CONTROLLER_TRAINING_PREREGISTRATION_ONLY"
        or cpu.get("failed_checks") != []
        or cpu.get("execution", {}).get("stage2_optimizer_updates") != 1
    ):
        raise ValueError("support CPU result does not authorize preregistration")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v13.support_controller_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V13_SUPPORT_CONTROLLER_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_SUPPORT_CONTROLLER_RUN_ONLY",
        "causal_hypothesis": (
            "The frozen normalized-response encoder contains enough deployable state "
            "for a separately trained action/value head to complete safe automatic "
            "support calibration across the 40-configuration, two-plant envelope."
        ),
        "frozen_training": {
            "source_stage1_snapshot_sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
            "source_stage1_snapshot_bytes": 189027,
            "optimizer_updates": 100,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "trainable_leaves": [
                "action_bias",
                "action_weight",
                "training_only_log_std",
                "training_only_value_bias",
                "training_only_value_weight",
            ],
            "frozen_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "persistent_snapshots": "atomic readback-verified snapshot after every update",
            "persistent_checkpoints": {"half": 50, "final": 100},
        },
        "training_success_rule": (
            "Exact 100 finite Stage-2 updates; Stage-1 remains bit-exact; every "
            "Stage-2 leaf changes; every raw-to-bounded action check is exact; all "
            "100 snapshots and both 115/14/64 ONNX checkpoints validate. Reward "
            "curves do not select or reject a checkpoint."
        ),
        "deferred_architecture": {
            "flat_long_range_kernel": "not selected",
            "reason": (
                "The 250-tick recurrent state has passed observability and one-update "
                "contracts; no evidence yet attributes failure to information transport."
            ),
        },
        "future_gate": {
            "executed_now": False,
            "cells_per_checkpoint": 124,
            "checkpoints": ["half", "final"],
            "pass_rule": "all cells at both checkpoints must pass; no closest selection",
        },
        "execution_now": {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": False,
            "pass_authorizes_only": "a separate 124-cell support/context gate preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v13 support-controller training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: exact passing Stage-1 update-100 snapshot",
                "- Training: `100` CPU-only Stage-2 updates, `80 x 250` ticks each",
                "- Frozen: all Stage-1 encoder and response-prediction leaves",
                "- Recovery: atomic snapshot after every update",
                "- Persistent checkpoints: half `50`, final `100`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "Reward curves are not a success gate. A mechanically valid run only",
                "authorizes the separately frozen 124-cell half/final support gate.",
                "The proposed flat transport kernel remains deferred until evidence",
                "shows that recurrent information transport is the limiting mechanism.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
