#!/usr/bin/env python3
"""Run the frozen corrected Winner-v87 diagnostic source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main() -> int:
    import build_winner_v87b_teacher_population_correction as builder

    correction = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
    source, original_hash, corrected_hash = builder.corrected_source()
    if (
        correction.get("status")
        != "CORRECTED_WINNER_V87_TEACHER_POPULATION_PRE_ROLLOUT"
        or correction.get("decision")
        != "RERUN_EXACT_V87_AUDIT_ON_TWELVE_SELECTED_TEACHER_CONFIGURATIONS"
        or correction.get("correction", {}).get("original_runner_lf_sha256")
        != original_hash
        or correction.get("correction", {}).get("corrected_runner_lf_sha256")
        != corrected_hash
    ):
        raise ValueError("Winner-v87b correction identity changed")
    for name, item in correction["sources"].items():
        if builder.lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v87b correction source changed: {name}")
    if (
        builder.canonical_sha256(correction["sources"])
        != correction["source_manifest_sha256"]
    ):
        raise ValueError("Winner-v87b correction source manifest changed")
    if hashlib.sha256(source.replace("\r\n", "\n").encode()).hexdigest() != corrected_hash:
        raise ValueError("Winner-v87b corrected source changed")
    namespace: dict[str, Any] = {
        "__file__": str(Path(__file__)),
        "__name__": "winner_v87b_corrected_pitch_head_linear_feasibility",
    }
    exec(compile(source, str(Path(__file__)), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
