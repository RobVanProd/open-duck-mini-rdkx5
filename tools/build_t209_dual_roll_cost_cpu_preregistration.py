#!/usr/bin/env python3
"""Freeze T209's dual roll-cost CPU training contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t209_dual_roll_cost_cpu_preregistration.json"
MARKDOWN = ANALYSIS / "T209_DUAL_ROLL_COST_CPU_PREREGISTRATION_20260730.md"
BASE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t202_predicted_roll_risk_cpu_source_v1"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t209_dual_roll_cost_cpu_source_v3"
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
MANIFEST = PLAYGROUND / "T209_COMPOSED_SOURCE_MANIFEST.json"
T208 = ANALYSIS / "t208_t203_persistence_autopsy_result.json"
T204 = ANALYSIS / "t204_t203_recovered_training_validation.json"
V127 = ANALYSIS / "winner_v127_constrained_cpu_result.json"
V128 = ANALYSIS / "winner_v128_nominal_behavior_result.json"
BUILDER = Path(__file__).resolve()
PATCH = ROOT / "patches/winner_t209_dual_roll_cost.patch"
COMPOSER = ROOT / "tools/compose_t209_dual_roll_cost_playground.py"
ENV_WORKER = ROOT / "tools/run_t209_environment_contract_worker.py"
RUNNER = ROOT / "tools/run_t209_dual_roll_cost_cpu_contract.py"
TEST = ROOT / "tests/test_t209_dual_roll_cost.py"
ENGINE_TRAIN = PLAYGROUND / (
    "playground/common/winner_v127_constrained_ppo_train.py"
)
ENGINE_LOSSES = PLAYGROUND / (
    "playground/common/winner_v127_constrained_ppo_losses.py"
)

READBACK = (
    "T209_DUAL_ROLL_COST="
    "horizon_s=0.08,envelope_rad=0.3541802655745987,"
    "cost=unscaled_squared_excess,reward_channel=unchanged,"
    "cost_critic=separate,cost_discount=1.0,"
    "actor_advantage=(A_R-lambda*A_C)/(1+lambda),"
    "dual_eta=1/(ceil(K/4)*J_C0),deployment_graph=unchanged"
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
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T209: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T209 preregistration requires clean worktree")
    required_dirs = (BASE, PLAYGROUND, SOURCE, TOPOLOGY)
    required_files = (
        SOURCE_RAW,
        REFERENCE,
        GATE,
        MANIFEST,
        T208,
        T204,
        V127,
        V128,
        BUILDER,
        PATCH,
        COMPOSER,
        ENV_WORKER,
        RUNNER,
        TEST,
        ENGINE_TRAIN,
        ENGINE_LOSSES,
    )
    if not all(path.is_dir() for path in required_dirs):
        raise FileNotFoundError("T209 required directory missing")
    if not all(path.is_file() for path in required_files):
        raise FileNotFoundError("T209 required file missing")

    t208 = load(T208)
    t204 = load(T204)
    v127 = load(V127)
    v128 = load(V128)
    manifest = load(MANIFEST)
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
        "t208_earns_only_t209_cpu_preregistration": (
            t208["status"] == "PASS_T208_T203_PERSISTENCE_AUTOPSY"
            and t208["failed_checks"] == []
            and t208["classification"]
            == "ROLL_SIGNAL_RETAINED_FIXED_PRICE_LOST_PERSISTENCE"
            and t208["decision"]
            == (
                "EARN_T209_DUAL_ROLL_COST_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t203_half_is_exact_green_source": (
            Path(t204_half["path"]).resolve() == SOURCE.resolve()
            and t204_half["directory_sha256"] == directory_sha256(SOURCE)
            and t204_half_onnx["sha256"] == sha256(SOURCE_RAW)
            and t204["status"]
            == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
        ),
        "validated_v127_engine_is_reused_not_old_objective": (
            v127["status"] == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and v127["failed_checks"] == []
            and sha256(ENGINE_TRAIN) == v127["input_hashes"]["train"]
            and sha256(ENGINE_LOSSES) == v127["input_hashes"]["losses"]
            and "v173_tangent"
            not in ENGINE_TRAIN.read_text(encoding="utf-8")
            and "mixed_advantages"
            in ENGINE_LOSSES.read_text(encoding="utf-8")
            and v128["decision"]["status"]
            == "REJECT_V128_NOMINAL_POLICY"
        ),
        "cost_is_dense_unscaled_squared_roll_excess": (
            "constrained_cost = jp.square(roll_risk_excess)"
            in patch_text
            and "reward_channel=unchanged" in patch_text
        ),
        "fixed_t202_reward_cost_is_disabled": (
            "not args.winner_t202_predicted_roll_risk" in patch_text
        ),
        "deployment_graph_is_unchanged": (
            "deployment_graph=unchanged" in patch_text
        ),
        "composed_manifest_and_inventory_present": (
            manifest["schema_version"]
            == "open_duck.t209_composed_source.v1"
            and bool(python_inventory)
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": file_receipt(BUILDER),
        "source_patch": file_receipt(PATCH),
        "composer": file_receipt(COMPOSER),
        "environment_worker": file_receipt(ENV_WORKER),
        "runner": file_receipt(RUNNER),
        "unit_test": file_receipt(TEST),
        "constrained_train_engine": file_receipt(ENGINE_TRAIN),
        "constrained_loss_engine": file_receipt(ENGINE_LOSSES),
    }
    assets = {
        "source_checkpoint": directory_receipt(SOURCE),
        "source_raw_onnx": file_receipt(SOURCE_RAW),
        "cpu_topology_template": directory_receipt(TOPOLOGY),
        "reference_features": file_receipt(REFERENCE),
        "hidden_gate_static_asset": file_receipt(GATE),
        "t208_selection_result": file_receipt(T208),
        "t204_source_validation": file_receipt(T204),
        "v127_engine_cpu_result": file_receipt(V127),
        "v128_old_objective_closure": file_receipt(V128),
        "composed_source_manifest": file_receipt(MANIFEST),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t209_dual_roll_cost_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T209_DUAL_ROLL_COST_CPU_CONTRACT",
        "mechanism": {
            "source": "T203_HALF",
            "risk": "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)",
            "prediction_horizon_s": 0.08,
            "passing_envelope_rad": 0.3541802655745987,
            "cost": "square(max(0, risk - envelope))",
            "cost_scale": 1.0,
            "reward_channel": "unchanged_original_clipped_reward",
            "cost_channel": "separate_unclipped_training_only",
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
            "protected": [
                "mature actor outside negative_adapter_location",
                "observation normalizer",
                "policy ABI",
                "deployment action graph",
            ],
            "scalar_sweep": False,
        },
        "training_smoke": {
            "timesteps": 1024,
            "num_envs": 8,
            "environments_per_stratum": 1,
            "source_checkpoint": str(SOURCE.resolve()),
            "export_steps": [0, 1024],
            "all_nonconstraint_PPO_values": "bit_exact_T203",
            "removed_closed_constraint_reward_terms": [
                "T202 fixed predicted-roll price",
                "legacy torque reward penalties",
            ],
        },
        "environment_contract": {
            "default_off_steps": 8,
            "enabled_source_policy_ticks": 108,
            "enabled_seed": 209,
            "synthetic_roll_rate_rad_s": 10.0,
            "metric_error_tolerance": 1.0e-7,
            "reward_must_remain_bit_equal_to_original_clip": True,
            "formal_behavior_cells": 0,
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
                "EARN_T210_DUAL_ROLL_COST_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T209_DUAL_ROLL_COST_WITHOUT_HOSTED_TRAINING"
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
        "# T209 dual roll-cost CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Source: exact T203 half checkpoint\n"
        "- Cost: unscaled squared predicted-roll excess through the "
        "validated separate cost critic and derived dual update\n"
        "- Deployment graph and reward channel: unchanged\n"
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
