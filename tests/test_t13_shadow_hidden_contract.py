from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import t13_shadow_hidden_eval_adapter as adapter  # noqa: E402


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t13_adapter_is_a_narrow_frozen_t8_patch() -> None:
    source = adapter.patched_source()
    assert adapter.source_bytes()
    assert adapter.patched_source_sha256() == hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()
    assert "response_shadow_policy_hidden: bool = False" in source
    assert "shadow_policy_actions_ignored" in source
    assert "hidden_state[\"h_in\"] = shadow_policy_hidden.copy()" in source


def test_t13_preregistration_is_canonical_and_zero_training() -> None:
    value = json.loads(
        (
            ANALYSIS / "t13_shadow_hidden_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    assert canonical_sha256(basis) == value[
        "preregistered_contract_sha256"
    ]
    assert value["matrix"] == {
        "checkpoints": 2,
        "fits": ["p30", "p31_34"],
        "commands_x_m_s": [0.074],
        "torso_com_offset_m": [-0.05, 0.0, 0.0],
        "seed": 167931544,
        "calibration_ticks": 250,
        "scored_locomotion_ticks": 1,
        "simulator_prefix_cells": 4,
        "scored_behavior_cells": 0,
    }
    assert value["authority"]["optimizer_steps"] == 0
    assert value["authority"]["hosted_or_colab_compute"] is False
    assert value["authority"]["robot_or_rdk_access"] is False
    assert value["execution_now"] == {
        "simulator_prefix_cells": 0,
        "scored_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }


def test_t13_auditor_does_not_import_the_runner() -> None:
    source = (
        TOOLS / "audit_t13_shadow_hidden_contract.py"
    ).read_text(encoding="utf-8")
    assert "run_" + "t13_shadow_hidden_contract" not in source
