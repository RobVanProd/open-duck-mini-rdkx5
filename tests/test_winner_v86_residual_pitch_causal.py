from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v86_residual_pitch_causal_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v86_residual_pitch_causal.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v86_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_freezes_twelve_exact_failed_pairs(tmp_path: Path) -> None:
    output = tmp_path / "v86.json"
    markdown = tmp_path / "v86.md"
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output",
            str(output),
            "--markdown",
            str(markdown),
        ],
        cwd=ROOT,
        check=True,
    )
    value = json.loads(output.read_text(encoding="utf-8"))
    frozen = value["frozen_source"]
    assert frozen["failure_pair_count"] == 12
    assert frozen["diagnostic_cells"] == 48
    assert frozen["checkpoint_labels_updates"] == {"half": 705, "final": 755}
    assert frozen["arms"] == ["graph", "full_teacher", "pitch_teacher", "nonpitch_zero"]
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_read_only_cpu_diagnostic() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--causal-diagnostic-authorized" in source
    assert "v48.InterventionSession" in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
