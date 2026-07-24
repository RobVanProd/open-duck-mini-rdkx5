#!/usr/bin/env python3
"""Attribute V122 CPU metric scale before authorizing hosted training."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from validate_winner_v112_recovered_training import (  # noqa: E402
    event_scalars,
)


ANALYSIS = ROOT / "outputs/analysis"
V119_RESULT = ANALYSIS / "winner_v119_transition_cpu_result.json"
V122_RESULT = ANALYSIS / "winner_v122_episode_peak_cpu_result.json"
OUTPUT = ANALYSIS / "winner_v122_cpu_reward_mass_attribution.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V122_CPU_REWARD_MASS_ATTRIBUTION_20260724.md"
)
EXPECTED = {
    "v119_result": (
        "5761e21e652a66ae46cd8aff92dd84ee3eaeb3a088d2d1345b0218b5e62b94fb"
    ),
    "v122_result": (
        "56006d763f9a92ef2a40ea6e0501ef7181d5411569f411b43b85f6614f88689a"
    ),
    "v119_event": (
        "a82e880295ec98bea511ecd26989f0fd977d29cedf47edefa811e17d64b19a3b"
    ),
    "v122_event": (
        "d23c081f2e49b0820a9f9448fd5fd1dc15d9512e574e09f242238158c397a8e0"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(scalars: dict, tag: str) -> list[dict]:
    return scalars.get(tag, [])


def values(scalars: dict, tag: str) -> list[float]:
    return [float(row["value"]) for row in rows(scalars, tag)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v119-event", type=Path, required=True)
    parser.add_argument("--v122-event", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V122: {path}")
    v119_event = args.v119_event.resolve()
    v122_event = args.v122_event.resolve()
    v119_result = json.loads(V119_RESULT.read_text(encoding="utf-8"))
    v122_result = json.loads(V122_RESULT.read_text(encoding="utf-8"))
    hashes = {
        "v119_result": sha256(V119_RESULT),
        "v122_result": sha256(V122_RESULT),
        "v119_event": sha256(v119_event),
        "v122_event": sha256(v122_event),
    }
    old = event_scalars(v119_event)
    new = event_scalars(v122_event)
    old_reward = values(old, "eval/episode_reward")
    new_reward = values(new, "eval/episode_reward")
    old_length = values(old, "eval/avg_episode_length")
    new_length = values(new, "eval/avg_episode_length")
    peak_metric = values(
        new, "eval/episode_cost/episode_peak_torque_increment"
    )
    total_loss = values(new, "training/total_loss")
    policy_loss = values(new, "training/policy_loss")
    value_loss = values(new, "training/v_loss")
    kl = values(new, "training/kl_mean")
    scale_weighted_integral = [
        value * 0.02 for value in peak_metric
    ]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "both_cpu_contracts_pass": (
            v119_result.get("status")
            == "PASS_WINNER_V119_TRANSITION_CPU_SMOKE_RECOVERED"
            and v122_result.get("status")
            == "PASS_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
        ),
        "exact_eval_steps_present": all(
            [row["step"] for row in rows(scalars, tag)] == [0, 1024]
            for scalars, tag in (
                (old, "eval/episode_reward"),
                (new, "eval/episode_reward"),
                (old, "eval/avg_episode_length"),
                (new, "eval/avg_episode_length"),
                (
                    new,
                    "eval/episode_cost/episode_peak_torque_increment",
                ),
            )
        ),
        "v122_eval_reward_did_not_collapse": (
            min(new_reward) >= 0.90 * min(old_reward)
        ),
        "v122_episode_length_did_not_collapse": (
            min(new_length) >= 0.95 * min(old_length)
        ),
        "v122_update_losses_finite": all(
            math.isfinite(value)
            for value in total_loss + policy_loss + value_loss + kl
        ),
        "v122_update_kl_below_smoke_hold": max(kl) < 0.05,
        "objective_active_and_not_diluted": (
            len(peak_metric) == 2
            and all(value > 0.0 for value in peak_metric)
            and all(value > 0.0 for value in scale_weighted_integral)
        ),
        "formal_behavior_not_rerun": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v122.cpu_reward_mass_attribution.v1",
        "status": (
            "PASS_WINNER_V122_CPU_REWARD_MASS_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V122_CPU_REWARD_MASS_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "comparison": {
            "v119_eval_episode_reward": old_reward,
            "v122_eval_episode_reward": new_reward,
            "v119_eval_episode_length": old_length,
            "v122_eval_episode_length": new_length,
            "v122_episode_peak_metric_rate_sum": peak_metric,
            "v122_scale_weighted_increment_integral": (
                scale_weighted_integral
            ),
            "v122_training_total_loss": total_loss,
            "v122_training_policy_loss": policy_loss,
            "v122_training_value_loss": value_loss,
            "v122_training_kl_mean": kl,
        },
        "interpretation": {
            "large_metric_is_rate_sum": (
                "The evaluator sums the scale-weighted cost rate without "
                "multiplying by dt; multiplying by 0.02 recovers the "
                "scale-weighted episode peak increment."
            ),
            "reward_path": (
                "The environment multiplies the summed scaled terms by dt "
                "and clips per-step reward at zero. The CPU smoke retains "
                "healthy episode reward and length while the objective is "
                "active."
            ),
            "scalar_search": False,
            "post_hoc_scale_change": False,
        },
        "decision": (
            "PREREGISTER_ONE_V122_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WITHOUT_COLAB"
        ),
        "execution": {
            "new_training_steps": 0,
            "formal_behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_training_authorized": False,
            "colab_authorized": False,
            "behavior_evaluation_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v122 CPU reward-mass attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        "The large TensorBoard cost value is a summed cost rate. After the "
        "required 0.02-second conversion, the active objective leaves CPU "
        "evaluation reward and episode length healthy, with finite PPO "
        "losses and KL. This authorizes only a hosted preregistration, not "
        "training by itself.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
