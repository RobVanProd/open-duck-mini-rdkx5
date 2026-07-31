#!/usr/bin/env python3
"""Preregister the zero-update Winner-v74 count-638 replay numeric audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v74_update638_hidden_replay_numeric_audit_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT_PREREGISTRATION_20260722.md"
V73_PREREG = ANALYSIS / "winner_v73_update638_contract_attribution_preregistration.json"
V73_RESULT = ANALYSIS / "winner_v73_update638_contract_attribution_result.json"
V73_RESULT_SHA256 = "7d3a0dd6a528e18d7a1f6503abdae1b13864e4a013ea7bd981605096565b1a18"
V59_PREREG = ANALYSIS / "winner_v59_hidden_replay_numeric_attribution_preregistration.json"
V59_RESULT = ANALYSIS / "winner_v59_hidden_replay_numeric_attribution_result.json"
V59_RESULT_SHA256 = "2bc025115d2c2d4eba2aca7e8d0670b2c9e6f90fc2d96507d38034cbc946c39b"

FUNCTIONAL_THRESHOLDS = {
    "eager_hidden_max_abs_error": 0.0,
    "mean_action_max_abs_delta": 1.0e-6,
    "value_max_abs_delta": 1.0e-5,
    "log_probability_max_abs_delta": 1.0e-4,
    "probability_ratio_max_abs_delta": 1.0e-4,
    "ppo_loss_abs_delta": 1.0e-4,
}

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v73b_empty_directory_check_correction as v73b  # noqa: E402


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


def replace_exact(source: str, old: str, new: str, *, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v74 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v74 region changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v74.update638_hidden_replay_numeric_audit_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT_ONLY"
        or value.get("diagnostic", {}).get("source_optimizer_count") != 637
        or value.get("diagnostic", {}).get("attempted_optimizer_count") != 638
        or value.get("functional_thresholds")
        != {
            "eager_hidden_max_abs_error": 0.0,
            "mean_action_max_abs_delta": 1.0e-6,
            "value_max_abs_delta": 1.0e-5,
            "log_probability_max_abs_delta": 1.0e-4,
            "probability_ratio_max_abs_delta": 1.0e-4,
            "ppo_loss_abs_delta": 1.0e-4,
        }
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v74 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v74 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v74 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v74 source manifest changed")


'''


NUMERIC_AUDIT = '''        stored_hidden = np.asarray(batch_np["hidden"], dtype=np.float32)
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
        crossing = np.argwhere(sampled_hidden_mask & (scan_error > np.float32(2.0e-6)))
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
        functional_thresholds = preregistration["functional_thresholds"]
        functional_checks = {
            name: numeric_metrics[name] <= threshold
            for name, threshold in functional_thresholds.items()
        }
        checks = {
            "source_count_637_exact": int(np.asarray(optimizer["count"])) == 637,
            "rollout_index_637_exact": rollout_update_index == 637,
            "would_complete_638_exact": completed_updates == 638,
            "v73_sole_failure_is_hidden_replay_at_2e_6": preregistration[
                "v73_result"
            ]["failed_checks"] == ["sampled_hidden_replay_at_most_2e_6"],
            "scan_metric_reproduces_v73": numeric_metrics["scan_hidden_max_abs_error"]
            == float(ppo_metrics["sampled_hidden_replay_max_abs_error"]),
            "scan_exceeds_legacy_2e_6_guard": numeric_metrics[
                "scan_hidden_max_abs_error"
            ] > 2.0e-6,
            "eager_replay_bit_exact_to_rollout": functional_checks[
                "eager_hidden_max_abs_error"
            ],
            "mean_action_delta_within_1e_6": functional_checks[
                "mean_action_max_abs_delta"
            ],
            "value_delta_within_1e_5": functional_checks["value_max_abs_delta"],
            "log_probability_delta_within_1e_4": functional_checks[
                "log_probability_max_abs_delta"
            ],
            "probability_ratio_delta_within_1e_4": functional_checks[
                "probability_ratio_max_abs_delta"
            ],
            "ppo_loss_delta_within_1e_4": functional_checks["ppo_loss_abs_delta"],
            "all_preupdate_values_finite": training.finite_tree({
                "ppo_loss": ppo_loss,
                "ppo_metrics": ppo_metrics,
                "stored_ppo_loss": stored_ppo_loss,
                "numeric_metrics": numeric_metrics,
            }),
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        passed = not failed_checks
        result = {
            "schema_version": "winner_v74.update638_hidden_replay_numeric_audit_result.v1",
            "status": (
                "PASS_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT"
                if passed
                else "HOLD_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT"
            ),
            "classification": (
                "EAGER_SCAN_FLOAT32_DRIFT_WITH_BOUNDED_POLICY_EFFECT_AND_STALE_ABSOLUTE_SCAN_GUARD"
                if passed
                else "COUNT638_HIDDEN_REPLAY_DISCREPANCY_NOT_PROVEN_BOUNDED"
            ),
            "decision": (
                "PREREGISTER_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION_ONLY"
                if passed
                else "DO_NOT_CONTINUE_WINNER_V71"
            ),
            "checks": {name: bool(value) for name, value in checks.items()},
            "failed_checks": failed_checks,
            "thresholds": {
                "legacy_scan_hidden_max_abs_error": 2.0e-6,
                **functional_thresholds,
            },
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
                "rollout_update_indices": [637],
                "scheduled_episode_slots": 20000,
                "optimizer_updates": 0,
                "snapshots_written": 0,
                "onnx_graphs_written": 0,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": preregistration["authority"],
            "sources": preregistration["sources"],
            "source_manifest_sha256": preregistration["source_manifest_sha256"],
        }
        if any(any((args.work_root / name).iterdir()) for name in ("snapshots", "graphs")):
            raise ValueError("Winner-v74 numeric audit wrote a training artifact")
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        print(f"classification={result['classification']}")
        print(f"decision={result['decision']}")
        print(f"sha256={sha256(args.output)}")
        return 0
'''


def transformed_source() -> tuple[str, str]:
    source, _ = v73b.corrected_source()
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v73_update638_contract_attribution_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v74_update638_hidden_replay_numeric_audit_preregistration.json"',
    )
    source = replace_region(
        source,
        "def validate_preregistration",
        "def validate_artifact",
        VALIDATE_PREREGISTRATION,
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--update638-contract-attribution-authorized", action="store_true")',
        '    parser.add_argument("--update638-hidden-replay-numeric-audit-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.update638_contract_attribution_authorized:",
        "if not args.offline_cpu_only or not args.update638_hidden_replay_numeric_audit_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v73 requires --offline-cpu-only --update638-contract-attribution-authorized"',
        '"Winner-v74 requires --offline-cpu-only --update638-hidden-replay-numeric-audit-authorized"',
    )
    source = replace_region(
        source,
        '        checks = {\n            "sampled_hidden_replay_at_most_2e_6"',
        "        reset_keys = tuple(sorted(v29.ANCHOR_GRADIENT_KEYS))",
        NUMERIC_AUDIT,
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v74_update638_hidden_replay_numeric_audit.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v74 contract: {path}")
    v73_prereg = json.loads(V73_PREREG.read_text(encoding="utf-8"))
    v73_result = json.loads(V73_RESULT.read_text(encoding="utf-8"))
    v59_prereg = json.loads(V59_PREREG.read_text(encoding="utf-8"))
    v59_result = json.loads(V59_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V73_RESULT) != V73_RESULT_SHA256
        or v73_result.get("status")
        != "PASS_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION"
        or v73_result.get("decision")
        != "PREREGISTER_HIDDEN_REPLAY_TOLERANCE_CAUSAL_AUDIT_ONLY"
        or v73_result.get("failed_checks") != ["sampled_hidden_replay_at_most_2e_6"]
        or sha256(V59_RESULT) != V59_RESULT_SHA256
        or v59_result.get("classification")
        != "EAGER_SCAN_FLOAT32_NUMERIC_DRIFT_WITH_BOUNDED_POLICY_EFFECT"
        or {
            key: v59_prereg["thresholds"][key] for key in FUNCTIONAL_THRESHOLDS
        }
        != FUNCTIONAL_THRESHOLDS
    ):
        raise ValueError("Winner-v74 selection evidence changed")
    transformed, transformed_hash = transformed_source()
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v74_update638_hidden_replay_numeric_audit.py"),
            "runner": Path("tools/run_winner_v74_update638_hidden_replay_numeric_audit.py"),
            "tests": Path("tests/test_winner_v74_update638_hidden_replay_numeric_audit.py"),
            "v73_preregistration": V73_PREREG.relative_to(ROOT),
            "v73_result": V73_RESULT.relative_to(ROOT),
            "v73b_correction": Path(
                "outputs/analysis/winner_v73b_empty_directory_check_correction.json"
            ),
            "v59_preregistration": V59_PREREG.relative_to(ROOT),
            "v59_result": V59_RESULT.relative_to(ROOT),
            "v73b_builder": Path("tools/build_winner_v73b_empty_directory_check_correction.py"),
        }.items()
    }
    payload = {
        "schema_version": "winner_v74.update638_hidden_replay_numeric_audit_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT_ONLY",
        "causal_question": (
            "Does count 638 reproduce the previously proven eager-versus-lax.scan float32 "
            "execution-order drift while eager replay remains bit-exact and every frozen "
            "downstream policy/PPO effect remains within the V59 functional bounds?"
        ),
        "prior_invocation": v73_prereg["prior_invocation"],
        "source_checkpoint": v73_prereg["source_checkpoint"],
        "teacher_checkpoint": v73_prereg["teacher_checkpoint"],
        "v73_result": {
            "path": V73_RESULT.relative_to(ROOT).as_posix(),
            "bytes": V73_RESULT.stat().st_size,
            "sha256": sha256(V73_RESULT),
            "failed_checks": v73_result["failed_checks"],
        },
        "v59_numeric_precedent": {
            "path": V59_RESULT.relative_to(ROOT).as_posix(),
            "bytes": V59_RESULT.stat().st_size,
            "sha256": sha256(V59_RESULT),
            "classification": v59_result["classification"],
        },
        "functional_thresholds": FUNCTIONAL_THRESHOLDS,
        "threshold_basis": {
            "source": "unchanged preregistered Winner-v59 functional bounds",
            "scan_hidden_2e_6": "reproduced and reported but not enlarged or searched",
            "eager_hidden": "must remain bit-exact to the stored rollout",
            "downstream": "all fixed action/value/log-probability/ratio/PPO bounds must pass",
            "coefficient_or_threshold_search": False,
        },
        "diagnostic": {
            "source_optimizer_count": 637,
            "rollout_update_index": 637,
            "attempted_optimizer_count": 638,
            "environments": 80,
            "ticks_per_environment": 250,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "diagnostic_authorized": True,
            "continuation_authorized": False,
            "formal_support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "v73b_corrected_source_sha256": v73b.corrected_source()[1],
            "transformed_source_sha256": transformed_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v74 update-638 hidden-replay numeric audit preregistration",
                "",
                "- Source / attempted count: `637 / 638`",
                "- Eager replay must be bit-exact",
                "- Fixed V59 bounds: action `1e-6`, value `1e-5`, logp/ratio/PPO `1e-4`",
                "- The crossed scan bound `2e-6` is reported, not enlarged or searched",
                "- Optimizer updates / support / robot: `0 / 0 / 0`",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
