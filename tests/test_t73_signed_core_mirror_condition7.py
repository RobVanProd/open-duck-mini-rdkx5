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


def test_t73_preregistration_is_exact_when_present() -> None:
    path = ANALYSIS / "t73_signed_core_mirror_condition7_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T73_SIGNED_CORE_MIRROR_CONDITION7"
    )
    assert value["failed_checks"] == []
    assert value["condition"] == {
        "condition_index": 7,
        "id": "TORSO_COM_X_NEG",
        "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
    }
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"] is True
    assert value["decision_rule"]["no_hosted_run_earned"] is True
    assert (
        canonical_sha256(value, "preregistered_contract_sha256")
        == value["preregistered_contract_sha256"]
    )


def test_t73_result_obeys_decision_when_present() -> None:
    path = ANALYSIS / "t73_signed_core_mirror_condition7_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T73_SIGNED_CORE_MIRROR_CONDITION7"
        assert (
            value["decision"]
            == "EARN_T74_SIGNED_CORE_MIRROR_NOMINAL_PREREGISTRATION"
        )
    else:
        assert value["status"] == "HOLD_T73_SIGNED_CORE_MIRROR_CONDITION7"
        assert value["decision"] == "CLOSE_SIGNED_CORE_MIRROR"
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert (
        canonical_sha256(value, "result_sha256")
        == value["result_sha256"]
    )
