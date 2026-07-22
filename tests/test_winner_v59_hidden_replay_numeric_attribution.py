from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v59_hidden_replay_numeric_attribution_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v59_hidden_replay_numeric_attribution.py"
CONTRACT = ROOT / "outputs/analysis/winner_v59_hidden_replay_numeric_attribution_preregistration.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_and_transformed_numeric_attribution_compile() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    builder = load_module(BUILDER, "winner_v59_builder_test")
    transformed, receipts = builder.transformed_source()
    compile(transformed, "winner_v59_transformed.py", "exec")
    assert receipts
    assert "recurrent_hidden_trajectory" in transformed
    assert "eager_hidden" in transformed
    assert "probability_ratio_max_abs_delta" in transformed
    assert 'print(result["status"])\n        return 0\n\n' in transformed
    assert transformed.index('print(result["status"])\n        return 0') < transformed.index(
        "after, optimizer = training.adam_step("
    )
    assert "winner_v59.hidden_replay_numeric_attribution_preregistration.v1" in transformed
    assert "PREREGISTERED_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION" in transformed
    assert "AUTHORIZE_ONE_ZERO_UPDATE_EAGER_SCAN_NUMERIC_ATTRIBUTION_ONLY" in transformed
    assert 'authority.get("continuation_authorized") is not False' in transformed
    assert 'authority.get("retry_authorized") is not False' not in transformed
    assert "--hardware-authorized" not in transformed
    assert '"robot_clearance": False' in transformed


def test_runner_requires_explicit_diagnostic_flags(monkeypatch, tmp_path: Path) -> None:
    module = load_module(RUNNER, "winner_v59_runner_test")
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


def test_contract_freezes_numeric_thresholds_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["thresholds"] == {
        "eager_hidden_max_abs_error": 0.0,
        "log_probability_max_abs_delta": 0.0001,
        "mean_action_max_abs_delta": 1e-06,
        "ppo_loss_abs_delta": 0.0001,
        "probability_ratio_max_abs_delta": 0.0001,
        "scan_hidden_max_abs_error": 2e-06,
        "value_max_abs_delta": 1e-05,
    }
    assert value["authority"]["continuation_authorized"] is False
    assert value["execution_now"]["optimizer_updates"] == 0


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
    builder = load_module(BUILDER, "winner_v59_builder_manifest_test")
    transformed, receipts = builder.transformed_source()
    assert hashlib.sha256(transformed.encode()).hexdigest() == value["transformation"][
        "transformed_source_sha256"
    ]
    assert receipts == value["transformation"]["replacements"]
