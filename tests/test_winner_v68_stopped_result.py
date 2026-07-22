from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v68_stopped_result.py"


def test_v68_stopped_builder_compiles_and_freezes_counts() -> None:
    compile(BUILDER.read_text(encoding="utf-8"), str(BUILDER), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v68_stopped_result as builder

    assert builder.SOURCE_COUNT == 575
    assert builder.EXPECTED_COUNTS == tuple(range(576, 602))
    assert builder.LAST_DURABLE_COUNT == 601
    assert builder.FAILED_ATTEMPT_COUNT == 602
    assert builder.snapshot_name(601).endswith("_601.npz")


def test_v68_stopped_metadata_contract() -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v68_stopped_result as builder

    metadata = {
        "schema_version": "winner_v21.predictor_preserving_snapshot.v1",
        "stage": "backtracked_persistent_teacher_joint_stage2",
        "completed_updates": 601,
        "source_completed_updates": 575,
        "root_seed": 120120,
        "learning_rate": 0.0001,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
        "objective": {
            "update_gradient": "full_action_persistent_teacher_only",
            "attention_or_flat_transport_added": False,
        },
    }
    assert builder.metadata_exact(metadata, 601)
    assert not builder.metadata_exact({**metadata, "completed_updates": 602}, 601)


def test_v68_stopped_builder_has_no_training_or_hardware_path() -> None:
    source = BUILDER.read_text(encoding="utf-8").lower()
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
    assert "torque_enable" not in source
