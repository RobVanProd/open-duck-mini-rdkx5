from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v24_symmetric_failure_cpu_contract.json"
WORKFLOW = ROOT / ".github/workflows/winner-v24-symmetric-failure-cpu-contract.yml"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_SYMMETRIC_FAILURE_OBJECTIVE_PROOF_ONLY"
    assert value["objective"]["settled_success_bonus"] == 250.0
    assert value["objective"]["roll_pitch_failure_penalty"] == -250.0
    assert value["objective"]["reads_hidden_configuration"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["future_execution"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized"] is False


def test_workflow_is_dormant_until_contract_commit() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v24_symmetric_failure_cpu_contract.json" in trigger
    assert "--zero-update-objective-proof-authorized" in source
    assert "--hardware-authorized" not in source
