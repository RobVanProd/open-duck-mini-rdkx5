#!/usr/bin/env python3
"""Audit local Open Duck Playground sim/morphology drift from upstream.

This is an offline evidence tool. It compares the local Playground checkout to
an upstream git ref and reports whether morphology/reference files changed, or
whether the drift is limited to training/evaluation code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "UPSTREAM_SIM_MORPHOLOGY_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "upstream_sim_morphology_audit.json"

KEY_FILES = [
    "playground/open_duck_mini_v2/data/polynomial_coefficients.pkl",
    "playground/open_duck_mini_v2/xmls/joints_properties.xml",
    "playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml",
    "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml",
    "playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml",
    "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
    "playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml",
    "playground/open_duck_mini_v2/xmls/sensors.xml",
    "playground/open_duck_mini_v2/base.py",
    "playground/open_duck_mini_v2/constants.py",
    "playground/open_duck_mini_v2/joystick.py",
    "playground/open_duck_mini_v2/runner.py",
]

MORPHOLOGY_FILES = {
    path
    for path in KEY_FILES
    if "/xmls/" in path or path.endswith("polynomial_coefficients.pkl")
}


def run_git(playground: Path, args: list[str], *, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(playground), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def git_bytes(playground: Path, ref: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "-C", str(playground), "show", f"{ref}:{path}"],
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout if result.returncode == 0 else None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_comparison(playground: Path, upstream_ref: str) -> list[dict[str, Any]]:
    rows = []
    for relpath in KEY_FILES:
        local = playground / relpath
        upstream_data = git_bytes(playground, upstream_ref, relpath)
        local_sha = sha256_file(local)
        upstream_sha = sha256_bytes(upstream_data) if upstream_data is not None else None
        rows.append(
            {
                "path": relpath,
                "local_exists": local.exists(),
                "upstream_exists": upstream_data is not None,
                "local_sha256": local_sha,
                "upstream_sha256": upstream_sha,
                "matches_upstream": (
                    local_sha is not None
                    and upstream_sha is not None
                    and local_sha == upstream_sha
                ),
                "category": "morphology_or_reference"
                if relpath in MORPHOLOGY_FILES
                else "code",
            }
        )
    return rows


def xml_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True}
    root = ET.parse(path).getroot()
    options = [element.attrib for element in root.iter("option")]
    defaults = []
    for default in root.iter("default"):
        item = {"class": default.attrib.get("class")}
        joint = default.find("joint")
        position = default.find("position")
        geom = default.find("geom")
        if joint is not None:
            item["joint"] = joint.attrib
        if position is not None:
            item["position"] = position.attrib
        if geom is not None:
            item["geom"] = geom.attrib
        defaults.append(item)
    actuators = [element.attrib for element in root.iter("position")]
    geoms = [element.attrib for element in root.iter("geom")]
    floor_geoms = [
        geom for geom in geoms if geom.get("name") == "floor" or geom.get("type") == "plane"
    ]
    return {
        "options": options,
        "defaults": defaults[:8],
        "actuator_count": len(actuators),
        "actuator_names": [item.get("name") for item in actuators if item.get("name")],
        "floor_geoms": floor_geoms,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    playground = Path(args.playground_path).resolve()
    # Fetching is explicit in the validation command; this tool only reads refs.
    head = run_git(playground, ["rev-parse", "HEAD"])
    upstream = run_git(playground, ["rev-parse", args.upstream_ref])
    branch = run_git(playground, ["branch", "--show-current"])
    remotes = run_git(playground, ["remote", "-v"])
    status = run_git(playground, ["status", "--short"])
    diff_name_status = run_git(
        playground,
        ["diff", "--name-status", f"{args.upstream_ref}...HEAD", "--", "playground/open_duck_mini_v2"],
    )
    diff_stat = run_git(
        playground,
        ["diff", "--stat", f"{args.upstream_ref}...HEAD", "--", "playground/open_duck_mini_v2"],
    )
    files = file_comparison(playground, args.upstream_ref)
    morphology_mismatches = [
        row for row in files if row["category"] == "morphology_or_reference" and not row["matches_upstream"]
    ]
    code_mismatches = [
        row for row in files if row["category"] == "code" and not row["matches_upstream"]
    ]
    if morphology_mismatches:
        status_value = "HOLD_MORPHOLOGY_OR_REFERENCE_DRIFT"
    elif code_mismatches:
        status_value = "PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY"
    else:
        status_value = "PASS_MATCHES_UPSTREAM"
    return {
        "status": status_value,
        "playground_path": str(playground),
        "branch": branch,
        "head": head,
        "upstream_ref": args.upstream_ref,
        "upstream_commit": upstream,
        "remotes": remotes.splitlines(),
        "worktree_status_short": status.splitlines(),
        "diff_name_status": diff_name_status.splitlines(),
        "diff_stat": diff_stat.splitlines(),
        "file_comparison": files,
        "morphology_mismatch_count": len(morphology_mismatches),
        "code_mismatch_count": len(code_mismatches),
        "xml_summary": {
            "open_duck_mini_v2.xml": xml_summary(
                playground / "playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml"
            ),
            "scene_flat_terrain.xml": xml_summary(
                playground / "playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml"
            ),
        },
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Upstream Sim / Morphology Audit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline audit. It does not train, deploy, SSH, or touch the robot.",
        "",
        "## Git State",
        "",
        f"- playground_path: `{payload['playground_path']}`",
        f"- branch: `{payload['branch']}`",
        f"- head: `{payload['head']}`",
        f"- upstream_ref: `{payload['upstream_ref']}`",
        f"- upstream_commit: `{payload['upstream_commit']}`",
        f"- morphology_mismatch_count: `{payload['morphology_mismatch_count']}`",
        f"- code_mismatch_count: `{payload['code_mismatch_count']}`",
        "",
        "## Drift From Upstream",
        "",
    ]
    if payload["diff_name_status"]:
        for line in payload["diff_name_status"]:
            lines.append(f"- `{line}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Key File Hashes",
            "",
            "| category | path | matches_upstream |",
            "|---|---|---:|",
        ]
    )
    for row in payload["file_comparison"]:
        lines.append(
            f"| {row['category']} | `{row['path']}` | `{row['matches_upstream']}` |"
        )
    lines.extend(
        [
            "",
            "## Physics Summary",
            "",
            "### open_duck_mini_v2.xml",
            "",
            "```json",
            json.dumps(payload["xml_summary"]["open_duck_mini_v2.xml"], indent=2)[:4000],
            "```",
            "",
            "### scene_flat_terrain.xml",
            "",
            "```json",
            json.dumps(payload["xml_summary"]["scene_flat_terrain.xml"], indent=2)[:2000],
            "```",
            "",
            "## Interpretation",
            "",
        ]
    )
    if payload["status"] == "PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY":
        lines.extend(
            [
                "- The local morphology XML and polynomial reference file match upstream byte-for-byte.",
                "- The local branch drift is in training/eval code, primarily `joystick.py` and `runner.py`.",
                "- The upstream-reference push-effectiveness failure therefore is not explained by local XML/reference-file drift.",
                "- Next audit target: runtime environment/config behavior inside `joystick.py`, termination/reward overrides, and whether the known upstream walking demo used a different checkpoint/export path or older commit.",
            ]
        )
    elif payload["status"] == "HOLD_MORPHOLOGY_OR_REFERENCE_DRIFT":
        lines.extend(
            [
                "- Morphology or reference files differ from upstream.",
                "- Resolve those differences before drawing conclusions from local reference-rollout failures.",
            ]
        )
    else:
        lines.append("- Local key files match upstream.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--upstream-ref", default="origin/main")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
