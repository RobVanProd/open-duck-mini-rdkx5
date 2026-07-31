#!/usr/bin/env python3
"""Freeze one saved-result-only Winner-v31 replay attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v31_cross_worker_replay_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION_PREREGISTRATION_20260722.md"
V30_HOLD = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v31_cross_worker_replay_attribution_preregistration.py"),
    "runner": Path("tools/run_winner_v31_cross_worker_replay_attribution.py"),
    "runner_tests": Path("tests/test_winner_v31_cross_worker_replay_attribution.py"),
    "preregistration_tests": Path("tests/test_winner_v31_cross_worker_replay_attribution_preregistration.py"),
    "result_importer": Path("tools/import_winner_v31_cross_worker_replay_attribution.py"),
    "result_importer_tests": Path("tests/test_winner_v31_cross_worker_replay_attribution_import.py"),
    "workflow": Path(".github/workflows/winner-v31-cross-worker-replay-attribution.yml"),
    "winner_v29_result": Path("outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_result.json"),
    "winner_v30_contract": Path("outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"),
    "winner_v30_hold_correction": Path("outputs/analysis/winner_v30_one_update_hold_import_correction.json"),
    "winner_v30_hold_result": Path("outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"),
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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v31 preregistration")
    hold = json.loads(V30_HOLD.read_text(encoding="utf-8"))
    if (
        hold.get("status")
        != "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or hold.get("failed_checks")
        != [
            "exact_v29_anchor_loss_gradient_and_scale_reproduced",
            "exact_v29_update_200_batch_reproduced",
        ]
        or hold.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v30 HOLD did not authorize saved-result attribution")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v31.cross_worker_replay_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_SAVED_RESULT_ONLY_REPLAY_ATTRIBUTION",
        "question": (
            "Are Winner-v30's two exact-replay holds confined to bounded cross-worker "
            "float32 variation while the single update, snapshot, and ONNX contracts pass?"
        ),
        "attribution_rule": {
            "failed_checks_must_equal": [
                "exact_v29_anchor_loss_gradient_and_scale_reproduced",
                "exact_v29_update_200_batch_reproduced",
            ],
            "all_non_replay_checks_must_pass": True,
            "float32_loss_pairs": [
                "anchor_loss_before",
                "ppo_loss",
                "normalized_predictor_loss",
            ],
            "maximum_ulp_distance_each": 8,
            "minimum_anchor_improvement_to_cross_worker_delta_ratio": 10_000.0,
            "same_failure_count_required": True,
            "same_selected_element_count_required": True,
            "same_maximum_selected_action_delta_required": True,
            "snapshot_graph_and_update_checks_must_pass": True,
            "old_hold_result_rewritten": False,
            "thresholds_in_old_contract_changed": False,
            "rerun_authorized": False,
        },
        "decision_tree": {
            "bounded_float_replay_only": (
                "AUTHORIZE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_"
                "USING_PRESERVED_COUNT_201_ARTIFACT_ONLY"
            ),
            "unresolved": "DO_NOT_USE_WINNER_V30_ARTIFACT_FOR_TRAINING",
        },
        "execution_now": {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen prefix right-pitch anchor training preregistration "
                "using the preserved count-201 artifact"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v31 cross-worker replay attribution preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Maximum per-loss float32 distance: `8 ULP`",
                "- Minimum update-improvement / replay-delta ratio: `10,000x`",
                "- New simulation / optimizer / support / locomotion / robot: `0 / 0 / 0 / 0 / 0`",
                "",
                value["question"],
                "",
                "The attribution uses only committed V29/V30 JSON evidence. It does not",
                "rerun or rewrite Winner-v30 and cannot itself authorize training or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
