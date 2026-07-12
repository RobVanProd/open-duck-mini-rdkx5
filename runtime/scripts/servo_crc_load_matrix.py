#!/usr/bin/env python3
"""Matched all-servo CRC test: torque off versus static home torque on."""

import argparse
import json
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-per-phase", type=float, default=15.0)
    parser.add_argument("--rate-hz", type=float, default=50.0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--i-understand-static-home-enables-torque", action="store_true")
    return parser.parse_args()


def collect(hwi, name, ids, duration, rate_hz):
    started = time.monotonic()
    period = 1.0 / rate_hz
    attempts = 0
    start_errors = hwi.read_error_count
    start_resets = hwi.transport_reset_count
    max_call_s = 0.0
    while time.monotonic() - started < duration:
        cycle = time.monotonic()
        for operation in ("read_present_position", "read_present_velocity"):
            call_started = time.monotonic()
            hwi._retry(operation, ids)
            max_call_s = max(max_call_s, time.monotonic() - call_started)
            attempts += 1
        time.sleep(max(0.0, period - (time.monotonic() - cycle)))
    return {
        "name": name,
        "ids": ids,
        "elapsed_s": time.monotonic() - started,
        "sync_read_attempts": attempts,
        "read_errors": hwi.read_error_count - start_errors,
        "transport_resets": hwi.transport_reset_count - start_resets,
        "max_call_s": max_call_s,
    }


def main():
    args = parse_args()
    if not args.i_understand_static_home_enables_torque:
        raise SystemExit("Refusing without static-home torque authorization flag")
    if args.duration_per_phase <= 0 or args.rate_hz <= 0:
        raise SystemExit("duration and rate must be positive")

    from mini_bdx_runtime.duck_config import DuckConfig
    from mini_bdx_runtime.rustypot_position_hwi import HWI

    hwi = HWI(DuckConfig())
    ids = list(hwi.joints.values())
    result = {
        "schema_version": "open_duck_servo_crc_load_matrix_v1",
        "duration_per_phase_s": args.duration_per_phase,
        "rate_hz": args.rate_hz,
        "policy_loaded": False,
        "nonzero_command_sent": False,
        "eeprom_changed": False,
        "servo_rail_voltage_v": None,
        "servo_rail_voltage_reason": "not exposed by installed Rustypot wrapper",
        "phases": [],
        "cleanup": "not attempted",
    }
    try:
        hwi.turn_off()
        print("PHASE=torque_disabled_all14", flush=True)
        row = collect(hwi, "torque_disabled_all14", ids, args.duration_per_phase, args.rate_hz)
        result["phases"].append(row)
        print("PHASE_RESULT=" + json.dumps(row, sort_keys=True), flush=True)

        print("PHASE=static_home_torque_enabled_all14", flush=True)
        hwi.turn_on()
        row = collect(
            hwi,
            "static_home_torque_enabled_all14",
            ids,
            args.duration_per_phase,
            args.rate_hz,
        )
        result["phases"].append(row)
        print("PHASE_RESULT=" + json.dumps(row, sort_keys=True), flush=True)
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
