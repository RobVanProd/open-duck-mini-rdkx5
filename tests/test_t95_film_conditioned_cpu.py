from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t95_film_conditioned_cpu_preregistration_v3.json"
)
RESULT = (
    ROOT / "outputs" / "analysis" / "t95_film_conditioned_cpu_result.json"
)


def test_t95_preregistration_is_cpu_only_and_distinct() -> None:
    if not PREREG.exists():
        pytest.skip("T95 preregistration has not run")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T95_FILM_CONDITIONED_CPU_CONTRACT_V3"
    )
    assert value["failed_checks"] == []
    assert value["architecture_contract"]["new_actor_parameters"] == [
        "context_film_scale/kernel"
    ]
    assert value["architecture_contract"]["source_action_head_rank"] == 14
    assert value["context_observability"][
        "negative_com_contexts_are_unique"
    ]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t95_result_never_authorizes_hardware() -> None:
    if not RESULT.exists():
        pytest.skip("T95 CPU result has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"]["hosted_or_colab_compute"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["gate5_authorized"]
    assert not value["authority"]["rdkx5_or_robot_access"]
    assert not value["authority"]["hosted_training_authorized"]
