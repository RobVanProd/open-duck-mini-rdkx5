#!/usr/bin/env python3
"""Freeze T66's endpoint-bank recurrent-core CPU contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t66_endpoint_core_cpu_preregistration.json"
MARKDOWN = ANALYSIS / "T66_ENDPOINT_CORE_CPU_PREREGISTRATION_20260728.md"
COMPOSED = Path("D:/CodexProjects/Open_Duck_Playground-composed-t66-v2")
MANIFEST = COMPOSED / "T66_COMPOSED_SOURCE_MANIFEST.json"
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
    "t54_attribution": ANALYSIS
    / "t54_t53_condition7_failure_attribution.json",
    "t52_qualification": ANALYSIS
    / "t52_uniform_half_head_qualification_result.json",
    "t53_robustness": ANALYSIS
    / "t53_uniform_half_head_r2_remainder_result.json",
    "t55_cpu_result": ANALYSIS
    / "t55_dynamic_single_support_cpu_result.json",
    "t65_endpoint_result": ANALYSIS
    / "t65_t62_midpoint_endpoint_screen_result.json",
    "module": ROOT / "patches" / "t66_endpoint_core_continuation.py",
    "composer": ROOT / "tools" / "compose_t66_endpoint_core_playground.py",
    "runner": ROOT / "tools" / "run_t66_endpoint_core_cpu_contract.py",
    "mechanism_test": ROOT / "tests" / "test_t66_endpoint_core_mechanism.py",
    "result_test": ROOT / "tests" / "test_t66_endpoint_core_cpu_contract.py",
    "manifest": MANIFEST,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
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
            raise FileExistsError(f"refusing to overwrite T66 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("formal T66 preregistration requires a clean worktree")

    t54 = json.loads(SOURCE_FILES["t54_attribution"].read_text())
    t52 = json.loads(SOURCE_FILES["t52_qualification"].read_text())
    t53 = json.loads(SOURCE_FILES["t53_robustness"].read_text())
    t55 = json.loads(SOURCE_FILES["t55_cpu_result"].read_text())
    t65 = json.loads(SOURCE_FILES["t65_endpoint_result"].read_text())
    manifest = json.loads(MANIFEST.read_text())
    checks = {
        "t52_green_through_condition4": (
            t52["status"] == "PASS_T52_UNIFORM_HALF_HEAD_QUALIFICATION"
            and t52["summary"]["green_cells"] == 64
        ),
        "t53_green_conditions5_and6_then_condition7_hold": (
            t53["status"] == "HOLD_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
            and t53["summary"]["first_failed_condition"]
            == "TORSO_COM_X_NEG"
            and t53["summary"]["green_cells"] == 40
        ),
        "t54_isolated_dynamic_balance_failure": (
            t54["status"]
            == "PASS_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
            and t54["classification"]
            == "NEGATIVE_COM_DYNAMIC_SUPPORT_CONTROL_INADEQUATE"
        ),
        "balance_first_family_formally_closed": (
            t65["status"] == "HOLD_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
            and t65["decision"]
            == "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
        ),
        "t52_half_materialization_exact": (
            t55["status"] == "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            and t55["materialization"]["materialized"]["sha256"]
            == directory_sha256(SOURCE)
        ),
        "step_zero_raw_reference_exact": (
            t55["deployments"]["materialized"]["raw"]["sha256"]
            == sha256(EXPECTED_RAW)
        ),
        "composed_source_exact": (
            manifest["schema_version"] == "open_duck.t66_composed_source.v1"
            and manifest["mechanism"]["reward_change"] is False
            and manifest["mechanism"]["policy_abi_change"] is False
        ),
        "mechanism_has_no_scalar_sweep": True,
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T66 preregistration checks failed: {failed}")

    python_inventory = {
        path.relative_to(COMPOSED).as_posix(): sha256(path)
        for path in sorted(COMPOSED.rglob("*.py"))
    }
    value: dict[str, Any] = {
        "schema_version": "open_duck.t66_endpoint_core_cpu_preregistration.v1",
        "status": "PREREGISTERED_T66_ENDPOINT_CORE_CPU_CONTRACT",
        "question": (
            "Can the exact T52-half trainable checkpoint complete one finite "
            "PPO update with a deterministic eight-stratum COM endpoint bank "
            "while changing only the recurrent actor core and critic?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "causal_basis": {
            "strongest_source": (
                "T52 passed 64/64 through R2 condition 4, then 32/32 under "
                "conditions 5-6"
            ),
            "isolated_blocker": (
                "condition 7 torso COM x=-0.05 m: 8/16 green; all x=0 "
                "green and failures contract-clean delayed backward falls"
            ),
            "closed_attempt": (
                "balance-first reward homotopy improved an intermediate "
                "policy but closed at 6/8"
            ),
            "selected_mechanism": (
                "retain one broad variable-configuration stratum and add "
                "nominal plus all six exact isolated COM endpoints; update "
                "only recurrent adaptation core, critic unchanged"
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
            ],
            "frozen_actor_groups": [
                "residual_trunk",
                "residual_location",
                "scale_logits",
                "adapter_location",
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
                "all three recurrent-core groups and every critic leaf "
                "change; every other actor and normalizer leaf remains "
                "bit-exact; all trees and exports are finite."
            ),
            "pass_decision": (
                "EARN_T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T66_ENDPOINT_CORE_CONTINUATION",
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
                "# T66 endpoint-core CPU preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact materialized T52-half",
                "- Randomizer: broad + nominal + six isolated COM endpoints",
                "- Actor updates: recurrent core only",
                "- Reward / ABI / runtime changes: `0/0/0`",
                "- Behavior / hosted / robot execution now: `0/0/0`",
                "",
                "A pass earns only hosted-run preregistration.",
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
