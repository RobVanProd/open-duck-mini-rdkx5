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


def test_t74_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t74_signed_core_secant_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T74_SIGNED_CORE_SECANT"
    assert value["failed_checks"] == []
    assert value["mechanism"]["scalar_sweep"] is False
    assert value["mechanism"]["both_endpoints_required"] is True
    assert [
        row["coefficients_s_e1_e2"]
        for row in value["mechanism"]["candidates"]
    ] == [[2, 1, -2], [2, 2, -3]]
    assert value["decision_rule"]["no_hosted_run_earned"] is True
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t74_result_obeys_contract_when_present() -> None:
    path = ANALYSIS / "t74_signed_core_secant_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["simulator_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert len(value["candidates"]) == 2
    if not value["failed_checks"]:
        assert value["status"] == "PASS_T74_SIGNED_CORE_SECANT"
        assert (
            value["decision"]
            == "EARN_T75_SIGNED_CORE_SECANT_CONDITION7_PREREGISTRATION"
        )
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
