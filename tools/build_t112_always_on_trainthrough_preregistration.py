#!/usr/bin/env python3
"""Freeze T112's always-on hidden-expert train-through CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t112_always_on_trainthrough_preregistration.json"
MARKDOWN = ANALYSIS / "T112_ALWAYS_ON_TRAINTHROUGH_PREREGISTRATION_20260729.md"
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t112-always-on-expert-v1"
)
TRAINING_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
SOURCE = TRAINING_ROOT / "2026_07_29_023820_1003520"
SOURCE_RAW = TRAINING_ROOT / "2026_07_29_023820_1003520.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t98_hidden_expert_cpu_v1/smoke/2026_07_28_214028_1024"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
T97_PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
T100C_VALIDATION = ANALYSIS / "t100c_recovered_training_validation.json"
T104_RESULT = ANALYSIS / "t104_t100c_gate_dynamics_result.json"
T110_RESULT = ANALYSIS / "t110_always_on_nominal_result.json"
T111_RESULT = ANALYSIS / "t111_always_on_negative_endpoint_result.json"
PATCH_NETWORKS = ROOT / "patches" / "t112_always_on_hidden_expert_ppo_networks.py"
PATCH_RUNNER = ROOT / "patches" / "t112_open_duck_mini_v2_runner.py"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t112_always_on_trainthrough_cpu_contract.py",
    "test": ROOT / "tests" / "test_t112_always_on_trainthrough.py",
    "patched_networks": PATCH_NETWORKS,
    "patched_runner": PATCH_RUNNER,
    "t100c_validation": T100C_VALIDATION,
    "t104_gate_dynamics": T104_RESULT,
    "t110_nominal": T110_RESULT,
    "t111_negative_endpoint": T111_RESULT,
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
        if not item.is_file():
            continue
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
            raise FileExistsError(f"refusing to overwrite T112 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T112 preregistration requires a clean worktree")

    t100c = json.loads(T100C_VALIDATION.read_text(encoding="utf-8"))
    t104 = json.loads(T104_RESULT.read_text(encoding="utf-8"))
    t110 = json.loads(T110_RESULT.read_text(encoding="utf-8"))
    t111 = json.loads(T111_RESULT.read_text(encoding="utf-8"))
    source_export = next(
        item
        for item in t100c["exports"]["checkpoints"]
        if item["step"] == 1_003_520
    )
    checks = {
        "t100c_half_source_validated": (
            t100c["status"] == "PASS_T100C_RECOVERED_TRAINING_VALIDATION"
            and t100c["failed_checks"] == []
            and Path(source_export["path"]).resolve() == SOURCE.resolve()
            and source_export["directory_sha256"] == directory_sha256(SOURCE)
        ),
        "hard_gate_dynamics_closed": (
            t104["status"] == "PASS_T104_T100C_GATE_DYNAMICS_AUDIT"
            and t104["classification"] == "HARD_GATE_DYNAMICS_INCONSISTENT"
            and t104["decision_inputs"][
                "nominal_false_active_fraction_post_warmup"
            ]
            > 0.20
            and t104["decision_inputs"][
                "negative_com_false_inactive_fraction_post_warmup"
            ]
            > 0.20
        ),
        "always_on_half_retains_nominal": (
            t110["status"] == "PASS_T110_ALWAYS_ON_NOMINAL_MATRIX"
            and t110["condition"]["green_cells"] == 16
        ),
        "posthoc_always_on_is_not_persistent": (
            t111["status"] == "HOLD_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
            and t111["condition"]["green_cells"] == 6
            and t111["decision"] == "CLOSE_T100C_ALWAYS_ON_EXPERT"
        ),
        "assets_present": all(
            path.exists()
            for path in (
                SOURCE,
                SOURCE_RAW,
                TOPOLOGY,
                REFERENCE,
                GATE,
                T97_PREREG,
                PLAYGROUND,
                *SOURCE_FILES.values(),
            )
        ),
        "composed_networks_match_frozen_patch": (
            sha256(
                PLAYGROUND
                / "playground/common/t98_hidden_expert_ppo_networks.py"
            )
            == sha256(PATCH_NETWORKS)
        ),
        "composed_runner_matches_frozen_patch": (
            sha256(PLAYGROUND / "playground/open_duck_mini_v2/runner.py")
            == sha256(PATCH_RUNNER)
        ),
        "no_reward_scalar_randomizer_abi_or_runtime_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T112 preregistration checks failed: {failed}")

    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    value: dict[str, Any] = {
        "schema_version": "open_duck.t112_always_on_trainthrough_preregistration.v1",
        "status": "PREREGISTERED_T112_ALWAYS_ON_TRAINTHROUGH_CPU_CONTRACT",
        "question": (
            "Can the useful T100C-half negative-COM residual become one "
            "persistent universal correction when it is applied and trained "
            "on every tick of the unchanged eight endpoint strata?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "t104": (
                "the hard hidden gate is dynamically inconsistent: both "
                "nominal false-active and negative-COM false-inactive rates "
                "exceed 20 percent"
            ),
            "t106_t108": (
                "continuous sigmoid routing retained nominal behavior but "
                "failed the exact negative-COM endpoint at 4/16"
            ),
            "t109_t111": (
                "the exact always-on half checkpoint retained 16/16 nominal "
                "cells and repaired some endpoint cells, but the final "
                "checkpoint drifted and the pair reached only 6/16"
            ),
            "selection": (
                "remove routing from both forward action and gradient flow; "
                "train the existing residual universally rather than tune "
                "another gate or scalar"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_half_checkpoint",
            "actor_equation": (
                "anchored = mature_anchored + negative_adapter_location(h_out)"
            ),
            "gate_action_path": "none_always_on",
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
            "minimum_trace_raw_action_changed_fraction": 0.5,
            "minimum_trace_final_action_changed_fraction": 0.1,
            "minimum_random_raw_action_delta": 1.0e-6,
        },
        "sources": {
            name: file_receipt(path) for name, path in SOURCE_FILES.items()
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
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "The CPU-remapped T100C-half tree is exact; step-zero export "
                "matches the exact always-on transform on 72 trace rows and "
                "a 256-step stateful chain; only negative_adapter_location "
                "and critic leaves change; normalizer and every mature actor "
                "leaf remain bit-exact; the updated expert changes deployed "
                "actions materially; ONNX ABI and recurrent execution remain "
                "finite."
            ),
            "pass_decision": (
                "EARN_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_ALWAYS_ON_TRAINTHROUGH_MECHANISM",
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
                "# T112 always-on train-through CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact T100C half checkpoint",
                "- Forward path: existing negative expert always on",
                "- Trainable: negative expert and critic only",
                "- Strata: unchanged broad + nominal + six COM endpoints",
                "- Reward / randomizer / optimizer / ABI changes: `0/0/0/0`",
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
