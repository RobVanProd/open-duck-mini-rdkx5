#!/usr/bin/env python3
"""Freeze the sole Winner-v80b teacher-mask indexing correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v80b_mask_indexing_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V80B_MASK_INDEXING_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v80_pitch_action_head_step_contract.json"
INVALID = ANALYSIS / "winner_v80_pitch_action_head_step_invalid_invocation.json"
RESULT = ANALYSIS / "winner_v80_pitch_action_head_step_result.json"
BASE_RUNNER = ROOT / "tools/run_winner_v80_pitch_action_head_step.py"
INVALID_WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v80-pitch-action-head-step"
)
OLD = "        mask[environment, :, pitch] = valid[environment, :, None]"
NEW = "        mask[environment][:, pitch] = valid[environment, :, None]"


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
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v80b correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v80b_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v80b contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    if (
        sha256(BASE)
        != "3e6962428cf17c1717875a11973a922efd8ec6fdae64949c563d68d966193f10"
        or base.get("status") != "PREREGISTERED_WINNER_V80_PITCH_ACTION_HEAD_STEP"
        or invalid.get("status")
        != "INVALID_WINNER_V80_NUMPY_ADVANCED_INDEX_MASK_ASSIGNMENT"
        or invalid.get("authority", {}).get("optimizer_updates") != 0
        or invalid.get("authority", {}).get("artifacts_written") != 0
        or invalid.get("failure", {}).get("result_written") is not False
        or INVALID_WORK_ROOT.exists()
        or RESULT.exists()
        or corrected.count(NEW) != 1
    ):
        raise ValueError("Winner-v80b correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v80b_builder": Path("tools/build_winner_v80b_mask_indexing_correction.py"),
        "v80b_runner": Path("tools/run_winner_v80b_mask_indexing_correction.py"),
        "v80b_tests": Path("tests/test_winner_v80b_mask_indexing_correction.py"),
        "v80_invalid_invocation": Path(
            "outputs/analysis/winner_v80_pitch_action_head_step_invalid_invocation.json"
        ),
    }
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in additions.items()
        }
    )
    value = dict(base)
    value["v80b"] = {
        "identity": "WINNER_V80B_MASK_INDEXING_CORRECTION",
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
            "select the environment view before the six pitch columns so the "
            "250x1 validity vector broadcasts over 250x6 exactly as in Winner-v43"
        ),
        "population_objective_gradient_optimizer_threshold_or_authority_change": False,
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
                "# Winner-v80b mask-indexing correction",
                "",
                "- Replacement count: `1`",
                "- Prior rollout slots / scheduled ticks: `80 / 20,000`",
                "- Prior optimizer / artifacts / result / robot: `0 / 0 / 0 / 0`",
                "- Population/objective/gradient/optimizer/threshold/authority changes: `false`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V80B_MASK_INDEXING_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
