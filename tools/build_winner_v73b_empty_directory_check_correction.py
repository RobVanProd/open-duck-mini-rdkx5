#!/usr/bin/env python3
"""Freeze the sole Winner-v73b empty-directory Boolean correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v73b_empty_directory_check_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V73B_EMPTY_DIRECTORY_CHECK_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v73_update638_contract_attribution_preregistration.json"
INVALID = ANALYSIS / "winner_v73_update638_contract_attribution_invalid_invocation.json"
INVALID_WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v73-update638-contract-attribution"
)
OLD = '''        if any((args.work_root / name).iterdir() for name in ("snapshots", "graphs")):
            raise ValueError("Winner-v73 diagnostic wrote a training artifact")'''
NEW = '''        if any(any((args.work_root / name).iterdir()) for name in ("snapshots", "graphs")):
            raise ValueError("Winner-v73 diagnostic wrote a training artifact")'''

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v73_update638_contract_attribution as v73  # noqa: E402


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
    source, _ = v73.transformed_source()
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v73b correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v73b_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v73b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    empty_counts = {
        name: len(list((INVALID_WORK_ROOT / name).iterdir()))
        for name in ("snapshots", "graphs")
    }
    if (
        sha256(BASE)
        != "7e6bc3de549d323ac5c59b00836faa8aee02282f40256fc475473018175b4ab4"
        or base.get("status")
        != "PREREGISTERED_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION"
        or invalid.get("status")
        != "INVALID_WINNER_V73_EMPTY_DIRECTORY_ITERATOR_CHECK"
        or invalid.get("failure", {}).get("result_written") is not False
        or invalid.get("authority", {}).get("committed_optimizer_updates") != 0
        or empty_counts != {"snapshots": 0, "graphs": 0}
        or corrected.count(NEW) != 1
    ):
        raise ValueError("Winner-v73b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v73b_builder": Path("tools/build_winner_v73b_empty_directory_check_correction.py"),
        "v73b_runner": Path("tools/run_winner_v73b_empty_directory_check_correction.py"),
        "v73b_tests": Path("tests/test_winner_v73b_empty_directory_check_correction.py"),
        "v73_invalid_invocation": Path(
            "outputs/analysis/winner_v73_update638_contract_attribution_invalid_invocation.json"
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
    value["v73b"] = {
        "identity": "WINNER_V73B_EMPTY_DIRECTORY_BOOLEAN_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "old_fragment_sha256": hashlib.sha256(OLD.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": (
            "test directory contents instead of the truthiness of iterator objects"
        ),
        "rollout_objective_gradient_threshold_or_authority_change": False,
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
                "# Winner-v73b empty-directory check correction",
                "",
                "- Replacement count: `1`",
                "- Prior result / updates / snapshots / graphs / robot: `0 / 0 / 0 / 0 / 0`",
                "- Rollout/objective/gradient/threshold/authority changes: `false`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V73B_EMPTY_DIRECTORY_BOOLEAN_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
