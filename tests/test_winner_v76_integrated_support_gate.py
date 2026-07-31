from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v76_integrated_support_gate_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v76_integrated_support_gate.py"
PREREG = ROOT / "outputs/analysis/winner_v76_integrated_support_gate_preregistration.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_and_transformed_gate_compile_without_training_or_hardware() -> None:
    builder = load_module(BUILDER, "winner_v76_builder_test")
    transformed, receipts = builder.transformed_source()
    compile(transformed, "winner_v76_transformed.py", "exec")
    assert receipts
    assert "adam_step(" not in transformed
    assert 'CHECKPOINTS = (("half", 605), ("final", 655))' in transformed
    assert 'expected_stage="fresh_moment_safeguarded_teacher_joint_stage2"' in transformed
    assert "snapshot_fresh_moment_safeguarded_update_" in transformed
    assert 'f"winner_v71_{label}.onnx"' in transformed
    assert "PASS_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION" in transformed
    assert "--hardware-authorized" not in transformed
    assert '"grounded_walking_authorized": False' in transformed


def test_runner_requires_explicit_cpu_gate_flags(monkeypatch, tmp_path: Path) -> None:
    module = load_module(RUNNER, "winner_v76_runner_test")
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


def test_preregistered_selection_is_fixed_final_not_metric_ranked() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["future_frozen_support_gate"]["cells_per_checkpoint"] == 124
    assert value["pass_rule"]["closest_checkpoint_selection"] is False
    assert value["selection_rule"]["selected_update_if_pass"] == 655
    assert value["selection_rule"]["metric_ranking_or_closest_result"] is False
    assert value["authority"]["robot_clearance"] is False


def test_source_manifest_and_transform_are_exact_when_preregistered() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    builder = load_module(BUILDER, "winner_v76_builder_manifest_test")
    transformed, receipts = builder.transformed_source()
    assert hashlib.sha256(transformed.encode()).hexdigest() == value["transformation"][
        "transformed_source_sha256"
    ]
    assert receipts == value["transformation"]["replacements"]
