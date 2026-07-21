#!/usr/bin/env python3
"""Freeze the zero-update Winner-v22 normalized-predictor CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v22_normalized_predictor_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v21_normalized_semantics_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v22_normalized_predictor_cpu_contract.py"),
    "runner": Path("tools/run_winner_v22_normalized_predictor_cpu_contract.py"),
    "mechanics": Path("patches/winner_v22_normalized_predictor.py"),
    "mechanics_tests": Path("tests/test_winner_v22_normalized_predictor.py"),
    "contract_tests": Path("tests/test_winner_v22_normalized_predictor_cpu_contract.py"),
    "workflow": Path(".github/workflows/winner-v22-normalized-predictor-cpu-contract.yml"),
    "result_importer": Path("tools/import_winner_v22_normalized_predictor_cpu_result.py"),
    "result_importer_tests": Path("tests/test_winner_v22_normalized_predictor_cpu_import.py"),
    "attribution": Path("outputs/analysis/winner_v21_normalized_semantics_attribution.json"),
    "attribution_builder": Path("tools/build_winner_v21_normalized_semantics_attribution.py"),
    "stage1_result": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"),
    "winner_v21_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "winner_v20_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "winner_v15_objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_payload() -> dict[str, Any]:
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1["snapshot_manifest"][-1]
    if (
        attribution.get("status") != "PASS_WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_CORRECT_NORMALIZED_PREDICTOR_CPU_CONTRACT_ONLY"
        or attribution.get("authority", {}).get("optimizer_updates_authorized_now") != 0
        or attribution.get("findings", {}).get("flat_transport_equation_selected") is not False
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v22 CPU-contract source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    return {
        "schema_version": "winner_v22.normalized_predictor_cpu_contract.v1",
        "status": "FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_NORMALIZED_SEMANTICS_PROOF_ONLY",
        "source_artifact": {
            "github_run_id": 29822834921,
            "github_run_attempt": 1,
            "github_run_head_sha": "0b1dac9ea47a93861f72fa5dd393134f36d6db02",
            "github_artifact_id": 8492593761,
            "github_artifact_name": "winner-v13-normalized-response-stage1-v2-29822834921",
            "artifact_zip_sha256": "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680",
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
            "snapshot_sha256": final_snapshot["sha256"],
            "snapshot_bytes": final_snapshot["bytes"],
        },
        "single_correction": {
            "inherited_head_meaning": "normalized next-response coordinates",
            "rejected_formula": "(prediction_normalized - next_response_raw) / target_std",
            "required_formula": (
                "prediction_normalized - ((next_response_raw - target_mean) / target_std)"
            ),
            "required_evaluator": (
                "learned=square(prediction_normalized-normalized_target); "
                "constant=square(normalized_target)"
            ),
            "new_parameters": 0,
            "onnx_abi_change": False,
            "rollout_reward_population_seed_horizon_action_bound_change": False,
            "flat_transport_equation_used": False,
        },
        "frozen_cpu_proof": {
            "optimizer_updates": 0,
            "population": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "rollout_update_index": 0,
            "training_root_seed": 120120,
            "predictor_scale_evaluations": 1,
            "scale_sweep": False,
            "requirements": [
                "exact Stage-1 update-100 source and exact CPU software environment",
                "old raw-coordinate formula reproduces completed Winner-v21 update-1 loss",
                "corrected JAX loss matches an independent NumPy normalized-coordinate evaluator",
                "constant contact target has exactly zero corrected error and exposes the old formula",
                "stored-successor mask is exact and nonempty",
                "corrected predictor gradients open recurrent plus auxiliary leaves only",
                "one corrected head-gradient RMS scale is finite and strictly positive",
                "all twelve combined gradients are finite and nonzero",
                "all parameters remain bit-exact and optimizer updates remain zero",
            ],
        },
        "pass_rule": (
            "Every proof check passes. A pass freezes the single corrected scale and "
            "authorizes only a separately preregistered two-update CPU proof."
        ),
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "winner_v22_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate two-update normalized-predictor CPU proof preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v22 CPU contract")
    payload = build_payload()
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v22 normalized-predictor CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: identical Winner-v13 Stage-1 update-100 snapshot",
                "- Correct formula: `prediction_normalized - ((raw - mean) / std)`",
                "- Optimizer updates / support cells / locomotion / robot: `0 / 0 / 0 / 0`",
                "- Corrected scale evaluations / sweeps: `1 / 0`",
                "- Flat-transport equation: `not used`",
                "",
                "A pass authorizes only a separate two-update CPU proof. It does not",
                "authorize support training, response-conditioned locomotion, or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
