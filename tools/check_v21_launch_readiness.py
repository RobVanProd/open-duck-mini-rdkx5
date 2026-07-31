#!/usr/bin/env python3
"""Check whether the explicit V21 soft-prior Colab run is ready to launch.

This is a read-only preflight. It does not start Colab work, train, deploy,
SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "V21_LAUNCH_READINESS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "v21_launch_readiness.json"
DEFAULT_SESSION = "open-duck-l4"
DEFAULT_SOFT_PRIOR_CONFIG = ROOT / "outputs" / "analysis" / "soft_prior_fragment_config.json"
DEFAULT_V21_PLAN_JSON = ROOT / "outputs" / "analysis" / "staged_curriculum_training_plan_v21.json"
DEFAULT_HANDOFF_DIR = ROOT.parent / "cuda_colab_handoff_v21"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run(command: list[str], cwd: Path, timeout_s: int = 30) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
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
            "timeout_s": timeout_s,
        }


def git_clean(repo: Path) -> dict[str, Any]:
    result = run(["git", "status", "--porcelain"], repo)
    dirty = bool(result.get("stdout", "").strip())
    return {
        "repo": str(repo),
        "ok": result["ok"] and not dirty,
        "dirty": dirty,
        "status": result.get("stdout", ""),
        "error": result.get("stderr", ""),
    }


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:  # noqa: BLE001 - report as readiness evidence.
        return None, f"{type(exc).__name__}: {exc}"


def check_soft_prior_config(path: Path) -> dict[str, Any]:
    payload, error = load_json(path)
    if payload is None:
        return {"path": str(path), "ok": False, "error": error}
    prior = payload.get("prior") or {}
    action_mean = prior.get("action_mean") or []
    joint_indices = prior.get("joint_indices") or []
    return {
        "path": str(path),
        "ok": bool(action_mean and joint_indices),
        "dataset_id": payload.get("dataset_id"),
        "window_len": prior.get("window_len"),
        "rows": len(action_mean),
        "joint_indices": joint_indices,
    }


def check_v21_plan(path: Path) -> dict[str, Any]:
    payload, error = load_json(path)
    if payload is None:
        return {"path": str(path), "ok": False, "error": error}
    phases = payload.get("phases") or []
    phase_summaries = []
    for phase in phases:
        command = phase.get("command") or []
        phase_summaries.append(
            {
                "name": phase.get("name"),
                "soft_prior_config_json": phase.get("soft_prior_config_json"),
                "soft_prior_scale": phase.get("soft_prior_scale"),
                "phase_gate_bridge_mode": phase.get("phase_gate_bridge_mode"),
                "has_enable_soft_prior_flag": "--enable-soft-prior" in command,
            }
        )
    expected = (
        payload.get("recipe") == "movement_bootstrap_v21"
        and len(phases) == 2
        and all(item["has_enable_soft_prior_flag"] for item in phase_summaries)
        and [item["phase_gate_bridge_mode"] for item in phase_summaries]
        == ["vanilla", "fitted"]
    )
    return {
        "path": str(path),
        "ok": expected,
        "status": payload.get("status"),
        "recipe": payload.get("recipe"),
        "phase_gate_command_x": payload.get("phase_gate_command_x"),
        "phases": phase_summaries,
    }


def check_playground_patch(playground: Path) -> dict[str, Any]:
    joystick = playground / "playground" / "open_duck_mini_v2" / "joystick.py"
    runner = playground / "playground" / "open_duck_mini_v2" / "runner.py"
    missing = [str(path) for path in (joystick, runner) if not path.exists()]
    if missing:
        return {"ok": False, "missing": missing}
    joystick_text = joystick.read_text()
    runner_text = runner.read_text()
    checks = {
        "joystick_soft_prior_config": "soft_prior=config_dict.create(" in joystick_text,
        "joystick_soft_prior_reward": '"soft_prior": info["soft_prior_cost"]' in joystick_text,
        "runner_enable_soft_prior_arg": "--enable_soft_prior" in runner_text,
        "runner_soft_prior_config_arg": "--soft_prior_config_json" in runner_text,
    }
    return {"ok": all(checks.values()), "checks": checks}


def check_colab_session(session: str) -> dict[str, Any]:
    status = run(["colab", "status", "-s", session], ROOT, timeout_s=30)
    text = (status.get("stdout") or "") + (status.get("stderr") or "")
    active = status["ok"] and "not found" not in text.lower()
    return {
        "session": session,
        "ok": active,
        "returncode": status.get("returncode"),
        "text": text.strip(),
    }


def check_pr(repo: str, number: int) -> dict[str, Any]:
    result = run(
        [
            "gh",
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "state,isDraft,mergeable,statusCheckRollup,headRefName",
        ],
        ROOT,
        timeout_s=60,
    )
    if not result["ok"]:
        return {"repo": repo, "number": number, "ok": False, "error": result["stderr"]}
    payload = json.loads(result["stdout"])
    checks = payload.get("statusCheckRollup") or []
    failures = [
        item
        for item in checks
        if item.get("status") == "COMPLETED" and item.get("conclusion") != "SUCCESS"
    ]
    pending = [item for item in checks if item.get("status") != "COMPLETED"]
    return {
        "repo": repo,
        "number": number,
        "ok": payload.get("state") == "OPEN" and not failures and not pending,
        "state": payload.get("state"),
        "isDraft": payload.get("isDraft"),
        "mergeable": payload.get("mergeable"),
        "headRefName": payload.get("headRefName"),
        "check_count": len(checks),
        "failures": failures,
        "pending": pending,
    }


def check_single_cell_fallback() -> dict[str, Any]:
    generator = ROOT / "tools" / "print_cuda_colab_cell.py"
    if not generator.exists():
        return {"ok": False, "error": f"missing generator: {generator}"}
    text = generator.read_text()
    checks = {
        "has_staged_curriculum_v21_arg": "--staged-curriculum-v21" in text,
        "runs_staged_planner": "plan_staged_curriculum_training.py" in text,
        "uses_v21_recipe": "movement_bootstrap_v21" in text,
        "packages_staged_runs": "open_duck_staged_runs" in text,
    }
    return {"ok": all(checks.values()), "checks": checks, "path": str(generator)}


def launch_command(session: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--session",
        session,
        "--workflow",
        "staged-curriculum",
        "--staged-recipe",
        "movement_bootstrap_v21",
        "--staged-phase-gate-seeds",
        "0-3",
        "--staged-phase-gate-command-x",
        "0.04",
        "--staged-phase-gate-bridge-mode",
        "vanilla",
        "--staged-phase-gate-freeze-check",
        "--run",
    ]


def fallback_command(handoff_dir: Path) -> list[str]:
    return [
        "python3",
        "tools/print_cuda_colab_cell.py",
        "--staged-curriculum-v21",
        "--rdk-branch",
        "codex/colab-cli-cuda-workflow",
        "--playground-branch",
        "codex/forward-progress-reward",
        "--handoff-dir",
        str(handoff_dir),
    ]


def status_from_checks(checks: dict[str, Any]) -> str:
    required = [
        checks["soft_prior_config"]["ok"],
        checks["v21_plan"]["ok"],
        checks["playground_patch"]["ok"],
        checks["single_cell_fallback"]["ok"],
    ]
    if not all(required):
        return "HOLD_V21_LOCAL_PRECHECK"
    if not checks["colab_session"]["ok"]:
        return "HOLD_COLAB_SESSION_MISSING"
    return "PASS_V21_READY_TO_LAUNCH"


def write_reports(payload: dict[str, Any], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# V21 Launch Readiness",
        "",
        f"status: `{payload['status']}`",
        f"timestamp: `{payload['timestamp']}`",
        "",
        "## Required Checks",
        "",
        "| check | status | detail |",
        "|---|---|---|",
        (
            f"| soft prior config | `{payload['soft_prior_config']['ok']}` | "
            f"{payload['soft_prior_config'].get('rows')} rows, "
            f"dataset `{payload['soft_prior_config'].get('dataset_id')}` |"
        ),
        (
            f"| V21 plan | `{payload['v21_plan']['ok']}` | "
            f"recipe `{payload['v21_plan'].get('recipe')}`, "
            f"phase gate x `{payload['v21_plan'].get('phase_gate_command_x')}` |"
        ),
        (
            f"| Playground soft-prior patch | `{payload['playground_patch']['ok']}` | "
            f"default-off hook present |"
        ),
        (
            f"| Colab session | `{payload['colab_session']['ok']}` | "
            f"{payload['colab_session'].get('text') or 'active'} |"
        ),
        (
            f"| browser-Colab fallback | `{payload['single_cell_fallback']['ok']}` | "
            f"`tools/print_cuda_colab_cell.py --staged-curriculum-v21` |"
        ),
        "",
        "## Launch Command",
        "",
        "```bash",
        " ".join(payload["launch_command"]),
        "```",
        "",
        "## Browser-Colab Fallback",
        "",
        "Use this when `google-colab-cli` cannot see the session but a browser",
        "Colab notebook is already authenticated:",
        "",
        "```bash",
        " ".join(payload["fallback_command"]),
        "```",
        "",
        "Then open the generated notebook and run its single cell.",
        "",
        "## Safety",
        "",
        "This preflight did not start training, SSH, deploy, change robot runtime",
        "behavior, or touch the robot.",
    ]
    if payload.get("prs"):
        lines.extend(["", "## PR Status", ""])
        for item in payload["prs"]:
            lines.append(
                f"- `{item['repo']}#{item['number']}` ok=`{item['ok']}` "
                f"state=`{item.get('state')}` draft=`{item.get('isDraft')}` "
                f"mergeable=`{item.get('mergeable')}` checks=`{item.get('check_count')}`"
            )
    output_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default=DEFAULT_SESSION)
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--soft-prior-config", type=Path, default=DEFAULT_SOFT_PRIOR_CONFIG)
    parser.add_argument("--v21-plan-json", type=Path, default=DEFAULT_V21_PLAN_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--handoff-dir", type=Path, default=DEFAULT_HANDOFF_DIR)
    parser.add_argument("--skip-pr-checks", action="store_true")
    args = parser.parse_args()

    payload: dict[str, Any] = {
        "timestamp": timestamp(),
        "robot_touched": False,
        "deploy_performed": False,
        "training_started": False,
        "soft_prior_config": check_soft_prior_config(args.soft_prior_config),
        "v21_plan": check_v21_plan(args.v21_plan_json),
        "playground_patch": check_playground_patch(args.playground_path),
        "single_cell_fallback": check_single_cell_fallback(),
        "colab_session": check_colab_session(args.session),
        "rdk_git": git_clean(ROOT),
        "playground_git": git_clean(args.playground_path),
        "launch_command": launch_command(args.session),
        "fallback_command": fallback_command(args.handoff_dir),
    }
    if not args.skip_pr_checks:
        payload["prs"] = [
            check_pr("RobVanProd/open-duck-mini-rdkx5", 74),
            check_pr("RobVanProd/Open_Duck_Playground", 4),
        ]
    payload["status"] = status_from_checks(payload)
    write_reports(payload, args.output_md, args.output_json)
    print(payload["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
