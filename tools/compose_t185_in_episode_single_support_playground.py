#!/usr/bin/env python3
"""Compose the default-off T185 curriculum playground from frozen T170 base."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = (
    ROOT
    / "patches"
    / "winner_t185_in_episode_single_support_prefix.patch"
)
MODULE = (
    ROOT
    / "patches"
    / "t185_in_episode_single_support_prefix.py"
)


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
        raise FileExistsError(f"refusing to reuse T185 tree: {output}")
    required = (
        base / "playground" / "common" / "runner.py",
        base / "playground" / "common" / "poly_reference_motion.py",
        base / "playground" / "open_duck_mini_v2" / "constants.py",
        base / "playground" / "open_duck_mini_v2" / "joystick.py",
        base / "playground" / "open_duck_mini_v2" / "runner.py",
        base
        / "playground"
        / "open_duck_mini_v2"
        / "data"
        / "polynomial_coefficients.pkl",
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    shutil.copytree(base, output)
    destination = (
        output
        / "playground"
        / "common"
        / "t185_in_episode_single_support_prefix.py"
    )
    shutil.copy2(MODULE, destination)
    run(["git", "apply", "--recount", "--check", str(PATCH)], output)
    run(["git", "apply", "--recount", str(PATCH)], output)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "playground/common/t185_in_episode_single_support_prefix.py",
            "playground/open_duck_mini_v2/joystick.py",
            "playground/open_duck_mini_v2/runner.py",
        ],
        output,
    )
    final_python_hashes = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted((output / "playground").rglob("*.py"))
    }
    manifest = {
        "schema_version": "open_duck.t185_composed_source.v1",
        "base": {
            "path": str(base),
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
            "module": {
                "path": MODULE.relative_to(ROOT).as_posix(),
                "sha256": sha256(MODULE),
            },
        },
        "final_python_hashes": final_python_hashes,
    }
    manifest_path = output / "T185_COMPOSED_SOURCE_MANIFEST.json"
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
