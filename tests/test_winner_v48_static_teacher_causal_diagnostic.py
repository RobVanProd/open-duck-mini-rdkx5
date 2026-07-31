from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v48_static_teacher_causal_diagnostic.py"
BUILDER = (
    ROOT
    / "tools/build_winner_v48_static_teacher_causal_diagnostic_preregistration.py"
)
PREREGISTRATION = (
    ROOT
    / "outputs/analysis/winner_v48_static_teacher_causal_diagnostic_preregistration.json"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeSession:
    def run(self, output_names, inputs):
        del output_names, inputs
        return [
            np.full((1, 14), 0.4, dtype=np.float32),
            np.full((1, 14), 0.4, dtype=np.float32),
            np.full((1, 64), 0.25, dtype=np.float32),
        ]


def identity_bound(raw: np.ndarray, previous: np.ndarray) -> np.ndarray:
    del previous
    return np.asarray(raw, dtype=np.float32)


def test_interventions_preserve_hidden_and_chain_applied_action() -> None:
    runner = load(RUNNER, "winner_v48_interventions")
    teacher = np.zeros((14,), dtype=np.float32)
    teacher[runner.PITCH_INDICES] = np.asarray(
        [-0.25, -0.5, 0.25, 0.25, -0.5, 0.25], dtype=np.float32
    )
    inputs = {"previous_action": np.zeros((1, 14), dtype=np.float32)}

    full = runner.InterventionSession(
        FakeSession(), raw_teacher=teacher, mode="full_teacher",
        bounded_action=identity_bound,
    ).run([], inputs)
    pitch = runner.InterventionSession(
        FakeSession(), raw_teacher=teacher, mode="pitch_teacher",
        bounded_action=identity_bound,
    ).run([], inputs)
    nonpitch = runner.InterventionSession(
        FakeSession(), raw_teacher=teacher, mode="nonpitch_zero",
        bounded_action=identity_bound,
    ).run([], inputs)

    assert np.array_equal(full[0][0], teacher)
    assert np.array_equal(pitch[0][0, runner.PITCH_INDICES], teacher[runner.PITCH_INDICES])
    assert np.all(pitch[0][0, runner.NONPITCH_INDICES] == np.float32(0.4))
    assert np.all(nonpitch[0][0, runner.NONPITCH_INDICES] == 0.0)
    assert np.all(nonpitch[0][0, runner.PITCH_INDICES] == np.float32(0.4))
    for outputs in (full, pitch, nonpitch):
        assert np.array_equal(outputs[0], outputs[1])
        assert np.array_equal(outputs[2], np.full((1, 64), 0.25, dtype=np.float32))


def test_action_alignment_uses_each_realized_previous_action() -> None:
    runner = load(RUNNER, "winner_v48_alignment")
    actions = np.zeros((2, 14), dtype=np.float32)
    actions[0, runner.PITCH_INDICES] = 0.25
    actions[1, runner.PITCH_INDICES] = 0.5
    teacher = np.zeros((14,), dtype=np.float32)
    teacher[runner.PITCH_INDICES] = 0.5
    previous_seen = []

    def bound(raw: np.ndarray, previous: np.ndarray) -> np.ndarray:
        previous_seen.append(np.asarray(previous).copy())
        return np.asarray(raw, dtype=np.float32)

    result = runner.action_alignment(actions, teacher, bound)
    assert np.array_equal(previous_seen[0], np.zeros((14,), dtype=np.float32))
    assert np.array_equal(previous_seen[1], actions[0])
    assert result["tick_count"] == 2
    assert result["pitch"]["maximum_abs"] == 0.25
    assert result["nonpitch"]["maximum_abs"] == 0.0
    assert len(result["per_tick"]) == 2


def test_failed_pair_classification_is_exhaustive() -> None:
    runner = load(RUNNER, "winner_v48_classification")

    def arms(full: bool, pitch: bool, nonpitch: bool):
        return {
            "full_teacher": {"support_pass": full},
            "pitch_teacher": {"support_pass": pitch},
            "nonpitch_zero": {"support_pass": nonpitch},
        }

    assert runner.classify_failed_pair(arms(False, False, False)) == "teacher_insufficient"
    assert runner.classify_failed_pair(arms(True, True, False)) == "pitch_output_causal"
    assert runner.classify_failed_pair(arms(True, False, True)) == "nonpitch_output_causal"
    assert runner.classify_failed_pair(arms(True, True, True)) == "either_single_intervention_rescues"
    assert runner.classify_failed_pair(arms(True, False, False)) == "pitch_nonpitch_interaction"


def test_builder_binds_exact_v47b_failures_and_v42_teacher() -> None:
    builder = load(BUILDER, "winner_v48_builder")
    v47b = json.loads(builder.V47B_RESULT.read_text(encoding="utf-8"))
    teacher = json.loads(builder.V42_RESULT.read_text(encoding="utf-8"))
    builder.validate_v47b_hold(v47b)
    builder.validate_teacher_table(teacher)
    failures = builder.failed_cells(v47b)
    assert len(failures) == 28
    assert sorted({row["configuration_id"] for row in failures}) == (
        builder.EXPECTED_CONFIGURATION_IDS
    )


def test_generated_preregistration_is_exact_and_source_bound_when_present() -> None:
    if not PREREGISTRATION.exists():
        return
    runner = load(RUNNER, "winner_v48_generated")
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
    assert value["decision"] == "AUTHORIZE_ONE_READ_ONLY_CPU_CAUSAL_DIAGNOSTIC"
    assert value["frozen_population"]["total_cells"] == 128
    assert value["frozen_population"]["formal_failed_pairs"] == 28
    assert value["action_alignment_report"]["threshold_or_closest_selection"] is False
    assert not any(value["execution_now"].values())
    assert value["authority"]["robot_clearance"] is False
    runner.validate_source_manifest(value)


def test_runner_contains_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "optimizer_updates\": 0" in source
    assert "--hardware-authorized" not in source
    assert "--suspended-or-benched" not in source
    assert "/dev/tty" not in source
