#!/usr/bin/env python3
"""Execute exactly one frozen Winner-v64 isolated teacher step."""

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
CONTRACT = ANALYSIS / "winner_v64_isolated_persistent_teacher_step_contract.json"
BASE_RUNNER = ROOT / "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
sys.path.insert(0, str(ROOT / "tools"))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_contract(value: Mapping[str, Any]) -> None:
    v64 = value.get("v64", {})
    if (
        v64.get("identity") != "WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP"
        or v64.get("replacement_count") != 1
        or v64.get("source", {}).get("optimizer_count") != 554
        or v64.get("objective", {}).get("result_optimizer_count") != 555
        or v64.get("objective", {}).get("scale") != 136.35153198242188
        or v64.get("execution_now", {}).get("optimizer_updates") != 0
        or v64.get("authority", {}).get("one_optimizer_update_authorized") is not True
        or v64.get("authority", {}).get("continuation_training_authorized") is not False
    ):
        raise ValueError("Winner-v64 contract identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v64 source manifest absent")
    for name, item in sources.items():
        if (
            item.get("hash_mode") != "lf"
            or lf_sha256(ROOT / item["path"]) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v64 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v64 source-manifest digest changed")


def transformed_source(value: Mapping[str, Any]) -> str:
    import build_winner_v64_isolated_persistent_teacher_step as builder

    source, digest = builder.transformed_source()
    if digest != value["v64"]["transformed_source_sha256"]:
        raise ValueError("Winner-v64 transformed source changed")
    return source


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
    parser.add_argument("--one-update-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.one_update_authorized:
        raise PermissionError(
            "Winner-v64 requires --offline-cpu-only --one-update-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v64 evidence")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v64 summary: {markdown}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    source = transformed_source(contract)
    namespace: dict[str, Any] = {
        "__file__": str(BASE_RUNNER),
        "__name__": "winner_v64_isolated_teacher_step",
        "V64_WORK_ROOT": args.work_root,
    }
    exec(compile(source, str(BASE_RUNNER), "exec"), namespace)
    namespace["PREREGISTRATION"] = CONTRACT
    original_argv = sys.argv[:]
    try:
        with tempfile.TemporaryDirectory(prefix="winner-v64-") as temporary:
            temporary_result = Path(temporary) / "v63.json"
            temporary_markdown = Path(temporary) / "v63.md"
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
            base_return = namespace["main"]()
            attribution = json.loads(temporary_result.read_text(encoding="utf-8"))
    finally:
        sys.argv = original_argv
    artifact = namespace.get("V64_ARTIFACT")
    if not isinstance(artifact, Mapping):
        raise ValueError("Winner-v64 artifact was not produced")
    checks = dict(artifact["checks"])
    checks["base_attribution_passed"] = base_return == 0 and not attribution["failed_checks"]
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v64.isolated_persistent_teacher_step_result.v1",
        "status": (
            "PASS_WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP"
            if not failed
            else "HOLD_WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP"
        ),
        "decision": (
            "PREREGISTER_BOUNDED_ISOLATED_PERSISTENT_TEACHER_CONTINUATION_ONLY"
            if not failed
            else "DO_NOT_CONTINUE_ISOLATED_PERSISTENT_TEACHER_TRAINING"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source": contract["v64"]["source"],
        "objective": contract["v64"]["objective"],
        "optimization": artifact["optimization"],
        "snapshot": artifact["snapshot"],
        "graph": artifact["graph"],
        "attribution_replay": {
            "classification": attribution["classification"],
            "decision": attribution["decision"],
            "checks": attribution["checks"],
        },
        "execution": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20000,
            "optimizer_updates": 1,
            "continuation_updates": 0,
            "formal_support_cells": 0,
            "candidate_graph_exports": 1,
            "robot_or_rdk_access": 0,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "continuation_training_executed": False,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered bounded isolated-teacher continuation"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v64 isolated persistent-teacher step result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Optimizer: `554 -> {artifact['optimization']['optimizer_count_after']}`",
                f"- Loss: `{artifact['optimization']['loss_before']} -> {artifact['optimization']['loss_after']}`",
                f"- Snapshot SHA-256: `{artifact['snapshot']['sha256']}`",
                f"- ONNX SHA-256: `{artifact['graph']['sha256']}`",
                "- Continuation / support / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
