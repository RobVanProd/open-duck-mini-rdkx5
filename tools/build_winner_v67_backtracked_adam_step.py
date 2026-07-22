#!/usr/bin/env python3
"""Preregister one deterministic backtracked-Adam proof step."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v67_backtracked_adam_step_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V67_BACKTRACKED_ADAM_STEP_CONTRACT_20260722.md"
V66_RESULT = ANALYSIS / "winner_v66_failed_step_attribution_result.json"
V66_CONTRACT = ANALYSIS / "winner_v66_failed_step_attribution_preregistration.json"
V66_RESULT_SHA256 = "dc25ee23ecfaa7910c39e3a3ff4c00b7f97f52a9a0b11d630e9d0dff3cfc25de"
SOURCE_COUNT = 574
COMPLETED_COUNT = 575
FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625)
EXPECTED_ACCEPTED_FRACTION = 0.25
EXPECTED_LOSS_BEFORE = 0.003351836698129773
EXPECTED_LOSS_AFTER = 0.0033518008422106504

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v66_failed_step_attribution as v66  # noqa: E402


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
            f"Winner-v67 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v67 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def select_first_descent(
    rows: Sequence[Mapping[str, float]], loss_before: float
) -> Mapping[str, float] | None:
    for expected, row in zip(FRACTIONS, rows, strict=True):
        if float(row["fraction"]) != expected:
            raise ValueError("Winner-v67 backtracking order changed")
        if float(row["loss"]) < loss_before:
            return row
    return None


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v67.backtracked_adam_step_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V67_BACKTRACKED_ADAM_STEP"
        or value.get("decision")
        != "AUTHORIZE_EXACTLY_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("step", {}).get("source_optimizer_count")
        != SOURCE_COMPLETED_UPDATES
        or value.get("step", {}).get("completed_optimizer_count") != 575
        or value.get("step", {}).get("fractions_largest_first")
        != [1.0, 0.5, 0.25, 0.125, 0.0625]
        or value.get("step", {}).get("expected_accepted_fraction") != 0.25
    ):
        raise ValueError("Winner-v67 preregistration changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v67 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v67 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v67 source manifest changed")


'''

ATTRIBUTION_EVIDENCE = '''    attribution = json.loads(V66_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V66_RESULT)
        != "dc25ee23ecfaa7910c39e3a3ff4c00b7f97f52a9a0b11d630e9d0dff3cfc25de"
        or attribution.get("status")
        != "PASS_WINNER_V66_FAILED_STEP_ATTRIBUTION"
        or attribution.get("classification")
        != "INHERITED_ADAM_FULL_STEP_OVERSHOOT"
        or attribution.get("decision")
        != "PREREGISTER_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP_PROOF"
        or attribution.get("failed_checks") != []
    ):
        raise ValueError("Winner-v67 attribution evidence changed")
'''

STEP_BLOCK = '''        raw_after, proposed_optimizer = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        full_after = training.clamp_stage2_parameters(raw_after)
        full.validate_log_std(full_after)
        full_loss, full_metrics = static_teacher_objective(full_after)
        full_delta = jax.tree_util.tree_map(
            lambda old, new: jnp.asarray(new, dtype=jnp.float32)
            - jnp.asarray(old, dtype=jnp.float32),
            before,
            full_after,
        )
        rows = []
        trials = []
        for fraction in preregistration["step"]["fractions_largest_first"]:
            trial = jax.tree_util.tree_map(
                lambda old, change: jnp.asarray(old, dtype=jnp.float32)
                + jnp.asarray(fraction, dtype=jnp.float32)
                * jnp.asarray(change, dtype=jnp.float32),
                before,
                full_delta,
            )
            trial = training.clamp_stage2_parameters(trial)
            full.validate_log_std(trial)
            loss, trial_metrics = static_teacher_objective(trial)
            rows.append({
                "fraction": float(fraction),
                "loss": float(loss),
                "loss_delta": float(loss) - float(teacher_loss),
                "maximum_selected_action_delta": float(
                    trial_metrics["maximum_selected_action_delta"]
                ),
            })
            trials.append(trial)
        accepted_row = v67_builder.select_first_descent(rows, float(teacher_loss))
        if accepted_row is None:
            raise ValueError("Winner-v67 backtracking found no strict descent")
        accepted_index = next(
            index for index, row in enumerate(rows) if row is accepted_row
        )
        accepted = trials[accepted_index]
        accepted_fraction = float(accepted_row["fraction"])
        accepted_loss, accepted_metrics = static_teacher_objective(accepted)
        if (
            float(teacher_loss) != preregistration["step"]["expected_loss_before"]
            or accepted_fraction
            != preregistration["step"]["expected_accepted_fraction"]
            or float(accepted_loss)
            != preregistration["step"]["expected_loss_after"]
        ):
            raise ValueError("Winner-v67 frozen accepted step changed")
        parameters_after = v21.merge_joint_trainable(parameters, accepted)
        optimizer_after = proposed_optimizer
        deltas = v20.leaf_max_abs_delta(before, accepted)
        snapshot_path = args.work_root / "snapshots" / "snapshot_backtracked_adam_update_575.npz"
        snapshot_receipt = v22v2.save_snapshot(
            snapshot_path,
            parameters_after,
            optimizer_after,
            {
                "stage": "backtracked_persistent_teacher_joint_stage2",
                "completed_updates": 575,
                "source_completed_updates": 574,
                "source_snapshot_sha256": source_receipt["sha256"],
                "teacher_snapshot_sha256": teacher_receipt["sha256"],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "accepted_backtracking_fraction": accepted_fraction,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            restored["target_mean"],
            restored["target_std"],
        )
        loaded = v22v2.load_snapshot(snapshot_path)
        snapshot_exact = bool(
            common.tree_equal(parameters_after, loaded["parameters"])
            and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
            and common.tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
            and common.tree_equal(optimizer_after["v"], loaded["optimizer"]["v"])
            and np.array_equal(restored["target_mean"], loaded["target_mean"])
            and np.array_equal(restored["target_std"], loaded["target_std"])
            and loaded["metadata"].get("stage")
            == "backtracked_persistent_teacher_joint_stage2"
            and loaded["metadata"].get("completed_updates") == 575
            and loaded["metadata"].get("accepted_backtracking_fraction") == 0.25
        )
        graph = graph_receipt(
            smoke=smoke,
            networks=networks,
            training=training,
            parameters=parameters_after,
            observations=observations,
            path=args.work_root / "graphs" / "winner_v67_backtracked_adam_update_575.onnx",
            label="proof",
            completed_updates=575,
        )
        checks = {
            "v66_attribution_and_count_574_source_exact": True,
            "full_step_non_descent_reproduced": float(full_loss) >= float(teacher_loss),
            "largest_first_fraction_order_exact": [row["fraction"] for row in rows]
            == [1.0, 0.5, 0.25, 0.125, 0.0625],
            "first_strict_descent_fraction_exactly_one_quarter": accepted_fraction == 0.25,
            "same_batch_loss_strictly_decreases": float(accepted_loss) < float(teacher_loss),
            "optimizer_count_574_to_575_exact": int(np.asarray(optimizer_after["count"])) == 575,
            "all_six_policy_leaves_changed": all(
                deltas[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
            ),
            "all_parameters_optimizer_losses_metrics_finite": training.finite_tree({
                "parameters": parameters_after,
                "optimizer": optimizer_after,
                "teacher_loss": teacher_loss,
                "full_loss": full_loss,
                "accepted_loss": accepted_loss,
                "full_metrics": full_metrics,
                "accepted_metrics": accepted_metrics,
                "rows": rows,
            }),
            "snapshot_readback_exact": snapshot_exact,
            "onnx_abi_exact": graph["contract"]["abi_exact"],
            "onnx_training_only_tensors_absent": graph["contract"][
                "training_only_tensors_absent"
            ],
            "onnx_jax_chain_at_most_1e_7": graph["contract"][
                "jax_onnx_at_most_1e_7"
            ],
            "onnx_previous_action_chain_exact": graph["contract"][
                "previous_action_out_equals_action_bit_exact"
            ],
            "formal_support_continuation_robot_zero": True,
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        if failed_checks:
            raise ValueError(f"Winner-v67 proof invalid: {failed_checks}")
        result = {
            "schema_version": "winner_v67.backtracked_adam_step_result.v1",
            "status": "PASS_WINNER_V67_BACKTRACKED_ADAM_STEP",
            "decision": "PREREGISTER_BOUNDED_DETERMINISTIC_BACKTRACKED_ADAM_CONTINUATION_ONLY",
            "source": {
                "snapshot": source_receipt,
                "optimizer_count": 574,
                "rollout_update_index": rollout_update_index,
                "episode_receipts_sha256": episode_hash,
            },
            "optimization": {
                "optimizer_count_before": 574,
                "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
                "loss_before": float(teacher_loss),
                "full_step_loss": float(full_loss),
                "accepted_loss": float(accepted_loss),
                "accepted_loss_delta": float(accepted_loss) - float(teacher_loss),
                "accepted_fraction": accepted_fraction,
                "backtracking_rows": rows,
                "leaf_max_abs_delta": deltas,
            },
            "snapshot": snapshot_receipt,
            "graph": graph,
            "checks": {key: bool(value) for key, value in checks.items()},
            "failed_checks": [],
            "execution": {
                "optimizer_updates": 1,
                "continuation_optimizer_updates": 0,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": preregistration["authority"],
            "sources": preregistration["sources"],
            "source_manifest_sha256": preregistration["source_manifest_sha256"],
        }
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        print(f"accepted_fraction={accepted_fraction}")
        print(f"sha256={sha256(args.output)}")
        return 0'''


def transformed_source() -> tuple[str, str]:
    source, _ = v66.transformed_source()
    source = replace_exact(source, "Winner-v66", "Winner-v67", count=30)
    source = replace_exact(source, "winner_v66", "winner_v67", count=6)
    source = replace_exact(source, "WINNER_V66", "WINNER_V67", count=6)
    source = replace_exact(
        source,
        'import build_winner_v67_failed_step_attribution as v66_builder  # noqa: E402',
        'import build_winner_v67_backtracked_adam_step as v67_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v67_failed_step_attribution_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v67_backtracked_adam_step_contract.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"',
        '''V45_RESULT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"
V66_RESULT = ANALYSIS / "winner_v66_failed_step_attribution_result.json"''',
    )
    source = replace_region(
        source, "def validate_preregistration", "def validate_artifact", VALIDATE_PREREGISTRATION
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--failed-step-attribution-authorized", action="store_true")',
        '    parser.add_argument("--backtracked-adam-step-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.failed_step_attribution_authorized:",
        "if not args.offline_cpu_only or not args.backtracked_adam_step_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v67 requires --offline-cpu-only --failed-step-attribution-authorized"',
        '"Winner-v67 requires --offline-cpu-only --backtracked-adam-step-authorized"',
    )
    source = replace_exact(
        source,
        '    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))\n    validate_preregistration(preregistration)\n',
        '''    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
''' + ATTRIBUTION_EVIDENCE,
    )
    source = replace_region(
        source,
        "        raw_after, proposed_optimizer = training.adam_step(",
        "        deltas = v20.leaf_max_abs_delta(before, after)",
        STEP_BLOCK + "\n",
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v67_backtracked_adam_step_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v67 contract: {path}")
    attribution = json.loads(V66_RESULT.read_text(encoding="utf-8"))
    v66_contract = json.loads(V66_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    inherited = attribution.get("loss_geometry", {}).get(
        "inherited_adam_fraction_rows", []
    )
    descending = [row for row in inherited if row["loss"] < EXPECTED_LOSS_BEFORE]
    if (
        sha256(V66_RESULT) != V66_RESULT_SHA256
        or attribution.get("status") != "PASS_WINNER_V66_FAILED_STEP_ATTRIBUTION"
        or attribution.get("classification") != "INHERITED_ADAM_FULL_STEP_OVERSHOOT"
        or attribution.get("decision")
        != "PREREGISTER_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP_PROOF"
        or attribution.get("loss_geometry", {}).get("teacher_loss_before")
        != EXPECTED_LOSS_BEFORE
        or next(row for row in inherited if row["fraction"] == 0.25)["loss"]
        != EXPECTED_LOSS_AFTER
        or [row["fraction"] for row in descending] != [0.0625, 0.125, 0.25]
        or source.count("v67_builder.select_first_descent") != 1
    ):
        raise ValueError("Winner-v67 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v67_backtracked_adam_step.py"),
            "runner": Path("tools/run_winner_v67_backtracked_adam_step.py"),
            "tests": Path("tests/test_winner_v67_backtracked_adam_step.py"),
            "v66_result": Path(
                "outputs/analysis/winner_v66_failed_step_attribution_result.json"
            ),
            "v66_contract": Path(
                "outputs/analysis/winner_v66_failed_step_attribution_preregistration.json"
            ),
            "v66_builder": Path(
                "tools/build_winner_v66_failed_step_attribution.py"
            ),
            "v65b_stopped_result": Path(
                "outputs/analysis/winner_v65b_isolated_persistent_teacher_training_result.json"
            ),
        }.items()
    }
    value = {
        "schema_version": "winner_v67.backtracked_adam_step_contract.v1",
        "status": "PREREGISTERED_WINNER_V67_BACKTRACKED_ADAM_STEP",
        "decision": "AUTHORIZE_EXACTLY_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP",
        "source_checkpoint": v66_contract["source_checkpoint"],
        "teacher_checkpoint": v66_contract["teacher_checkpoint"],
        "step": {
            "source_optimizer_count": SOURCE_COUNT,
            "rollout_update_index": SOURCE_COUNT,
            "completed_optimizer_count": COMPLETED_COUNT,
            "fractions_largest_first": list(FRACTIONS),
            "acceptance_rule": "first fraction with strict same-batch teacher-loss descent",
            "expected_accepted_fraction": EXPECTED_ACCEPTED_FRACTION,
            "expected_loss_before": EXPECTED_LOSS_BEFORE,
            "expected_loss_after": EXPECTED_LOSS_AFTER,
            "optimizer_moments": "advance once from the exact full Adam proposal",
            "parameter_delta": "scale the clamped full-Adam parameter delta by the accepted fraction",
        },
        "objective": {
            "update_gradient": "full_action_persistent_teacher_only",
            "persistent_teacher_scale": 136.35153198242188,
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "stop_rules": [
            "stop if the V66 result or exact count-574 source differs",
            "stop unless the full step fails and the first strict descent is exactly one quarter",
            "stop unless optimizer count advances exactly 574 to 575",
            "stop on any snapshot or ONNX round-trip mismatch",
            "do not continue training or inspect support behavior",
        ],
        "authority": {
            "pass_authorizes_only": (
                "preregistration of a bounded deterministic backtracked-Adam continuation"
            ),
            "continuation_authorized_now": False,
            "support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "base": "Winner-v66 exact failed-step attribution runner",
            "transformed_source_sha256": transformed_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v67 backtracked-Adam step contract",
                "",
                "- Source / completed optimizer counts: `574 / 575`",
                "- Fractions, largest first: `1, 1/2, 1/4, 1/8, 1/16`",
                "- Acceptance: first strict same-batch loss descent",
                "- Frozen expected accepted fraction: `1/4`",
                "- Updates / snapshots / ONNX after pass: `1 / 1 / 1`",
                "- Continuation / support / deployment / robot authorized now: `false / false / false / false`",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
