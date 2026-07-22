#!/usr/bin/env python3
"""Preregister the bounded Winner-v84 negative-gradient pitch-head continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_PREREGISTRATION_20260722.md"
)
V83_RESULT = ANALYSIS / "winner_v83_count675_negative_gradient_step_result.json"
V83_RESULT_SHA256 = "1ac6326f6a9b0a703e5035aec186d4bf4601774008ea8b7029629b8f0d22a98d"
SOURCE_COUNT = 675
HALF_COUNT = 705
FINAL_COUNT = 755
CONTINUATION_UPDATES = 80
FRACTIONS = tuple(2.0**-power for power in range(13))
PITCH_INDICES = (2, 3, 4, 11, 12, 13)


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
            raise FileExistsError(f"refusing to overwrite Winner-v84 contract: {path}")
    proof = json.loads(V83_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V83_RESULT) != V83_RESULT_SHA256
        or proof.get("status") != "PASS_WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP"
        or proof.get("decision")
        != "PREREGISTER_BOUNDED_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY"
        or proof.get("failed_checks") != []
        or proof.get("optimization", {}).get("optimizer_count_after") != SOURCE_COUNT
        or proof.get("optimization", {}).get("accepted_fraction") != 0.5
        or proof.get("optimization", {}).get("optimizer_m_and_v_bit_exact") is not True
        or proof.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v84 source proof changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v84_negative_gradient_pitch_head_continuation_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v84_negative_gradient_pitch_head_continuation.py"),
        "tests": Path("tests/test_winner_v84_negative_gradient_pitch_head_continuation.py"),
        "v83_result": V83_RESULT.relative_to(ROOT),
        "v83_preregistration": Path(
            "outputs/analysis/winner_v83_count675_negative_gradient_step_preregistration.json"
        ),
        "v83_runner": Path("tools/run_winner_v83_count675_negative_gradient_step.py"),
        "v82_runner": Path("tools/run_winner_v82_count675_direction_precision_attribution.py"),
        "v81_runner": Path("tools/run_winner_v81_pitch_action_head_continuation.py"),
        "v46_graph_receipt": Path("tools/run_winner_v46_static_target_teacher_training.py"),
        "snapshot_abi": Path("patches/winner_v22_normalized_predictor_v2.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v84.negative_gradient_pitch_head_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION",
        "decision": "AUTHORIZE_ONE_80_UPDATE_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY",
        "source": {
            "optimizer_count": SOURCE_COUNT,
            "snapshot": proof["snapshot"],
            "graph": proof["graph"],
            "result_sha256": V83_RESULT_SHA256,
        },
        "continuation": {
            "optimizer_updates": CONTINUATION_UPDATES,
            "source_optimizer_count": SOURCE_COUNT,
            "half_optimizer_count": HALF_COUNT,
            "final_optimizer_count": FINAL_COUNT,
            "persistent_checkpoints": [HALF_COUNT, FINAL_COUNT],
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "direction_each_update": "instantaneous negative projected pitch-teacher gradient",
            "direction_l2_norm_each_update": "match that update's inherited Adam full parameter-delta L2 norm",
            "fractions_largest_first": list(FRACTIONS),
            "acceptance_rule": "first strict same-batch pitch-teacher-loss descent",
            "mutable_parameter_slices": [
                "action_weight[:, [2,3,4,11,12,13]]",
                "action_bias[[2,3,4,11,12,13]]",
            ],
            "optimizer_m_and_v_transition": "all elements bit-exact preserved across all updates",
            "optimizer_count_transition": [SOURCE_COUNT, FINAL_COUNT],
            "snapshot_every_accepted_update": True,
            "graphs_only_at_counts": [HALF_COUNT, FINAL_COUNT],
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
            "supervised_action_indices": list(PITCH_INDICES),
            "ppo_predictor_anchor_first_tick_gradient_scale": 0.0,
            "heldout_teacher_labels_forbidden": True,
            "attention_or_flat_transport_added": False,
            "coefficient_or_training_length_search": False,
        },
        "pass_rule": {
            "exact_80_updates_676_through_755": True,
            "every_update_first_strict_same_batch_descent": True,
            "same_batch_predictor_loss_bit_exact_every_update": True,
            "all_unselected_parameter_elements_bit_exact": True,
            "all_optimizer_m_and_v_elements_bit_exact": True,
            "all_80_snapshots_digest_readback_exact": True,
            "half_and_final_stateful_onnx_contracts_exact": True,
            "no_posthoc_fraction_length_or_checkpoint_change": True,
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
            "continuation_authorized": True,
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
                "# Winner-v84 negative-gradient pitch-head continuation preregistration",
                "",
                "- Source / half / final counts: `675 / 705 / 755`",
                "- Remaining updates: `80`",
                "- Direction: per-update instantaneous negative pitch-teacher gradient",
                "- Scale: norm-match that update's inherited Adam proposal; backtrack `1` through `1/4096`",
                "- Mutable parameters: six pitch action-weight columns and bias elements only",
                "- Optimizer `m/v`: bit-exact preserved; count alone advances",
                "- Snapshot every update; graphs only at `705 / 755`",
                "- Attention / flat-transport equation: `not added`",
                "- Support / selection / deployment / robot authorized now: `0 / 0 / 0 / 0`",
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
