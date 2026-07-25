from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v166_integer_and_fractional_interpolation_math() -> None:
    table = np.asarray([[0.0, 2.0], [4.0, 6.0]], dtype=np.float32)
    lower = table[0]
    upper = table[1]
    np.testing.assert_array_equal(lower + 0.0 * (upper - lower), lower)
    np.testing.assert_array_equal(
        lower + 0.25 * (upper - lower),
        np.asarray([1.0, 3.0], dtype=np.float32),
    )


def test_v166_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "bf9da2c27e801b8942358d0f88d0f7f89954665dbe13cf8e60b50e3996a8279d"
    )
    assert value["status"] == (
        "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 1
    assert value["mechanism"]["factor"] == 0.95
    assert value["authority"]["production_contract_change"] is False
    assert value["authority"]["training"] is False


def test_v166_result_when_present() -> None:
    path = ANALYSIS / "winner_v166_continuous_reference_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V166_CONTINUOUS_REFERENCE",
        "HOLD_WINNER_V166_CONTINUOUS_REFERENCE",
    }
    assert value["authority"]["production_contract_change"] is False
    assert value["authority"]["training"] is False
    if value["status"].startswith("PASS_"):
        assert value["decision"] == (
            "EARN_REVIEWED_CONTINUOUS_REFERENCE_ADAPTER_CONTRACT_DECISION"
        )
    else:
        assert value["decision"] == (
            "CLOSE_CONTINUOUS_REFERENCE_CADENCE_EXPANSION_NO_RETRY"
        )
