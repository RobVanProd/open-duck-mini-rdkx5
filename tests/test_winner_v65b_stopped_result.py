from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v65b_stopped_result.py"


def test_v65b_stopped_builder_compiles_and_freezes_counts() -> None:
    compile(BUILDER.read_text(encoding="utf-8"), str(BUILDER), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v65b_stopped_result as builder

    assert builder.SOURCE_COUNT == 555
    assert builder.EXPECTED_COUNTS == tuple(range(556, 575))
    assert builder.LAST_DURABLE_COUNT == 574
    assert builder.FAILED_ATTEMPT_COUNT == 575
    assert builder.snapshot_name(574).endswith("_574.npz")


def test_v65b_stopped_metadata_contract() -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v65b_stopped_result as builder

    metadata = {
        "schema_version": "winner_v21.predictor_preserving_snapshot.v1",
        "stage": "isolated_persistent_teacher_joint_stage2",
        "completed_updates": 574,
        "source_completed_updates": 555,
        "root_seed": 120120,
        "learning_rate": 0.0001,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
        "objective": {
            "update_gradient": "full_action_persistent_teacher_only",
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
    }
    assert builder.metadata_exact(metadata, 574)
    assert not builder.metadata_exact({**metadata, "completed_updates": 575}, 574)
    assert not builder.metadata_exact(
        {**metadata, "robot_or_rdk_access": 1}, 574
    )


def test_v65b_stopped_builder_has_no_hardware_or_training_path() -> None:
    source = BUILDER.read_text(encoding="utf-8").lower()
    assert "adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
    assert "torque_enable" not in source
