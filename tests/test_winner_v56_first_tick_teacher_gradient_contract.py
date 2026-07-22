from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v56_first_tick_teacher_gradient_contract.py"
RUNNER = ROOT / "tools/run_winner_v56_first_tick_teacher_gradient_contract.py"
MECHANISM = ROOT / "patches/winner_v56_first_tick_teacher_mapping.py"
CONTRACT = ROOT / "outputs/analysis/winner_v56_first_tick_teacher_gradient_contract.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v56_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_compile_and_have_no_optimizer_or_hardware_path() -> None:
    for path in (BUILDER, RUNNER, MECHANISM):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "mujoco.mj_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source


def test_runner_requires_explicit_cpu_gradient_flags(
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


def test_default_off_composition_is_bit_exact() -> None:
    sys_path = str(ROOT / "patches")
    import sys

    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    import winner_v56_first_tick_teacher_mapping as mechanism

    baseline = jnp.asarray(np.float32(3.25))
    reset = jnp.asarray(np.float32(0.75))
    disabled = mechanism.combine_objective(baseline, reset, enabled=False)
    enabled = mechanism.combine_objective(baseline, reset, enabled=True)
    assert np.array_equal(np.asarray(disabled), np.asarray(baseline))
    assert float(enabled) > float(baseline)


def test_contract_freezes_exact_objective_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["objective"]["total_rows"] == 44
    assert value["objective"]["selected_elements"] == 616
    assert value["objective"]["scale"] == 136.35153198242188
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized"] is False


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
