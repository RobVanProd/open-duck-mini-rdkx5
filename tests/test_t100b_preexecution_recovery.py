from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t100_preexecution_attribution_is_optimizer_zero() -> None:
    result = json.loads(
        (ANALYSIS / "t100_preexecution_hold_attribution.json").read_text(
            encoding="utf-8"
        )
    )
    assert result["status"] == "PASS_T100_PREEXECUTION_HOLD_ATTRIBUTION"
    assert result["failed_checks"] == []
    assert result["interpretation"]["optimizer_started"] is False
    assert result["interpretation"]["simulator_training_started"] is False
    assert result["interpretation"]["hosted_training_attempt_consumed"] is False


def test_t100b_driver_captures_base_dispatch_before_replacement() -> None:
    text = (
        ROOT / "tools" / "colab_t100_hidden_expert_continuation.py"
    ).read_text(encoding="utf-8")
    capture = text.index("_BASE_RUNNER_COMMAND = base.runner_command")
    use = text.index("command = _BASE_RUNNER_COMMAND(")
    replacement = text.index("base.runner_command = runner_command")
    assert capture < use < replacement


def test_t100c_wrapper_changes_only_frozen_command_dispatch() -> None:
    text = (
        ROOT / "tools" / "colab_t100c_original_driver_wrapper.py"
    ).read_text(encoding="utf-8")
    assert "_BASE_RUNNER_COMMAND = frozen_t100.base.runner_command" in text
    assert "frozen_t100.runner_command = corrected_runner_command" in text
    assert "return frozen_t100.main()" in text
    assert "train" not in text.lower()
    assert "reward" not in text.lower()
