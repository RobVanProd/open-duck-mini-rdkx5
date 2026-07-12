#!/usr/bin/env python3
"""Suspended fixed-target P30 versus P31/34 replay with mandatory rollback."""

import argparse
import json
import time
from pathlib import Path

import numpy as np


PHASES = (
    ("normal_p30", {}),
    ("gain_p31_p34", {"left_hip_pitch": 31.0, "left_knee": 34.0}),
)


def runtime_gains(hwi, overrides):
    names = list(hwi.joints)
    kps = [30.0] * len(names)
    kps[5:9] = [8.0] * 4
    for name, value in overrides.items():
        kps[names.index(name)] = value
    return kps


def restore(hwi):
    hwi.set_kps(runtime_gains(hwi, {}))
    hwi.set_kds([0.0] * len(hwi.joints))
    hwi.turn_off()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--i-understand-this-replays-suspended-motion", action="store_true")
    args = parser.parse_args()
    if not args.i_understand_this_replays_suspended_motion:
        raise SystemExit("refusing without suspended-motion acknowledgement")

    target_payload = json.loads(Path(args.targets).read_text())
    if target_payload.get("schema_version") != "open_duck_fixed_target_replay_v1":
        raise SystemExit("unexpected target schema")
    if target_payload.get("samples") != 747 or target_payload.get("period_s") != 0.02:
        raise SystemExit("fixed replay requires exactly 747 targets at 50 Hz")

    from mini_bdx_runtime.duck_config import DuckConfig
    from mini_bdx_runtime.rustypot_position_hwi import HWI

    hwi = HWI(DuckConfig())
    names = list(hwi.joints)
    if target_payload["joint_names"] != names:
        raise SystemExit("target joint order does not match HWI")
    targets = np.asarray(target_payload["targets_rad"], dtype=float)
    output_rows = []
    summaries = []
    try:
        hwi.turn_off()
        for phase_name, overrides in PHASES:
            start_read_errors = hwi.read_error_count
            start_write_errors = hwi.write_error_count
            start_resets = hwi.transport_reset_count
            hwi.kps = np.asarray(runtime_gains(hwi, overrides), dtype=float)
            hwi.turn_on()
            previous_target = np.asarray(list(hwi.init_pos.values()), dtype=float)
            errors = []
            next_tick = time.monotonic()
            for tick, target in enumerate(targets):
                actual = hwi.get_present_positions()
                if actual is None:
                    raise RuntimeError(f"position read failed at {phase_name} tick {tick}")
                error = np.asarray(actual) - previous_target
                errors.append(error)
                output_rows.append(
                    {
                        "phase": phase_name,
                        "tick": tick,
                        "timestamp_monotonic_s": time.monotonic(),
                        "kp_overrides": overrides,
                        "target_rad": target.tolist(),
                        "previous_target_rad": previous_target.tolist(),
                        "actual_rad": np.asarray(actual).tolist(),
                        "tracking_error_rad": error.tolist(),
                    }
                )
                hwi.set_position_all(dict(zip(names, target)))
                previous_target = target
                next_tick += 0.02
                time.sleep(max(0.0, next_tick - time.monotonic()))
            error_abs = np.abs(np.asarray(errors))
            summaries.append(
                {
                    "phase": phase_name,
                    "kp_overrides": overrides,
                    "samples": len(errors),
                    "tracking_p95_abs_rad": dict(
                        zip(names, np.percentile(error_abs, 95, axis=0).tolist())
                    ),
                    "tracking_max_abs_rad": dict(zip(names, np.max(error_abs, axis=0).tolist())),
                    "read_errors": hwi.read_error_count - start_read_errors,
                    "write_errors": hwi.write_error_count - start_write_errors,
                    "transport_resets": hwi.transport_reset_count - start_resets,
                }
            )
            hwi.set_position_all(hwi.init_pos)
            time.sleep(1.0)
            restore(hwi)
            time.sleep(1.0)
    finally:
        try:
            restore(hwi)
            cleanup = "DEFAULT_RUNTIME_GAINS_RESTORED_AND_TORQUE_DISABLED"
        except Exception as exc:
            cleanup = f"CLEANUP_FAILED: {exc!r}"
        print(cleanup, flush=True)

    jsonl = Path(args.output_jsonl)
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    jsonl.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in output_rows))
    result = {
        "schema_version": "open_duck_fixed_target_gain_ab_result_v1",
        "target_source_sha256": target_payload["source_sha256"],
        "target_artifact": args.targets,
        "phases": summaries,
        "cleanup": cleanup,
        "policy_loaded": False,
        "imu_used": False,
        "eeprom_changed": False,
    }
    Path(args.output_json).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summaries, indent=2), flush=True)


if __name__ == "__main__":
    main()
