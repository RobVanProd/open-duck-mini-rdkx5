#!/usr/bin/env python3
"""Write a manifest for required Phase 2 Colab package inputs.

This read-only report verifies the exact local artifacts needed by the
`phase2-z005-support` workflow before a Colab session is available. It walks
required files and checkpoint directories, checks the same tar filter used by
`run_colab_cli_cuda_workflow.py`, and records hashes so the launch package is
reviewable without touching Colab, SSH, robot hardware, or training.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

from run_colab_cli_cuda_workflow import required_rdk_package_paths, tar_filter, would_package_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_colab_package_manifest.json"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def included_by_filter(relative_path: str) -> bool:
    return tar_filter(tarfile.TarInfo(f"open-duck-mini-rdkx5/{relative_path}")) is not None


def summarize_file(path: Path) -> dict[str, Any]:
    relative = rel(path)
    return {
        "path": relative,
        "exists": path.exists(),
        "included_by_tar_filter": included_by_filter(relative or str(path)),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": file_sha256(path) if path.exists() and path.is_file() else None,
    }


def summarize_directory(path: Path) -> dict[str, Any]:
    files = sorted(child for child in path.rglob("*") if child.is_file())
    included_files = []
    excluded_files = []
    total_size = 0
    digest = hashlib.sha256()
    for child in files:
        relative = rel(child)
        if relative is None:
            excluded_files.append(str(child))
            continue
        if included_by_filter(relative):
            child_sha = file_sha256(child)
            size = child.stat().st_size
            total_size += size
            included_files.append(
                {
                    "path": relative,
                    "size_bytes": size,
                    "sha256": child_sha,
                }
            )
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(child_sha.encode())
            digest.update(b"\0")
        else:
            excluded_files.append(relative)
    return {
        "path": rel(path),
        "exists": path.exists(),
        "included_by_tar_filter": would_package_path(rel(path) or str(path)),
        "file_count": len(files),
        "included_file_count": len(included_files),
        "excluded_file_count": len(excluded_files),
        "size_bytes": total_size,
        "sha256": digest.hexdigest() if included_files else None,
        "excluded_files": excluded_files,
        "included_files": included_files,
    }


def summarize_required_path(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        return {
            "path": relative_path,
            "exists": False,
            "included_by_tar_filter": would_package_path(relative_path),
            "status": "MISSING",
        }
    if path.is_dir():
        item = summarize_directory(path)
        item["status"] = (
            "PRESENT_DIR_INCLUDED"
            if item["included_by_tar_filter"] and item["included_file_count"] > 0 and not item["excluded_files"]
            else "PRESENT_DIR_INCOMPLETE"
        )
        return item
    item = summarize_file(path)
    item["status"] = "PRESENT_FILE_INCLUDED" if item["included_by_tar_filter"] else "PRESENT_FILE_EXCLUDED"
    return item


def collect(args: argparse.Namespace) -> dict[str, Any]:
    items = [summarize_required_path(path) for path in required_rdk_package_paths(args.workflow)]
    missing = [item["path"] for item in items if not item["exists"]]
    excluded = [
        item["path"]
        for item in items
        if item["exists"] and not item.get("included_by_tar_filter")
    ]
    incomplete_dirs = [
        item["path"]
        for item in items
        if item.get("status") == "PRESENT_DIR_INCOMPLETE"
    ]
    status = (
        "PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY"
        if not missing and not excluded and not incomplete_dirs
        else "HOLD_PHASE2_COLAB_PACKAGE_MANIFEST"
    )
    return {
        "status": status,
        "workflow": args.workflow,
        "required_paths": items,
        "missing": missing,
        "excluded_by_tar_filter": excluded,
        "incomplete_dirs": incomplete_dirs,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Colab Package Manifest",
        "",
        f"status: `{payload['status']}`",
        f"workflow: `{payload['workflow']}`",
        "",
        "This is a read-only package manifest. It did not train, SSH, deploy, touch the robot, or upload to Colab.",
        "",
        "## Required Paths",
        "",
        "| path | status | files included | files excluded | size bytes | sha256 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for item in payload["required_paths"]:
        files_included = item.get("included_file_count")
        if files_included is None and item.get("exists"):
            files_included = 1
        files_excluded = item.get("excluded_file_count", 0)
        lines.append(
            f"| `{item['path']}` | `{item.get('status')}` | {files_included if files_included is not None else 'NA'} | "
            f"{files_excluded} | {item.get('size_bytes', 'NA')} | `{item.get('sha256', 'NA')}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    if payload["status"].startswith("PASS"):
        lines.append("All required z=0.005 Colab package inputs are present and included by the upload tar filter.")
    else:
        lines.append("Do not launch the z=0.005 Colab workflow until missing or excluded package inputs are fixed.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", default="phase2-z005-support")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = collect(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
