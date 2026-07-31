from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v55_reset_label_handoff_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v55_reset_label_handoff.py"
PREREG = ROOT / "outputs/analysis/winner_v55_reset_label_handoff_preregistration.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v55_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_compile_and_have_no_training_or_hardware_path() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source


def test_runner_requires_explicit_cpu_diagnostic_flags(
    monkeypatch, tmp_path: Path
) -> None:
    module = load_runner()
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--training-work-root",
            str(tmp_path),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_delayed_teacher_session_preserves_prefix_and_switches_at_tick() -> None:
    module = load_runner()

    class FakeSession:
        def run(self, output_names, inputs):
            del output_names, inputs
            return [
                np.full((1, 14), 0.01, dtype=np.float32),
                np.full((1, 14), 0.01, dtype=np.float32),
                np.full((1, 64), 0.5, dtype=np.float32),
            ]

    wrapper = module.DelayedTeacherSession(
        FakeSession(),
        raw_teacher=np.full((14,), 0.4, dtype=np.float32),
        handoff_tick=2,
        bounded_action=lambda raw, previous: np.minimum(raw, previous + 0.1).astype(
            np.float32
        ),
    )
    inputs = {
        "previous_action": np.zeros((1, 14), dtype=np.float32),
        "obs": np.zeros((1, 115), dtype=np.float32),
        "h_in": np.zeros((1, 64), dtype=np.float32),
    }
    assert np.array_equal(wrapper.run([], inputs)[0], np.full((1, 14), 0.01, np.float32))
    assert np.array_equal(wrapper.run([], inputs)[0], np.full((1, 14), 0.01, np.float32))
    switched = wrapper.run([], inputs)
    assert np.allclose(switched[0], 0.1)
    assert np.array_equal(switched[0], switched[1])
    assert np.array_equal(switched[2], np.full((1, 64), 0.5, np.float32))


def test_classification_selects_latest_full_positive_handoff() -> None:
    module = load_runner()
    classification, decision, selected = module.select_classification(
        reset_conflict=True,
        pass_counts={0: 12, 1: 12, 2: 12, 4: 11, 8: 12, 12: 10, 16: 0, 20: 0},
    )
    assert classification == "RESET_LABEL_CONFLICT_WITH_DELAYED_HANDOFF_FEASIBLE"
    assert decision == "AUTHORIZE_DELAYED_TEACHER_MECHANISM_CPU_CONTRACT_PREREGISTRATION_ONLY"
    assert selected == 8


def test_preregistration_freezes_population_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["reset_collision_audit"]["rows"] == 30
    assert value["handoff_audit"]["handoff_ticks"] == [0, 1, 2, 4, 8, 12, 16, 20, 250]
    assert value["handoff_audit"]["cells"] == 108
    assert value["execution_now"]["diagnostic_cells"] == 0
    assert value["authority"]["training_authorized"] is False


def test_source_manifest_is_exact_when_preregistered() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
