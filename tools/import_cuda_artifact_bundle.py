#!/usr/bin/env python3
"""Import a small CUDA/Colab artifact bundle for review.

The generated CUDA cell writes one tarball containing analysis summaries,
candidate gate reports, candidate metadata, and exported ONNX files. This tool
extracts that bundle into the repo evidence area and writes a compact manifest
so review can start from one markdown file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "outputs/analysis/cuda_imports"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_member_path(member_name: str) -> Path:
    candidate = Path(member_name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe tar member path: {member_name}")
    return candidate


def extract_bundle(bundle: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "r:*") as tar:
        for member in tar.getmembers():
            safe_member_path(member.name)
        tar.extractall(output_dir)


def copy_directory(src: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / src.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def first_status_from_md(path: Path) -> str | None:
    try:
        for line in path.read_text(errors="replace").splitlines():
            stripped = line.strip()
            if "overall_status:" in stripped:
                return stripped.split("overall_status:", 1)[1].strip().strip("`")
            if "assessment_status:" in stripped:
                return stripped.split("assessment_status:", 1)[1].strip().strip("`")
            if "candidate_gate_status:" in stripped:
                return stripped.split("candidate_gate_status:", 1)[1].strip().strip("`")
    except Exception:
        return None
    return None


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def collect_files(output_dir: Path) -> dict[str, list[Path]]:
    return {
        "markdown": sorted(output_dir.rglob("*.md")),
        "json": sorted(output_dir.rglob("*.json")),
        "onnx": sorted(output_dir.rglob("*.onnx")),
        "stdout_stderr": sorted(
            list(output_dir.rglob("stdout.txt")) + list(output_dir.rglob("stderr.txt"))
        ),
    }


def build_summary(
    bundle: Path | None, source_dir: Path | None, output_dir: Path
) -> tuple[str, dict[str, Any]]:
    files = collect_files(output_dir)
    markdown_statuses = []
    for path in files["markdown"]:
        status = first_status_from_md(path)
        markdown_statuses.append(
            {
                "path": relative(path),
                "status": status or "UNKNOWN",
                "size_bytes": path.stat().st_size,
            }
        )

    json_summaries = []
    for path in files["json"]:
        payload = read_json(path)
        item: dict[str, Any] = {
            "path": relative(path),
            "size_bytes": path.stat().st_size,
        }
        if isinstance(payload, dict):
            for key in [
                "overall_status",
                "assessment_status",
                "status",
                "candidate_gate_status",
            ]:
                if key in payload:
                    item[key] = payload[key]
            candidate = payload.get("candidate")
            if isinstance(candidate, dict):
                item["candidate_name"] = candidate.get("name")
                item["candidate_sha256"] = candidate.get("sha256")
        json_summaries.append(item)

    onnx_summaries = [
        {
            "path": relative(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in files["onnx"]
    ]

    payload = {
        "schema_version": "cuda_artifact_import.v1",
        "timestamp": timestamp(),
        "bundle": None
        if bundle is None
        else {
            "path": str(bundle),
            "size_bytes": bundle.stat().st_size,
            "sha256": sha256_file(bundle),
        },
        "source_dir": None if source_dir is None else str(source_dir),
        "output_dir": str(output_dir),
        "markdown_statuses": markdown_statuses,
        "json_summaries": json_summaries,
        "onnx_files": onnx_summaries,
        "stdout_stderr_files": [relative(path) for path in files["stdout_stderr"]],
    }

    lines = [
        "# CUDA Artifact Import Summary",
        "",
        f"- timestamp: `{payload['timestamp']}`",
        f"- output_dir: `{relative(output_dir)}`",
    ]
    if payload["bundle"]:
        lines.extend(
            [
                f"- bundle: `{payload['bundle']['path']}`",
                f"- bundle_sha256: `{payload['bundle']['sha256']}`",
            ]
        )
    if source_dir:
        lines.append(f"- source_dir: `{source_dir}`")

    lines.extend(["", "## Markdown Statuses", ""])
    if markdown_statuses:
        lines.append("| file | status |")
        lines.append("|---|---|")
        for item in markdown_statuses:
            lines.append(f"| `{item['path']}` | `{item['status']}` |")
    else:
        lines.append("No markdown files found.")

    lines.extend(["", "## JSON Statuses", ""])
    if json_summaries:
        lines.append("| file | status | candidate |")
        lines.append("|---|---|---|")
        for item in json_summaries:
            status = (
                item.get("overall_status")
                or item.get("assessment_status")
                or item.get("candidate_gate_status")
                or item.get("status")
                or "UNKNOWN"
            )
            candidate = item.get("candidate_name") or ""
            lines.append(f"| `{item['path']}` | `{status}` | `{candidate}` |")
    else:
        lines.append("No JSON files found.")

    lines.extend(["", "## ONNX Files", ""])
    if onnx_summaries:
        lines.append("| file | size_bytes | sha256 |")
        lines.append("|---|---:|---|")
        for item in onnx_summaries:
            lines.append(
                f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` |"
            )
    else:
        lines.append("No ONNX files found.")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "This import does not approve robot testing. Review candidate sim gates",
            "and package metadata before any suspended validation is discussed.",
            "",
        ]
    )
    return "\n".join(lines), payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import a CUDA/Colab artifact bundle and summarize it."
    )
    parser.add_argument("source", help="artifact .tar.gz/.tgz file or extracted directory")
    parser.add_argument("--output-dir", help="destination directory")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"source not found: {source}")

    suffix = "".join(source.suffixes)
    stem = source.name
    for ext in [".tar.gz", ".tgz", ".tar"]:
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else DEFAULT_OUTPUT_ROOT / f"{timestamp()}_{stem}"
    )

    bundle: Path | None = None
    source_dir: Path | None = None
    if source.is_dir():
        source_dir = source
        copy_directory(source, output_dir)
    elif suffix.endswith(".tar.gz") or suffix.endswith(".tgz") or source.suffix == ".tar":
        bundle = source
        extract_bundle(source, output_dir)
    else:
        raise SystemExit("source must be a .tar/.tar.gz/.tgz bundle or directory")

    summary_md, payload = build_summary(bundle, source_dir, output_dir)
    (output_dir / "CUDA_ARTIFACT_IMPORT_SUMMARY.md").write_text(summary_md + "\n")
    (output_dir / "cuda_artifact_import_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(output_dir / "CUDA_ARTIFACT_IMPORT_SUMMARY.md")
    print(output_dir / "cuda_artifact_import_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
