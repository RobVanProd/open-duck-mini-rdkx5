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


def test_t12_recovery_is_narrow_and_keeps_partial_weight_zero() -> None:
    value = json.loads(
        (
            ANALYSIS / "t12_execution_recovery_amendment.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "amendment_contract_sha256"
    }
    assert canonical_sha256(basis) == value[
        "amendment_contract_sha256"
    ]
    assert value["failed_execution"]["completed_cells"] == 3
    assert value["failed_execution"]["decision_weight"] == 0
    assert value["failed_execution"]["selection_use_forbidden"] is True
    assert value["authorized_recovery"]["attempts_exact"] == 1
    assert value["authorized_recovery"]["reuse_partial_v1_forbidden"] is True
    assert value["unchanged_contract"]["decision_rule"] is True
    assert value["unchanged_contract"][
        "partial_results_selection_weight"
    ] == 0
    assert value["execution_now"] == {
        "formal_decision_cells": 0,
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }


def test_t12_result_is_canonical_and_closes_the_mechanism() -> None:
    value = json.loads(
        (
            ANALYSIS / "t12_response_prefix_com_result.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "result_sha256"
    }
    assert canonical_sha256(basis) == value["result_sha256"]
    assert value["status"] == "HOLD_T12_RESPONSE_PREFIX_COM_SCREEN"
    assert value["decision"] == "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
    assert value["failed_checks"] == ["all_cells_green"]
    assert value["summary"]["green_cells"] == 5
    assert value["summary"]["total_cells"] == 12
    assert value["summary"]["worst_rate_excess_rad_s"] == 0.0
    assert value["checks"]["all_com_readbacks_exact"] is True
    assert value["checks"]["all_handoff_chains_exact"] is True
    assert value["execution"] == {
        "hosted_or_colab_compute": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
        "simulator_behavior_cells": 12,
    }


def test_t12_independent_audit_reproduces_the_hold() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t12_response_prefix_com_independent_audit.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item
        for key, item in value.items()
        if key != "audit_sha256"
    }
    assert canonical_sha256(basis) == value["audit_sha256"]
    assert (
        value["status"]
        == "PASS_T12_RESPONSE_PREFIX_COM_INDEPENDENT_AUDIT"
    )
    assert value["decision"] == "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
    assert value["issues"] == []
    assert value["recomputed_green_cells"] == 5
    assert value["recomputed_total_cells"] == 12
    assert value["execution"] == {
        "hosted_or_colab_compute": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
        "simulator_behavior_cells": 0,
    }
