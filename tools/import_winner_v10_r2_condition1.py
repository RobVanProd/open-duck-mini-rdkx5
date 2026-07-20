#!/usr/bin/env python3
"""Import Winner-v10 R2 condition-1 evidence without traces or policy binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v10_r2_condition1_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v10_r2_condition1_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V10_R2_CONDITION1_RESULT_20260720.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def flatten(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for fit in payload["matrices"].values() for row in fit.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--artifact-name", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v10 R2 condition-1 result already imported")
    raw_path = args.raw_result.resolve()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if raw["preregistration_sha256"] != lf_sha256(PREREG):
        raise ValueError("raw result does not bind condition-1 preregistration")
    if raw["status"] not in {
        "PASS_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO",
        "HOLD_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO",
    }:
        raise ValueError("unexpected Winner-v10 R2 condition-1 status")
    if raw["input_hashes"] != prereg["input_hashes"]:
        raise ValueError("condition-1 input hashes do not match")
    if raw["policy_hashes"] != prereg["policy_hashes"]:
        raise ValueError("condition-1 policy hashes do not match")
    blocks = flatten(raw)
    traces = [trace for block in blocks for trace in block["traces"]]
    if len(blocks) != 4 or len(traces) != 16 or not all(
        trace["rows"] == 600 and trace["ticks_contiguous"] for trace in traces
    ):
        raise ValueError("condition-1 result is incomplete")
    failed = [name for name, passed in raw["checks"].items() if not passed]
    if failed != raw["failed_checks"]:
        raise ValueError("condition-1 failed-check list is inconsistent")
    expected_status = (
        "PASS_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO"
        if not failed
        else "HOLD_WINNER_V10_R2_CONDITION1_FLOOR_FRICTION_LO"
    )
    if raw["status"] != expected_status:
        raise ValueError("condition-1 status is inconsistent")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "artifact_name": args.artifact_name,
        "contract_commit": args.contract_commit,
        "execution_commit": args.execution_commit,
        "run_url": args.run_url,
        "preregistration_sha256": sha256(PREREG),
        "execution_preregistration_lf_sha256": lf_sha256(PREREG),
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "trace_files_committed": False,
        "policy_binaries_committed": False,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    worst_tracking = max(
        block["behavior"]["worst_nominal_tracking_p95_rad"] for block in blocks
    )
    worst_current = max(trace["worst_peak_current_a"] for trace in traces)
    worst_torque = max(trace["worst_peak_torque_nm"] for trace in traces)
    longest = max(
        trace["maximum_consecutive_ticks_above_2a"] for trace in traces
    )
    worst_rate = max(
        trace["maximum_full_measured_vector_excess_rad_s"] for trace in traces
    )
    next_step = (
        "Condition 1 passed and authorizes a separately frozen condition-2 preregistration only."
        if not failed
        else "R2 stops at condition 1; no later robustness condition is authorized."
    )
    OUTPUT_MD.write_text(
        "# Winner-v10 R2 Condition 1 Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- condition: `{payload['condition']}`\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- worst tracking p95: `{worst_tracking}` rad\n"
        f"- worst peak current: `{worst_current}` A\n"
        f"- worst peak torque: `{worst_torque}` Nm\n"
        f"- longest consecutive duration above 2 A: `{longest}` ticks\n"
        f"- worst full measured-vector excess: `{worst_rate}` rad/s\n"
        f"- imported JSON SHA-256: `{sha256(OUTPUT_JSON)}`\n"
        f"- raw result SHA-256: `{sha256(raw_path)}`\n\n"
        f"{next_step}\n\n"
        "No trace or policy binary is committed. No training, runtime, robot access, "
        "torque, motion, Gate 5, deployment, or robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
