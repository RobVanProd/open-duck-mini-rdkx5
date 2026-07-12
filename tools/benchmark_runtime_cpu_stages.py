#!/usr/bin/env python3
"""Benchmark policy inference and telemetry serialization without robot I/O."""

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort


def summary(values):
    ordered = sorted(values)
    return {
        "mean_s": statistics.fmean(ordered),
        "p95_s": ordered[int(0.95 * (len(ordered) - 1))],
        "max_s": ordered[-1],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--telemetry-jsonl", required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.iterations < 100:
        raise SystemExit("--iterations must be >= 100")

    record = json.loads(Path(args.telemetry_jsonl).read_text().splitlines()[0])
    session = ort.InferenceSession(args.policy, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    obs = np.asarray(record["observation"]["raw_vector"], dtype=np.float32)[None, :]

    for _ in range(20):
        session.run([output_name], {input_name: obs})
    inference = []
    for _ in range(args.iterations):
        t0 = time.perf_counter()
        session.run([output_name], {input_name: obs})
        inference.append(time.perf_counter() - t0)

    encoded = (json.dumps(record, separators=(",", ":")) + "\n").encode()
    serialization = []
    for _ in range(args.iterations):
        t0 = time.perf_counter()
        json.dumps(record, separators=(",", ":"))
        serialization.append(time.perf_counter() - t0)

    writes = []
    with tempfile.TemporaryFile() as output:
        for _ in range(args.iterations):
            t0 = time.perf_counter()
            output.write(encoded)
            output.flush()
            writes.append(time.perf_counter() - t0)

    result = {
        "status": "OFFLINE_CPU_COMPONENT_BENCHMARK",
        "iterations": args.iterations,
        "policy": args.policy,
        "telemetry_jsonl": args.telemetry_jsonl,
        "record_bytes": len(encoded),
        "inference": summary(inference),
        "json_serialization": summary(serialization),
        "buffered_write_flush": summary(writes),
        "not_measured": ["serial_read", "serial_write", "scheduler_delay"],
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
