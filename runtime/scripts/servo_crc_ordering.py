#!/usr/bin/env python3
"""Torque-disabled synchronous-read ordering test; no targets or EEPROM writes."""

import argparse
import json
import time
from pathlib import Path


ORDERS = {
    "canonical": [12, 13, 14],
    "id13_last": [12, 14, 13],
    "four_servo_control": [12, 13, 14, 23],
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-per-order", type=float, default=15.0)
    parser.add_argument("--rate-hz", type=float, default=50.0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--i-understand-this-disables-torque", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.i_understand_this_disables_torque:
        raise SystemExit("Refusing without --i-understand-this-disables-torque")
    if args.duration_per_order <= 0 or args.rate_hz <= 0:
        raise SystemExit("duration and rate must be positive")

    from mini_bdx_runtime.duck_config import DuckConfig
    from mini_bdx_runtime.rustypot_position_hwi import HWI

    hwi = HWI(DuckConfig())
    result = {
        "schema_version": "open_duck_servo_crc_ordering_v1",
        "duration_per_order_s": args.duration_per_order,
        "rate_hz": args.rate_hz,
        "position_targets_sent": False,
        "torque_enabled": False,
        "policy_loaded": False,
        "eeprom_changed": False,
        "orders": [],
        "cleanup": "not attempted",
    }
    period = 1.0 / args.rate_hz
    try:
        hwi.turn_off()
        print("TORQUE_DISABLED_ALL_JOINTS", flush=True)
        for name, ids in ORDERS.items():
            started = time.monotonic()
            attempts = 0
            start_errors = hwi.read_error_count
            start_resets = hwi.transport_reset_count
            max_call_s = 0.0
            while time.monotonic() - started < args.duration_per_order:
                cycle = time.monotonic()
                for operation in ("read_present_position", "read_present_velocity"):
                    call_started = time.monotonic()
                    hwi._retry(operation, ids)
                    max_call_s = max(max_call_s, time.monotonic() - call_started)
                    attempts += 1
                time.sleep(max(0.0, period - (time.monotonic() - cycle)))
            row = {
                "name": name,
                "ids": ids,
                "elapsed_s": time.monotonic() - started,
                "sync_read_attempts": attempts,
                "read_errors": hwi.read_error_count - start_errors,
                "transport_resets": hwi.transport_reset_count - start_resets,
                "max_call_s": max_call_s,
            }
            result["orders"].append(row)
            print("ORDER_RESULT=" + json.dumps(row, sort_keys=True), flush=True)
    finally:
        try:
            hwi.turn_off()
            result["cleanup"] = "TORQUE_DISABLED_ALL_JOINTS"
            print(result["cleanup"], flush=True)
        except Exception as exc:
            result["cleanup"] = f"TORQUE_DISABLE_FAILED: {exc!r}"
            print(result["cleanup"], flush=True)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"RESULT_JSON={output}", flush=True)


if __name__ == "__main__":
    main()
