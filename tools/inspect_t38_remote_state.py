#!/usr/bin/env python3
"""Print a read-only inventory of T38 state in the current Colab runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(path: Path) -> dict[str, object]:
    row: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
    }
    if path.is_file():
        row["bytes"] = path.stat().st_size
        row["sha256"] = sha256(path)
    if path.is_dir():
        children = sorted(path.iterdir())
        row["child_count"] = len(children)
        row["children"] = [item.name for item in children[:100]]
    return row


roots = [
    Path("/content/t38-frozen-normalizer-hosted-20260727.tar.gz"),
    Path("/content/t38_launch"),
    Path("/content/t38_work"),
    Path("/content/t38_result.json"),
    Path("/content/t38_artifacts.tar.gz"),
    Path("/content/t38_launch_receipt.json"),
]
rows = [describe(path) for path in roots]
content_matches = sorted(
    path
    for path in Path("/content").rglob("*")
    if "t38" in path.name.lower()
)
processes = subprocess.run(
    ["ps", "-eo", "pid,etimes,stat,cmd"],
    capture_output=True,
    text=True,
    check=False,
)
print(
    json.dumps(
        {
            "schema_version": "open_duck.t38_remote_inventory.v1",
            "roots": rows,
            "t38_matches": [str(path) for path in content_matches[:500]],
            "t38_match_count": len(content_matches),
            "processes": [
                line
                for line in processes.stdout.splitlines()
                if "t38" in line.lower()
                or "open_duck" in line.lower()
                or "runner.py" in line.lower()
            ],
        },
        indent=2,
        sort_keys=True,
    )
)
