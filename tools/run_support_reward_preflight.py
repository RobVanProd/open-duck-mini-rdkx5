#!/usr/bin/env python3
"""Run a short support-contact reward activation preflight.

This helper wraps one tiny closed-loop eval and
``tools/audit_reward_term_activation.py``. It is offline-only: no training, SSH,
deployment, robot access, or runtime behavior changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
DEFAULT_FIT_JSON = ROOT / "outputs" / "analysis" / "actuator_response_fit.json"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"
DEFAULT_PLAN = (
    ROOT / "outputs" / "analysis" / "movement_bootstrap_v24_transition_propulsion_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "support_reward_preflight"


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def run_command(command: list[str], *, cwd: Path, timeout_s: int) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_s,
        check=False,
    )
    return {
        "command": command,
        "command_shell": shell_join(command),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-8000:],
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Support Reward Preflight",
        "",
        f"status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- reward overrides: `{summary['reward_overrides_json']}`",
        f"- phase: `{summary['reward_overrides_phase']}`",
        f"- command_x: `{summary['command_x']}`",
        f"- duration_s: `{summary['duration_s']}`",
        f"- seed: `{summary['seed']}`",
        f"- bridge: `{summary['bridge_mode']}`",
        f"- jax_platform: `{summary['jax_platform']}`",
        "",
        "## Results",
        "",
        f"- eval_returncode: `{summary['eval']['returncode']}`",
        f"- audit_returncode: `{summary['audit']['returncode']}`",
        f"- audit_status: `{summary.get('audit_status')}`",
        f"- eval_json: `{summary['eval_json']}`",
        f"- audit_json: `{summary['audit_json']}`",
        f"- audit_md: `{summary['audit_md']}`",
        "",
    ]
    audit = summary.get("audit_payload") or {}
    term_rows = audit.get("term_audit") or []
    if term_rows:
        lines.extend(
            [
                "## Term Audit",
                "",
                "| term | scale | observed files | max abs stat | status |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for row in term_rows:
            max_abs = row.get("max_abs_stat")
            lines.append(
                "| {term} | {scale:.4f} | {count} | {max_abs} | `{status}` |".format(
                    term=row.get("term"),
                    scale=float(row.get("scale") or 0.0),
                    count=row.get("observed_count"),
                    max_abs="NA" if max_abs is None else f"{float(max_abs):.4f}",
                    status=row.get("status"),
                )
            )
        lines.append("")
    lines.extend(
        [
            "## Safety",
            "",
            "- robot_tests_run: `false`",
            "- ssh_run: `false`",
            "- deploy_run: `false`",
            "- training_run: `false`",
            "- runtime_behavior_changed: `false`",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--fit-json", type=Path, default=DEFAULT_FIT_JSON)
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--env-python", type=Path, default=DEFAULT_ENV_PYTHON)
    parser.add_argument("--reward-overrides-json", type=Path, default=DEFAULT_PLAN)
    parser.add_argument(
        "--reward-overrides-phase",
        default="phase1_transition_propulsion_probe",
    )
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--bridge-mode", default="vanilla")
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout-s", type=int, default=600)
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_cmd = [
        str(args.env_python),
        str(ROOT / "tools" / "eval_policy_with_actuator_bridge.py"),
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        str(args.policy),
        "--fit-json",
        str(args.fit_json),
        "--playground-path",
        str(args.playground_path),
        "--env-python",
        str(args.env_python),
        "--command-x",
        str(args.command_x),
        "--duration",
        str(args.duration),
        "--seed",
        str(args.seed),
        "--bridge-mode",
        args.bridge_mode,
        "--jax-platform",
        args.jax_platform,
        "--sim-preflight-timeout-s",
        str(args.timeout_s),
        "--closed-loop-timeout-s",
        str(args.timeout_s),
        "--reward-overrides-json",
        str(args.reward_overrides_json),
        "--reward-overrides-phase",
        args.reward_overrides_phase,
        "--output-dir",
        str(output_dir / "eval"),
    ]
    eval_result = run_command(eval_cmd, cwd=ROOT, timeout_s=args.timeout_s + 120)

    audit_md = output_dir / "REWARD_TERM_ACTIVATION.md"
    audit_json = output_dir / "reward_term_activation.json"
    audit_cmd = [
        sys.executable,
        str(ROOT / "tools" / "audit_reward_term_activation.py"),
        "--reward-overrides-json",
        str(args.reward_overrides_json),
        "--reward-overrides-phase",
        args.reward_overrides_phase,
        "--eval-path",
        str(output_dir / "eval"),
        "--output-md",
        str(audit_md),
        "--output-json",
        str(audit_json),
    ]
    audit_result = (
        run_command(audit_cmd, cwd=ROOT, timeout_s=120)
        if eval_result["returncode"] == 0
        else {
            "command": audit_cmd,
            "command_shell": shell_join(audit_cmd),
            "returncode": None,
            "stdout_tail": "skipped because eval failed",
        }
    )
    audit_payload = load_json(audit_json) if audit_json.exists() else {}
    audit_status = audit_payload.get("status")
    status = audit_status or "HOLD_PREFLIGHT_EVAL_FAILED"
    if eval_result["returncode"] != 0:
        status = "HOLD_PREFLIGHT_EVAL_FAILED"
    elif audit_result["returncode"] != 0:
        status = "HOLD_PREFLIGHT_AUDIT_FAILED"

    summary = {
        "status": status,
        "reward_overrides_json": str(args.reward_overrides_json),
        "reward_overrides_phase": args.reward_overrides_phase,
        "command_x": args.command_x,
        "duration_s": args.duration,
        "seed": args.seed,
        "bridge_mode": args.bridge_mode,
        "jax_platform": args.jax_platform,
        "eval": eval_result,
        "audit": audit_result,
        "audit_status": audit_status,
        "eval_json": str(output_dir / "eval" / "closed_loop_actuator_bridge_eval.json"),
        "audit_json": str(audit_json),
        "audit_md": str(audit_md),
        "audit_payload": audit_payload,
        "robot_tests_run": False,
        "ssh_run": False,
        "deploy_run": False,
        "training_run": False,
        "runtime_behavior_changed": False,
    }
    summary_json = output_dir / "support_reward_preflight.json"
    summary_md = output_dir / "SUPPORT_REWARD_PREFLIGHT.md"
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_summary_md(summary_md, summary)
    print(summary_md)
    print(summary_json)
    print(status)
    return 0 if status in {"PASS_REWARD_TERMS_OBSERVED", "WARN_REWARD_TERMS_ZERO"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
