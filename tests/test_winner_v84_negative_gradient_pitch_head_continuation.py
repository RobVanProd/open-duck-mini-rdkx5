from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT
    / "tools/build_winner_v84_negative_gradient_pitch_head_continuation_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v84_negative_gradient_pitch_head_continuation.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v84_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_freezes_original_persistence_boundaries(tmp_path: Path) -> None:
    output = tmp_path / "v84.json"
    markdown = tmp_path / "v84.md"
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
    continuation = value["continuation"]
    assert continuation["source_optimizer_count"] == 675
    assert continuation["half_optimizer_count"] == 705
    assert continuation["final_optimizer_count"] == 755
    assert continuation["optimizer_updates"] == 80
    assert continuation["fractions_largest_first"][-1] == 2.0**-12
    assert continuation["optimizer_m_and_v_transition"] == (
        "all elements bit-exact preserved across all updates"
    )
    assert value["authority"]["support_gate_authorized_now"] is False
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_localized_persistent_and_cpu_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "for completed_count in range(builder.SOURCE_COUNT + 1, builder.FINAL_COUNT + 1)" in source
    assert "v80.project_pitch_head_gradient" in source
    assert "negative_gradient_delta" in source
    assert "v63.tree_bit_exact(source_optimizer[\"m\"], optimizer[\"m\"])" in source
    assert "--negative-gradient-continuation-authorized" in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
