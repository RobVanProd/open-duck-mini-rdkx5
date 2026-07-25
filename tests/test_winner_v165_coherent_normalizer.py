from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from training.winner_v165_coherent_normalizer_state import (
    compose_coherent_normalizer,
    int_to_uint64_dict,
    normalizer_consistency_error,
    uint64_dict_to_int,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalizer(count: int, mean: float, std: float) -> dict:
    return {
        "count": int_to_uint64_dict(count),
        "mean": {"state": np.asarray([mean], dtype=np.float32)},
        "std": {"state": np.asarray([std], dtype=np.float32)},
        "std_eps": np.asarray(0.0, dtype=np.float32),
        "summed_variance": {
            "state": np.asarray([std * std * count], dtype=np.float32)
        },
    }


def test_v165_coherent_normalizer_matches_deployed_interpolation() -> None:
    source = normalizer(100, 1.0, 2.0)
    proposal = normalizer(132, 5.0, 6.0)
    accepted = compose_coherent_normalizer(source, proposal, 1.0 / 32.0)
    assert uint64_dict_to_int(accepted["count"]) == 101
    np.testing.assert_array_equal(
        accepted["mean"]["state"], np.asarray([1.125], dtype=np.float32)
    )
    np.testing.assert_array_equal(
        accepted["std"]["state"], np.asarray([2.125], dtype=np.float32)
    )
    assert normalizer_consistency_error(accepted) <= 1.0e-7


def test_v165_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v165_coherent_normalizer_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "d4c890bb07f65b0156288f634b4e8546bf2e8c51b36b38422bbe7a6fce15c312"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V165_COHERENT_NORMALIZER"
    )
    assert value["failed_checks"] == []
    assert value["state_rule"]["block_iterations"] == 28
    assert value["state_rule"]["accepted_alpha"] == 1.0 / 28.0
    assert value["state_rule"]["alpha_or_block_retry"] is False
    assert value["authority"]["hosted_training"] is False


def test_v165_result_when_present() -> None:
    path = ANALYSIS / "winner_v165_coherent_normalizer_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V165_COHERENT_NORMALIZER",
        "HOLD_WINNER_V165_COHERENT_NORMALIZER",
    }
    assert value["authority"]["training"] is False
    assert value["authority"]["hosted_training"] is False
    if value["status"].startswith("PASS_"):
        assert value["failed_checks"] == []
        assert value["decision"] == (
            "EARN_V166_28_ITERATION_TRAINER_INTEGRATION_CPU_SMOKE"
        )
    else:
        assert value["decision"] == (
            "CLOSE_FEASIBILITY_PRESERVING_BLOCK_CONTINUATION_NO_RETRY"
        )
