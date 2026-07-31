from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v24_baseline_anchored_support_gate_preregistration.json"
BUILDER = ROOT / "tools/build_winner_v24_baseline_anchored_support_gate_preregistration.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("winner_v24_support_gate_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gate_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
    assert value["decision"] == "AUTHORIZE_ONE_FROZEN_WINNER_V24_248_CELL_GATE_ONLY"
    gate = value["future_frozen_support_gate"]
    assert gate["cells_per_checkpoint"] == 124
    assert gate["checkpoint_labels"] == ["half", "final"]
    assert gate["all_cells_at_both_checkpoints_must_pass"] is True
    assert gate["selection_by_closest_result"] is False
    assert gate["predictor_scoring"]["head_output_coordinates"] == "normalized"
    assert value["training_artifact"]["half"]["snapshot"]["completed_updates"] == 150
    assert value["training_artifact"]["final"]["snapshot"]["completed_updates"] == 200
    assert value["pass_rule"]["learned_prediction_beats_constant_per_plant"] is True
    assert value["execution_now"] == {
        "formal_support_cells": 0,
        "heldout_repeat_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = ROOT / ".github/workflows/winner-v24-baseline-anchored-support-gate.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v24_baseline_anchored_support_gate_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source


def test_builder_binds_completed_updates_150_and_200(tmp_path, monkeypatch) -> None:
    builder = _load_builder()
    training_path = tmp_path / "training.json"
    base_path = tmp_path / "base.json"
    output = tmp_path / "prereg.json"
    markdown = tmp_path / "prereg.md"
    snapshots = [
        {
            "completed_updates": update,
            "sha256": f"{update:064x}"[-64:],
            "bytes": 1000 + update,
        }
        for update in range(101, 201)
    ]
    checkpoints = [
        {
            "label": label,
            "completed_updates": update,
            "graph": {"sha256": digit * 64, "bytes": 2000 + update},
        }
        for label, update, digit in (("half", 150, "a"), ("final", 200, "b"))
    ]
    training_path.write_text(
        json.dumps(
            {
                "status": "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT",
                "decision": "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_ONLY",
                "failed_checks": [],
                "execution": {"formal_support_cells": 0, "optimizer_updates": 100},
                "authority": {"robot_clearance": False},
                "repository_attribution": {
                    "repository": "RobVanProd/open-duck-mini-rdkx5",
                    "github_run_attempt": 1,
                    "github_run_id": 1,
                    "github_artifact_id": 2,
                },
                "snapshot_manifest": snapshots,
                "persistent_checkpoints": checkpoints,
                "source_snapshot": {"sha256": "c" * 64, "bytes": 999},
                "objective": {"terminal_delta": -250.0},
            }
        ),
        encoding="utf-8",
    )
    base_path.write_text(
        json.dumps(
            {
                "future_frozen_support_gate": {
                    "cells_per_checkpoint": 124,
                    "checkpoint_labels": ["half", "final"],
                    "duration_ticks": 250,
                    "all_cells_at_both_checkpoints_must_pass": True,
                    "selection_by_closest_result": False,
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "TRAINING_RESULT", training_path)
    monkeypatch.setattr(builder, "BASE_PREREGISTRATION", base_path)
    monkeypatch.setattr(builder, "SOURCES", {})
    monkeypatch.setattr(
        sys,
        "argv",
        [str(BUILDER), "--output", str(output), "--markdown", str(markdown)],
    )
    assert builder.main() == 0
    value = json.loads(output.read_text(encoding="utf-8"))
    assert value["training_artifact"]["half"]["snapshot"] == snapshots[49]
    assert value["training_artifact"]["final"]["snapshot"] == snapshots[99]
    assert value["training_artifact"]["half"]["graph"] == checkpoints[0]["graph"]
    assert value["training_artifact"]["final"]["graph"] == checkpoints[1]["graph"]
