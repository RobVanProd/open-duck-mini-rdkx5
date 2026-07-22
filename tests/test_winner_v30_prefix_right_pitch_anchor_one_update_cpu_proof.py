from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v30_prefix_right_pitch_anchor_one_update_cpu_proof.py"
PREREG = ROOT / "outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v30_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_one_update_constants_are_exact() -> None:
    module = load()
    assert module.ROLLOUT_UPDATE_INDEX == 200
    assert module.SOURCE_OPTIMIZER_COUNT == 200
    assert module.RESULT_OPTIMIZER_COUNT == 201
    assert float(module.FROZEN_ANCHOR_SCALE) == 197.3112030029297


def test_runner_validates_contract_when_present() -> None:
    if not PREREG.exists():
        return
    module = load()
    module.validate_contract(json.loads(PREREG.read_text(encoding="utf-8")))


def test_runner_requires_exact_authority_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path / "fit.json"),
            "--v22-training-work-root",
            str(tmp_path),
            "--v24-training-work-root",
            str(tmp_path),
            "--work-root",
            str(tmp_path / "work"),
            "--output",
            str(tmp_path / "result.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_has_exactly_one_adam_call_and_no_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert source.count("training.adam_step(") == 1
    assert "--one-update-prefix-right-pitch-anchor-proof-authorized" in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert "ssh" not in source.lower()
