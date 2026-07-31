#!/usr/bin/env python3
"""Preregister one Winner-v83 count-675 negative-gradient step proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v83_count675_negative_gradient_step_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP_PREREGISTRATION_20260722.md"
)
V82_RESULT = ANALYSIS / "winner_v82_count675_direction_precision_attribution_result.json"
V82_RESULT_SHA256 = "5d7a3b646fa191b8c46c90173e08ef77177e8a5d06455a39273b5dbf415ebc37"
SOURCE_COUNT = 674
TARGET_COUNT = 675
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
            raise FileExistsError(f"refusing to overwrite Winner-v83 contract: {path}")
    attribution = json.loads(V82_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V82_RESULT) != V82_RESULT_SHA256
        or attribution.get("status")
        != "PASS_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION"
        or attribution.get("classification")
        != "ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS"
        or attribution.get("decision")
        != "PREREGISTER_ONE_COUNT675_NEGATIVE_GRADIENT_STEP_PROOF"
        or attribution.get("failed_checks") != []
        or attribution.get("execution", {}).get("committed_optimizer_updates") != 0
        or attribution.get("source", {}).get("optimizer_count") != SOURCE_COUNT
        or attribution.get("source", {}).get("attempted_optimizer_count") != TARGET_COUNT
        or attribution.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v83 selection evidence changed")
    rows = attribution["loss_geometry"]["negative_gradient_norm_matched_fraction_rows"]
    descending = [row for row in rows if row["loss"] < attribution["loss_geometry"]["teacher_loss_before"]]
    if (
        [row["fraction"] for row in rows] != list(FRACTIONS)
        or not descending
        or descending[0]["fraction"] != 0.5
    ):
        raise ValueError("Winner-v83 negative-gradient grid changed")
    source_paths = {
        "builder": Path("tools/build_winner_v83_count675_negative_gradient_step_preregistration.py"),
        "runner": Path("tools/run_winner_v83_count675_negative_gradient_step.py"),
        "tests": Path("tests/test_winner_v83_count675_negative_gradient_step.py"),
        "v82_result": V82_RESULT.relative_to(ROOT),
        "v82_preregistration": Path(
            "outputs/analysis/winner_v82_count675_direction_precision_attribution_preregistration.json"
        ),
        "v82_runner": Path("tools/run_winner_v82_count675_direction_precision_attribution.py"),
        "v81_result": Path("outputs/analysis/winner_v81_pitch_action_head_continuation_result.json"),
        "v81_runner": Path("tools/run_winner_v81_pitch_action_head_continuation.py"),
        "v46_graph_receipt": Path("tools/run_winner_v46_static_target_teacher_training.py"),
        "snapshot_abi": Path("patches/winner_v22_normalized_predictor_v2.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v83.count675_negative_gradient_step_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP",
        "decision": "AUTHORIZE_EXACTLY_ONE_COUNT675_NEGATIVE_GRADIENT_STEP_PROOF",
        "source": {
            "optimizer_count": SOURCE_COUNT,
            "target_optimizer_count": TARGET_COUNT,
            "snapshot": attribution["source"]["snapshot"],
            "attribution_result_sha256": V82_RESULT_SHA256,
            "episode_receipts_sha256": attribution["source"]["episode_receipts_sha256"],
        },
        "step": {
            "rollout_update_index": SOURCE_COUNT,
            "direction": "instantaneous negative projected pitch-teacher gradient",
            "direction_l2_norm": "match the inherited Adam full parameter-delta L2 norm",
            "fractions_largest_first": list(FRACTIONS),
            "acceptance_rule": "first strict same-batch pitch-teacher-loss descent",
            "expected_first_descent_fraction_from_read_only_attribution": 0.5,
            "mutable_parameter_slices": [
                "action_weight[:, [2,3,4,11,12,13]]",
                "action_bias[[2,3,4,11,12,13]]",
            ],
            "optimizer_count_transition": [SOURCE_COUNT, TARGET_COUNT],
            "optimizer_m_and_v_transition": "all elements bit-exact preserved",
            "snapshot_count": 1,
            "stateful_onnx_count": 1,
            "attention_or_flat_transport_added": False,
        },
        "pass_rule": {
            "v82_geometry_bit_exact_reproduced": True,
            "first_strict_descent_fraction_selected": True,
            "only_pitch_action_head_parameter_elements_change": True,
            "all_optimizer_m_and_v_elements_bit_exact": True,
            "same_batch_predictor_loss_bit_exact": True,
            "snapshot_digest_readback_exact": True,
            "stateful_onnx_contract_exact": True,
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
            "one_step_proof_authorized": True,
            "pass_authorizes_only": "preregistration of a bounded negative-gradient pitch-head continuation",
            "continuation_authorized_now": False,
            "support_gate_authorized": False,
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
                "# Winner-v83 count-675 negative-gradient step preregistration",
                "",
                "- Source / target count: `674 / 675`",
                "- Direction: instantaneous negative pitch-teacher gradient, norm-matched to V82 Adam delta",
                "- Frozen fractions: `1` through `1/4096`; first strict descent only",
                "- Mutable parameters: six pitch action-weight columns and bias elements",
                "- Optimizer `m/v`: bit-exact preserved; count alone advances",
                "- Snapshot / non-selected ONNX: `1 / 1`",
                "- Continuation / support / selection / robot authorized now: `0 / 0 / 0 / 0`",
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
