#!/usr/bin/env python3
"""Execute the frozen one-fragment Winner-v63b loader correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v63b_training_snapshot_loader_correction.json"
BASE_RUNNER = ROOT / "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
OLD_FRAGMENT = '''    snapshot = v61.load_snapshot_for_reviewed_gate(checkpoint_path)
    v61.validate_snapshot_for_reviewed_gate(snapshot)'''
NEW_FRAGMENT = '''    snapshot = v22v2.load_snapshot(checkpoint_path)
    v61._validate_snapshot(
        snapshot, expected_stage="integrated_first_tick_teacher_joint_stage2"
    )'''


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def corrected_source(value: Mapping[str, Any]) -> str:
    source = BASE_RUNNER.read_text(encoding="utf-8")
    correction = value["correction"]
    if (
        source.count(OLD_FRAGMENT) != 1
        or NEW_FRAGMENT in source
        or lf_sha256(BASE_RUNNER) != correction["frozen_runner_lf_sha256"]
        or hashlib.sha256(OLD_FRAGMENT.encode()).hexdigest()
        != correction["old_fragment_sha256"]
        or hashlib.sha256(NEW_FRAGMENT.encode()).hexdigest()
        != correction["new_fragment_sha256"]
    ):
        raise ValueError("Winner-v63b frozen correction source changed")
    corrected = source.replace(OLD_FRAGMENT, NEW_FRAGMENT)
    if (
        corrected.count(NEW_FRAGMENT) != 1
        or hashlib.sha256(corrected.encode()).hexdigest()
        != correction["corrected_source_sha256"]
    ):
        raise ValueError("Winner-v63b corrected source digest changed")
    return corrected


def validate_contract(value: Mapping[str, Any]) -> None:
    correction = value.get("correction", {})
    if (
        value.get("schema_version")
        != "winner_v63.persistent_teacher_conflict_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
        or correction.get("identity")
        != "WINNER_V63B_EXACT_TRAINING_SNAPSHOT_LOADER_CORRECTION"
        or correction.get("replacement_count") != 1
        or correction.get(
            "objective_rollout_gradient_adam_classification_or_authority_change"
        )
        is not False
        or value.get("frozen_execution", {}).get("committed_optimizer_updates")
        != 0
    ):
        raise ValueError("Winner-v63b contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v63b source manifest absent")
    for name, item in sources.items():
        if (
            item.get("hash_mode") != "lf"
            or lf_sha256(ROOT / item["path"]) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v63b source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v63b source-manifest digest changed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--teacher-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--loader-correction-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.loader_correction_authorized:
        raise PermissionError(
            "Winner-v63b requires --offline-cpu-only --loader-correction-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v63b result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v63b summary: {markdown}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    source = corrected_source(contract)
    namespace: dict[str, Any] = {
        "__file__": str(BASE_RUNNER),
        "__name__": "winner_v63b_corrected_attribution",
    }
    exec(compile(source, str(BASE_RUNNER), "exec"), namespace)
    namespace["PREREGISTRATION"] = CONTRACT
    original_argv = sys.argv[:]
    try:
        with tempfile.TemporaryDirectory(prefix="winner-v63b-") as temporary:
            temporary_result = Path(temporary) / "winner_v63_result.json"
            temporary_markdown = Path(temporary) / "winner_v63_result.md"
            sys.argv = [
                str(BASE_RUNNER),
                "--training-work-root",
                str(args.training_work_root),
                "--teacher-snapshot",
                str(args.teacher_snapshot),
                "--playground-root",
                str(args.playground_root),
                "--canonical-fit",
                str(args.canonical_fit),
                "--output",
                str(temporary_result),
                "--markdown",
                str(temporary_markdown),
                "--offline-cpu-only",
                "--conflict-attribution-authorized",
            ]
            return_code = namespace["main"]()
            result = json.loads(temporary_result.read_text(encoding="utf-8"))
    finally:
        sys.argv = original_argv
    result["schema_version"] = (
        "winner_v63b.persistent_teacher_conflict_result.v1"
    )
    result["status"] = result["status"].replace("WINNER_V63_", "WINNER_V63B_")
    result["correction"] = contract["correction"]
    result["sources"] = contract["sources"]
    result["source_manifest_sha256"] = contract["source_manifest_sha256"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v63b persistent-teacher conflict attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                "- Loader correction: exact training-coordinate snapshot",
                "- Committed optimizer / support / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
