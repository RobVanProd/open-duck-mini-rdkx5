#!/usr/bin/env python3
"""Import the external winner-v9 nominal result without trace or ONNX binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v9_nominal_behavior_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v9_nominal_behavior_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V9_NOMINAL_BEHAVIOR_RESULT_20260720.md"
EXPECTED_STATUSES = {
    "PASS_WINNER_V9_NOMINAL_BEHAVIOR",
    "HOLD_WINNER_V9_NOMINAL_BEHAVIOR",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def flatten(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for fit in payload["matrices"].values()
        for row in fit.values()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--artifact-name", required=True)
    args = parser.parse_args()
    raw_path = args.raw_result.resolve()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v9 nominal result has already been imported")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    prereg_sha = sha256(PREREG)
    if raw["preregistration_sha256"] != prereg_sha:
        raise ValueError("raw result does not bind the frozen nominal preregistration")
    if raw["status"] not in EXPECTED_STATUSES:
        raise ValueError(f"unexpected winner-v9 nominal status: {raw['status']}")
    if raw["input_hashes"] != prereg["input_hashes"]:
        raise ValueError("raw result input hashes do not match preregistration")
    if raw["policy_hashes"] != prereg["policy_hashes"]:
        raise ValueError("raw result policy hashes do not match preregistration")
    if raw["playground_commit"] != prereg["playground"]["required_commit"]:
        raise ValueError("raw result Playground commit does not match preregistration")
    if raw["playground_file_hashes"] != prereg["playground"]["required_file_hashes"]:
        raise ValueError("raw result Playground files do not match preregistration")

    blocks = flatten(raw)
    traces = [trace for block in blocks for trace in block["traces"]]
    if set(raw["matrices"]) != {"P30", "P31_34"} or any(
        set(rows) != {"half", "final"} for rows in raw["matrices"].values()
    ):
        raise ValueError("winner-v9 nominal result must contain the frozen four matrices")
    if len(blocks) != 4 or len(traces) != 16:
        raise ValueError("winner-v9 nominal result must contain exactly 16 cells")
    if not all(trace["rows"] == 600 and trace["ticks_contiguous"] for trace in traces):
        raise ValueError("winner-v9 nominal result contains an incomplete trace")
    expected_failed = [name for name, passed in raw["checks"].items() if not passed]
    if raw["failed_checks"] != expected_failed:
        raise ValueError("winner-v9 failed-check list is inconsistent")
    expected_status = (
        "PASS_WINNER_V9_NOMINAL_BEHAVIOR"
        if not expected_failed
        else "HOLD_WINNER_V9_NOMINAL_BEHAVIOR"
    )
    if raw["status"] != expected_status:
        raise ValueError("winner-v9 status is inconsistent with its frozen checks")

    payload = dict(raw)
    payload["repository_attribution"] = {
        "artifact_name": args.artifact_name,
        "contract_commit": args.contract_commit,
        "execution_commit": args.execution_commit,
        "onnx_binaries_committed": False,
        "preregistration_path": str(PREREG.relative_to(ROOT)).replace("\\", "/"),
        "preregistration_sha256": prereg_sha,
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "run_url": args.run_url,
        "trace_files_committed": False,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    worst_tracking = max(
        block["behavior"]["worst_nominal_tracking_p95_rad"] for block in blocks
    )
    worst_current = max(trace["worst_peak_current_a"] for trace in traces)
    worst_torque = max(trace["worst_peak_torque_nm"] for trace in traces)
    longest_overcurrent = max(
        trace["maximum_consecutive_ticks_above_2a"] for trace in traces
    )
    worst_rate_excess = max(
        trace["maximum_full_measured_vector_excess_rad_s"] for trace in traces
    )
    next_step = (
        "The result authorizes a separately frozen sequential robustness preregistration only."
        if not expected_failed
        else "The exact winner-v9 policy route is closed; it is not retried or reclassified."
    )
    OUTPUT_MD.write_text(
        "# Winner-v9 Nominal Behavior Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- worst tracking p95: `{worst_tracking}` rad\n"
        f"- worst peak current: `{worst_current}` A\n"
        f"- worst peak torque: `{worst_torque}` Nm\n"
        f"- longest consecutive duration above 2 A: `{longest_overcurrent}` ticks\n"
        f"- worst full measured-vector excess: `{worst_rate_excess}` rad/s\n"
        f"- imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n"
        f"- raw result SHA-256: `{sha256(raw_path)}`\n\n"
        f"{next_step}\n\n"
        "No trace or ONNX binary is committed by this import. No training, runtime, "
        "robot access, torque, motion, Gate 5, deployment, or robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
