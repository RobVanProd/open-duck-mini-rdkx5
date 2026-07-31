#!/usr/bin/env python3
"""Preregister T22's corrected 1,024-step CPU smoke."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t22_corrected_one_update_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T22_CORRECTED_ONE_UPDATE_CPU_PREREGISTRATION_20260726.md"
)
T21B_RESULT = ANALYSIS / "t21b_source_initialization_cpu_result.json"
T20_ATTRIBUTION = ANALYSIS / "t20_two_rate_mismatch_attribution.json"
T20_PREREGISTRATION = (
    ANALYSIS
    / "t20_support_trainthrough_one_update_recovery_preregistration.json"
)
V121_PREREGISTRATION = (
    ANALYSIS / "winner_v121_deployment_transform_preregistration.json"
)
V121_RAW = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v119-extracted-20260724/"
    "winner_v119_transition_continuation/training/"
    "2026_07_24_193907_1003520.onnx"
)
V121_DEPLOYED = Path(
    "D:/CodexArtifacts/open-duck-mini-rdkx5/"
    "winner-v121-deployment-policies-20260724/"
    "V121_DEPLOYMENT_1003520.onnx"
)
COMPOSED = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6"
)
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
RUNNER = ROOT / "tools" / "run_t22_corrected_one_update_cpu_smoke.py"
BUILDER = (
    ROOT / "tools" / "build_t22_corrected_one_update_cpu_preregistration.py"
)
TEST = ROOT / "tests" / "test_t22_corrected_one_update_cpu_smoke.py"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
SOURCE_RATES = [
    1.0,
    0.75,
    1.4736209064722061,
    1.4300791546702385,
    1.3976470567286015,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.75,
    1.25,
    1.0,
    1.2215287424623966,
]
EXTERNAL_RATES = [
    1.0,
    0.75,
    1.5,
    1.5,
    1.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.75,
    1.25,
    1.0,
    1.25,
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "kind": "file",
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T22: {path}")
    t21b = json.loads(T21B_RESULT.read_text(encoding="utf-8"))
    t20_attribution = json.loads(
        T20_ATTRIBUTION.read_text(encoding="utf-8")
    )
    original = json.loads(T20_PREREGISTRATION.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    v121_prereg = json.loads(
        V121_PREREGISTRATION.read_text(encoding="utf-8")
    )
    sources = {
        "t21b_result": file_receipt(T21B_RESULT),
        "t20_two_rate_attribution": file_receipt(T20_ATTRIBUTION),
        "reference": file_receipt(REFERENCE),
        "composed_manifest": file_receipt(MANIFEST),
        "t19_module": file_receipt(
            ROOT / "patches" / "t19_support_trainthrough.py"
        ),
        "t19_patch": file_receipt(
            ROOT / "patches" / "winner_t19_support_trainthrough.patch"
        ),
        "t20_base_runner": file_receipt(
            ROOT / "tools" / "run_t20_support_trainthrough_one_update.py"
        ),
        "t22_runner": file_receipt(RUNNER),
        "t22_builder": file_receipt(BUILDER),
        "t22_test": file_receipt(TEST),
        "v121_transform_preregistration": file_receipt(
            V121_PREREGISTRATION
        ),
        "guard_transform": file_receipt(
            ROOT / "tools" / "build_ground_up_actual_centered_guard_screen.py"
        ),
        "deadband_transform": file_receipt(
            ROOT / "tools" / "build_ground_up_command_deadband_repair.py"
        ),
        "source_rate_transform": file_receipt(
            ROOT
            / "tools"
            / "build_winner_v117_postguard_rate_projection_policies.py"
        ),
        "context_abi_builder": file_receipt(
            ROOT / "tools" / "build_t8_state_coherent_handoff_assets.py"
        ),
        "external_rate_wrapper": file_receipt(
            ROOT / "tools" / "t18_rate_coherent_support_onnx.py"
        ),
    }
    assets = dict(original["assets"])
    assets["source_v121_half_onnx"] = file_receipt(V121_RAW)
    assets["frozen_v121_deployed_half_onnx"] = file_receipt(
        V121_DEPLOYED
    )
    checks = {
        "t21b_passed_and_earned_t22": (
            t21b.get("status")
            == "PASS_T21B_SOURCE_INITIALIZATION_CPU_CONTRACT"
            and t21b.get("decision")
            == "EARN_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
            and t21b.get("failed_checks") == []
        ),
        "t20_training_has_zero_selection_weight": (
            t20_attribution.get("attribution", {}).get(
                "t20_training_selection_weight"
            )
            == 0
        ),
        "v121_transform_is_frozen_green": (
            v121_prereg.get("status")
            == "PREREGISTERED_WINNER_V121_DEPLOYMENT_TRANSFORM"
            and v121_prereg.get("failed_checks") == []
        ),
        "all_four_step_zero_assets_exact": (
            assets["source_v121_half_onnx"]["sha256"]
            == "2d3cfb686a9c9643d9414a99a10e4db3aee7fc8f63cbc2fd81f107b487cf1311"
            and assets["frozen_v121_deployed_half_onnx"]["sha256"]
            == "d4f280e8ebb4accd5c5c983bbf83042ec0162647efb446f0f6c8bffda42bc17a"
            and assets["frozen_t18_context_abi_onnx"]["sha256"]
            == "8749ba91e98c18b8c2d123bae3558154bc7221cc8b58c1a8ad6c9adc39d8ae4a"
            and assets["frozen_t18_wrapped_onnx"]["sha256"]
            == "31d81484ab2faa301488a7eb4962f9ab7f56f8be1127d0126a25ba1c1d0aef1e"
        ),
        "source_and_external_rates_are_separated": (
            SOURCE_RATES != EXTERNAL_RATES
            and all(
                source <= external
                for source, external in zip(
                    SOURCE_RATES,
                    EXTERNAL_RATES,
                    strict=True,
                )
            )
        ),
        "composed_v6_schema_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "one_cpu_smoke_only": True,
        "hosted_and_robot_authority_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t22_corrected_one_update_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
            if not failed
            else "HOLD_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
        ),
        "question": (
            "Can the T21b-corrected two-rate environment restore V121-half "
            "exactly, update every actor/critic leaf in 1,024 CPU simulator "
            "steps, and reproduce the complete four-stage step-zero deployment "
            "chain byte-for-byte?"
        ),
        "causal_basis": {
            "t20_hold": (
                "T20 optimizer plumbing was finite and updated every leaf, but "
                "its raw actor used the full external rate vector and omitted "
                "the V121 source deployment hierarchy; its training output has "
                "zero selection weight."
            ),
            "t21b_gate": (
                "The corrected source/external ownership and coherent prefix "
                "initialization pass all zero-optimizer CPU contracts."
            ),
            "deployment_chain": (
                "raw V121 actor -> exact V121 G3/deadband/final source-rate "
                "hierarchy -> ignored context ABI -> T18 support homeomorphism "
                "and full external physical-rate projection"
            ),
            "scope": (
                "one 1,024-step CPU restore/update/export smoke; no behavior "
                "cells, hosted compute, checkpoint selection, or hardware"
            ),
        },
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(COMPOSED.resolve()),
            "manifest_sha256": sha256(MANIFEST),
            "final_python_hashes": manifest["final_python_hashes"],
        },
        "contract": {
            "source": "V121_TRAIN_MATCHED_HALF",
            "source_step": 1003520,
            "policy_observation_dim": 115,
            "runtime_observation_dim": 101,
            "actions": 14,
            "recurrent_hidden_size": 64,
            "source_rate_limits_rad_s": SOURCE_RATES,
            "external_rate_limits_rad_s": EXTERNAL_RATES,
            "optimizer_smoke": {
                "simulator_steps_exact": 1024,
                "seed": 100,
                "num_envs": 4,
                "num_evals": 2,
                "episode_length": 64,
                "unroll_length": 8,
                "batch_size": 4,
                "num_minibatches": 1,
                "updates_per_batch": 2,
                "learning_rate": 0.0003,
                "discounting": 0.97,
                "entropy_cost": 0.005,
                "maximum_wall_seconds": 1800,
            },
            "required_exports": [0, 1024],
            "step_zero_hashes": {
                "raw": assets["source_v121_half_onnx"]["sha256"],
                "source_deployed": assets[
                    "frozen_v121_deployed_half_onnx"
                ]["sha256"],
                "context_abi": assets["frozen_t18_context_abi_onnx"][
                    "sha256"
                ],
                "final_external": assets["frozen_t18_wrapped_onnx"][
                    "sha256"
                ],
            },
            "restore_requirement": (
                "CPU topology remap and step-zero checkpoint exact to the "
                "frozen source"
            ),
            "update_requirement": (
                "all actor and critic leaves change; all trees and metrics "
                "remain finite"
            ),
            "export_requirement": (
                "both 0/1024 graphs pass raw, source-deployment, context, "
                "external-wrapper ABI and inference contracts"
            ),
        },
        "decision_rule": {
            "pass": (
                "earn only a separate hosted-continuation preregistration; "
                "hosted execution is not yet authorized"
            ),
            "fail": (
                "keep hosted training closed and attribute the exact failing "
                "restore/update/export check without retry"
            ),
            "partial_results": "zero decision weight",
        },
        "authority": {
            "cpu_optimizer_steps_authorized": 1024,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": False,
            "hosted_training": False,
            "checkpoint_selection": False,
            "policy_deployment": False,
            "gate5": False,
            "robot_or_rdk_access": False,
            "torque_or_motion": False,
        },
        "checks": checks,
        "failed_checks": failed,
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T22 corrected one-update CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- CPU simulator steps authorized: `1,024`",
                "- Behavior/hosted/robot authority: `0/0/0`",
                (
                    "- Pass earns only a separate hosted-continuation "
                    "preregistration."
                ),
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
