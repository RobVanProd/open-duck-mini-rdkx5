#!/usr/bin/env python3
"""Preregister one safeguarded pitch-action-head-only teacher step."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v80_pitch_action_head_step_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V80_PITCH_ACTION_HEAD_STEP_CONTRACT_20260722.md"
V79_RESULT = ANALYSIS / "winner_v79_complete_residual_teacher_causal_result.json"
V75_RESULT = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_result.json"
V78_RESULT = ANALYSIS / "winner_v78_missing_teacher_extension_result.json"
V79_RESULT_SHA256 = "8e3effb6bbe9a4e830efd4485cadb34446863eada581f6f4d78398c587c3ebaf"
V75_RESULT_SHA256 = "42fd60cb79ae047ecaea05f6ef8fdb3cb18eb037e344585196e44eb90a166383"
V78_RESULT_SHA256 = "a2fe470324c7aa59574e7e01cba339ef0a1eb6a4215464fc617318085537e2c4"
PITCH_INDICES = [2, 3, 4, 11, 12, 13]
TRAINING_TEACHER_IDS = [
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
]
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
            raise FileExistsError(f"refusing to overwrite Winner-v80 contract: {path}")

    causal = json.loads(V79_RESULT.read_text(encoding="utf-8"))
    training = json.loads(V75_RESULT.read_text(encoding="utf-8"))
    extension = json.loads(V78_RESULT.read_text(encoding="utf-8"))
    final = next(row for row in training["persistent_checkpoints"] if row["label"] == "final")
    if (
        sha256(V79_RESULT) != V79_RESULT_SHA256
        or causal.get("status") != "PASS_WINNER_V79_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or causal.get("findings", {}).get("classification_counts", {}).get(
            "pitch_output_causal"
        )
        != 9
        or causal.get("findings", {}).get("support_pass_counts")
        != {"graph": 0, "full_teacher": 9, "pitch_teacher": 9, "nonpitch_zero": 0}
        or sha256(V75_RESULT) != V75_RESULT_SHA256
        or final.get("completed_updates") != 655
        or final.get("snapshot", {}).get("sha256")
        != "00a68b8c0f08996afa770cd84218574872851e613cbb8441caa66af84ece73c6"
        or sha256(V78_RESULT) != V78_RESULT_SHA256
        or extension.get("status") != "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
    ):
        raise ValueError("Winner-v80 selection evidence changed")

    source_paths = {
        "builder": Path("tools/build_winner_v80_pitch_action_head_step_contract.py"),
        "runner": Path("tools/run_winner_v80_pitch_action_head_step.py"),
        "tests": Path("tests/test_winner_v80_pitch_action_head_step.py"),
        "v79_result": Path(
            "outputs/analysis/winner_v79_complete_residual_teacher_causal_result.json"
        ),
        "v75_result": Path(
            "outputs/analysis/winner_v75_functional_numeric_guard_continuation_result.json"
        ),
        "v78_result": Path("outputs/analysis/winner_v78_missing_teacher_extension_result.json"),
        "v42_teacher_table": Path(
            "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
        ),
        "v43_teacher_abi": Path("patches/winner_v43_static_target_teacher.py"),
        "v44_training_population": Path(
            "tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"
        ),
        "v46_graph_receipt": Path("tools/run_winner_v46_static_target_teacher_training.py"),
        "v63_gradient_helpers": Path(
            "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
        ),
        "v79b_module_stack": Path(
            "tools/build_winner_v79b_preregistration_path_correction.py"
        ),
        "full_training_design": Path(
            "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
        ),
        "configuration_domain": Path(
            "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
        ),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v80.pitch_action_head_step_contract.v1",
        "status": "PREREGISTERED_WINNER_V80_PITCH_ACTION_HEAD_STEP",
        "decision": "AUTHORIZE_EXACTLY_ONE_PITCH_ACTION_HEAD_TEACHER_STEP",
        "selection_evidence": {
            "v79_result_sha256": V79_RESULT_SHA256,
            "nine_of_nine_failures_pitch_output_causal": True,
            "v76_final_predictor_regressed": True,
            "mechanism": (
                "change only action_weight[:, pitch_indices] and "
                "action_bias[pitch_indices], preserving the recurrent representation, "
                "predictor, value head, distribution, and all non-pitch outputs"
            ),
        },
        "source_checkpoint": {
            "completed_updates": 655,
            "snapshot": final["snapshot"],
            "graph": final["graph"],
        },
        "step": {
            "source_optimizer_count": 655,
            "rollout_update_index": 655,
            "completed_optimizer_count": 656,
            "pitch_action_indices": PITCH_INDICES,
            "allowed_parameter_slices": [
                "action_weight[:, [2,3,4,11,12,13]]",
                "action_bias[[2,3,4,11,12,13]]",
            ],
            "fresh_moment_slices": "the same two allowed parameter slices only",
            "preserve_bit_exact": (
                "all other parameter elements and optimizer moment elements"
            ),
            "fractions_largest_first": FRACTIONS,
            "acceptance_rule": "first strict same-batch pitch-teacher-loss descent",
        },
        "objective": {
            "teacher_configuration_ids": TRAINING_TEACHER_IDS,
            "heldout_teacher_labels_forbidden": True,
            "pitch_teacher_scale": 58.436370849609375,
            "per_selected_element_scale": 9.739395141601562,
            "supervised_action_indices": PITCH_INDICES,
            "ppo_predictor_anchor_first_tick_gradient_scale": 0.0,
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
        "pass_rule": {
            "exact_12_training_teacher_configurations_each_two_plants": True,
            "no_heldout_teacher_label": True,
            "unprojected_pitch_gradient_nonzero": True,
            "projected_gradient_nonzero_only_on_two_allowed_slices": True,
            "first_accepted_fraction_strictly_descends": True,
            "same_batch_predictor_loss_bit_exact": True,
            "all_unselected_parameter_and_moment_elements_bit_exact": True,
            "snapshot_readback_exact": True,
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
            "pass_authorizes_only": "one separately preregistered bounded pitch-head continuation",
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
                "# Winner-v80 pitch-action-head step contract",
                "",
                "- Source / completed optimizer counts: `655 / 656`",
                "- Mutable parameters: six pitch columns of `action_weight` and six pitch elements of `action_bias` only",
                "- Recurrent core and predictor: bit-exact frozen",
                "- Teacher labels: `12` training configurations; held-out labels forbidden",
                "- Safeguard: largest-first powers of two through `1/1024`",
                "- Optimizer / support / robot authorized now: `1 / 0 / 0`",
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
