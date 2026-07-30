#!/usr/bin/env python3
"""Freeze T193's corrected dynamic reference-support CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS
    / "t193_corrected_dynamic_reference_support_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_CPU_"
    "PREREGISTRATION_20260730.md"
)
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_original_driver_wrapper_package_v1/"
    "t100c_original_driver_wrapper_bundle/playground"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t193_corrected_dynamic_reference_support_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t170_colab_recovery_20260729/extracted/"
    "t170_eight_stratum_head_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_003907_1003520"
SOURCE_RAW = TRAINING / "2026_07_30_003907_1003520.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/t100c_half_cpu_remap"
)
REFERENCE_FEATURES = (
    ANALYSIS / "ground_up_projected_reference_feature_table.npz"
)
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
COMPOSED_MANIFEST = PLAYGROUND / "T193_COMPOSED_SOURCE_MANIFEST.json"
T185_PREREG = (
    ANALYSIS / "t185_in_episode_single_support_cpu_preregistration.json"
)
T185F_RESULT = (
    ANALYSIS / "t185f_metric_runner_path_recovery_result.json"
)
T190B_RESULT = (
    ANALYSIS / "t190b_interrupted_execution_recovery_result.json"
)
T192B_RESULT = (
    ANALYSIS / "t192b_switch_effect_attribution_result.json"
)
BUILDER = Path(__file__).resolve()
MODULE = ROOT / "patches/t193_corrected_dynamic_reference_support.py"
PATCH = (
    ROOT / "patches/winner_t193_corrected_dynamic_reference_support.patch"
)
COMPOSER = (
    ROOT
    / "tools/compose_t193_corrected_dynamic_reference_support_playground.py"
)
ENV_WORKER = ROOT / "tools/run_t193_environment_contract_worker.py"
RUNNER = (
    ROOT
    / "tools/run_t193_corrected_dynamic_reference_support_cpu_contract.py"
)
TEST = ROOT / "tests/test_t193_corrected_dynamic_reference_support.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode())
            digest.update(b"\0")
            with item.open("rb") as stream:
                for block in iter(
                    lambda: stream.read(1024 * 1024), b""
                ):
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
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "directory",
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T193: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T193 preregistration requires clean worktree")
    required_dirs = (BASE, PLAYGROUND, SOURCE, TOPOLOGY)
    required_files = (
        SOURCE_RAW,
        REFERENCE_FEATURES,
        GATE,
        COMPOSED_MANIFEST,
        T185_PREREG,
        T185F_RESULT,
        T190B_RESULT,
        T192B_RESULT,
        BUILDER,
        MODULE,
        PATCH,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
    )
    if not all(path.is_dir() for path in required_dirs):
        raise FileNotFoundError("T193 required directory missing")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("T193 required file missing")

    t185 = load(T185_PREREG)
    t185f = load(T185F_RESULT)
    t190b = load(T190B_RESULT)
    t192b = load(T192B_RESULT)
    reference_contract = t185["reference_contract"]
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    checks = {
        "t192b_earns_only_t193_cpu_preregistration": (
            t192b.get("status")
            == "PASS_T192B_SWITCH_EFFECT_ATTRIBUTION"
            and t192b.get("decision")
            == "EARN_T193_CORRECTED_DYNAMIC_SUPPORT_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
        ),
        "t185_cpu_mechanism_was_software_valid": (
            t185f.get("status")
            == "PASS_T185F_METRIC_READBACK_RECOVERY"
        ),
        "t186_is_closed_without_checkpoint_selection": (
            t190b.get("status")
            == "HOLD_T190B_INTERRUPTED_EXECUTION_RECOVERY"
            and t190b.get("decision")
            == "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION"
        ),
        "reference_contacts_are_frozen_left_right_channels": (
            reference_contract.get("contact_channels") == [32, 34]
            and reference_contract.get("contact_order")
            == ["left", "right"]
            and reference_contract.get("period_ticks") == 27
        ),
        "old_phase_sign_mapping_is_proven_wrong": bool(
            reference_contract.get(
                "t55_mapping_disagrees_with_reference_at_both_anchors"
            )
        ),
        "correct_reference_anchors_are_frozen": (
            reference_contract.get("support_phase_anchors")
            == {"left": 2, "right": 15}
        ),
        "source_is_exact_t170_half": (
            SOURCE.name == "2026_07_30_003907_1003520"
            and SOURCE_RAW.stem == SOURCE.name
        ),
        "composed_source_inventory_present": bool(python_inventory),
        "implementation_has_no_tunable_support_scale": (
            "ALIVE_REWARD_PER_TICK = ALIVE_REWARD_SCALE * CONTROL_DT_S"
            in MODULE.read_text(encoding="utf-8")
            and "original_reward) + jnp.asarray(support_reward)"
            in MODULE.read_text(encoding="utf-8")
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": file_receipt(BUILDER),
        "module": file_receipt(MODULE),
        "source_patch": file_receipt(PATCH),
        "composer": file_receipt(COMPOSER),
        "environment_worker": file_receipt(ENV_WORKER),
        "runner": file_receipt(RUNNER),
        "unit_test": file_receipt(TEST),
    }
    assets = {
        "source_checkpoint": directory_receipt(SOURCE),
        "source_raw_onnx": file_receipt(SOURCE_RAW),
        "cpu_topology_template": directory_receipt(TOPOLOGY),
        "reference_features": file_receipt(REFERENCE_FEATURES),
        "hidden_gate_static_asset": file_receipt(GATE),
        "t185_reference_contract": file_receipt(T185_PREREG),
        "t185_cpu_result": file_receipt(T185F_RESULT),
        "t190b_closure": file_receipt(T190B_RESULT),
        "t192b_earning_decision": file_receipt(T192B_RESULT),
        "composed_source_manifest": file_receipt(COMPOSED_MANIFEST),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t193_corrected_dynamic_reference_support_"
            "cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
            "CPU_CONTRACT"
        ),
        "mechanism": {
            "source": "T170_HALF",
            "reference_contact_slice": [32, 34],
            "reference_contact_order": ["left", "right"],
            "activation": (
                "every locomotion tick whose reference row requests exact "
                "single support"
            ),
            "match": "exact observed single support on requested side",
            "tilt_quality": (
                "exp(-sum((predicted_roll_pitch/0.25)^2))"
            ),
            "prediction_horizon_ticks": 4,
            "perfect_match_reward_per_tick": 0.4,
            "scale_derivation": "existing alive scale 20.0 * dt 0.02",
            "objective": "original_clipped_reward + support_reward",
            "phase_sign_heuristic": False,
            "phase_freeze_or_prefix": False,
            "separate_optimizer_stage": False,
            "deployment_graph_change": False,
            "trainable_actor_groups": [
                "negative_adapter_location"
            ],
            "protected": [
                "mature actor outside negative_adapter_location",
                "observation normalizer",
                "policy ABI",
                "deployment action graph",
            ],
        },
        "reference_contract": reference_contract,
        "training_smoke": {
            "timesteps": 1024,
            "num_envs": 8,
            "environments_per_stratum": 1,
            "source_checkpoint": str(SOURCE),
            "export_steps": [0, 1024],
        },
        "environment_contract": {
            "default_off_steps": 8,
            "enabled_source_policy_ticks": 108,
            "enabled_seed": 193,
            "both_reference_sides_required": True,
            "both_matched_sides_required": True,
            "metric_module_error": 0.0,
            "objective_addition_error": 0.0,
            "formal_behavior_cells": 0,
        },
        "expected_runner_readback": (
            "T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT="
            "reference_channels=32:34,objective=original_plus_support,"
            "perfect_tick=0.4,phase_heuristic=none,"
            "active=all_locomotion"
        ),
        "sources": sources,
        "assets": assets,
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "base_path": str(BASE.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(
                python_inventory
            ),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "EARN_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_AND_"
                "RETURN_TO_MECHANISM_SELECTION"
            ),
            "no_hosted_run_from_preregistration_alone": True,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_cpu_contract": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
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
        "# T193 corrected dynamic reference-support CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Source: exact T170 half\n"
        "- Objective: unchanged locomotion reward plus an alive-derived "
        "reference-contact support reward on every applicable gait tick\n"
        "- Reference contacts: `[32:34]`, left then right; no phase-sign "
        "heuristic and no reset-only prefix\n"
        "- CPU optimizer / formal behavior / hosted / robot now: "
        "`0/0/0/0`\n"
        f"- Failed checks: `{failed}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
