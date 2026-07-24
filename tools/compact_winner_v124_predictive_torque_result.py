#!/usr/bin/env python3
"""Compact the hash-frozen V124 trace result for repository storage."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_RAW_SHA256 = (
    "8e880f7505a0370e8f86d10a0e9d2cbe08017dff641885b74e51328b02e87b9a"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[key]) for row in rows).items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--raw-archive-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_path = args.raw_result.resolve()
    if sha256(raw_path) != EXPECTED_RAW_SHA256:
        raise ValueError("V124 raw result hash changed")
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    v121_events = raw["s1"]["events"]["v121"]
    v123_events = raw["s1"]["events"]["v123"]
    v123_nonpreventable = [
        row for row in v123_events if not row["locally_preventable"]
    ]
    empty = raw["s2"]["empty_intersections"]
    s0 = {
        key: value
        for key, value in raw["s0"].items()
        if key != "rows"
    }
    s1b = {
        key: value
        for key, value in raw["s1"]["s1b"].items()
        if key != "rows"
    }
    compact = {
        "schema_version": "winner_v124.predictive_torque_s0_s2_compact_result.v1",
        "status": raw["status"],
        "preregistration_sha256": raw["preregistration_sha256"],
        "amendment_sha256": raw["amendment_sha256"],
        "raw_artifact": {
            "sha256": EXPECTED_RAW_SHA256,
            "bytes": raw_path.stat().st_size,
            "archive_path": str(args.raw_archive_path.resolve()),
            "repository_committed": False,
        },
        "s0": s0,
        "s1": {
            "pass": raw["s1"]["pass"],
            "checks": raw["s1"]["checks"],
            "summary": raw["s1"]["summary"],
            "s1b": s1b,
            "event_summary": {
                "v121_by_joint": counts(v121_events, "joint"),
                "v121_by_checkpoint": counts(v121_events, "checkpoint"),
                "v121_all_events": v121_events,
                "v123_by_joint": counts(v123_events, "joint"),
                "v123_by_checkpoint": counts(v123_events, "checkpoint"),
                "v123_nonpreventable_events": v123_nonpreventable,
            },
        },
        "s2": {
            "pass": raw["s2"]["pass"],
            "checks": raw["s2"]["checks"],
            "reserve_by_joint": raw["s2"]["reserve_by_joint"],
            "summary": raw["s2"]["summary"],
            "occupancy_by_joint": raw["s2"]["occupancy_by_joint"],
            "empty_intersection_summary": {
                "count": len(empty),
                "by_joint": counts(empty, "joint"),
                "sample_first_32": empty[:32],
            },
        },
        "decision": raw["decision"],
        "execution": raw["execution"],
        "authority": raw["authority"],
    }
    args.output.write_text(
        json.dumps(compact, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"sha256={sha256(args.output)}")
    print(f"bytes={args.output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
