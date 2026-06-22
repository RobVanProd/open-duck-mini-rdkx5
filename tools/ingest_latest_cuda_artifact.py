#!/usr/bin/env python3
"""Find and import the latest CUDA/Colab artifact bundle.

The generated CUDA/Colab cell downloads files like:

  open_duck_cuda_artifacts_<timestamp>.tar.gz
  open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256

This helper searches common download locations, verifies whether the bundle was
already imported by SHA256, and delegates extraction/summarization to
tools/import_cuda_artifact_bundle.py.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from import_cuda_artifact_bundle import DEFAULT_OUTPUT_ROOT, sha256_file


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEARCH_DIRS = [
    Path.home() / "Downloads",
    Path.home() / "robots",
    ROOT.parent,
]


def unique_existing(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen or not resolved.exists() or not resolved.is_dir():
            continue
        seen.add(resolved)
        result.append(resolved)
    return result


def find_bundles(search_dirs: list[Path]) -> list[Path]:
    bundles: list[Path] = []
    for directory in unique_existing(search_dirs):
        bundles.extend(directory.rglob("open_duck_cuda_artifacts_*.tar.gz"))
    return sorted(
        [path for path in bundles if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def existing_import_for_sha(bundle_sha256: str, output_root: Path) -> Path | None:
    if not output_root.exists():
        return None
    for summary in sorted(output_root.rglob("cuda_artifact_import_summary.json")):
        payload = read_json(summary)
        if not isinstance(payload, dict):
            continue
        bundle = payload.get("bundle")
        if isinstance(bundle, dict) and bundle.get("sha256") == bundle_sha256:
            md = summary.with_name("CUDA_ARTIFACT_IMPORT_SUMMARY.md")
            return md if md.exists() else summary
    return None


def print_bundle_list(bundles: list[Path], limit: int = 10) -> None:
    if not bundles:
        print("No CUDA artifact bundles found.")
        return
    print("CUDA artifact bundles:")
    for path in bundles[:limit]:
        sidecar = path.with_name(path.name + ".sha256")
        sidecar_status = "sidecar=yes" if sidecar.exists() else "sidecar=no"
        print(
            f"- {path} size={path.stat().st_size} mtime={path.stat().st_mtime:.0f} "
            f"{sidecar_status}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find the newest CUDA artifact bundle and import it."
    )
    parser.add_argument("--bundle", help="explicit artifact bundle path")
    parser.add_argument(
        "--search-dir",
        action="append",
        dest="search_dirs",
        help="directory to search; may be passed multiple times",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="import output root; defaults to outputs/analysis/cuda_imports",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="import even if a bundle with the same SHA256 was already imported",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show selected bundle and sidecar without importing",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list candidate bundles and exit",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    if args.bundle:
        bundle = Path(args.bundle).expanduser().resolve()
        bundles = [bundle]
    else:
        search_dirs = (
            [Path(item) for item in args.search_dirs]
            if args.search_dirs
            else DEFAULT_SEARCH_DIRS
        )
        bundles = find_bundles(search_dirs)
        bundle = bundles[0] if bundles else None

    if args.list:
        print_bundle_list(bundles)
        return 0

    if bundle is None:
        raise SystemExit(
            "No CUDA artifact bundle found. Download "
            "open_duck_cuda_artifacts_<timestamp>.tar.gz first, or pass --bundle."
        )
    if not bundle.exists():
        raise SystemExit(f"bundle not found: {bundle}")
    if not bundle.is_file():
        raise SystemExit(f"bundle is not a file: {bundle}")

    sidecar = bundle.with_name(bundle.name + ".sha256")
    bundle_sha256 = sha256_file(bundle)
    existing = existing_import_for_sha(bundle_sha256, output_root)

    print(f"CUDA_ARTIFACT_SELECTED {bundle}")
    print(f"CUDA_ARTIFACT_SELECTED_SIZE_BYTES {bundle.stat().st_size}")
    print(f"CUDA_ARTIFACT_SELECTED_SHA256 {bundle_sha256}")
    if sidecar.exists():
        print(f"CUDA_ARTIFACT_SELECTED_SHA256_FILE {sidecar}")
    else:
        print("CUDA_ARTIFACT_SELECTED_SHA256_FILE MISSING")

    if existing and not args.force:
        print(f"CUDA_ARTIFACT_ALREADY_IMPORTED {existing}")
        return 0

    if args.dry_run:
        print("CUDA_ARTIFACT_DRY_RUN no import performed")
        return 0

    command = [
        sys.executable,
        str(ROOT / "tools/import_cuda_artifact_bundle.py"),
        str(bundle),
        "--output-dir",
        str(output_root / f"manual_{bundle.stem.replace('.tar', '')}"),
    ]
    if sidecar.exists():
        command.extend(["--expected-sha256-file", str(sidecar)])

    print("CUDA_ARTIFACT_IMPORT_COMMAND", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
