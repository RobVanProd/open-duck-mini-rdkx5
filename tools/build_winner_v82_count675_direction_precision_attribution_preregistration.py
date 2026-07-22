#!/usr/bin/env python3
"""Preregister the zero-update Winner-v82 count-675 direction/precision audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v82_count675_direction_precision_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION_PREREGISTRATION_20260722.md"
)
V81_RESULT = ANALYSIS / "winner_v81_pitch_action_head_continuation_result.json"
V81_PREREGISTRATION = (
    ANALYSIS / "winner_v81_pitch_action_head_continuation_preregistration.json"
)
V81_RESULT_SHA256 = "dfdd8088214b32dc7db018ede13bcac92c4d17e9e880030490d9d4c42ec021e2"
SOURCE_COUNT = 674
ATTEMPT_COUNT = 675
ORIGINAL_FRACTIONS = tuple(2.0**-power for power in range(11))
EXTENDED_ADAM_FRACTIONS = tuple(2.0**-power for power in range(21))
NEGATIVE_GRADIENT_FRACTIONS = tuple(2.0**-power for power in range(13))


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


def classify_count675(
    *,
    loss_before: float,
    adam_gradient_dot_delta: float,
    adam_losses: Sequence[float],
    negative_gradient_losses: Sequence[float],
    adam_parameter_changes: Sequence[int],
    negative_gradient_parameter_changes: Sequence[int],
) -> tuple[str, str]:
    original = adam_losses[: len(ORIGINAL_FRACTIONS)]
    extended = adam_losses[len(ORIGINAL_FRACTIONS) :]
    if any(loss < loss_before for loss in original):
        return (
            "ORIGINAL_COUNT675_GRID_EXHAUSTION_DID_NOT_REPRODUCE",
            "STOP_REPRODUCTION_MISMATCH",
        )
    if adam_gradient_dot_delta >= 0.0:
        return "ADAM_DIRECTION_NOT_FIRST_ORDER_DESCENT", "STOP_REPRODUCTION_MISMATCH"
    if any(loss < loss_before for loss in extended):
        return (
            "ADAM_DESCENT_EXISTS_BELOW_ONE_OVER_1024",
            "PREREGISTER_ONE_COUNT675_EXTENDED_ADAM_STEP_PROOF",
        )
    if any(loss < loss_before for loss in negative_gradient_losses):
        return (
            "ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS",
            "PREREGISTER_ONE_COUNT675_NEGATIVE_GRADIENT_STEP_PROOF",
        )
    extended_changes = adam_parameter_changes[len(ORIGINAL_FRACTIONS) :]
    extended_pairs = [
        loss
        for loss, changed in zip(extended, extended_changes, strict=True)
        if changed
    ]
    negative_tail_losses = negative_gradient_losses[-5:]
    negative_tail_changes = negative_gradient_parameter_changes[-5:]
    negative_pairs = [
        loss
        for loss, changed in zip(
            negative_tail_losses,
            negative_tail_changes,
            strict=True,
        )
        if changed
    ]
    changed_losses = extended_pairs + negative_pairs
    if changed_losses and all(loss == loss_before for loss in changed_losses):
        return "FLOAT32_TEACHER_LOSS_PLATEAU", "STOP_ISOLATED_PITCH_HEAD_ROUTE"
    if not changed_losses:
        return "FLOAT32_PARAMETER_PLATEAU", "STOP_ISOLATED_PITCH_HEAD_ROUTE"
    return "UNRESOLVED_COUNT675_GEOMETRY", "STOP_FOR_REVIEW"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v82 contract: {path}")
    stopped = json.loads(V81_RESULT.read_text(encoding="utf-8"))
    stop = stopped.get("stop", {})
    snapshots = stopped.get("snapshot_manifest", [])
    if (
        sha256(V81_RESULT) != V81_RESULT_SHA256
        or stopped.get("status") != "HOLD_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION"
        or stopped.get("decision") != "DO_NOT_RUN_PERSISTENCE_GATE"
        or stopped.get("execution", {}).get("optimizer_updates") != 18
        or stopped.get("persistent_checkpoints") != []
        or [row.get("completed_updates") for row in snapshots]
        != list(range(657, 675))
        or snapshots[-1].get("sha256")
        != "bfcc8f4c3cc22e3259decafb2f5a557a55e94534a2464933d061b6facbe80057"
        or stop.get("attempted_completed_count") != ATTEMPT_COUNT
        or stop.get("moment_reset_attempted") is not False
        or not float(stop.get("gradient_dot_proposed_delta", 0.0)) < 0.0
        or [row.get("fraction") for row in stop.get("backtracking_rows", [])]
        != list(ORIGINAL_FRACTIONS)
        or any(
            row.get("loss", float("-inf")) < stop.get("loss_before", float("inf"))
            for row in stop.get("backtracking_rows", [])
        )
    ):
        raise ValueError("Winner-v82 source stop changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v82_count675_direction_precision_attribution_preregistration.py"
        ),
        "runner": Path(
            "tools/run_winner_v82_count675_direction_precision_attribution.py"
        ),
        "tests": Path(
            "tests/test_winner_v82_count675_direction_precision_attribution.py"
        ),
        "v81_result": V81_RESULT.relative_to(ROOT),
        "v81_preregistration": V81_PREREGISTRATION.relative_to(ROOT),
        "v81_runner": Path("tools/run_winner_v81_pitch_action_head_continuation.py"),
        "v80_result": Path("outputs/analysis/winner_v80_pitch_action_head_step_result.json"),
        "v80c_builder": Path("tools/build_winner_v80c_action_boundary_check_correction.py"),
        "snapshot_abi": Path("patches/winner_v22_normalized_predictor_v2.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v82.count675_direction_precision_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_COUNT675_DIRECTION_PRECISION_ATTRIBUTION_ONLY",
        "source": {
            "optimizer_count": SOURCE_COUNT,
            "attempted_optimizer_count": ATTEMPT_COUNT,
            "snapshot": snapshots[-1],
            "stopped_result_sha256": V81_RESULT_SHA256,
            "loss_before": stop["loss_before"],
            "gradient_dot_proposed_delta": stop["gradient_dot_proposed_delta"],
        },
        "diagnostic": {
            "rollout_update_index": SOURCE_COUNT,
            "original_adam_fractions": list(ORIGINAL_FRACTIONS),
            "extended_adam_fractions": list(EXTENDED_ADAM_FRACTIONS),
            "negative_gradient_fractions": list(NEGATIVE_GRADIENT_FRACTIONS),
            "negative_gradient_norm": "match the full inherited Adam parameter-delta L2 norm",
            "arithmetic": "runtime float32 JAX objective and float32 parameters",
            "record_parameter_change_count_and_loss_ulp": True,
            "committed_optimizer_updates": 0,
            "attention_or_flat_transport_added": False,
            "coefficient_or_training_length_search": False,
        },
        "classification_order": [
            "ORIGINAL_COUNT675_GRID_EXHAUSTION_DID_NOT_REPRODUCE",
            "ADAM_DIRECTION_NOT_FIRST_ORDER_DESCENT",
            "ADAM_DESCENT_EXISTS_BELOW_ONE_OVER_1024",
            "ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS",
            "FLOAT32_TEACHER_LOSS_PLATEAU",
            "FLOAT32_PARAMETER_PLATEAU",
            "UNRESOLVED_COUNT675_GEOMETRY",
        ],
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "diagnostic_authorized": True,
            "pass_authorizes_only": "one separately preregistered count-675 step proof selected by the frozen classification",
            "continuation_authorized": False,
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
                "# Winner-v82 count-675 direction/precision attribution preregistration",
                "",
                "- Source / attempted count: `674 / 675`",
                "- Existing Adam grid: reproduce through `1/1024`",
                "- Extended Adam grid: continue through `1/1,048,576`",
                "- Counterfactual: norm-matched instantaneous negative gradient through `1/4096`",
                "- Committed optimizer updates / support cells / robot access: `0 / 0 / 0`",
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
