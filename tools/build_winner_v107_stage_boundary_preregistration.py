#!/usr/bin/env python3
"""Preregister the minimal V105 stage-boundary behavior diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = ANALYSIS / "winner_v106_response_gate_attribution.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
OUTPUT = ANALYSIS / "winner_v107_stage_boundary_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V107_STAGE_BOUNDARY_PREREGISTRATION_20260724.md"
ATTRIBUTION_SHA256 = (
    "64f1c3130f8ffe5dc245202d1b6c029c79019cd2cc434324292d024ee43d38c8"
)
BASE_PREREG_SHA256 = (
    "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
)
REFERENCE_SHA256 = (
    "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
)
CALIBRATOR_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
CHECKPOINTS = [
    {
        "id": "EXPANDED_INITIAL",
        "relative_path": (
            "stage1_domain_25_percent/2026_07_23_143437_0.onnx"
        ),
        "sha256": (
            "0076e743edb67bc8139d6c70ed6ee2973945c483640180b9de90da190a5a038e"
        ),
        "aliases": ["stage1_0"],
        "cumulative_optimizer_steps": 0,
    },
    {
        "id": "AFTER_DOMAIN_25_PERCENT",
        "relative_path": (
            "stage1_domain_25_percent/2026_07_23_144104_245760.onnx"
        ),
        "sha256": (
            "63f22d7cc253c0533291c4f996edf257a82f30d97a003b558651131268be7871"
        ),
        "aliases": ["stage1_245760", "stage2_0"],
        "cumulative_optimizer_steps": 245_760,
    },
    {
        "id": "AFTER_DOMAIN_50_PERCENT",
        "relative_path": (
            "stage2_domain_50_percent/2026_07_23_150629_245760.onnx"
        ),
        "sha256": (
            "e3c2d93b1d0e6c7a4f10d3d033a1c3b71b64d8737ace1a90bd3560a3c91b3fd5"
        ),
        "aliases": ["stage2_245760", "stage3_0"],
        "cumulative_optimizer_steps": 491_520,
    },
    {
        "id": "DOMAIN_100_PERCENT_HALF",
        "relative_path": (
            "stage3_domain_100_percent/2026_07_23_153215_1003520.onnx"
        ),
        "sha256": (
            "86271b2bec3795df5f801ff640a78c409b69d26ba7c4c591e6329919e408292a"
        ),
        "aliases": ["stage3_1003520"],
        "cumulative_optimizer_steps": 1_495_040,
    },
    {
        "id": "DOMAIN_100_PERCENT_FINAL",
        "relative_path": (
            "stage3_domain_100_percent/2026_07_23_153822_2007040.onnx"
        ),
        "sha256": (
            "24be9a6d565c4d2e841de82d11b1ecf226d27ad9b58a7edeb198a05e28844b13"
        ),
        "aliases": ["stage3_2007040"],
        "cumulative_optimizer_steps": 2_498_560,
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite Winner-v107 preregistration: {path}"
            )
    artifact_root = args.artifact_root.resolve()
    calibrator = args.calibrator.resolve()
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        sha256(ATTRIBUTION) != ATTRIBUTION_SHA256
        or attribution.get("decision")
        != "AUTHORIZE_EVALUATOR_CORRECTION_AND_STAGE_BOUNDARY_DIAGNOSTIC"
        or sha256(BASE_PREREG) != BASE_PREREG_SHA256
        or sha256(REFERENCE) != REFERENCE_SHA256
        or sha256(calibrator) != CALIBRATOR_SHA256
    ):
        raise ValueError("Winner-v107 preregistration inputs changed")

    observed = []
    for row in CHECKPOINTS:
        path = artifact_root / row["relative_path"]
        observed.append(
            {
                **row,
                "bytes": path.stat().st_size,
                "observed_sha256": sha256(path),
            }
        )
    checks = {
        "five_unique_checkpoints_exact": len(observed) == 5
        and len({row["sha256"] for row in observed}) == 5,
        "all_checkpoint_hashes_exact": all(
            row["observed_sha256"] == row["sha256"] for row in observed
        ),
        "all_checkpoint_bytes_exact": all(
            row["bytes"] == 983_117 for row in observed
        ),
        "stage_continuity_aliases_preserved": observed[1]["aliases"]
        == ["stage1_245760", "stage2_0"]
        and observed[2]["aliases"] == ["stage2_245760", "stage3_0"],
        "calibrator_exact": True,
        "attribution_authorizes_diagnostic": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    matrix = [
        {
            "checkpoint_id": checkpoint["id"],
            "checkpoint_sha256": checkpoint["sha256"],
            "plant": "P30_ALL_JOINT",
            "command_x_m_s": command,
            "seed": 167_931_544,
            "configuration": None,
            "transport": {
                "sensor_noise_scales": None,
                "native_quantization": False,
                "additional_action_delay_ticks": 0,
                "imu_delay_ticks": 0,
            },
            "duration_ticks": 600,
        }
        for checkpoint in observed
        for command in (0.0, 0.074, 0.077, 0.08)
    ]
    value = {
        "schema_version": "winner_v107.stage_boundary_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
        ),
        "failed_checks": failed,
        "checks": checks,
        "causal_question": (
            "At which first frozen curriculum boundary does the exact "
            "response-conditioned actor lose the protected nominal gait?"
        ),
        "checkpoints": observed,
        "matrix": {
            "cells": len(matrix),
            "sha256": canonical_sha256(matrix),
            "rows": matrix,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "seed": 167_931_544,
            "plant": "P30_ALL_JOINT",
            "configuration": None,
            "transport": "default_off",
            "scored_ticks": 600,
            "calibration_ticks": 250,
            "home_return_ticks": 250,
        },
        "evaluator_corrections": {
            "cpu_only": (
                "Require jax.default_backend() == 'cpu' and every "
                "jax device.platform == 'cpu'; do not parse rendered device names."
            ),
            "early_return": (
                "Record simulator status/error and fail the cell without "
                "attempting absent environment/readback arithmetic."
            ),
            "formal_v103_result_unchanged": True,
            "thresholds_changed": False,
            "behavior_semantics_changed": False,
        },
        "decision_rule": {
            "per_checkpoint_requires_all_four_cells": True,
            "first_transition": (
                "First checkpoint in cumulative-step order that fails after "
                "at least one earlier checkpoint passes all four cells."
            ),
            "expanded_initial_failure": (
                "Select expansion/export or calibration-prefix integration, "
                "not curriculum training, as the first causal boundary."
            ),
            "no_checkpoint_selection": True,
            "no_reward_or_closest_ranking": True,
            "no_training_until_result": True,
        },
        "input_hashes": {
            "v106_attribution": sha256(ATTRIBUTION),
            "base_preregistration": sha256(BASE_PREREG),
            "reference_features": sha256(REFERENCE),
            "calibrator": sha256(calibrator),
        },
        "authority": {
            "stage_boundary_diagnostic_authorized": not failed,
            "formal_behavior_cells_authorized": 20 if not failed else 0,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v107 stage-boundary preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "The diagnostic evaluates five unique frozen graphs representing all "
        "seven curriculum boundaries. Each graph receives the same four-command "
        "nominal P30 matrix. The first pass-to-fail transition localizes the "
        "collapse; no graph can be selected, ranked by reward, or promoted from "
        "this diagnostic. No hosted training or robot action is authorized.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"matrix_sha256={value['matrix']['sha256']}")
    print(f"sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
