#!/usr/bin/env python3
"""Preregister T20's one-update support train-through CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t20_support_trainthrough_one_update_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_PREREGISTRATION_20260726.md"
)
T19_CORRECTION = (
    ANALYSIS / "t19_default_off_digest_correction_result.json"
)
T19_RESULT = ANALYSIS / "t19_support_trainthrough_cpu_result.json"
T18_RESULT = ANALYSIS / "t18_rate_coherent_support_result.json"
V119_VALIDATION = (
    ANALYSIS / "winner_v119_recovered_training_validation.json"
)
T10_ASSET_MANIFEST = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t10_response_conditioned_assets_v1/manifest.json"
)
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t19-v3")
COMPOSED_MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
RUNNER = ROOT / "tools" / "run_t20_support_trainthrough_one_update.py"
BUILDER = (
    ROOT
    / "tools"
    / "build_t20_support_trainthrough_one_update_preregistration.py"
)
TEST = ROOT / "tests" / "test_t20_support_trainthrough_one_update.py"
T8_ASSET_BUILDER = ROOT / "tools" / "build_t8_state_coherent_handoff_assets.py"
T17_WRAPPER = ROOT / "tools" / "t17_support_homeomorphism_onnx.py"
T18_WRAPPER = ROOT / "tools" / "t18_rate_coherent_support_onnx.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
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


def receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "kind": "file",
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise FileNotFoundError(resolved)
    return {
        "kind": "directory",
        "path": str(resolved),
        "sha256": directory_sha256(resolved),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite T20 preregistration: {path}"
            )
    t19_correction = json.loads(
        T19_CORRECTION.read_text(encoding="utf-8")
    )
    t19_result = json.loads(T19_RESULT.read_text(encoding="utf-8"))
    t18_result = json.loads(T18_RESULT.read_text(encoding="utf-8"))
    v119 = json.loads(V119_VALIDATION.read_text(encoding="utf-8"))
    t10_assets = json.loads(
        T10_ASSET_MANIFEST.read_text(encoding="utf-8")
    )
    composed_manifest = json.loads(
        COMPOSED_MANIFEST.read_text(encoding="utf-8")
    )
    half_wrapper = next(
        row
        for row in t18_result["wrappers"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    source_checkpoint = Path(
        t10_assets["sources"]["source_checkpoint"]["path"]
    )
    cpu_template = Path(t10_assets["sources"]["cpu_template"]["path"])
    source_policy = Path(
        t10_assets["sources"]["v121_half_policy"]["path"]
    )
    context_policy = Path(half_wrapper["wrapper"]["source_path"])
    wrapped_policy = Path(half_wrapper["wrapper"]["output_path"])
    checks = {
        "t19_corrected_contract_earned_one_update": (
            t19_correction.get("status")
            == "PASS_T19_SUPPORT_TRAINTHROUGH_CPU_CONTRACT_CORRECTED"
            and t19_correction.get("decision")
            == "EARN_T19_ONE_UPDATE_CPU_CONTRACT"
            and t19_correction.get("failed_checks") == []
        ),
        "t19_enabled_mechanism_was_64_of_64": (
            t19_result.get("enabled", {}).get("failed_checks") == []
            and t19_result.get("enabled", {}).get("prefix_valid_count") == 64
            and t19_result.get("enabled", {}).get("episode_reset_count") == 64
        ),
        "v119_source_validation_green": (
            v119.get("status")
            == "PASS_WINNER_V119_RECOVERED_TRAINING_VALIDATION"
            and v119.get("failed_checks") == []
            and v119["checkpoints"][1]["step"] == 1_003_520
        ),
        "source_checkpoint_hash_exact": (
            directory_sha256(source_checkpoint)
            == t10_assets["sources"]["source_checkpoint"]["sha256"]
            == v119["checkpoints"][1]["directory_sha256"]
        ),
        "cpu_template_hash_exact": (
            directory_sha256(cpu_template)
            == t10_assets["sources"]["cpu_template"]["sha256"]
        ),
        "source_policy_hash_exact": (
            sha256(source_policy)
            == t10_assets["sources"]["v121_half_policy"]["sha256"]
        ),
        "t18_context_and_wrapper_hashes_exact": (
            sha256(context_policy)
            == half_wrapper["wrapper"]["source_sha256"]
            and sha256(wrapped_policy)
            == half_wrapper["wrapper"]["output_sha256"]
        ),
        "composed_schema_exact": (
            composed_manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "no_hosted_or_robot_authority": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "t19_corrected_result": receipt(T19_CORRECTION),
        "t19_formal_result": receipt(T19_RESULT),
        "t18_result": receipt(T18_RESULT),
        "v119_recovered_validation": receipt(V119_VALIDATION),
        "t10_asset_manifest": receipt(T10_ASSET_MANIFEST),
        "composed_manifest": receipt(COMPOSED_MANIFEST),
        "reference": receipt(REFERENCE),
        "runner": receipt(RUNNER),
        "builder": receipt(BUILDER),
        "test": receipt(TEST),
        "t8_context_abi_builder": receipt(T8_ASSET_BUILDER),
        "t17_homeomorphism_wrapper": receipt(T17_WRAPPER),
        "t18_rate_wrapper": receipt(T18_WRAPPER),
    }
    assets = {
        "source_checkpoint": directory_receipt(source_checkpoint),
        "cpu_topology_template": directory_receipt(cpu_template),
        "source_v121_half_onnx": receipt(source_policy),
        "frozen_t18_context_abi_onnx": receipt(context_policy),
        "frozen_t18_wrapped_onnx": receipt(wrapped_policy),
    }
    basis = {
        "schema_version": (
            "open_duck.t20_support_trainthrough_one_update_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE"
            if not failed
            else "HOLD_T20_SUPPORT_TRAINTHROUGH_ONE_UPDATE_PREREGISTRATION"
        ),
        "question": (
            "Can the exact V121-half tree be restored through a CPU topology "
            "remap, execute one finite 1,024-step PPO smoke through T19's "
            "support/reset transition, and export the exact T18 physical "
            "deployment hierarchy at step zero plus a valid updated graph?"
        ),
        "causal_basis": {
            "t18": (
                "The zero-training physical support composition retained "
                "25/32 cells, with the residual misses localized to "
                "saturation and two falls."
            ),
            "t19": (
                "The train-through environment and complete episode reset "
                "passed every enabled check across 64 variable configurations "
                "and exact default-off parity."
            ),
            "minimal_update": (
                "Change no actor architecture, reward, rate vector, support "
                "action, map, bridge, or reset. Test only whether the existing "
                "V121 actor can update through the selected transition."
            ),
        },
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(COMPOSED.resolve()),
            "manifest_sha256": sha256(COMPOSED_MANIFEST),
            "final_python_hashes": composed_manifest["final_python_hashes"],
        },
        "contract": {
            "source": "V121_TRAIN_MATCHED_HALF",
            "source_step": 1_003_520,
            "cpu_topology_remap": (
                "restore source into frozen CPU template, save once to the "
                "fresh work root, restore again, and require exact tree/leaf "
                "equality before training"
            ),
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
            "unchanged_training_recipe": {
                "policy_architecture": (
                    "reference_residual_recurrent_adapter"
                ),
                "recurrent_hidden_size": 64,
                "policy_observation_dim": 115,
                "runtime_observation_dim": 101,
                "actions": 14,
                "reference_support_x": [0.074, 0.080],
                "variable_configuration_scale": 1.0,
                "t19_support_trainthrough": True,
                "t19_calibration_ticks": 250,
                "t19_home_return_ticks": 0,
                "full_episode_handoff_reset": True,
                "rate_limits_rad_s": [
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
                ],
            },
            "required_exports": [0, 1024],
            "step_zero_requirements": [
                "checkpoint tree exact to V121-half after CPU remap",
                "raw ONNX byte-exact to frozen V121-half deployment graph",
                "diagnostic context ABI byte-exact to T8/T18 source",
                "physical support/rate wrapper byte-exact to T18 half",
            ],
            "step_1024_requirements": [
                "tree structure exact and every actor/critic leaf finite",
                "every actor and critic leaf changes",
                "raw/context/wrapped graphs have exact ABI",
                "context input remains bit-exactly ignored",
                "physical wrapper matches T18 equations on 256 CPU cases",
                "x=0 emits support exactly and previous_action_out is final action",
            ],
        },
        "decision_rule": {
            "pass": (
                "Every restore, update, export, graph, CPU, authority, and "
                "receipt check passes."
            ),
            "pass_next_action": (
                "Earn only a separately preregistered, no-retry hosted "
                "continuation from V121-half through the exact T19 transition."
            ),
            "fail": (
                "Keep hosted training closed and file the exact failed check; "
                "no scalar, map, reset, support, or rate tuning."
            ),
            "partial_result_weight": 0,
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
                "# T20 support train-through one-update preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- CPU simulator steps: `1,024`",
                "- Formal behavior cells: `0`",
                "- Hosted/robot execution: `0/0`",
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
