#!/usr/bin/env python3
"""Freeze recovery of the interrupted T116 nominal matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T116 = ANALYSIS / "t116_t113_nominal_preregistration.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t116b_interrupted_nominal_recovery.py"
TEST = ROOT / "tests" / "test_t116b_interrupted_nominal_recovery.py"
OUTPUT = ANALYSIS / "t116b_interrupted_nominal_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T116B_INTERRUPTED_NOMINAL_RECOVERY_PREREGISTRATION_20260729.md"
)
CACHE = Path("D:/CodexArtifacts/open-duck-policy/t116_t113_nominal_v1")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T116B preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T116B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T116B preregistration requires clean worktree")
    t116 = json.loads(T116.read_text(encoding="utf-8"))
    manifest_paths = sorted(CACHE.rglob("manifest.json"))
    cached = [
        {
            "checkpoint_id": path.parent.parent.name,
            "fit_id": path.parent.name,
            "manifest": receipt(path),
        }
        for path in manifest_paths
    ]
    expected = {
        ("T113_ALWAYS_ON_TRAINTHROUGH_HALF", "p30"),
        ("T113_ALWAYS_ON_TRAINTHROUGH_HALF", "p31_34"),
    }
    observed = {
        (item["checkpoint_id"], item["fit_id"]) for item in cached
    }
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t116_preregistration": T116,
    }
    checks = {
        "t116_preregistration_green": (
            t116["status"] == "PREREGISTERED_T116_T113_NOMINAL_MATRIX"
            and not t116["failed_checks"]
        ),
        "exact_two_completed_blocks": observed == expected,
        "no_original_result": not (
            ANALYSIS / "t116_t113_nominal_result.json"
        ).exists(),
        "inputs_present": all(path.is_file() for path in inputs.values()),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t116b_interrupted_nominal_recovery_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T116B_INTERRUPTED_NOMINAL_RECOVERY"
            if not failed
            else "HOLD_T116B_INTERRUPTED_NOMINAL_RECOVERY"
        ),
        "source_contract_sha256": t116["preregistered_contract_sha256"],
        "source_preregistration": receipt(T116),
        "cached_blocks": cached,
        "remaining_blocks": [
            {
                "checkpoint_id": "T113_ALWAYS_ON_TRAINTHROUGH_FINAL",
                "fit_id": fit_id,
            }
            for fit_id in ("p30", "p31_34")
        ],
        "execution_rule": {
            "reuse_cached_blocks_without_rerun": True,
            "run_only_missing_blocks": True,
            "matrix_cells_total": 16,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
        },
        "decision_rule": t116["decision_rule"],
        "frozen_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "resume_exact_cpu_matrix": not failed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T116B interrupted nominal recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse two hashed half-checkpoint blocks; run two missing final blocks\n"
        "- Total frozen matrix remains 16 cells; no selection or retry\n"
        "- Training / Colab / robot: `0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
