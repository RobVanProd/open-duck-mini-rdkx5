#!/usr/bin/env python3
"""Preregister the read-only Winner-v87 linear pitch-head feasibility audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v87_pitch_head_linear_feasibility_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY_PREREGISTRATION_20260722.md"
)
V86_RESULT = ANALYSIS / "winner_v86_residual_pitch_causal_result.json"
V86_RESULT_SHA256 = "11225fed5b87a884fa149b1aa6f60ac904017e5ab35fac4587aa8a3f3b10a8d5"
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
CHECKPOINTS = {"half": 705, "final": 755}
TEACHER_CONFIGURATION_COUNT = 16
TEACHER_EPISODES_PER_CHECKPOINT = 32


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
            raise FileExistsError(f"refusing to overwrite Winner-v87 contract: {path}")

    source = json.loads(V86_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V86_RESULT) != V86_RESULT_SHA256
        or source.get("status")
        != "PASS_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC"
        or source.get("findings", {}).get("classification_counts", {}).get(
            "pitch_output_causal"
        )
        != 12
        or source.get("findings", {}).get("support_pass_counts")
        != {"full_teacher": 12, "graph": 0, "nonpitch_zero": 0, "pitch_teacher": 12}
        or source.get("execution", {}).get("optimizer_updates") != 0
        or source.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v87 causal source changed")

    source_paths = {
        "builder": Path(
            "tools/build_winner_v87_pitch_head_linear_feasibility_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v87_pitch_head_linear_feasibility.py"),
        "tests": Path("tests/test_winner_v87_pitch_head_linear_feasibility.py"),
        "v86_result": V86_RESULT.relative_to(ROOT),
        "v84_result": Path(
            "outputs/analysis/winner_v84_negative_gradient_pitch_head_continuation_result.json"
        ),
        "v80_runner": Path("tools/run_winner_v80_pitch_action_head_step.py"),
        "recurrent_policy": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v87.pitch_head_linear_feasibility_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V87_PITCH_HEAD_LINEAR_FEASIBILITY",
        "decision": "AUTHORIZE_ONE_READ_ONLY_TWO_ENDPOINT_LINEAR_FEASIBILITY_AUDIT_ONLY",
        "question": (
            "Can the frozen 64-D recurrent hidden state represent the replay-bound "
            "six-pitch teacher through the existing affine-plus-tanh action head, "
            "or must the next mechanism change the recurrent representation?"
        ),
        "frozen_source": {
            "v86_result_sha256": V86_RESULT_SHA256,
            "checkpoint_labels_updates": CHECKPOINTS,
            "pitch_indices": list(PITCH_INDICES),
            "training_population_episodes": 80,
            "teacher_configuration_count": TEACHER_CONFIGURATION_COUNT,
            "teacher_episodes_per_checkpoint": TEACHER_EPISODES_PER_CHECKPOINT,
            "teacher_table": "exact complete replay-bound Winner-v80/v84 table",
        },
        "fit": {
            "features": "frozen recurrent hidden[64] plus an intercept",
            "targets": "float64 arctanh of the six static raw teacher actions",
            "solver": "numpy.linalg.lstsq",
            "rcond": None,
            "deployed_precision_emulation": (
                "cast fitted weights and bias to float32 before affine, tanh, and "
                "the unchanged graph-authoritative bounded_action"
            ),
            "full_fit_count_per_checkpoint": 1,
            "cross_validation": (
                "leave one of the 16 teacher configuration IDs out, removing both "
                "plant episodes; fit on the other 15 and score only the held-out ID"
            ),
            "cross_validation_fits_per_checkpoint": TEACHER_CONFIGURATION_COUNT,
            "hyperparameter_search": False,
        },
        "classification_rule": {
            "endpoint_feasible": (
                "both full-fit and aggregate leave-one-configuration-out bounded "
                "pitch MSE are strictly below that endpoint's unchanged source MSE"
            ),
            "next_source": (
                "half if feasible; otherwise final if feasible; otherwise none"
            ),
            "feasible_authority": (
                "a separate exact fitted-head CPU proof only; this audit writes no "
                "snapshot or ONNX and runs no support cell"
            ),
            "infeasible_authority": (
                "a separate recurrent-representation diagnostic only"
            ),
        },
        "required_checks": {
            "two_exact_source_checkpoints": True,
            "two_exact_80_episode_rollouts": True,
            "exact_teacher_population_per_checkpoint": True,
            "all_targets_strictly_inside_tanh_domain": True,
            "full_design_matrix_rank_and_singular_values_recorded": True,
            "repeat_solves_bit_exact": True,
            "all_values_finite": True,
            "no_snapshot_or_onnx_written": True,
        },
        "execution_now": {
            "stage2_rollout_episodes": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "diagnostic_authorized": True,
            "result_authorizes": "one separate mechanism proof preregistration only",
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
                "# Winner-v87 linear pitch-head feasibility preregistration",
                "",
                "- Sources: exact Winner-v84 half/final checkpoints at `705 / 755`",
                "- Data: one frozen 80-episode stage-2 rollout per checkpoint",
                "- Teacher population: `16 configurations x 2 plants` per checkpoint",
                "- Fit: affine hidden-state pitch head in teacher-logit space",
                "- Validation: leave one configuration (both plants) out, 16 folds",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
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
