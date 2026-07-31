#!/usr/bin/env python3
"""Split BC manifest samples into phase-quadrant manifests.

This is an offline analysis helper for the live-oracle phase-student branch.
It reads one or more existing BC manifests and writes four per-quadrant
manifests using the two phase channels in the 101-observation contract.

The split rule is intentionally simple and ONNX-friendly:

  bin 0: obs[a] >= 0 and obs[b] >= 0
  bin 1: obs[a] <  0 and obs[b] >= 0
  bin 2: obs[a] <  0 and obs[b] <  0
  bin 3: obs[a] >= 0 and obs[b] <  0

It does not train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

import numpy as np


def phase_bin(obs: list[float], phase_a_index: int, phase_b_index: int) -> int:
    a = float(obs[phase_a_index])
    b = float(obs[phase_b_index])
    if a >= 0.0 and b >= 0.0:
        return 0
    if a < 0.0 and b >= 0.0:
        return 1
    if a < 0.0 and b < 0.0:
        return 2
    return 3


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.4f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="append", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--phase-a-index", type=int, default=99)
    parser.add_argument("--phase-b-index", type=int, default=100)
    parser.add_argument("--output-md", default="outputs/analysis/PHASE_SPLIT_BC_MANIFEST.md")
    parser.add_argument("--output-json", default="outputs/analysis/phase_split_bc_manifest.json")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bins: dict[int, list[dict[str, Any]]] = {index: [] for index in range(4)}
    source_counts: Counter[str] = Counter()
    skipped = 0

    for manifest_path_text in args.manifest:
        manifest_path = Path(manifest_path_text)
        manifest = json.loads(manifest_path.read_text())
        for entry in manifest.get("entries", []):
            if not entry.get("bc_ready", False):
                continue
            source_path = Path(entry["source_path"])
            if not source_path.exists():
                skipped += 1
                continue
            for row in read_jsonl(source_path):
                obs = row.get("obs_state")
                action = row.get("action")
                if not (
                    isinstance(obs, list)
                    and len(obs) == 101
                    and isinstance(action, list)
                    and len(action) == 14
                ):
                    skipped += 1
                    continue
                bin_index = phase_bin(obs, int(args.phase_a_index), int(args.phase_b_index))
                out_row = dict(row)
                out_row["phase_split_source_path"] = str(source_path)
                out_row["phase_split_bin"] = bin_index
                bins[bin_index].append(out_row)
                source_counts[str(source_path)] += 1

    manifests = {}
    for bin_index, rows in bins.items():
        bin_dir = output_dir / f"phase_bin_{bin_index}"
        jsonl_path = bin_dir / "samples.jsonl"
        manifest_path = bin_dir / "manifest.json"
        write_jsonl(jsonl_path, rows)
        manifest_payload = {
            "status": "PASS_PHASE_SPLIT_MANIFEST_READY" if rows else "HOLD_PHASE_SPLIT_EMPTY",
            "dataset_id": f"phase_bin_{bin_index}",
            "phase_bin": bin_index,
            "phase_a_index": int(args.phase_a_index),
            "phase_b_index": int(args.phase_b_index),
            "entries": [
                {
                    "source_path": str(jsonl_path),
                    "mode": f"phase_bin_{bin_index}",
                    "bc_ready": bool(rows),
                    "samples": len(rows),
                }
            ],
        }
        manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n")
        manifests[str(bin_index)] = {
            "manifest": str(manifest_path),
            "samples_jsonl": str(jsonl_path),
            "samples": len(rows),
        }

    sample_counts = np.asarray([item["samples"] for item in manifests.values()], dtype=float)
    report = {
        "status": "PASS_PHASE_SPLIT_MANIFESTS_READY"
        if all(item["samples"] > 0 for item in manifests.values())
        else "HOLD_PHASE_SPLIT_EMPTY_BIN",
        "input_manifests": args.manifest,
        "output_dir": str(output_dir),
        "phase_a_index": int(args.phase_a_index),
        "phase_b_index": int(args.phase_b_index),
        "manifests": manifests,
        "skipped": int(skipped),
        "source_paths": len(source_counts),
        "samples_total": int(sum(item["samples"] for item in manifests.values())),
        "samples_min": int(np.min(sample_counts)) if sample_counts.size else 0,
        "samples_max": int(np.max(sample_counts)) if sample_counts.size else 0,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Phase-Split BC Manifest",
        "",
        f"status: `{report['status']}`",
        "",
        f"- output_dir: `{report['output_dir']}`",
        f"- phase indices: `{report['phase_a_index']}`, `{report['phase_b_index']}`",
        f"- samples_total: `{report['samples_total']}`",
        f"- skipped: `{report['skipped']}`",
        "",
        "| phase_bin | samples | manifest |",
        "|---:|---:|---|",
    ]
    for bin_index, item in manifests.items():
        lines.append(
            f"| {bin_index} | {item['samples']} | `{item['manifest']}` |"
        )
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(report["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if report["status"] == "PASS_PHASE_SPLIT_MANIFESTS_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
