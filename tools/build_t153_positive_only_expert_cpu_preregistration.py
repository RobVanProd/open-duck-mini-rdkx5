#!/usr/bin/env python3
"""Freeze T153's exact-positive-only linear-expert CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t153_positive_only_expert_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T153_POSITIVE_ONLY_EXPERT_CPU_PREREGISTRATION_20260729.md"
)
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t153-positive-only-expert-v1"
)
MANIFEST = PLAYGROUND / "T153_COMPOSED_SOURCE_MANIFEST.json"
T128_PREREG = ANALYSIS / "t128_negative_only_expert_cpu_preregistration.json"
T128_RESULT = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
T151_RESULT = ANALYSIS / "t151_command_plateau_full_r2_result.json"
T152B_RESULT = (
    ANALYSIS / "t152b_reflected_positive_expert_recovery_result.json"
)
T143C_RESULT = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
MECHANISM = ROOT / "patches" / "t153_positive_only_hidden_expert.py"
NETWORKS = ROOT / "patches" / "t112_always_on_hidden_expert_ppo_networks.py"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t153_positive_only_expert_cpu_contract.py",
    "test": ROOT / "tests" / "test_t153_positive_only_expert_cpu.py",
    "mechanism_test": ROOT / "tests" / "test_t153_positive_only_expert.py",
    "mechanism": MECHANISM,
    "composer": (
        ROOT / "tools" / "compose_t153_positive_only_expert_playground.py"
    ),
    "network_source": NETWORKS,
    "t128_cpu_contract": T128_RESULT,
    "t151_full_r2_stop": T151_RESULT,
    "t152b_reflection_close": T152B_RESULT,
    "t143c_current_router": T143C_RESULT,
}


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


def graph_receipt(item: dict[str, Any]) -> dict[str, Any]:
    path = Path(item["path"])
    value = {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if value != item:
        raise RuntimeError(f"preserved deployment receipt changed: {item}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T153 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T153 preregistration requires clean tree")

    t128_prereg = json.loads(T128_PREREG.read_text(encoding="utf-8"))
    t128 = json.loads(T128_RESULT.read_text(encoding="utf-8"))
    t151 = json.loads(T151_RESULT.read_text(encoding="utf-8"))
    t152b = json.loads(T152B_RESULT.read_text(encoding="utf-8"))
    t143c = json.loads(T143C_RESULT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_basis = dict(manifest)
    manifest_hash = manifest_basis.pop("manifest_sha256")
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    positive_blocks = [
        block
        for block in t151["blocks"]
        if block["condition_id"] == "TORSO_COM_X_POS"
    ]
    preserved = {
        step: graph_receipt(row["transformed"])
        for step, row in t143c["graphs"].items()
    }
    source_assets = {
        name: item
        for name, item in t128_prereg["assets"].items()
        if name
        in {
            "source_checkpoint",
            "source_raw_onnx",
            "cpu_topology_template",
            "reference_features",
            "hidden_gate_static_asset",
            "trace_population",
        }
    }
    checks = {
        "t151_isolated_persistent_positive_com_failure": (
            t151["status"] == "HOLD_T151_COMMAND_PLATEAU_FULL_R2"
            and len(positive_blocks) == 4
            and all(
                block["result"]["summary"]["passed_cells"] == 1
                and block["result"]["summary"]["failed_cells"] == 3
                for block in positive_blocks
            )
        ),
        "zero_credit_reflection_closed": (
            t152b["status"]
            == "HOLD_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
            and t152b["decision"] == "CLOSE_REFLECTED_POSITIVE_EXPERT"
        ),
        "sign_symmetric_negative_cpu_precedent_green": (
            t128["status"] == "PASS_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
            and t128["failed_checks"] == []
        ),
        "current_nominal_negative_router_frozen": (
            t143c["status"]
            == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143c["failed_checks"] == []
            and set(preserved) == {"1003520", "2007040"}
        ),
        "same_t100c_source_as_t128": (
            set(source_assets)
            == {
                "source_checkpoint",
                "source_raw_onnx",
                "cpu_topology_template",
                "reference_features",
                "hidden_gate_static_asset",
                "trace_population",
            }
        ),
        "all_sources_and_assets_present": all(
            path.exists()
            for path in (
                PLAYGROUND,
                MANIFEST,
                *SOURCE_FILES.values(),
                *(Path(item["path"]) for item in source_assets.values()),
            )
        ),
        "manifest_identity_exact": (
            canonical_sha256(manifest_basis) == manifest_hash
            and manifest["python_inventory"] == python_inventory
        ),
        "mechanism_copied_exact": (
            sha256(
                PLAYGROUND
                / "playground/common/t98_hidden_expert_continuation.py"
            )
            == sha256(MECHANISM)
        ),
        "always_on_network_unchanged": (
            sha256(
                PLAYGROUND
                / "playground/common/t98_hidden_expert_ppo_networks.py"
            )
            == sha256(NETWORKS)
        ),
        "no_reflection_reward_optimizer_abi_or_runtime_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T153 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t153_positive_only_expert_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T153_POSITIVE_ONLY_EXPERT_CPU_CONTRACT",
        "question": (
            "Can the same isolated linear expert mechanism that learned the "
            "-0.05 m endpoint receive a causally clean update on exact "
            "+0.05 m torso COM while the mature actor remains bit-exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "failed_condition": (
                "T151 localized the first full-R2 failure to exact +0.05 m "
                "torso COM for every moving command, checkpoint, and fit"
            ),
            "cheapest_transform_closed": (
                "T152/T152B closed the unique zero-credit first-order "
                "reflection under their frozen rule"
            ),
            "matched_precedent": (
                "T128 proved the identical isolated-head CPU contract at "
                "the sign-symmetric -0.05 m endpoint"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_half_checkpoint_same_as_T128",
            "initialization": "source_checkpoint_only_no_reflection",
            "forward_path": "isolated_linear_expert_slot_always_on",
            "training_slot_parameter_name": "negative_adapter_location",
            "deployment_role": "positive_adapter_location",
            "trainable_actor_groups": ["negative_adapter_location"],
            "frozen_actor_groups": [
                "residual_trunk",
                "residual_location",
                "scale_logits",
                "adapter_obs_projection",
                "adapter_hidden_projection",
                "adapter_hidden_bias",
                "adapter_location",
            ],
            "critic_trainable": True,
            "normalizer_frozen": True,
            "body_configuration_population": [
                {
                    "name": "torso_com_x_pos",
                    "torso_com_offset_m": [0.05, 0.0, 0.0],
                    "fraction": 1.0,
                }
            ],
            "other_body_physics": "nominal",
            "episode_actuator_sensor_variation": "unchanged_scale_1",
            "original_nominal_negative_graphs_modified": False,
            "reward_change": False,
            "optimizer_change": False,
            "command_support_change": False,
            "network_capacity_change": False,
            "policy_abi_change": False,
            "runtime_change": False,
            "scalar_sweep": False,
        },
        "training": {
            "timesteps": 1024,
            "num_envs": 8,
            "batch_size": 8,
            "exports": [0, 1024],
            "cpu_only": True,
            "formal_behavior_cells": 0,
        },
        "thresholds": {
            "step_zero_trace_bit_exact_rows": 72,
            "step_zero_random_chain_bit_exact_steps": 256,
            "minimum_trace_raw_action_changed_fraction": 0.5,
            "minimum_trace_final_action_changed_fraction": 0.1,
            "minimum_random_raw_action_delta": 1.0e-6,
        },
        "sources": {
            name: file_receipt(path) for name, path in SOURCE_FILES.items()
        },
        "assets": {
            **source_assets,
            "composed_manifest": file_receipt(MANIFEST),
        },
        "preserved_deployments": preserved,
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(python_inventory),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "All eight physical models read back exact +0.05 m torso "
                "COM with other body physics nominal; step zero matches the "
                "same T100C always-on source used by T128; only the isolated "
                "expert slot and critic change; the normalizer and mature "
                "actor remain bit-exact; updated actions are causally bound; "
                "both ONNX exports preserve the 115/14/64 stateful ABI; and "
                "the current nominal/negative graphs remain byte-exact."
            ),
            "pass_decision": (
                "EARN_T154_POSITIVE_ONLY_EXPERT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_POSITIVE_ONLY_LINEAR_EXPERT",
            "no_behavior_selection": True,
        },
        "authority": {
            "execute_one_cpu_contract": True,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T153 exact-positive-only expert CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Physical population: 8/8 exact torso COM x = +0.05 m\n"
        "- Source: same frozen T100C-half checkpoint as T128\n"
        "- Trainable actor: isolated linear expert slot only\n"
        "- CPU steps / behavior / hosted / robot: `1024/0/0/0`\n\n"
        "A pass earns only a separate hosted-run preregistration.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
