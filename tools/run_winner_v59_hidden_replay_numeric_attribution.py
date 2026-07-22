#!/usr/bin/env python3
"""Execute the frozen zero-update hidden-replay numeric attribution."""

from __future__ import annotations

import argparse
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

import build_winner_v59_hidden_replay_numeric_attribution_preregistration as spec  # noqa: E402


CONTRACT = ANALYSIS / "winner_v59_hidden_replay_numeric_attribution_preregistration.json"


def validate_contract(value: Mapping[str, Any]) -> str:
    if (
        value.get("schema_version")
        != "winner_v59.hidden_replay_numeric_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_EAGER_SCAN_NUMERIC_ATTRIBUTION_ONLY"
        or value.get("thresholds") != spec.THRESHOLDS
        or value.get("authority", {}).get("diagnostic_authorized") is not True
        or value.get("authority", {}).get("continuation_authorized") is not False
    ):
        raise ValueError("Winner-v59 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v59 source manifest absent")
    for name, item in sources.items():
        if (
            item.get("hash_mode") != "lf"
            or spec.lf_sha256(ROOT / item["path"]) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v59 source changed: {name}")
    if spec.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v59 source-manifest digest changed")
    transformed, receipts = spec.transformed_source()
    transformation = value.get("transformation", {})
    if (
        transformation.get("transformed_source_sha256")
        != spec.hashlib.sha256(transformed.encode()).hexdigest()
        or transformation.get("replacements") != receipts
        or transformation.get("replacement_groups") != len(receipts)
    ):
        raise ValueError("Winner-v59 transformed source changed")
    return transformed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--source-graph", type=Path, required=True)
    parser.add_argument("--teacher-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--guard-failure-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.guard_failure_attribution_authorized:
        raise PermissionError(
            "Winner-v59 requires --offline-cpu-only "
            "--guard-failure-attribution-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v59 evidence")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    transformed = validate_contract(contract)
    namespace: dict[str, Any] = {
        "__file__": str(ROOT / "tools/run_winner_v46_static_target_teacher_training.py"),
        "__name__": "winner_v59_transformed_attribution",
    }
    exec(compile(transformed, namespace["__file__"], "exec"), namespace)
    namespace["PREREGISTRATION"] = CONTRACT
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            namespace["__file__"],
            "--playground-root", str(args.playground_root),
            "--canonical-fit", str(args.canonical_fit),
            "--source-snapshot", str(args.source_snapshot),
            "--source-graph", str(args.source_graph),
            "--teacher-snapshot", str(args.teacher_snapshot),
            "--work-root", str(args.work_root),
            "--output", str(args.output),
            "--offline-cpu-only",
            "--guard-failure-attribution-authorized",
        ]
        return_code = namespace["main"]()
    finally:
        sys.argv = original_argv
    result = json.loads(args.output.read_text(encoding="utf-8"))
    result["sources"] = contract["sources"]
    result["source_manifest_sha256"] = contract["source_manifest_sha256"]
    result["transformation"] = contract["transformation"]
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
