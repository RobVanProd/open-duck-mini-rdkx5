#!/usr/bin/env python3
"""Check local sim/training environment readiness without starting training."""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND_ROOT = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ROCM_ENV = ROOT.parent / "envs" / "rocm-baseline"
DEFAULT_RENDER_SMOKE = ROOT.parent / "verify_scratch" / "render_mujoco_egl.py"


def row(status: str, name: str, detail: str) -> dict:
    return {"status": status, "name": name, "detail": detail}


def import_check(name: str) -> dict:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", None)
        detail = f"imported {name}"
        if version:
            detail += f" {version}"
        return row("PASS", f"import:{name}", detail)
    except Exception as exc:  # pragma: no cover - environment-dependent
        return row("HOLD", f"import:{name}", f"{type(exc).__name__}: {exc}")


def command_check(command: list[str], timeout_s: int = 5) -> dict:
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        return row("WARN", f"command:{command[0]}", "not found")
    except subprocess.TimeoutExpired:
        return row("WARN", f"command:{command[0]}", f"timed out after {timeout_s}s")
    first_line = (result.stdout or "").strip().splitlines()
    detail = first_line[0] if first_line else f"exit={result.returncode}"
    status = "PASS" if result.returncode == 0 else "WARN"
    return row(status, f"command:{command[0]}", detail[:240])


def check_jax() -> list[dict]:
    checks = []
    try:
        import jax

        checks.append(row("PASS", "jax.import", f"imported jax {jax.__version__}"))
        devices = jax.devices()
        backend = jax.default_backend()
        device_text = ", ".join(str(device) for device in devices)
        checks.append(row("PASS", "jax.backend", f"default_backend={backend}"))
        checks.append(row("PASS", "jax.devices", device_text or "no devices listed"))
        gpu_like = [
            device
            for device in devices
            if getattr(device, "platform", "") in {"gpu", "rocm"}
            or "gpu" in str(device).lower()
            or "rocm" in str(device).lower()
        ]
        if gpu_like:
            checks.append(row("PASS", "jax.gpu", f"GPU/ROCm-like devices visible: {gpu_like}"))
        else:
            checks.append(
                row(
                    "HOLD",
                    "jax.gpu",
                    "HOLD_GPU_NOT_READY: no GPU/ROCm JAX device is visible",
                )
            )
    except Exception as exc:  # pragma: no cover - environment-dependent
        checks.append(row("HOLD", "jax.import", f"{type(exc).__name__}: {exc}"))
    return checks


def check_mujoco(render_check: bool) -> list[dict]:
    checks = []
    try:
        import mujoco

        checks.append(row("PASS", "mujoco.import", f"imported mujoco {mujoco.__version__}"))
        xml = """
<mujoco>
  <worldbody>
    <body name="box" pos="0 0 0.1">
      <freejoint/>
      <geom type="box" size="0.05 0.05 0.05"/>
    </body>
  </worldbody>
</mujoco>
"""
        model = mujoco.MjModel.from_xml_string(xml)
        data = mujoco.MjData(model)
        mujoco.mj_step(model, data)
        checks.append(row("PASS", "mujoco.model_load", "loaded and stepped minimal model"))
        if render_check:
            try:
                ctx = mujoco.GLContext(64, 64)
                ctx.make_current()
                checks.append(row("PASS", "mujoco.gl_context", "created offscreen GLContext"))
            except Exception as exc:  # pragma: no cover - environment-dependent
                checks.append(
                    row("HOLD", "mujoco.gl_context", f"{type(exc).__name__}: {exc}")
                )
    except Exception as exc:  # pragma: no cover - environment-dependent
        checks.append(row("HOLD", "mujoco.import_or_model", f"{type(exc).__name__}: {exc}"))
    return checks


def check_playground(playground_root: Path) -> list[dict]:
    checks = []
    if not playground_root.exists():
        return [
            row(
                "HOLD",
                "playground.path",
                f"HOLD_SIM_CODE_MISSING: {playground_root} does not exist",
            )
        ]
    checks.append(row("PASS", "playground.path", str(playground_root)))
    sys.path.insert(0, str(playground_root))
    for module in [
        "playground.open_duck_mini_v2.joystick",
        "playground.open_duck_mini_v2.constants",
    ]:
        checks.append(import_check(module))
    return checks


def summarize_status(checks: list[dict]) -> str:
    if any(item["status"] == "HOLD" for item in checks):
        return "HOLD_ENV_NOT_READY"
    if any(item["status"] == "WARN" for item in checks):
        return "WARN_ENV_CHECKS"
    return "PASS_ENV_READY"


def print_markdown(payload: dict) -> None:
    print("# Training Environment Check")
    print()
    print(f"overall_status: `{payload['overall_status']}`")
    print(f"python: `{payload['python']}`")
    print(f"platform: `{payload['platform']}`")
    print(f"target_gpu: `{payload['target_gpu']}`")
    print(f"playground_root: `{payload['playground_root']}`")
    print(f"rocm_env_hint: `{payload['rocm_env_hint']}`")
    print(f"mujoco_render_smoke_hint: `{payload['mujoco_render_smoke_hint']}`")
    print()
    print("| status | check | detail |")
    print("|---|---|---|")
    for item in payload["checks"]:
        detail = str(item["detail"]).replace("|", "\\|")
        print(f"| {item['status']} | {item['name']} | {detail} |")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local Open Duck training/eval readiness without starting training."
    )
    parser.add_argument("--playground-root", default=str(DEFAULT_PLAYGROUND_ROOT))
    parser.add_argument("--json-output", default=None)
    parser.add_argument(
        "--render-check",
        action="store_true",
        help="also try to create a MuJoCo offscreen GL context",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return nonzero if any HOLD checks are present",
    )
    args = parser.parse_args()

    playground_root = Path(args.playground_root).expanduser().resolve()
    checks: list[dict] = []
    checks.append(row("PASS", "python.version", sys.version.split()[0]))
    checks.append(row("PASS", "python.executable", sys.executable))
    checks.append(row("PASS", "env.MUJOCO_GL", os.environ.get("MUJOCO_GL", "unset")))
    checks.append(row("PASS", "env.PYTHONPATH", os.environ.get("PYTHONPATH", "unset")))
    checks.append(
        row(
            "PASS" if DEFAULT_ROCM_ENV.exists() else "WARN",
            "local.rocm_env_hint",
            str(DEFAULT_ROCM_ENV),
        )
    )
    checks.append(
        row(
            "PASS" if DEFAULT_RENDER_SMOKE.exists() else "WARN",
            "local.mujoco_render_smoke_hint",
            str(DEFAULT_RENDER_SMOKE),
        )
    )

    for command in [["rocminfo"], ["rocm-smi", "--showproductname"]]:
        checks.append(command_check(command))

    for package in ["numpy", "onnxruntime", "ml_collections", "mujoco_playground"]:
        checks.append(import_check(package))
    checks.extend(check_jax())
    checks.extend(check_mujoco(args.render_check))
    checks.extend(check_playground(playground_root))

    payload = {
        "overall_status": summarize_status(checks),
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "target_gpu": "AMD Radeon RX 7900 XTX / ROCm",
        "playground_root": str(playground_root),
        "rocm_env_hint": str(DEFAULT_ROCM_ENV),
        "mujoco_render_smoke_hint": str(DEFAULT_RENDER_SMOKE),
        "checks": checks,
    }

    if args.json_output:
        path = Path(args.json_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n")

    print_markdown(payload)
    if args.strict and payload["overall_status"].startswith("HOLD"):
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
