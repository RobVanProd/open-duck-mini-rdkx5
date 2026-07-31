from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v48c_causal_population_scope_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v48c_causal_population_scope.py"
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v48c_causal_population_scope_preregistration.json"
)
RESULT = ROOT / "outputs/analysis/winner_v48c_causal_population_scope_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_binds_all_three_source_results() -> None:
    builder = load(BUILDER, "winner_v48c_builder")
    v48 = json.loads(builder.V48_RESULT.read_text(encoding="utf-8"))
    v48b = json.loads(builder.V48B_RESULT.read_text(encoding="utf-8"))
    v47b = json.loads(builder.V47B_RESULT.read_text(encoding="utf-8"))
    builder.validate_sources(v48, v48b, v47b)


def test_discrete_outcome_excludes_float_diagnostics() -> None:
    runner = load(RUNNER, "winner_v48c_discrete")
    cell = {
        "support_pass": False,
        "terminal": {"tick": 3, "checks": {"roll_pitch": False}, "contacts": [1, 1], "pitch": 0.4},
        "episode": {"valid_ticks": 3, "initial_contacts": [1, 1], "maximum_abs_tilt": 0.4},
        "previous_action_chain_exact": True,
    }
    assert runner.discrete_outcome(cell) == {
        "support_pass": False,
        "terminal_tick": 3,
        "terminal_checks": {"roll_pitch": False},
        "terminal_contacts": [1, 1],
        "valid_ticks": 3,
        "initial_contacts": [1, 1],
        "previous_action_chain_exact": True,
    }


def test_generated_preregistration_has_no_float_tolerance_when_present() -> None:
    if not PREREGISTRATION.exists():
        return
    runner = load(RUNNER, "winner_v48c_generated")
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
    assert value["decision"] == "AUTHORIZE_ONE_CAPTURED_CAUSAL_POPULATION_AUDIT_ONLY"
    assert value["scope"]["float_tolerance"] is None
    assert value["scope"]["new_physics_cells"] == 0
    assert value["authority"]["training_authorized"] is False
    runner.validate_source_manifest(value)


def test_result_selects_only_mechanism_preregistration_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
    assert value["decision"] == (
        "AUTHORIZE_FULL_14D_STATIC_TEACHER_MECHANISM_PREREGISTRATION_ONLY"
    )
    assert value["execution"]["captured_failure_pair_audits"] == 28
    assert value["execution"]["new_diagnostic_cells"] == 0
    assert value["authority"]["training_authorized"] is False


def test_runner_contains_no_physics_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "mujoco" not in source.lower()
    assert "onnxruntime" not in source.lower()
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "/dev/tty" not in source
