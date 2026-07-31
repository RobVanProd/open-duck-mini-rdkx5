#!/usr/bin/env python3
"""Freeze the sole integrated first-tick-teacher continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v58_integrated_first_tick_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V58_INTEGRATED_FIRST_TICK_TRAINING_PREREGISTRATION_20260722.md"
V52_PREREG = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"
V57_RESULT = ANALYSIS / "winner_v57_first_tick_teacher_one_update_result.json"
V57_RESULT_SHA256 = "66c075dd291a016f4ed07d6486516faf61bfc44ab2d5caeb1c1480ccb63351d2"

CUSTOM_SOURCES = {
    "v58_builder": Path("tools/build_winner_v58_integrated_first_tick_training_preregistration.py"),
    "v58_runner": Path("tools/run_winner_v58_integrated_first_tick_training.py"),
    "v58_tests": Path("tests/test_winner_v58_integrated_first_tick_training.py"),
    "v57_result": Path("outputs/analysis/winner_v57_first_tick_teacher_one_update_result.json"),
    "v56_mechanism": Path("patches/winner_v56_first_tick_teacher_mapping.py"),
    "v52_transform_builder": Path("tools/build_winner_v52_full_action_teacher_training_preregistration.py"),
    "v46_base_runner": Path("tools/run_winner_v46_static_target_teacher_training.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
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
    import build_winner_v52_full_action_teacher_training_preregistration as v52

    source, _ = v52.transformed_source()
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v58 transform count changed: expected {count}, found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )

    replace(
        '"""Run the one frozen 100-update Winner-v52 full-action-teacher CPU arm."""',
        '"""Run the one frozen 100-update Winner-v58 integrated first-tick-teacher CPU arm."""',
    )
    replace(
        "import winner_v49_full_action_static_target_teacher as v49  # noqa: E402",
        "import winner_v49_full_action_static_target_teacher as v49  # noqa: E402\nimport winner_v56_first_tick_teacher_mapping as v56  # noqa: E402",
    )
    replace(
        '"winner_v52_full_action_teacher_training_preregistration.json"',
        '"winner_v58_integrated_first_tick_training_preregistration.json"',
    )
    replace(
        '"winner_v51b_full_action_teacher_one_update_cpu_result.json"',
        '"winner_v57_first_tick_teacher_one_update_result.json"',
    )
    replace("SOURCE_COMPLETED_UPDATES = 353", "SOURCE_COMPLETED_UPDATES = 454")
    replace("HALF_COMPLETED_UPDATES = 403", "HALF_COMPLETED_UPDATES = 504")
    replace("FINAL_COMPLETED_UPDATES = 453", "FINAL_COMPLETED_UPDATES = 554")
    replace(
        '"winner_v52.full_action_teacher_training_preregistration.v1"',
        '"winner_v58.integrated_first_tick_training_preregistration.v1"',
    )
    replace(
        '"PREREGISTERED_WINNER_V52_FULL_ACTION_TEACHER_TRAINING"',
        '"PREREGISTERED_WINNER_V58_INTEGRATED_FIRST_TICK_TEACHER_TRAINING"',
    )
    replace(
        '"AUTHORIZE_ONE_100_UPDATE_FULL_ACTION_TEACHER_ARM_ONLY"',
        '"AUTHORIZE_ONE_100_UPDATE_INTEGRATED_FIRST_TICK_TEACHER_ARM_ONLY"',
    )
    replace(
        '        raise ValueError("Winner-v46 teacher objective changed")',
        '''        raise ValueError("Winner-v46 teacher objective changed")
    reset = value.get("objective", {}).get("first_tick_teacher", {})
    if (
        reset.get("configuration_ids") != list(TRAINING_TEACHER_IDS)
        or reset.get("heldout_ids_excluded") != list(HELDOUT_TEACHER_IDS)
        or reset.get("raw_rows") != 22
        or reset.get("native_quantized_rows") != 22
        or reset.get("selected_elements") != 616
        or reset.get("scale") != float(v56.RESET_TEACHER_SCALE)
        or reset.get("coefficient_search") is not False
        or reset.get("flat_transport_or_attention_added") is not False
    ):
        raise ValueError("Winner-v58 first-tick objective changed")''',
    )

    start = source.index("def validate_source_snapshot(")
    end = source.index("\ndef graph_receipt(", start)
    old_function = source[start:end]
    new_function = '''def validate_source_snapshot(snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v58 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "first_tick_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 453
        or metadata.get("source_snapshot_sha256") != source_result["source"]["snapshot_sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("first_tick_teacher_scale") != float(v56.RESET_TEACHER_SCALE)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("continuation_training_updates") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"])) != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v58 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v58 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v58 source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v58 source snapshot contains nonfinite arrays")

'''
    source = source[:start] + new_function + source[end + 1 :]
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old_function.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new_function.encode()).hexdigest(),
            "replacement_count": 1,
        }
    )

    replace(
        "import run_winner_v12_calibrator_cpu_smoke as smoke",
        "import run_winner_v12_calibrator_cpu_smoke as smoke\n    import run_winner_v12_calibrator_support_gate as base_gate",
    )
    replace(
        "full_action_teacher_training_authorized",
        "integrated_first_tick_teacher_training_authorized",
        1,
    )
    replace(
        "--full-action-teacher-training-authorized",
        "--integrated-first-tick-teacher-training-authorized",
        2,
    )
    replace(
        'source_result.get("status") != "PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"',
        'source_result.get("status") != "PASS_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"',
    )
    replace(
        'source_result.get("decision") != "AUTHORIZE_BOUNDED_FULL_ACTION_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"',
        'source_result.get("decision") != "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"',
    )
    reset_batch = '''    domain_matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    reset_configurations = (
        domain_matrix["fixed_anchors"]
        + domain_matrix["discovery_samples"]
        + domain_matrix["heldout_samples"]
    )
    reset_by_id = {row["id"]: row for row in reset_configurations}
    reset_observations = []
    reset_targets = []
    reset_variants = []
    for configuration_id in TRAINING_TEACHER_IDS:
        reset_target = smoke.bounded_action_numpy(
            np.asarray(table[configuration_id], dtype=np.float32),
            np.zeros((14,), dtype=np.float32),
        )
        for plant in smoke.PLANTS:
            reset_episode = smoke.Episode(
                mujoco, scene, reset_by_id[configuration_id], plant, design,
                observer_type, args.canonical_fit,
            )
            reset_raw = base_gate.ObservationTransport(None, None).observe(
                reset_episode.observation()
            )
            reset_quantized = base_gate.native_quantize_observation(reset_raw)
            for reset_variant, reset_observation in enumerate((reset_raw, reset_quantized)):
                reset_observations.append(reset_observation)
                reset_targets.append(reset_target)
                reset_variants.append(reset_variant)
    reset_batch = {
        "observations": jnp.asarray(np.asarray(reset_observations, dtype=np.float32)),
        "targets": jnp.asarray(np.asarray(reset_targets, dtype=np.float32)),
        "variant": jnp.asarray(np.asarray(reset_variants, dtype=np.int32)),
    }
    if (
        reset_batch["observations"].shape != (44, 115)
        or reset_batch["targets"].shape != (44, 14)
        or reset_batch["variant"].shape != (44,)
    ):
        raise ValueError("Winner-v58 reset batch changed")
'''
    replace(
        "    observer_type = smoke.load_runtime_observer(args.canonical_fit)\n    metrics: list[dict[str, Any]] = []",
        "    observer_type = smoke.load_runtime_observer(args.canonical_fit)\n" + reset_batch + "    metrics: list[dict[str, Any]] = []",
    )
    replace(
        '''    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, data, target_mean, target_std)

    ppo_grad = jax.value_and_grad(ppo_objective, has_aux=True)
    predictor_grad = jax.value_and_grad(predictor_objective, has_aux=True)''',
        '''    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, data, target_mean, target_std)

    def reset_objective(values_tree: Mapping[str, Any]):
        return v56.first_tick_teacher_loss(values_tree, reset_batch)

    ppo_grad = jax.value_and_grad(ppo_objective, has_aux=True)
    predictor_grad = jax.value_and_grad(predictor_objective, has_aux=True)
    reset_grad = jax.value_and_grad(reset_objective, has_aux=True)''',
    )
    replace(
        "        (teacher_loss, teacher_metrics), teacher_gradients = jax.value_and_grad(static_teacher_objective, has_aux=True)(before)",
        "        (teacher_loss, teacher_metrics), teacher_gradients = jax.value_and_grad(static_teacher_objective, has_aux=True)(before)\n        (reset_loss, reset_metrics), reset_gradients = reset_grad(before)",
    )
    replace(
        '''        gradients = v29.compose_gradients(
            baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=True
        )''',
        '''        full_horizon_gradients = v29.compose_gradients(
            baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=True
        )
        gradients = v29.compose_gradients(
            full_horizon_gradients, reset_gradients, v56.RESET_TEACHER_SCALE, enabled=True
        )''',
    )
    replace(
        "            + jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss\n        )",
        "            + jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss\n            + jnp.asarray(v56.RESET_TEACHER_SCALE, dtype=jnp.float32) * reset_loss\n        )",
    )
    replace(
        "        teacher_gradient_max = common.tree_max_abs(teacher_gradients)\n        anchor_gradient_max = common.tree_max_abs(anchor_gradients)",
        "        teacher_gradient_max = common.tree_max_abs(teacher_gradients)\n        anchor_gradient_max = common.tree_max_abs(anchor_gradients)\n        reset_gradient_max = common.tree_max_abs(reset_gradients)",
    )
    replace(
        "            or not all(teacher_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)\n        ):",
        '''            or not all(teacher_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            or int(reset_metrics["sample_count"]) != 44
            or int(reset_metrics["selected_elements"]) != 616
            or sorted(key for key, value in reset_gradient_max.items() if value > 0.0)
            != ["action_bias", "action_weight", "hidden_bias", "obs_weight"]
            or any(
                reset_gradient_max[key] != 0.0
                for key in reset_gradient_max
                if key not in {"action_bias", "action_weight", "hidden_bias", "obs_weight"}
            )
        ):''',
    )
    replace(
        '            "teacher_loss": teacher_loss, "teacher_metrics": teacher_metrics,\n            "combined_loss": combined_loss, "gradients": gradients,',
        '            "teacher_loss": teacher_loss, "teacher_metrics": teacher_metrics,\n            "reset_loss": reset_loss, "reset_metrics": reset_metrics,\n            "combined_loss": combined_loss, "gradients": gradients,',
    )
    replace(
        '            "full_action_teacher_loss": float(teacher_loss),',
        '''            "full_action_teacher_loss": float(teacher_loss),
            "first_tick_teacher_loss": float(reset_loss),
            "first_tick_raw_mse": float(reset_metrics["raw_reset_mse"]),
            "first_tick_quantized_mse": float(reset_metrics["quantized_reset_mse"]),
            "first_tick_pitch_rms": float(reset_metrics["pitch_rms"]),
            "first_tick_nonpitch_rms": float(reset_metrics["nonpitch_rms"]),
            "selected_reset_elements": int(reset_metrics["selected_elements"]),
            "reset_gradient_max_abs": reset_gradient_max,''',
    )
    replace(
        'f"snapshot_full_action_teacher_update_{completed_updates:03d}.npz"',
        'f"snapshot_integrated_first_tick_teacher_update_{completed_updates:03d}.npz"',
    )
    replace(
        '"stage": "full_action_static_target_teacher_joint_stage2"',
        '"stage": "integrated_first_tick_teacher_joint_stage2"',
    )
    replace(
        '                "full_action_teacher_scale": float(FROZEN_TEACHER_SCALE),',
        '                "full_action_teacher_scale": float(FROZEN_TEACHER_SCALE),\n                "first_tick_teacher_scale": float(v56.RESET_TEACHER_SCALE),',
    )
    replace(
        'loaded["metadata"].get("stage") == "full_action_static_target_teacher_joint_stage2"',
        'loaded["metadata"].get("stage") == "integrated_first_tick_teacher_joint_stage2"',
    )
    replace('f"winner_v52_{label}.onnx"', 'f"winner_v58_{label}.onnx"')
    replace("list(range(354, 454))", "list(range(455, 555))")
    replace(
        '''        "all_100_prefix_anchor_contracts_exact": all(
            row["selected_anchor_elements"] == v29.EXPECTED_ANCHOR_ELEMENTS
            and all(row["anchor_gradient_max_abs"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            and all(row["anchor_gradient_max_abs"][key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            for row in metrics
        ),''',
        '''        "all_100_prefix_anchor_contracts_exact": all(
            row["selected_anchor_elements"] == v29.EXPECTED_ANCHOR_ELEMENTS
            and all(row["anchor_gradient_max_abs"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            and all(row["anchor_gradient_max_abs"][key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            for row in metrics
        ),
        "all_100_first_tick_teacher_contracts_exact": all(
            row["selected_reset_elements"] == 616
            and row["first_tick_teacher_loss"] >= 0.0
            and row["first_tick_raw_mse"] >= 0.0
            and row["first_tick_quantized_mse"] >= 0.0
            and sorted(key for key, value in row["reset_gradient_max_abs"].items() if value > 0.0)
            == ["action_bias", "action_weight", "hidden_bias", "obs_weight"]
            for row in metrics
        ),''',
    )
    replace('"optimizer_count_453_exact"', '"optimizer_count_554_exact"')
    replace(
        '== [("half", 403), ("final", 453)]',
        '== [("half", 504), ("final", 554)]',
    )
    replace(
        '"winner_v52.full_action_teacher_training_result.v1"',
        '"winner_v58.integrated_first_tick_teacher_training_result.v1"',
    )
    replace(
        '"PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"',
        '"PASS_WINNER_V58_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"',
    )
    replace(
        '"HOLD_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"',
        '"HOLD_WINNER_V58_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"',
    )
    replace(
        '"AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
        '"AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
    )
    replace('"DO_NOT_EVALUATE_WINNER_V52_POLICY"', '"DO_NOT_EVALUATE_WINNER_V58_POLICY"')
    replace(
        '"completed_updates": 353, "optimizer_count": 353',
        '"completed_updates": 454, "optimizer_count": 454',
    )
    replace('"completed_updates": 353,', '"completed_updates": 454,')
    replace('"v51b_result_lf_sha256"', '"v57_result_lf_sha256"')
    replace(
        '"a separate frozen full-action-teacher support gate preregistration"',
        '"a separate frozen integrated first-tick-teacher support gate preregistration"',
    )
    replace(
        '"source_snapshot_graph_and_optimizer_count_252_exact"',
        '"source_snapshot_graph_and_optimizer_count_454_exact"',
    )
    replace(
        'int(np.asarray(optimizer["count"])) == 453',
        'int(np.asarray(optimizer["count"])) == FINAL_COMPLETED_UPDATES',
    )
    replace("Winner-v46", "Winner-v58", 23)
    compile(source, "winner_v58_transformed_training.py", "exec")
    return source, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v58 preregistration: {path}")
    old = json.loads(V52_PREREG.read_text(encoding="utf-8"))
    source_result = json.loads(V57_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V57_RESULT) != V57_RESULT_SHA256
        or source_result.get("status")
        != "PASS_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"
        or source_result.get("decision")
        != "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"
        or source_result.get("execution", {}).get("optimizer_updates") != 1
    ):
        raise ValueError("Winner-v58 source authority changed")
    transformed, receipts = transformed_source()
    sources = dict(old["sources"])
    for name, path in CUSTOM_SOURCES.items():
        sources[name] = {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
    objective = dict(old["objective"])
    objective["first_tick_teacher"] = {
        "configuration_ids": old["objective"]["full_action_static_target_teacher"][
            "configuration_ids"
        ],
        "heldout_ids_excluded": old["objective"]["full_action_static_target_teacher"][
            "heldout_ids_excluded"
        ],
        "raw_rows": 22,
        "native_quantized_rows": 22,
        "selected_elements": 616,
        "scale": 136.35153198242188,
        "coefficient_search": False,
        "action_replacement": False,
        "actor_input_added": False,
        "flat_transport_or_attention_added": False,
    }
    value = {
        "schema_version": "winner_v58.integrated_first_tick_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V58_INTEGRATED_FIRST_TICK_TEACHER_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_INTEGRATED_FIRST_TICK_TEACHER_ARM_ONLY",
        "causal_hypothesis": (
            "The first graph tick is causal to eight V55 failures, its reset labels "
            "remain separable after native quantization, and V57 proves its exact "
            "loss/optimizer/export path. Adding that reset term to the unchanged "
            "V52 objectives can repair the critical mapping without changing ABI."
        ),
        "source_checkpoint": {
            "completed_updates": 454,
            "optimizer_count": 454,
            "snapshot": source_result["snapshot"],
            "graph": source_result["graph"],
        },
        "teacher_checkpoint": old["teacher_checkpoint"],
        "frozen_training": {
            **old["frozen_training"],
            "source_completed_updates": 454,
            "source_optimizer_count": 454,
            "final_optimizer_count": 554,
            "persistent_checkpoints": {"half": 504, "final": 554},
            "first_tick_teacher_scale": 136.35153198242188,
        },
        "objective": objective,
        "post_training_selection": {
            "checkpoint_selection_during_training": False,
            "half_and_final_both_required_for_future_support_gate": True,
            "closest_or_reward_selection_forbidden": True,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "transformation": {
            "base_v52_transformed_source_sha256": old["transformation"][
                "transformed_source_sha256"
            ],
            "transformed_source_sha256": hashlib.sha256(transformed.encode()).hexdigest(),
            "replacements": receipts,
            "replacement_groups": len(receipts),
        },
        "stop_rules": {
            "stop_on_nonfinite": True,
            "stop_on_source_mask_boundary_or_restore_mismatch": True,
            "stop_on_first_tick_gradient_locality_change": True,
            "no_retry_or_coefficient_search": True,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separately preregistered unchanged half/final support gate",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v58 integrated first-tick training preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source / half / final: `454 / 504 / 554`",
                "- Training: `100 x 80 x 250` CPU scheduled ticks",
                "- First-tick rows / elements / scale: `44 / 616 / 136.35153198242188`",
                "- Attention / flat transport / ABI changes: `0 / 0 / 0`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
