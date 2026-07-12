#!/usr/bin/env python3
"""Torque-disabled CRC isolation for IDs 12, 13, 14, and left-knee control 23.

This sends torque-disable writes, then position/velocity reads only. It never
sends a position target, enables torque, loads a policy, or changes EEPROM.
"""

import argparse, collections, json, time
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--duration", type=float, default=15.0)
    p.add_argument("--rate-hz", type=float, default=50.0)
    p.add_argument("--output", required=True)
    p.add_argument("--i-understand-this-disables-torque", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    if not args.i_understand_this_disables_torque:
        raise SystemExit("Refusing without --i-understand-this-disables-torque")
    if args.duration <= 0 or args.rate_hz <= 0:
        raise SystemExit("duration and rate must be positive")

    from mini_bdx_runtime.duck_config import DuckConfig
    from mini_bdx_runtime.rustypot_position_hwi import HWI

    cfg = DuckConfig()
    hwi = HWI(cfg)
    targets = [(12, "right_hip_pitch"), (13, "right_knee"),
               (14, "right_ankle"), (23, "left_knee")]
    counts = collections.Counter()
    errors = []
    started = time.monotonic()
    period = 1.0 / args.rate_hz
    cleanup = "not attempted"
    try:
        hwi.turn_off()
        print("TORQUE_DISABLED_ALL_JOINTS", flush=True)
        while time.monotonic() - started < args.duration:
            cycle = time.monotonic()
            for servo_id, joint in targets:
                for operation, function in (
                    ("position", hwi.io.read_present_position),
                    ("velocity", hwi.io.read_present_velocity),
                ):
                    key = f"{joint}:{servo_id}:{operation}"
                    counts[f"{key}:attempts"] += 1
                    try:
                        function([servo_id])
                        counts[f"{key}:success"] += 1
                    except Exception as exc:
                        counts[f"{key}:errors"] += 1
                        errors.append({"elapsed_s": time.monotonic() - started,
                                       "servo_id": servo_id, "joint": joint,
                                       "operation": operation, "error": repr(exc)})
            time.sleep(max(0.0, period - (time.monotonic() - cycle)))
    finally:
        try:
            hwi.turn_off()
            cleanup = "TORQUE_DISABLED_ALL_JOINTS"
            print(cleanup, flush=True)
        except Exception as exc:
            cleanup = f"TORQUE_DISABLE_FAILED: {exc!r}"
            print(cleanup, flush=True)

    payload = {"schema_version": "open_duck_servo_crc_isolation_v1",
               "duration_requested_s": args.duration, "rate_hz": args.rate_hz,
               "elapsed_s": time.monotonic() - started, "counts": dict(counts),
               "errors": errors, "cleanup": cleanup,
               "position_targets_sent": False, "torque_enabled": False,
               "policy_loaded": False, "eeprom_changed": False}
    path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"RESULT_JSON={path}", flush=True)


if __name__ == "__main__":
    main()
