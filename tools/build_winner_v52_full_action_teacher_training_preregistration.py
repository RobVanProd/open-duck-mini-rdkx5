#!/usr/bin/env python3
"""Freeze the 100-update Winner-v52 full-action-teacher continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V52_FULL_ACTION_TEACHER_TRAINING_PREREGISTRATION_20260722.md"
V46_PREREGISTRATION = ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
V46_RUNNER = ROOT / "tools/run_winner_v46_static_target_teacher_training.py"
V51B_RESULT = ANALYSIS / "winner_v51b_full_action_teacher_one_update_cpu_result.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V51B_RESULT_SHA256 = "9e08a08bd9614fbb31dc5104abb64270e2739157026f9c966e3466578bf92aa7"


TRANSFORMS: tuple[tuple[str, str, int], ...] = (
    (
        '"""Run the one frozen 100-update Winner-v46 static-target-teacher CPU arm."""',
        '"""Run the one frozen 100-update Winner-v52 full-action-teacher CPU arm."""',
        1,
    ),
    (
        "import run_winner_v44_static_target_teacher_source_gradient_contract as v44_runner  # noqa: E402",
        "import run_winner_v50_full_action_teacher_source_gradient_contract as v44_runner  # noqa: E402",
        1,
    ),
    (
        "import winner_v43_static_target_teacher as v43  # noqa: E402",
        "import winner_v43_static_target_teacher as v43  # noqa: E402\nimport winner_v49_full_action_static_target_teacher as v49  # noqa: E402",
        1,
    ),
    (
        '"winner_v46_static_target_teacher_training_preregistration.json"',
        '"winner_v52_full_action_teacher_training_preregistration.json"',
        1,
    ),
    (
        '"winner_v45_static_target_teacher_one_update_cpu_result.json"',
        '"winner_v51b_full_action_teacher_one_update_cpu_result.json"',
        1,
    ),
    ("SOURCE_COMPLETED_UPDATES = 252", "SOURCE_COMPLETED_UPDATES = 353", 1),
    ("HALF_COMPLETED_UPDATES = 302", "HALF_COMPLETED_UPDATES = 403", 1),
    ("FINAL_COMPLETED_UPDATES = 352", "FINAL_COMPLETED_UPDATES = 453", 1),
    (
        "FROZEN_TEACHER_SCALE = np.float32(58.436370849609375)",
        "FROZEN_TEACHER_SCALE = np.float32(136.35153198242188)",
        1,
    ),
    (
        '"winner_v46.static_target_teacher_training_preregistration.v1"',
        '"winner_v52.full_action_teacher_training_preregistration.v1"',
        1,
    ),
    (
        '"PREREGISTERED_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING"',
        '"PREREGISTERED_WINNER_V52_FULL_ACTION_TEACHER_TRAINING"',
        1,
    ),
    (
        '"AUTHORIZE_ONE_100_UPDATE_STATIC_TARGET_TEACHER_ARM_ONLY"',
        '"AUTHORIZE_ONE_100_UPDATE_FULL_ACTION_TEACHER_ARM_ONLY"',
        1,
    ),
    ('"static_target_teacher_scale"', '"full_action_teacher_scale"', 3),
    (
        'teacher = value.get("objective", {}).get("static_target_teacher", {})',
        'teacher = value.get("objective", {}).get("full_action_static_target_teacher", {})',
        1,
    ),
    ("list(v43.PITCH_ACTION_INDICES)", "list(v49.ACTION_INDICES)", 1),
    (
        'metadata.get("stage") != "static_target_teacher_joint_stage2"',
        'metadata.get("stage") != "full_action_static_target_teacher_joint_stage2"',
        1,
    ),
    (
        'metadata.get("source_completed_updates") != 251',
        'metadata.get("source_completed_updates") != 352',
        1,
    ),
    (
        'source_result["source_identity"]["source_snapshot"]["sha256"]',
        'source_result["source_identity"]["snapshot_sha256"]',
        1,
    ),
    (
        'source_result["source_identity"]["teacher_snapshot"]["sha256"]',
        'source_result["source_identity"]["teacher_snapshot_sha256"]',
        1,
    ),
    (
        "static_target_teacher_training_authorized",
        "full_action_teacher_training_authorized",
        1,
    ),
    (
        "--static-target-teacher-training-authorized",
        "--full-action-teacher-training-authorized",
        2,
    ),
    (
        '"PASS_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF"',
        '"PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"',
        1,
    ),
    (
        '"AUTHORIZE_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_ONLY"',
        '"AUTHORIZE_BOUNDED_FULL_ACTION_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"',
        1,
    ),
    ("v44_runner.training_teacher_loss", "v44_runner.full_training_teacher_loss", 1),
    (
        "v44_runner.build_training_teacher_batch",
        "v44_runner.build_full_training_teacher_batch",
        1,
    ),
    ('"static_target_teacher_loss"', '"full_action_teacher_loss"', 2),
    (
        'f"snapshot_static_target_teacher_update_{completed_updates:03d}.npz"',
        'f"snapshot_full_action_teacher_update_{completed_updates:03d}.npz"',
        1,
    ),
    (
        '"stage": "static_target_teacher_joint_stage2"',
        '"stage": "full_action_static_target_teacher_joint_stage2"',
        1,
    ),
    (
        'loaded["metadata"].get("stage") == "static_target_teacher_joint_stage2"',
        'loaded["metadata"].get("stage") == "full_action_static_target_teacher_joint_stage2"',
        1,
    ),
    ('f"winner_v46_{label}.onnx"', 'f"winner_v52_{label}.onnx"', 1),
    ("list(range(253, 353))", "list(range(354, 454))", 1),
    (
        '"optimizer_count_352_exact": int(np.asarray(optimizer["count"])) == 352',
        '"optimizer_count_453_exact": int(np.asarray(optimizer["count"])) == 453',
        1,
    ),
    (
        '== [("half", 302), ("final", 352)]',
        '== [("half", 403), ("final", 453)]',
        1,
    ),
    (
        '"winner_v46.static_target_teacher_training_result.v1"',
        '"winner_v52.full_action_teacher_training_result.v1"',
        1,
    ),
    (
        '"PASS_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT"',
        '"PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"',
        1,
    ),
    (
        '"HOLD_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT"',
        '"HOLD_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"',
        1,
    ),
    (
        '"AUTHORIZE_STATIC_TARGET_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
        '"AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
        1,
    ),
    (
        '"DO_NOT_EVALUATE_WINNER_V46_POLICY"',
        '"DO_NOT_EVALUATE_WINNER_V52_POLICY"',
        1,
    ),
    (
        '"completed_updates": 252, "optimizer_count": 252',
        '"completed_updates": 353, "optimizer_count": 353',
        1,
    ),
    ('"completed_updates": 252,', '"completed_updates": 353,', 1),
    (
        '"v45_result_lf_sha256": lf_sha256(V45_RESULT)',
        '"v51b_result_lf_sha256": lf_sha256(V45_RESULT)',
        1,
    ),
    (
        '"a separate frozen static-target-teacher support gate preregistration"',
        '"a separate frozen full-action-teacher support gate preregistration"',
        1,
    ),
)


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
    source = V46_RUNNER.read_text(encoding="utf-8")
    receipts: list[dict[str, Any]] = []
    for old, new, count in TRANSFORMS:
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v52 transform count changed: expected {count}, found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )
    return source, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v52 preregistration: {path}")

    old_prereg = json.loads(V46_PREREGISTRATION.read_text(encoding="utf-8"))
    source_result = json.loads(V51B_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    transformed, transform_receipts = transformed_source()
    if (
        sha256(V51B_RESULT) != V51B_RESULT_SHA256
        or source_result.get("status")
        != "PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
        or source_result.get("decision")
        != "AUTHORIZE_BOUNDED_FULL_ACTION_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"
        or source_result.get("execution", {}).get("optimizer_updates") != 1
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v52 source authority changed")

    sources = dict(old_prereg["sources"])
    additions = {
        "winner_v52_builder": Path("tools/build_winner_v52_full_action_teacher_training_preregistration.py"),
        "winner_v52_runner": Path("tools/run_winner_v52_full_action_teacher_training.py"),
        "winner_v52_tests": Path("tests/test_winner_v52_full_action_teacher_training.py"),
        "winner_v51b_result": Path("outputs/analysis/winner_v51b_full_action_teacher_one_update_cpu_result.json"),
        "winner_v50_full_teacher": Path("tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"),
        "winner_v49_teacher": Path("patches/winner_v49_full_action_static_target_teacher.py"),
        "winner_v46_frozen_runner": Path("tools/run_winner_v46_static_target_teacher_training.py"),
    }
    sources.update(
        {
            name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
            for name, path in additions.items()
        }
    )
    source_checkpoint = {
        "completed_updates": 353,
        "optimizer_count": 353,
        "snapshot": source_result["snapshot"],
        "graph": source_result["graph"],
    }
    teacher_final = next(
        row
        for row in teacher_result["persistent_checkpoints"]
        if row["label"] == "final"
    )
    value = {
        "schema_version": "winner_v52.full_action_teacher_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V52_FULL_ACTION_TEACHER_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_FULL_ACTION_TEACHER_ARM_ONLY",
        "causal_hypothesis": (
            "The V48c-selected full-14D teacher mapping can preserve the corrected "
            "gait across the inherited half/final persistence horizon."
        ),
        "source_checkpoint": source_checkpoint,
        "teacher_checkpoint": {
            "completed_updates": 100,
            "optimizer_count": 100,
            "snapshot": teacher_final["snapshot"],
        },
        "frozen_training": {
            "source_completed_updates": 353,
            "source_optimizer_count": 353,
            "continuation_optimizer_updates": 100,
            "final_optimizer_count": 453,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "full_action_teacher_scale": 136.35153198242188,
            "persistent_checkpoints": {"half": 403, "final": 453},
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "coefficient_or_length_search": False,
            "duration_source": "inherit the exact Winner-v46 100-update half/final persistence design",
        },
        "objective": {
            "ppo": "unchanged Winner-v46 recurrent PPO objective and failure transition shaping",
            "predictor": "unchanged normalized successor predictor at scale 380.9135437011719",
            "prefix_anchor": "unchanged prefix right-pitch anchor at scale 197.3112030029297",
            "combined_gradient": "existing Winner-v46 gradient with the pitch teacher replaced by the full-14D teacher gradient",
            "full_action_static_target_teacher": {
                "configuration_ids": [
                    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
                    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
                    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
                ],
                "heldout_ids_excluded": ["HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15"],
                "configuration_plant_rows": 22,
                "action_indices": list(range(14)),
                "scale": 136.35153198242188,
                "loss": "full-14D mask mean squared error",
                "candidate": "deterministic graph-authoritative bounded recurrent mean",
                "target": "stop-gradient graph-bounded static target relative to realized previous action",
                "table": "exact imported Winner-v42 selected shared two-plant targets",
                "action_replacement": False,
                "actor_input_added": False,
            },
        },
        "stop_rules": [
            "stop if source snapshot, graph, Adam state, teacher snapshot, or transformed source differs",
            "stop if any environment, population, receipt, action boundary, reward, mask, or transition differs",
            "stop if a heldout configuration receives a teacher label",
            "stop unless every update selects exactly 22 plant rows and all 14 action indices",
            "stop if teacher gradients affect value, log-std, or predictor leaves",
            "stop if hidden replay exceeds 1e-6 or successor masks disagree",
            "stop if any gradient, parameter delta, loss, metric, snapshot, or ONNX contract is invalid",
            "do not run or inspect the formal support gate in this workflow",
            "do not select a checkpoint from training losses or intermediate behavior",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "checkpoint_rule": "both checkpoints remain evidence until one separately frozen support gate classifies both",
            "pass_authorizes_only": "a separately preregistered half/final support gate",
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "transformation": {
            "base_runner": V46_RUNNER.relative_to(ROOT).as_posix(),
            "base_runner_lf_sha256": lf_sha256(V46_RUNNER),
            "transformed_source_sha256": hashlib.sha256(transformed.encode()).hexdigest(),
            "replacements": transform_receipts,
            "replacement_groups": len(transform_receipts),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate frozen full-action-teacher support gate preregistration",
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v52 full-action teacher training preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source / half / final optimizer counts: `353 / 403 / 453`",
                "- Updates / episode slots: `100 / 2,000,000`",
                "- Full-action teacher scale: `136.35153198242188`",
                "- Formal support / robot: `0 / 0`",
                "",
                "This inherits the exact V46 persistence horizon. Both checkpoints",
                "remain unselected evidence until a separate frozen support gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
