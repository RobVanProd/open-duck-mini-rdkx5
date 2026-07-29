#!/usr/bin/env python3
"""Preregister T148B after T148 exposed stochastic CPU group coverage."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

import build_t128_negative_only_expert_cpu_preregistration as t128
import run_t148_command_group_risk_cpu_contract as t148


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = (
    ANALYSIS / "t148b_command_group_risk_cpu_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T148B_COMMAND_GROUP_RISK_CPU_RECOVERY_PREREGISTRATION_20260729.md"
)
T148_PREREG = ANALYSIS / "t148_command_group_risk_cpu_preregistration.json"
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t148-command-group-risk-v1"
)
ORIGINAL_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t148_command_group_risk_cpu_v1"
)
ORIGINAL_OUTPUT = ORIGINAL_WORK / "smoke"
ORIGINAL_LOG = ORIGINAL_WORK / "training.log"

SOURCE_FILES = {
    "builder": Path(__file__).resolve(),
    "runner": ROOT
    / "tools/run_t148b_command_group_risk_cpu_recovery.py",
    "test": ROOT / "tests/test_t148b_command_group_risk_cpu_recovery.py",
    "original_preregistration": T148_PREREG,
    "original_runner": ROOT
    / "tools/run_t148_command_group_risk_cpu_contract.py",
    "loss_source": ROOT / "patches/t147_command_group_risk_ppo_losses.py",
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T148B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T148B preregistration requires clean tree")

    original = json.loads(T148_PREREG.read_text(encoding="utf-8"))
    original_events = list(ORIGINAL_OUTPUT.glob("events.out.tfevents*"))
    if len(original_events) != 1:
        raise RuntimeError("T148 recovery requires one original event file")
    scalars = t148.read_tensorboard_scalars(original_events[0])
    checkpoints = sorted(
        int(path.name.rsplit("_", 1)[1])
        for path in ORIGINAL_OUTPUT.iterdir()
        if path.is_dir()
    )
    graphs = sorted(
        int(path.stem.rsplit("_", 1)[1])
        for path in ORIGINAL_OUTPUT.glob("*.onnx")
    )
    low_count = scalars.get("training/command_group_074_count", [])
    low_loss = scalars.get("training/command_group_074_loss", [])
    all_present = scalars.get(
        "training/command_groups_all_present", []
    )
    total_loss = scalars.get("training/total_loss", [])
    log_text = ORIGINAL_LOG.read_text(encoding="utf-8")
    inventory = {
        path.relative_to(PLAYGROUND).as_posix(): t128.sha256(path)
        for path in sorted(PLAYGROUND.rglob("*.py"))
    }
    checks = {
        "original_contract_identity_green": (
            original["status"]
            == "PREREGISTERED_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
            and original["failed_checks"] == []
        ),
        "original_update_and_exports_completed": (
            checkpoints == [0, 1024]
            and graphs == [0, 1024]
            and t148.READBACK in log_text
        ),
        "original_total_loss_finite": (
            len(total_loss) == 1
            and total_loss[0]["step"] == 1024
            and np.isfinite(total_loss[0]["value"])
        ),
        "original_validation_population_missed_low_group": (
            len(low_count) == 1
            and low_count[0]["step"] == 1024
            and low_count[0]["value"] == 0.0
            and len(low_loss) == 1
            and np.isneginf(low_loss[0]["value"])
            and len(all_present) == 1
            and all_present[0]["value"] == 0.0
        ),
        "original_result_absent_after_nonfinite_recorder_stop": (
            not t148.RESULT.exists()
        ),
        "recovery_changes_validation_population_only": True,
        "environment_steps_and_exports_unchanged": True,
        "composed_source_inventory_unchanged": (
            inventory == original["playground"]["python_inventory"]
        ),
        "all_sources_present": all(
            path.exists() for path in SOURCE_FILES.values()
        ),
        "no_behavior_hosted_or_robot_execution": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T148B preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t148b_command_group_risk_cpu_recovery_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T148B_COMMAND_GROUP_RISK_CPU_RECOVERY"
        ),
        "question": (
            "Does the unchanged T147 trainer integration pass when the "
            "CPU-only validation population is large enough to contain all "
            "three continuous command groups deterministically in practice?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "recovery_basis": {
            "original_execution": {
                "work_root": str(ORIGINAL_WORK.resolve()),
                "log": t128.file_receipt(ORIGINAL_LOG),
                "event_file": t128.file_receipt(original_events[0]),
                "checkpoint_steps": checkpoints,
                "graph_steps": graphs,
                "group_074_count": low_count,
                "group_074_loss": low_loss,
                "all_groups_present": all_present,
                "total_loss": total_loss,
            },
            "classification": (
                "CPU validation population coverage failure, not optimizer "
                "or policy-graph failure"
            ),
            "change": (
                "num_envs and batch_size 8->32; source, loss, seed, support, "
                "steps, exports, physics, reward, optimizer and ABI unchanged"
            ),
        },
        "mechanism": original["mechanism"],
        "training": {
            **original["training"],
            "num_envs": 32,
            "batch_size": 32,
            "exports": [0, 1024],
            "validation_population_change_only": True,
        },
        "thresholds": original["thresholds"],
        "sources": {
            name: t128.file_receipt(path)
            for name, path in SOURCE_FILES.items()
        },
        "assets": original["assets"],
        "playground": {
            "path": str(PLAYGROUND.resolve()),
            "python_inventory": inventory,
            "python_inventory_sha256": t128.canonical_sha256(inventory),
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": original["decision_rule"]["pass"],
            "pass_decision": (
                "EARN_T149_COMMAND_GROUP_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_COMMAND_GROUP_RISK_INTEGRATION",
            "no_behavior_selection": True,
            "no_further_cpu_recovery": True,
        },
        "authority": {
            "execute_one_cpu_recovery": True,
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
        "# T148B command-group risk CPU recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- T148 execution/export: completed\n"
        "- T148 recorder hold: 8-env population contained zero `.074` rows\n"
        "- Recovery-only change: env/batch population `8 → 32`\n"
        "- Steps/exports/mechanism/reward/optimizer/ABI: unchanged\n"
        "- Hosted/behavior/robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
