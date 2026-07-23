#!/usr/bin/env python3
"""Freeze the Winner-v96 response-conditioned locomotion mechanics contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v96_response_conditioned_mechanics_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V96_RESPONSE_CONDITIONED_MECHANICS_PREREGISTRATION_20260722.md"
)
V92_RESULT = ANALYSIS / "winner_v92_universal_target_response_observer_result.json"
V95_RESULT = ANALYSIS / "winner_v95_precision_truncated_readout_result.json"
POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
GOLDEN_ZERO = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.000.npz"
)
GOLDEN_MOVING = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.080.npz"
)

V92_RESULT_SHA256 = "3f706f1a36b66f7cd5d1a78d693162bdfa47dcf02fa18bb5556c6936494ae652"
V95_RESULT_SHA256 = "034e2e65c6d4f92082bfba63f8b2c57f6e79d0d2b97627f1021ff727106cab55"
CALIBRATOR_SNAPSHOT_SHA256 = (
    "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
)
CALIBRATOR_ONNX_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
POLICY_SHA256 = "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
UNIVERSAL_TARGET = (
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
SIGNED_CONFIGURATION_IDS = ("COM_X_NEG", "COM_X_POS")
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")


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


def tensor(name: str, shape: list[int]) -> dict[str, Any]:
    return {"name": name, "dtype": "float32", "shape": shape}


def signed_response_receipts(v92: dict[str, Any]) -> list[dict[str, Any]]:
    selected = [
        cell
        for cell in v92["core_model_plant_cells"]
        if cell["configuration_id"] in SIGNED_CONFIGURATION_IDS
    ]
    expected_pairs = {
        (configuration_id, plant)
        for configuration_id in SIGNED_CONFIGURATION_IDS
        for plant in PLANTS
    }
    if {(cell["configuration_id"], cell["plant"]) for cell in selected} != expected_pairs:
        raise ValueError("Winner-v92 signed-X source population changed")
    return [
        {
            "configuration_id": cell["configuration_id"],
            "plant": cell["plant"],
            "configuration_sha256": cell["configuration_sha256"],
            "final_h_out": cell["final_h_out"],
            "trace_hashes": cell["trace_hashes"],
        }
        for cell in selected
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v96 contract: {path}")
    v92 = json.loads(V92_RESULT.read_text(encoding="utf-8"))
    v95 = json.loads(V95_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V92_RESULT) != V92_RESULT_SHA256
        or v92.get("status") != "HOLD_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
        or v92.get("failed_checks")
        != ["learned_prediction_beats_constant_per_plant"]
        or v92.get("frozen_target", {}).get("candidate_index") != 536
        or v92.get("frozen_target", {}).get("expanded_raw_action")
        != list(UNIVERSAL_TARGET)
    ):
        raise ValueError("Winner-v92 source evidence changed")
    if (
        sha256(V95_RESULT) != V95_RESULT_SHA256
        or v95.get("status") != "PASS_WINNER_V95_PRECISION_TRUNCATED_READOUT"
        or v95.get("failed_checks") != []
        or v95.get("fit", {}).get("retained_rank") != 28
        or v95.get("fit", {}).get("combined_coefficient_sha256")
        != "ccab7d2ad3b2a29591f6696eba5c08a4b6446ebab3d246a46bbc6f2043419e76"
    ):
        raise ValueError("Winner-v95 source evidence changed")
    binary_sources = {
        "protected_policy": {"path": POLICY.relative_to(ROOT).as_posix(), "sha256": POLICY_SHA256},
        "golden_x0": {"path": GOLDEN_ZERO.relative_to(ROOT).as_posix(), "sha256": sha256(GOLDEN_ZERO)},
        "golden_x008": {"path": GOLDEN_MOVING.relative_to(ROOT).as_posix(), "sha256": sha256(GOLDEN_MOVING)},
        "winner_v22_final_snapshot": {"external_path_role": "--training-work-root/snapshots/snapshot_normalized_predictor_update_100.npz", "sha256": CALIBRATOR_SNAPSHOT_SHA256},
        "winner_v22_final_onnx": {"external_path_role": "--training-work-root/graphs/winner_v22_final.onnx", "sha256": CALIBRATOR_ONNX_SHA256},
    }
    if sha256(POLICY) != POLICY_SHA256:
        raise ValueError("selected locomotion policy changed")
    source_paths = {
        "builder": Path("tools/build_winner_v96_response_conditioned_mechanics_preregistration.py"),
        "runner": Path("tools/run_winner_v96_response_conditioned_mechanics.py"),
        "network": Path("patches/winner_v96_response_conditioned_networks.py"),
        "tests": Path("tests/test_winner_v96_response_conditioned_mechanics.py"),
        "v92_runner": Path("tools/run_winner_v92_universal_target_response_observer.py"),
        "v22_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
        "base_gate": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "v92_result": V92_RESULT.relative_to(ROOT),
        "v95_result": V95_RESULT.relative_to(ROOT),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    calibrator_abi = {
        "inputs": [tensor("obs", [1, 115]), tensor("previous_action", [1, 14]), tensor("h_in", [1, 64])],
        "outputs": [tensor("calibration_actions", [1, 14]), tensor("previous_action_out", [1, 14]), tensor("h_out", [1, 64])],
    }
    locomotion_abi = {
        "inputs": [tensor("obs", [1, 115]), tensor("previous_action", [1, 14]), tensor("h_in", [1, 64]), tensor("calibration_context", [1, 64])],
        "outputs": [tensor("continuous_actions", [1, 14]), tensor("previous_action_out", [1, 14]), tensor("h_out", [1, 64])],
    }
    value = {
        "schema_version": "winner_v96.response_conditioned_mechanics_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V96_RESPONSE_CONDITIONED_MECHANICS",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_CPU_MECHANICS_CONTRACT_ONLY",
        "hypothesis": (
            "The exact Winner-v22 response encoder can drive the already-selected 512K "
            "locomotion graph through a default-disabled recurrent adapter without changing "
            "protected behavior, while an enabled nonzero adapter remains graph-bounded."
        ),
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "binary_sources": binary_sources,
        "source_evidence": {
            "v92_result_sha256": V92_RESULT_SHA256,
            "v95_result_sha256": V95_RESULT_SHA256,
            "universal_target_candidate": 536,
            "universal_target_action": list(UNIVERSAL_TARGET),
            "signed_response_receipts": signed_response_receipts(v92),
            "v92_limited_use": (
                "signed response traces, deterministic contexts, physical support, and "
                "graph parity only; its failed frozen predictor is superseded by V95"
            ),
            "stable_readout": {
                "retained_rank": 28,
                "combined_coefficient_sha256": v95["fit"]["combined_coefficient_sha256"],
                "hidden_weight_sha256": v95["readout"][
                    "auxiliary_hidden_weight_sha256"
                ],
                "action_weight_sha256": v95["readout"][
                    "auxiliary_action_weight_sha256"
                ],
                "bias_sha256": v95["readout"]["auxiliary_bias_sha256"],
            },
        },
        "expected_abi": {"calibrator": calibrator_abi, "locomotion": locomotion_abi},
        "fixed_initialization": {
            "adapter_seed": 60721,
            "adapter_max_normalized": 0.25,
            "action_heads_and_context_paths": "exact-zero at zero update",
            "calibration_ticks": 250,
            "flat_transport_feature_enabled": False,
            "stable_v95_readout_exported": False,
        },
        "test_population": {
            "signed_calibration_cells": 4,
            "signed_configuration_ids": list(SIGNED_CONFIGURATION_IDS),
            "plants": list(PLANTS),
            "golden_ticks": 1200,
            "golden_commands_x": [0.0, 0.08],
            "stress_cases": 256,
            "invalid_handoff_cases": 9,
        },
        "thresholds": {
            "signed_context_linf_separation_same_plant_at_least": 0.15,
            "calibrator_jax_onnx_hidden_max_abs_at_most": 1.0e-7,
            "zero_adapter_enabled_action_max_abs_delta_at_most": 1.0e-6,
            "stress_jax_onnx_hidden_and_delta_max_abs_at_most": 1.0e-6,
            "stress_onnx_numpy_final_action_max_abs_at_most": 1.0e-6,
        },
        "pass_rule": [
            "all source hashes, exact ABIs, and CPU-only execution match",
            "the exported universal calibrator exactly reproduces the four frozen signed-X V92 action, observation, hidden, and final-context receipts",
            "same-plant COM_X_NEG versus COM_X_POS final context Linf separation is at least 0.15",
            "the 250-tick handoff is immutable and all nine invalid handoffs fail closed",
            "the adapter-disabled graph is bit-exact to all 1,200 selected-policy golden actions and previous-action outputs",
            "the enabled exact-zero adapter changes actions by at most 1e-6 and x=0 remains exact zero",
            "256 deterministic nonzero-adapter cases agree with JAX/NumPy references and obey graph absolute, rate, actual-centered guard, and x=0 deadband boundaries",
            "the V95 stable readout identity remains bound but is not exported into either deployable graph",
        ],
        "execution_now": {"simulator_cells": 0, "golden_ticks": 0, "stress_cases": 0, "optimizer_updates": 0, "robot_or_rdk_access": 0},
        "authority": {
            "formal_cpu_contract_authorized": True,
            "result_authorizes": "one separately preregistered response-conditioned locomotion training experiment only if every check passes",
            "training_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(
        "# Winner-v96 response-conditioned mechanics preregistration\n\n"
        "- Calibrator: exact Winner-v22 final encoder with Winner-v91 universal target\n"
        "- Locomotion source: selected T2 512K graph `99d3afce…304de`\n"
        "- Population: 4 signed calibration cells + 1,200 golden ticks + 256 stress cases\n"
        "- Required: exact default-off identity, immutable handoff, graph-owned bounds\n"
        "- V95 stable readout: identity-bound, training-only, not exported\n"
        "- Flat transport: disabled\n"
        "- Optimizer updates / robot access: `0 / 0`\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
