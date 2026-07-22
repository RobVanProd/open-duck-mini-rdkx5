from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v27_early_prefix_recovery_scan.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v27_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scan_population_is_frozen() -> None:
    module = load()
    assert module.CANDIDATES == (("half", 150), ("final", 200))
    assert module.FORK_TICKS == (0, 4, 8, 12, 16, 20)
    assert module.ABSOLUTE_END_TICK == 52
    assert module.TICK0_RECOVERY_FRACTION == 1.0
    assert module.TICK20_MAX_RECOVERY_FRACTION == 0.25
    assert module.EXPECTED_CANDIDATE_PREFIXES == 40
    assert module.EXPECTED_FORKS == 240
    assert module.EXPECTED_BRANCH_ROLLOUTS == 720


def test_recovery_comparison_is_exact() -> None:
    module = load()
    candidate = {"terminal_absolute_tick": 30, "initial_action": [0.1] * 14}
    source = {"terminal_absolute_tick": 36, "initial_action": [0.0] * 14}
    value = module.compare_recovery(candidate, source)
    assert value == {
        "source_recovers": True,
        "source_survival_lead_ticks": 6,
        "initial_action_delta_linf": 0.1,
        "initial_action_changed": True,
    }


def test_support_terminal_is_right_censored_at_tick_52() -> None:
    module = load()
    assert module.right_censor_terminal(None) is None
    assert module.right_censor_terminal(57) is None
    assert module.right_censor_terminal(52) is None
    assert module.right_censor_terminal(51) == 51


def test_aggregate_lock_in_rule() -> None:
    module = load()
    rows = []
    for label, _ in module.CANDIDATES:
        for tick in module.FORK_TICKS:
            for configuration in module.CONFIGURATION_IDS:
                for plant in ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"):
                    rows.append(
                        {
                            "candidate": label,
                            "configuration_id": configuration,
                            "plant": plant,
                            "fork_tick": tick,
                            "comparison": {
                                "source_recovers": tick < 20,
                                "source_survival_lead_ticks": 2 if tick < 20 else 0,
                            },
                        }
                    )
    value = module.aggregate_scan(rows)
    assert value["half"]["by_fork_tick"]["0"]["recovery_fraction"] == 1.0
    assert value["final"]["by_fork_tick"]["20"]["recovery_fraction"] == 0.0
    assert value["half"]["meets_frozen_early_state_lock_in_rule"] is True
    assert value["final"]["meets_frozen_early_state_lock_in_rule"] is True


def test_runner_is_zero_update_cpu_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_steps": 0' in source
    assert "training.adam_step(" not in source
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
