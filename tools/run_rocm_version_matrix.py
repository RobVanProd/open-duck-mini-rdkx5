#!/usr/bin/env python3
"""Run repeatable disposable ROCm/MJX version-matrix probes.

This tool intentionally creates throwaway envs instead of mutating the known
local Open Duck Playground env. It defaults to dry-run mode and prints the exact
commands it would run.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_ROOT = ROOT.parent / "envs"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs" / "analysis" / "rocm_mjx_version_matrix_auto"
DEFAULT_POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
DEFAULT_FIT_JSON = ROOT / "outputs" / "analysis" / "actuator_response_fit.json"


@dataclass(frozen=True)
class MatrixCase:
    name: str
    env_name: str
    description: str
    package_specs: tuple[str, ...]


BASE_ROCM_PACKAGES = (
    "jax[rocm7]==0.8.2",
    "jaxlib==0.8.2",
    "onnxruntime",
    "ml-collections",
    "numpy",
    "matplotlib",
    "mediapy",
)


CASES: dict[str, MatrixCase] = {
    "playground005": MatrixCase(
        name="playground005",
        env_name="open-duck-playground-rocm-playground005",
        description="ROCm JAX 0.8.2, current MuJoCo/MJX range, playground==0.0.5",
        package_specs=BASE_ROCM_PACKAGES
        + (
            "mujoco>=3.2.7,<3.10",
            "mujoco-mjx>=3.2.7",
            "playground==0.0.5",
        ),
    ),
    "mujoco337": MatrixCase(
        name="mujoco337",
        env_name="open-duck-playground-rocm-mujoco337",
        description="ROCm JAX 0.8.2, MuJoCo/MJX 3.3.7, playground==0.0.5",
        package_specs=BASE_ROCM_PACKAGES
        + (
            "mujoco==3.3.7",
            "mujoco-mjx==3.3.7",
            "playground==0.0.5",
        ),
    ),
    "mujoco327": MatrixCase(
        name="mujoco327",
        env_name="open-duck-playground-rocm-mujoco327",
        description="ROCm JAX 0.8.2, MuJoCo/MJX 3.2.7, playground==0.0.5",
        package_specs=BASE_ROCM_PACKAGES
        + (
            "mujoco==3.2.7",
            "mujoco-mjx==3.2.7",
            "playground==0.0.5",
        ),
    ),
}


def shell_join(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(item)) for item in command)


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def run(command: Sequence[str], *, cwd: Path | None = None, timeout_s: int | None = None) -> subprocess.CompletedProcess[str]:
    print(f">>> {shell_join(command)}")
    return subprocess.run(
        list(map(str, command)),
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_s,
    )


def command_plan_for_case(args: argparse.Namespace, case: MatrixCase) -> list[list[str]]:
    env_dir = args.env_root / case.env_name
    python = env_dir / "bin" / "python"
    commands: list[list[str]] = []
    if args.use_uv:
        commands.append(["uv", "venv", "--python", args.python, str(env_dir)])
        commands.append(
            ["uv", "pip", "install", "--python", str(python), *case.package_specs]
        )
        commands.append(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--no-deps",
                "-e",
                str(args.playground_path),
            ]
        )
    else:
        commands.append([args.python, "-m", "venv", str(env_dir)])
        commands.append([str(python), "-m", "pip", "install", "-U", "pip"])
        commands.append([str(python), "-m", "pip", "install", *case.package_specs])
        commands.append(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-deps",
                "-e",
                str(args.playground_path),
            ]
        )
    commands.append(
        [
            str(python),
            str(ROOT / "tools" / "isolate_rocm_mjx_failure.py"),
            "--playground-path",
            str(args.playground_path),
            "--env-python",
            str(python),
            "--policy",
            str(args.policy),
            "--fit-json",
            str(args.fit_json),
            "--output-dir",
            str(args.output_root / case.name),
            "--command-x",
            str(args.command_x),
            "--steps",
            args.steps,
            "--platforms",
            args.platforms,
            "--subtests",
            args.subtests,
            "--timeout-s",
            str(args.timeout_s),
        ]
    )
    return commands


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def metadata_for_env(python: Path) -> dict[str, Any]:
    code = """
