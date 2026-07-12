#!/usr/bin/env python3
"""Build a policy-free fixed-target replay from a validated telemetry JSONL."""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_jsonl")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.input_jsonl)
    raw = source.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows) != 747:
        raise SystemExit(f"expected 747 rows, got {len(rows)}")
    names = rows[0]["joints"]["names"]
    policy_sha = rows[0]["policy"]["onnx_sha256"]
    targets = []
    for row in rows:
        commands = row["control"]["commands"]
        if commands != [0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]:
            raise SystemExit(f"noncanonical command at tick {row['tick']}: {commands}")
        if row["joints"]["names"] != names or row["policy"]["onnx_sha256"] != policy_sha:
            raise SystemExit("joint order or policy identity changed within source")
        targets.append(row["action"]["motor_targets_sent_rad"])

    payload = {
        "schema_version": "open_duck_fixed_target_replay_v1",
        "source_path": str(source),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "policy_sha256": policy_sha,
        "command": [0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "joint_names": names,
        "period_s": 0.02,
        "samples": len(targets),
        "targets_rad": targets,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    print(hashlib.sha256(output.read_bytes()).hexdigest(), output)


if __name__ == "__main__":
    main()
