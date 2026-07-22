#!/usr/bin/env python3
"""Preregister the full Winner-v75 functional-numeric-guard continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION_PREREGISTRATION_20260722.md"
V71B_CONTRACT = ANALYSIS / "winner_v71b_full_loss_binding_correction.json"
V74_RESULT = ANALYSIS / "winner_v74_update638_hidden_replay_numeric_audit_result.json"
V74_RESULT_SHA256 = "c30027f0fdc4cb93499461692ece2ed65bcb831c9858b7c65e80575c81d6bc33"
SOURCE_COUNT = 602
UPDATES = 53
HALF_COUNT = 605
FINAL_COUNT = 655

FUNCTIONAL_THRESHOLDS = {
    "eager_hidden_max_abs_error": 0.0,
    "mean_action_max_abs_delta": 1.0e-6,
    "value_max_abs_delta": 1.0e-5,
    "log_probability_max_abs_delta": 1.0e-4,
    "probability_ratio_max_abs_delta": 1.0e-4,
    "ppo_loss_abs_delta": 1.0e-4,
}

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v71b_full_loss_binding_correction as v71b  # noqa: E402


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
            f"Winner-v75 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v75.functional_numeric_guard_continuation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_53_UPDATE_FUNCTIONAL_NUMERIC_GUARD_ARM_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v75 preregistration identity changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or frozen.get("continuation_optimizer_updates") != UPDATES
        or frozen.get("final_optimizer_count") != FINAL_COMPLETED_UPDATES
        or frozen.get("persistent_checkpoints")
        != {"half": HALF_COMPLETED_UPDATES, "final": FINAL_COMPLETED_UPDATES}
        or frozen.get("functional_numeric_guard")
        != {
            "legacy_scan_hidden_max_abs_error": 2.0e-6,
            "audit_only_if_legacy_scan_guard_crosses": True,
            "eager_hidden_max_abs_error": 0.0,
            "mean_action_max_abs_delta": 1.0e-6,
            "value_max_abs_delta": 1.0e-5,
            "log_probability_max_abs_delta": 1.0e-4,
            "probability_ratio_max_abs_delta": 1.0e-4,
            "ppo_loss_abs_delta": 1.0e-4,
        }
    ):
        raise ValueError("Winner-v75 frozen training changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v75 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v75 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v75 source manifest changed")


'''


FUNCTIONAL_GUARD = '''        scan_hidden_max_abs_error = float(
            ppo_metrics["sampled_hidden_replay_max_abs_error"]
        )
        hidden_replay_functional_evidence = {
            "scan_hidden_max_abs_error": scan_hidden_max_abs_error,
            "legacy_scan_hidden_max_abs_error": 2.0e-6,
            "legacy_scan_guard_passed": scan_hidden_max_abs_error <= 2.0e-6,
            "functional_audit_performed": False,
            "eager_hidden_max_abs_error": None,
            "mean_action_max_abs_delta": None,
            "value_max_abs_delta": None,
            "log_probability_max_abs_delta": None,
            "probability_ratio_max_abs_delta": None,
            "ppo_loss_abs_delta": None,
            "pass": True,
        }
        if scan_hidden_max_abs_error > 2.0e-6:
            stored_hidden = np.asarray(batch_np["hidden"], dtype=np.float32)
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
                        jnp.asarray(
                            batch_np["observations"][environment, tick], dtype=jnp.float32
                        ),
                        jnp.asarray(
                            batch_np["previous_actions"][environment, tick], dtype=jnp.float32
                        ),
                        jnp.asarray(eager_state, dtype=jnp.float32),
                        zero_action,
                    )
                    eager_state = np.asarray(eager_out, dtype=np.float32)
                    eager_hidden[environment, tick] = eager_state
            sampled_mask = np.asarray(batch_np["valid_mask"], dtype=np.float32) > 0.0
            sampled_hidden_mask = np.broadcast_to(
                sampled_mask[..., None], stored_hidden.shape
            )
            eager_hidden_max_abs_error = float(
                np.max(np.abs(eager_hidden - stored_hidden)[sampled_hidden_mask])
            )
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
            stored_ratio = jnp.exp(
                stored_log_probability - batch["old_log_probability"]
            )
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
            sampled_action_mask = np.broadcast_to(
                sampled_mask[..., None], mean_delta.shape
            )
            numeric_metrics = {
                "eager_hidden_max_abs_error": eager_hidden_max_abs_error,
                "mean_action_max_abs_delta": float(
                    np.max(mean_delta[sampled_action_mask])
                ),
                "value_max_abs_delta": float(np.max(value_delta[sampled_mask])),
                "log_probability_max_abs_delta": float(
                    np.max(log_probability_delta[sampled_mask])
                ),
                "probability_ratio_max_abs_delta": float(
                    np.max(ratio_delta[sampled_mask])
                ),
                "ppo_loss_abs_delta": float(
                    np.abs(np.asarray(ppo_loss - stored_ppo_loss))
                ),
            }
            functional_thresholds = preregistration["frozen_training"][
                "functional_numeric_guard"
            ]
            numeric_pass = all(
                numeric_metrics[name] <= functional_thresholds[name]
                for name in numeric_metrics
            )
            hidden_replay_functional_evidence.update(numeric_metrics)
            hidden_replay_functional_evidence["functional_audit_performed"] = True
            hidden_replay_functional_evidence["pass"] = bool(numeric_pass)
'''


def transformed_source() -> tuple[str, str]:
    source, _ = v71b.corrected_source()
    source = replace_exact(
        source,
        'import build_winner_v71_fresh_moment_safeguarded_continuation as v71_builder  # noqa: E402',
        'import build_winner_v75_functional_numeric_guard_continuation as v71_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_preregistration.json"',
    )
    start = source.index("def validate_preregistration")
    end = source.index("def validate_artifact", start)
    source = source[:start] + VALIDATE_PREREGISTRATION + source[end:]
    source = replace_exact(
        source,
        '    parser.add_argument("--isolated-persistent-teacher-training-authorized", action="store_true")',
        '    parser.add_argument("--functional-numeric-guard-continuation-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.isolated_persistent_teacher_training_authorized:",
        "if not args.offline_cpu_only or not args.functional_numeric_guard_continuation_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v71 requires --offline-cpu-only --isolated-persistent-teacher-training-authorized"',
        '"Winner-v75 requires --offline-cpu-only --functional-numeric-guard-continuation-authorized"',
    )
    invariant_marker = '''        if (
            float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 2.0e-6'''
    source = replace_exact(
        source,
        invariant_marker,
        FUNCTIONAL_GUARD
        + '''        if (
            hidden_replay_functional_evidence["pass"] is not True''',
    )
    source = replace_exact(
        source,
        '            "sampled_hidden_replay_max_abs_error": float(ppo_metrics["sampled_hidden_replay_max_abs_error"]),',
        '''            "sampled_hidden_replay_max_abs_error": float(ppo_metrics["sampled_hidden_replay_max_abs_error"]),
            "hidden_replay_functional_evidence": hidden_replay_functional_evidence,''',
    )
    source = replace_exact(
        source,
        '"all_53_hidden_replays_at_most_2e_6": all(row["sampled_hidden_replay_max_abs_error"] <= 2.0e-6 for row in metrics),',
        '"all_53_hidden_replays_functionally_bounded": all(row["hidden_replay_functional_evidence"]["pass"] is True for row in metrics),',
    )
    source = replace_exact(
        source,
        '"schema_version": "winner_v71.isolated_persistent_teacher_training_result.v1",',
        '"schema_version": "winner_v75.functional_numeric_guard_continuation_result.v1",',
    )
    source = replace_exact(
        source,
        '"status": "PASS_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION" if not failed else "HOLD_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION",',
        '"status": "PASS_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION" if not failed else "HOLD_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION",',
    )
    source = replace_exact(
        source,
        '"decision": "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_605_AND_655_ONLY" if not failed else "DO_NOT_EVALUATE_WINNER_V71_POLICY",',
        '"decision": "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_605_AND_655_ONLY" if not failed else "DO_NOT_EVALUATE_WINNER_V75_POLICY",',
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v75_functional_numeric_guard_continuation.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v75 contract: {path}")
    v71b_contract = json.loads(V71B_CONTRACT.read_text(encoding="utf-8"))
    v74_result = json.loads(V74_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V71B_CONTRACT)
        != "c15d9edd05b10979cef47bd43b3d05dabeba2bca21e3ed6978039e716324dc10"
        or sha256(V74_RESULT) != V74_RESULT_SHA256
        or v74_result.get("status")
        != "PASS_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT"
        or v74_result.get("decision")
        != "PREREGISTER_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION_ONLY"
        or v74_result.get("failed_checks") != []
        or v74_result.get("metrics", {}).get("eager_hidden_max_abs_error") != 0.0
        or any(
            v74_result["thresholds"].get(name) != threshold
            for name, threshold in FUNCTIONAL_THRESHOLDS.items()
        )
    ):
        raise ValueError("Winner-v75 selection evidence changed")
    transformed, transformed_hash = transformed_source()
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v75_functional_numeric_guard_continuation.py"),
            "runner": Path("tools/run_winner_v75_functional_numeric_guard_continuation.py"),
            "tests": Path("tests/test_winner_v75_functional_numeric_guard_continuation.py"),
            "v71b_contract": V71B_CONTRACT.relative_to(ROOT),
            "v71b_builder": Path("tools/build_winner_v71b_full_loss_binding_correction.py"),
            "v74_result": V74_RESULT.relative_to(ROOT),
            "v74_preregistration": Path(
                "outputs/analysis/winner_v74_update638_hidden_replay_numeric_audit_preregistration.json"
            ),
        }.items()
    }
    functional_guard = {
        "legacy_scan_hidden_max_abs_error": 2.0e-6,
        "audit_only_if_legacy_scan_guard_crosses": True,
        **FUNCTIONAL_THRESHOLDS,
    }
    payload = {
        "schema_version": "winner_v75.functional_numeric_guard_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION",
        "decision": "AUTHORIZE_ONE_53_UPDATE_FUNCTIONAL_NUMERIC_GUARD_ARM_ONLY",
        "source_checkpoint": v71b_contract["source_checkpoint"],
        "teacher_checkpoint": v71b_contract["teacher_checkpoint"],
        "objective": v71b_contract["objective"],
        "frozen_training": {
            "source_completed_updates": SOURCE_COUNT,
            "continuation_optimizer_updates": UPDATES,
            "final_optimizer_count": FINAL_COUNT,
            "persistent_checkpoints": {"half": HALF_COUNT, "final": FINAL_COUNT},
            "fractions_largest_first": v71b_contract["frozen_training"][
                "fractions_largest_first"
            ],
            "conditional_moment_reset": v71b_contract["frozen_training"][
                "conditional_moment_reset"
            ],
            "functional_numeric_guard": functional_guard,
            "guard_behavior": (
                "retain the legacy 2e-6 fast path; on a crossing require bit-exact eager "
                "replay and every unchanged V59 functional bound"
            ),
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "persistent_snapshots": True,
        },
        "v74_evidence": {
            "path": V74_RESULT.relative_to(ROOT).as_posix(),
            "bytes": V74_RESULT.stat().st_size,
            "sha256": sha256(V74_RESULT),
            "classification": v74_result["classification"],
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the unchanged persistence gate for counts 605 and 655",
        },
        "transformation": {
            "v71b_corrected_source_sha256": v71b.corrected_source()[1],
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
                "# Winner-v75 functional numeric-guard continuation preregistration",
                "",
                "- Source / half / final counts: `602 / 605 / 655`",
                "- Updates: `53`, each `80 x 250`, CPU only",
                "- Legacy `2e-6` scan guard remains the fast path",
                "- On crossing: eager replay exact; action `1e-6`, value `1e-5`, logp/ratio/PPO `1e-4`",
                "- Objective, Adam safeguard, moment reset, checkpoints, and selection rule unchanged",
                "- Support / selection / deployment / robot: `0 / false / false / 0`",
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
