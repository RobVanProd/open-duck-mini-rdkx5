#!/usr/bin/env python3
"""Correct the Winner-v111 CPU smoke's stdout-only metric-presence check."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from tensorboardX.proto.event_pb2 import Event


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ORIGINAL = ANALYSIS / "winner_v111_peak_torque_cpu_result.json"
RESULT = ANALYSIS / "winner_v111_peak_torque_cpu_correction.json"
MARKDOWN = ANALYSIS / "WINNER_V111_PEAK_TORQUE_CPU_CORRECTION_20260724.md"
ORIGINAL_SHA256 = (
    "e38f812b7691f499520a9ae2f1b95e9b4729d441061367c3b476c8c182856a03"
)
EVENT_SHA256 = (
    "c8b26051aaf92f9d025678f55c5cc89b8c689125944f9f262f3249e1558493d4"
)
METRIC_TAG = "eval/episode_cost/peak_torque_exceedance"
EXPECTED_STEPS = [0, 1024]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_scalar_events(path: Path, tag: str) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    with path.open("rb") as stream:
        while True:
            length_bytes = stream.read(8)
            if not length_bytes:
                break
            if len(length_bytes) != 8:
                raise ValueError("truncated TensorBoard event length")
            length = struct.unpack("<Q", length_bytes)[0]
            if len(stream.read(4)) != 4:
                raise ValueError("truncated TensorBoard length checksum")
            payload = stream.read(length)
            if len(payload) != length:
                raise ValueError("truncated TensorBoard event payload")
            if len(stream.read(4)) != 4:
                raise ValueError("truncated TensorBoard payload checksum")
            event = Event()
            event.ParseFromString(payload)
            if not event.HasField("summary"):
                continue
            for value in event.summary.value:
                if value.tag == tag:
                    rows.append(
                        {
                            "step": int(event.step),
                            "value": float(value.simple_value),
                        }
                    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite Winner-v111 correction")
    if sha256(ORIGINAL) != ORIGINAL_SHA256:
        raise ValueError("original Winner-v111 result changed")
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    if original["status"] != "HOLD_WINNER_V111_PEAK_TORQUE_CPU_SMOKE":
        raise ValueError("original result is not the expected HOLD")
    if original["failed_checks"] != ["objective_metric_present"]:
        raise ValueError("correction is restricted to the sole reporting check")
    if Path(original["run_root"]).resolve() != run_root:
        raise ValueError("run root does not match the original result")
    log = run_root / "training.log"
    event_files = sorted((run_root / "smoke").glob("events.out.tfevents*"))
    if len(event_files) != 1:
        raise ValueError(f"expected one event file, found {len(event_files)}")
    event_file = event_files[0]
    if sha256(log) != original["training"]["log_sha256"]:
        raise ValueError("training log changed")
    if sha256(event_file) != EVENT_SHA256:
        raise ValueError("TensorBoard event file changed")
    rows = read_scalar_events(event_file, METRIC_TAG)
    steps = [row["step"] for row in rows]
    finite = bool(rows) and all(math.isfinite(row["value"]) for row in rows)
    checks = {
        "original_result_hash_exact": True,
        "original_only_failed_stdout_metric_presence": True,
        "training_log_hash_exact": True,
        "tensorboard_event_hash_exact": True,
        "objective_metric_tag_exact": steps == EXPECTED_STEPS,
        "objective_metric_values_finite": finite,
        "no_training_retry": True,
        "no_policy_or_checkpoint_change": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v111.peak_torque_cpu_correction.v1",
        "status": (
            "PASS_WINNER_V111_PEAK_TORQUE_CPU_SMOKE_REPORTING_CORRECTED"
            if not failed
            else "HOLD_WINNER_V111_PEAK_TORQUE_CPU_SMOKE_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "correction_scope": {
            "classification": "reporting_only",
            "original_check": (
                "searched captured stdout for peak_torque_exceedance"
            ),
            "correct_source": "TensorBoard scalar event stream",
            "training_rerun": False,
            "policy_change": False,
            "checkpoint_change": False,
            "gate_change": False,
        },
        "objective_metric_evidence": {
            "tag": METRIC_TAG,
            "events": rows,
        },
        "input_hashes": {
            "original_result": sha256(ORIGINAL),
            "training_log": sha256(log),
            "tensorboard_event": sha256(event_file),
        },
        "run_root": str(run_root),
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v111 peak-torque CPU reporting correction\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        f"TensorBoard metric: `{METRIC_TAG}`\n\n"
        f"Recorded events: `{rows}`\n\n"
        "This correction is reporting-only. The original run, checkpoints, "
        "ONNX files, and training log are unchanged. A pass authorizes only "
        "a separate hosted-run preregistration; it does not authorize hosted "
        "training, behavior selection, Gate 5, robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
