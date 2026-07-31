#!/usr/bin/env python3
"""Freeze T215B's axis-complete tilt dual CPU software contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t215b_axis_complete_tilt_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T215B_AXIS_COMPLETE_TILT_CPU_PREREGISTRATION_20260730.md"
)
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t209_dual_roll_cost_cpu_source_v3"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t215b_axis_complete_tilt_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t203_colab_recovery_20260730/extracted/"
    "t203_predicted_roll_risk_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_125443_1003520"
SOURCE_RAW = TRAINING / "2026_07_30_125443_1003520.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/t100c_half_cpu_remap"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
MANIFEST = PLAYGROUND / "T215B_COMPOSED_SOURCE_MANIFEST.json"
T214B = ANALYSIS / "t214b_axis_complete_tilt_source_transfer_result.json"
T204 = ANALYSIS / "t204_t203_recovered_training_validation.json"
T209 = ANALYSIS / "t209_dual_roll_cost_cpu_result.json"
BUILDER = Path(__file__).resolve()
MODULE = ROOT / "training/t215b_axis_complete_tilt.py"
PATCH = ROOT / "patches/winner_t215b_axis_complete_tilt.patch"
COMPOSER = ROOT / "tools/compose_t215b_axis_complete_tilt_playground.py"
ENV_WORKER = ROOT / "tools/run_t215b_environment_contract_worker.py"
RUNNER = ROOT / "tools/run_t215b_axis_complete_tilt_cpu_contract.py"
TEST = ROOT / "tests/test_t215b_axis_complete_tilt.py"

READBACK = (
    "T215B_AXIS_COMPLETE_TILT_COST="
    "horizon_s=0.08,"
    "roll_envelope_rad=0.3541802655745987,"
    "pitch_envelope_rad=0.2379576557426921,"
    "score=max(roll_norm,pitch_norm),"
    "cost=unscaled_squared_box_excess,"
    "reward_channel=unchanged,cost_critic=separate,"
    "cost_discount=1.0,"
    "actor_advantage=(A_R-lambda*A_C)/(1+lambda),"
    "dual_eta=1/(ceil(K/4)*J_C0),"
    "deployment_graph=unchanged"
)


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
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T215B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T215B preregistration requires clean worktree")
    required_dirs = (BASE, PLAYGROUND, SOURCE, TOPOLOGY)
    required_files = (
        SOURCE_RAW,
        REFERENCE,
        GATE,
        MANIFEST,
        T214B,
        T204,
        T209,
        BUILDER,
        MODULE,
        PATCH,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
    )
    if not all(path.is_dir() for path in required_dirs):
        raise FileNotFoundError("T215B required directory missing")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("T215B required file missing")

    t214b = load(T214B)
    t204 = load(T204)
    t209 = load(T209)
    manifest = load(MANIFEST)
    module_text = MODULE.read_text(encoding="utf-8")
    patch_text = PATCH.read_text(encoding="utf-8")
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    t204_half = next(
        item
        for item in t204["exports"]["checkpoints"]
        if int(item["step"]) == 1003520
    )
    t204_half_onnx = next(
        item
        for item in t204["exports"]["onnx"]
        if int(item["step"]) == 1003520
    )
    checks = {
        "t214b_earns_only_t215b_cpu_preregistration": (
            t214b["status"]
            == "PASS_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
            and not t214b["failed_checks"]
            and t214b["decision"]
            == (
                "EARN_T215B_AXIS_COMPLETE_TILT_DUAL_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
            and t214b["dominant_failure_axes"] == ["pitch", "roll"]
        ),
        "t203_half_is_exact_protected_source": (
            Path(t204_half["path"]).resolve() == SOURCE.resolve()
            and t204_half["directory_sha256"] == directory_sha256(SOURCE)
            and t204_half_onnx["sha256"] == sha256(SOURCE_RAW)
            and t204["status"]
            == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
        ),
        "validated_t209_dual_engine_is_reused": (
            t209["status"] == "PASS_T209_DUAL_ROLL_COST_CPU_CONTRACT"
            and not t209["failed_checks"]
            and t209["checks"]["cost_critic_structure_exact"]
            and t209["checks"][
                "synthetic_persistent_cost_reaches_one_by_quarter"
            ]
        ),
        "axis_complete_cost_is_exact_and_unscaled": (
            "ROLL_PASSING_ENVELOPE_RAD = 0.3541802655745987"
            in module_text
            and "PITCH_PASSING_ENVELOPE_RAD = 0.2379576557426921"
            in module_text
            and "jnp.maximum(roll_normalized, pitch_normalized)"
            in module_text
            and "return jnp.square(tilt_box_excess(score))"
            in module_text
            and "constrained_cost = jp.square(box_excess)" in patch_text
        ),
        "old_roll_and_reward_costs_are_disabled": (
            "not args.winner_t209_dual_roll_cost" in patch_text
            and "not args.winner_t202_predicted_roll_risk" in patch_text
        ),
        "deployment_graph_and_policy_abi_unchanged": (
            "deployment_graph=unchanged" in patch_text
            and manifest["scientific_scope"]["policy_abi_unchanged"]
            and manifest["scientific_scope"][
                "deployment_graph_unchanged"
            ]
        ),
        "composed_manifest_and_inventory_present": (
            manifest["schema_version"]
            == "open_duck.t215b_composed_source.v1"
            and bool(python_inventory)
            and python_inventory[
                "playground/common/t215b_axis_complete_tilt.py"
            ]
            == sha256(MODULE)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": file_receipt(BUILDER),
        "tilt_module": file_receipt(MODULE),
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
        "reference_features": file_receipt(REFERENCE),
        "hidden_gate_static_asset": file_receipt(GATE),
        "t214b_selection_result": file_receipt(T214B),
        "t204_source_validation": file_receipt(T204),
        "t209_engine_cpu_result": file_receipt(T209),
        "composed_source_manifest": file_receipt(MANIFEST),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t215b_axis_complete_tilt_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
        ),
        "mechanism": {
            "source": "T203_HALF",
            "prediction_horizon_s": 0.08,
            "roll_passing_envelope_rad": 0.3541802655745987,
            "pitch_passing_envelope_rad": 0.2379576557426921,
            "score": "max(roll_risk/roll_envelope,pitch_risk/pitch_envelope)",
            "cost": "square(max(0,score-1))",
            "cost_scale": 1.0,
            "cost_channel": "separate_unclipped_training_only",
            "reward_channel": "unchanged_original_clipped_reward",
            "cost_critic": "separate",
            "cost_discount": 1.0,
            "cost_gae_lambda": "frozen_T203_reward_GAE_lambda",
            "actor_advantage": "(A_R-lambda*A_C)/(1+lambda)",
            "dual_initial_lambda": 0.0,
            "dual_update": "lambda=max(0,lambda+eta*J_C)",
            "dual_eta": "1/(ceil(K/4)*J_C0)",
            "deployment_graph_change": False,
            "policy_abi_change": False,
            "trainable_actor_groups": ["negative_adapter_location"],
            "reward_critic_trainable": True,
            "cost_critic_trainable": True,
            "scalar_or_axis_sweep": False,
            "t210_eta_retry": False,
        },
        "training_smoke": {
            "timesteps": 1024,
            "num_envs": 8,
            "environments_per_stratum": 1,
            "source_checkpoint": str(SOURCE.resolve()),
            "export_steps": [0, 1024],
            "all_nonconstraint_PPO_values": "bit_exact_T203",
            "formal_behavior_cells": 0,
        },
        "environment_contract": {
            "default_off_steps": 8,
            "enabled_source_policy_ticks": 108,
            "enabled_seed": 215,
            "synthetic_roll_rate_rad_s": 10.0,
            "synthetic_pitch_rate_rad_s": 10.0,
            "metric_error_tolerance": 1.0e-7,
            "reward_must_remain_bit_equal_to_original_clip": True,
        },
        "expected_runner_readback": READBACK,
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
                "EARN_T216_AXIS_COMPLETE_TILT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T215B_AXIS_COMPLETE_TILT_WITHOUT_HOSTED_TRAINING"
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
        "# T215B axis-complete tilt CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Source: exact protected T203 half checkpoint\n"
        "- Change: independent roll/pitch pass envelopes feeding one "
        "componentwise normalized safety-box cost\n"
        "- Reward, policy ABI, and deployment graph: unchanged\n"
        "- CPU optimizer / formal behavior / hosted / robot now: "
        "`0/0/0/0`\n"
        f"- Failed checks: `{failed}`\n",
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
