from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jax
import numpy as np
import pytest

from training.winner_v164_feasibility_preserving_state import (
    compose_accepted_checkpoint,
    finite_tree,
    interpolate_float_tree,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v164_tree_interpolation_and_state_roles() -> None:
    source = [
        {"mean": np.asarray([1.0], dtype=np.float32)},
        {"weight": np.asarray([0.0, 2.0], dtype=np.float32)},
        {"value": np.asarray([3.0], dtype=np.float32)},
    ]
    proposal = [
        {"mean": np.asarray([9.0], dtype=np.float32)},
        {"weight": np.asarray([4.0, 6.0], dtype=np.float32)},
        {"value": np.asarray([7.0], dtype=np.float32)},
    ]
    accepted = compose_accepted_checkpoint(source, proposal, 0.25)
    np.testing.assert_array_equal(accepted[0]["mean"], source[0]["mean"])
    np.testing.assert_array_equal(
        accepted[1]["weight"], np.asarray([1.0, 3.0], dtype=np.float32)
    )
    np.testing.assert_array_equal(
        accepted[2]["value"], proposal[2]["value"]
    )
    assert finite_tree(accepted)


def test_v164_interpolation_rejects_nonfloating_change() -> None:
    with pytest.raises(ValueError, match="nonfloating"):
        interpolate_float_tree(
            {"value": np.asarray([1], dtype=np.int32)},
            {"value": np.asarray([2], dtype=np.int32)},
            0.5,
        )


def test_v164_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v164_state_coherence_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "ee779c4877beca09f9dd80d15300e47f7c065255ad29e4172d90e5b70a017512"
    )
    assert value["status"] == "PREREGISTERED_WINNER_V164_STATE_COHERENCE"
    assert value["failed_checks"] == []
    assert value["state_rule"]["block_iterations"] == 28
    assert value["state_rule"]["blocks_to_half_export"] == 7
    assert value["state_rule"]["blocks_to_final_export"] == 14
    assert value["state_rule"]["accepted_alpha"] == 1.0 / 28.0
    assert value["state_rule"]["normalizer"] == "source exact and frozen"
    assert value["decision_rule"]["hosted_training_authorized"] is False


def test_v164_result_when_present() -> None:
    path = ANALYSIS / "winner_v164_state_coherence_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V164_STATE_COHERENCE",
        "HOLD_WINNER_V164_STATE_COHERENCE",
    }
    assert value["authority"]["training"] is False
    assert value["authority"]["hosted_training"] is False
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["decision"] == (
            "EARN_V165_FEASIBILITY_PRESERVING_TRAINER_INTEGRATION_CPU_SMOKE"
        )
    else:
        assert value["decision"] == (
            "CLOSE_ACTOR_ONLY_FROZEN_NORMALIZER_STATE_NO_RETRY"
        )


def test_v164_tree_structure_is_stable() -> None:
    source = {"a": np.asarray([1.0], dtype=np.float32)}
    result = interpolate_float_tree(source, source, 0.5)
    assert jax.tree_util.tree_structure(result) == jax.tree_util.tree_structure(
        source
    )
