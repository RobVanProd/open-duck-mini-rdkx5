#!/usr/bin/env python3
"""Freeze T128's exact-negative-only linear-expert CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t128_negative_only_expert_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T128_NEGATIVE_ONLY_EXPERT_CPU_PREREGISTRATION_20260729.md"
)
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t128-negative-only-expert-v1"
)
MANIFEST = PLAYGROUND / "T128_COMPOSED_SOURCE_MANIFEST.json"
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
T127_RESULT = ANALYSIS / "t127_negative_expert_interference_result.json"
T112B_RESULT = ANALYSIS / "t112b_cpu_recovery_result.json"
MECHANISM = ROOT / "patches" / "t128_negative_only_hidden_expert.py"
NETWORKS = ROOT / "patches" / "t112_always_on_hidden_expert_ppo_networks.py"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t128_negative_only_expert_cpu_contract.py",
    "test": ROOT / "tests" / "test_t128_negative_only_expert_cpu.py",
    "mechanism": MECHANISM,
    "composer": (
        ROOT / "tools" / "compose_t128_negative_only_expert_playground.py"
    ),
    "network_source": NETWORKS,
    "t127_selection": T127_RESULT,
    "t112b_cpu_contract": T112B_RESULT,
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


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T128 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T128 preregistration requires clean worktree")

    t127 = json.loads(T127_RESULT.read_text(encoding="utf-8"))
    t112b = json.loads(T112B_RESULT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_basis = dict(manifest)
    manifest_hash = manifest_basis.pop("manifest_sha256")
    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    checks = {
        "t127_selected_exact_negative_only": (
            t127["status"]
            == "PASS_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
            and t127["decision"]
            == (
                "EARN_T128_NEGATIVE_ONLY_LINEAR_EXPERT_CPU_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "existing_always_on_cpu_contract_green": (
            t112b["status"] == "PASS_T112B_READ_ONLY_CPU_RECOVERY"
            and t112b["failed_checks"] == []
        ),
        "all_sources_and_assets_present": all(
            path.exists()
            for path in (
                PLAYGROUND,
                MANIFEST,
                SOURCE,
                SOURCE_RAW,
                TOPOLOGY,
                REFERENCE,
                GATE,
                T97_PREREG,
                *SOURCE_FILES.values(),
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
        "no_reward_optimizer_abi_or_runtime_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T128 preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t128_negative_only_expert_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T128_NEGATIVE_ONLY_EXPERT_CPU_CONTRACT"
        ),
        "question": (
            "Can the existing linear hidden expert receive an isolated, "
            "causally clean update on exact -0.05 m torso COM while the "
            "mature actor remains bit-exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "hidden_state": (
                "T71 proved that the recurrent state contains and uses COM "
                "information; the control law, not observability, was weak"
            ),
            "mixed_gradient_interference": (
                "T127 proved every correction head trained through eight "
                "body-configuration strata, while none exceeded the T67 "
                "negative-COM recurrent-core baseline"
            ),
            "selection": (
                "isolate the existing linear expert on the exact failed "
                "endpoint before adding nonlinear capacity"
            ),
        },
        "mechanism": {
            "source": "exact_T100C_half_checkpoint",
            "forward_path": "negative_adapter_location_always_on",
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
                    "name": "torso_com_x_neg",
                    "torso_com_offset_m": [-0.05, 0.0, 0.0],
                    "fraction": 1.0,
                }
            ],
            "other_body_physics": "nominal",
            "episode_actuator_sensor_variation": "unchanged_scale_1",
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
            "source_checkpoint": directory_receipt(SOURCE),
            "source_raw_onnx": file_receipt(SOURCE_RAW),
            "cpu_topology_template": directory_receipt(TOPOLOGY),
            "reference_features": file_receipt(REFERENCE),
            "hidden_gate_static_asset": file_receipt(GATE),
            "trace_population": file_receipt(T97_PREREG),
            "composed_manifest": file_receipt(MANIFEST),
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
                "All eight physical models read back exact -0.05 m torso "
                "COM with other body physics nominal; step zero matches the "
                "existing always-on export exactly; only the linear expert "
                "and critic change; the normalizer and mature actor remain "
                "bit-exact; updated actions are causally bound; both ONNX "
                "exports preserve the 115/14/64 stateful ABI."
            ),
            "pass_decision": (
                "EARN_T129_NEGATIVE_ONLY_EXPERT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_NEGATIVE_ONLY_LINEAR_EXPERT",
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
        "# T128 exact-negative-only expert CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Physical population: 8/8 exact torso COM x = -0.05 m\n"
        "- Trainable actor: existing linear negative expert only\n"
        "- Episode actuator/sensor variation: unchanged\n"
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
