#!/usr/bin/env python3
"""Import one generic Winner-v10 R2 condition result without raw traces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--contract-commit", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--artifact-name", required=True)
    args = parser.parse_args()
    prereg_path = args.preregistration.resolve()
    raw_path = args.raw_result.resolve()
    output_json = args.output_json.resolve()
    output_md = args.output_md.resolve()
    if output_json.exists() or output_md.exists():
        raise FileExistsError("Winner-v10 R2 condition result already imported")
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw["preregistration_sha256"] != lf_sha256(prereg_path):
        raise ValueError("raw result does not bind the R2 preregistration")
    if raw["status"] not in set(prereg["result_status"].values()):
        raise ValueError("unexpected Winner-v10 R2 condition status")
    if raw["input_hashes"] != prereg["input_hashes"]:
        raise ValueError("R2 condition input hashes do not match")
    if raw["policy_hashes"] != prereg["policy_hashes"]:
        raise ValueError("R2 condition policy hashes do not match")
    blocks = flatten(raw)
    traces = [trace for block in blocks for trace in block["traces"]]
    if len(blocks) != 4 or len(traces) != 16 or not all(
        trace["rows"] == 600 and trace["ticks_contiguous"] for trace in traces
    ):
        raise ValueError("R2 condition result is incomplete")
    failed = [name for name, passed in raw["checks"].items() if not passed]
    if failed != raw["failed_checks"]:
        raise ValueError("R2 condition failed-check list is inconsistent")
    expected_status = prereg["result_status"]["pass"] if not failed else prereg[
        "result_status"
    ]["hold"]
    expected_decision = prereg["result_decision"]["pass"] if not failed else prereg[
        "result_decision"
    ]["hold"]
    if raw["status"] != expected_status or raw["decision"] != expected_decision:
        raise ValueError("R2 condition classification is inconsistent")
    payload = dict(raw)
    payload["repository_attribution"] = {
        "artifact_name": args.artifact_name,
        "contract_commit": args.contract_commit,
        "execution_commit": args.execution_commit,
        "run_url": args.run_url,
        "preregistration_path": str(prereg_path.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_sha256": sha256(prereg_path),
        "execution_preregistration_lf_sha256": lf_sha256(prereg_path),
        "raw_result_filename": raw_path.name,
        "raw_result_sha256": sha256(raw_path),
        "trace_files_committed": False,
        "policy_binaries_committed": False,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
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
        prereg["pass_authorizes_only"]
        if not failed
        else f"R2 stops at condition {prereg['condition_index'] + 1}."
    )
    output_md.write_text(
        f"# Winner-v10 R2 Condition {prereg['condition_index'] + 1} Result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- condition: `{payload['condition']}`\n"
        f"- failed checks: `{payload['failed_checks']}`\n"
        f"- worst tracking p95: `{worst_tracking}` rad\n"
        f"- worst peak current: `{worst_current}` A\n"
        f"- worst peak torque: `{worst_torque}` Nm\n"
        f"- longest consecutive duration above 2 A: `{longest}` ticks\n"
        f"- worst full measured-vector excess: `{worst_rate}` rad/s\n"
        f"- imported JSON SHA-256: `{sha256(output_json)}`\n"
        f"- raw result SHA-256: `{sha256(raw_path)}`\n\n"
        f"{next_step}\n\n"
        "No trace or policy binary is committed. No training, runtime, robot access, "
        "torque, motion, Gate 5, deployment, or robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(output_json)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
