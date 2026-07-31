#!/usr/bin/env python3
"""Preregister one isolated first-tick teacher Adam-update proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v57_first_tick_teacher_one_update_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CONTRACT_20260722.md"
V56_RESULT = ANALYSIS / "winner_v56_first_tick_teacher_gradient_result.json"
V56_RESULT_SHA256 = "6363c17ab6bcf602dff964d3770bcd8e38f73669ca4f2a521aae5c319051c1a8"
V52_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
V52_RESULT_SHA256 = "a964b30f7a9958a7f6ed6db209fa11da8a36a118e59ffbbf2956a67d38b208b3"

SOURCES = {
    "builder": Path("tools/build_winner_v57_first_tick_teacher_one_update_contract.py"),
    "runner": Path("tools/run_winner_v57_first_tick_teacher_one_update.py"),
    "tests": Path("tests/test_winner_v57_first_tick_teacher_one_update.py"),
    "mechanism": Path("patches/winner_v56_first_tick_teacher_mapping.py"),
    "v56_result": Path("outputs/analysis/winner_v56_first_tick_teacher_gradient_result.json"),
    "v56_contract": Path("outputs/analysis/winner_v56_first_tick_teacher_gradient_contract.json"),
    "v52_result": Path("outputs/analysis/winner_v52_full_action_teacher_training_result.json"),
    "v54_runner": Path("tools/run_winner_v54_residual_teacher_causal.py"),
    "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "joint_training": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "snapshot_io": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "network_export": Path("patches/winner_v12_decomposed_backend_networks.py"),
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
            raise FileExistsError(f"refusing to overwrite Winner-v57 contract: {path}")
    v56 = json.loads(V56_RESULT.read_text(encoding="utf-8"))
    v52 = json.loads(V52_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V56_RESULT) != V56_RESULT_SHA256
        or v56.get("status")
        != "PASS_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT"
        or v56.get("decision")
        != "AUTHORIZE_ONE_FIRST_TICK_TEACHER_ADAM_UPDATE_PREREGISTRATION_ONLY"
        or sha256(V52_RESULT) != V52_RESULT_SHA256
        or v52.get("status") != "PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v57 source authority changed")
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
        "schema_version": "winner_v57.first_tick_teacher_one_update_contract.v1",
        "status": "PREREGISTERED_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF",
        "decision": "AUTHORIZE_EXACTLY_ONE_ISOLATED_ADAM_UPDATE_ONLY",
        "source": {
            "v56_result_sha256": V56_RESULT_SHA256,
            "v52_result_sha256": V52_RESULT_SHA256,
            "snapshot_sha256": final["snapshot"]["sha256"],
            "onnx_sha256": final["graph"]["sha256"],
            "optimizer_count": 453,
        },
        "objective": {
            "rows": 44,
            "selected_elements": 616,
            "scale": 136.35153198242188,
            "gradient": "exact V56 scaled first-tick teacher gradient",
            "baseline_ppo_predictor_anchor_full_horizon_gradients": (
                "not recomputed in this isolated optimizer/state proof"
            ),
            "optimizer_state": "retain the complete V52 count-453 Adam m/v state",
            "learning_rate": 0.0001,
            "result_optimizer_count": 454,
        },
        "proof": {
            "recompute_v56_loss_metrics_and_gradient_bit_exact": True,
            "one_adam_update_453_to_454": True,
            "same_batch_total_raw_and_quantized_losses_strictly_decrease": True,
            "all_12_trainable_leaves_change": True,
            "source_state_remains_unchanged": True,
            "complete_snapshot_optimizer_normalizer_roundtrip": True,
            "one_nonselected_stateful_onnx_export": True,
            "onnx_abi": "obs[1,115]+previous_action[1,14]+h_in[1,64] -> calibration_actions[1,14]+previous_action_out[1,14]+h_out[1,64]",
            "onnx_jax_chain_max_abs": 1.0e-7,
            "no_teacher_or_privileged_export_tokens": True,
        },
        "execution_now": {
            "reset_rows": 0,
            "simulator_steps": 0,
            "optimizer_updates": 0,
            "continuation_updates": 0,
            "formal_support_cells": 0,
            "candidate_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "continuation_training_authorized": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separately preregistered integrated bounded continuation",
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
                "# Winner-v57 first-tick teacher one-update CPU contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Optimizer count: `453 -> 454`",
                "- Rows / elements / scale: `44 / 616 / 136.35153198242188`",
                "- Simulator / continuation / support / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
