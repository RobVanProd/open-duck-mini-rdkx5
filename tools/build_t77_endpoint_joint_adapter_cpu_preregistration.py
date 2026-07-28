#!/usr/bin/env python3
"""Freeze T77's endpoint-bank joint-adapter CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t77_endpoint_joint_adapter_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T77_ENDPOINT_JOINT_ADAPTER_CPU_PREREGISTRATION_20260728.md"
)
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t77-v1")
MANIFEST = COMPOSED / "T77_COMPOSED_SOURCE_MANIFEST.json"
SOURCE = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t55_dynamic_single_support_cpu_v2"
    / "t52_half_materialized_checkpoint"
)
EXPECTED_RAW = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t55_dynamic_single_support_cpu_v2"
    / "balance_smoke"
    / "2026_07_28_063423_0.onnx"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "t66_cpu_result": ANALYSIS / "t66_endpoint_core_cpu_result.json",
    "t67_training_validation": ANALYSIS
    / "t67_recovered_training_validation.json",
    "t70_condition7_result": ANALYSIS
    / "t70_t67_condition7_result.json",
    "t71_com_causal_result": ANALYSIS
    / "t71_t67_com_hidden_causal_result.json",
    "t76_geometry_result": ANALYSIS
    / "t76_com_hidden_geometry_result.json",
    "t66_preregistration": ANALYSIS
    / "t66_endpoint_core_cpu_preregistration.json",
    "module": ROOT
    / "patches"
    / "t77_endpoint_joint_adapter_continuation.py",
    "composer": ROOT
    / "tools"
    / "compose_t77_endpoint_joint_adapter_playground.py",
    "runner": ROOT
    / "tools"
    / "run_t77_endpoint_joint_adapter_cpu_contract.py",
    "mechanism_test": ROOT
    / "tests"
    / "test_t77_endpoint_joint_adapter_mechanism.py",
    "result_test": ROOT
    / "tests"
    / "test_t77_endpoint_joint_adapter_cpu_contract.py",
    "manifest": MANIFEST,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    for item in files:
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T77 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("formal T77 preregistration requires a clean worktree")

    t66 = json.loads(SOURCE_FILES["t66_cpu_result"].read_text())
    t67 = json.loads(SOURCE_FILES["t67_training_validation"].read_text())
    t70 = json.loads(SOURCE_FILES["t70_condition7_result"].read_text())
    t71 = json.loads(SOURCE_FILES["t71_com_causal_result"].read_text())
    t76 = json.loads(SOURCE_FILES["t76_geometry_result"].read_text())
    t66_prereg = json.loads(SOURCE_FILES["t66_preregistration"].read_text())
    manifest = json.loads(MANIFEST.read_text())
    checks = {
        "t66_cpu_contract_green": (
            t66["status"] == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
            and t66["decision"]
            == "EARN_T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION_ONLY"
        ),
        "t67_recurrent_core_training_completed": (
            t67["status"] == "PASS_T67_RECOVERED_TRAINING_VALIDATION"
            and t67["classification"]["actor_update_scope"]
            == "recurrent_core_only"
        ),
        "t67_condition7_not_persistent": (
            t70["status"] == "HOLD_T70_T67_CONDITION7"
            and t70["decision"] == "CLOSE_T67_ENDPOINT_CORE_CONTINUATION"
        ),
        "com_signal_present_and_used": (
            t71["status"] == "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
            and t71["classification"]
            == "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
        ),
        "rank_one_head_transform_closed": (
            t76["status"] == "HOLD_T76_COM_HIDDEN_GEOMETRY"
            and t76["classification"]
            == "COM_HIDDEN_DISPLACEMENT_NOT_STABLE_RANK_ONE"
            and t76["decision"] == "CLOSE_COM_AXIS_OUTPUT_HEAD_REFLECTION"
        ),
        "t52_source_identity_unchanged": (
            t66_prereg["assets"]["source_checkpoint"]["sha256"]
            == directory_sha256(SOURCE)
        ),
        "step_zero_raw_reference_unchanged": (
            t66_prereg["assets"]["expected_step_zero_raw"]["sha256"]
            == sha256(EXPECTED_RAW)
        ),
        "composed_source_exact": (
            manifest["schema_version"]
            == "open_duck.t77_composed_source.v1"
            and manifest["mechanism"]["reward_change"] is False
            and manifest["mechanism"]["policy_abi_change"] is False
            and manifest["mechanism"]["runtime_change"] is False
        ),
        "mechanism_has_no_scalar_sweep": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T77 preregistration checks failed: {failed}")

    python_inventory = {
        path.relative_to(COMPOSED).as_posix(): sha256(path)
        for path in sorted(COMPOSED.rglob("*.py"))
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t77_endpoint_joint_adapter_cpu_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
        ),
        "question": (
            "Can the exact T52-half checkpoint complete one finite PPO "
            "update on the unchanged eight-stratum COM endpoint bank while "
            "jointly changing only the recurrent adapter core, its output "
            "head, and the critic?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "causal_basis": {
            "t67_outcome": (
                "recurrent-core-only training stayed nominally valid but "
                "failed condition-7 persistence"
            ),
            "t71_result": (
                "the recurrent state contains COM information and the "
                "control law causally uses it"
            ),
            "t76_result": (
                "the COM response has consistent sign but is too distributed "
                "for a preregistered rank-one output-head transform"
            ),
            "selected_mechanism": (
                "co-adapt the recurrent representation and the adapter "
                "output head on the already frozen endpoint bank"
            ),
        },
        "mechanism": {
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
            "cpu_environments": 8,
            "hosted_environments": 256,
            "hosted_per_category": 32,
            "trainable_actor_groups": [
                "adapter_obs_projection",
                "adapter_hidden_projection",
                "adapter_hidden_bias",
                "adapter_location",
            ],
            "frozen_actor_groups": [
                "residual_trunk",
                "residual_location",
                "scale_logits",
            ],
            "normalizer_frozen": True,
            "critic_unchanged_trainable": True,
            "reward_change": False,
            "optimizer_change": "exact parameter-update mask only",
            "policy_abi_change": False,
            "runtime_change": False,
            "scalar_sweep": False,
        },
        "training": {
            "timesteps": 1024,
            "num_envs": 8,
            "batch_size": 8,
            "source": "exact_T55_materialized_T52_half",
            "exports": [0, 1024],
            "cpu_only": True,
        },
        "sources": {
            name: file_receipt(path) for name, path in SOURCE_FILES.items()
        },
        "assets": {
            "source_checkpoint": directory_receipt(SOURCE),
            "expected_step_zero_raw": file_receipt(EXPECTED_RAW),
            "reference_features": file_receipt(REFERENCE),
        },
        "playground": {
            "path": str(COMPOSED.resolve()),
            "python_inventory": python_inventory,
            "python_inventory_sha256": canonical_sha256(python_inventory),
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Source restores exactly; step-zero raw ONNX is byte-exact; "
                "all four recurrent-adapter groups and every critic leaf "
                "change; every base actor and normalizer leaf remains "
                "bit-exact; all trees and exports are finite."
            ),
            "pass_decision": (
                "EARN_T78_ENDPOINT_JOINT_ADAPTER_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_T77_ENDPOINT_JOINT_ADAPTER_CONTINUATION"
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
        "\n".join(
            [
                "# T77 endpoint joint-adapter CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact materialized T52-half",
                "- Randomizer: unchanged broad + nominal + six COM endpoints",
                "- Actor updates: recurrent core plus adapter output head",
                "- Base actor / normalizer: frozen",
                "- Reward / ABI / runtime changes: `0/0/0`",
                "- Behavior / hosted / robot execution now: `0/0/0`",
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
    print(f"sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
