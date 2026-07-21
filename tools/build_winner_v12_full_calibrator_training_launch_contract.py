#!/usr/bin/env python3
"""Freeze the exact one-run Winner-v12 full-calibrator training launch."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v12_full_calibrator_training.py"
PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
CPU_CONTRACT = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract.json"
CPU_RESULT = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract_result.json"
CLAIM = ANALYSIS / "winner_v12_full_calibrator_training_authorization_claim.json"
OUTPUT = ANALYSIS / "winner_v12_full_calibrator_training_launch_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_CONTRACT_20260721.md"
WORKFLOW = ROOT / ".github/workflows/winner-v12-full-calibrator-training.yml"
TEST = ROOT / "tests/test_winner_v12_full_calibrator_training_launch_contract.py"
IMPORTER = (
    ROOT / "tools/import_winner_v12_full_calibrator_training_cpu_contract_result.py"
)
EXACT_WORK_ROOT = "/tmp/winner-v12-full-calibrator-training-work"
LOGICAL_RUN_ID = "winner-v12-full-calibrator-seed-120120"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def assigned_integer(module: ast.Module, name: str) -> int:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return int(ast.literal_eval(node.value))
    raise ValueError(f"missing literal assignment: {name}")


def source_manifest() -> dict[str, dict[str, str]]:
    paths = {
        "authorization_claim": (CLAIM, "lf"),
        "builder": (Path(__file__), "lf"),
        "cpu_contract": (CPU_CONTRACT, "lf"),
        "cpu_result": (CPU_RESULT, "lf"),
        "cpu_result_importer": (IMPORTER, "lf"),
        "preregistration": (PREREGISTRATION, "lf"),
        "runner": (RUNNER, "lf"),
        "tests": (TEST, "lf"),
        "workflow": (WORKFLOW, "lf"),
    }
    return {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
        for name, (path, mode) in paths.items()
    }


def main() -> int:
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu_contract = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    runner_source = RUNNER.read_text(encoding="utf-8")
    workflow_source = WORKFLOW.read_text(encoding="utf-8")
    runner_module = ast.parse(runner_source)
    runner_hash = lf_sha256(RUNNER)
    # The formal host checks out text as LF. Canonicalize here so a Windows
    # working tree cannot freeze a CRLF-only identity that Linux cannot match.
    cpu_result_hash = lf_sha256(CPU_RESULT)
    claim_payload = {
        "schema_version": "winner_v12.full_calibrator_training_authorization_claim.v1",
        "logical_run_id": LOGICAL_RUN_ID,
        "resolved_work_root": EXACT_WORK_ROOT,
        "repository_relative_claim_path": str(CLAIM.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "cpu_result_sha256": cpu_result_hash,
        "runner_lf_sha256": runner_hash,
    }
    CLAIM.write_text(
        json.dumps(claim_payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    schedule = {
        "root_seed": assigned_integer(runner_module, "ROOT_SEED"),
        "parameter_seed": assigned_integer(runner_module, "PARAMETER_SEED"),
        "episode_ticks": assigned_integer(runner_module, "EPISODE_TICKS"),
        "stage1_updates": assigned_integer(runner_module, "STAGE1_UPDATES"),
        "stage2_updates": assigned_integer(runner_module, "STAGE2_UPDATES"),
        "scheduled_tick_slots_per_update": assigned_integer(
            runner_module, "SCHEDULED_TICK_SLOTS_PER_UPDATE"
        ),
    }
    checks = {
        "preregistration_exact": preregistration.get("status")
        == "PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING"
        and preregistration.get("decision")
        == "AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY",
        "cpu_contract_frozen_and_passed": cpu_contract.get("status")
        == "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN"
        and cpu_contract.get("failed_checks") == []
        and all(cpu_contract.get("checks", {}).values()),
        "cpu_result_passed_zero_update": cpu_result.get("status")
        == "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT"
        and cpu_result.get("decision")
        == "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
        and cpu_result.get("failed_checks") == []
        and all(cpu_result.get("checks", {}).values())
        and cpu_result.get("execution")
        == {
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "cpu_result_contract_identity_exact": cpu_result.get("contract_lf_sha256")
        == lf_sha256(CPU_CONTRACT),
        "runner_identity_matches_cpu_contract": (
            cpu_contract.get("sources", {}).get("runner", {}).get("sha256")
            == runner_hash
            and cpu_contract.get("sources", {}).get("runner", {}).get("hash_mode")
            == "lf"
        ),
        "schedule_exact": schedule
        == {
            "root_seed": 120120,
            "parameter_seed": 60720,
            "episode_ticks": 250,
            "stage1_updates": 100,
            "stage2_updates": 100,
            "scheduled_tick_slots_per_update": 20_000,
        },
        "claim_exact": json.loads(CLAIM.read_text(encoding="utf-8")) == claim_payload,
        "runner_requires_explicit_offline_training_flags": (
            'parser.add_argument("--training-authorized", action="store_true")'
            in runner_source
            and 'parser.add_argument("--offline-cpu-only", action="store_true")'
            in runner_source
            and "full training requires --training-authorized --offline-cpu-only"
            in runner_source
        ),
        "runner_has_atomic_per_update_recovery": all(
            token in runner_source
            for token in (
                "def save_snapshot(",
                "def ensure_snapshot_receipt(",
                "def quarantine_uncommitted_pending(",
                "def newest_committed_snapshot(",
                "resume must use the newest committed per-update snapshot",
            )
        ),
        "workflow_one_shot_cpu_exact": (
            "workflow_dispatch:" not in workflow_source
            and "matrix:" not in workflow_source
            and "codex/winner-v4-response-contract" in workflow_source
            and "- .github/workflows/winner-v12-full-calibrator-training.yml"
            in workflow_source
            and 'python-version: "3.12.13"' in workflow_source
            and "runs-on: ubuntu-latest" in workflow_source
            and "timeout-minutes: 240" in workflow_source
            and "jax[cpu]==0.7.2" in workflow_source
            and "${{ github.run_attempt }}" in workflow_source
            and 'test "${{ github.run_attempt }}" = "1"' in workflow_source
        ),
        "workflow_exact_single_training_invocation": workflow_source.count(
            "python tools/run_winner_v12_full_calibrator_training.py"
        )
        == 1
        and "--training-authorized" in workflow_source
        and "--offline-cpu-only" in workflow_source
        and f"--work-root {EXACT_WORK_ROOT}" in workflow_source
        and "--resume-snapshot" not in workflow_source,
        "workflow_uploads_recovery_on_failure": "if: always()" in workflow_source
        and "actions/upload-artifact@v4" in workflow_source
        and EXACT_WORK_ROOT in workflow_source
        and "winner-v12-full-calibrator-training-${{ github.run_id }}"
        in workflow_source,
        "workflow_has_no_gpu_surface": "runs-on: ubuntu-latest" in workflow_source
        and "runs-on: [self-hosted" not in workflow_source
        and "--gpu" not in workflow_source
        and "cuda" not in workflow_source.lower(),
        "formal_support_and_robot_remain_zero": (
            cpu_result.get("authority", {}).get("formal_support_gate_executed") is False
            and cpu_result.get("authority", {}).get("robot_clearance") is False
            and cpu_result.get("authority", {}).get(
                "rdkx5_robot_serial_gpio_i2c_torque_motion"
            )
            is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit(f"Winner-v12 launch contract build failed: {failed}")
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v12.full_calibrator_training_launch_contract.v1",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN",
        "decision": "AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN",
        "logical_run_id": LOGICAL_RUN_ID,
        "cpu_result_sha256": cpu_result_hash,
        "runner_lf_sha256": runner_hash,
        "authorization_claim": {
            "path": str(CLAIM.relative_to(ROOT)).replace("\\", "/"),
            "lf_sha256": lf_sha256(CLAIM),
        },
        "authorization_claim_payload": claim_payload,
        "host": {
            "provider": "GitHub Actions",
            "runner": "ubuntu-latest",
            "device": "CPU only",
            "timeout_minutes": 240,
            "resolved_work_root": EXACT_WORK_ROOT,
            "reason": "the exact pinned CPU environment passed the formal zero-update contract and the measured contract runtime projects below the fixed wall ceiling",
        },
        "schedule": schedule,
        "artifact_policy": {
            "snapshot_every_update": True,
            "immutable_snapshot_count_on_success": 201,
            "stage1_final_checkpoint": True,
            "half_and_final_checkpoint_and_onnx": True,
            "upload_work_root_even_on_failure": True,
            "retry": False,
            "resume": "only the same logical run from its newest committed hash-verified snapshot under a separately reviewed failure attribution",
        },
        "execution_before_launch": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "checks": checks,
        "failed_checks": [],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "pass_authorizes_only": "one seed-120120 full automatic-calibrator training logical run; it does not authorize the 124-cell support gate, response-conditioned locomotion, deployment selection, Gate 5, or robot access",
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v12 full-calibrator training launch contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Logical run: `{LOGICAL_RUN_ID}`",
                f"- Work root: `{EXACT_WORK_ROOT}`",
                f"- Runner LF SHA-256: `{runner_hash}`",
                f"- CPU-result SHA-256: `{cpu_result_hash}`",
                f"- Claim LF SHA-256: `{lf_sha256(CLAIM)}`",
                f"- Source-manifest SHA-256: `{payload['source_manifest_sha256']}`",
                "- Optimizer updates before launch: `0`",
                "- Formal support/locomotion/robot execution: `0 / 0 / 0`",
                "",
                "This freezes one CPU-only seed-120120 logical training run with 100",
                "Stage-1 and 100 Stage-2 updates. Every update commits an immutable",
                "hash-verified recovery snapshot. The complete work root is uploaded even",
                "if the process fails. No retry or alternate work root is authorized.",
                "",
                "A successful artifact still must pass the separate 124-cell support/context",
                "gate before response-conditioned locomotion may be preregistered.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
