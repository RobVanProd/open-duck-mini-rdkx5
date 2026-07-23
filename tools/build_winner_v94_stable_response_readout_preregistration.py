#!/usr/bin/env python3
"""Preregister the Winner-v94 stable universal-response readout contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v94_stable_response_readout_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V94_STABLE_RESPONSE_READOUT_PREREGISTRATION_20260722.md"
V93_RESULT = ANALYSIS / "winner_v93_universal_response_readout_result.json"
V93_RESULT_SHA256 = "6990cd76c61b18405bbf9e5edff46d2533e281553aa077780470912d7a4a3cf2"
SNAPSHOT_SHA256 = "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
ONNX_SHA256 = "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
FLOAT32_AMPLIFICATION_LIMIT = 1.0e-3
FLOAT32_PREDICTION_DELTA_LIMIT = 1.0e-4
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v94 contract: {path}")
    source = json.loads(V93_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V93_RESULT) != V93_RESULT_SHA256
        or source.get("status") != "PASS_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
        or source.get("failed_checks") != []
        or source.get("fit", {}).get("rank") != 70
        or source.get("fit", {}).get("feature_dimension") != 79
        or source.get("fit", {}).get("coefficient_maximum_abs") != 290354176.0
        or source.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v93 source evidence changed")
    source_paths = {
        "builder": Path("tools/build_winner_v94_stable_response_readout_preregistration.py"),
        "runner": Path("tools/run_winner_v94_stable_response_readout.py"),
        "tests": Path("tests/test_winner_v94_stable_response_readout.py"),
        "v93_runner": Path("tools/run_winner_v93_universal_response_readout.py"),
        "v93_result": V93_RESULT.relative_to(ROOT),
        "v92_runner": Path("tools/run_winner_v92_universal_target_response_observer.py"),
        "base_gate": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "v22_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
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
        "schema_version": "winner_v94.stable_response_readout_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V94_STABLE_RESPONSE_READOUT",
        "decision": "AUTHORIZE_ONE_FROZEN_NUMERIC_STABILITY_CONTRACT_ONLY",
        "source": {
            "v93_result_sha256": V93_RESULT_SHA256,
            "observer_label": "winner_v22_final",
            "snapshot_sha256": SNAPSHOT_SHA256,
            "onnx_sha256": ONNX_SHA256,
            "universal_target_candidate": 536,
            "universal_target_action": list(ACTION),
            "universal_target_source_lf_sha256": source["sources"]["v92_result"][
                "sha256"
            ],
        },
        "split": {
            "fit_configurations": 40,
            "heldout_configurations": 16,
            "actuator_plants": 2,
            "ticks_per_cell": 250,
            "fit_transitions": 19920,
            "heldout_transitions": 7968,
            "heldout_data_used_during_fit_or_selection": False,
        },
        "readout": {
            "feature_order": ["h_out[0:64]", "bias"],
            "feature_dimension": 65,
            "target_dimension": 50,
            "mapping": {
                "auxiliary_hidden_weight": "fit rows 0:64",
                "auxiliary_action_weight": "exact zeros [14,50]",
                "auxiliary_bias": "fit row 64",
            },
            "rationale": (
                "the calibration action is fixed and configuration-independent; "
                "removing its rank-deficient direct columns preserves the recurrent "
                "response path and yields an identifiable deployable parameterization"
            ),
            "solver": "numpy.linalg.lstsq float64 rcond=None minimum-norm",
            "stored_coefficient_dtype": "float32",
            "regularization": None,
            "hyperparameter_or_alternative_feature_search": False,
            "full_rank_required": 65,
            "condition_number_times_float32_epsilon_at_most": (
                FLOAT32_AMPLIFICATION_LIMIT
            ),
            "heldout_float64_vs_float32_max_abs_at_most": (
                FLOAT32_PREDICTION_DELTA_LIMIT
            ),
            "recurrent_parameters_changed": False,
            "policy_action_parameters_changed": False,
            "flat_transport_feature_enabled": False,
        },
        "pass_rule": (
            "the 65-column fit is full-rank; condition number times float32 epsilon "
            "is at most 1e-3; heldout float64-to-float32 prediction delta is at "
            "most 1e-4; the float32 readout beats the frozen predictor and constant "
            "on each plant; and all 112 source traces retain support"
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
            "formal_cpu_contract_authorized": True,
            "result_authorizes": (
                "one separately preregistered response-conditioned locomotion CPU "
                "contract only if every pass condition is met"
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
                "# Winner-v94 stable-response readout preregistration",
                "",
                "- Frozen source/action/split: unchanged from Winner-v93",
                "- Readout: `[h_out(64), bias] -> next response(50)`",
                "- Direct action weights: exact zero",
                "- Required rank: `65 / 65`",
                "- Required `condition × eps(float32)`: `<= 1e-3`",
                "- Required float64/float32 heldout delta: `<= 1e-4`",
                "- Required heldout advantage: below frozen and constant per plant",
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
