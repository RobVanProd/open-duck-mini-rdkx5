#!/usr/bin/env python3
"""Compose the default-off T19 support train-through playground."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "winner_t19_support_trainthrough.patch"
MODULE = ROOT / "patches" / "t19_support_trainthrough.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        raise FileExistsError(f"refusing to reuse T19 tree: {output}")
    required = (
        base / "playground" / "open_duck_mini_v2" / "joystick.py",
        base / "playground" / "open_duck_mini_v2" / "runner.py",
        base / "playground" / "common" / "runner.py",
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    shutil.copytree(base, output)
    destination = (
        output
        / "playground"
        / "common"
        / "t19_support_trainthrough.py"
    )
    shutil.copy2(MODULE, destination)
    run(["git", "apply", "--recount", "--check", str(PATCH)], output)
    run(["git", "apply", "--recount", str(PATCH)], output)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "playground/common/t19_support_trainthrough.py",
            "playground/common/runner.py",
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
        "schema_version": "open_duck.t19_composed_source.v1",
        "base": {
            "path": str(base),
            "required_file_sha256": {
                str(path.relative_to(base).as_posix()): sha256(path)
                for path in required
            },
        },
        "sources": {
            "patch": {
                "path": str(PATCH.relative_to(ROOT).as_posix()),
                "sha256": sha256(PATCH),
            },
            "module": {
                "path": str(MODULE.relative_to(ROOT).as_posix()),
                "sha256": sha256(MODULE),
            },
        },
        "final_python_hashes": final_python_hashes,
    }
    manifest_path = output / "T19_COMPOSED_SOURCE_MANIFEST.json"
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
