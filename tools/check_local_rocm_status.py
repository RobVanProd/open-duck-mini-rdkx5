#!/usr/bin/env python3
"""Collect a read-only local ROCm/JAX backend status report.

This tool is workstation-only. It does not train, SSH, deploy, or touch the
robot. It exists so local 7900 XTX / ROCm readiness can be rechecked after a
reboot, driver change, or firmware update without relying on ad hoc terminal
history.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "LOCAL_ROCM_STATUS_20260625.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "local_rocm_status_20260625.json"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run(
    command: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    timeout_s: int = 30,
) -> dict[str, Any]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=merged_env,
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
            "timeout_s": timeout_s,
            "env_overrides": env or {},
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
            "missing_executable": command[0],
            "timeout_s": timeout_s,
            "env_overrides": env or {},
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "ok": False,
            "timeout": True,
            "timeout_s": timeout_s,
            "env_overrides": env or {},
        }


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def combined_text(result: dict[str, Any]) -> str:
    return strip_ansi(((result.get("stdout") or "") + (result.get("stderr") or "")).strip())


def first_lines(text: str, limit: int = 80) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(lines[:limit] + [f"... truncated {len(lines) - limit} lines ..."])


def rocm_variants() -> dict[str, dict[str, str]]:
    opt_path = "/opt/rocm-7.2.1"
    return {
        "default": {},
        "opt_rocm_path": {
            "LD_LIBRARY_PATH": f"{opt_path}/lib",
            "PATH": f"{opt_path}/bin:{os.environ.get('PATH', '')}",
        },
        "hsa_override": {"HSA_OVERRIDE_GFX_VERSION": "11.0.0"},
        "opt_rocm_path_hsa_override": {
            "HSA_OVERRIDE_GFX_VERSION": "11.0.0",
            "LD_LIBRARY_PATH": f"{opt_path}/lib",
            "PATH": f"{opt_path}/bin:{os.environ.get('PATH', '')}",
        },
    }


def jax_probe_script() -> str:
    return """
import os
import sys

print("python", sys.executable)
for key in ["JAX_PLATFORMS", "JAX_PLATFORM_NAME", "HSA_OVERRIDE_GFX_VERSION", "LD_LIBRARY_PATH"]:
    if os.environ.get(key):
        print(key, os.environ.get(key))
try:
    import jax
    print("jax", jax.__version__)
    print("backend", jax.default_backend())
    print("devices", jax.devices())
except Exception as exc:
    print("jax_error", type(exc).__name__, exc)
try:
    import mujoco
    print("mujoco", mujoco.__version__)
except Exception as exc:
    print("mujoco_error", type(exc).__name__, exc)
