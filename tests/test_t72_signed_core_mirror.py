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


def test_t72_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t72_signed_core_mirror_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T72_SIGNED_CORE_MIRROR"
    assert value["failed_checks"] == []
    assert value["mechanism"]["fixed_alpha"] == -1.0
    assert value["mechanism"]["scalar_sweep"] is False
    assert value["core_initializers"] == [
        "adapter_obs_weight",
        "adapter_hidden_weight",
        "adapter_hidden_bias",
    ]
    assert value["decision_rule"]["hosted_run_earned"] is False
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t72_result_obeys_contract_when_present() -> None:
    path = ANALYSIS / "t72_signed_core_mirror_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["simulator_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert len(value["candidates"]) == 2
    if not value["failed_checks"]:
        assert value["status"] == "PASS_T72_SIGNED_CORE_MIRROR"
        assert (
            value["decision"]
            == "EARN_T73_SIGNED_CORE_MIRROR_CONDITION7_PREREGISTRATION"
        )
        assert all(
            set(row["transform"]["changed_initializers"])
            == {
                "adapter_obs_weight",
                "adapter_hidden_weight",
                "adapter_hidden_bias",
            }
            for row in value["candidates"]
        )
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
