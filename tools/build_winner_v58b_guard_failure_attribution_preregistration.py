#!/usr/bin/env python3
"""Freeze the corrected zero-update Winner-v58 guard attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v58b_guard_failure_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V58B_GUARD_FAILURE_ATTRIBUTION_PREREGISTRATION_20260722.md"
V58A_PREREG = ANALYSIS / "winner_v58a_guard_failure_attribution_preregistration.json"
EXPECTED_TEACHER_SNAPSHOT_SHA256 = (
    "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
)

CUSTOM_SOURCES = {
    "v58b_builder": Path(
        "tools/build_winner_v58b_guard_failure_attribution_preregistration.py"
    ),
    "v58b_runner": Path("tools/run_winner_v58b_guard_failure_attribution.py"),
    "v58b_tests": Path("tests/test_winner_v58b_guard_failure_attribution.py"),
    "v58a_preregistration": Path(
        "outputs/analysis/winner_v58a_guard_failure_attribution_preregistration.json"
    ),
    "v58a_transform_builder": Path(
        "tools/build_winner_v58a_guard_failure_attribution_preregistration.py"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    import build_winner_v58a_guard_failure_attribution_preregistration as v58a

    source, _ = v58a.transformed_source()
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v58b transform count changed: expected {count}, "
                f"found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )

    replace(
        'source_result["teacher"]["snapshot_sha256"]',
        repr(EXPECTED_TEACHER_SNAPSHOT_SHA256),
    )
    replace("winner_v58a", "winner_v58b", source.count("winner_v58a"))
    replace("Winner-v58a", "Winner-v58b", source.count("Winner-v58a"))
    replace("WINNER_V58A", "WINNER_V58B", source.count("WINNER_V58A"))
    compile(source, "winner_v58b_guard_failure_attribution.py", "exec")
    return source, receipts


def main() -> int:
    import build_winner_v58a_guard_failure_attribution_preregistration as v58a

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v58b evidence: {path}")
    old = json.loads(V58A_PREREG.read_text(encoding="utf-8"))
    if (
        old.get("status")
        != "PREREGISTERED_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION"
        or old.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_WINNER_V58_GUARD_ATTRIBUTION_ONLY"
        or old.get("authority", {}).get("retry_authorized") is not False
        or old.get("teacher_checkpoint", {}).get("snapshot", {}).get("sha256")
        != EXPECTED_TEACHER_SNAPSHOT_SHA256
    ):
        raise ValueError("Winner-v58b predecessor contract changed")
    snapshots = v58a._snapshot_manifest()
    if snapshots != old["interruption"]["snapshot_chain"]:
        raise ValueError("Winner-v58b interrupted snapshot chain changed")
    transformed, receipts = transformed_source()
    sources = dict(old["sources"])
    for name, path in CUSTOM_SOURCES.items():
        sources[name] = {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
    payload = json.loads(json.dumps(old))
    payload.update(
        {
            "schema_version": "winner_v58b.guard_failure_attribution_preregistration.v1",
            "status": "PREREGISTERED_WINNER_V58B_GUARD_FAILURE_ATTRIBUTION",
            "decision": "AUTHORIZE_ONE_ZERO_UPDATE_WINNER_V58_GUARD_ATTRIBUTION_ONLY",
            "predecessor_failure": {
                "contract": V58A_PREREG.relative_to(ROOT).as_posix(),
                "contract_lf_sha256": lf_sha256(V58A_PREREG),
                "failure_stage": "source_snapshot_metadata_validation_before rollout construction",
                "failure": "V58a referenced a nonexistent source_result['teacher'] key",
                "rollouts": 0,
                "optimizer_updates": 0,
                "output_created": False,
                "work_root_created": False,
                "correction_only": (
                    "compare the source metadata teacher hash to the exact already-bound "
                    "V58 teacher snapshot SHA-256"
                ),
            },
            "sources": sources,
            "source_manifest_sha256": canonical_sha256(sources),
            "transformation": {
                "base_v58a_transformed_source_sha256": old["transformation"][
                    "transformed_source_sha256"
                ],
                "transformed_source_sha256": hashlib.sha256(
                    transformed.encode()
                ).hexdigest(),
                "replacements": receipts,
                "replacement_groups": len(receipts),
            },
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v58b corrected guard-failure attribution preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- V58a execution: `0` rollouts / `0` optimizer updates",
                "- Correction: bind the already-frozen teacher snapshot SHA directly",
                "- Interrupted source / diagnostic rollout: `476 / 476`",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
                "- Retry authorization: `false`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
