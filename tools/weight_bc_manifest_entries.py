#!/usr/bin/env python3
"""Apply reproducible per-entry sample weights to a BC trace manifest.

This is an offline curation helper. It does not train, deploy, SSH, run robot
tests, or change robot runtime behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def entry_label(entry: dict[str, Any]) -> str:
    return str(entry.get("source_name") or entry.get("source_path") or "")


def parse_rule(text: str) -> tuple[re.Pattern[str], float]:
    if "=" not in text:
        raise ValueError(f"weight rule must be REGEX=WEIGHT, got {text!r}")
    pattern, value = text.rsplit("=", 1)
    return re.compile(pattern), float(value)


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Weighted BC Manifest",
        "",
        f"status: `{payload['status']}`",
        "",
        "This offline artifact applies per-entry sample weights to a BC trace manifest.",
        "It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- input_manifest: `{payload['input_manifest']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- entries: `{payload['summary']['entries']}`",
        f"- samples: `{payload['summary']['samples']}`",
        f"- weighted_samples: `{payload['summary']['weighted_samples']:.4f}`",
        "",
        "## Rules",
        "",
    ]
    for rule in payload["rules"]:
        lines.append(f"- `{rule['pattern']}` -> `{rule['weight']}`")
    lines.extend(
        [
            "",
            "## Entries",
            "",
            "| source | samples | weight | weighted_samples | matched_rule |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for entry in payload["entries"]:
        lines.append(
            "| {source} | {samples} | {weight:.4f} | {weighted:.4f} | `{rule}` |".format(
                source=entry_label(entry),
                samples=int(entry.get("samples") or 0),
                weight=float(entry.get("sample_weight", 1.0)),
                weighted=float(entry.get("weighted_samples", 0.0)),
                rule=entry.get("sample_weight_rule") or "default",
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Weights are for offline supervised curation only.",
            "- A weighted manifest is not a candidate policy.",
            "- Robot validation remains blocked until closed-loop gates pass.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--weight-regex", action="append", default=[], help="REGEX=WEIGHT; repeatable.")
    parser.add_argument("--default-weight", type=float, default=1.0)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    payload = load_json(Path(args.manifest))
    rules = parse_rule_items = [parse_rule(item) for item in args.weight_regex]
    applied_rules = [{"pattern": item.pattern, "weight": weight} for item, weight in parse_rule_items]
    entries = []
    for entry in payload.get("entries", []):
        copied = dict(entry)
        label = entry_label(copied)
        weight = float(args.default_weight)
        matched = "default"
        for pattern, value in rules:
            if pattern.search(label) or pattern.search(str(copied.get("source_path") or "")):
                weight = float(value)
                matched = pattern.pattern
        copied["sample_weight"] = max(weight, 0.0)
        copied["sample_weight_rule"] = matched
        copied["weighted_samples"] = float(copied["sample_weight"] * int(copied.get("samples") or 0))
        entries.append(copied)

    digest_payload = {
        "input_dataset_id": payload.get("dataset_id"),
        "entries": entries,
        "rules": applied_rules,
        "default_weight": float(args.default_weight),
    }
    dataset_id = hashlib.sha256(json.dumps(digest_payload, sort_keys=True).encode()).hexdigest()[:16]
    out = dict(payload)
    out["status"] = "PASS_WEIGHTED_BC_MANIFEST_READY" if entries else "HOLD_WEIGHTED_BC_MANIFEST_EMPTY"
    out["dataset_id"] = dataset_id
    out["input_manifest"] = str(args.manifest)
    out["input_dataset_id"] = payload.get("dataset_id")
    out["rules"] = applied_rules
    out["default_weight"] = float(args.default_weight)
    out["entries"] = entries
    out["summary"] = {
        **dict(payload.get("summary") or {}),
        "entries": len(entries),
        "samples": int(sum(int(entry.get("samples") or 0) for entry in entries)),
        "weighted_samples": float(sum(float(entry.get("weighted_samples") or 0.0) for entry in entries)),
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_md(out), encoding="utf-8")
    print(f"status={out['status']}")
    print(f"dataset_id={dataset_id}")
    print(f"weighted_samples={out['summary']['weighted_samples']:.4f}")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0 if out["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
