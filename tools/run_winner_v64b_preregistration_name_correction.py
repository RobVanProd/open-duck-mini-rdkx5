#!/usr/bin/env python3
"""Execute the frozen Winner-v64b local-name correction."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v64b_preregistration_name_correction.json"
sys.path.insert(0, str(TOOLS))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--teacher-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--name-correction-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.name_correction_authorized:
        raise PermissionError(
            "Winner-v64b requires --offline-cpu-only --name-correction-authorized"
        )
    import build_winner_v64b_preregistration_name_correction as builder
    import run_winner_v64_isolated_persistent_teacher_step as base

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    base.validate_contract(contract)
    corrected, digest = builder.corrected_source()
    if digest != contract["v64b"]["corrected_source_sha256"]:
        raise ValueError("Winner-v64b corrected source changed")
    original_contract = base.CONTRACT
    original_transform = base.transformed_source
    original_argv = sys.argv[:]
    try:
        base.CONTRACT = CONTRACT
        base.transformed_source = lambda _value: corrected
        sys.argv = [
            str(Path(base.__file__)),
            "--training-work-root",
            str(args.training_work_root),
            "--teacher-snapshot",
            str(args.teacher_snapshot),
            "--playground-root",
            str(args.playground_root),
            "--canonical-fit",
            str(args.canonical_fit),
            "--work-root",
            str(args.work_root),
            "--output",
            str(args.output),
            "--offline-cpu-only",
            "--one-update-authorized",
        ]
        if args.markdown is not None:
            sys.argv.extend(["--markdown", str(args.markdown)])
        return_code = base.main()
    finally:
        base.CONTRACT = original_contract
        base.transformed_source = original_transform
        sys.argv = original_argv
    result = json.loads(args.output.read_text(encoding="utf-8"))
    result["schema_version"] = (
        "winner_v64b.isolated_persistent_teacher_step_result.v1"
    )
    result["status"] = result["status"].replace("WINNER_V64_", "WINNER_V64B_")
    result["v64b"] = contract["v64b"]
    result["sources"] = contract["sources"]
    result["source_manifest_sha256"] = contract["source_manifest_sha256"]
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
