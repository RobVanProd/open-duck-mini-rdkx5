#!/usr/bin/env python3
"""Preregister the Winner-v92 universal-target response-observer gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v92_universal_target_response_observer_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER_PREREGISTRATION_20260722.md"
)
V91_RESULT = ANALYSIS / "winner_v91_universal_target_full_gate_result.json"
V22_SUPPORT_RESULT = ANALYSIS / "winner_v22_normalized_predictor_support_gate_result.json"
V22_TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V91_RESULT_SHA256 = "3d4611164c21bcf0ea8296f5faa0941580a99b61ed66b4b50d07d3c56735c41c"
V22_SUPPORT_RESULT_SHA256 = (
    "0831de56a34cc5b4e5c1247168045ec7697d35b7f3ea68f764d3f0345eaf895e"
)
V22_TRAINING_RESULT_SHA256 = (
    "19b17f330e27633e1be975325beb5ecdea821332e1ad8e071bbac93fdc62133b"
)
SNAPSHOT_SHA256 = "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
ONNX_SHA256 = "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
ACTION = (
    0.0,
    0.0,
    -0.5,
    0.25,
    0.25,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.5,
    0.25,
    0.25,
)


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


def selected_v22_final() -> dict[str, Any]:
    support = json.loads(V22_SUPPORT_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V22_SUPPORT_RESULT) != V22_SUPPORT_RESULT_SHA256
        or support.get("status")
        != "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
        or support.get("failed_checks") != ["all_248_main_cells_pass"]
    ):
        raise ValueError("Winner-v22 support evidence changed")
    rows = support.get("checkpoint_results", [])
    if [row.get("label") for row in rows] != ["half", "final"]:
        raise ValueError("Winner-v22 endpoint population changed")
    half, final = rows
    for row in rows:
        checks = row.get("checks", {})
        if (
            checks.get("learned_prediction_beats_constant_per_plant") is not True
            or checks.get("all_16_heldout_contexts_separate") is not True
            or checks.get("all_32_heldout_repeats_bit_exact") is not True
            or checks.get("all_previous_action_chains_exact") is not True
            or checks.get("all_jax_onnx_hidden_errors_at_most_1e_7") is not True
        ):
            raise ValueError("Winner-v22 observer evidence changed")
    final_prediction = final["heldout_prediction"]
    half_prediction = half["heldout_prediction"]
    final_advantage = {
        plant: row["constant_normalized_prediction_mse"]
        - row["learned_normalized_prediction_mse"]
        for plant, row in final_prediction.items()
    }
    half_advantage = {
        plant: row["constant_normalized_prediction_mse"]
        - row["learned_normalized_prediction_mse"]
        for plant, row in half_prediction.items()
    }
    if (
        final.get("update") != 100
        or final.get("checkpoint_sha256") != SNAPSHOT_SHA256
        or final.get("onnx_sha256") != ONNX_SHA256
        or not all(
            final_advantage[plant] > half_advantage[plant]
            for plant in final_advantage
        )
    ):
        raise ValueError("Winner-v22 final observer selection evidence changed")
    return {
        "label": "final",
        "update": 100,
        "snapshot_sha256": SNAPSHOT_SHA256,
        "onnx_sha256": ONNX_SHA256,
        "selection_rule": (
            "preselected from saved Winner-v22 evidence because both endpoints pass "
            "predictor/context/repeatability, while final has the larger heldout "
            "predictor advantage on both actuator plants"
        ),
        "heldout_prediction": final_prediction,
        "heldout_advantage_over_constant": final_advantage,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v92 contract: {path}")
    if sha256(V22_TRAINING_RESULT) != V22_TRAINING_RESULT_SHA256:
        raise ValueError("Winner-v22 training evidence changed")
    training = json.loads(V22_TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v22 training artifact is not admissible")
    source_observer = selected_v22_final()
    universal = json.loads(V91_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V91_RESULT) != V91_RESULT_SHA256
        or universal.get("status") != "PASS_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE"
        or universal.get("failed_checks") != []
        or universal.get("frozen_target", {}).get("candidate_index") != 536
        or universal.get("frozen_target", {}).get("expanded_raw_action")
        != list(ACTION)
    ):
        raise ValueError("Winner-v91 universal-target evidence changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v92_universal_target_response_observer_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v92_universal_target_response_observer.py"),
        "tests": Path("tests/test_winner_v92_universal_target_response_observer.py"),
        "base_gate": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "v22_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
        "intervention": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
        "target_expansion": Path("patches/winner_v43_static_target_teacher.py"),
        "v22_coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
        "v22_support_result": V22_SUPPORT_RESULT.relative_to(ROOT),
        "v22_training_result": V22_TRAINING_RESULT.relative_to(ROOT),
        "v91_result": V91_RESULT.relative_to(ROOT),
    }
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v92.universal_target_response_observer_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER",
        "decision": "AUTHORIZE_ONE_FROZEN_UNIVERSAL_TARGET_RESPONSE_OBSERVER_GATE_ONLY",
        "source_observer": source_observer,
        "frozen_target": universal["frozen_target"],
        "gate": {
            "duration_ticks": 250,
            "core_model_configurations": 56,
            "sensor_transport_conditions": 6,
            "actuator_plants": 2,
            "formal_support_cells": 124,
            "heldout_repeat_cells": 32,
            "sensor_prng_checkpoint_index": 1,
            "thresholds": "unchanged reviewed Winner-v12 physical support thresholds",
            "pass_rule": (
                "all 124 support cells pass; all 32 heldout repeats are bit-exact; "
                "all 16 heldout configurations separate the two actuator plants in "
                "final recurrent state above 1e-7; the learned response predictor "
                "strictly beats the constant comparator per plant; every requested "
                "action equals the bounded universal-target chain; previous_action "
                "is exact; and JAX/ONNX hidden error is at most 1e-7"
            ),
            "checkpoint_or_candidate_selection_from_new_result": False,
            "flat_transport_feature_enabled": False,
        },
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "formal_cpu_gate_authorized": True,
            "result_authorizes": (
                "one separately preregistered response-conditioned locomotion CPU "
                "contract only if the entire gate passes"
            ),
            "training_authorized_now": False,
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
                "# Winner-v92 universal-target response-observer preregistration",
                "",
                "- Observer: exact Winner-v22 final checkpoint at update `100`",
                "- Target: Winner-v91 candidate `536 / [0.5, 0.25, 0.25]`",
                "- Population: `124` formal cells + `32` heldout repeats",
                "- Duration: `250` ticks per cell",
                "- Required: support + repeatability + context + predictor advantage",
                "- Flat-transport feature: `disabled`",
                "- Optimizer updates / artifacts / robot access: `0 / 0 / 0`",
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
