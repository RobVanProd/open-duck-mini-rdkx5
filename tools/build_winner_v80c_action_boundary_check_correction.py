#!/usr/bin/env python3
"""Freeze the sole Winner-v80c action-boundary checker correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v80c_action_boundary_check_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V80C_ACTION_BOUNDARY_CHECK_CORRECTION_20260722.md"
BASE = ANALYSIS / "winner_v80b_mask_indexing_correction.json"
INVALID = ANALYSIS / "winner_v80b_pitch_action_head_step_invalid_invocation.json"
RESULT = ANALYSIS / "winner_v80_pitch_action_head_step_result.json"
INVALID_WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v80-pitch-action-head-step"
)
RERUN_WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v80c-pitch-action-head-step"
)
OLD = '        "action_boundary_exact": bool(boundary["all_exact"]),'
NEW = '''        "action_boundary_exact": bool(
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
        ),'''

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v80b_mask_indexing_correction as v80b  # noqa: E402


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
    source, _ = v80b.corrected_source()
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError("Winner-v80c correction fragment changed")
    corrected = source.replace(OLD, NEW)
    compile(corrected, "winner_v80c_corrected.py", "exec")
    return corrected, hashlib.sha256(corrected.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v80c contract: {path}")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    corrected, corrected_hash = corrected_source()
    expected_artifacts = {
        (
            "graphs/winner_v80_pitch_action_head_update_656.onnx",
            54896,
            "38e9dd4886593c4e3a996ec74493748138295e9740098a9594020ed152249210",
        ),
        (
            "snapshots/snapshot_pitch_action_head_update_656.npz",
            196195,
            "6d0cbb20c0985ba2926471a6d5902d6f969ce2e82bb04471a3ddc308f183ce71",
        ),
    }
    actual_artifacts = {
        (
            path.relative_to(INVALID_WORK_ROOT).as_posix(),
            path.stat().st_size,
            sha256(path),
        )
        for path in INVALID_WORK_ROOT.rglob("*")
        if path.is_file()
    }
    if (
        sha256(BASE)
        != "232c89b23584757dae18752f9b489e4da21d4c646be6b118c89569ff8f250525"
        or base.get("status") != "PREREGISTERED_WINNER_V80_PITCH_ACTION_HEAD_STEP"
        or invalid.get("status") != "INVALID_WINNER_V80B_ACTION_BOUNDARY_SUMMARY_KEY"
        or invalid.get("authority", {}).get("result_written") is not False
        or actual_artifacts != expected_artifacts
        or RESULT.exists()
        or RERUN_WORK_ROOT.exists()
        or corrected.count("realized_equals_numpy_bit_exact") < 1
    ):
        raise ValueError("Winner-v80c correction authority changed")
    sources = dict(base["sources"])
    additions = {
        "v80c_builder": Path(
            "tools/build_winner_v80c_action_boundary_check_correction.py"
        ),
        "v80c_runner": Path(
            "tools/run_winner_v80c_action_boundary_check_correction.py"
        ),
        "v80c_tests": Path(
            "tests/test_winner_v80c_action_boundary_check_correction.py"
        ),
        "v80b_invalid_invocation": Path(
            "outputs/analysis/winner_v80b_pitch_action_head_step_invalid_invocation.json"
        ),
    }
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in additions.items()
        }
    )
    value = dict(base)
    value["v80c"] = {
        "identity": "WINNER_V80C_ACTION_BOUNDARY_CHECK_CORRECTION",
        "invalid_invocation": {
            "path": INVALID.relative_to(ROOT).as_posix(),
            "bytes": INVALID.stat().st_size,
            "sha256": sha256(INVALID),
        },
        "invalid_artifacts": [
            {"path": path, "bytes": size, "sha256": digest}
            for path, size, digest in sorted(actual_artifacts)
        ],
        "old_fragment_sha256": hashlib.sha256(OLD.encode()).hexdigest(),
        "new_fragment_sha256": hashlib.sha256(NEW.encode()).hexdigest(),
        "corrected_source_sha256": corrected_hash,
        "replacement_count": 1,
        "semantic_change": (
            "require both existing action-boundary predicates instead of a nonexistent "
            "aggregate key"
        ),
        "population_objective_gradient_optimizer_threshold_or_authority_change": False,
        "rerun_work_root": str(RERUN_WORK_ROOT),
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
                "# Winner-v80c action-boundary checker correction",
                "",
                "- Replacement count: `1`",
                "- Invalid partial snapshot / graph: `1 / 1`, quarantined and hashed",
                "- Valid result / support / robot: `0 / 0 / 0`",
                "- Population/objective/gradient/optimizer/threshold/authority changes: `false`",
                f"- Corrected source SHA-256: `{corrected_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V80C_ACTION_BOUNDARY_CHECK_CORRECTION")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
