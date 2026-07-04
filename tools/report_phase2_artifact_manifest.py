#!/usr/bin/env python3
"""Write a compact hash manifest for the current Phase 2 stage.

The manifest is a review artifact for the offline domain-randomization
campaign. It records the exact candidate, corrected bridge, warm-start
checkpoint, stage-gate evidence, and recipe/decision tools currently defining
Phase 2. It is read-only: it does not train, SSH, deploy, touch the robot, or
modify Playground.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_ARTIFACT_MANIFEST.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_artifact_manifest.json"
DEFAULT_CANDIDATE = ROOT / "policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx"
DEFAULT_CANDIDATE_METADATA = (
    ROOT / "policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/README.md"
)
DEFAULT_BRIDGE = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint"
)


REVIEW_ARTIFACTS = [
    "docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md",
    "docs/TRAINING_ENV_7900XTX.md",
    "outputs/analysis/PHASE2_CURRENT_STATUS.md",
    "outputs/analysis/phase2_current_status.json",
    "outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_DECISION.md",
    "outputs/analysis/phase2_limit198_ppo_loc_warmstart_decision.json",
    "outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_EXPORT_FIDELITY.md",
    "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_export_fidelity.json",
    "outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X008_GATE.md",
    "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_x008_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X0_GATE.md",
    "outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_x0_gate.json",
    "outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md",
    "outputs/analysis/phase2_curriculum_gate_ledger.json",
    "outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md",
    "outputs/analysis/phase2_z005_seed5_failure_diagnostic.json",
    "outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md",
    "outputs/analysis/phase2_z005_support_next_recipe.json",
    "outputs/analysis/PHASE2_Z005_SUPPORT_LIMIT198_A100_RESULT.md",
    "outputs/analysis/phase2_z005_support_limit198_a100_result.json",
    "outputs/analysis/PHASE2_Z005_MOTION_FLOOR_NEXT_RECIPE.md",
    "outputs/analysis/phase2_z005_motion_floor_next_recipe.json",
    "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_NEXT_RECIPE.md",
    "outputs/analysis/phase2_z002_tracking_margin_next_recipe.json",
    "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_LAUNCH_AUDIT.md",
    "outputs/analysis/phase2_z002_tracking_margin_launch_audit.json",
    "outputs/analysis/PHASE2_Z002_COLAB_LAUNCH_HANDOFF.md",
    "outputs/analysis/phase2_z002_colab_launch_handoff.json",
    "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_NEXT_RECIPE.md",
    "outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json",
    "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_LAUNCH_AUDIT.md",
    "outputs/analysis/phase2_z002_teacher_continuity_launch_audit.json",
    "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_COLAB_LAUNCH_HANDOFF.md",
    "outputs/analysis/phase2_z002_teacher_continuity_colab_launch_handoff.json",
    "outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_A100_RESULT.md",
    "outputs/analysis/phase2_z002_teacher_continuity_a100_result.json",
    "outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/CANDIDATE_CHECKPOINT_SWEEP.md",
    "outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/candidate_checkpoint_sweep.json",
    "outputs/analysis/PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION.md",
    "outputs/analysis/phase2_package_only_archive_verification.json",
    "outputs/analysis/PHASE2_LOCAL_FALLBACK_READINESS.md",
    "outputs/analysis/phase2_local_fallback_readiness.json",
    "outputs/analysis/PHASE2_NEXT_RUN_PLAN.md",
    "outputs/analysis/phase2_next_run_plan.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/LIVE_ORACLE_DAGGER_ITERATION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_plan/live_oracle_dagger_iteration.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_decision.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_ITERATION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_iteration.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_ROLLOUT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_rollout.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_ROLLOUT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_rollout.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_RELABEL.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_relabel.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_RELABEL.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_relabel.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X008_MANIFEST.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x008_manifest.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_X0_MANIFEST.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_x0_manifest.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student/PHASE_MODULATED_BC_STUDENT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student/phase_modulated_bc_student.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_decision.json",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_x008_gate/candidate_seed_sweep.partial.json",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_20260703/README.md",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_20260703/candidate.onnx",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_20260703/student.npz",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate180/PHASE_MODULATED_BC_STUDENT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate180/phase_modulated_bc_student.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_X008_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_x008_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_X0_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_x0_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_decision.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_GENTLE_PUSH_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_gentle_push_decision.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_X008_Z0026_GENTLE_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_x008_z0026_gentle_push_gate.json",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/README.md",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/candidate.onnx",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate180_20260703/student.npz",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate160/PHASE_MODULATED_BC_STUDENT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate160/phase_modulated_bc_student.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_X008_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_x008_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_X008_Z0026_GENTLE_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_x008_z0026_gentle_push_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_X0_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_x0_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_X0_Z0026_GENTLE_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_x0_z0026_gentle_push_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_Z005_X008_NO_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_z005_x008_no_push_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_Z005_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_z005_decision.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_decision.json",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/README.md",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/candidate.onnx",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate160_20260703/student.npz",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate150/PHASE_MODULATED_BC_STUDENT.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate150/phase_modulated_bc_student.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_X008_NO_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z005_x008_no_push_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_X0_NO_PUSH_GATE.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z005_x0_no_push_gate.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z0026_X008_NO_PUSH_REGRESSION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0026_x008_no_push_regression.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z0026_X0_NO_PUSH_REGRESSION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0026_x0_no_push_regression.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z0026_X008_GENTLE_PUSH_REGRESSION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0026_x008_gentle_push_regression.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z0026_X0_GENTLE_PUSH_REGRESSION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0026_x0_gentle_push_regression.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_decision.json",
    "outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE150_Z005_DECISION.md",
    "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z005_decision.json",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/README.md",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx",
    "policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/student.npz",
    "outputs/analysis/PHASE2_STAGE_GUARD.md",
    "outputs/analysis/phase2_stage_guard.json",
    "outputs/analysis/rocm_mjx_isolation_post_bios/ROCM_MJX_RUNTIME_ISOLATION.md",
    "outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json",
    "outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md",
    "outputs/analysis/phase2_colab_package_manifest.json",
    "outputs/analysis/PHASE2_COLAB_PACKAGE_ONLY_MANIFEST.md",
    "outputs/analysis/phase2_colab_package_only_manifest.json",
    "outputs/analysis/PHASE2_Z005_T4_RECOVERY_DECISION.md",
    "outputs/analysis/phase2_z005_t4_recovery_decision.json",
    "outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_NEXT_DECISION.md",
    "outputs/analysis/phase2_z005_recovery_dagger_next_decision.json",
    "outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md",
    "outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_decision.json",
    "outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0030_SHORT_DECISION.md",
    "outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0030_short_decision.json",
    "outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0027_SHORT_DECISION.md",
    "outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0027_short_decision.json",
    "outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z00255_SHORT_DECISION.md",
    "outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z00255_short_decision.json",
    "outputs/analysis/PHASE2_TERRAIN_SUPPORT_SOURCE_NEXT_PLAN.md",
    "outputs/analysis/phase2_terrain_support_source_next_plan.json",
    "outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/CANDIDATE_CHECKPOINT_SWEEP.md",
    "outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/candidate_checkpoint_sweep.json",
    "tools/plan_phase2_z005_support_recipe.py",
    "tools/plan_phase2_z005_motion_floor_recipe.py",
    "tools/plan_phase2_z002_tracking_margin_recipe.py",
    "tools/plan_phase2_z002_teacher_continuity_recipe.py",
    "tools/report_phase2_colab_package_manifest.py",
    "tools/report_phase2_local_fallback_readiness.py",
    "tools/report_phase2_z005_post_training_gates.py",
    "tools/report_phase2_z002_tracking_margin_post_training_gates.py",
    "tools/report_phase2_z002_launch_audit.py",
    "tools/report_phase2_colab_launch_handoff.py",
    "tools/report_phase2_package_only_archive_verification.py",
    "tools/report_phase2_stage_guard.py",
    "tools/run_colab_cli_cuda_workflow.py",
]


GATE_ARTIFACTS = [
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json",
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json",
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json",
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json",
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json",
    "outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_nopush_15s_8seed_cpu.json",
]


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(file_sha256(child).encode())
        digest.update(b"\0")
    return digest.hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
    }
    if not path.exists():
        item["status"] = "MISSING"
        return item
    if path.is_dir():
        files = [child for child in path.rglob("*") if child.is_file()]
        item.update(
            {
                "status": "PRESENT_DIR",
                "sha256": directory_sha256(path),
                "file_count": len(files),
                "size_bytes": sum(child.stat().st_size for child in files),
            }
        )
    else:
        item.update(
            {
                "status": "PRESENT_FILE",
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return item


def run_git(command: list[str]) -> str | None:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def git_state() -> dict[str, Any]:
    branch = run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    upstream = run_git(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    return {
        "branch": branch,
        "upstream": upstream,
        "note": (
            "This manifest records stable artifact hashes. It intentionally does not record HEAD, "
            "because a committed manifest cannot self-reference its containing commit hash."
        ),
    }


def load_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def collect(args: argparse.Namespace) -> dict[str, Any]:
    candidate = Path(args.candidate)
    metadata = Path(args.candidate_metadata)
    bridge = Path(args.bridge_json)
    restore_checkpoint = Path(args.restore_checkpoint)
    ledger = load_json_optional(ROOT / "outputs/analysis/phase2_curriculum_gate_ledger.json")
    recipe = load_json_optional(ROOT / "outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json")
    return {
        "status": "PASS_PHASE2_ARTIFACT_MANIFEST_READY",
        "stage": "stage_z002_teacher_continuity",
        "current_gate_status": ledger.get("status"),
        "next_recipe_status": recipe.get("status"),
        "git": git_state(),
        "core_artifacts": {
            "candidate": artifact(candidate),
            "candidate_metadata": artifact(metadata),
            "corrected_bridge": artifact(bridge),
            "restore_checkpoint": artifact(restore_checkpoint),
        },
        "gate_artifacts": {name: artifact(ROOT / name) for name in GATE_ARTIFACTS},
        "review_artifacts": {name: artifact(ROOT / name) for name in REVIEW_ARTIFACTS},
        "promotion_gate": {
            "decision_tool": "tools/report_phase2_z002_tracking_margin_post_training_gates.py",
            "required_post_training_status": "PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES",
            "robot_validation_allowed": False,
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Artifact Manifest",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"current_gate_status: `{payload.get('current_gate_status')}`",
        f"next_recipe_status: `{payload.get('next_recipe_status')}`",
        "",
        "This is a read-only hash manifest. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Git",
        "",
    ]
    for key, value in payload["git"].items():
        lines.append(f"- `{key}`: `{value}`")

    def table(title: str, items: dict[str, dict[str, Any]]) -> None:
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| name | status | sha256 | size/files | path |",
                "|---|---|---|---:|---|",
            ]
        )
        for name, item in items.items():
            size = item.get("file_count", item.get("size_bytes", "NA"))
            lines.append(
                f"| `{name}` | `{item.get('status')}` | `{item.get('sha256', 'NA')}` | "
                f"{size} | `{item.get('path')}` |"
            )

    table("Core Artifacts", payload["core_artifacts"])
    table("Gate Artifacts", payload["gate_artifacts"])
    table("Review Artifacts", payload["review_artifacts"])
    lines.extend(
        [
            "",
            "## Promotion Gate",
            "",
            f"- decision_tool: `{payload['promotion_gate']['decision_tool']}`",
            f"- required_post_training_status: `{payload['promotion_gate']['required_post_training_status']}`",
            f"- robot_validation_allowed: `{payload['promotion_gate']['robot_validation_allowed']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    parser.add_argument("--candidate-metadata", default=str(DEFAULT_CANDIDATE_METADATA))
    parser.add_argument("--bridge-json", default=str(DEFAULT_BRIDGE))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = collect(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
