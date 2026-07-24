#!/usr/bin/env python3
"""Attribute the V120 transform hold to float32 operation ordering."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v113_postexport_policies import sha256  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
HOLD = ANALYSIS / "winner_v120_deployment_transform_contract.json"
PREREG = ANALYSIS / "winner_v120_deployment_transform_preregistration.json"
OUTPUT = ANALYSIS / "winner_v120_deployment_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V120_DEPLOYMENT_HOLD_ATTRIBUTION_20260724.md"
EXPECTED = {
    "hold": "0023ab72f929d834790c9df5dd1c5f699e0530ecba7819f3774523d9343fc247",
    "preregistration": (
        "8a86e09bbacccd2849f62f532414f32a18732f759248b6a4c0d107be400727c8"
    ),
}


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V120: {path}")
    source_root = args.source_root.resolve()
    hold = json.loads(HOLD.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    expected_delta = np.asarray(
        prereg["transform"]["selected_normalized_action_delta"],
        dtype=np.float32,
    )
    rows = []
    train_deltas = []
    for spec in prereg["sources"]:
        path = source_root / spec["filename"]
        model = onnx.load(path)
        values = {
            item.name: numpy_helper.to_array(item)
            for item in model.graph.initializer
        }
        delta = np.asarray(values["max_action_delta"][0], dtype=np.float32)
        train_deltas.append(delta)
        difference = delta.astype(np.float64) - expected_delta.astype(
            np.float64
        )
        rows.append(
            {
                "step": spec["step"],
                "source_sha256": sha256(path),
                "train_normalized_action_delta": delta.tolist(),
                "v117_artifact_normalized_action_delta": (
                    expected_delta.tolist()
                ),
                "difference": difference.tolist(),
                "differing_indices": np.flatnonzero(
                    delta != expected_delta
                ).tolist(),
                "train_delta_never_looser": bool(
                    np.all(delta <= expected_delta)
                ),
                "maximum_absolute_difference": float(
                    np.max(np.abs(difference))
                ),
            }
        )
    shared_train_delta = bool(
        len(train_deltas) == 2
        and np.array_equal(train_deltas[0], train_deltas[1])
    )
    checks = {
        "hold_and_preregistration_exact": {
            "hold": sha256(HOLD),
            "preregistration": sha256(PREREG),
        }
        == EXPECTED,
        "v120_held_only_on_source_train_delta_check": (
            hold.get("status")
            == "HOLD_WINNER_V120_DEPLOYMENT_TRANSFORM_CONTRACT"
            and hold.get("failed_checks")
            == ["all_source_train_rate_projections_exact"]
        ),
        "all_other_v120_checks_pass": all(
            passed
            for name, passed in hold["checks"].items()
            if name != "all_source_train_rate_projections_exact"
        ),
        "both_raw_source_hashes_exact": all(
            row["source_sha256"] == spec["sha256"]
            for row, spec in zip(rows, prereg["sources"], strict=True)
        ),
        "both_sources_share_exact_train_delta": shared_train_delta,
        "difference_is_four_one_ulp_tightenings": (
            rows[0]["differing_indices"] == [2, 3, 4, 11]
            and rows[1]["differing_indices"] == [2, 3, 4, 11]
            and all(row["train_delta_never_looser"] for row in rows)
            and all(
                row["maximum_absolute_difference"]
                == float(np.float32(2.0) ** np.float32(-27.0))
                for row in rows
            )
        ),
        "formal_behavior_cells_zero": (
            hold.get("formal_behavior_cells_executed") == 0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v120.deployment_hold_attribution.v1",
        "status": (
            "PASS_WINNER_V120_DEPLOYMENT_HOLD_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V120_DEPLOYMENT_HOLD_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "cause": (
            "The historical V117 artifact derived four normalized deltas "
            "with a different float32 operation order. V119 training and its "
            "raw ONNX export both use rate * dt / action_scale, yielding one "
            "ULP tighter deltas at indices 2,3,4,11."
        ),
        "rows": rows,
        "shared_train_normalized_action_delta": (
            train_deltas[0].tolist() if shared_train_delta else None
        ),
        "shared_train_delta_canonical_sha256": (
            canonical_sha256(train_deltas[0].tolist())
            if shared_train_delta
            else None
        ),
        "decision": (
            "PREREGISTER_V121_EXACT_TRAIN_DELTA_DEPLOYMENT_TRANSFORM"
            if not failed
            else "HOLD_WITHOUT_TRANSFORM_OR_BEHAVIOR"
        ),
        "execution": {
            "training_steps": 0,
            "formal_behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "v121_transform_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "additional_training_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v120 deployment hold attribution\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Decision: `{result['decision']}`\n\n"
        "The hold is a four-joint, one-ULP float32 ordering mismatch. The "
        "trained/exported delta is always equally or more conservative. V121 "
        "must use that exact shared trained delta. No behavior was run.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
