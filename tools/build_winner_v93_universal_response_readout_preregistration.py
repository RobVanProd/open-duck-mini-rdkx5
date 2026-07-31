#!/usr/bin/env python3
"""Preregister the Winner-v93 universal-response readout feasibility test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v93_universal_response_readout_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V93_UNIVERSAL_RESPONSE_READOUT_PREREGISTRATION_20260722.md"
V92_RESULT = ANALYSIS / "winner_v92_universal_target_response_observer_result.json"
V22_TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V92_RESULT_SHA256 = "3f706f1a36b66f7cd5d1a78d693162bdfa47dcf02fa18bb5556c6936494ae652"
V22_TRAINING_RESULT_SHA256 = (
    "19b17f330e27633e1be975325beb5ecdea821332e1ad8e071bbac93fdc62133b"
)
SNAPSHOT_SHA256 = "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
ONNX_SHA256 = "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"


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
            raise FileExistsError(f"refusing to overwrite Winner-v93 contract: {path}")
    source = json.loads(V92_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V92_RESULT) != V92_RESULT_SHA256
        or source.get("status") != "HOLD_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
        or source.get("failed_checks")
        != ["learned_prediction_beats_constant_per_plant"]
        or source.get("failed_cells") != []
        or source.get("checks", {}).get("all_16_heldout_contexts_separate") is not True
        or source.get("checks", {}).get("all_124_support_cells_pass") is not True
        or source.get("source_observer", {}).get("snapshot_sha256")
        != SNAPSHOT_SHA256
        or source.get("source_observer", {}).get("onnx_sha256") != ONNX_SHA256
    ):
        raise ValueError("Winner-v92 source evidence changed")
    if sha256(V22_TRAINING_RESULT) != V22_TRAINING_RESULT_SHA256:
        raise ValueError("Winner-v22 training evidence changed")
    source_paths = {
        "builder": Path("tools/build_winner_v93_universal_response_readout_preregistration.py"),
        "runner": Path("tools/run_winner_v93_universal_response_readout.py"),
        "tests": Path("tests/test_winner_v93_universal_response_readout.py"),
        "base_gate": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "v22_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
        "v92_runner": Path("tools/run_winner_v92_universal_target_response_observer.py"),
        "v92_result": V92_RESULT.relative_to(ROOT),
        "v22_training_result": V22_TRAINING_RESULT.relative_to(ROOT),
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
        "schema_version": "winner_v93.universal_response_readout_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V93_UNIVERSAL_RESPONSE_READOUT",
        "decision": "AUTHORIZE_ONE_FROZEN_HELDOUT_READOUT_FEASIBILITY_TEST_ONLY",
        "source": {
            "v92_result_sha256": V92_RESULT_SHA256,
            "observer_label": "winner_v22_final",
            "observer_update": 100,
            "snapshot_sha256": SNAPSHOT_SHA256,
            "onnx_sha256": ONNX_SHA256,
            "universal_target": source["frozen_target"],
        },
        "split": {
            "fit_configuration_groups": ["fixed_anchors", "discovery_samples"],
            "fit_configurations": 40,
            "heldout_configuration_group": "heldout_samples",
            "heldout_configurations": 16,
            "actuator_plants": 2,
            "ticks_per_cell": 250,
            "fit_transitions": 19920,
            "heldout_transitions": 7968,
            "heldout_data_used_during_fit_or_selection": False,
        },
        "readout": {
            "feature_order": ["h_out[0:64]", "realized_action[0:14]", "bias"],
            "feature_dimension": 79,
            "target": "next_observation[AUXILIARY_INDICES]",
            "target_dimension": 50,
            "normalization": "exact frozen Winner-v22 target_mean and target_std",
            "solver": "numpy.linalg.lstsq float64 rcond=None minimum-norm",
            "stored_coefficient_dtype": "float32",
            "regularization": None,
            "hyperparameter_or_feature_search": False,
            "recurrent_parameters_changed": False,
            "policy_action_parameters_changed": False,
            "flat_transport_feature_enabled": False,
        },
        "pass_rule": (
            "all 112 source trace cells retain support; the one frozen fitted "
            "float32 readout is finite; and on the untouched 16-configuration "
            "heldout set its normalized MSE is strictly below both the frozen "
            "Winner-v22 predictor and the frozen constant comparator separately "
            "for each actuator plant"
        ),
        "execution_now": {
            "source_trace_cells": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "formal_cpu_diagnostic_authorized": True,
            "result_authorizes": (
                "one separately preregistered universal-action observer CPU contract "
                "only if every pass condition is met"
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
                "# Winner-v93 universal-response readout preregistration",
                "",
                "- Frozen recurrent source: Winner-v22 final",
                "- Frozen action: Winner-v91/V92 universal candidate `536`",
                "- Fit / heldout configurations: `40 / 16`",
                "- Fit / heldout transitions: `19,920 / 7,968`",
                "- Readout: one minimum-norm `[h_out, action, bias] -> response` fit",
                "- Required: heldout MSE below frozen predictor and constant per plant",
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
