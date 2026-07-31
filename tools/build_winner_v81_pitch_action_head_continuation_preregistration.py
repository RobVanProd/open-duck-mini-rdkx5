#!/usr/bin/env python3
"""Preregister the bounded Winner-v81 pitch-action-head continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v81_pitch_action_head_continuation_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION_PREREGISTRATION_20260722.md"
V80_RESULT = ANALYSIS / "winner_v80_pitch_action_head_step_result.json"
V80_RESULT_SHA256 = "7cff575bf948705bfd3b3d9c5a4867ce0a7611a5800f3b4051996446714181db"
SOURCE_COUNT = 656
HALF_COUNT = 705
FINAL_COUNT = 755
CONTINUATION_UPDATES = 99
FRACTIONS = [
    1.0,
    0.5,
    0.25,
    0.125,
    0.0625,
    0.03125,
    0.015625,
    0.0078125,
    0.00390625,
    0.001953125,
    0.0009765625,
]


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
            raise FileExistsError(f"refusing to overwrite Winner-v81 contract: {path}")
    proof = json.loads(V80_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V80_RESULT) != V80_RESULT_SHA256
        or proof.get("status") != "PASS_WINNER_V80_PITCH_ACTION_HEAD_STEP"
        or proof.get("decision")
        != "PREREGISTER_BOUNDED_PITCH_ACTION_HEAD_CONTINUATION_ONLY"
        or proof.get("failed_checks") != []
        or proof.get("optimization", {}).get("optimizer_count_after") != SOURCE_COUNT
        or proof.get("optimization", {}).get("accepted_fraction") != 1.0
        or proof.get("optimization", {}).get("predictor_loss_before")
        != proof.get("optimization", {}).get("predictor_loss_after")
        or proof.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v81 source proof changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v81_pitch_action_head_continuation_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v81_pitch_action_head_continuation.py"),
        "tests": Path("tests/test_winner_v81_pitch_action_head_continuation.py"),
        "v80_result": Path("outputs/analysis/winner_v80_pitch_action_head_step_result.json"),
        "v80_contract": Path("outputs/analysis/winner_v80_pitch_action_head_step_contract.json"),
        "v80c_correction": Path(
            "outputs/analysis/winner_v80c_action_boundary_check_correction.json"
        ),
        "v80c_builder": Path(
            "tools/build_winner_v80c_action_boundary_check_correction.py"
        ),
        "v46_graph_receipt": Path("tools/run_winner_v46_static_target_teacher_training.py"),
        "snapshot_abi": Path("patches/winner_v22_normalized_predictor_v2.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v81.pitch_action_head_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION",
        "decision": "AUTHORIZE_ONE_99_UPDATE_PITCH_ACTION_HEAD_CONTINUATION_ONLY",
        "source": {
            "v80_result_sha256": V80_RESULT_SHA256,
            "snapshot": proof["snapshot"],
            "graph": proof["graph"],
            "optimizer_count": SOURCE_COUNT,
        },
        "continuation": {
            "optimizer_updates": CONTINUATION_UPDATES,
            "source_optimizer_count": SOURCE_COUNT,
            "half_optimizer_count": HALF_COUNT,
            "final_optimizer_count": FINAL_COUNT,
            "persistent_checkpoints": [HALF_COUNT, FINAL_COUNT],
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "pitch_action_indices": [2, 3, 4, 11, 12, 13],
            "mutable_parameter_slices": [
                "action_weight[:, [2,3,4,11,12,13]]",
                "action_bias[[2,3,4,11,12,13]]",
            ],
            "preserve_bit_exact": (
                "all other parameter elements and optimizer moment elements"
            ),
            "fractions_largest_first": FRACTIONS,
            "acceptance_rule": "first strict same-batch pitch-teacher-loss descent",
            "conditional_moment_reset": (
                "only the two mutable moment slices, only after inherited-grid "
                "exhaustion with nonnegative teacher-gradient dot proposed delta"
            ),
            "snapshot_every_accepted_update": True,
        },
        "objective": {
            "teacher_configuration_ids": [
                "COM_X_NEG",
                "COM_CORNER_00",
                "COM_CORNER_01",
                "COM_CORNER_02",
                "COM_CORNER_03",
                "COM_CORNER_07",
                "OPTIONAL_AGGREGATE_HEAVY_AFT",
                "DISCOVERY_02",
                "DISCOVERY_03",
                "DISCOVERY_06",
                "DISCOVERY_09",
                "DISCOVERY_10",
            ],
            "pitch_teacher_scale": 58.436370849609375,
            "supervised_action_indices": [2, 3, 4, 11, 12, 13],
            "ppo_predictor_anchor_first_tick_gradient_scale": 0.0,
            "heldout_teacher_labels_forbidden": True,
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
        "pass_rule": {
            "exact_99_updates_657_through_755": True,
            "every_update_strict_same_batch_descent": True,
            "same_batch_predictor_loss_bit_exact_every_update": True,
            "all_unselected_parameter_and_moment_elements_bit_exact": True,
            "all_99_snapshots_digest_readback_exact": True,
            "half_and_final_stateful_onnx_contracts_exact": True,
            "no_posthoc_length_coefficient_or_checkpoint_change": True,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "training_authorized": True,
            "pass_authorizes_only": "the unchanged persistence gate for counts 705 and 755",
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
                "# Winner-v81 pitch-action-head continuation preregistration",
                "",
                "- Source / half / final counts: `656 / 705 / 755`",
                "- Continuation updates: `99`",
                "- Mutable parameters: six pitch action-weight columns and bias elements only",
                "- Recurrent core, predictor, non-pitch outputs, and unselected moments: bit-exact frozen",
                "- Snapshot every accepted update; graphs only at `705 / 755`",
                "- Support / selection / deployment / robot authorized now: `0 / 0 / 0 / 0`",
                "- Attention / flat-transport equation: `not added`",
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
