#!/usr/bin/env python3
"""Preregister one fresh-moment safeguarded teacher step."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v70_fresh_moment_step_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V70_FRESH_MOMENT_STEP_CONTRACT_20260722.md"
V69_RESULT = ANALYSIS / "winner_v69_count602_direction_attribution_result.json"
V69_CONTRACT = ANALYSIS / "winner_v69_count602_direction_attribution_preregistration.json"
V69_RESULT_SHA256 = "cd1c25f0adf89597297a8fa5a52cd1a03a9da5e4743ad92a32fbaa23caf85b75"
SOURCE_COUNT = 601
COMPLETED_COUNT = 602
FRACTIONS = (
    1.0,
    0.5,
    0.25,
    0.125,
    0.0625,
    0.03125,
    0.015625,
    0.0078125,
    0.00390625,
    0.001953125,
    0.0009765625,
)

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v69_count602_direction_attribution as v69  # noqa: E402


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
            f"Winner-v70 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v70 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def select_first_descent(
    rows: Sequence[Mapping[str, float]], loss_before: float
) -> Mapping[str, float] | None:
    for expected, row in zip(FRACTIONS, rows, strict=True):
        if float(row["fraction"]) != expected:
            raise ValueError("Winner-v70 safeguard order changed")
        if float(row["loss"]) < loss_before:
            return row
    return None


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v70.fresh_moment_step_contract.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V70_FRESH_MOMENT_STEP"
        or value.get("decision") != "AUTHORIZE_EXACTLY_ONE_FRESH_MOMENT_TEACHER_STEP"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("step", {}).get("source_optimizer_count") != SOURCE_COMPLETED_UPDATES
        or value.get("step", {}).get("completed_optimizer_count") != 602
        or value.get("step", {}).get("fractions_largest_first")
        != [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625, 0.001953125, 0.0009765625]
    ):
        raise ValueError("Winner-v70 preregistration changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v70 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v70 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v70 source manifest changed")


'''

ATTRIBUTION_EVIDENCE = '''    attribution = json.loads(V69_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V69_RESULT)
        != "cd1c25f0adf89597297a8fa5a52cd1a03a9da5e4743ad92a32fbaa23caf85b75"
        or attribution.get("status")
        != "PASS_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION"
        or attribution.get("classification")
        != "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER"
        or attribution.get("decision")
        != "PREREGISTER_ONE_FRESH_MOMENT_TEACHER_STEP_PROOF"
        or attribution.get("failed_checks") != []
    ):
        raise ValueError("Winner-v70 attribution evidence changed")
'''

STEP_BLOCK = '''        reset_keys = tuple(sorted(v29.ANCHOR_GRADIENT_KEYS))
        fresh_m = {
            key: jnp.zeros_like(value) if key in reset_keys else jnp.asarray(value)
            for key, value in optimizer["m"].items()
        }
        fresh_v = {
            key: jnp.zeros_like(value) if key in reset_keys else jnp.asarray(value)
            for key, value in optimizer["v"].items()
        }
        fresh_optimizer = {
            "count": jnp.asarray(optimizer["count"]),
            "m": fresh_m,
            "v": fresh_v,
        }
        reset_exact = all(
            np.count_nonzero(np.asarray(fresh_m[key])) == 0
            and np.count_nonzero(np.asarray(fresh_v[key])) == 0
            for key in reset_keys
        )
        preserved_exact = all(
            np.array_equal(np.asarray(fresh_m[key]), np.asarray(optimizer["m"][key]))
            and np.array_equal(np.asarray(fresh_v[key]), np.asarray(optimizer["v"][key]))
            for key in optimizer["m"] if key not in reset_keys
        )
        raw_after, optimizer_after = training.adam_step(
            before, gradients, fresh_optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        full_after = training.clamp_stage2_parameters(raw_after)
        full.validate_log_std(full_after)
        full_loss, _ = static_teacher_objective(full_after)
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
            loss, _ = static_teacher_objective(trial)
            rows.append({
                "fraction": float(fraction),
                "loss": float(loss),
                "loss_delta": float(loss) - float(teacher_loss),
            })
            trials.append(trial)
        accepted_row = v70_builder.select_first_descent(rows, float(teacher_loss))
        if accepted_row is None:
            raise ValueError("Winner-v70 fresh-moment safeguard found no strict descent")
        accepted_index = next(index for index, row in enumerate(rows) if row is accepted_row)
        accepted = trials[accepted_index]
        accepted_fraction = float(accepted_row["fraction"])
        accepted_loss, accepted_metrics = static_teacher_objective(accepted)
        parameters_after = v21.merge_joint_trainable(parameters, accepted)
        deltas = v20.leaf_max_abs_delta(before, accepted)
        snapshot_path = args.work_root / "snapshots" / "snapshot_fresh_moment_update_602.npz"
        snapshot_receipt = v22v2.save_snapshot(
            snapshot_path,
            parameters_after,
            optimizer_after,
            {
                "stage": "fresh_moment_persistent_teacher_joint_stage2",
                "completed_updates": 602,
                "source_completed_updates": 601,
                "source_snapshot_sha256": source_receipt["sha256"],
                "teacher_snapshot_sha256": teacher_receipt["sha256"],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "reset_moment_keys": list(reset_keys),
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
            and loaded["metadata"].get("stage")
            == "fresh_moment_persistent_teacher_joint_stage2"
            and loaded["metadata"].get("completed_updates") == 602
            and loaded["metadata"].get("reset_moment_keys") == list(reset_keys)
        )
        graph = graph_receipt(
            smoke=smoke,
            networks=networks,
            training=training,
            parameters=parameters_after,
            observations=observations,
            path=args.work_root / "graphs" / "winner_v70_fresh_moment_update_602.onnx",
            label="proof",
            completed_updates=602,
        )
        checks = {
            "v69_attribution_and_count_601_source_exact": True,
            "exact_six_teacher_active_moment_keys_reset": len(reset_keys) == 6 and reset_exact,
            "all_other_optimizer_moments_bit_exact_before_step": preserved_exact,
            "largest_first_fraction_order_exact": [row["fraction"] for row in rows]
            == preregistration["step"]["fractions_largest_first"],
            "first_accepted_fraction_strictly_descends": float(accepted_loss) < float(teacher_loss),
            "optimizer_count_601_to_602_exact": int(np.asarray(optimizer_after["count"])) == 602,
            "all_six_policy_leaves_changed": all(
                deltas[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
            ),
            "all_parameters_optimizer_losses_metrics_finite": training.finite_tree({
                "parameters": parameters_after,
                "optimizer": optimizer_after,
                "teacher_loss": teacher_loss,
                "full_loss": full_loss,
                "accepted_loss": accepted_loss,
                "accepted_metrics": accepted_metrics,
                "rows": rows,
            }),
            "snapshot_readback_exact": snapshot_exact,
            "onnx_abi_exact": graph["contract"]["abi_exact"],
            "onnx_training_only_tensors_absent": graph["contract"]["training_only_tensors_absent"],
            "onnx_jax_chain_at_most_1e_7": graph["contract"]["jax_onnx_at_most_1e_7"],
            "onnx_previous_action_chain_exact": graph["contract"]["previous_action_out_equals_action_bit_exact"],
            "formal_support_continuation_robot_zero": True,
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        if failed_checks:
            raise ValueError(f"Winner-v70 proof invalid: {failed_checks}")
        result = {
            "schema_version": "winner_v70.fresh_moment_step_result.v1",
            "status": "PASS_WINNER_V70_FRESH_MOMENT_STEP",
            "decision": "PREREGISTER_BOUNDED_FRESH_MOMENT_SAFEGUARDED_CONTINUATION_ONLY",
            "source": {
                "snapshot": source_receipt,
                "optimizer_count": 601,
                "rollout_update_index": rollout_update_index,
                "episode_receipts_sha256": episode_hash,
            },
            "optimization": {
                "optimizer_count_before": 601,
                "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
                "reset_moment_keys": list(reset_keys),
                "loss_before": float(teacher_loss),
                "fresh_full_step_loss": float(full_loss),
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
    source, _ = v69.transformed_source()
    source = replace_exact(source, "Winner-v69", "Winner-v70", count=29)
    source = replace_exact(source, "winner_v69", "winner_v70", count=6)
    source = replace_exact(source, "WINNER_V69", "WINNER_V70", count=6)
    source = replace_exact(
        source,
        'import build_winner_v70_count602_direction_attribution as v69_builder  # noqa: E402',
        'import build_winner_v70_fresh_moment_step as v70_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v70_count602_direction_attribution_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v70_fresh_moment_step_contract.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v68_backtracked_adam_continuation_result.json"',
        '''V45_RESULT = ANALYSIS / "winner_v68_backtracked_adam_continuation_result.json"
V69_RESULT = ANALYSIS / "winner_v69_count602_direction_attribution_result.json"''',
    )
    source = replace_region(
        source, "def validate_preregistration", "def validate_artifact", VALIDATE_PREREGISTRATION
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--count602-attribution-authorized", action="store_true")',
        '    parser.add_argument("--fresh-moment-step-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.count602_attribution_authorized:",
        "if not args.offline_cpu_only or not args.fresh_moment_step_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v70 requires --offline-cpu-only --count602-attribution-authorized"',
        '"Winner-v70 requires --offline-cpu-only --fresh-moment-step-authorized"',
    )
    source = replace_exact(
        source,
        '    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))\n    validate_preregistration(preregistration)\n',
        '''    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
''' + ATTRIBUTION_EVIDENCE,
    )
    source = replace_exact(
        source,
        '!= "PREREGISTER_WINNER_V70_COUNT_602_DIRECTION_ATTRIBUTION_ONLY"',
        '!= "PREREGISTER_WINNER_V69_COUNT_602_DIRECTION_ATTRIBUTION_ONLY"',
    )
    source = replace_region(
        source,
        "        raw_after, proposed_optimizer = training.adam_step(",
        "        deltas = v20.leaf_max_abs_delta(before, after)",
        STEP_BLOCK + "\n",
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v70_fresh_moment_step_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v70 contract: {path}")
    attribution = json.loads(V69_RESULT.read_text(encoding="utf-8"))
    v69_contract = json.loads(V69_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    if (
        sha256(V69_RESULT) != V69_RESULT_SHA256
        or attribution.get("status") != "PASS_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION"
        or attribution.get("classification")
        != "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER"
        or attribution.get("decision")
        != "PREREGISTER_ONE_FRESH_MOMENT_TEACHER_STEP_PROOF"
        or source.count("v70_builder.select_first_descent") != 1
    ):
        raise ValueError("Winner-v70 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v70_fresh_moment_step.py"),
            "runner": Path("tools/run_winner_v70_fresh_moment_step.py"),
            "tests": Path("tests/test_winner_v70_fresh_moment_step.py"),
            "v69_result": Path(
                "outputs/analysis/winner_v69_count602_direction_attribution_result.json"
            ),
            "v69_contract": Path(
                "outputs/analysis/winner_v69_count602_direction_attribution_preregistration.json"
            ),
            "v69_builder": Path(
                "tools/build_winner_v69_count602_direction_attribution.py"
            ),
            "v68_stopped_result": Path(
                "outputs/analysis/winner_v68_backtracked_adam_continuation_result.json"
            ),
        }.items()
    }
    value = {
        "schema_version": "winner_v70.fresh_moment_step_contract.v1",
        "status": "PREREGISTERED_WINNER_V70_FRESH_MOMENT_STEP",
        "decision": "AUTHORIZE_EXACTLY_ONE_FRESH_MOMENT_TEACHER_STEP",
        "source_checkpoint": v69_contract["source_checkpoint"],
        "teacher_checkpoint": v69_contract["teacher_checkpoint"],
        "step": {
            "source_optimizer_count": SOURCE_COUNT,
            "rollout_update_index": SOURCE_COUNT,
            "completed_optimizer_count": COMPLETED_COUNT,
            "reset_moments": "m and v only for the six teacher-active policy leaves",
            "preserve": "global optimizer count and all non-teacher-active moments",
            "fractions_largest_first": list(FRACTIONS),
            "acceptance_rule": "first strict same-batch teacher-loss descent",
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
        "authority": {
            "pass_authorizes_only": (
                "preregistration of a bounded fresh-moment safeguarded continuation"
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
            "base": "Winner-v69 exact count-602 attribution runner",
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
                "# Winner-v70 fresh-moment step contract",
                "",
                "- Source / completed counts: `601 / 602`",
                "- Reset: Adam `m/v` for exactly six teacher-active policy leaves",
                "- Preserve: optimizer count and every other moment",
                "- Safeguard: largest-first powers of two through `1/1024`",
                "- Committed update / snapshot / ONNX after pass: `1 / 1 / 1`",
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
