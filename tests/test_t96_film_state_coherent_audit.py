from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t96_film_state_coherent_audit_preregistration.json"
)
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t96_film_state_coherent_audit_result.json"
)


def test_t96_preregistration_preserves_t95_thresholds() -> None:
    if not PREREG.exists():
        pytest.skip("T96 preregistration has not run")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T96_FILM_STATE_COHERENT_AUDIT"
    )
    assert value["failed_checks"] == []
    assert value["formal_contract"]["minimum_effect_tick_fraction"] == 0.05
    assert value["formal_contract"][
        "minimum_context_pair_effect_fraction"
    ] == 0.50
    assert value["formal_contract"]["minimum_maximum_action_delta"] == 1e-5
    assert value["execution_now"]["optimizer_steps"] == 0
    assert not value["authority"]["hosted_training"]


def test_t96_result_is_read_only() -> None:
    if not RESULT.exists():
        pytest.skip("T96 result has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]

