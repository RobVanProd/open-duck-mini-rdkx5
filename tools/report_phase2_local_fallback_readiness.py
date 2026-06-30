#!/usr/bin/env python3
"""Report whether the local ROCm path is usable as Phase 2 fallback evidence.

This is a read-only diagnostic. It does not train, SSH, deploy, touch the
robot, modify Playground, or start a long eval. The A100/L4 Colab path remains
the preferred Phase 2 training path; this report only records whether the local
machine can safely run debug/fallback checks while Colab is unavailable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"
DEFAULT_PLAYGROUND_ROOT = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "PHASE2_LOCAL_FALLBACK_READINESS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "phase2_local_fallback_readiness.json"
PINNED_COLAB_JAX = "0.7.2"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run_command(command: list[str], timeout_s: int, cwd: Path = ROOT) -> dict[str, Any]:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        elapsed = time.monotonic() - start
        return {
            "command": command,
            "returncode": completed.returncode,
            "elapsed_s": round(elapsed, 3),
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "timed_out": False,
        }
    except FileNotFoundError as exc:
        elapsed = time.monotonic() - start
        return {
            "command": command,
            "returncode": None,
            "elapsed_s": round(elapsed, 3),
            "stdout": "",
            "stderr": f"FileNotFoundError: {exc}",
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        return {
            "command": command,
            "returncode": None,
            "elapsed_s": round(elapsed, 3),
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def parse_probe(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


def core_artifacts(workflow: str) -> dict[str, dict[str, Any]]:
    base_paths = {
        "phase2_candidate": ROOT
        / "policy"
        / "candidates"
        / "phase2_stagea2_seed5_recovery_command_gated_gain099_20260629"
        / "candidate.onnx",
        "corrected_bridge": ROOT / "outputs" / "analysis" / "actuator_response_fit_corrected_knee.json",
    }
    workflow_paths = {
        "phase2-z002-tracking-margin": {
            "restore_checkpoint": ROOT
            / "outputs"
            / "phase2_domain_randomization"
            / "stage_c0_terrain_z002_preserve_from_a2_gpu"
            / "smoke_20260628T103743Z_gpu"
            / "2026_06_28_064431_245760",
            "recipe": ROOT / "outputs" / "analysis" / "phase2_z002_tracking_margin_next_recipe.json",
        },
        "phase2-z005-support": {
            "restore_checkpoint": ROOT
            / "outputs"
            / "phase2_domain_randomization"
            / "stage_a2_preserve_narrow_flat_no_push_gpu"
            / "smoke_20260628T031553Z_gpu"
            / "2026_06_27_232221_491520",
            "recipe": ROOT / "outputs" / "analysis" / "phase2_z005_support_next_recipe.json",
        },
        "phase2-z0035-motion-floor": {
            "restore_checkpoint": ROOT
            / "outputs"
            / "phase2_domain_randomization"
            / "stage_a2_preserve_narrow_flat_no_push_gpu"
            / "smoke_20260628T031553Z_gpu"
            / "2026_06_27_232221_491520",
            "recipe": ROOT / "outputs" / "analysis" / "phase2_z0035_motion_floor_next_recipe.json",
        },
    }
    paths = {
        **base_paths,
        **workflow_paths.get(workflow, workflow_paths["phase2-z005-support"]),
    }
    if workflow not in workflow_paths:
        paths["workflow_warning"] = ROOT / f"UNKNOWN_WORKFLOW_{workflow}"
    return {
        name: {
            "path": rel(path),
            "exists": path.exists(),
            "kind": "directory" if path.is_dir() else "file",
        }
        for name, path in paths.items()
    }


def collect(args: argparse.Namespace) -> dict[str, Any]:
    # Do not resolve the venv Python symlink before execution. Python uses
    # argv[0] to discover the virtual environment; executing the resolved base
    # interpreter bypasses the venv site-packages.
    env_python = Path(args.env_python).expanduser()
    playground_root = Path(args.playground_root).expanduser().resolve()
    artifacts = core_artifacts(args.workflow)

    probe_code = r"""
import json
import os
import sys

payload = {"python": sys.executable, "python_version": sys.version.split()[0]}

try:
    import jax
    payload["jax_version"] = jax.__version__
    payload["jax_backend"] = jax.default_backend()
    payload["jax_devices"] = [str(device) for device in jax.devices()]
