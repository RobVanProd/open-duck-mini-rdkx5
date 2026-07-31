from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
BUILDER = ROOT / "tools/build_winner_v58a_guard_failure_attribution_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v58a_guard_failure_attribution.py"
CONTRACT = ROOT / "outputs/analysis/winner_v58a_guard_failure_attribution_preregistration.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_and_transformed_attribution_compile() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    builder = load_module(BUILDER, "winner_v58a_builder_test")
    transformed, receipts = builder.transformed_source()
    compile(transformed, "winner_v58a_transformed.py", "exec")
    assert receipts
    assert "training.adam_step(" in transformed
    assert (
        'print(result["status"])\n        return 0\n\n'
        "        after, optimizer = training.adam_step("
        in transformed
    )
    assert '"optimizer_updates": 0' in transformed
    assert "first_tick_nonzero_gradient_leaf_set_exact" in transformed
    assert "SOURCE_COMPLETED_UPDATES = 476" in transformed
    assert "--hardware-authorized" not in transformed
    assert '"robot_clearance": False' in transformed


def test_runner_requires_explicit_diagnostic_flags(monkeypatch, tmp_path: Path) -> None:
    module = load_module(RUNNER, "winner_v58a_runner_test")
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


def test_contract_freezes_zero_update_attribution_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["diagnostic"] == {
        "all_original_guard_predicates_reported": True,
        "environments": 80,
        "optimizer_updates": 0,
        "rollout_update_index": 476,
        "source_completed_updates": 476,
        "ticks_per_environment": 250,
        "would_complete_update": 477,
    }
    assert value["authority"]["retry_authorized"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert len(value["interruption"]["snapshot_chain"]) == 22


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
    builder = load_module(BUILDER, "winner_v58a_builder_manifest_test")
    transformed, receipts = builder.transformed_source()
    assert hashlib.sha256(transformed.encode()).hexdigest() == value["transformation"][
        "transformed_source_sha256"
    ]
    assert receipts == value["transformation"]["replacements"]
