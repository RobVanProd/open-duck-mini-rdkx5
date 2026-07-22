#!/usr/bin/env python3
"""Preregister the complete nine-pair residual-teacher causal diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v79_complete_residual_teacher_causal_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V79_COMPLETE_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md"
V77_PREREGISTRATION = ANALYSIS / "winner_v77_residual_teacher_causal_preregistration.json"
V77_RESULT = ANALYSIS / "winner_v77_residual_teacher_causal_result.json"
V78_RESULT = ANALYSIS / "winner_v78_missing_teacher_extension_result.json"
V78_RESULT_SHA256 = "a2fe470324c7aa59574e7e01cba339ef0a1eb6a4215464fc617318085537e2c4"

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v77b_population_authorization_correction as v77b  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def replace_exact(source: str, old: str, new: str, *, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v79 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def transformed_source() -> tuple[str, str]:
    source, _ = v77b.corrected_source()
    for old, new in (
        ("Winner-v77", "Winner-v79"),
        ("winner_v77", "winner_v79"),
        ("WINNER_V77", "WINNER_V79"),
    ):
        if source.count(old) <= 0:
            raise ValueError(f"Winner-v79 transform token absent: {old}")
        source = source.replace(old, new)
    source = replace_exact(
        source,
        'V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"',
        'V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"\n'
        'V78_RESULT = ANALYSIS / "winner_v78_missing_teacher_extension_result.json"',
    )
    old_load = (
        "    teacher_table = v43.load_teacher_table("
        "json.loads(V42_RESULT.read_text(encoding=\"utf-8\")))\n"
        "    if any(row[\"configuration_id\"] not in by_id or "
        "row[\"configuration_id\"] not in teacher_table for row in failure_pairs):"
    )
    new_load = '''    teacher_table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    extension_result = json.loads(V78_RESULT.read_text(encoding="utf-8"))
    extension = extension_result.get("teacher_table_extension", {}).get("COM_CORNER_07")
    extension_replays = extension_result.get("configuration_result", {}).get(
        "selected_replay_results", []
    )
    if (
        extension_result.get("status") != "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
        or extension_result.get("decision")
        != "AUTHORIZE_SEPARATELY_PREREGISTERED_RESIDUAL_TEACHER_DIAGNOSTIC_ONLY"
        or sha256(V78_RESULT) != preregistration["frozen_source"]["v78_result_sha256"]
        or not isinstance(extension, dict)
        or extension.get("shared_support_pass") is not True
        or len(extension_replays) != 2
        or any(
            replay.get("support_pass") is not True or replay.get("terminal") is not None
            for replay in extension_replays
        )
    ):
        raise ValueError("Winner-v79 teacher extension changed")
    extension_action = v43.expand_coordinates(extension["coordinates"])
    if any(
        replay.get("raw_target_sha256") != v43.array_sha256(extension_action)
        for replay in extension_replays
    ):
        raise ValueError("Winner-v79 teacher extension replay binding changed")
    extension_action.setflags(write=False)
    teacher_table["COM_CORNER_07"] = extension_action
    if any(row["configuration_id"] not in by_id or row["configuration_id"] not in teacher_table for row in failure_pairs):'''
    source = replace_exact(source, old_load, new_load)
    source = replace_exact(
        source,
        '"full_teacher_all_13_pass": support_counts["full_teacher"] == 13,',
        '"full_teacher_all_9_pass": support_counts["full_teacher"] == 9,',
    )
    source = replace_exact(
        source,
        '            "v76_result_sha256": sha256(V76_RESULT),',
        '            "v76_result_sha256": sha256(V76_RESULT),\n'
        '            "v78_result_sha256": sha256(V78_RESULT),',
    )
    compile(source, "winner_v79_complete_residual_teacher_causal.py", "exec")
    return source, hashlib.sha256(source.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v79 contract: {path}")
    base = json.loads(V77_PREREGISTRATION.read_text(encoding="utf-8"))
    extension = json.loads(V78_RESULT.read_text(encoding="utf-8"))
    transformed, transformed_hash = transformed_source()
    if (
        sha256(V77_PREREGISTRATION)
        != "4aa1ea646f03e1e2aac26014e1b625f0441f028102e0526db9321d84c969f322"
        or base.get("frozen_source", {}).get("formal_failed_cells") != 9
        or base.get("frozen_execution", {}).get("diagnostic_cells") != 36
        or sha256(V78_RESULT) != V78_RESULT_SHA256
        or extension.get("status") != "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
        or not all(extension.get("checks", {}).values())
        or extension.get("authority", {}).get("robot_clearance") is not False
        or V77_RESULT.exists()
    ):
        raise ValueError("Winner-v79 source authority changed")

    source_paths = {
        "v79_builder": Path(
            "tools/build_winner_v79_complete_residual_teacher_causal_preregistration.py"
        ),
        "v79_runner": Path("tools/run_winner_v79_complete_residual_teacher_causal.py"),
        "v79_tests": Path("tests/test_winner_v79_complete_residual_teacher_causal.py"),
        "v77_preregistration": Path(
            "outputs/analysis/winner_v77_residual_teacher_causal_preregistration.json"
        ),
        "v77b_correction": Path(
            "outputs/analysis/winner_v77b_population_authorization_correction.json"
        ),
        "v77b_correction_builder": Path(
            "tools/build_winner_v77b_population_authorization_correction.py"
        ),
        "v78_result": Path("outputs/analysis/winner_v78_missing_teacher_extension_result.json"),
        "v78_preregistration": Path(
            "outputs/analysis/winner_v78_missing_teacher_extension_preregistration.json"
        ),
        "teacher_abi": Path("patches/winner_v43_static_target_teacher.py"),
    }
    sources = dict(base["sources"])
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in source_paths.items()
        }
    )
    value = dict(base)
    value["schema_version"] = "winner_v79.residual_teacher_causal_preregistration.v1"
    value["status"] = "PREREGISTERED_WINNER_V79_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
    value["causal_question"] = (
        "With complete replay-bound static-teacher coverage, does the frozen full teacher "
        "rescue every final Winner-v76 failure, and is the mismatch still localized to "
        "the six pitch outputs?"
    )
    frozen = dict(base["frozen_source"])
    frozen["v78_result_sha256"] = V78_RESULT_SHA256
    frozen["teacher_configuration_extension"] = "COM_CORNER_07"
    frozen["teacher_extension_coordinates"] = [0.25, -0.25, 0.25]
    value["frozen_source"] = frozen
    value["transformation"] = {
        "v77b_corrected_source_sha256": v77b.corrected_source()[1],
        "transformed_source_sha256": transformed_hash,
    }
    value["sources"] = sources
    value["source_manifest_sha256"] = canonical_sha256(sources)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v79 complete residual-teacher causal preregistration",
                "",
                "- Population: `9 exact failed pairs x 4 arms = 36 cells`",
                "- Static-teacher coverage: `complete`, including replay-bound `COM_CORNER_07`",
                "- Checkpoint: exact Winner-v75 final update `655`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
