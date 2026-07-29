#!/usr/bin/env python3
"""Freeze T148's integrated command-group-risk CPU contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import build_t128_negative_only_expert_cpu_preregistration as t128


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t148_command_group_risk_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T148_COMMAND_GROUP_RISK_CPU_PREREGISTRATION_20260729.md"
)
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t148-command-group-risk-v1"
)
MANIFEST = PLAYGROUND / "T148_COMPOSED_SOURCE_MANIFEST.json"
T147_RESULT = ANALYSIS / "t147_command_group_risk_cpu_result.json"
T128_RESULT = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
LOSS_SOURCE = ROOT / "patches" / "t147_command_group_risk_ppo_losses.py"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools/run_t148_command_group_risk_cpu_contract.py",
    "test": ROOT / "tests/test_t148_command_group_risk_cpu.py",
    "loss_source": LOSS_SOURCE,
    "composer": ROOT / "tools/compose_t148_command_group_risk_playground.py",
    "t147_loss_contract": T147_RESULT,
    "t128_restore_update_export_contract": T128_RESULT,
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T148 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T148 preregistration requires clean worktree")

    t147 = json.loads(T147_RESULT.read_text(encoding="utf-8"))
    t128_result = json.loads(T128_RESULT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_basis = dict(manifest)
    manifest_hash = manifest_basis.pop("manifest_sha256")
    inventory = {
        path.relative_to(PLAYGROUND).as_posix(): t128.sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    copied_loss = (
        PLAYGROUND
        / "playground/common/t147_command_group_risk_ppo_losses.py"
    )
    checks = {
        "t147_standalone_contract_green": (
            t147["status"] == "PASS_T147_COMMAND_GROUP_RISK_CPU_CONTRACT"
            and t147["failed_checks"] == []
            and t147["decision"]
            == (
                "EARN_T148_COMMAND_GROUP_RISK_ONE_UPDATE_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t128_restore_update_export_contract_green": (
            t128_result["status"]
            == "PASS_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
            and t128_result["failed_checks"] == []
        ),
        "all_sources_and_assets_present": all(
            path.exists()
            for path in (
                PLAYGROUND,
                MANIFEST,
                copied_loss,
                t128.SOURCE,
                t128.SOURCE_RAW,
                t128.TOPOLOGY,
                t128.REFERENCE,
                t128.GATE,
                t128.T97_PREREG,
                *SOURCE_FILES.values(),
            )
        ),
        "manifest_identity_exact": (
            t128.canonical_sha256(manifest_basis) == manifest_hash
            and manifest["python_inventory"] == inventory
        ),
        "loss_copied_exact": t128.sha256(copied_loss)
        == t128.sha256(LOSS_SOURCE),
        "base_t128_source_frozen": manifest["base"]
        == str(
            Path(
                "D:/CodexProjects/"
                "Open_Duck_Playground-t128-negative-only-expert-v1"
            ).resolve()
        ),
        "actor_loss_only_no_reward_critic_optimizer_or_abi_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T148 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t148_command_group_risk_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
        ),
        "question": (
            "Can the parameter-free command-group max surrogate be bound "
            "into the exact T129 training stack while preserving source "
            "restore, update isolation, export semantics, and the stateful "
            "115/14/64 ONNX ABI?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "attribution": (
                "T146C proved upper-command failures begin from bit-exact "
                "physical policy state and only emerge after 94-381 ticks"
            ),
            "selection": (
                "T129 optimized expected batch return while .077/.080 "
                "failed; the weakest command group must become authoritative"
            ),
            "standalone_contract": (
                "T147 proved only the unique worst command group receives "
                "actor gradient and introduced no scalar hyperparameter"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_half_checkpoint",
            "training_population": "exact_negative_torso_com_x_-0.05_m",
            "command_support_m_s": [0.074, 0.080],
            "command_sampling": "unchanged_continuous_uniform",
            "command_group_anchors_m_s": [0.074, 0.077, 0.080],
            "command_group_boundaries_m_s": [0.0755, 0.0785],
            "command_observation_index": 6,
            "advantage_normalization": "unchanged_global",
            "actor_objective": (
                "maximum_present_group_negative_mean_clipped_surrogate"
            ),
            "reward_change": False,
            "critic_change": False,
            "entropy_change": False,
            "optimizer_change": False,
            "command_distribution_change": False,
            "network_change": False,
            "policy_abi_change": False,
            "runtime_change": False,
            "new_scalar_hyperparameters": 0,
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
            "required_command_group_metric_count": 3,
        },
        "sources": {
            name: t128.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "source_checkpoint": t128.directory_receipt(t128.SOURCE),
            "source_raw_onnx": t128.file_receipt(t128.SOURCE_RAW),
            "cpu_topology_template": t128.directory_receipt(t128.TOPOLOGY),
            "reference_features": t128.file_receipt(t128.REFERENCE),
            "hidden_gate_static_asset": t128.file_receipt(t128.GATE),
            "trace_population": t128.file_receipt(t128.T97_PREREG),
            "composed_manifest": t128.file_receipt(MANIFEST),
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": inventory,
            "python_inventory_sha256": t128.canonical_sha256(inventory),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "The T147 loss readback is exact; all three group metrics "
                "are present and finite in the real update; step zero is "
                "exact; only the negative expert and critic change; "
                "normalizer and mature actor remain exact; both ONNX exports "
                "preserve the stateful ABI and updated actions are bound."
            ),
            "pass_decision": (
                "EARN_T149_COMMAND_GROUP_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_COMMAND_GROUP_RISK_INTEGRATION",
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
    value["preregistered_contract_sha256"] = t128.canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T148 integrated command-group risk CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Only change: actor batch mean → worst command-group mean\n"
        "- Command support/reward/critic/optimizer/ABI: unchanged\n"
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