import importlib.metadata as md
import json
names = [
    "jax",
    "jaxlib",
    "jax-rocm7-pjrt",
    "jax-rocm7-plugin",
    "mujoco",
    "mujoco-mjx",
    "playground",
    "numpy",
    "onnxruntime",
    "ml_collections",
]
out = {}
for name in names:
    try:
        out[name] = md.version(name)
    except Exception as exc:
        out[name] = f"{type(exc).__name__}: {exc}"
print(json.dumps(out, sort_keys=True))
"""
    result = run([str(python), "-c", code], timeout_s=30)
    if result.returncode != 0:
        return {"error": result.stderr.strip() or result.stdout.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout.strip()}


def summarize_case(args: argparse.Namespace, case: MatrixCase) -> dict[str, Any]:
    env_dir = args.env_root / case.env_name
    report_json = args.output_root / case.name / "rocm_mjx_runtime_isolation.json"
    payload = read_json(report_json) or {}
    assessment = payload.get("assessment") or {}
    capabilities = payload.get("capabilities") or {}
    return {
        "case": case.name,
        "description": case.description,
        "env_dir": str(env_dir),
        "package_specs": list(case.package_specs),
        "package_versions": metadata_for_env(env_dir / "bin" / "python")
        if (env_dir / "bin" / "python").exists()
        else {"status": "MISSING_ENV"},
        "evidence_dir": str(args.output_root / case.name),
        "gate_result": assessment.get("gate_result", "MISSING"),
        "smallest_failing_subtest": assessment.get("smallest_failing_subtest"),
        "capabilities": capabilities,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# ROCm / MJX Version Matrix Auto Runner",
        "",
        f"generated_at: `{summary['generated_at']}`",
        f"mode: `{summary['mode']}`",
        "",
        "## Purpose",
        "",
        "This report records disposable-env ROCm/MJX version-matrix probes. It",
        "does not mutate the known `../envs/open-duck-playground` env and does",
        "not involve robot hardware, SSH, deployment, or training.",
        "",
        "## Case Summary",
        "",
        "| case | env | mujoco/mjx | playground | gate | smallest failing subtest |",
        "|---|---|---|---|---|---|",
    ]
    for row in summary["cases"]:
        versions = row.get("package_versions") or {}
        mujoco = versions.get("mujoco", "UNKNOWN")
        mjx = versions.get("mujoco-mjx", "UNKNOWN")
        playground = versions.get("playground", "UNKNOWN")
        lines.append(
            f"| `{row['case']}` | `{row['env_dir']}` | `{mujoco}` / `{mjx}` | "
            f"`{playground}` | `{row['gate_result']}` | "
            f"`{row.get('smallest_failing_subtest')}` |"
        )
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for row in summary["cases"]:
        lines.append(f"### {row['case']}")
        lines.append("")
        lines.append(row["description"])
        lines.append("")
        lines.append("```bash")
        for command in row.get("commands", []):
            lines.append(command)
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "Promote a local ROCm package set only if the direct Open Duck",
            "`playground_direct_mjx_step` gate passes on GPU and the contract",
            "remains `obs=101`, `actions=14`. A CPU pass with a GPU direct-step",
            "hold is useful backend evidence, but it is not enough for local",
            "ROCm training.",
            "",
            "Known current interpretation: the already-run matrix did not clear",
            "the 7900 XTX Open Duck MJX direct-step blocker, so CUDA remains the",
            "full training/eval backend and local CPU remains the reduced",
            "correctness-check backend.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_summary(args: argparse.Namespace, cases: Sequence[MatrixCase], mode: str, commands_by_case: dict[str, list[str]]) -> tuple[Path, Path]:
    args.output_root.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "mode": mode,
        "inputs": {
            "playground_path": str(args.playground_path),
            "env_root": str(args.env_root),
            "output_root": str(args.output_root),
            "policy": str(args.policy),
            "fit_json": str(args.fit_json),
            "platforms": args.platforms,
            "subtests": args.subtests,
            "steps": args.steps,
            "timeout_s": args.timeout_s,
        },
        "cases": [],
    }
    for case in cases:
        row = summarize_case(args, case)
        row["commands"] = commands_by_case.get(case.name, [])
        summary["cases"].append(row)
    md_path = args.output_root / "ROCM_VERSION_MATRIX_AUTO.md"
    json_path = args.output_root / "rocm_version_matrix_auto.json"
    md_path.write_text(build_markdown(summary))
    json_path.write_text(json.dumps(summary, indent=2) + "\n")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create and run disposable ROCm/MJX Open Duck version-matrix probes."
    )
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--env-root", type=Path, default=DEFAULT_ENV_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--fit-json", type=Path, default=DEFAULT_FIT_JSON)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--cases",
        default="playground005,mujoco337,mujoco327",
        help=f"comma-separated cases from: {', '.join(sorted(CASES))}",
    )
    parser.add_argument("--platforms", default="gpu,cpu")
    parser.add_argument("--subtests", default="basic_jax,minimal_mjx_step,playground_contract_only,playground_reset,playground_direct_mjx_step")
    parser.add_argument("--steps", default="1")
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--timeout-s", type=int, default=120)
    parser.add_argument("--apply", action="store_true", help="Create envs and run probes.")
    parser.add_argument("--force-recreate", action="store_true", help="Remove an existing disposable matrix env before recreating it.")
    parser.add_argument("--no-uv", action="store_true", help="Use python -m venv and pip instead of uv.")
    args = parser.parse_args()

    args.playground_path = args.playground_path.expanduser().absolute()
    args.env_root = args.env_root.expanduser().absolute()
    args.output_root = args.output_root.expanduser().absolute()
    args.policy = args.policy.expanduser().absolute()
    args.fit_json = args.fit_json.expanduser().absolute()
    args.use_uv = not args.no_uv and shutil.which("uv") is not None

    case_names = split_csv(args.cases)
    unknown = [name for name in case_names if name not in CASES]
    if unknown:
        raise SystemExit(f"Unknown cases: {', '.join(unknown)}")
    selected = [CASES[name] for name in case_names]

    commands_by_case: dict[str, list[str]] = {}
    for case in selected:
        env_dir = args.env_root / case.env_name
        if args.force_recreate and not str(env_dir).startswith(str(args.env_root)):
            raise SystemExit(f"Refusing to remove suspicious env path: {env_dir}")
        commands = command_plan_for_case(args, case)
        commands_by_case[case.name] = [shell_join(command) for command in commands]
        print(f"\n=== {case.name}: {case.description} ===")
        for command in commands:
            print(shell_join(command))
        if not args.apply:
            continue
        if env_dir.exists():
            if args.force_recreate:
                print(f"Removing disposable env: {env_dir}")
                shutil.rmtree(env_dir)
            else:
                raise SystemExit(
                    f"{env_dir} already exists. Use --force-recreate or choose another case/env root."
                )
        for command in commands:
            result = run(command, cwd=ROOT, timeout_s=None)
            if result.stdout:
                print(result.stdout[-4000:], end="" if result.stdout.endswith("\n") else "\n")
            if result.stderr:
                print(result.stderr[-4000:], file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
            if result.returncode != 0:
                raise SystemExit(f"Command failed with return code {result.returncode}: {shell_join(command)}")

    mode = "apply" if args.apply else "dry-run"
    md_path, json_path = write_summary(args, selected, mode, commands_by_case)
    print(f"\nWrote {md_path}")
    print(f"Wrote {json_path}")
    if not args.apply:
        print("Dry-run only. Re-run with --apply to create disposable envs and run probes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
