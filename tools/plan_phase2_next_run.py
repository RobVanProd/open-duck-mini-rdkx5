#!/usr/bin/env python3
"""Write the next runnable Phase 2 command bundle.

This is read-only planning. It does not train, SSH, deploy, or touch the robot.
It consumes the current Phase 2 status report and emits the preferred A100/Colab
command plus a local ROCm fallback command that uses recorded environment
settings.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS_JSON = ROOT / "outputs" / "analysis" / "phase2_current_status.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "PHASE2_NEXT_RUN_PLAN.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "phase2_next_run_plan.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs"
    / "phase2_domain_randomization"
    / "stage_a2_preserve_narrow_flat_no_push_gpu"
    / "smoke_20260628T031553Z_gpu"
    / "2026_06_27_232221_491520"
)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def run_probe(command: list[str], timeout_s: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_s,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "ok": completed.returncode == 0,
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
            "missing_executable": command[0],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "ok": False,
            "timeout": True,
        }


def combined_text(result: dict[str, Any]) -> str:
    return ((result.get("stdout") or "") + (result.get("stderr") or "")).strip()


def colab_readiness(session: str, timeout_s: int) -> dict[str, Any]:
    colab_path = shutil.which("colab")
    payload: dict[str, Any] = {
        "checked": True,
        "session": session,
        "colab_executable": colab_path,
        "sessions_command": None,
        "status_command": None,
        "active": False,
    }
    if colab_path is None:
        payload["status"] = "HOLD_COLAB_CLI_MISSING"
        return payload

    sessions = run_probe(["colab", "sessions"], timeout_s)
    status = run_probe(["colab", "status", "-s", session], timeout_s)
    status_text = combined_text(status).lower()
    payload["sessions_command"] = sessions
    payload["status_command"] = status
    payload["active"] = status["ok"] and "not found" not in status_text and "no active" not in status_text
    payload["status"] = "PASS_COLAB_SESSION_VISIBLE" if payload["active"] else "HOLD_NO_ACTIVE_COLAB_SESSION"
    return payload


def git_readiness(timeout_s: int) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "checked": True,
        "remote": None,
        "branch": None,
        "read_auth_ok": False,
    }
    remote = run_probe(["git", "remote", "get-url", "origin"], timeout_s)
    branch = run_probe(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout_s)
    payload["remote_command"] = remote
    payload["branch_command"] = branch
    if remote["ok"]:
        payload["remote"] = (remote.get("stdout") or "").strip()
    if branch["ok"]:
        payload["branch"] = (branch.get("stdout") or "").strip()

    if payload["branch"]:
        ls_remote = run_probe(
            ["git", "ls-remote", "--exit-code", "origin", f"refs/heads/{payload['branch']}"],
            timeout_s,
        )
    else:
        ls_remote = run_probe(["git", "ls-remote", "--exit-code", "origin", "HEAD"], timeout_s)
    payload["ls_remote_command"] = ls_remote
    payload["read_auth_ok"] = ls_remote["ok"]
    payload["status"] = "PASS_GIT_REMOTE_READ_AUTH" if ls_remote["ok"] else "HOLD_GIT_REMOTE_AUTH_UNAVAILABLE"
    return payload


def unchecked_readiness() -> dict[str, Any]:
    return {
        "colab": {
            "checked": False,
            "status": "NOT_CHECKED",
        },
        "git": {
            "checked": False,
            "status": "NOT_CHECKED",
        },
        "launch_status": "NOT_CHECKED",
    }


def colab_command(session: str, candidate_name: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z005-support",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-timeout-s",
        "10800",
        "--run",
    ]


def local_rocm_command(restore_checkpoint: Path, output_root: str) -> list[str]:
    return [
        "../envs/open-duck-playground/bin/python",
        "tools/run_actuator_bridge_training_smoke.py",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--output-root",
        output_root,
        "--run",
        "--platform",
        "gpu",
        "--local-rocm-safe-env",
        "--timeout-s",
        "2700",
        "--task",
        "rough_terrain_backlash",
        "--num-timesteps",
        "81920",
        "--export-min-step",
        "1",
        "--ppo-num-envs",
        "8",
        "--ppo-num-evals",
        "4",
        "--ppo-episode-length",
        "750",
        "--ppo-unroll-length",
        "20",
        "--ppo-batch-size",
        "64",
        "--ppo-num-minibatches",
        "1",
        "--ppo-num-updates-per-batch",
        "2",
        "--restore-checkpoint-path",
        rel(restore_checkpoint) or str(restore_checkpoint),
        "--ppo-learning-rate",
        "0.000003",
        "--ppo-entropy-cost",
        "0.001",
        "--ppo-clipping-epsilon",
        "0.02",
        "--ppo-max-grad-norm",
        "0.1",
        "--restore-policy-kl-scale",
        "3",
        "--tracking-lin-vel-scale",
        "3",
        "--tracking-sigma",
        "0.01",
        "--forward-progress-scale",
        "2.5",
        "--forward-wrong-direction-scale",
        "-3",
        "--forward-wrong-direction-allowed-reverse-ratio",
        "0.05",
        "--command-progress-scale",
        "1.5",
        "--command-progress-shortfall-scale",
        "-4",
        "--command-progress-required-ratio",
        "0.45",
        "--command-progress-warmup-steps",
        "30",
        "--action-rate-huber-delta",
        "0.05",
        "--actuator-tracking-huber-delta",
        "0.03",
        "--forward-swing-clearance-huber-delta",
        "0.003",
        "--forward-swing-advance-huber-delta",
        "0.002",
        "--action-rate-scale",
        "-0.08",
        "--action-magnitude-scale",
        "-0.005",
        "--base-height-scale",
        "-0.3",
        "--forward-pitch-scale",
        "-0.4",
        "--forward-pitch-rate-scale",
        "-0.08",
        "--forward-single-support-scale",
        "0.2",
        "--forward-double-support-scale",
        "-0.35",
        "--forward-double-support-dwell-scale",
        "-1",
        "--forward-double-support-dwell-grace-steps",
        "8",
        "--forward-swing-clearance-scale",
        "-0.0005",
        "--forward-swing-clearance-target-m",
        "0.018",
        "--forward-swing-advance-scale",
        "-0.002",
        "--forward-swing-advance-target-m",
        "0.004",
        "--alive-scale",
        "2",
        "--imitation-scale",
        "0",
        "--lin-vel-x-min",
        "0.06",
        "--lin-vel-x-max",
        "0.1",
        "--lin-vel-y-min",
        "0",
        "--lin-vel-y-max",
        "0",
        "--ang-vel-yaw-min",
        "0",
        "--ang-vel-yaw-max",
        "0",
        "--command-resample-steps",
        "600",
        "--zero-command-probability",
        "0.15",
        "--dr-friction-min",
        "0.98",
        "--dr-friction-max",
        "1.02",
        "--dr-frictionloss-scale-min",
        "0.995",
        "--dr-frictionloss-scale-max",
        "1.005",
        "--dr-armature-scale-min",
        "1",
        "--dr-armature-scale-max",
        "1.005",
        "--dr-com-jitter-m",
        "0.002",
        "--dr-mass-scale-min",
        "0.995",
        "--dr-mass-scale-max",
        "1.005",
        "--dr-torso-mass-delta-min",
        "-0.005",
        "--dr-torso-mass-delta-max",
        "0.005",
        "--dr-qpos-jitter-rad",
        "0.002",
        "--dr-actuator-gain-scale-min",
        "0.995",
        "--dr-actuator-gain-scale-max",
        "1.005",
        "--dr-leg-geometry-jitter-scale",
        "0.001",
        "--push-interval-min-s",
        "7",
        "--push-interval-max-s",
        "12",
        "--push-magnitude-min",
        "0.02",
        "--push-magnitude-max",
        "0.1",
        "--noise-level",
        "0.5",
        "--noise-hip-pos",
        "0.0075",
        "--noise-knee-pos",
        "0.0075",
        "--noise-ankle-pos",
        "0.0075",
        "--noise-joint-vel",
        "0.75",
        "--noise-gravity",
        "0.04",
        "--noise-gyro",
        "0.04",
        "--noise-accelerometer",
        "0.02",
        "--no-push-enable",
        "--actuator-bridge-delay-min-ticks",
        "3",
        "--actuator-bridge-delay-max-ticks",
        "3",
        "--actuator-bridge-tau-min-s",
        "0.06",
        "--actuator-bridge-tau-max-s",
        "0.14",
        "--actuator-bridge-velocity-limit-min-rad-s",
        "2",
        "--actuator-bridge-velocity-limit-max-rad-s",
        "3.25",
        "--actuator-bridge-per-joint-variation",
        "0.1",
        "--actuator-tracking-scale",
        "-0.01",
        "--terrain-hfield-z-scale",
        "0.005",
    ]


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    readiness = payload.get("readiness", {})
    colab = readiness.get("colab", {})
    git = readiness.get("git", {})
    lines = [
        "# Phase 2 Next Run Plan",
        "",
        f"status: `{payload['status']}`",
        f"launch_status: `{readiness.get('launch_status')}`",
        "",
        "## Current Decision",
        "",
        f"- current_status: `{payload['current_status']}`",
        f"- blocking_gate: `{payload['blocking_gate']}`",
        f"- candidate: `{payload['candidate']['path']}`",
        f"- candidate_sha256: `{payload['candidate']['sha256']}`",
        f"- restore_checkpoint: `{payload['restore_checkpoint']['path']}`",
        f"- restore_checkpoint_present: `{payload['restore_checkpoint']['present']}`",
        "",
        "## Readiness",
        "",
        f"- colab_status: `{colab.get('status')}`",
        f"- colab_session: `{colab.get('session')}`",
        f"- colab_active: `{colab.get('active')}`",
        f"- git_status: `{git.get('status')}`",
        f"- git_branch: `{git.get('branch')}`",
        f"- git_remote_read_auth_ok: `{git.get('read_auth_ok')}`",
        "",
        "The Colab check is read-only (`colab sessions` / `colab status`). The Git check is read-only (`git ls-remote`) and does not push.",
        "",
        "## Preferred A100 / Colab Command",
        "",
        "Use this when a visible Colab GPU session is available:",
        "",
        "```bash",
        payload["commands"]["colab"]["shell"],
        "```",
        "",
        "## Local ROCm Fallback Command",
        "",
        "This is fallback/backend evidence only unless it clears the same post-training gates:",
        "",
        "```bash",
        payload["commands"]["local_rocm"]["shell"],
        "```",
        "",
        "## Promotion Rule",
        "",
        "Promotion still requires full corrected-bridge post-training gates, not a smoke pass:",
        "",
        "- z=0.005 x=0.08 no-push, 8 seeds, 15s",
        "- z=0.005 x=0.0 no-push, 8 seeds, 15s",
        "- z=0.002 x=0.08 no-push, 8 seeds, 15s",
        "- z=0.002 x=0.0 no-push, 8 seeds, 15s",
        "- z=0.002 x=0.08 gentle-push, 8 seeds, 15s",
        "- z=0.002 x=0.0 gentle-push, 8 seeds, 15s",
        "",
        "No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this plan.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", default=str(DEFAULT_STATUS_JSON))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument("--candidate-name", default="phase2_z005_support_stability_cuda")
    parser.add_argument(
        "--local-output-root",
        default="outputs/phase2_domain_randomization/stage_z005_support_local_rocm_safeenv_8env_81920",
    )
    parser.add_argument(
        "--output-md",
        default=str(ROOT / "outputs" / "analysis" / "PHASE2_NEXT_RUN_PLAN.md"),
    )
    parser.add_argument(
        "--output-json",
        default=str(ROOT / "outputs" / "analysis" / "phase2_next_run_plan.json"),
    )
    parser.add_argument("--check-colab", action="store_true")
    parser.add_argument("--check-git-auth", action="store_true")
    parser.add_argument("--readiness-timeout-s", type=int, default=30)
    args = parser.parse_args()

    status = read_json(Path(args.status_json))
    restore_checkpoint = Path(args.restore_checkpoint)
    colab = colab_command(args.session, args.candidate_name)
    local = local_rocm_command(restore_checkpoint, args.local_output_root)
    candidate = status.get("candidate", {})
    readiness = unchecked_readiness()
    if args.check_colab:
        readiness["colab"] = colab_readiness(args.session, args.readiness_timeout_s)
    if args.check_git_auth:
        readiness["git"] = git_readiness(args.readiness_timeout_s)
    if args.check_colab and readiness["colab"].get("status") != "PASS_COLAB_SESSION_VISIBLE":
        readiness["launch_status"] = "HOLD_PHASE2_A100_SESSION_NOT_READY"
    elif args.check_colab:
        readiness["launch_status"] = "PASS_PHASE2_A100_SESSION_READY"

    payload: dict[str, Any] = {
        "status": "PASS_PHASE2_NEXT_RUN_PLAN_READY",
        "current_status": status.get("status"),
        "blocking_gate": "z005_x008_nopush",
        "candidate": {
            "path": candidate.get("path"),
            "sha256": candidate.get("sha256"),
        },
        "restore_checkpoint": {
            "path": rel(restore_checkpoint),
            "present": restore_checkpoint.exists(),
        },
        "readiness": readiness,
        "commands": {
            "colab": {
                "preferred": True,
                "argv": colab,
                "shell": multiline_shell(colab),
            },
            "local_rocm": {
                "preferred": False,
                "argv": local,
                "shell": multiline_shell(local),
            },
        },
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
    }
    if not restore_checkpoint.exists():
        payload["status"] = "HOLD_PHASE2_RESTORE_CHECKPOINT_MISSING"

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
