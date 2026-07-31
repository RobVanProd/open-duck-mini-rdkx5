#!/usr/bin/env python3
"""Extract one adjacent legacy runtime tick pair with the frozen C3 fields."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text().splitlines()]
    contiguous = all(int(b["tick"]) == int(a["tick"]) + 1 for a, b in zip(rows, rows[1:]))
    selected = None
    for prior, current in zip(rows, rows[1:]):
        obs = current.get("observation", {}).get("full_raw_vector")
        post = prior.get("action", {}).get("motor_targets_post_rate_limit_rad")
        sent = prior.get("action", {}).get("motor_targets_sent_rad")
        cutoff = prior.get("control", {}).get("cutoff_frequency_hz")
        if obs is None or len(obs) != 101 or post is None or len(post) != 14 or sent is None or len(sent) != 14:
            continue
        if cutoff is not None:
            continue
        slot_error = float(np.max(np.abs(np.asarray(obs[83:97]) - np.asarray(sent))))
        if slot_error <= 1e-12:
            selected = (prior, current, slot_error)
            break
    if selected is None:
        raise SystemExit("no qualifying adjacent pair")
    prior, current, slot_error = selected
    payload = {
        "schema_version": "legacy_runtime_golden_vector.v1",
        "source_path": str(args.input),
        "source_sha256": sha256(args.input),
        "source_rows": len(rows),
        "telemetry_every_n_1_inferred_from_contiguous_ticks": contiguous,
        "action_filter_off": prior["control"].get("cutoff_frequency_hz") is None,
        "pre_head_overlay_target_field": "motor_targets_post_rate_limit_rad",
        "prior": prior,
        "current": current,
        "derived": {
            "obs83_97_equals_prior_sent_max_error_rad": slot_error,
            "current_obs_phase_equals_prior_recorded_advanced_phase_max_error": float(np.max(np.abs(np.asarray(current["observation"]["full_raw_vector"][99:101]) - np.asarray(prior["control"]["imitation_phase"])))),
            "prior_post_rate_limit_to_sent_max_difference_rad": float(np.max(np.abs(np.asarray(prior["action"]["motor_targets_post_rate_limit_rad"]) - np.asarray(prior["action"]["motor_targets_sent_rad"])))),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS_GOLDEN_VECTOR_EXTRACT", "ticks": [prior["tick"], current["tick"]], "output_sha256": sha256(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
