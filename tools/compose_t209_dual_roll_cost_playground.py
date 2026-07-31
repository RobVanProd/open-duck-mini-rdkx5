#!/usr/bin/env python3
"""Compose T209's dual roll-cost playground from the frozen T202 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "winner_t209_dual_roll_cost.patch"
ENGINE_FILES = (
    "playground/common/winner_v127_constrained_ppo_train.py",
    "playground/common/winner_v127_constrained_ppo_losses.py",
)
ENGINE_SOURCES = {
    "playground/common/winner_v127_constrained_ppo_train.py": (
        "training/winner_v127_constrained_ppo_train.py"
    ),
    "playground/common/winner_v127_constrained_ppo_losses.py": (
        "training/winner_v127_constrained_ppo_losses.py"
    ),
}


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


def git_blob(path: str) -> tuple[bytes, str]:
    blob = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if blob.returncode != 0:
        raise RuntimeError(
            f"cannot read frozen repository engine {path}: "
            f"{blob.stderr.decode(errors='replace')}"
        )
    oid = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        text=True,
    ).strip()
    return blob.stdout, oid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    base = args.base_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T209 tree: {output}")
    base_manifest = base / "T202_COMPOSED_SOURCE_MANIFEST.json"
    required = [
        base / "playground/open_duck_mini_v2/joystick.py",
        base / "playground/open_duck_mini_v2/runner.py",
        base / "playground/common/t202_predicted_roll_risk.py",
        *(base / name for name in ENGINE_FILES),
    ]
    if not base_manifest.is_file() or not all(
        path.is_file() for path in required
    ):
        raise FileNotFoundError("T209 frozen base is incomplete")

    shutil.copytree(base, output)
    frozen_engine_blobs = {}
    for name in ENGINE_FILES:
        source_name = ENGINE_SOURCES[name]
        content, oid = git_blob(source_name)
        target = output / name
        target.write_bytes(content)
        frozen_engine_blobs[name] = {
            "repository_path": source_name,
            "git_blob_oid": oid,
            "sha256": sha256(target),
        }
    run(["git", "apply", "--recount", "--check", str(PATCH)], output)
    run(["git", "apply", "--recount", str(PATCH)], output)
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "playground/common/t202_predicted_roll_risk.py",
            *ENGINE_FILES,
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
        "schema_version": "open_duck.t209_composed_source.v1",
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
            }
        },
        "constrained_engine": {
            "source": "frozen pure V127 repository blobs",
            "files": frozen_engine_blobs,
            "v173_tangent_selector_absent": (
                "v173_tangent"
                not in (output / ENGINE_FILES[0]).read_text(encoding="utf-8")
            ),
            "mixed_lagrangian_advantage_present": (
                "mixed_advantages"
                in (output / ENGINE_FILES[1]).read_text(encoding="utf-8")
            ),
        },
        "final_python_hashes": final_python_hashes,
    }
    manifest_path = output / "T209_COMPOSED_SOURCE_MANIFEST.json"
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
