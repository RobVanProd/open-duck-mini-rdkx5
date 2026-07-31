#!/usr/bin/env python3
"""Execute the frozen Winner-v52 full-action-teacher continuation."""

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

import build_winner_v52_full_action_teacher_training_preregistration as spec  # noqa: E402


CONTRACT = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"


def validate_contract(value: Mapping[str, Any]) -> str:
    if (
        value.get("schema_version")
        != "winner_v52.full_action_teacher_training_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V52_FULL_ACTION_TEACHER_TRAINING"
        or value.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_FULL_ACTION_TEACHER_ARM_ONLY"
        or value.get("frozen_training", {}).get("source_completed_updates") != 353
        or value.get("frozen_training", {}).get("continuation_optimizer_updates")
        != 100
        or value.get("frozen_training", {}).get("persistent_checkpoints")
        != {"half": 403, "final": 453}
        or value.get("authority", {}).get("training_authorized") is not True
        or value.get("authority", {}).get("formal_support_gate_authorized")
        is not False
    ):
        raise ValueError("Winner-v52 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v52 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or spec.lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v52 source changed: {name}")
    if spec.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v52 source-manifest digest changed")
    transformed, receipts = spec.transformed_source()
    transformation = value.get("transformation", {})
    if (
        transformation.get("base_runner_lf_sha256") != spec.lf_sha256(spec.V46_RUNNER)
        or transformation.get("transformed_source_sha256")
        != spec.hashlib.sha256(transformed.encode()).hexdigest()
        or transformation.get("replacements") != receipts
        or transformation.get("replacement_groups") != len(spec.TRANSFORMS)
    ):
        raise ValueError("Winner-v52 transformed source changed")
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
    parser.add_argument("--full-action-teacher-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.full_action_teacher_training_authorized:
        raise PermissionError(
            "Winner-v52 requires --offline-cpu-only "
            "--full-action-teacher-training-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v52 evidence")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    transformed = validate_contract(contract)
    namespace: dict[str, Any] = {
        "__file__": str(spec.V46_RUNNER),
        "__name__": "winner_v52_transformed_training",
    }
    exec(compile(transformed, str(spec.V46_RUNNER), "exec"), namespace)
    namespace["PREREGISTRATION"] = CONTRACT
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            str(spec.V46_RUNNER),
            "--playground-root", str(args.playground_root),
            "--canonical-fit", str(args.canonical_fit),
            "--source-snapshot", str(args.source_snapshot),
            "--source-graph", str(args.source_graph),
            "--teacher-snapshot", str(args.teacher_snapshot),
            "--work-root", str(args.work_root),
            "--output", str(args.output),
            "--offline-cpu-only",
            "--full-action-teacher-training-authorized",
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
