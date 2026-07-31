from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v55b_native_reset_quantization_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v55b_native_reset_quantization.py"
PREREG = ROOT / "outputs/analysis/winner_v55b_native_reset_quantization_preregistration.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v55b_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_compile_and_have_no_training_or_hardware_path() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "mujoco.mj_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source


def test_runner_requires_explicit_cpu_attribution_flags(
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


def test_preregistration_freezes_native_reset_population_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["frozen_attribution"]["rows"] == 30
    assert value["frozen_source"]["raw_unique_reset_inputs"] == 15
    assert value["execution_now"]["simulator_steps"] == 0
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
