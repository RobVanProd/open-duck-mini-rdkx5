from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v28_prefix_joint_group_causal_screen.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v28_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_groups_partition_all_14_actions() -> None:
    module = load()
    indices = [index for group in module.GROUPS.values() for index in group]
    assert sorted(indices) == list(range(14))
    assert len(indices) == len(set(indices))
    assert module.ARMS == (
        "CONTROL", "LEFT_LATERAL", "LEFT_PITCH_CHAIN", "HEAD",
        "RIGHT_LATERAL", "RIGHT_PITCH_CHAIN",
    )


def test_counts_and_threshold_are_frozen() -> None:
    module = load()
    assert module.REPAIR_TICKS == 8
    assert module.ABSOLUTE_END_TICK == 52
    assert module.MINIMUM_RECOVERY_GAIN == 0.25
    assert module.EXPECTED_PREFIX_ARMS == 240
    assert module.EXPECTED_RECOVERY_ROLLOUTS == 480
    assert module.CONTROL_REPLAY_POSE_ATOL_RAD == 1.0e-12


def test_unique_group_selection_rule() -> None:
    module = load()
    rows = []
    for label, _ in module.CANDIDATES:
        for arm in module.ARMS:
            recovered = 8 if arm == "CONTROL" else (15 if arm == "LEFT_PITCH_CHAIN" else 10)
            for index in range(20):
                rows.append(
                    {
                        "candidate": label,
                        "arm": arm,
                        "comparison": {
                            "source_recovers": index < recovered,
                            "source_survival_lead_ticks": 1 if index < recovered else 0,
                        },
                    }
                )
    _, selected = module.aggregate_screen(rows)
    assert selected == "LEFT_PITCH_CHAIN"


def test_runner_is_zero_update_cpu_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_steps": 0' in source
    assert "training.adam_step(" not in source
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
