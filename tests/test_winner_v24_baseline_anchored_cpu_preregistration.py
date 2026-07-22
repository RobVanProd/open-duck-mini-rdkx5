from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_cpu_contract.json"
WORKFLOW = ROOT / ".github/workflows/winner-v24-baseline-anchored-cpu-contract.yml"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_BASELINE_ANCHORED_OBJECTIVE_PROOF_ONLY"
    assert value["objective"]["baseline_gae_reconstruction"] is False
    assert value["attribution_boundary"]["old_threshold_relaxed"] is False
    assert value["attribution_boundary"]["old_result_rewritten"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["future_execution"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized"] is False


def test_workflow_is_dormant_until_contract_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v24_baseline_anchored_cpu_contract.json" in trigger
    assert "--zero-update-baseline-anchored-proof-authorized" in source
    assert "--hardware-authorized" not in source
