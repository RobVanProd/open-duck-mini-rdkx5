from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def test_t12_preregistration_is_canonical_and_zero_training() -> None:
    value = json.loads(
        (
            ANALYSIS / "t12_response_prefix_com_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: value[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playground",
            "candidate",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    assert canonical_sha256(basis) == value[
        "preregistered_contract_sha256"
    ]
    assert value["matrix"] == {
        "checkpoints": 2,
        "fits": ["p30", "p31_34"],
        "commands_x_m_s": [0.074, 0.077, 0.08],
        "torso_com_offset_m": [-0.05, 0.0, 0.0],
        "seed": 167931544,
        "ticks": 600,
        "frequency_hz": 50,
        "formal_cells": 12,
    }
    assert value["authority"]["optimizer_steps"] == 0
    assert value["authority"]["hosted_or_colab_compute"] is False
    assert value["authority"]["robot_or_rdk_access"] is False
    assert value["execution_now"] == {
        "simulator_behavior_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }


def test_t12_auditor_is_independent_of_runner() -> None:
    source = (
        ROOT / "tools" / "audit_t12_response_prefix_com_screen.py"
    ).read_text(encoding="utf-8")
    assert "run_" + "t12_response_prefix_com_screen" not in source
