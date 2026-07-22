#!/usr/bin/env python3
"""Freeze the V86 core-population formal-cell lookup correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v86_residual_pitch_causal.py"
PREREGISTRATION = ANALYSIS / "winner_v86_residual_pitch_causal_preregistration.json"
RESULT = ANALYSIS / "winner_v86_residual_pitch_causal_result.json"
OUTPUT = ANALYSIS / "winner_v86b_formal_cell_map_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V86B_FORMAL_CELL_MAP_CORRECTION_20260722.md"
PREREGISTRATION_SHA256 = "7516d8856f39e1bdaf53e682a1757f9a12d02527fc549ff86345e14eccd2affb"
OLD = '''    cells = checkpoint["core_model_plant_cells"] + checkpoint["sensor_transport_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}'''
NEW = '''    cells = checkpoint["core_model_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def corrected_source() -> tuple[str, str, str]:
    source = RUNNER.read_text(encoding="utf-8")
    if source.count(OLD) != 1:
        raise ValueError("Winner-v86b correction target changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v86b_corrected.py", "exec")
    return (
        corrected,
        hashlib.sha256(source.replace("\r\n", "\n").encode()).hexdigest(),
        hashlib.sha256(corrected.replace("\r\n", "\n").encode()).hexdigest(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v86b correction: {path}")
    corrected, original_hash, corrected_hash = corrected_source()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        sha256(PREREGISTRATION) != PREREGISTRATION_SHA256
        or preregistration.get("frozen_source", {}).get("failure_pair_count") != 12
        or preregistration.get("frozen_source", {}).get("diagnostic_cells") != 48
        or RESULT.exists()
    ):
        raise ValueError("Winner-v86b pre-execution boundary changed")
    source_paths = {
        "correction_builder": Path("tools/build_winner_v86b_formal_cell_map_correction.py"),
        "correction_runner": Path("tools/run_winner_v86b_formal_cell_map_correction.py"),
        "correction_tests": Path("tests/test_winner_v86b_formal_cell_map_correction.py"),
        "v86_runner": RUNNER.relative_to(ROOT),
        "v86_preregistration": PREREGISTRATION.relative_to(ROOT),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v86b.formal_cell_map_correction.v1",
        "status": "CORRECTED_WINNER_V86_FORMAL_CELL_MAP_PRE_SIMULATION",
        "decision": "RERUN_EXACT_V86_DIAGNOSTIC_WITH_CORE_FORMAL_MAP_ONLY",
        "failure": {
            "stage": "formal-cell map construction before the first gate.run_cell call",
            "exception": "ValueError: Winner-v86 formal cell population contains duplicates",
            "diagnostic_cells_completed": 0,
            "optimizer_updates": 0,
            "result_written": False,
        },
        "correction": {
            "old": "core_model_plant_cells + sensor_transport_plant_cells",
            "new": "core_model_plant_cells",
            "reason": (
                "the 12 frozen residual failures are all core-model cells; the two formal "
                "populations intentionally overlap and cannot form one unique-key map"
            ),
            "arms_pairs_thresholds_artifacts_authority_unchanged": True,
            "original_runner_lf_sha256": original_hash,
            "corrected_runner_lf_sha256": corrected_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": preregistration["authority"],
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v86b formal-cell map correction",
                "",
                "- Failed before first diagnostic cell: `yes`",
                "- Change: formal readback map uses `core_model_plant_cells` only",
                "- Arms / pairs / thresholds / artifacts / authority changed: `no`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
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
