#!/usr/bin/env python3
"""Freeze the sole Winner-v77b 52-to-36-cell authorization correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v77b_population_authorization_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V77B_POPULATION_AUTHORIZATION_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v77_residual_teacher_causal_preregistration.json"
INVALID = ANALYSIS / "winner_v77_residual_teacher_causal_invalid_invocation.json"
RESULT = ANALYSIS / "winner_v77_residual_teacher_causal_result.json"
OLD = "AUTHORIZE_ONE_READ_ONLY_52_CELL_CPU_DIAGNOSTIC_ONLY"
NEW = "AUTHORIZE_ONE_READ_ONLY_36_CELL_CPU_DIAGNOSTIC_ONLY"

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v77_residual_teacher_causal_preregistration as v77  # noqa: E402


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
    source, _ = v77.transformed_source()
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v77b correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v77b_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v77b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "4aa1ea646f03e1e2aac26014e1b625f0441f028102e0526db9321d84c969f322"
        or base.get("status")
        != "PREREGISTERED_WINNER_V77_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or base.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_36_CELL_CPU_DIAGNOSTIC_ONLY"
        or invalid.get("status")
        != "INVALID_WINNER_V77_STALE_52_CELL_AUTHORIZATION_STRING"
        or invalid.get("authority", {}).get("diagnostic_cells") != 0
        or invalid.get("failure", {}).get("result_written") is not False
        or RESULT.exists()
        or corrected.count(NEW) != 1
    ):
        raise ValueError("Winner-v77b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v77b_builder": Path(
            "tools/build_winner_v77b_population_authorization_correction.py"
        ),
        "v77b_runner": Path(
            "tools/run_winner_v77b_population_authorization_correction.py"
        ),
        "v77b_tests": Path(
            "tests/test_winner_v77b_population_authorization_correction.py"
        ),
        "v77_invalid_invocation": Path(
            "outputs/analysis/winner_v77_residual_teacher_causal_invalid_invocation.json"
        ),
    }
    sources.update(
        {
            name: {
                "path": path.as_posix(),
                "hash_mode": "lf",
                "sha256": lf_sha256(ROOT / path),
            }
            for name, path in additions.items()
        }
    )
    value = dict(base)
    value["v77b"] = {
        "identity": "WINNER_V77B_POPULATION_AUTHORIZATION_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "old_fragment_sha256": hashlib.sha256(OLD.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": "make the copied authorization string equal the already frozen 36-cell population",
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
                "# Winner-v77b population-authorization correction",
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
    print("PREREGISTERED_WINNER_V77B_POPULATION_AUTHORIZATION_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
