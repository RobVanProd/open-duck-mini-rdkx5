from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"
PREREG = ROOT / "outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v29_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_constants_match_selected_mechanism() -> None:
    module = load()
    assert module.ROLLOUT_UPDATE_INDEX == 200
    assert module.COMPOSITION_TOLERANCE == 4.0e-6
    assert module.GRAPH_TOLERANCE == 1.0e-7
    assert module.v29.PREFIX_TICKS == 8
    assert module.v29.RIGHT_PITCH_ACTION_INDICES == (11, 12, 13)
    assert module.v29.EXPECTED_ANCHOR_ELEMENTS == 384


def test_runner_validates_frozen_contract_when_present() -> None:
    if not PREREG.exists():
        return
    module = load()
    module.validate_contract(json.loads(PREREG.read_text(encoding="utf-8")))


def test_runner_requires_both_offline_authority_flags(monkeypatch, tmp_path) -> None:
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
            "--output",
            str(tmp_path / "result.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_contains_no_optimizer_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "optimizer_updates\": 0" in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert "ssh" not in source.lower()
