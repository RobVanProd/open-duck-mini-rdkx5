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


def test_t11_preregistration_is_canonical_and_zero_execution() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t11_context_action_observability_preregistration.json"
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
            "formal_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    assert canonical_sha256(basis) == value[
        "preregistered_contract_sha256"
    ]
    assert value["formal_contract"]["optimizer_steps"] == 0
    assert value["formal_contract"]["simulator_behavior_cells"] == 0
    assert value["authority"]["hosted_or_colab_compute"] is False
    assert value["authority"]["robot_or_rdk_access"] is False
    assert value["decision_rule"]["partial_results_selection_weight"] == 0
    assert value["execution_now"] == {
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "simulator_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }


def test_t11_auditor_is_independent_of_runner() -> None:
    source = (
        ROOT / "tools" / "audit_t11_context_action_observability.py"
    ).read_text(encoding="utf-8")
    assert "run_" + "t11_context_action_observability" not in source


def test_t11_result_is_canonical_and_closes_action_binding() -> None:
    value = json.loads(
        (
            ANALYSIS / "t11_context_action_observability_result.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item for key, item in value.items() if key != "result_sha256"
    }
    assert canonical_sha256(basis) == value["result_sha256"]
    assert value["status"] == "HOLD_T11_CONTEXT_ACTION_OBSERVABILITY"
    assert value["decision"] == (
        "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
    )
    assert value["failed_checks"] == [
        "coherent_effect_frequency",
        "causal_sequence_effect_frequency",
    ]
    assert value["disjoint_state_coherent_test"][
        "effective_case_fraction"
    ] == 9 / 2048
    assert value["disjoint_causal_sequence_test"][
        "divergent_sequence_fraction"
    ] == 1 / 128
    assert value["execution"] == {
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "simulator_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }


def test_t11_independent_audit_reproduces_the_hold() -> None:
    value = json.loads(
        (
            ANALYSIS
            / "t11_context_action_observability_independent_audit.json"
        ).read_text(encoding="utf-8")
    )
    basis = {
        key: item for key, item in value.items() if key != "audit_sha256"
    }
    assert canonical_sha256(basis) == value["audit_sha256"]
    assert value["status"] == (
        "HOLD_T11_CONTEXT_ACTION_INDEPENDENT_AUDIT"
    )
    assert value["issues"] == [
        "coherent_effect_frequency",
        "causal_sequence_frequency",
    ]
    assert value["coherent_recomputation"][
        "effective_case_fraction"
    ] == 9 / 2048
    assert value["sequence_recomputation"][
        "divergent_sequence_fraction"
    ] == 1 / 128
    assert value["execution"] == {
        "optimizer_steps": 0,
        "hosted_or_colab_compute": 0,
        "simulator_behavior_cells": 0,
        "robot_or_rdk_access": 0,
    }
