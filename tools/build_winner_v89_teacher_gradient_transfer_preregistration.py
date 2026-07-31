#!/usr/bin/env python3
"""Preregister the Winner-v89 teacher-gradient transfer diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v89_teacher_gradient_transfer_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V89_TEACHER_GRADIENT_TRANSFER_PREREGISTRATION_20260722.md"
V88_RESULT = ANALYSIS / "winner_v88_flat_transport_representation_result.json"
V88_RESULT_SHA256 = "adf4a892b9d19d5b5458e544b576de2188873814128f43b13c0ab232641faaae"
GROUPS = ("recurrent_core", "action_head", "combined_policy")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            raise FileExistsError(f"refusing to overwrite Winner-v89 contract: {path}")
    source = json.loads(V88_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V88_RESULT) != V88_RESULT_SHA256
        or source.get("classification") != "NO_LINEAR_OBSERVABLE_REPRESENTATION_SELECTED"
        or source.get("selected_source_checkpoint_for_mechanism_proof") is not None
        or source.get("selected_feature_family_for_mechanism_proof") is not None
        or source.get("execution", {}).get("optimizer_updates") != 0
        or source.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v89 source result changed")
    source_paths = {
        "builder": Path("tools/build_winner_v89_teacher_gradient_transfer_preregistration.py"),
        "runner": Path("tools/run_winner_v89_teacher_gradient_transfer.py"),
        "tests": Path("tests/test_winner_v89_teacher_gradient_transfer.py"),
        "v88_result": V88_RESULT.relative_to(ROOT),
        "v80_runner": Path("tools/run_winner_v80_pitch_action_head_step.py"),
        "joint_policy": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
        "recurrent_policy": Path("patches/winner_v20_joint_recurrent_support.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v89.teacher_gradient_transfer_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V89_TEACHER_GRADIENT_TRANSFER_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_TWO_ENDPOINT_LOO_GRADIENT_AUDIT_ONLY",
        "question": (
            "Does descending the persistent six-pitch teacher loss on 11 "
            "configurations also descend that loss on the held-out twelfth "
            "configuration, and is transfer carried by recurrence or the action head?"
        ),
        "frozen_source": {
            "v88_result_sha256": V88_RESULT_SHA256,
            "checkpoint_labels_updates": {"half": 705, "final": 755},
            "training_population_episodes": 80,
            "teacher_configurations": 12,
            "teacher_episodes_per_checkpoint": 24,
            "pitch_indices": [2, 3, 4, 11, 12, 13],
            "groups": list(GROUPS),
        },
        "diagnostic": {
            "folds_per_checkpoint": 12,
            "training_mask": "11 configuration IDs, both plants, every valid tick, pitch only",
            "heldout_mask": "one configuration ID, both plants, every valid tick, pitch only",
            "objective": "unchanged graph-bounded action MSE to bounded static teacher",
            "direction_test": (
                "float64 dot(g_train, g_heldout); positive means an infinitesimal "
                "negative training-gradient step also descends heldout loss"
            ),
            "parameter_groups": {
                "recurrent_core": [
                    "obs_weight",
                    "previous_action_weight",
                    "hidden_weight",
                    "hidden_bias",
                ],
                "action_head": ["action_weight", "action_bias"],
                "combined_policy": "union of recurrent_core and action_head",
            },
            "teacher_gradient_evaluations": 48,
            "optimizer_step_or_parameter_commit": False,
        },
        "classification_rule": {
            "group_coherent_for_endpoint": (
                "all 12 leave-one-configuration-out gradient dots are strictly positive"
            ),
            "endpoint_mechanism": (
                "joint if combined, recurrent, and action groups are coherent; "
                "recurrent_only if recurrent is coherent and action is not; "
                "action_only if action is coherent and recurrent is not; otherwise none"
            ),
            "checkpoint_priority": "half, then final",
            "action_only_boundary": (
                "report only; V87 already rejected a frozen-hidden action-head proof"
            ),
            "no_coherent_group": (
                "reject static-teacher gradient transfer and select only a separate "
                "outcome-aligned mechanism diagnostic"
            ),
        },
        "execution_now": {
            "stage2_rollout_episodes": 0,
            "gradient_evaluations": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "diagnostic_authorized": True,
            "training_authorized_now": False,
            "support_gate_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v89 teacher-gradient transfer preregistration",
                "",
                "- Checkpoints: exact V84 half/final at `705 / 755`",
                "- Folds: `12` leave-one-configuration-out per checkpoint",
                "- Groups: recurrent core / action head / combined policy",
                "- Transfer sign: `dot(g_train, g_heldout) > 0`",
                "- Coherence: all `12 / 12` folds positive",
                "- Optimizer updates / support cells / artifacts / robot access: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
