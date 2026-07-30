#!/usr/bin/env python3
"""Compose T215B's tilt-box playground from the frozen T209 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/winner_t215b_axis_complete_tilt.patch"
MODULE = ROOT / "training/t215b_axis_complete_tilt.py"
TARGET_MODULE = "playground/common/t215b_axis_complete_tilt.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command}\n"
            f"{completed.stdout}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    base = args.base_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T215B tree: {output}")
    base_manifest = base / "T209_COMPOSED_SOURCE_MANIFEST.json"
    required = [
        base / "playground/open_duck_mini_v2/joystick.py",
        base / "playground/open_duck_mini_v2/runner.py",
        base
        / "playground/common/winner_v127_constrained_ppo_train.py",
        base
        / "playground/common/winner_v127_constrained_ppo_losses.py",
    ]
    if not base_manifest.is_file() or not all(
        path.is_file() for path in required
    ):
        raise FileNotFoundError("T215B frozen T209 base is incomplete")

    shutil.copytree(base, output)
    target_module = output / TARGET_MODULE
    shutil.copy2(MODULE, target_module)
    run(["git", "apply", "--recount", "--check", str(PATCH)], output)
    run(["git", "apply", "--recount", str(PATCH)], output)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            TARGET_MODULE,
            "playground/open_duck_mini_v2/joystick.py",
            "playground/open_duck_mini_v2/runner.py",
        ],
        output,
    )
    python_hashes = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted((output / "playground").rglob("*.py"))
    }
    manifest = {
        "schema_version": "open_duck.t215b_composed_source.v1",
        "base": {
            "path": str(base),
            "manifest": str(base_manifest),
            "manifest_sha256": sha256(base_manifest),
            "required_file_sha256": {
                path.relative_to(base).as_posix(): sha256(path)
                for path in required
            },
        },
        "sources": {
            "patch": {
                "path": PATCH.relative_to(ROOT).as_posix(),
                "sha256": sha256(PATCH),
            },
            "tilt_module": {
                "path": MODULE.relative_to(ROOT).as_posix(),
                "sha256": sha256(MODULE),
                "installed_as": TARGET_MODULE,
            },
        },
        "scientific_scope": {
            "base_engine": "exact T209 separate-cost/dual engine",
            "changed_signal_only": True,
            "reward_channel_unchanged": True,
            "deployment_graph_unchanged": True,
            "policy_abi_unchanged": True,
        },
        "final_python_hashes": python_hashes,
    }
    manifest_path = output / "T215B_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest": str(manifest_path),
                "manifest_sha256": sha256(manifest_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