"""


def collect(env_python: Path, include_journal: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": timestamp(),
        "robot_touched": False,
        "deploy_performed": False,
        "training_started": False,
        "env_python": str(env_python),
        "commands": {},
        "rocminfo_variants": {},
        "jax_variants": {},
    }

    payload["commands"]["id"] = run(["id"])
    payload["commands"]["groups"] = run(["groups"])
    payload["commands"]["uname"] = run(["uname", "-a"])
    payload["commands"]["device_nodes"] = run(
        ["bash", "-lc", "ls -l /dev/kfd /dev/dri/renderD* 2>/dev/null || true"]
    )
    payload["commands"]["rocm_smi"] = run(["rocm-smi"], timeout_s=60)
    payload["commands"]["rocm_paths"] = run(
        [
            "bash",
            "-lc",
            (
                "which rocminfo hipcc rocm-smi || true; "
                "find /opt/rocm* -maxdepth 3 "
                "\\( -name rocminfo -o -name libhsa-runtime64.so.1 -o "
                "-name libamdhip64.so.7 \\) -printf '%p -> %l\\n' 2>/dev/null | sort"
            ),
        ],
        timeout_s=30,
    )
    payload["commands"]["rocm_packages"] = run(
        [
            "bash",
            "-lc",
            (
                "dpkg-query -W -f='${Package} ${Version}\\n' "
                "'rocm*' 'hip*' 'hsa*' 'libamdhip*' 'libhsa*' 'amdgpu*' 2>/dev/null "
                "| sort || true"
            ),
        ],
        timeout_s=30,
    )
    payload["commands"]["ldconfig_rocm"] = run(
        ["bash", "-lc", "ldconfig -p 2>/dev/null | rg 'libhsa|libamdhip|libhiprtc|libhsakmt' || true"],
        timeout_s=30,
    )
    payload["commands"]["amdgpu_params"] = run(
        [
            "bash",
            "-lc",
            (
                "printf 'cwsr_enable='; cat /sys/module/amdgpu/parameters/cwsr_enable 2>/dev/null || true; "
                "printf 'amdgpu_version='; cat /sys/module/amdgpu/version 2>/dev/null || true"
            ),
        ],
        timeout_s=30,
    )
    if include_journal:
        payload["commands"]["kernel_amdgpu_recent"] = run(
            [
                "bash",
                "-lc",
                (
                    "journalctl -k --since '2 hours ago' --no-pager 2>/dev/null "
                    "| rg -i 'amdgpu|kfd|hsa|gpu|ring|gfx|reset|fault|ras|drm' "
                    "| tail -n 180 || true"
                ),
            ],
            timeout_s=30,
        )

    for name, env in rocm_variants().items():
        payload["rocminfo_variants"][name] = run(["rocminfo"], env=env, timeout_s=60)

    jax_variants = rocm_variants()
    jax_variants["cpu"] = {"JAX_PLATFORMS": "cpu", "JAX_PLATFORM_NAME": "cpu"}
    for name, env in jax_variants.items():
        payload["jax_variants"][name] = run(
            [str(env_python), "-c", jax_probe_script()],
            env=env,
            timeout_s=60,
        )

    payload["status"] = classify(payload)
    return payload


def rocminfo_kfd_failed(payload: dict[str, Any]) -> bool:
    default = payload["rocminfo_variants"].get("default") or {}
    text = combined_text(default).lower()
    return "unable to open /dev/kfd" in text or "/dev/kfd" in text and "invalid argument" in text


def jax_has_gpu(payload: dict[str, Any]) -> bool:
    default = payload["jax_variants"].get("default") or {}
    text = combined_text(default).lower()
    return default.get("ok") and ("rocm" in text or "gpu" in text) and "jax_error" not in text


def classify(payload: dict[str, Any]) -> str:
    default_rocminfo = payload["rocminfo_variants"].get("default") or {}
    if rocminfo_kfd_failed(payload):
        return "HOLD_LOCAL_ROCM_KFD"
    if not default_rocminfo.get("ok"):
        return "HOLD_LOCAL_ROCMINFO"
    if not jax_has_gpu(payload):
        return "HOLD_LOCAL_JAX_ROCM"
    return "PASS_LOCAL_ROCM_READY"


def md_bool(value: bool) -> str:
    return "PASS" if value else "HOLD"


def write_reports(payload: dict[str, Any], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Local ROCm Status",
        "",
        f"status: `{payload['status']}`",
        f"timestamp: `{payload['timestamp']}`",
        "",
        "This read-only check did not train, SSH, deploy, change runtime",
        "behavior, or touch the robot.",
        "",
        "## Summary",
        "",
        "| check | result |",
        "|---|---|",
        f"| rocminfo default | `{md_bool(payload['rocminfo_variants']['default']['ok'])}` |",
        f"| rocminfo /dev/kfd failure | `{rocminfo_kfd_failed(payload)}` |",
        f"| JAX default GPU visible | `{jax_has_gpu(payload)}` |",
        f"| JAX CPU fallback | `{md_bool(payload['jax_variants']['cpu']['ok'])}` |",
        "",
        "## rocminfo Variants",
        "",
    ]
    for name, result in payload["rocminfo_variants"].items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"returncode: `{result.get('returncode')}`",
                "",
                "```text",
                first_lines(combined_text(result), 80),
                "```",
                "",
            ]
        )

    lines.extend(["## JAX Variants", ""])
    for name, result in payload["jax_variants"].items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"returncode: `{result.get('returncode')}`",
                "",
                "```text",
                first_lines(combined_text(result), 80),
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## System Evidence",
            "",
            "### Device Nodes",
            "",
            "```text",
            first_lines(combined_text(payload["commands"]["device_nodes"]), 80),
            "```",
            "",
            "### ROCm Packages",
            "",
            "```text",
            first_lines(combined_text(payload["commands"]["rocm_packages"]), 120),
            "```",
            "",
            "### ROCm Library Paths",
            "",
            "```text",
            first_lines(combined_text(payload["commands"]["ldconfig_rocm"]), 120),
            "```",
            "",
        ]
    )
    if "kernel_amdgpu_recent" in payload["commands"]:
        lines.extend(
            [
                "### Recent Kernel GPU Lines",
                "",
                "```text",
                first_lines(combined_text(payload["commands"]["kernel_amdgpu_recent"]), 120),
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## External Leads",
            "",
            "- ROCm `/dev/kfd` `Invalid argument` issue:",
            "  <https://github.com/ROCm/ROCm/issues/4043>",
            "- Similar ROCm `/dev/kfd` issue:",
            "  <https://github.com/ROCm/ROCm/issues/6166>",
            "- AMD ROCm installation prerequisites:",
            "  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html>",
            "- AMD ROCm quick start:",
            "  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html>",
            "",
            "## Next Gate",
            "",
            "Do not use local ROCm for V21 training until both commands pass:",
            "",
            "```bash",
            "rocminfo",
            "../envs/open-duck-playground/bin/python -c 'import jax; print(jax.devices())'",
            "```",
            "",
            "CUDA/Colab remains the preferred V21 path while this hold is active.",
        ]
    )
    output_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-python", type=Path, default=DEFAULT_ENV_PYTHON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument(
        "--skip-journal",
        action="store_true",
        help="Skip recent kernel journal capture.",
    )
    args = parser.parse_args()

    payload = collect(args.env_python, include_journal=not args.skip_journal)
    write_reports(payload, args.output_md, args.output_json)
    print(payload["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
