from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value: Any, hash_key: str) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t75_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t75_signed_core_secant_condition7_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T75_SIGNED_CORE_SECANT_CONDITION7"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["matrix"]["both_checkpoints_required"] is True
    assert value["decision_rule"]["no_hosted_run_earned"] is True
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t75_result_obeys_decision_when_present() -> None:
    path = ANALYSIS / "t75_signed_core_secant_condition7_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T75_SIGNED_CORE_SECANT_CONDITION7"
        assert (
            value["decision"]
            == "EARN_T76_SIGNED_CORE_SECANT_NOMINAL_PREREGISTRATION"
        )
    else:
        assert value["status"] == "HOLD_T75_SIGNED_CORE_SECANT_CONDITION7"
        assert value["decision"] == "CLOSE_SIGNED_CORE_SECANT_FAMILY"
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
