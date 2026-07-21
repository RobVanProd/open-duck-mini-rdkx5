#!/usr/bin/env python3
"""Freeze the two-update Winner-v22 normalized-predictor CPU proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v22_normalized_predictor_two_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V22_NORMALIZED_PREDICTOR_TWO_UPDATE_CPU_CONTRACT_20260721.md"
ZERO_UPDATE = ANALYSIS / "winner_v22_normalized_predictor_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v22_normalized_predictor_two_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v22_normalized_predictor_two_update_cpu_proof.py"),
    "mechanics_v1": Path("patches/winner_v22_normalized_predictor.py"),
    "mechanics_v2": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "mechanics_v1_tests": Path("tests/test_winner_v22_normalized_predictor.py"),
    "mechanics_v2_tests": Path("tests/test_winner_v22_normalized_predictor_v2.py"),
    "contract_tests": Path("tests/test_winner_v22_normalized_predictor_two_update_cpu_contract.py"),
    "workflow": Path(".github/workflows/winner-v22-normalized-predictor-two-update-cpu-proof.yml"),
    "result_importer": Path("tools/import_winner_v22_normalized_predictor_two_update_result.py"),
    "result_importer_tests": Path("tests/test_winner_v22_normalized_predictor_two_update_cpu_import.py"),
    "zero_update_result": Path("outputs/analysis/winner_v22_normalized_predictor_cpu_result.json"),
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
    zero = json.loads(ZERO_UPDATE.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1["snapshot_manifest"][-1]
    if (
        zero.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
        or zero.get("decision")
        != "AUTHORIZE_SEPARATE_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_PREREGISTRATION_ONLY"
        or zero.get("failed_checks") != []
        or zero.get("objective", {}).get("balance", {}).get("predictor_scale")
        != 380.9135437011719
        or zero.get("execution", {}).get("optimizer_updates") != 0
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v22 two-update source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    return {
        "schema_version": "winner_v22.normalized_predictor_two_update_cpu_contract.v1",
        "status": "FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_TWO_UPDATE_CPU_CONTRACT",
        "decision": "AUTHORIZE_EXACT_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_ONLY",
        "source_artifact": {
            "github_artifact_id": 8492593761,
            "artifact_zip_sha256": "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680",
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
            "snapshot_sha256": final_snapshot["sha256"],
            "snapshot_bytes": final_snapshot["bytes"],
        },
        "single_change": {
            "optimizer_gradient": (
                "per-leaf g_ppo + float32(380.9135437011719) * corrected_g_predictor"
            ),
            "predictor_formula": (
                "prediction_normalized - ((next_response_raw - target_mean) / target_std)"
            ),
            "predictor_scale_recomputed": False,
            "predictor_scale_sweep": False,
            "new_parameters": 0,
            "onnx_abi_change": False,
            "flat_transport_equation_used": False,
        },
        "proof": {
            "optimizer_updates": 2,
            "population_per_update": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "training_root_seed": 120120,
            "frozen_predictor_scale": 380.9135437011719,
            "requirements": [
                "both action/reward/mask/episode boundaries remain exact",
                "both recurrent replay errors are at most 1e-6",
                "both stored-successor masks are exact and nonempty",
                "all twelve composed gradients and deltas are nonzero on both updates",
                "all twelve leaves change cumulatively and the optimizer count is two",
                "snapshot and deployable ONNX contracts pass",
                "formal support, locomotion, RDK, and robot counts remain zero",
            ],
        },
        "pass_rule": (
            "Every proof check passes. A pass authorizes only a separately "
            "preregistered 100-update normalized-predictor CPU training run."
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
                "a separate 100-update normalized-predictor training preregistration"
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
        raise FileExistsError("refusing to overwrite Winner-v22 two-update contract")
    payload = build_payload()
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v22 normalized-predictor two-update CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Optimizer updates now / in proof: `0 / 2`",
                "- Corrected predictor scale: `380.9135437011719`; recomputation/sweeps: `0 / 0`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "- Flat-transport equation: `not used`",
                "",
                "A pass authorizes only a separate 100-update training preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
