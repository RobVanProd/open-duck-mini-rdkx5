#!/usr/bin/env python3
"""Freeze one zero-update first-tick teacher mapping gradient proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v56_first_tick_teacher_gradient_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CONTRACT_20260722.md"
V55B_RESULT = ANALYSIS / "winner_v55b_native_reset_quantization_result.json"
V55B_RESULT_SHA256 = "303fee53c378a11e54e7bd99edebb78f88747f0ca05d6f56c84570a72ad78e99"
V52_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
V52_RESULT_SHA256 = "a964b30f7a9958a7f6ed6db209fa11da8a36a118e59ffbbf2956a67d38b208b3"
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

SOURCES = {
    "builder": Path("tools/build_winner_v56_first_tick_teacher_gradient_contract.py"),
    "runner": Path("tools/run_winner_v56_first_tick_teacher_gradient_contract.py"),
    "tests": Path("tests/test_winner_v56_first_tick_teacher_gradient_contract.py"),
    "mechanism": Path("patches/winner_v56_first_tick_teacher_mapping.py"),
    "v55b_result": Path("outputs/analysis/winner_v55b_native_reset_quantization_result.json"),
    "v55_result": Path("outputs/analysis/winner_v55_reset_label_handoff_result.json"),
    "v52_result": Path("outputs/analysis/winner_v52_full_action_teacher_training_result.json"),
    "v52_preregistration": Path("outputs/analysis/winner_v52_full_action_teacher_training_preregistration.json"),
    "v54_runner": Path("tools/run_winner_v54_residual_teacher_causal.py"),
    "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "full_action_teacher": Path("patches/winner_v49_full_action_static_target_teacher.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_smoke_runner": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
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
            raise FileExistsError(f"refusing to overwrite Winner-v56 contract: {path}")
    v55b = json.loads(V55B_RESULT.read_text(encoding="utf-8"))
    v52 = json.loads(V52_RESULT.read_text(encoding="utf-8"))
    v52_prereg = json.loads(
        (ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        sha256(V55B_RESULT) != V55B_RESULT_SHA256
        or v55b.get("classification") != "NATIVE_RESET_LABELS_REMAIN_SEPARABLE"
        or v55b.get("decision")
        != "AUTHORIZE_FIRST_TICK_TEACHER_MAPPING_CPU_CONTRACT_PREREGISTRATION_ONLY"
        or sha256(V52_RESULT) != V52_RESULT_SHA256
        or v52.get("status") != "PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"
        or v52_prereg.get("objective", {})
        .get("full_action_static_target_teacher", {})
        .get("configuration_ids")
        != TRAINING_IDS
    ):
        raise ValueError("Winner-v56 source authority changed")
    final = next(
        row for row in v52["persistent_checkpoints"] if row["label"] == "final"
    )
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v56.first_tick_teacher_gradient_contract.v1",
        "status": "PREREGISTERED_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_FIRST_TICK_GRADIENT_PROOF_ONLY",
        "causal_basis": {
            "v55b_result_sha256": V55B_RESULT_SHA256,
            "native_reset_labels_separable": True,
            "v55_one_graph_tick_support_passes": 4,
            "v55_immediate_teacher_support_passes": 12,
        },
        "source_checkpoint": {
            "v52_result_sha256": V52_RESULT_SHA256,
            "label": "final",
            "completed_updates": 453,
            "snapshot_sha256": final["snapshot"]["sha256"],
            "onnx_sha256": final["graph"]["sha256"],
        },
        "objective": {
            "configuration_ids": TRAINING_IDS,
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "heldout_configuration_ids_forbidden": [
                "HELDOUT_04",
                "HELDOUT_07",
                "HELDOUT_09",
                "HELDOUT_15",
            ],
            "raw_reset_rows": 22,
            "native_quantized_reset_rows": 22,
            "total_rows": 44,
            "teacher_action_indices": list(range(14)),
            "selected_elements": 616,
            "previous_action": "zero",
            "h_in": "zero",
            "scale": 136.35153198242188,
            "scale_rule": (
                "exactly equal to the frozen V52 full-action teacher scale so the "
                "mean reset loss receives one objective-term weight; no search"
            ),
        },
        "gradient_contract": {
            "expected_nonzero_leaves": [
                "action_bias",
                "action_weight",
                "hidden_bias",
                "obs_weight",
            ],
            "expected_zero_leaves": [
                "auxiliary_action_weight",
                "auxiliary_bias",
                "auxiliary_hidden_weight",
                "hidden_weight",
                "previous_action_weight",
                "training_only_log_std",
                "training_only_value_bias",
                "training_only_value_weight",
            ],
            "default_off_loss_bit_exact": True,
            "default_off_gradients_bit_exact_zero": True,
            "no_optimizer_update": True,
        },
        "pass_rule": {
            "source_snapshot_and_onnx_exact": True,
            "exact_44_rows_616_elements": True,
            "heldout_labels_absent": True,
            "raw_and_quantized_inputs_distinct_per_configuration": True,
            "jax_onnx_actions_at_most_1e_7": True,
            "targets_obey_graph_boundary": True,
            "gradient_leaf_locality_exact": True,
            "scaled_loss_and_gradients_finite_nonzero": True,
            "default_off_exact": True,
        },
        "execution_now": {
            "reset_rows": 0,
            "simulator_steps": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "exports": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": "one separately preregistered CPU Adam update proof",
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
                "# Winner-v56 first-tick teacher gradient CPU contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Rows / elements: `44 / 616`",
                "- Scale: `136.35153198242188` (equal frozen V52 term weight)",
                "- Simulator steps / optimizer / export / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
