from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v60_integrated_numeric_guard_training_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v60_integrated_numeric_guard_training.py"
CONTRACT = ROOT / "outputs/analysis/winner_v60_integrated_numeric_guard_training_preregistration.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_and_transformed_training_compile() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    builder = load_module(BUILDER, "winner_v60_builder_test")
    transformed, receipts = builder.transformed_source()
    compile(transformed, "winner_v60_transformed.py", "exec")
    assert receipts
    assert transformed.count("training.adam_step(") == 1
    assert "SOURCE_COMPLETED_UPDATES = 454" in transformed
    assert "HALF_COMPLETED_UPDATES = 504" in transformed
    assert "FINAL_COMPLETED_UPDATES = 554" in transformed
    assert '"all_100_hidden_replays_at_most_2e_6"' in transformed
    assert 'float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 2.0e-6' in transformed
    assert 'row["sampled_hidden_replay_max_abs_error"] <= 2.0e-6' in transformed
    assert '"all_100_hidden_replays_at_most_1e_6"' not in transformed
    assert "winner_v56_first_tick_teacher_mapping" in transformed
    assert "reset_grad(before)" in transformed
    assert "flat_transport_or_attention_added" in transformed
    assert "Winner-v58" not in transformed
    assert "--hardware-authorized" not in transformed
    assert '"robot_clearance": False' in transformed


def test_runner_requires_explicit_training_flags(monkeypatch, tmp_path: Path) -> None:
    module = load_module(RUNNER, "winner_v60_runner_test")
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path),
            "--source-snapshot", str(tmp_path),
            "--source-graph", str(tmp_path),
            "--teacher-snapshot", str(tmp_path),
            "--work-root", str(tmp_path / "work"),
            "--output", str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_contract_freezes_exact_continuation_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["frozen_training"]["source_completed_updates"] == 454
    assert value["frozen_training"]["continuation_optimizer_updates"] == 100
    assert value["frozen_training"]["final_optimizer_count"] == 554
    assert value["frozen_training"]["persistent_checkpoints"] == {
        "half": 504,
        "final": 554,
    }
    assert value["frozen_training"]["hidden_replay_numeric_guard"] == {
        "coefficient_or_threshold_search": False,
        "metric": "sampled_hidden_replay_max_abs_error",
        "selected_threshold": 2e-6,
        "selection_basis": "next power-of-two bound above the V59 measured maximum",
        "source_legacy_threshold": 1e-6,
        "v59_measured_maximum": 1.125037670135498e-6,
        "v59_result_sha256": "2bc025115d2c2d4eba2aca7e8d0670b2c9e6f90fc2d96507d38034cbc946c39b",
    }
    assert value["objective"]["first_tick_teacher"]["selected_elements"] == 616
    assert value["objective"]["first_tick_teacher"]["flat_transport_or_attention_added"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["formal_support_gate_authorized"] is False


def test_source_manifest_and_transform_are_exact_when_preregistered() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    builder = load_module(BUILDER, "winner_v60_builder_manifest_test")
    transformed, receipts = builder.transformed_source()
    assert hashlib.sha256(transformed.encode()).hexdigest() == value["transformation"][
        "transformed_source_sha256"
    ]
    assert receipts == value["transformation"]["replacements"]
