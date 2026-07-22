#!/usr/bin/env python3
"""Run the frozen Winner-v85 half/final offline support gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import build_winner_v85_integrated_support_gate_preregistration as spec  # noqa: E402


CONTRACT = ANALYSIS / "winner_v85_integrated_support_gate_preregistration.json"


def validate_contract(value: Mapping[str, Any]) -> str:
    if (
        value.get("schema_version")
        != "winner_v85.integrated_support_gate_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V85_INTEGRATED_SUPPORT_GATE"
        or value.get("decision")
        != "AUTHORIZE_ONE_FROZEN_WINNER_V85_248_CELL_GATE_ONLY"
        or value.get("selection_rule", {}).get("selected_update_if_pass") != 755
        or value.get("authority", {}).get("formal_support_gate_authorized") is not True
        or value.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v85 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v85 source manifest absent")
    for name, item in sources.items():
        if (
            item.get("hash_mode") != "lf"
            or spec.lf_sha256(ROOT / item["path"]) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v85 source changed: {name}")
    if spec.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v85 source-manifest digest changed")
    transformed, receipts = spec.transformed_source()
    transformation = value.get("transformation", {})
    if (
        transformation.get("transformed_source_sha256")
        != hashlib.sha256(transformed.encode()).hexdigest()
        or transformation.get("replacements") != receipts
        or transformation.get("replacement_groups") != len(receipts)
    ):
        raise ValueError("Winner-v85 transformed source changed")
    return transformed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError(
            "Winner-v85 requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v85 evidence")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    transformed = validate_contract(contract)
    namespace: dict[str, Any] = {
        "__file__": str(ROOT / "tools/run_winner_v85_integrated_support_gate.py"),
        "__name__": "winner_v85_transformed_support_gate",
    }
    exec(compile(transformed, namespace["__file__"], "exec"), namespace)
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            namespace["__file__"],
            "--training-work-root",
            str(args.training_work_root),
            "--playground-root",
            str(args.playground_root),
            "--canonical-fit",
            str(args.canonical_fit),
            "--output",
            str(args.output),
            "--offline-cpu-only",
            "--formal-gate-authorized",
        ]
        return int(namespace["main"]())
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
