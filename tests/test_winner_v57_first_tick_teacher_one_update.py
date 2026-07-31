from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v57_first_tick_teacher_one_update_contract.py"
RUNNER = ROOT / "tools/run_winner_v57_first_tick_teacher_one_update.py"
CONTRACT = ROOT / "outputs/analysis/winner_v57_first_tick_teacher_one_update_contract.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v57_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_compile_and_scope_is_exact() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source = RUNNER.read_text(encoding="utf-8")
    assert source.count("training.adam_step(") == 1
    assert "stage2_rollout(" not in source
    assert "mujoco.mj_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source


def test_runner_requires_explicit_one_update_flags(
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
            "--work-root",
            str(tmp_path / "work"),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_contract_freezes_exact_update_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["source"]["optimizer_count"] == 453
    assert value["objective"]["result_optimizer_count"] == 454
    assert value["objective"]["rows"] == 44
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["continuation_training_authorized"] is False


def test_source_manifest_is_exact_when_preregistered() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
