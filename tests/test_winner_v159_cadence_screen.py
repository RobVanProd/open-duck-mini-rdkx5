from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
COMPOSER = ROOT / "tools/compose_winner_v159_cadence_evaluator.py"


def load_composer():
    spec = importlib.util.spec_from_file_location(
        "compose_winner_v159_cadence_evaluator", COMPOSER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v159_composition_is_default_off() -> None:
    module = load_composer()
    source = module.SOURCE.read_text(encoding="utf-8")
    composed = module.compose(source)
    assert "phase_frequency_factor: float = 1.0" in composed
    assert (
        'state.info["imitation_i"] += config.phase_frequency_factor'
        in composed
    )
    restored = composed.replace(
        "    phase_frequency_factor: float = 1.0\n", ""
    ).replace(
        '            state.info["imitation_i"] += '
        "config.phase_frequency_factor\n",
        '            state.info["imitation_i"] += 1\n',
    ).replace(
        '        "phase_frequency_factor": float(\n'
        "            config.phase_frequency_factor\n"
        "        ),\n",
        "",
    )
    assert restored == source


def test_v159_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v159_cadence_screen_preregistration.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "8f2cbd258ad974d3fe82c561e68f18222e9237ade5de081c24eb02e0cd561408"
    )
    assert result["status"] == "PREREGISTERED_WINNER_V159_CADENCE_SCREEN"
    assert result["failed_checks"] == []
    assert result["matrix"]["cells"] == 1
    assert result["matrix"]["row"]["phase_frequency_factor"] == 0.95
    assert result["matrix"]["row"]["phase_frequency_factor_offset"] == -0.05
    assert result["authority"]["training"] is False
