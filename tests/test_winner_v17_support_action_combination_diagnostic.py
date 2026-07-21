from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v17_support_action_combination_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v17_combination", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_interventions_are_complete_nonempty_subsets_plus_baseline() -> None:
    module = load()
    assert [row["id"] for row in module.INTERVENTIONS] == [
        "BASELINE",
        "HIP_MAG_NEG",
        "KNEE_POS",
        "ANKLE_POS",
        "HIP_NEG_KNEE_POS",
        "HIP_NEG_ANKLE_POS",
        "KNEE_POS_ANKLE_POS",
        "HIP_NEG_KNEE_POS_ANKLE_POS",
    ]
    subsets = {
        tuple(row["axis"])
        for row in module.INTERVENTIONS[1:]
    }
    assert len(subsets) == 7
    assert {len(row) for row in subsets} == {1, 2, 3}


def test_runner_is_cpu_diagnostic_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
    assert "diagnostic_cells\"] != 192" in source
