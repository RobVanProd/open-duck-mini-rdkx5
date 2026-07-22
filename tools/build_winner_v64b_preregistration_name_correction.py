#!/usr/bin/env python3
"""Freeze the V64b injected preregistration-name correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v64b_preregistration_name_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V64B_PREREGISTRATION_NAME_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v64_isolated_persistent_teacher_step_contract.json"
INVALID = ANALYSIS / "winner_v64_isolated_persistent_teacher_invalid_invocation.json"
OLD_FRAGMENT = '''            "source_snapshot_sha256": contract["frozen_source"]["snapshot"]["sha256"],
            "objective": contract["v64"]["objective"],'''
NEW_FRAGMENT = '''            "source_snapshot_sha256": preregistration["frozen_source"]["snapshot"]["sha256"],
            "objective": preregistration["v64"]["objective"],'''


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
    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v64_isolated_persistent_teacher_step as v64

    source, _ = v64.transformed_source()
    if source.count(OLD_FRAGMENT) != 1 or NEW_FRAGMENT in source:
        raise ValueError("Winner-v64b correction fragment changed")
    corrected = source.replace(OLD_FRAGMENT, NEW_FRAGMENT)
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v64b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "611c38f246e5e2779ee7b726832ba807e8955adddf337efb3f5a7cdd5a88ff40"
        or base.get("v64", {}).get("identity")
        != "WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP"
        or invalid.get("status")
        != "INVALID_WINNER_V64_ISOLATED_PERSISTENT_TEACHER_INVOCATION"
        or invalid.get("failure", {}).get("result_json_written") is not False
        or invalid.get("failure", {}).get("committed_snapshot_writes") != 0
        or corrected.count(NEW_FRAGMENT) != 1
    ):
        raise ValueError("Winner-v64b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v64b_builder": Path(
            "tools/build_winner_v64b_preregistration_name_correction.py"
        ),
        "v64b_runner": Path(
            "tools/run_winner_v64b_preregistration_name_correction.py"
        ),
        "v64b_tests": Path(
            "tests/test_winner_v64b_preregistration_name_correction.py"
        ),
        "v64_invalid_invocation": Path(
            "outputs/analysis/winner_v64_isolated_persistent_teacher_invalid_invocation.json"
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
    value["v64b"] = {
        "identity": "WINNER_V64B_PREREGISTRATION_LOCAL_NAME_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "old_fragment_sha256": hashlib.sha256(OLD_FRAGMENT.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW_FRAGMENT.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": (
            "bind the already validated preregistration object under the base runner's "
            "actual local name during snapshot metadata persistence"
        ),
        "objective_rollout_gradient_adam_artifact_schema_or_authority_change": False,
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
                "# Winner-v64b preregistration-name correction",
                "",
                "- Identity: `WINNER_V64B_PREREGISTRATION_LOCAL_NAME_CORRECTION`",
                "- Replacement count: `1`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "- Objective/rollout/gradient/Adam/artifact schema/authority changes: `false`",
                "- Prior snapshot/result/support/robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V64B_PREREGISTRATION_NAME_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
