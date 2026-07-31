#!/usr/bin/env python3
"""Preregister one zero-commit persistent-teacher conflict attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v63_persistent_teacher_conflict_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V63_PERSISTENT_TEACHER_CONFLICT_PREREGISTRATION_20260722.md"
)
V60_RESULT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_result.json"
V62_RESULT = ANALYSIS / "winner_v62_residual_teacher_causal_result.json"
V60_RESULT_SHA256 = "50622331dea979369bdea7bb001cd168f94162270a0ea0ec1bdb4d6d9f6b8b57"
V62_RESULT_SHA256 = "2da0c48a257e0bace9506998db95a9a7bbf8f736448a78db651742e5235251f5"
TRAINING_IDS = [
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
]
HELDOUT_IDS = ["HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15"]

SOURCES = {
    "builder": Path(
        "tools/build_winner_v63_persistent_teacher_conflict_preregistration.py"
    ),
    "runner": Path(
        "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
    ),
    "tests": Path("tests/test_winner_v63_persistent_teacher_conflict.py"),
    "v60_result": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"
    ),
    "v60_preregistration": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_preregistration.json"
    ),
    "v62_result": Path(
        "outputs/analysis/winner_v62_residual_teacher_causal_result.json"
    ),
    "v62_preregistration": Path(
        "outputs/analysis/winner_v62_residual_teacher_causal_preregistration.json"
    ),
    "v61_builder": Path(
        "tools/build_winner_v61_integrated_support_gate_preregistration.py"
    ),
    "v50_teacher_helpers": Path(
        "tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"
    ),
    "v56_reset_teacher": Path("patches/winner_v56_first_tick_teacher_mapping.py"),
    "v49_full_teacher": Path(
        "patches/winner_v49_full_action_static_target_teacher.py"
    ),
    "v43_teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "v29_prefix_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "v24_failure_v3": Path(
        "patches/winner_v24_symmetric_support_failure_v3.py"
    ),
    "v22_predictor_v2": Path(
        "patches/winner_v22_normalized_predictor_v2.py"
    ),
    "v22_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "v21_joint": Path(
        "patches/winner_v21_predictor_preserving_joint_support.py"
    ),
    "v20_recurrent": Path("patches/winner_v20_joint_recurrent_support.py"),
    "training": Path("patches/winner_v12_calibrator_training.py"),
    "full_training_runner": Path(
        "tools/run_winner_v12_full_calibrator_training.py"
    ),
    "support_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "teacher_table": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
}


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
            raise FileExistsError(f"refusing to overwrite Winner-v63 contract: {path}")

    v60 = json.loads(V60_RESULT.read_text(encoding="utf-8"))
    v62 = json.loads(V62_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V60_RESULT) != V60_RESULT_SHA256
        or v60.get("status")
        != "PASS_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"
        or sha256(V62_RESULT) != V62_RESULT_SHA256
        or v62.get("status")
        != "PASS_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or v62.get("findings", {}).get("support_pass_counts")
        != {"full_teacher": 13, "graph": 0, "nonpitch_zero": 0, "pitch_teacher": 12}
        or v62.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v63 frozen evidence changed")
    final = next(
        row for row in v60["persistent_checkpoints"] if row["label"] == "final"
    )
    if (
        final["completed_updates"] != 554
        or final["snapshot"]["sha256"]
        != "c8eb7032dea20c2c197ab03f7544ea9be92d2694a3a3414656941978117d8802"
        or final["graph"]["sha256"]
        != "4a6386d8dddfcc441f90bce4f64d7307144446bb3032c171c22cb2e299ac3939"
    ):
        raise ValueError("Winner-v63 final checkpoint changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    frozen_execution = {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "counterfactual_in_memory_adam_steps": 2,
        "committed_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }
    value = {
        "schema_version": "winner_v63.persistent_teacher_conflict_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_COMMIT_CPU_ATTRIBUTION_ONLY",
        "question": (
            "Why did the already full-horizon teacher objective plateau even though the "
            "same full teacher rescues all 13 final failures: opposing integrated gradients, "
            "inherited Adam moments, or a remaining trajectory-distribution mismatch?"
        ),
        "evidence_selection": {
            "v62_full_teacher_support": "13/13",
            "v62_pitch_teacher_support": "12/13",
            "v62_first_tick_pitch_rms_mean": 0.07728285739495369,
            "v62_post_first_tick_pitch_rms_mean": 0.0817888110754449,
            "v60_full_teacher_loss_first": 0.0031359954737126827,
            "v60_full_teacher_loss_final": 0.0032995049841701984,
            "v60_first_tick_teacher_loss_first": 0.0040571861900389194,
            "v60_first_tick_teacher_loss_final": 0.0036237684544175863,
            "flat_transport_or_attention_selected": False,
        },
        "frozen_source": {
            "v60_result_sha256": V60_RESULT_SHA256,
            "v62_result_sha256": V62_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 554,
            "snapshot": final["snapshot"],
            "graph": final["graph"],
            "teacher_snapshot": {
                "bytes": v60["teacher_snapshot"]["bytes"],
                "sha256": v60["teacher_snapshot"]["sha256"],
                "completed_updates": v60["teacher_snapshot"]["completed_updates"],
            },
        },
        "frozen_objective": {
            "rollout_update_index": 554,
            "population_episode_slots": 80,
            "training_teacher_configuration_ids": TRAINING_IDS,
            "heldout_teacher_configuration_ids_forbidden": HELDOUT_IDS,
            "policy_gradient_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "action_weight",
                "action_bias",
            ],
            "components": [
                "PPO",
                "normalized predictor x 380.9135437011719",
                "prefix anchor x 197.3112030029297",
                "full-action persistent teacher x 136.35153198242188",
                "first-tick teacher x 136.35153198242188",
            ],
            "analysis": (
                "float64 dot products/cosines against the scaled persistent-teacher "
                "gradient over policy, recurrent-core, and action-head leaves"
            ),
            "counterfactual": (
                "evaluate exactly one integrated and one teacher-only Adam step in memory "
                "from the same immutable count-554 moments; write neither state"
            ),
        },
        "classification_rule": [
            {
                "if": "teacher-only inherited-Adam same-batch loss does not decrease",
                "classification": "INHERITED_ADAM_STATE_BLOCKS_ISOLATED_TEACHER_DESCENT",
                "next": "fresh-moment persistent-teacher step contract",
            },
            {
                "if": "integrated same-batch loss does not decrease",
                "classification": "INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT",
                "next": "isolated persistent-teacher step contract",
            },
            {
                "if": "all non-persistent-teacher terms have negative dot product with the persistent-teacher gradient",
                "classification": "OTHER_OBJECTIVES_OPPOSE_PERSISTENT_TEACHER_GRADIENT",
                "next": "conflict-projected persistent-teacher step contract",
            },
            {
                "if": "the total gradient has nonpositive dot product with the persistent-teacher gradient",
                "classification": "TOTAL_GRADIENT_OPPOSES_PERSISTENT_TEACHER_GRADIENT",
                "next": "isolated persistent-teacher step contract",
            },
            {
                "otherwise": "NO_LOCAL_OPTIMIZATION_CONFLICT",
                "next": "teacher-trajectory persistent-prefix contract",
            },
        ],
        "pass_rule": {
            "source_artifacts_exact": True,
            "cpu_only_environment_exact": True,
            "exact_80_episode_rollout_at_update_554": True,
            "episode_receipts_exact": True,
            "action_boundary_exact": True,
            "reward_and_failure_transition_rule_exact": True,
            "hidden_replay_within_v59_bound": True,
            "predictor_successors_present": True,
            "anchor_elements_exact": True,
            "full_teacher_elements_and_rows_exact": True,
            "reset_batch_exact_and_heldout_absent": True,
            "teacher_gradient_policy_only": True,
            "composed_gradient_bit_exact": True,
            "all_losses_gradients_alignments_finite": True,
            "counterfactual_counts_exact": True,
            "source_parameters_and_optimizer_unchanged": True,
        },
        "frozen_execution": frozen_execution,
        "execution_now": {
            **frozen_execution,
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "counterfactual_in_memory_adam_steps": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "one separately preregistered CPU mechanism selected by the frozen classification"
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
                "# Winner-v63 persistent-teacher conflict preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source: exact Winner-v60 final count `554`",
                "- Work: one 80-episode rollout plus two in-memory counterfactual steps",
                "- Committed optimizer / support / robot: `0 / 0 / 0`",
                "- Attention or flat-transport change: `none`",
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
