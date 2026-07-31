#!/usr/bin/env python3
"""Freeze the T98 hidden-gated negative-COM expert CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t98_hidden_expert_cpu_preregistration.json"
MARKDOWN = ANALYSIS / "T98_HIDDEN_EXPERT_CPU_PREREGISTRATION_20260728.md"
PLAYGROUND = Path("D:/CodexProjects/Open_Duck_Playground-t98-hidden-expert-v1")
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/t78_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_28_183936_2007040"
)
SOURCE_RAW = SOURCE.parent / "2026_07_28_183936_2007040.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t77_endpoint_joint_adapter_cpu_v1/smoke/"
    "2026_07_28_140308_1024"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
T97_PREREG = ANALYSIS / "t97_hidden_gate_preregistration.json"
T97_RESULT = ANALYSIS / "t97_hidden_gate_result.json"
T78_VALIDATION = ANALYSIS / "t78_recovered_training_validation.json"
T93_RESULT = ANALYSIS / "t93_adapter_authority_result.json"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT / "tools" / "run_t98_hidden_expert_cpu_contract.py",
    "gate_builder": ROOT / "tools" / "build_t98_hidden_gate_asset.py",
    "mechanism_test": ROOT / "tests" / "test_t98_hidden_expert_mechanism.py",
    "gate_test": ROOT / "tests" / "test_t98_hidden_gate_asset.py",
    "t97_preregistration": T97_PREREG,
    "t97_result": T97_RESULT,
    "t78_validation": T78_VALIDATION,
    "t93_result": T93_RESULT,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            raise FileExistsError(f"refusing to overwrite T98 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T98 preregistration requires a clean worktree")

    t97 = json.loads(T97_RESULT.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    t78 = json.loads(T78_VALIDATION.read_text(encoding="utf-8"))
    t93 = json.loads(T93_RESULT.read_text(encoding="utf-8"))
    checks = {
        "t97_gate_falsifier_passed": (
            t97["status"] == "PASS_T97_HIDDEN_GATE_FALSIFIER"
            and t97["decision"]
            == "EARN_T98_HIDDEN_GATED_EXPERT_CPU_CONTRACT_PREREGISTRATION_ONLY"
        ),
        "gate_asset_frozen_exact": (
            gate["status"] == "FROZEN_T98_HIDDEN_GATE_ASSET"
            and gate["failed_checks"] == []
            and gate["asset_sha256"]
            == canonical_sha256(
                {
                    key: item
                    for key, item in gate.items()
                    if key != "asset_sha256"
                }
            )
            and gate["training_population"]["metrics"][
                "balanced_accuracy"
            ]
            == 1.0
        ),
        "t78_final_source_validated": (
            t78["status"] == "PASS_T78_RECOVERED_TRAINING_VALIDATION"
            and t78["failed_checks"] == []
            and any(
                item["step"] == 2_007_040
                and Path(item["path"]).resolve() == SOURCE.resolve()
                for item in t78["exports"]["checkpoints"]
            )
        ),
        "t93_shared_adapter_has_material_authority": (
            t93["status"] == "PASS_T93_ADAPTER_AUTHORITY_AUDIT"
            and t93["classification"]
            == "NO_HARD_ADAPTER_AUTHORITY_LIMIT_FOUND"
            and t93["decision"] == "CLOSE_ADAPTER_AUTHORITY_HYPOTHESIS"
        ),
        "source_assets_present": all(
            path.exists()
            for path in (SOURCE, SOURCE_RAW, TOPOLOGY, REFERENCE, PLAYGROUND)
        ),
        "mechanism_is_live_hidden_not_calibration_context": (
            gate["constraints"]["new_policy_input"] is False
            and gate["constraints"]["new_runtime_sensor"] is False
            and gate["constraints"]["manual_measurement"] is False
            and gate["constraints"]["policy_abi_change"] is False
        ),
        "no_scalar_reward_optimizer_or_runtime_change": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T98 preregistration checks failed: {failed}")

    python_inventory = {
        path.relative_to(PLAYGROUND).as_posix(): sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    value: dict[str, Any] = {
        "schema_version": "open_duck.t98_hidden_expert_cpu_preregistration.v1",
        "status": "PREREGISTERED_T98_HIDDEN_EXPERT_CPU_CONTRACT",
        "question": (
            "Can a fixed classifier of the mature recurrent hidden state "
            "route a zero-initialized negative-COM correction head, preserve "
            "T78-final exactly on the nominal branch, and acquire material "
            "causal action authority in one CPU smoke?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "t71": (
                "the mature recurrent state contains and causally uses COM "
                "information"
            ),
            "t76": (
                "the COM displacement is not stable rank-one, closing a "
                "single fixed head transform"
            ),
            "t78": (
                "a single co-adapted recurrent adapter retained nominal "
                "behavior but did not close the endpoint family"
            ),
            "t93": (
                "the adapter output head has full-rank material action "
                "authority"
            ),
            "t95_t96": (
                "reset-calibration routing and FiLM conditioning produced "
                "negligible action binding and are closed"
            ),
            "t97": (
                "a deployable linear gate on h_out generalizes across "
                "checkpoint, fit, command, and exact groups, with perfect "
                "tick-8 recall and specificity"
            ),
        },
        "mechanism": {
            "source": "exact_T78_final_checkpoint",
            "gate": (
                "fixed standardized linear ridge on current h_out; "
                "negative_com iff score >= 0"
            ),
            "actor_equation": (
                "anchored = T78_anchored + where(gate, "
                "negative_adapter_location(h_out), 0)"
            ),
            "new_head_initialization": "kernel_and_bias_exact_zero",
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
            "optimizer_change": "exact_parameter_update_mask_only",
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
            "step_zero_t97_trace_bit_exact_rows": 72,
            "step_zero_random_chain_bit_exact_steps": 256,
            "final_nominal_bit_exact_rows": 36,
            "minimum_negative_raw_action_changed_fraction": 0.5,
            "minimum_negative_final_action_changed_fraction": 0.1,
            "minimum_maximum_negative_raw_action_delta": 1.0e-5,
        },
        "sources": {
            name: file_receipt(path) for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "source_checkpoint": directory_receipt(SOURCE),
            "source_raw_onnx": file_receipt(SOURCE_RAW),
            "topology_template": directory_receipt(TOPOLOGY),
            "reference_features": file_receipt(REFERENCE),
            "hidden_gate": file_receipt(GATE),
            "t97_preregistration": file_receipt(T97_PREREG),
        },
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(python_inventory),
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Materialized T78 source is exact apart from a zero head; "
                "step-zero T97 rows and 256-step stateful chain are bit-exact; "
                "only the negative head and critic change; normalizer and "
                "mature actor remain bit-exact; all nominal gated rows stay "
                "bit-exact; at least 50% of negative rows change raw action, "
                "at least 10% change deployed action, and maximum raw action "
                "change reaches 1e-5."
            ),
            "pass_decision": (
                "EARN_T99_HIDDEN_EXPERT_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T98_HIDDEN_EXPERT_MECHANISM",
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
                "# T98 hidden-gated expert CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact T78 final checkpoint",
                "- Gate: fixed T97 live-hidden linear classifier",
                "- New actor state: one zero-initialized 64×14 correction head",
                "- Trainable: correction head and critic only",
                "- Mature actor / normalizer: bit-exact frozen",
                "- Reward / optimizer / ABI / runtime-input changes: `0/0/0/0`",
                "- CPU steps / behavior / hosted / robot now: `1024/0/0/0`",
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
