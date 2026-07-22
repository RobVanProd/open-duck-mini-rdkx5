from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_contract.json"
WORKFLOW = ROOT / ".github/workflows/winner-v24-baseline-anchored-one-update-cpu-proof.yml"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_EXACT_ONE_BASELINE_ANCHORED_OPTIMIZER_UPDATE_ONLY"
    assert value["source_checkpoint"]["optimizer_count"] == 100
    assert value["execution_future"]["optimizer_updates"] == 1
    assert value["execution_future"]["formal_support_cells"] == 0
    assert value["authority"]["training_authorized"] is False


def test_workflow_is_dormant_until_contract_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v24_baseline_anchored_one_update_cpu_contract.json" in trigger
    assert "--one-update-baseline-anchored-proof-authorized" in source
    assert "--hardware-authorized" not in source
