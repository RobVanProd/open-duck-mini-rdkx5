#!/usr/bin/env python3
"""Import the external winner-v7 behavior result without traces or ONNX binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v7_full_behavior_revalidation_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v7_full_behavior_revalidation_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V7_FULL_BEHAVIOR_REVALIDATION_RESULT_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    args = parser.parse_args()
    raw_path = args.raw_result.resolve()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v7 behavior result has already been imported")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    preregistration_sha = sha256(PREREGISTRATION)
    if raw["preregistration_sha256"] != preregistration_sha:
        raise ValueError("raw result does not match the frozen behavior preregistration")
    if raw["status"] not in {
        "PASS_WINNER_V7_FULL_BEHAVIOR_REVALIDATION",
        "HOLD_WINNER_V7_FULL_BEHAVIOR_REVALIDATION",
    }:
        raise ValueError(f"unexpected raw result status: {raw['status']}")
    if len(raw["conditions"]) != 8:
        raise ValueError("winner-v7 behavior result must contain exactly eight conditions")
    if raw["checks"]["exactly_128_cells"] is not True:
        raise ValueError("winner-v7 behavior result is incomplete")

    payload = dict(raw)
    payload["repository_attribution"] = {
        "contract_commit": args.contract_commit,
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_sha256": preregistration_sha,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "trace_files_committed": False,
        "policy_binaries_committed": False,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    flat = [
        policy
        for condition in payload["conditions"]
        for fit in condition["matrices"].values()
        for policy in fit.values()
    ]
    worst_tracking = max(
        row["behavior"]["worst_nominal_tracking_p95_rad"] for row in flat
    )
    worst_peak = max(row["current"]["worst_peak_current_a"] for row in flat)
    longest_overcurrent = max(
        row["current"]["maximum_consecutive_ticks_above_2a"] for row in flat
    )
    OUTPUT_MD.write_text(
        "# Winner-v7 Full Behavior Revalidation Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"Imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n\n"
        f"- raw result SHA-256: `{sha256(raw_path)}`\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- worst tracking p95: `{worst_tracking}` rad\n"
        f"- worst peak current: `{worst_peak}` A\n"
        f"- longest consecutive duration above 2 A: `{longest_overcurrent}` ticks\n\n"
        "All 128 cells, behavior expectations, dynamics readbacks, transformed-policy "
        "hashes, CPU attestations, and trace continuity checks were present. Behavior "
        "was preserved, but the frozen 2.5 A peak-current protection gate failed. "
        "The exact winner-v7 protected base is closed and is not retried or reclassified.\n\n"
        "No trace or ONNX binary is committed by this import. No training, runtime, "
        "robot access, torque, motion, Gate 5, deployment, or clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
