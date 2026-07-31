#!/usr/bin/env python3
"""Verify the exact Phase 2 package-only upload archives.

This read-only report opens a package-only manifest produced by
run_colab_cli_cuda_workflow.py, verifies archive size/SHA, and checks that the
required RDK package paths are present in the actual tarball referenced by that
manifest. It does not upload, train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_MANIFEST = (
    ROOT
    / "outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T011011Z"
    / "PACKAGE_ONLY_MANIFEST.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_package_only_archive_verification.json"
RDK_ARCHIVE_PREFIX = "open-duck-mini-rdkx5/"


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


def tar_member_sha256(archive: tarfile.TarFile, name: str) -> str | None:
    try:
        member = archive.getmember(name)
    except KeyError:
        return None
    if not member.isfile():
        return None
    extracted = archive.extractfile(member)
    if extracted is None:
        return None
    digest = hashlib.sha256()
    with extracted:
        for chunk in iter(lambda: extracted.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_entries(relative_path: str) -> list[str]:
    local_path = ROOT / relative_path
    if local_path.is_dir():
        return [
            RDK_ARCHIVE_PREFIX + str(child.relative_to(ROOT))
            for child in sorted(item for item in local_path.rglob("*") if item.is_file())
        ]
    return [RDK_ARCHIVE_PREFIX + relative_path]


def verify_archive(manifest: dict[str, Any], archive_name: str) -> dict[str, Any]:
    archive_info = (manifest.get("archives") or {}).get(archive_name) or {}
    archive_path = Path(archive_info.get("path", ""))
    exists = archive_path.exists()
    size_bytes = archive_path.stat().st_size if exists else None
    sha256 = file_sha256(archive_path) if exists else None
    return {
        "path": str(archive_path) if archive_info.get("path") else None,
        "exists": exists,
        "size_bytes": size_bytes,
        "expected_size_bytes": archive_info.get("size_bytes"),
        "size_matches": size_bytes == archive_info.get("size_bytes"),
        "sha256": sha256,
        "expected_sha256": archive_info.get("sha256"),
        "sha256_matches": sha256 == archive_info.get("sha256"),
    }


def verify_rdk_contents(manifest: dict[str, Any]) -> dict[str, Any]:
    rdk_info = (manifest.get("archives") or {}).get("rdk") or {}
    rdk_path = Path(rdk_info.get("path", ""))
    if not rdk_path.exists():
        return {
            "status": "HOLD_RDK_ARCHIVE_MISSING",
            "member_count": 0,
            "required_paths": [],
            "missing_entries": [],
            "mismatched_entries": [],
        }

    required_paths = manifest.get("required_rdk_package_paths") or []
    required_reports: list[dict[str, Any]] = []
    missing_entries: list[str] = []
    mismatched_entries: list[dict[str, str | None]] = []
    with tarfile.open(rdk_path) as archive:
        names = set(archive.getnames())
        for relative_path in required_paths:
            entries = expected_entries(relative_path)
            entry_reports = []
            for entry in entries:
                exists = entry in names
                local_path = ROOT / entry.removeprefix(RDK_ARCHIVE_PREFIX)
                local_sha = file_sha256(local_path) if local_path.is_file() else None
                archive_sha = tar_member_sha256(archive, entry) if exists else None
                hashes_match = exists and local_sha == archive_sha
                if not exists:
                    missing_entries.append(entry)
                elif local_sha is not None and not hashes_match:
                    mismatched_entries.append(
                        {
                            "entry": entry,
                            "local_sha256": local_sha,
                            "archive_sha256": archive_sha,
                        }
                    )
                entry_reports.append(
                    {
                        "entry": entry,
                        "exists": exists,
                        "local_sha256": local_sha,
                        "archive_sha256": archive_sha,
                        "hashes_match": hashes_match,
                    }
                )
            required_reports.append(
                {
                    "path": relative_path,
                    "expected_entries": len(entries),
                    "present_entries": sum(1 for item in entry_reports if item["exists"]),
                    "entries": entry_reports,
                }
            )
        member_count = len(names)

    status = (
        "PASS_PACKAGE_ONLY_ARCHIVE_VERIFIED"
        if not missing_entries and not mismatched_entries
        else "HOLD_PACKAGE_ONLY_ARCHIVE_CONTENTS"
    )
    return {
        "status": status,
        "member_count": member_count,
        "required_paths": required_reports,
        "missing_entries": missing_entries,
        "mismatched_entries": mismatched_entries,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = Path(args.package_manifest)
    manifest = json.loads(manifest_path.read_text())
    archives = {
        "rdk": verify_archive(manifest, "rdk"),
        "playground": verify_archive(manifest, "playground"),
    }
    rdk_contents = verify_rdk_contents(manifest)
    archive_checks_pass = all(
        item["exists"] and item["size_matches"] and item["sha256_matches"]
        for item in archives.values()
    )
    status = (
        "PASS_PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION"
        if manifest.get("status") == "PASS_COLAB_PACKAGE_ONLY_READY"
        and archive_checks_pass
        and rdk_contents["status"] == "PASS_PACKAGE_ONLY_ARCHIVE_VERIFIED"
        else "HOLD_PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION"
    )
    return {
        "status": status,
        "package_manifest": rel(manifest_path),
        "workflow": manifest.get("workflow"),
        "session": manifest.get("session"),
        "manifest_status": manifest.get("status"),
        "archives": archives,
        "rdk_contents": rdk_contents,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
        "uploaded_to_colab": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Package-Only Archive Verification",
        "",
        f"status: `{payload['status']}`",
        f"workflow: `{payload['workflow']}`",
        f"session: `{payload['session']}`",
        f"package_manifest: `{payload['package_manifest']}`",
        "",
        "This is a read-only archive verification. It did not upload, train, SSH, deploy, or touch the robot.",
        "",
        "## Archive Hashes",
        "",
        "| archive | exists | size matches | sha256 matches | size bytes | sha256 | path |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for name, item in payload["archives"].items():
        lines.append(
            f"| `{name}` | `{item['exists']}` | `{item['size_matches']}` | `{item['sha256_matches']}` | "
            f"{item['size_bytes']} | `{item['sha256']}` | `{item['path']}` |"
        )
    rdk = payload["rdk_contents"]
    lines.extend(
        [
            "",
            "## RDK Archive Contents",
            "",
            f"- status: `{rdk['status']}`",
            f"- member_count: `{rdk['member_count']}`",
            f"- missing_entries: `{len(rdk['missing_entries'])}`",
            f"- mismatched_entries: `{len(rdk['mismatched_entries'])}`",
            "",
            "| required path | expected entries | present entries |",
            "|---|---:|---:|",
        ]
    )
    for item in rdk["required_paths"]:
        lines.append(
            f"| `{item['path']}` | {item['expected_entries']} | {item['present_entries']} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(payload["status"])
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
