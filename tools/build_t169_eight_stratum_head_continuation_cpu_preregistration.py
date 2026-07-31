#!/usr/bin/env python3
"""Freeze T169's T100C-final eight-stratum head continuation CPU contract."""

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
    / "t169_eight_stratum_head_continuation_cpu_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_PREREGISTRATION_20260729.md"
)
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_original_driver_wrapper_package_v1/"
    "t100c_original_driver_wrapper_bundle/playground"
)
TRAINING_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
SOURCE = TRAINING_ROOT / "2026_07_29_024350_2007040"
SOURCE_RAW = TRAINING_ROOT / "2026_07_29_024350_2007040.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t128_negative_only_expert_cpu_v1/t100c_half_cpu_remap"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
T168 = ANALYSIS / "t168_nominal_adapter_persistence_attribution_result.json"
T100C_VALIDATION = ANALYSIS / "t100c_recovered_training_validation.json"
T100C_PREREG = ANALYSIS / "t100c_original_driver_wrapper_preregistration.json"
T97_PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
T100C_STATE = (
    Path(
        "D:/CodexArtifacts/open-duck-policy/"
        "t100c_colab_extracted_20260728/"
        "t78_endpoint_joint_adapter_continuation/run_state.json"
    )
)
MECHANISM = (
    PLAYGROUND
    / "playground/common/t98_hidden_expert_continuation.py"
)
RANDOMIZER = (
    PLAYGROUND
    / "playground/common/t66_endpoint_core_continuation.py"
)
NETWORKS = (
    PLAYGROUND
    / "playground/common/t98_hidden_expert_ppo_networks.py"
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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T169: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T169 builder requires clean worktree")
    t168 = json.loads(T168.read_text(encoding="utf-8"))
    validation = json.loads(T100C_VALIDATION.read_text(encoding="utf-8"))
    original = json.loads(T100C_PREREG.read_text(encoding="utf-8"))
    hosted = json.loads(T100C_STATE.read_text(encoding="utf-8"))
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    checks = {
        "t168_exactly_selected_existing_nominal_adapter": (
            t168["status"]
            == "PASS_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
            and t168["decision"]
            == (
                "EARN_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
            and t168["stored_trace_replay"][
                "nominal_hybrid_matches_final_rows"
            ]
            == t168["stored_trace_replay"]["rows"]
            == 8152
        ),
        "t100c_recovered_training_is_exact": (
            validation["status"]
            == "PASS_T100C_RECOVERED_TRAINING_VALIDATION"
            and validation["failed_checks"] == []
        ),
        "original_t100c_recipe_is_eight_strata_head_only": (
            original["status"]
            == "PREREGISTERED_T100C_ORIGINAL_DRIVER_WRAPPER_RECOVERY"
            and original["failed_checks"] == []
            and original["training"]["endpoint_strata"] == 8
            and original["training"]["actor_trainable_groups"]
            == ["negative_adapter_location"]
            and original["training"]["mature_actor_frozen"] is True
            and original["training"]["normalizer_frozen"] is True
        ),
        "hosted_source_contains_exact_final_checkpoint": (
            hosted["status"]
            == "PASS_T78_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and 2_007_040 in hosted["checkpoint_steps"]
            and 2_007_040 in hosted["onnx_steps"]
        ),
        "all_sources_and_assets_present": all(
            path.exists()
            for path in (
                PLAYGROUND,
                SOURCE,
                SOURCE_RAW,
                TOPOLOGY,
                REFERENCE,
                GATE,
                T168,
                T100C_VALIDATION,
                T100C_PREREG,
                T97_PREREG,
                T100C_STATE,
                MECHANISM,
                RANDOMIZER,
                NETWORKS,
            )
        ),
        "no_reward_optimizer_abi_runtime_or_curriculum_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T169 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t169_eight_stratum_head_continuation_cpu_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
        ),
        "question": (
            "Can the exact T100C-final nominal adapter continue through "
            "its unchanged eight-stratum curriculum while only that "
            "adapter and the critic update?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "static_router_closed": (
                "T167 found no defensible cross-fit static separator for "
                "Y-negative"
            ),
            "active_path_exact": (
                "T168 proved both Y-negative contexts take the nominal "
                "dynamic expert"
            ),
            "initializer_attribution_exact": (
                "T168 reproduced T164 final on all 8,152 protected rows "
                "by replacing only the nominal adapter weight and bias"
            ),
            "continuation_selection": (
                "continue the exact existing T100C-final head through "
                "the same broad/nominal/±X/±Y/±Z curriculum"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_final_checkpoint_2007040",
            "forward_path": "fixed_live_hidden_gate_plus_negative_adapter",
            "trainable_actor_groups": ["negative_adapter_location"],
            "critic_trainable": True,
            "mature_actor_frozen": True,
            "normalizer_frozen": True,
            "endpoint_names": [
                "broad_random",
                "nominal",
                "torso_com_x_neg",
                "torso_com_x_pos",
                "torso_com_y_neg",
                "torso_com_y_pos",
                "torso_com_z_neg",
                "torso_com_z_pos",
            ],
            "endpoint_offsets_m": [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [-0.05, 0.0, 0.0],
                [0.05, 0.0, 0.0],
                [0.0, -0.05, 0.0],
                [0.0, 0.05, 0.0],
                [0.0, 0.0, -0.05],
                [0.0, 0.0, 0.05],
            ],
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
            "environments_per_stratum": 1,
            "batch_size": 8,
            "exports": [0, 1024],
            "cpu_only": True,
            "formal_behavior_cells": 0,
            "all_other_ppo_values": "bit_exact_original_T100C",
        },
        "thresholds": {
            "step_zero_trace_bit_exact_rows": 72,
            "step_zero_random_chain_bit_exact_steps": 256,
            "minimum_trace_final_action_changed_fraction": 0.05,
            "minimum_random_raw_action_delta": 1.0e-6,
        },
        "sources": {
            "builder": file_receipt(Path(__file__).resolve()),
            "runner": file_receipt(
                ROOT
                / "tools/run_t169_eight_stratum_head_continuation_cpu_contract.py"
            ),
            "test": file_receipt(
                ROOT
                / "tests/test_t169_eight_stratum_head_continuation_cpu.py"
            ),
            "mechanism": file_receipt(MECHANISM),
            "randomizer": file_receipt(RANDOMIZER),
            "networks": file_receipt(NETWORKS),
            "t168_selection": file_receipt(T168),
            "t100c_validation": file_receipt(T100C_VALIDATION),
            "t100c_preregistration": file_receipt(T100C_PREREG),
            "t100c_hosted_state": file_receipt(T100C_STATE),
        },
        "assets": {
            "source_checkpoint": directory_receipt(SOURCE),
            "source_raw_onnx": file_receipt(SOURCE_RAW),
            "cpu_topology_template": directory_receipt(TOPOLOGY),
            "reference_features": file_receipt(REFERENCE),
            "hidden_gate_static_asset": file_receipt(GATE),
            "trace_population": file_receipt(T97_PREREG),
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(python_inventory),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "step zero restores/exports exact T100C final; all eight "
                "strata read back exactly; only negative_adapter_location "
                "and critic change; normalizer and mature actor remain "
                "bit-exact; updated actions are causally bound; both ONNX "
                "exports preserve the 115/14/64 stateful ABI"
            ),
            "pass_decision": (
                "EARN_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_EIGHT_STRATUM_NOMINAL_HEAD_CONTINUATION"
            ),
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
        "# T169 eight-stratum head continuation CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T100C final checkpoint\n"
        "- Population: broad, nominal, and all six ±0.05 m COM endpoints\n"
        "- Trainable actor: existing nominal adapter weight/bias only\n"
        "- CPU steps / behavior / hosted / robot: `1024 / 0 / 0 / 0`\n\n"
        "A pass earns only a separate hosted-run preregistration.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
