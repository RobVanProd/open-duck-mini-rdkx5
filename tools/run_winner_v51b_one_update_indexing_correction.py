#!/usr/bin/env python3
"""Execute the frozen one-line Winner-v51b indexing correction."""

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
CONTRACT = ANALYSIS / "winner_v51b_one_update_indexing_correction_contract.json"
V51_RUNNER = ROOT / "tools/run_winner_v51_full_action_teacher_one_update_cpu_proof.py"
OLD_FRAGMENT = '''    full_gradient_max = recomputed["objective_evidence"]
    ["full_teacher_gradient_max_abs"]'''
NEW_FRAGMENT = '''    full_gradient_max = recomputed["objective_evidence"][
        "full_teacher_gradient_max_abs"
    ]'''


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def corrected_source(value: Mapping[str, Any]) -> str:
    source = V51_RUNNER.read_text(encoding="utf-8")
    correction = value["correction"]
    if (
        source.count(OLD_FRAGMENT) != 1
        or NEW_FRAGMENT in source
        or lf_sha256(V51_RUNNER) != correction["frozen_runner_lf_sha256"]
        or hashlib.sha256(OLD_FRAGMENT.encode()).hexdigest()
        != correction["old_fragment_sha256"]
        or hashlib.sha256(NEW_FRAGMENT.encode()).hexdigest()
        != correction["new_fragment_sha256"]
    ):
        raise ValueError("Winner-v51b frozen correction source changed")
    corrected = source.replace(OLD_FRAGMENT, NEW_FRAGMENT)
    if (
        corrected.count(NEW_FRAGMENT) != 1
        or hashlib.sha256(corrected.encode()).hexdigest()
        != correction["corrected_source_sha256"]
    ):
        raise ValueError("Winner-v51b corrected source digest changed")
    return corrected


def validate_contract(value: Mapping[str, Any]) -> None:
    correction = value.get("correction", {})
    if (
        value.get("schema_version")
        != "winner_v51.full_action_teacher_one_update_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
        or correction.get("identity")
        != "WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION"
        or correction.get("replacement_count") != 1
        or correction.get("optimizer_objective_artifact_or_gate_change") is not False
        or value.get("execution_future", {}).get("optimizer_updates") != 1
    ):
        raise ValueError("Winner-v51b contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v51b source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v51b source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v51b source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v46-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-full-action-teacher-correction-authorized", action="store_true")
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.one_update_full_action_teacher_correction_authorized
    ):
        raise PermissionError(
            "Winner-v51b requires --offline-cpu-only and "
            "--one-update-full-action-teacher-correction-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v51b evidence")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    source = corrected_source(contract)
    namespace: dict[str, Any] = {
        "__file__": str(V51_RUNNER),
        "__name__": "winner_v51b_corrected_proof",
    }
    exec(compile(source, str(V51_RUNNER), "exec"), namespace)
    namespace["CONTRACT"] = CONTRACT
    original_argv = sys.argv[:]
    try:
        with tempfile.TemporaryDirectory(prefix="winner-v51b-") as temporary:
            temporary_result = Path(temporary) / "winner_v51_result.json"
            sys.argv = [
                str(V51_RUNNER),
                "--playground-root", str(args.playground_root),
                "--canonical-fit", str(args.canonical_fit),
                "--v46-training-work-root", str(args.v46_training_work_root),
                "--v22-training-work-root", str(args.v22_training_work_root),
                "--work-root", str(args.work_root),
                "--output", str(temporary_result),
                "--offline-cpu-only",
                "--one-update-full-action-teacher-proof-authorized",
            ]
            return_code = namespace["main"]()
            result = json.loads(temporary_result.read_text(encoding="utf-8"))
    finally:
        sys.argv = original_argv

    result["schema_version"] = "winner_v51b.full_action_teacher_one_update_cpu_result.v1"
    result["status"] = result["status"].replace("WINNER_V51_", "WINNER_V51B_")
    result["correction"] = contract["correction"]
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
