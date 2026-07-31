#!/usr/bin/env python3
"""Freeze the sole Winner-v71b full-loss local binding correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v71b_full_loss_binding_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V71B_FULL_LOSS_BINDING_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_preregistration.json"
INVALID = ANALYSIS / "winner_v71_fresh_moment_safeguarded_invalid_invocation.json"
OLD = '''        after = active_trials[accepted_index]
        accepted_fraction = float(accepted_row["fraction"])'''
NEW = '''        after = active_trials[accepted_index]
        full_loss = float(active_rows[0]["loss"])
        accepted_fraction = float(accepted_row["fraction"])'''

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v71_fresh_moment_safeguarded_continuation as v71  # noqa: E402


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
    source, _ = v71.transformed_source()
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v71b correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v71b_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v71b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "8b3a9dc020ce7cadde310c67d2a26ab9f5e03ac89c14a6053544dbc8048b138c"
        or base.get("status")
        != "PREREGISTERED_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION"
        or invalid.get("status")
        != "INVALID_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_INVOCATION"
        or invalid.get("failure", {}).get("snapshot_writes") != 0
        or invalid.get("failure", {}).get("optimizer_updates_persisted") != 0
        or corrected.count(NEW) != 1
    ):
        raise ValueError("Winner-v71b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v71b_builder": Path("tools/build_winner_v71b_full_loss_binding_correction.py"),
        "v71b_runner": Path("tools/run_winner_v71b_full_loss_binding_correction.py"),
        "v71b_tests": Path("tests/test_winner_v71b_full_loss_binding_correction.py"),
        "v71_invalid_invocation": Path(
            "outputs/analysis/winner_v71_fresh_moment_safeguarded_invalid_invocation.json"
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
    value["v71b"] = {
        "identity": "WINNER_V71B_FULL_LOSS_LOCAL_BINDING_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "old_fragment_sha256": hashlib.sha256(OLD.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": "bind metrics full_loss to the already computed active fraction-1 loss",
        "objective_rollout_gradient_safeguard_moment_reset_adam_or_authority_change": False,
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
                "# Winner-v71b full-loss binding correction",
                "",
                "- Replacement count: `1`",
                "- Prior persisted updates / snapshots / result / robot: `0 / 0 / 0 / 0`",
                "- Objective/rollout/gradient/safeguard/reset/Adam/authority changes: `false`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V71B_FULL_LOSS_BINDING_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
