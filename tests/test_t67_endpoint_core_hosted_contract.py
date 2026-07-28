from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t67_preregistration_is_green_when_present() -> None:
    path = ANALYSIS / "t67_endpoint_core_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T67_ENDPOINT_CORE_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["endpoint_strata"] == 8
    assert value["training"]["environments_per_stratum"] == 32
    assert value["training"]["reward_change"] is False
    assert value["training"]["policy_abi_change"] is False
    assert value["training"]["runtime_change"] is False
    assert value["training"]["retry"] is False
    assert value["training"]["resume"] is False
    assert value["post_training"]["both_postupdate_checkpoints_must_pass"]


def test_t67_driver_is_exact_no_retry_two_checkpoint_run() -> None:
    text = (
        ROOT / "tools" / "colab_t67_endpoint_core_continuation.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert '"--winner_t66_endpoint_core_continuation"' in text
    assert '"--winner_t37_freeze_observation_normalizer"' in text
    assert "no-retry path exists" in text
    assert "formal_behavior_cells_executed" in text
