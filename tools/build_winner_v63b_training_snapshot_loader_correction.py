#!/usr/bin/env python3
"""Freeze the Winner-v63b exact training-snapshot loader correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v63b_training_snapshot_loader_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V63B_TRAINING_SNAPSHOT_LOADER_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v63_persistent_teacher_conflict_preregistration.json"
INVALID = ANALYSIS / "winner_v63_persistent_teacher_conflict_invalid_invocation.json"
BASE_RUNNER = ROOT / "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
OLD_FRAGMENT = '''    snapshot = v61.load_snapshot_for_reviewed_gate(checkpoint_path)
    v61.validate_snapshot_for_reviewed_gate(snapshot)'''
NEW_FRAGMENT = '''    snapshot = v22v2.load_snapshot(checkpoint_path)
    v61._validate_snapshot(
        snapshot, expected_stage="integrated_first_tick_teacher_joint_stage2"
    )'''


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
    source = BASE_RUNNER.read_text(encoding="utf-8")
    if source.count(OLD_FRAGMENT) != 1 or NEW_FRAGMENT in source:
        raise ValueError("Winner-v63b correction fragment changed")
    corrected = source.replace(OLD_FRAGMENT, NEW_FRAGMENT)
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v63b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "c60abbd0a7e8a0ffd2bf26adb377868da09c154e88abcc8e83b1ac73294fbc07"
        or base.get("status")
        != "PREREGISTERED_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
        or invalid.get("status")
        != "INVALID_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_INVOCATION"
        or invalid.get("failure", {}).get("result_json_written") is not False
        or invalid.get("failure", {}).get("rollout_episode_slots") != 0
        or corrected.count(NEW_FRAGMENT) != 1
    ):
        raise ValueError("Winner-v63b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v63b_builder": Path(
            "tools/build_winner_v63b_training_snapshot_loader_correction.py"
        ),
        "v63b_runner": Path(
            "tools/run_winner_v63b_training_snapshot_loader_correction.py"
        ),
        "v63b_tests": Path(
            "tests/test_winner_v63b_training_snapshot_loader_correction.py"
        ),
        "v63_invalid_invocation": Path(
            "outputs/analysis/winner_v63_persistent_teacher_conflict_invalid_invocation.json"
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
    value["correction"] = {
        "identity": "WINNER_V63B_EXACT_TRAINING_SNAPSHOT_LOADER_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "frozen_runner_lf_sha256": lf_sha256(BASE_RUNNER),
        "old_fragment_sha256": hashlib.sha256(OLD_FRAGMENT.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW_FRAGMENT.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": (
            "use the immutable training-coordinate snapshot after the reviewed loader's "
            "own exact integrated-stage validation instead of its gate-adapted copy"
        ),
        "objective_rollout_gradient_adam_classification_or_authority_change": False,
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
                "# Winner-v63b exact training-snapshot loader correction",
                "",
                "- Identity: `WINNER_V63B_EXACT_TRAINING_SNAPSHOT_LOADER_CORRECTION`",
                "- Replacement count: `1`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "- Objective/rollout/gradient/Adam/classification/authority changes: `false`",
                "- Original rollout / counterfactual step / robot execution: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V63B_TRAINING_SNAPSHOT_LOADER_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
