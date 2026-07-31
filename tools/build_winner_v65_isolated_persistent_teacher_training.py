#!/usr/bin/env python3
"""Preregister the bounded Winner-v65 isolated-teacher continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v65_isolated_persistent_teacher_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING_PREREGISTRATION_20260722.md"
V64B_RESULT = ANALYSIS / "winner_v64b_isolated_persistent_teacher_step_result.json"
V64B_CONTRACT = ANALYSIS / "winner_v64b_preregistration_name_correction.json"
V60_RESULT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_result.json"
V64B_RESULT_SHA256 = "03e83022dd4f081d4f7258ee22e9260f305347b17a9a437dc76c1a90ca896800"

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v60_integrated_numeric_guard_training_preregistration as v60  # noqa: E402


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


def replace_exact(
    source: str,
    old: str,
    new: str,
    receipts: list[dict[str, Any]],
    *,
    count: int = 1,
) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v65 transform count changed: expected {count}, found {actual}: {old!r}"
        )
    receipts.append(
        {
            "kind": "exact",
            "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
            "replacement_count": count,
        }
    )
    return source.replace(old, new)


def replace_region(
    source: str,
    start: str,
    end: str,
    replacement: str,
    receipts: list[dict[str, Any]],
) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v65 region marker changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    old = source[left:right]
    receipts.append(
        {
            "kind": "region",
            "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(replacement.encode()).hexdigest(),
            "replacement_count": 1,
        }
    )
    return source[:left] + replacement + source[right:]


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v65.isolated_persistent_teacher_training_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING"
        or value.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_ISOLATED_PERSISTENT_TEACHER_ARM_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v65 preregistration identity changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or frozen.get("source_optimizer_count") != SOURCE_COMPLETED_UPDATES
        or frozen.get("continuation_optimizer_updates") != UPDATES
        or frozen.get("final_optimizer_count") != FINAL_COMPLETED_UPDATES
        or frozen.get("environments_per_update") != 80
        or frozen.get("ticks_per_environment") != 250
        or frozen.get("persistent_checkpoints")
        != {"half": HALF_COMPLETED_UPDATES, "final": FINAL_COMPLETED_UPDATES}
        or value.get("objective", {}).get("update_gradient")
        != "full_action_persistent_teacher_only"
        or value.get("objective", {}).get("persistent_teacher", {}).get("scale")
        != float(FROZEN_TEACHER_SCALE)
    ):
        raise ValueError("Winner-v65 frozen training changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v65 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v65 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v65 source manifest changed")


'''

VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v65 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "isolated_persistent_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 554
        or metadata.get("source_snapshot_sha256")
        != source_result["source"]["snapshot_sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("persistent_teacher_scale") != float(FROZEN_TEACHER_SCALE)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("continuation_training_updates") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v65 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v65 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v65 source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v65 source snapshot contains nonfinite arrays")

'''

SOURCE_EVIDENCE = '''    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status")
        != "PASS_WINNER_V64B_ISOLATED_PERSISTENT_TEACHER_STEP"
        or source_result.get("decision")
        != "PREREGISTER_BOUNDED_ISOLATED_PERSISTENT_TEACHER_CONTINUATION_ONLY"
        or source_result.get("failed_checks") != []
        or source_result.get("execution", {}).get("optimizer_updates") != 1
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v65 source evidence changed")
'''


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    source, _ = v60.transformed_source()
    receipts: list[dict[str, Any]] = []
    for old, new in (
        ("Winner-v60", "Winner-v65"),
        ("winner_v60", "winner_v65"),
        ("WINNER_V60", "WINNER_V65"),
        ("integrated-first-tick-teacher", "isolated-persistent-teacher"),
        ("integrated_first_tick_teacher", "isolated_persistent_teacher"),
        ("integrated first-tick-teacher", "isolated persistent-teacher"),
    ):
        count = source.count(old)
        if count:
            source = replace_exact(source, old, new, receipts, count=count)
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v57_first_tick_teacher_one_update_result.json"',
        'V45_RESULT = ANALYSIS / "winner_v64b_isolated_persistent_teacher_step_result.json"',
        receipts,
    )
    source = replace_exact(source, "SOURCE_COMPLETED_UPDATES = 454", "SOURCE_COMPLETED_UPDATES = 555", receipts)
    source = replace_exact(source, "HALF_COMPLETED_UPDATES = 504", "HALF_COMPLETED_UPDATES = 605", receipts)
    source = replace_exact(source, "FINAL_COMPLETED_UPDATES = 554", "FINAL_COMPLETED_UPDATES = 655", receipts)
    source = replace_region(
        source,
        "def validate_preregistration",
        "def validate_artifact",
        VALIDATE_PREREGISTRATION,
        receipts,
    )
    source = replace_region(
        source,
        "def validate_source_snapshot",
        "def graph_receipt",
        VALIDATE_SOURCE,
        receipts,
    )
    source = replace_region(
        source,
        '    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))',
        '    source_receipt = preregistration["source_checkpoint"]["snapshot"]',
        SOURCE_EVIDENCE,
        receipts,
    )
    old_gradient = '''        ppo_predictor_gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
        baseline_gradients = v29.compose_gradients(
            ppo_predictor_gradients, anchor_gradients, PREFIX_ANCHOR_SCALE, enabled=True
        )
        full_horizon_gradients = v29.compose_gradients(
            baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=True
        )
        gradients = v29.compose_gradients(
            full_horizon_gradients, reset_gradients, v56.RESET_TEACHER_SCALE, enabled=True
        )
        combined_loss = (
            ppo_loss
            + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32) * predictor_loss
            + jnp.asarray(PREFIX_ANCHOR_SCALE, dtype=jnp.float32) * anchor_loss
            + jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss
            + jnp.asarray(v56.RESET_TEACHER_SCALE, dtype=jnp.float32) * reset_loss
        )'''
    new_gradient = '''        gradients = jax.tree_util.tree_map(
            lambda value: jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32)
            * jnp.asarray(value, dtype=jnp.float32),
            teacher_gradients,
        )
        combined_loss = (
            jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss
        )'''
    source = replace_exact(source, old_gradient, new_gradient, receipts)
    source = replace_exact(
        source,
        '''        after = training.clamp_stage2_parameters(after)
        full.validate_log_std(after)''',
        '''        after = training.clamp_stage2_parameters(after)
        full.validate_log_std(after)
        teacher_loss_after, teacher_metrics_after = static_teacher_objective(after)
        if not float(teacher_loss_after) < float(teacher_loss):
            raise ValueError(
                f"Winner-v65 same-batch teacher loss did not decrease at {completed_updates}"
            )''',
        receipts,
    )
    source = replace_exact(
        source,
        '''        gradient_max = common.tree_max_abs(gradients)
        if not all(value > 0.0 for value in gradient_max.values()) or not all(value > 0.0 for value in deltas.values()):
            raise ValueError(f"Winner-v65 closed a leaf at {completed_updates}")''',
        '''        gradient_max = common.tree_max_abs(gradients)
        if (
            not all(gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            or not all(gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            or not all(deltas[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
        ):
            raise ValueError(f"Winner-v65 isolated teacher gradient closed at {completed_updates}")''',
        receipts,
    )
    source = replace_exact(
        source,
        '            "full_action_teacher_loss": float(teacher_loss),',
        '''            "full_action_teacher_loss": float(teacher_loss),
            "full_action_teacher_loss_after": float(teacher_loss_after),
            "full_action_teacher_loss_delta": float(teacher_loss_after) - float(teacher_loss),''',
        receipts,
    )
    source = replace_exact(source, "list(range(455, 555))", "list(range(556, 656))", receipts)
    source = replace_exact(
        source,
        '"source_snapshot_graph_and_optimizer_count_454_exact"',
        '"source_snapshot_graph_and_optimizer_count_555_exact"',
        receipts,
    )
    source = replace_exact(
        source,
        '''        "all_100_updates_all_12_gradients_and_deltas_nonzero": all(
            all(value > 0.0 for value in row["combined_gradient_max_abs"].values())
            and all(value > 0.0 for value in row["leaf_max_abs_delta"].values())
            for row in metrics
        ),
        "all_12_leaves_changed_cumulatively": all(value > 0.0 for value in cumulative.values()),''',
        '''        "all_100_teacher_gradients_local_and_policy_deltas_nonzero": all(
            all(row["combined_gradient_max_abs"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            and all(row["combined_gradient_max_abs"][key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            and all(row["leaf_max_abs_delta"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            for row in metrics
        ),
        "all_100_same_batch_teacher_losses_strictly_decrease": all(
            row["full_action_teacher_loss_delta"] < 0.0 for row in metrics
        ),
        "all_policy_leaves_changed_cumulatively": all(
            cumulative[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
        ),''',
        receipts,
    )
    source = replace_exact(source, '"optimizer_count_554_exact"', '"optimizer_count_655_exact"', receipts)
    source = replace_exact(source, '== [("half", 504), ("final", 554)]', '== [("half", 605), ("final", 655)]', receipts)
    source = replace_exact(
        source,
        '"completed_updates": 454, "optimizer_count": 454',
        '"completed_updates": 555, "optimizer_count": 555',
        receipts,
    )
    source = replace_exact(
        source,
        '"completed_updates": 454,',
        '"completed_updates": 555,',
        receipts,
    )
    source = replace_exact(
        source,
        '"v57_result_lf_sha256": lf_sha256(V45_RESULT)',
        '"v64b_result_lf_sha256": lf_sha256(V45_RESULT)',
        receipts,
    )
    compile(source, "winner_v65_transformed.py", "exec")
    return source, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v65 contract: {path}")
    v64b = json.loads(V64B_RESULT.read_text(encoding="utf-8"))
    v64b_contract = json.loads(V64B_CONTRACT.read_text(encoding="utf-8"))
    v60_result = json.loads(V60_RESULT.read_text(encoding="utf-8"))
    source, receipts = transformed_source()
    if (
        sha256(V64B_RESULT) != V64B_RESULT_SHA256
        or v64b.get("status")
        != "PASS_WINNER_V64B_ISOLATED_PERSISTENT_TEACHER_STEP"
        or v64b.get("decision")
        != "PREREGISTER_BOUNDED_ISOLATED_PERSISTENT_TEACHER_CONTINUATION_ONLY"
        or v64b.get("failed_checks") != []
        or v64b.get("execution", {}).get("optimizer_updates") != 1
        or v64b_contract.get("v64b", {}).get("identity")
        != "WINNER_V64B_PREREGISTRATION_LOCAL_NAME_CORRECTION"
        or v60_result.get("teacher_snapshot", {}).get("optimizer_count") != 100
    ):
        raise ValueError("Winner-v65 source authority changed")
    source_snapshot = v64b["snapshot"]
    source_graph = {
        "path": v64b["graph"]["path"],
        "sha256": v64b["graph"]["sha256"],
        "bytes": v64b["graph"]["bytes"],
        "completed_updates": 555,
    }
    teacher_snapshot = {
        "path": v60_result["teacher_snapshot"].get("path"),
        "sha256": v60_result["teacher_snapshot"]["sha256"],
        "bytes": v60_result["teacher_snapshot"]["bytes"],
        "completed_updates": 100,
        "optimizer_count": 100,
    }
    sources = dict(v64b_contract["sources"])
    additions = {
        "v65_builder": Path("tools/build_winner_v65_isolated_persistent_teacher_training.py"),
        "v65_runner": Path("tools/run_winner_v65_isolated_persistent_teacher_training.py"),
        "v65_tests": Path("tests/test_winner_v65_isolated_persistent_teacher_training.py"),
        "v64b_result": Path(
            "outputs/analysis/winner_v64b_isolated_persistent_teacher_step_result.json"
        ),
        "v60_builder": Path(
            "tools/build_winner_v60_integrated_numeric_guard_training_preregistration.py"
        ),
    }
    sources.update(
        {
            name: {
                "path": path.as_posix(),
                "hash_mode": "lf",
                "sha256": lf_sha256(ROOT / path),
            }
            for name, path in additions.items()
        }
    )
    objective = {
        "update_gradient": "full_action_persistent_teacher_only",
        "persistent_teacher": {
            "configuration_ids": [
                "COM_X_NEG",
                "COM_CORNER_00",
                "COM_CORNER_01",
                "COM_CORNER_02",
                "COM_CORNER_03",
                "OPTIONAL_AGGREGATE_HEAVY_AFT",
                "DISCOVERY_02",
                "DISCOVERY_03",
                "DISCOVERY_06",
                "DISCOVERY_09",
                "DISCOVERY_10",
            ],
            "heldout_ids_excluded": [
                "HELDOUT_04",
                "HELDOUT_07",
                "HELDOUT_09",
                "HELDOUT_15",
            ],
            "configuration_plant_rows": 22,
            "action_indices": list(range(14)),
            "scale": 136.35153198242188,
            "loss": "full-14D mask mean squared error",
            "candidate": "deterministic graph-authoritative bounded recurrent mean",
            "target": "stop-gradient graph-bounded static target relative to realized previous action",
        },
        "monitor_only_excluded_from_update": [
            "PPO",
            "normalized predictor",
            "prefix right-pitch anchor",
            "first-tick teacher",
        ],
        "inherited_adam_state": True,
        "coefficient_or_length_search": False,
        "attention_or_flat_transport_added": False,
    }
    value = {
        "schema_version": "winner_v65.isolated_persistent_teacher_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_ISOLATED_PERSISTENT_TEACHER_ARM_ONLY",
        "causal_hypothesis": (
            "Removing the V63b-measured opposing update terms lets the sufficient full "
            "persistent teacher reduce its on-policy residual without changing the ABI."
        ),
        "source_checkpoint": {
            "completed_updates": 555,
            "optimizer_count": 555,
            "snapshot": source_snapshot,
            "graph": source_graph,
        },
        "teacher_checkpoint": {
            "completed_updates": 100,
            "optimizer_count": 100,
            "snapshot": teacher_snapshot,
        },
        "frozen_training": {
            "source_completed_updates": 555,
            "source_optimizer_count": 555,
            "continuation_optimizer_updates": 100,
            "final_optimizer_count": 655,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "persistent_teacher_scale": 136.35153198242188,
            "persistent_checkpoints": {"half": 605, "final": 655},
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "coefficient_or_length_search": False,
            "duration_source": "inherit the reviewed 100-update half/final persistence design",
        },
        "objective": objective,
        "stop_rules": [
            "stop if source snapshot, graph, Adam state, teacher snapshot, or transformed source differs",
            "stop if any environment, population, receipt, action boundary, reward, mask, or transition differs",
            "stop if a heldout configuration receives a teacher label",
            "stop unless every update selects exactly 22 plant rows and all 14 action indices",
            "stop unless teacher gradients are nonzero on all six policy leaves and zero on all other leaves",
            "stop unless every update strictly reduces its own same-batch persistent-teacher loss",
            "stop if hidden replay exceeds 2e-6 or successor masks disagree",
            "stop if any gradient, parameter delta, loss, metric, snapshot, or ONNX contract is invalid",
            "do not run or inspect the formal support gate in this workflow",
            "do not select a checkpoint from training losses or intermediate behavior",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "checkpoint_rule": (
                "both checkpoints remain evidence until one separately frozen unchanged support gate classifies both"
            ),
            "pass_authorizes_only": "a separately preregistered half/final support gate",
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "transformation": {
            "base": "exact Winner-v60 transformed training source",
            "base_source_sha256": hashlib.sha256(v60.transformed_source()[0].encode()).hexdigest(),
            "transformed_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "replacements": receipts,
            "replacement_groups": len(receipts),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen isolated-persistent-teacher support gate preregistration"
            ),
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v65 isolated persistent-teacher training preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source / half / final optimizer counts: `555 / 605 / 655`",
                "- Updates / episode slots: `100 / 2,000,000`",
                "- Update gradient: `full-action persistent teacher only`",
                "- PPO/predictor/anchor/reset: `monitor-only, excluded`",
                "- Same-batch loss decrease required every update: `yes`",
                "- Formal support / robot: `0 / 0`",
                f"- Transformed source SHA-256: `{value['transformation']['transformed_source_sha256']}`",
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
