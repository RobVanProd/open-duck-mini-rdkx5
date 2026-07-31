from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v81_pitch_action_head_continuation_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v81_pitch_action_head_continuation.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v81_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_continuation_boundaries_are_exact() -> None:
    builder = load_builder()
    assert builder.SOURCE_COUNT == 656
    assert builder.HALF_COUNT == 705
    assert builder.FINAL_COUNT == 755
    assert builder.CONTINUATION_UPDATES == 99
    assert builder.FRACTIONS[-1] == 0.0009765625


def test_runner_is_localized_persistent_and_offline() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--pitch-action-head-continuation-authorized" in source
    assert "--hardware-authorized" not in source
    assert "for completed_count in range(SOURCE_COUNT + 1, FINAL_COUNT + 1)" in source
    assert "v80.project_pitch_head_gradient" in source
    assert "snapshot_every_accepted_update" in source
    assert "HALF_COUNT" in source and "FINAL_COUNT" in source
    assert '"optimizer_updates": len(metrics)' in source
    assert '"robot_or_rdk_access": 0' in source
