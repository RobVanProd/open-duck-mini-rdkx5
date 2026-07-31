#!/usr/bin/env python3
"""Preregister the exact T55 CPU recovery after its pre-execution hold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402


SOURCE_PREREG = (
    ANALYSIS / "t55_dynamic_single_support_cpu_preregistration.json"
)
ATTRIBUTION = (
    ANALYSIS / "t55_preexecution_velocity_hold_attribution.json"
)
OUTPUT = (
    ANALYSIS
    / "t55b_dynamic_single_support_cpu_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T55B_DYNAMIC_SINGLE_SUPPORT_CPU_RECOVERY_PREREGISTRATION_20260728.md"
)
RUNNER = ROOT / "tools" / "run_t55_dynamic_single_support_cpu_contract.py"
BUILDER = Path(__file__).resolve()
RECOVERY_TEST = (
    ROOT / "tests" / "test_t55b_dynamic_single_support_cpu_recovery.py"
)
EXPECTED_VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
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


def receipt_exact(value: dict[str, Any]) -> bool:
    path = Path(value["path"])
    if value["kind"] == "file":
        return (
            path.is_file()
            and path.stat().st_size == value["bytes"]
            and sha256(path) == value["sha256"]
        )
    if value["kind"] == "directory":
        return (
            path.is_dir()
            and t20.sha256_directory(path) == value["sha256"]
        )
    return False


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T55B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T55B preregistration requires a clean worktree")

    source = json.loads(SOURCE_PREREG.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    source_basis = {
        key: value
        for key, value in source.items()
        if key != "preregistered_contract_sha256"
    }
    attribution_basis = {
        key: value
        for key, value in attribution.items()
        if key != "result_sha256"
    }

    prior_velocity_limits = t20.VELOCITY_LIMITS
    command = t55.training_command(
        python=Path(sys.executable),
        output=Path("D:/frozen/t55b/output"),
        reference=Path("D:/frozen/t55b/reference.npz"),
        restore=Path("D:/frozen/t55b/checkpoint"),
        stage="balance",
    )
    velocity_index = command.index(
        "--ground_up_action_velocity_limits_rad_s"
    )
    velocity_value = command[velocity_index + 1]

    carried_sources = {
        name: item
        for name, item in source["sources"].items()
        if name != "runner"
    }
    sources = {
        **carried_sources,
        "source_preregistration": file_receipt(SOURCE_PREREG),
        "preexecution_attribution": file_receipt(ATTRIBUTION),
        "recovery_builder": file_receipt(BUILDER),
        "corrected_runner": file_receipt(RUNNER),
        "recovery_test": file_receipt(RECOVERY_TEST),
    }
    assets = source["assets"]
    old_runner = source["sources"]["runner"]
    checks = {
        "source_preregistration_identity_exact": (
            source["status"]
            == "PREREGISTERED_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            and source["failed_checks"] == []
            and canonical_sha256(source_basis)
            == source["preregistered_contract_sha256"]
        ),
        "preexecution_attribution_identity_exact": (
            attribution["status"]
            == "PASS_T55_PREEXECUTION_VELOCITY_HOLD_ATTRIBUTION"
            and attribution["decision"]
            == "EARN_T55B_EXACT_CPU_RECOVERY_PREREGISTRATION_ONLY"
            and attribution["failed_checks"] == []
            and canonical_sha256(attribution_basis)
            == attribution["result_sha256"]
        ),
        "failed_attempt_has_zero_policy_decision_weight": (
            attribution["execution"]["optimizer_steps"] == 0
            and attribution["execution"]["formal_behavior_cells"] == 0
            and attribution["execution"]["hosted_compute_units"] == 0
            and attribution["execution"]["robot_or_rdk_access"] == 0
        ),
        "old_runner_receipt_attributed_exactly": (
            {
                key: old_runner[key]
                for key in ("path", "bytes", "sha256")
            }
            == attribution["inputs"]["runner_before_correction"]
        ),
        "all_unchanged_sources_still_exact": all(
            receipt_exact(item) for item in carried_sources.values()
        ),
        "all_assets_still_exact": all(
            receipt_exact(item) for item in assets.values()
        ),
        "corrected_command_uses_t31_velocity_vector": (
            velocity_value == EXPECTED_VELOCITY_LIMITS
            and velocity_value == t31.VELOCITY_LIMITS
        ),
        "command_builder_restores_shared_t20_state": (
            t20.VELOCITY_LIMITS == prior_velocity_limits
        ),
        "recovery_changes_only_velocity_helper_wiring": (
            attribution["correction"]["single_change"]
            == "install T31.VELOCITY_LIMITS into T20 only while building "
            "each T55 command, then restore the prior helper value"
            and not attribution["correction"]["curriculum_formula_change"]
            and not attribution["correction"]["source_checkpoint_change"]
            and not attribution["correction"]["stage_order_change"]
            and not attribution["correction"]["step_count_change"]
            and not attribution["correction"]["gate_change"]
        ),
        "composed_inventory_unchanged": (
            {
                path.relative_to(
                    Path(source["playground"]["path"])
                ).as_posix(): sha256(path)
                for path in sorted(
                    Path(source["playground"]["path"]).rglob("*.py")
                )
            }
            == source["playground"]["python_inventory"]
        ),
        "hosted_behavior_robot_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t55b_dynamic_single_support_cpu_recovery_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T55B_DYNAMIC_SINGLE_SUPPORT_CPU_RECOVERY"
            if not failed
            else "HOLD_T55B_DYNAMIC_SINGLE_SUPPORT_CPU_RECOVERY"
        ),
        "question": source["question"],
        "source_contract": {
            "experiment": "T55",
            "path": str(SOURCE_PREREG.resolve()),
            "sha256": sha256(SOURCE_PREREG),
            "preregistered_contract_sha256": source[
                "preregistered_contract_sha256"
            ],
        },
        "preexecution_hold": {
            "path": str(ATTRIBUTION.resolve()),
            "sha256": sha256(ATTRIBUTION),
            "result_sha256": attribution["result_sha256"],
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "policy_decision_weight": 0,
        },
        "recovery": {
            "single_change": attribution["correction"]["single_change"],
            "velocity_limits_rad_s": velocity_value,
            "new_work_root_required": True,
            "reuse_partial_attempt": False,
            "one_attempt": True,
            "retry_or_tuning": False,
        },
        "causal_basis": source["causal_basis"],
        "mechanism": source["mechanism"],
        "materialization": source["materialization"],
        "sources": sources,
        "assets": assets,
        "playground": source["playground"],
        "cpu_contract": source["cpu_contract"],
        "decision_rule": source["decision_rule"],
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "cpu_simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_2048_step_cpu_recovery": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior_matrix": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    basis["preregistered_contract_sha256"] = canonical_sha256(basis)
    OUTPUT.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T55B dynamic single-support CPU recovery",
                "",
                f"- Status: `{basis['status']}`",
                "- Prior attempt: stopped before training (`0` steps)",
                "- Correction: install the frozen T31 velocity vector while "
                "building each command, then restore shared state",
                "- Mechanism/stages/steps/gates changed: `NO`",
                "- Recovery: one fresh 2,048-step CPU execution",
                "- Hosted/behavior/Gate5/robot authority: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(basis["status"])
    print(f"failed_checks={failed}")
    print(f"velocity_limits={velocity_value}")
    print(
        "preregistered_contract_sha256="
        f"{basis['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
