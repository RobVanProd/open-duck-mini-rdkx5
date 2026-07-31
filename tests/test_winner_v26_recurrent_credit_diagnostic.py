from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v26_recurrent_credit_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v26_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_population_horizon_and_counts_are_frozen() -> None:
    module = load()
    assert module.SOURCE_UPDATE == 100
    assert module.CANDIDATES == (("half", 150), ("final", 200))
    assert len(module.CONFIGURATION_IDS) == 10
    assert module.BASE_PREFIX_TICKS == 20
    assert module.RECURRENT_HORIZON_TICKS == 32
    assert module.REGRESSION_FRACTION_THRESHOLD == 0.75
    assert module.MINIMUM_MEDIAN_LEAD_TICKS == 1.0
    assert module.EXPECTED_BASE_TRAJECTORIES == 20
    assert module.EXPECTED_CANDIDATE_BRANCHES == 40
    assert module.EXPECTED_BRANCH_ROLLOUTS == 80


def test_branch_comparison_rederives_failure_lead() -> None:
    module = load()
    source = {
        "attempted_ticks": 32,
        "terminal_absolute_tick": None,
        "actions": [[0.0] * 14 for _ in range(32)],
        "hidden_outputs": [[0.0] * 64 for _ in range(32)],
        "pitch_rad": [0.01] * 32,
    }
    candidate = {
        "attempted_ticks": 9,
        "terminal_absolute_tick": 28,
        "actions": [[0.1] * 14 for _ in range(9)],
        "hidden_outputs": [[0.2] * 64 for _ in range(9)],
        "pitch_rad": [0.02] * 9,
    }
    result = module.compare_branches(source, candidate)
    assert result["common_attempted_ticks"] == 9
    assert result["initial_action_changed"] is True
    assert result["candidate_terminates_before_source"] is True
    assert result["candidate_failure_lead_ticks"] == 24


def test_aggregate_requires_both_candidates() -> None:
    module = load()
    rows = []
    for label, _ in module.CANDIDATES:
        for index in range(20):
            rows.append(
                {
                    "candidate": label,
                    "comparison": {
                        "initial_action_changed": True,
                        "candidate_terminates_before_source": index < 15,
                        "candidate_failure_lead_ticks": 2 if index < 15 else 0,
                    },
                }
            )
    result = module.aggregate_candidates(rows)
    assert result["half"]["regression_fraction"] == 0.75
    assert result["final"]["regression_fraction"] == 0.75
    assert result["half"]["meets_frozen_post_prefix_regression_rule"] is True
    assert result["final"]["meets_frozen_post_prefix_regression_rule"] is True


def test_runner_is_zero_update_cpu_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_steps": 0' in source
    assert "training.adam_step(" not in source
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
    assert "RECURRENT_HORIZON_TICKS = 32" in source
    assert "candidate_terminates_before_source" in source
