#!/usr/bin/env python3
"""Run one live-oracle DAgger data-collection iteration.

This closes the loop that static DAgger passes did not close:

1. roll out the current student with full-observation traces
2. query the source-VX selector oracle on those student-visited states
3. build per-command correction manifests
4. merge them with prior manifests for the next student fit

The tool is offline-only. It does not train PPO, deploy, SSH, or touch the
robot. By default it writes a command plan; pass --run to execute.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def run_command(command: list[str], *, cwd: Path, run: bool) -> dict[str, Any]:
    row: dict[str, Any] = {
        "command": [str(part) for part in command],
        "command_shell": shell_join(command),
        "cwd": str(cwd),
        "ran": bool(run),
    }
    if not run:
        row["returncode"] = None
        return row
    proc = subprocess.run(
        [str(part) for part in command],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    row["returncode"] = proc.returncode
    row["stdout_tail"] = proc.stdout[-12000:]
    return row


def parse_seed_count(seed_expr: str) -> int:
    total = 0
    for part in str(seed_expr).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            total += abs(end - start) + 1
        else:
            total += 1
    return total


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Live-Oracle DAgger Iteration",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is one offline live-oracle DAgger iteration plan/run. It does not",
        "SSH, deploy, train PPO, run robot tests, or change runtime behavior.",
        "",
        "## Config",
        "",
        f"- iteration: `{payload['iteration']}`",
        f"- rung: `{payload['rung']}`",
        f"- student_policy: `{payload['student_policy']}`",
        f"- teacher_manifest: `{payload['teacher_manifest']}`",
        f"- command_x: `{payload['command_x']}`",
        f"- duration_s: `{payload['duration_s']}`",
        f"- x008_seeds: `{payload['x008_seeds']}`",
        f"- x0_seeds: `{payload['x0_seeds']}`",
        f"- run: `{payload['run']}`",
        "",
        "## Outputs",
        "",
        f"- output_dir: `{payload['output_dir']}`",
        f"- x008_rollout_dir: `{payload['x008_rollout_dir']}`",
        f"- x0_rollout_dir: `{payload['x0_rollout_dir']}`",
        f"- x008_relabel_manifest: `{payload['x008_relabel_manifest_json']}`",
        f"- x0_relabel_manifest: `{payload['x0_relabel_manifest_json']}`",
        f"- aggregate_manifest: `{payload['aggregate_manifest_json']}`",
        "",
        "## Commands",
        "",
    ]
    for index, step in enumerate(payload["steps"], start=1):
        status = "not_run" if not step["ran"] else f"returncode={step['returncode']}"
        lines.extend(
            [
                f"### {index}. {step['name']}",
                "",
                f"status: `{status}`",
                "",
                "```bash",
                step["command_shell"],
                "```",
                "",
            ]
        )
        if step.get("stdout_tail"):
            lines.extend(["stdout tail:", "", "```text", step["stdout_tail"], "```", ""])
    lines.extend(
        [
            "## Gate",
            "",
            "- A dry run only proves the live-oracle iteration is planned.",
            "- A run that completes produces aggregated correction data for the next",
            "  student fit.",
            "- No output from this tool is a deployable candidate; candidates must",
            "  pass `docs/EVALUATOR_RECONCILIATION.md`'s canonical strict gate.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-policy", required=True)
    parser.add_argument(
        "--teacher-manifest",
        default="outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json",
    )
    parser.add_argument(
        "--base-manifest",
        action="append",
        default=["outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json"],
    )
    parser.add_argument("--iteration", type=int, default=0)
    parser.add_argument("--rung", default="frame_stack_k4_precheck")
    parser.add_argument("--output-dir", default="outputs/analysis/live_oracle_dagger_phase_student/iter_000")
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--x008-seeds", default="0-7")
    parser.add_argument("--x0-seeds", default="0-1")
    parser.add_argument("--bridge-mode", default="fitted")
    parser.add_argument("--task", default="flat_terrain_backlash")
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--teacher-model-kind", choices=["blend", "source_vx_blend"], default="source_vx_blend")
    parser.add_argument("--knn-k", type=int, default=5)
    parser.add_argument("--blend-alpha", type=float, default=0.80)
    parser.add_argument("--vx-blend-alpha", type=float, default=1.0)
    parser.add_argument("--vx-blend-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--source-vx-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--alt-exclude-source-regex", default="seed_004")
    parser.add_argument("--gate-aware-sample-weights", action="store_true", default=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument(
        "--output-md",
        default=None,
        help="Defaults to <output-dir>/LIVE_ORACLE_DAGGER_ITERATION.md",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Defaults to <output-dir>/live_oracle_dagger_iteration.json",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    x008_rollout_dir = output_dir / "rollouts_x008"
    x0_rollout_dir = output_dir / "rollouts_x0"
    x008_relabel_dir = output_dir / "relabel_x008"
    x0_relabel_dir = output_dir / "relabel_x0"
    x008_manifest_md = output_dir / "LIVE_ORACLE_DAGGER_X008_MANIFEST.md"
    x008_manifest_json = output_dir / "live_oracle_dagger_x008_manifest.json"
    x0_manifest_md = output_dir / "LIVE_ORACLE_DAGGER_X0_MANIFEST.md"
    x0_manifest_json = output_dir / "live_oracle_dagger_x0_manifest.json"
    aggregate_md = output_dir / "LIVE_ORACLE_DAGGER_AGGREGATE_MANIFEST.md"
    aggregate_json = output_dir / "live_oracle_dagger_aggregate_manifest.json"
    report_md = Path(args.output_md) if args.output_md else output_dir / "LIVE_ORACLE_DAGGER_ITERATION.md"
    report_json = Path(args.output_json) if args.output_json else output_dir / "live_oracle_dagger_iteration.json"

    seed_x008_count = parse_seed_count(args.x008_seeds)
    seed_x0_count = parse_seed_count(args.x0_seeds)
    trace_x008 = args.x008_seeds
    trace_x0 = args.x0_seeds

    common_eval = [
        args.env_python,
        "tools/run_candidate_seed_sweep.py",
        "--policies",
        f"student={args.student_policy}",
        "--fit-json",
        args.fit_json,
        "--playground-path",
        args.playground_path,
        "--env-python",
        args.env_python,
        "--duration",
        str(args.duration),
        "--bridge-mode",
        args.bridge_mode,
        "--task",
        args.task,
        "--jax-platform",
        args.jax_platform,
        "--trace-full-obs",
        "--run",
    ]
    x008_eval = [
        *common_eval,
        "--command-x",
        str(args.command_x),
        "--seeds",
        args.x008_seeds,
        "--trace-seeds",
        trace_x008,
        "--output-dir",
        str(x008_rollout_dir),
        "--output-md",
        str(output_dir / "LIVE_ORACLE_DAGGER_X008_ROLLOUT.md"),
        "--output-json",
        str(output_dir / "live_oracle_dagger_x008_rollout.json"),
    ]
    x0_eval = [
        *common_eval,
        "--command-x",
        "0.0",
        "--seeds",
        args.x0_seeds,
        "--trace-seeds",
        trace_x0,
        "--output-dir",
        str(x0_rollout_dir),
        "--output-md",
        str(output_dir / "LIVE_ORACLE_DAGGER_X0_ROLLOUT.md"),
        "--output-json",
        str(output_dir / "live_oracle_dagger_x0_rollout.json"),
    ]

    common_relabel = [
        "python3",
        "tools/relabel_bc_trace_actions.py",
        "--teacher-manifest",
        args.teacher_manifest,
        "--teacher-model-kind",
        args.teacher_model_kind,
        "--knn-k",
        str(args.knn_k),
        "--blend-alpha",
        str(args.blend_alpha),
        "--vx-blend-alpha",
        str(args.vx_blend_alpha),
        "--vx-blend-threshold-m-s",
        str(args.vx_blend_threshold_m_s),
        "--source-vx-threshold-m-s",
        str(args.source_vx_threshold_m_s),
        "--alt-exclude-source-regex",
        args.alt_exclude_source_regex,
        "--output-parent-depth",
        "3",
    ]
    if args.gate_aware_sample_weights:
        common_relabel.append("--gate-aware-sample-weights")

    x008_relabel = [
        *common_relabel,
        "--trace-glob",
        str(x008_rollout_dir / "student" / "seed_*" / "trace.jsonl"),
        "--output-trace-dir",
        str(x008_relabel_dir),
        "--output-md",
        str(output_dir / "LIVE_ORACLE_DAGGER_X008_RELABEL.md"),
        "--output-json",
        str(output_dir / "live_oracle_dagger_x008_relabel.json"),
        "--gate-command-x",
        str(args.command_x),
    ]
    x0_relabel = [
        *common_relabel,
        "--trace-glob",
        str(x0_rollout_dir / "student" / "seed_*" / "trace.jsonl"),
        "--output-trace-dir",
        str(x0_relabel_dir),
        "--output-md",
        str(output_dir / "LIVE_ORACLE_DAGGER_X0_RELABEL.md"),
        "--output-json",
        str(output_dir / "live_oracle_dagger_x0_relabel.json"),
        "--gate-command-x",
        "0.0",
    ]

    x008_manifest = [
        "python3",
        "tools/build_bc_manifest_from_traces.py",
        "--trace-glob",
        str(x008_relabel_dir / "student" / "seed_*" / "trace.jsonl"),
        "--output-md",
        str(x008_manifest_md),
        "--output-json",
        str(x008_manifest_json),
        "--command-x",
        str(args.command_x),
        "--default-mode",
        f"live_oracle_iter_{args.iteration}_x008",
        "--source-parent-depth",
        "3",
        "--min-entries",
        str(seed_x008_count),
    ]
    x0_manifest = [
        "python3",
        "tools/build_bc_manifest_from_traces.py",
        "--trace-glob",
        str(x0_relabel_dir / "student" / "seed_*" / "trace.jsonl"),
        "--output-md",
        str(x0_manifest_md),
        "--output-json",
        str(x0_manifest_json),
        "--command-x",
        "0.0",
        "--default-mode",
        f"live_oracle_iter_{args.iteration}_x0",
        "--source-parent-depth",
        "3",
        "--min-entries",
        str(seed_x0_count),
    ]
    aggregate = [
        "python3",
        "tools/filter_bc_manifest.py",
    ]
    for manifest in [*args.base_manifest, str(x008_manifest_json), str(x0_manifest_json)]:
        aggregate.extend(["--manifest", manifest])
    aggregate.extend(
        [
            "--output-md",
            str(aggregate_md),
            "--output-json",
            str(aggregate_json),
            "--min-entries",
            str(len(args.base_manifest) + seed_x008_count + seed_x0_count),
            "--min-samples",
            "1",
            "--min-mean-vx",
            "-10",
            "--max-vy-abs-p95",
            "999",
            "--max-pitch-abs-p95",
            "999",
            "--min-base-height",
            "-10",
            "--max-sent-velocity-p95",
            "999",
            "--max-tracking-p95",
            "999",
        ]
    )

    commands = [
        ("x008_student_rollout", x008_eval),
        ("x0_student_rollout", x0_eval),
        ("x008_live_oracle_relabel", x008_relabel),
        ("x0_live_oracle_relabel", x0_relabel),
        ("x008_manifest", x008_manifest),
        ("x0_manifest", x0_manifest),
        ("aggregate_manifest", aggregate),
    ]
    steps = []
    status = "PASS_LIVE_ORACLE_DAGGER_ITERATION_DRY_RUN"
    for name, command in commands:
        row = run_command(command, cwd=ROOT, run=args.run)
        row["name"] = name
        steps.append(row)
        if args.run and row.get("returncode") != 0:
            status = "HOLD_LIVE_ORACLE_DAGGER_ITERATION_FAILED"
            break
    else:
        if args.run:
            status = "PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY"

    payload = {
        "status": status,
        "iteration": int(args.iteration),
        "rung": args.rung,
        "student_policy": args.student_policy,
        "teacher_manifest": args.teacher_manifest,
        "base_manifests": args.base_manifest,
        "command_x": float(args.command_x),
        "duration_s": float(args.duration),
        "x008_seeds": args.x008_seeds,
        "x0_seeds": args.x0_seeds,
        "run": bool(args.run),
        "output_dir": str(output_dir),
        "x008_rollout_dir": str(x008_rollout_dir),
        "x0_rollout_dir": str(x0_rollout_dir),
        "x008_relabel_manifest_json": str(x008_manifest_json),
        "x0_relabel_manifest_json": str(x0_manifest_json),
        "aggregate_manifest_json": str(aggregate_json),
        "steps": steps,
    }
    write_json(report_json, payload)
    write_markdown(report_md, payload)
    print(status)
    print(f"wrote {report_md}")
    print(f"wrote {report_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
