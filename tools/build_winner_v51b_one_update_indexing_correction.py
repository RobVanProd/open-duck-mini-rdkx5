#!/usr/bin/env python3
"""Freeze the one-line Winner-v51b proof indexing correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v51b_one_update_indexing_correction_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION_CONTRACT_20260722.md"
V51_CONTRACT = ANALYSIS / "winner_v51_full_action_teacher_one_update_cpu_contract.json"
INVALID = ANALYSIS / "winner_v51_full_action_teacher_one_update_invalid_invocation.json"
V51_RUNNER = ROOT / "tools/run_winner_v51_full_action_teacher_one_update_cpu_proof.py"
OLD_FRAGMENT = '''    full_gradient_max = recomputed["objective_evidence"]
    ["full_teacher_gradient_max_abs"]'''
NEW_FRAGMENT = '''    full_gradient_max = recomputed["objective_evidence"][
        "full_teacher_gradient_max_abs"
    ]'''


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
    source = V51_RUNNER.read_text(encoding="utf-8")
    if source.count(OLD_FRAGMENT) != 1 or NEW_FRAGMENT in source:
        raise ValueError("Winner-v51b correction fragment changed")
    corrected = source.replace(OLD_FRAGMENT, NEW_FRAGMENT)
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v51b contract: {path}")

    base = json.loads(V51_CONTRACT.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        invalid.get("status")
        != "INVALID_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_INVOCATION"
        or invalid.get("failure", {}).get("result_json_written") is not False
        or base.get("status")
        != "PREREGISTERED_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
        or corrected.count(NEW_FRAGMENT) != 1
    ):
        raise ValueError("Winner-v51b correction authority changed")

    sources = dict(base["sources"])
    additions = {
        "winner_v51b_builder": Path("tools/build_winner_v51b_one_update_indexing_correction.py"),
        "winner_v51b_runner": Path("tools/run_winner_v51b_one_update_indexing_correction.py"),
        "winner_v51b_tests": Path("tests/test_winner_v51b_one_update_indexing_correction.py"),
        "winner_v51_invalid_invocation": Path("outputs/analysis/winner_v51_full_action_teacher_one_update_invalid_invocation.json"),
    }
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in additions.items()
        }
    )
    value = dict(base)
    value["correction"] = {
        "identity": "WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "frozen_runner_lf_sha256": lf_sha256(V51_RUNNER),
        "old_fragment_sha256": hashlib.sha256(OLD_FRAGMENT.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW_FRAGMENT.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": (
            "index objective_evidence['full_teacher_gradient_max_abs'] before "
            "policy/nonpolicy gradient checks"
        ),
        "optimizer_objective_artifact_or_gate_change": False,
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
                "# Winner-v51b one-update indexing correction contract",
                "",
                "- Identity: `WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION`",
                "- Replacement count: `1`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "- Optimizer/objective/artifact/gate changes: `false`",
                "- Formal support / continuation / robot: `0 / 0 / 0`",
                "",
                "The frozen V51 runner is not edited. V51b executes an exact in-memory",
                "source correction that indexes the already recorded nested teacher-gradient",
                "dictionary. Every other byte of the executed proof source is unchanged.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V51B_ONE_UPDATE_INDEXING_CORRECTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
