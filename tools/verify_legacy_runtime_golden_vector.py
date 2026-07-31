#!/usr/bin/env python3
"""Verify the C3 adjacent-tick legacy runtime contract."""

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
    parser.add_argument("vector", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    vector = json.loads(args.vector.read_text())
    prior, current = vector["prior"], vector["current"]
    obs = np.asarray(current["observation"]["full_raw_vector"], dtype=float)
    prior_sent = np.asarray(prior["action"]["motor_targets_sent_rad"], dtype=float)
    prior_phase = np.asarray(prior["control"]["imitation_phase"], dtype=float)
    checks = {
        "source_hash_present": len(vector["source_sha256"]) == 64,
        "adjacent_ticks": int(current["tick"]) == int(prior["tick"]) + 1,
        "telemetry_every_n_1": vector["telemetry_every_n_1_inferred_from_contiguous_ticks"] is True,
        "action_filter_off": vector["action_filter_off"] is True,
        "pre_head_overlay_target_present": len(prior["action"]["motor_targets_post_rate_limit_rad"]) == 14,
        "full_observation_101": obs.shape == (101,),
        "previous_motor_target_slot_exact": float(np.max(np.abs(obs[83:97] - prior_sent))) <= 1e-12,
        "obs_then_advance_phase_chain_exact": float(np.max(np.abs(obs[99:101] - prior_phase))) <= 1e-12,
    }
    status = "PASS_LEGACY_RUNTIME_GOLDEN_VECTOR" if all(checks.values()) else "HOLD_LEGACY_RUNTIME_GOLDEN_VECTOR"
    result = {
        "schema_version": "legacy_runtime_golden_vector_verification.v1",
        "status": status,
        "checks": checks,
        "failed_checks": sorted(key for key, value in checks.items() if not value),
        "vector_path": str(args.vector),
        "vector_sha256": sha256(args.vector),
        "ticks": [prior["tick"], current["tick"]],
        "metrics": {
            "obs83_97_previous_sent_max_error_rad": float(np.max(np.abs(obs[83:97] - prior_sent))),
            "obs_phase_previous_advanced_phase_max_error": float(np.max(np.abs(obs[99:101] - prior_phase))),
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "output_sha256": sha256(args.output)}, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
