from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT
    / "tools/build_winner_v92_universal_target_response_observer_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v92_universal_target_response_observer.py"
PREREGISTRATION = (
    ROOT
    / "outputs/analysis/winner_v92_universal_target_response_observer_preregistration.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v92_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_preselects_v22_final_from_saved_evidence() -> None:
    module = load_builder()
    selected = module.selected_v22_final()
    assert selected["label"] == "final"
    assert selected["update"] == 100
    assert selected["snapshot_sha256"] == module.SNAPSHOT_SHA256
    assert selected["onnx_sha256"] == module.ONNX_SHA256
    assert all(
        value > 0.0
        for value in selected["heldout_advantage_over_constant"].values()
    )


def test_preregistration_freezes_complete_combined_gate() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
    )
    assert value["source_observer"]["label"] == "final"
    assert value["frozen_target"]["candidate_index"] == 536
    assert value["gate"] == {
        "actuator_plants": 2,
        "checkpoint_or_candidate_selection_from_new_result": False,
        "core_model_configurations": 56,
        "duration_ticks": 250,
        "flat_transport_feature_enabled": False,
        "formal_support_cells": 124,
        "heldout_repeat_cells": 32,
        "pass_rule": value["gate"]["pass_rule"],
        "sensor_prng_checkpoint_index": 1,
        "sensor_transport_conditions": 6,
        "thresholds": "unchanged reviewed Winner-v12 physical support thresholds",
    }
    assert value["execution_now"] == {
        "formal_support_cells": 0,
        "heldout_repeat_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
    }
    assert value["authority"]["robot_clearance"] is False


def test_runner_uses_universal_action_without_optimizer_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'mode="full_teacher"' in source
    assert "v22_gate.load_snapshot_for_reviewed_gate" in source
    assert '"learned_prediction_beats_constant_per_plant"' in source
    assert '"all_16_heldout_contexts_separate"' in source
    assert '"all_32_heldout_repeats_bit_exact"' in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
