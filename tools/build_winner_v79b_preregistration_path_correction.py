#!/usr/bin/env python3
"""Freeze the sole Winner-v79b preregistration-path correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v79b_preregistration_path_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V79B_PREREGISTRATION_PATH_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v79_complete_residual_teacher_causal_preregistration.json"
INVALID = ANALYSIS / "winner_v79_complete_residual_teacher_causal_invalid_invocation.json"
RESULT = ANALYSIS / "winner_v79_complete_residual_teacher_causal_result.json"
OLD = "winner_v79_residual_teacher_causal_preregistration.json"
NEW = "winner_v79_complete_residual_teacher_causal_preregistration.json"

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v79_complete_residual_teacher_causal_preregistration as v79  # noqa: E402


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


def corrected_source() -> tuple[str, str]:
    source, _ = v79.transformed_source()
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v79b correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v79b_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v79b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "de083ee1bbf46d633a80bcfb05c835647f3e662f68c6a284c4f13301b6c289e1"
        or base.get("status")
        != "PREREGISTERED_WINNER_V79_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or invalid.get("status") != "INVALID_WINNER_V79_PREREGISTRATION_PATH"
        or invalid.get("authority", {}).get("diagnostic_cells") != 0
        or invalid.get("failure", {}).get("result_written") is not False
        or RESULT.exists()
        or corrected.count(NEW) != 1
    ):
        raise ValueError("Winner-v79b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v79b_builder": Path("tools/build_winner_v79b_preregistration_path_correction.py"),
        "v79b_runner": Path("tools/run_winner_v79b_preregistration_path_correction.py"),
        "v79b_tests": Path("tests/test_winner_v79b_preregistration_path_correction.py"),
        "v79_invalid_invocation": Path(
            "outputs/analysis/winner_v79_complete_residual_teacher_causal_invalid_invocation.json"
        ),
    }
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in additions.items()
        }
    )
    value = dict(base)
    value["v79b"] = {
        "identity": "WINNER_V79B_PREREGISTRATION_PATH_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "old_fragment_sha256": hashlib.sha256(OLD.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": "open the already frozen V79 preregistration filename",
        "population_arm_threshold_model_or_authority_change": False,
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
                "# Winner-v79b preregistration-path correction",
                "",
                "- Replacement count: `1`",
                "- Prior diagnostic cells / optimizer / locomotion / robot: `0 / 0 / 0 / 0`",
                "- Population/arm/threshold/model/authority changes: `false`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V79B_PREREGISTRATION_PATH_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
