#!/usr/bin/env python3
"""Compose V114 plus the default-off V119 train-transition match."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/winner_v119_train_transition_match.patch"


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
        raise FileExistsError(f"refusing to reuse V119 tree: {output}")
    base_manifest = base / "WINNER_V114_COMPOSED_SOURCE_MANIFEST.json"
    if not base_manifest.is_file():
        raise FileNotFoundError(base_manifest)
    shutil.copytree(base, output)
    run(["git", "apply", "--recount", "--check", str(PATCH)], output)
    run(["git", "apply", "--recount", str(PATCH)], output)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
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
        "schema_version": "winner_v119.train_transition_source.v1",
        "base": {
            "path": str(base),
            "manifest": str(base_manifest),
            "manifest_sha256": sha256(base_manifest),
        },
        "transition_patch": {
            "path": str(PATCH.relative_to(ROOT)),
            "sha256": sha256(PATCH),
        },
        "final_python_hashes": final_python_hashes,
    }
    manifest_path = output / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"output": str(output), "manifest": str(manifest_path)}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
