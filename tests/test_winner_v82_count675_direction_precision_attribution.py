from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT
    / "tools/build_winner_v82_count675_direction_precision_attribution_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v82_count675_direction_precision_attribution.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v82_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_classification_prefers_least_changed_descent_direction() -> None:
    builder = load_builder()
    before = 1.0
    original = [1.1] * len(builder.ORIGINAL_FRACTIONS)
    classification, decision = builder.classify_count675(
        loss_before=before,
        adam_gradient_dot_delta=-0.1,
        adam_losses=original + [0.99] + [1.0] * 9,
        negative_gradient_losses=[0.9] * len(builder.NEGATIVE_GRADIENT_FRACTIONS),
        adam_parameter_changes=[1] * len(builder.EXTENDED_ADAM_FRACTIONS),
        negative_gradient_parameter_changes=[1]
        * len(builder.NEGATIVE_GRADIENT_FRACTIONS),
    )
    assert classification == "ADAM_DESCENT_EXISTS_BELOW_ONE_OVER_1024"
    assert decision == "PREREGISTER_ONE_COUNT675_EXTENDED_ADAM_STEP_PROOF"
    classification, _ = builder.classify_count675(
        loss_before=before,
        adam_gradient_dot_delta=-0.1,
        adam_losses=original + [1.0] * 10,
        negative_gradient_losses=[0.9] * len(builder.NEGATIVE_GRADIENT_FRACTIONS),
        adam_parameter_changes=[1] * len(builder.EXTENDED_ADAM_FRACTIONS),
        negative_gradient_parameter_changes=[1]
        * len(builder.NEGATIVE_GRADIENT_FRACTIONS),
    )
    assert classification == "ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS"


def test_builder_freezes_zero_update_contract(tmp_path: Path) -> None:
    output = tmp_path / "v82.json"
    markdown = tmp_path / "v82.md"
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
    assert value["source"]["optimizer_count"] == 674
    assert value["source"]["attempted_optimizer_count"] == 675
    assert value["diagnostic"]["extended_adam_fractions"][-1] == 2.0**-20
    assert value["diagnostic"]["negative_gradient_fractions"][-1] == 2.0**-12
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_cpu_only_zero_commit_diagnostic() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--count675-attribution-authorized" in source
    assert '"committed_optimizer_updates": 0' in source
    assert '"snapshots_written": 0' in source
    assert '"onnx_graphs_written": 0' in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source.lower()
    compile(source, str(RUNNER), "exec")
