#!/usr/bin/env python3
"""Freeze T119's joint soft-router/expert 1,024-step CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t119_joint_soft_router_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T119_JOINT_SOFT_ROUTER_CPU_PREREGISTRATION_20260729.md"
)
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t119-joint-soft-router-v1"
)
ASSET_RESULT = ANALYSIS / "t119_joint_soft_router_assets.json"
T118_RESULT = ANALYSIS / "t118_routing_failure_attribution_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
T97_PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
T100C_VALIDATION = ANALYSIS / "t100c_recovered_training_validation.json"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
MANIFEST = PLAYGROUND / "T119_COMPOSED_SOURCE_MANIFEST.json"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t119_joint_soft_router_cpu_contract.py",
    "test": ROOT / "tests" / "test_t119_joint_soft_router.py",
    "composer": ROOT / "tools" / "compose_t119_joint_soft_router_playground.py",
    "asset_builder": ROOT / "tools" / "build_t119_joint_soft_router_assets.py",
    "update_mask": ROOT / "patches" / "t119_joint_soft_router_updates.py",
    "t118_result": T118_RESULT,
    "asset_result": ASSET_RESULT,
    "t100c_validation": T100C_VALIDATION,
}


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
            raise FileExistsError(f"refusing to overwrite T119 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T119 preregistration requires clean worktree")

    assets = json.loads(ASSET_RESULT.read_text(encoding="utf-8"))
    t118 = json.loads(T118_RESULT.read_text(encoding="utf-8"))
    expanded = Path(assets["assets"]["expanded_checkpoint"]["path"])
    expected = Path(assets["assets"]["expected_soft_graph"]["path"])
    step_zero = Path(assets["assets"]["step_zero_graph"]["path"])
    checks = {
        "t118_selects_joint_training": (
            t118["status"] == "PASS_T118_ROUTING_FAILURE_ATTRIBUTION"
            and t118["failed_checks"] == []
            and t118["decision"]
            == "EARN_T119_JOINT_SOFT_ROUTER_EXPERT_CPU_PREREGISTRATION_ONLY"
        ),
        "zero_update_assets_pass": (
            assets["status"] == "PASS_T119_JOINT_SOFT_ROUTER_ASSETS"
            and assets["failed_checks"] == []
            and assets["checks"]["expanded_checkpoint_roundtrip_exact"]
            and assets["checks"]["step_zero_soft_formula_exact"]
            and assets["checks"]["router_deltas_exact_zero"]
        ),
        "step_zero_graph_exact": (
            expected.is_file()
            and step_zero.is_file()
            and sha256(expected) == sha256(step_zero)
        ),
        "all_assets_present": all(
            path.exists()
            for path in (
                expanded,
                expected,
                step_zero,
                REFERENCE,
                T97_PREREG,
                GATE,
                MANIFEST,
                PLAYGROUND,
                *SOURCE_FILES.values(),
            )
        ),
        "no_behavior_hosted_or_robot_execution": True,
        "no_reward_randomizer_optimizer_abi_or_runtime_change": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T119 preregistration checks failed: {failed}")

    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t119_joint_soft_router_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT",
        "question": (
            "Can the T100C-half corrective expert and a zero-delta smooth "
            "state router learn jointly while the mature gait core and "
            "observation normalizer remain bit-exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "failure": (
                "T113's eleven moving failures are backward-pitch collapses "
                "spanning both supports and at least three phase quadrants"
            ),
            "closed_routes": (
                "fixed hard routing is dynamically inconsistent; post-hoc "
                "soft routing, always-on routing, and always-on train-through "
                "are not persistent endpoint solutions"
            ),
            "distinct_mechanism": (
                "jointly optimize the continuous router and its expert "
                "through the closed loop, without changing the mature gait"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_half_expanded_with_zero_router_deltas",
            "actor_equation": (
                "anchored=mature+sigmoid((coef+delta)@standardized_h+"
                "intercept+delta)*negative_expert(h)"
            ),
            "trainable_actor_groups": [
                "negative_adapter_location",
                "soft_router_coefficient_delta",
                "soft_router_intercept_delta",
            ],
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
            "endpoint_categories": [
                "broad_random",
                "nominal",
                "torso_com_x_neg",
                "torso_com_x_pos",
                "torso_com_y_neg",
                "torso_com_y_pos",
                "torso_com_z_neg",
                "torso_com_z_pos",
            ],
            "reward_change": False,
            "randomizer_change": False,
            "optimizer_change": False,
            "command_support_change": False,
            "runtime_input_change": False,
            "policy_abi_change": False,
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
            "minimum_changed_rows_each_population": 1,
            "minimum_router_weight_delta": 1.0e-7,
            "minimum_raw_action_delta": 1.0e-7,
        },
        "sources": {
            name: file_receipt(path) for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "expanded_checkpoint": directory_receipt(expanded),
            "expected_soft_graph": file_receipt(expected),
            "step_zero_asset_graph": file_receipt(step_zero),
            "reference_features": file_receipt(REFERENCE),
            "hidden_gate_static_asset": file_receipt(GATE),
            "t97_preregistration": file_receipt(T97_PREREG),
            "composed_manifest": file_receipt(MANIFEST),
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(python_inventory),
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Exact step-zero restore/export parity; only the expert, "
                "two router deltas, and critic change; all protected actor "
                "and normalizer leaves remain bit-exact; router weight and "
                "deployed raw action change on both frozen nominal and "
                "negative-COM trace populations; exported stateful ONNX "
                "graphs retain the frozen ABI and finite CPU execution."
            ),
            "pass_decision": (
                "EARN_T120_JOINT_SOFT_ROUTER_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_JOINT_SOFT_ROUTER_TRAINTHROUGH",
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
        "\n".join(
            [
                "# T119 joint soft-router CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact T100C half plus zero router deltas",
                "- Trainable actor: negative expert plus two router deltas",
                "- Protected: mature gait actor and observation normalizer",
                "- CPU steps / behavior / hosted / robot: `1024/0/0/0`",
                "",
                "A pass earns only a separate hosted-run preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
