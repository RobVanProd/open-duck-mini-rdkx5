#!/usr/bin/env python3
"""Freeze the explicit-gradient two-update Winner-v21 CPU proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v21_predictor_preserving_two_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_CONTRACT_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v21_gradient_composition_attribution.json"
ZERO_UPDATE = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v21_predictor_preserving_two_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v21_predictor_preserving_two_update_cpu_proof.py"),
    "mechanics_v1": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "mechanics_v2": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "mechanics_v1_tests": Path("tests/test_winner_v21_predictor_preserving_joint_support.py"),
    "mechanics_v2_tests": Path("tests/test_winner_v21_predictor_preserving_joint_support_v2.py"),
    "contract_tests": Path("tests/test_winner_v21_predictor_preserving_two_update_cpu_contract.py"),
    "workflow": Path(".github/workflows/winner-v21-predictor-preserving-two-update-cpu-proof.yml"),
    "result_importer": Path("tools/import_winner_v21_predictor_preserving_two_update_result.py"),
    "result_importer_tests": Path("tests/test_winner_v21_predictor_preserving_two_update_cpu_import.py"),
    "gradient_attribution": Path("outputs/analysis/winner_v21_gradient_composition_attribution.json"),
    "zero_update_result": Path("outputs/analysis/winner_v21_predictor_preserving_joint_cpu_result.json"),
    "stage1_result": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"),
    "winner_v20_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "winner_v15_objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v21 two-update contract")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    zero_update = json.loads(ZERO_UPDATE.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1["snapshot_manifest"][-1]
    if (
        attribution.get("status")
        != "PASS_WINNER_V21_GRADIENT_COMPOSITION_ATTRIBUTION"
        or attribution.get("decision")
        != "PREREGISTER_EXPLICITLY_COMPOSED_TWO_UPDATE_CPU_PROOF"
        or attribution.get("authority", {}).get("optimizer_updates_authorized_now") != 0
        or zero_update.get("status")
        != "HOLD_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
        or zero_update.get("failed_checks")
        != ["combined_gradient_is_exact_sum_at_most_1e_6"]
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v21 two-update source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v21.predictor_preserving_two_update_cpu_contract.v1",
        "status": "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_CONTRACT",
        "decision": "AUTHORIZE_EXACT_TWO_UPDATE_EXPLICIT_GRADIENT_PROOF_ONLY",
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
        "single_change": {
            "reference": "frozen Winner-v21 zero-update candidate",
            "optimizer_gradient": (
                "per-leaf g_ppo + float32(8.393629541414427e-11) * g_predictor"
            ),
            "combined_scalar_loss": "logging only; never differentiated for the optimizer",
            "predictor_scale_recomputed": False,
            "predictor_scale_sweep": False,
            "objective_rollout_population_seed_horizon_action_bound_change": False,
            "new_parameters": 0,
            "onnx_abi_change": False,
            "flat_transport_equation_used": False,
        },
        "proof": {
            "optimizer_updates": 2,
            "population_per_update": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "training_root_seed": 120120,
            "frozen_predictor_scale": 8.393629541414427e-11,
            "predictor_scale_evaluations": 0,
            "requirements": [
                "both rollouts preserve Winner-v15 reward/action/mask/episode data bit-exactly",
                "both sampled recurrent replay errors are at most 1e-6",
                "both stored-successor target masks are exact and nonempty",
                "all twelve explicitly composed gradients and parameter deltas are nonzero on both updates",
                "all twelve parameter leaves change cumulatively",
                "the twelve-leaf optimizer snapshot round-trips exactly after update two",
                "the deployable ONNX ABI and JAX chain checks pass unchanged",
                "formal support, locomotion, RDK, and robot counts remain zero",
            ],
        },
        "pass_rule": (
            "Every two-update proof check passes. A pass authorizes only a separately "
            "preregistered 100-update predictor-preserving CPU training run."
        ),
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "winner_v21_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate 100-update predictor-preserving training preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v21 predictor-preserving two-update CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Optimizer updates now / in proof: `0 / 2`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "- Predictor scale: frozen once; no recomputation or sweep",
                "- Flat-transport equation: `not used`",
                "",
                "The optimizer consumes the explicit per-leaf sum of the separately",
                "differentiated PPO and predictor gradients. This addresses only the",
                "observed float32 accumulation-order discrepancy. A pass authorizes",
                "a separate 100-update training preregistration, nothing further.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
