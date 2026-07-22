#!/usr/bin/env python3
"""Freeze one zero-update eager-versus-scan hidden replay attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v59_hidden_replay_numeric_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION_PREREGISTRATION_20260722.md"
V58B_PREREG = ANALYSIS / "winner_v58b_guard_failure_attribution_preregistration.json"
V58B_RESULT = ANALYSIS / "winner_v58b_guard_failure_attribution_result.json"
V58B_RESULT_SHA256 = "2070bcca541d5cb0545e34498dba34d34447af64bac13d3e998041684e91d3c3"

THRESHOLDS = {
    "scan_hidden_max_abs_error": 2.0e-6,
    "eager_hidden_max_abs_error": 0.0,
    "mean_action_max_abs_delta": 1.0e-6,
    "value_max_abs_delta": 1.0e-5,
    "log_probability_max_abs_delta": 1.0e-4,
    "probability_ratio_max_abs_delta": 1.0e-4,
    "ppo_loss_abs_delta": 1.0e-4,
}

CUSTOM_SOURCES = {
    "v59_builder": Path(
        "tools/build_winner_v59_hidden_replay_numeric_attribution_preregistration.py"
    ),
    "v59_runner": Path("tools/run_winner_v59_hidden_replay_numeric_attribution.py"),
    "v59_tests": Path("tests/test_winner_v59_hidden_replay_numeric_attribution.py"),
    "v58b_result": Path(
        "outputs/analysis/winner_v58b_guard_failure_attribution_result.json"
    ),
    "v58b_preregistration": Path(
        "outputs/analysis/winner_v58b_guard_failure_attribution_preregistration.json"
    ),
    "v58b_transform_builder": Path(
        "tools/build_winner_v58b_guard_failure_attribution_preregistration.py"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    import build_winner_v58b_guard_failure_attribution_preregistration as v58b

    source, _ = v58b.transformed_source()
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v59 transform count changed: expected {count}, "
                f"found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )

    replace("winner_v58b", "winner_v59", source.count("winner_v58b"))
    replace("Winner-v58b", "Winner-v59", source.count("Winner-v58b"))
    replace("WINNER_V58B", "WINNER_V59", source.count("WINNER_V58B"))
    replace(
        "winner_v59.guard_failure_attribution_preregistration.v1",
        "winner_v59.hidden_replay_numeric_attribution_preregistration.v1",
    )
    replace(
        "PREREGISTERED_WINNER_V59_GUARD_FAILURE_ATTRIBUTION",
        "PREREGISTERED_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION",
    )
    replace(
        "AUTHORIZE_ONE_ZERO_UPDATE_WINNER_V58_GUARD_ATTRIBUTION_ONLY",
        "AUTHORIZE_ONE_ZERO_UPDATE_EAGER_SCAN_NUMERIC_ATTRIBUTION_ONLY",
    )
    replace(
        'authority.get("retry_authorized") is not False',
        'authority.get("continuation_authorized") is not False',
    )

    start = source.index(
        "        attribution_complete = bool(failed_original) and bool(finite_preupdate)"
    )
    end = source.index("        after, optimizer = training.adam_step(", start)
    old = source[start:end]
    new = '''        stored_hidden = np.asarray(batch_np["hidden"], dtype=np.float32)
        scan_hidden = np.asarray(
            v20.recurrent_hidden_trajectory(
                before,
                jnp.asarray(batch_np["observations"], dtype=jnp.float32),
                jnp.asarray(batch_np["previous_actions"], dtype=jnp.float32),
            ),
            dtype=np.float32,
        )
        eager_hidden = np.zeros_like(stored_hidden)
        zero_action = jnp.zeros((training.ACTION_SIZE,), dtype=jnp.float32)
        for environment in range(stored_hidden.shape[0]):
            eager_state = np.zeros((training.HIDDEN_SIZE,), dtype=np.float32)
            for tick in range(stored_hidden.shape[1]):
                eager_out, _ = training.response_step(
                    before,
                    jnp.asarray(batch_np["observations"][environment, tick], dtype=jnp.float32),
                    jnp.asarray(batch_np["previous_actions"][environment, tick], dtype=jnp.float32),
                    jnp.asarray(eager_state, dtype=jnp.float32),
                    zero_action,
                )
                eager_state = np.asarray(eager_out, dtype=np.float32)
                eager_hidden[environment, tick] = eager_state

        sampled_mask = np.asarray(batch_np["valid_mask"], dtype=np.float32) > 0.0
        sampled_hidden_mask = np.broadcast_to(sampled_mask[..., None], stored_hidden.shape)
        scan_error = np.abs(scan_hidden - stored_hidden)
        eager_error = np.abs(eager_hidden - stored_hidden)
        sampled_scan_error = scan_error[sampled_hidden_mask]
        sampled_eager_error = eager_error[sampled_hidden_mask]
        masked_scan_error = np.where(sampled_hidden_mask, scan_error, np.float32(-1.0))
        maximum_flat = int(np.argmax(masked_scan_error))
        maximum_environment, maximum_tick, maximum_hidden_index = (
            int(value) for value in np.unravel_index(maximum_flat, masked_scan_error.shape)
        )
        crossing = np.argwhere(sampled_hidden_mask & (scan_error > np.float32(1.0e-6)))
        first_crossing = None
        if crossing.size:
            environment, tick, hidden_index = (int(value) for value in crossing[0])
            first_crossing = {
                "environment": environment,
                "tick": tick,
                "hidden_index": hidden_index,
                "configuration_id": identifiers[environment],
                "plant": smoke.PLANTS[environment % 2],
                "absolute_error": float(scan_error[environment, tick, hidden_index]),
            }

        stored_mean, stored_value = training.stage2_mean_value(
            before, jnp.asarray(stored_hidden, dtype=jnp.float32)
        )
        scan_mean, scan_value = training.stage2_mean_value(
            before, jnp.asarray(scan_hidden, dtype=jnp.float32)
        )
        stored_log_probability = training.diagonal_gaussian_log_probability(
            batch["raw_samples"], stored_mean, before["training_only_log_std"]
        )
        scan_log_probability = training.diagonal_gaussian_log_probability(
            batch["raw_samples"], scan_mean, before["training_only_log_std"]
        )
        stored_ratio = jnp.exp(stored_log_probability - batch["old_log_probability"])
        scan_ratio = jnp.exp(scan_log_probability - batch["old_log_probability"])
        stored_batch = dict(batch)
        stored_batch["hidden"] = jnp.asarray(stored_hidden, dtype=jnp.float32)
        stored_ppo_loss, _ = training.stage2_ppo_loss(
            before,
            stored_batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )
        mean_delta = np.abs(np.asarray(scan_mean) - np.asarray(stored_mean))
        value_delta = np.abs(np.asarray(scan_value) - np.asarray(stored_value))
        log_probability_delta = np.abs(
            np.asarray(scan_log_probability) - np.asarray(stored_log_probability)
        )
        ratio_delta = np.abs(np.asarray(scan_ratio) - np.asarray(stored_ratio))
        sampled_action_mask = np.broadcast_to(sampled_mask[..., None], mean_delta.shape)
        numeric_metrics = {
            "scan_hidden_max_abs_error": float(np.max(sampled_scan_error)),
            "scan_hidden_mean_abs_error": float(np.mean(sampled_scan_error)),
            "scan_hidden_p95_abs_error": float(np.percentile(sampled_scan_error, 95.0)),
            "scan_hidden_p99_abs_error": float(np.percentile(sampled_scan_error, 99.0)),
            "scan_hidden_p99_9_abs_error": float(np.percentile(sampled_scan_error, 99.9)),
            "eager_hidden_max_abs_error": float(np.max(sampled_eager_error)),
            "mean_action_max_abs_delta": float(np.max(mean_delta[sampled_action_mask])),
            "value_max_abs_delta": float(np.max(value_delta[sampled_mask])),
            "log_probability_max_abs_delta": float(
                np.max(log_probability_delta[sampled_mask])
            ),
            "probability_ratio_max_abs_delta": float(np.max(ratio_delta[sampled_mask])),
            "ppo_loss_abs_delta": float(np.abs(np.asarray(ppo_loss - stored_ppo_loss))),
        }
        numeric_thresholds = {
            "scan_hidden_max_abs_error": 2.0e-6,
            "eager_hidden_max_abs_error": 0.0,
            "mean_action_max_abs_delta": 1.0e-6,
            "value_max_abs_delta": 1.0e-5,
            "log_probability_max_abs_delta": 1.0e-4,
            "probability_ratio_max_abs_delta": 1.0e-4,
            "ppo_loss_abs_delta": 1.0e-4,
        }
        numeric_checks = {
            name: numeric_metrics[name] <= threshold
            for name, threshold in numeric_thresholds.items()
        }
        checks = {
            "source_count_476_exact": int(np.asarray(optimizer["count"])) == 476,
            "rollout_index_476_exact": rollout_update_index == 476,
            "would_complete_477_exact": completed_updates == 477,
            "sole_original_failure_is_hidden_replay_at_1e_6":
                failed_original == ["hidden_replay_at_most_1e_6"],
            "all_preupdate_values_finite": bool(finite_preupdate),
            "eager_replay_bit_exact_to_rollout":
                numeric_checks["eager_hidden_max_abs_error"],
            "scan_hidden_within_preregistered_2e_6":
                numeric_checks["scan_hidden_max_abs_error"],
            "mean_action_delta_within_1e_6":
                numeric_checks["mean_action_max_abs_delta"],
            "value_delta_within_1e_5": numeric_checks["value_max_abs_delta"],
            "log_probability_delta_within_1e_4":
                numeric_checks["log_probability_max_abs_delta"],
            "probability_ratio_delta_within_1e_4":
                numeric_checks["probability_ratio_max_abs_delta"],
            "ppo_loss_delta_within_1e_4": numeric_checks["ppo_loss_abs_delta"],
        }
        failed = sorted(name for name, passed in checks.items() if not passed)
        result = {
            "schema_version": "winner_v59.hidden_replay_numeric_attribution_result.v1",
            "status": (
                "PASS_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION"
                if not failed
                else "HOLD_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION"
            ),
            "decision": (
                "AUTHORIZE_REVISED_NUMERIC_GUARD_CONTINUATION_PREREGISTRATION_ONLY"
                if not failed
                else "DO_NOT_CONTINUE_INTEGRATED_FIRST_TICK_ARM"
            ),
            "classification": (
                "EAGER_SCAN_FLOAT32_NUMERIC_DRIFT_WITH_BOUNDED_POLICY_EFFECT"
                if not failed
                else "HIDDEN_REPLAY_DISCREPANCY_NOT_PROVEN_BOUNDED"
            ),
            "checks": checks,
            "failed_checks": failed,
            "original_guard_checks": original_guard_checks,
            "failed_original_guard_predicates": failed_original,
            "thresholds": numeric_thresholds,
            "metrics": numeric_metrics,
            "maximum_error_location": {
                "environment": maximum_environment,
                "tick": maximum_tick,
                "hidden_index": maximum_hidden_index,
                "configuration_id": identifiers[maximum_environment],
                "plant": smoke.PLANTS[maximum_environment % 2],
                "absolute_error": float(
                    scan_error[maximum_environment, maximum_tick, maximum_hidden_index]
                ),
            },
            "first_legacy_threshold_crossing": first_crossing,
            "execution": {
                "rollout_update_indices": [476],
                "scheduled_episode_slots": 20_000,
                "optimizer_updates": 0,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": {
                "robot_clearance": False,
                "continuation_executed": False,
                "formal_support_gate_executed": False,
                "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
                "pass_authorizes_only": "a separate continuation preregistration with the exact 2e-6 numeric replay guard",
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        return 0

'''
    source = source[:start] + new + source[end:]
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
            "replacement_count": 1,
        }
    )
    compile(source, "winner_v59_hidden_replay_numeric_attribution.py", "exec")
    return source, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v59 evidence: {path}")
    if not V58B_RESULT.is_file() or sha256(V58B_RESULT) != V58B_RESULT_SHA256:
        raise ValueError("Winner-v59 source result changed")
    old = json.loads(V58B_PREREG.read_text(encoding="utf-8"))
    result = json.loads(V58B_RESULT.read_text(encoding="utf-8"))
    if (
        old.get("status")
        != "PREREGISTERED_WINNER_V58B_GUARD_FAILURE_ATTRIBUTION"
        or result.get("status") != "PASS_WINNER_V58B_GUARD_FAILURE_ATTRIBUTION"
        or result.get("decision") != "DO_NOT_RETRY_WINNER_V58"
        or result.get("failed_original_guard_predicates")
        != ["hidden_replay_at_most_1e_6"]
        or result.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v59 source authority changed")
    transformed, receipts = transformed_source()
    sources = dict(old["sources"])
    for name, path in CUSTOM_SOURCES.items():
        sources[name] = {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
    payload = json.loads(json.dumps(old))
    payload.update(
        {
            "schema_version": "winner_v59.hidden_replay_numeric_attribution_preregistration.v1",
            "status": "PREREGISTERED_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION",
            "decision": "AUTHORIZE_ONE_ZERO_UPDATE_EAGER_SCAN_NUMERIC_ATTRIBUTION_ONLY",
            "causal_question": (
                "Is the 1.125e-6 hidden replay discrepancy bounded float32 execution-path "
                "drift between the eager rollout recurrence and lax.scan replay, with a "
                "negligible effect on policy outputs and PPO loss?"
            ),
            "thresholds": THRESHOLDS,
            "threshold_basis": {
                "scan_hidden": (
                    "2e-6 is the next power-of-two strict bound above the failed legacy 1e-6 guard"
                ),
                "eager_hidden": "must reproduce the stored rollout bit-exactly",
                "downstream": (
                    "fixed float32-scale output and objective tolerances selected before execution"
                ),
                "no_search": True,
            },
            "source_result": {
                "path": V58B_RESULT.relative_to(ROOT).as_posix(),
                "bytes": V58B_RESULT.stat().st_size,
                "sha256": sha256(V58B_RESULT),
            },
            "sources": sources,
            "source_manifest_sha256": canonical_sha256(sources),
            "transformation": {
                "base_v58b_transformed_source_sha256": old["transformation"][
                    "transformed_source_sha256"
                ],
                "transformed_source_sha256": hashlib.sha256(
                    transformed.encode()
                ).hexdigest(),
                "replacements": receipts,
                "replacement_groups": len(receipts),
            },
            "selection_rule": {
                "all_numeric_checks_must_pass": True,
                "pass_authorizes_only": (
                    "a separately preregistered continuation with an exact 2e-6 numeric replay guard"
                ),
                "failure_closes_integrated_first_tick_arm": True,
                "no_metric_or_coefficient_search": True,
            },
            "authority": {
                "robot_clearance": False,
                "diagnostic_authorized": True,
                "continuation_authorized": False,
                "formal_support_gate_authorized": False,
                "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            },
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v59 hidden-replay numeric attribution preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source / rollout: `476 / 476`",
                "- Legacy / test hidden bound: `1e-6 / 2e-6`",
                "- Eager replay: must be bit-exact to stored rollout",
                "- Output bounds: mean `1e-6`, value `1e-5`, logp/ratio `1e-4`",
                "- PPO-loss bound: `1e-4`",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
                "- Continuation authorization: `false`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
