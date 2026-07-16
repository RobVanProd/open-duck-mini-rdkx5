#!/usr/bin/env python3
"""Measure the CPU/mock incremental time of round-robin servo health reads."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_rustypot_transport_recovery import Config, FakeRustypot, load_hwi


OUTPUT = ROOT / "outputs/analysis/contract_c4_mock_bus_time.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(fn, count: int) -> np.ndarray:
    values = np.empty(count, dtype=float)
    for index in range(count):
        start = time.perf_counter()
        fn()
        values[index] = time.perf_counter() - start
    return values


def main() -> int:
    fake = FakeRustypot()
    HWI = load_hwi(fake)
    hwi = HWI(Config(), "/dev/fake-servo")
    fake.opens[0][2]().fail_first = False
    for _ in range(100):
        hwi.read_servo_health_round_robin()
    count = 5000
    baseline = measure(lambda: None, count)
    extended = measure(hwi.read_servo_health_round_robin, count)
    baseline_p95 = float(np.percentile(baseline, 95))
    extended_p95 = float(np.percentile(extended, 95))
    delta_p95 = max(0.0, extended_p95 - baseline_p95)
    payload = {
        "schema_version": "contract_c4_mock_bus_time.v1",
        "status": "PASS_C4_MOCK_DELTA_BELOW_5MS" if delta_p95 < 0.005 else "FAIL_C4_MOCK_DELTA_5MS",
        "samples": count,
        "baseline_noop_p95_s": baseline_p95,
        "extended_three_register_mock_p95_s": extended_p95,
        "incremental_p95_s": delta_p95,
        "budget_s": 0.005,
        "within_budget": delta_p95 < 0.005,
        "scope": "CPU_MOCK_ONLY_NOT_SERIAL_OR_RDK_TIMING",
        "source_hashes": {"tool": sha256(Path(__file__))},
        "hardware_accessed": False,
        "robot_clearance": "NO",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["within_budget"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
