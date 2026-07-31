from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t113_preregistration_when_present() -> None:
    path = ANALYSIS / "t113_always_on_trainthrough_hosted_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert value["preregistered_contract_sha256"] == canonical_sha256(basis)
    assert value["status"] == (
        "PREREGISTERED_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == []
    assert value["training"]["forward_path"] == (
        "negative_adapter_location_always_on"
    )
    assert value["training"]["actor_trainable_groups"] == [
        "negative_adapter_location"
    ]
    assert value["training"]["policy_abi_change"] is False
    assert value["post_training"]["both_checkpoint_persistence_required"]
    assert value["authority"]["checkpoint_selection"] is False
