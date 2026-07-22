from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v24_baseline_anchored_training_preregistration.json"
WORKFLOW = ROOT / ".github/workflows/winner-v24-baseline-anchored-training.yml"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_TRAINING"
    assert value["decision"] == "AUTHORIZE_ONE_100_UPDATE_BASELINE_ANCHORED_ARM_ONLY"
    assert value["frozen_training"]["source_optimizer_count"] == 100
    assert value["frozen_training"]["continuation_optimizer_updates"] == 100
    assert value["frozen_training"]["persistent_checkpoints"] == {"half": 150, "final": 200}
    assert value["single_change"]["flat_transport_equation_used"] is False
    assert value["authority"]["formal_support_gate_authorized"] is False


def test_workflow_is_dormant_until_preregistration_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v24_baseline_anchored_training_preregistration.json" in trigger
    assert "--baseline-anchored-training-authorized" in source
    assert "--hardware-authorized" not in source