except Exception as exc:
    payload["jax_error"] = f"{type(exc).__name__}: {exc}"

try:
    import mujoco
    payload["mujoco_version"] = mujoco.__version__
except Exception as exc:
    payload["mujoco_error"] = f"{type(exc).__name__}: {exc}"

try:
    import mujoco_playground
    payload["mujoco_playground_file"] = getattr(mujoco_playground, "__file__", None)
except Exception as exc:
    payload["mujoco_playground_error"] = f"{type(exc).__name__}: {exc}"

for module in [
    "playground.open_duck_mini_v2.joystick",
    "playground.open_duck_mini_v2.constants",
]:
    try:
        __import__(module)
        payload[f"import:{module}"] = "PASS"
    except Exception as exc:
        payload[f"import:{module}"] = f"{type(exc).__name__}: {exc}"

payload["env"] = {
    key: os.environ.get(key)
    for key in [
        "JAX_PLATFORM_NAME",
        "XLA_PYTHON_CLIENT_PREALLOCATE",
        "XLA_PYTHON_CLIENT_MEM_FRACTION",
        "HSA_OVERRIDE_GFX_VERSION",
        "MUJOCO_GL",
    ]
}
print(json.dumps(payload, sort_keys=True))
"""

    env_status = "HOLD_ENV_PYTHON_MISSING"
    probe: dict[str, Any] = {}
    probe_result: dict[str, Any] | None = None
    if env_python.exists():
        env_status = "PASS_ENV_PYTHON_EXISTS"
        probe_result = run_command([str(env_python), "-c", probe_code], args.timeout_s)
        probe = parse_probe(probe_result.get("stdout", ""))
        if probe_result.get("timed_out"):
            env_status = "HOLD_ENV_PROBE_TIMEOUT"
        elif probe_result.get("returncode") != 0:
            env_status = "HOLD_ENV_PROBE_FAILED"

    help_result = run_command(
        [str(env_python), "tools/run_actuator_bridge_training_smoke.py", "--help"],
        args.timeout_s,
    ) if env_python.exists() else None

    colab_sessions = run_command(["colab", "sessions"], min(args.timeout_s, 30))
    colab_status = run_command(["colab", "status", "-s", args.session], min(args.timeout_s, 30))
    check_training = run_command(
        [str(env_python), "tools/check_training_env.py", "--playground-root", str(playground_root)],
        args.check_training_timeout_s,
    ) if env_python.exists() else None

    jax_version = probe.get("jax_version")
    backend = probe.get("jax_backend")
    devices = probe.get("jax_devices") or []
    gpu_visible = backend == "gpu" or any("rocm" in str(item).lower() or "gpu" in str(item).lower() for item in devices)
    imports_ok = all(
        probe.get(f"import:{module}") == "PASS"
        for module in [
            "playground.open_duck_mini_v2.joystick",
            "playground.open_duck_mini_v2.constants",
        ]
    )
    help_ok = bool(help_result and help_result.get("returncode") == 0 and not help_result.get("timed_out"))
    artifacts_ok = all(item["exists"] for item in artifacts.values())

    warnings: list[str] = []
    if jax_version and jax_version != PINNED_COLAB_JAX:
        warnings.append(
            f"local JAX is {jax_version}, not pinned Colab/CUDA {PINNED_COLAB_JAX}; treat local runs as fallback/debug unless they clear canonical gates"
        )
    if not gpu_visible:
        warnings.append("local JAX GPU/ROCm backend is not visible")
    if not imports_ok:
        warnings.append("Open Duck Playground imports are not all passing")
    if not help_ok:
        warnings.append("training smoke CLI help is not available in the local env")
    if not artifacts_ok:
        warnings.append("one or more Phase 2 core artifacts are missing")

    if env_status.startswith("HOLD") or not imports_ok or not help_ok or not artifacts_ok:
        status = "HOLD_LOCAL_FALLBACK_NOT_READY"
    elif warnings:
        status = "WARN_LOCAL_FALLBACK_DEBUG_ONLY"
    else:
        status = "PASS_LOCAL_FALLBACK_READY"

    return {
        "status": status,
        "workflow": args.workflow,
        "preferred_path": "A100/L4 Colab via run_colab_cli_cuda_workflow.py",
        "local_role": "fallback/debug evidence only unless it clears the same canonical gates",
        "session": args.session,
        "env_python": str(env_python),
        "playground_root": str(playground_root),
        "pinned_colab_jax_version": PINNED_COLAB_JAX,
        "env_status": env_status,
        "probe": probe,
        "probe_result": probe_result,
        "check_training_env": check_training,
        "training_smoke_help": help_result,
        "colab_sessions": colab_sessions,
        "colab_status": colab_status,
        "core_artifacts": artifacts,
        "gpu_visible": gpu_visible,
        "imports_ok": imports_ok,
        "training_smoke_help_ok": help_ok,
        "core_artifacts_ok": artifacts_ok,
        "warnings": warnings,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def short_output(result: dict[str, Any] | None, limit: int = 240) -> str:
    if not result:
        return "not run"
    if result.get("timed_out"):
        return f"timeout after {result.get('elapsed_s')}s"
    text = result.get("stdout") or result.get("stderr") or ""
    text = " ".join(text.split())
    if not text:
        text = f"returncode={result.get('returncode')}"
    return text[:limit]


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Local Fallback Readiness",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is a read-only diagnostic. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Summary",
        "",
        f"- workflow: `{payload['workflow']}`",
        f"- preferred_path: `{payload['preferred_path']}`",
        f"- local_role: `{payload['local_role']}`",
        f"- env_python: `{payload['env_python']}`",
        f"- playground_root: `{payload['playground_root']}`",
        f"- pinned_colab_jax_version: `{payload['pinned_colab_jax_version']}`",
        f"- local_jax_version: `{payload.get('probe', {}).get('jax_version')}`",
        f"- local_jax_backend: `{payload.get('probe', {}).get('jax_backend')}`",
        f"- local_jax_devices: `{payload.get('probe', {}).get('jax_devices')}`",
        f"- gpu_visible: `{payload['gpu_visible']}`",
        f"- imports_ok: `{payload['imports_ok']}`",
        f"- training_smoke_help_ok: `{payload['training_smoke_help_ok']}`",
        f"- core_artifacts_ok: `{payload['core_artifacts_ok']}`",
        "",
        "## Warnings",
        "",
    ]
    if payload["warnings"]:
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")

    lines.extend(["", "## Core Artifacts", "", "| artifact | exists | path |", "|---|---:|---|"])
    for name, item in payload["core_artifacts"].items():
        lines.append(f"| `{name}` | `{item['exists']}` | `{item['path']}` |")

    lines.extend(
        [
            "",
            "## Command Checks",
            "",
            f"- colab_sessions: `{short_output(payload.get('colab_sessions'))}`",
            f"- colab_status: `{short_output(payload.get('colab_status'))}`",
            f"- check_training_env: `{short_output(payload.get('check_training_env'))}`",
            f"- training_smoke_help: `{short_output(payload.get('training_smoke_help'))}`",
            "",
            "## Decision",
            "",
        ]
    )
    if payload["status"] == "PASS_LOCAL_FALLBACK_READY":
        lines.append("Local fallback is technically ready, but Colab remains the preferred promotion path.")
    elif payload["status"] == "WARN_LOCAL_FALLBACK_DEBUG_ONLY":
        lines.append(
            "Local fallback may be used for debug evidence only. Promotion still requires the canonical gates and version-aware review."
        )
    else:
        lines.append("Local fallback is not ready; use Colab or fix the reported holds first.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report local ROCm fallback readiness for Phase 2 without starting training."
    )
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--playground-root", default=str(DEFAULT_PLAYGROUND_ROOT))
    parser.add_argument("--session", default="open-duck-l4")
    parser.add_argument(
        "--workflow",
        default="phase2-z002-tracking-margin",
        choices=[
            "phase2-z002-tracking-margin",
            "phase2-z0035-motion-floor",
            "phase2-z005-support",
        ],
    )
    parser.add_argument("--timeout-s", type=int, default=30)
    parser.add_argument("--check-training-timeout-s", type=int, default=120)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = collect(args)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    write_markdown(payload, output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"status: {payload['status']}")
    print(f"wrote: {rel(output_md)}")
    print(f"wrote: {rel(output_json)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
