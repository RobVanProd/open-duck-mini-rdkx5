from __future__ import annotations

import hashlib
import json
import numpy as np
import onnx
from onnx import numpy_helper
from pathlib import Path

from tools.build_winner_v110_pitch_guard_repair import (
    PITCH_INDICES,
    REPAIRED_MARGIN_RAD,
    SOURCE_MARGIN_RAD,
    replace_initializer,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v110_repair_replaces_only_named_initializer() -> None:
    model = onnx.helper.make_model(
        onnx.helper.make_graph(
            [],
            "test",
            [],
            [],
            initializer=[
                numpy_helper.from_array(
                    np.full((1, 14), SOURCE_MARGIN_RAD, dtype=np.float32),
                    name="guard_margin",
                ),
                numpy_helper.from_array(
                    np.asarray([7.0], dtype=np.float32), name="other"
                ),
            ],
        )
    )
    other_before = numpy_helper.to_array(model.graph.initializer[1]).copy()
    replacement = np.full((1, 14), SOURCE_MARGIN_RAD, dtype=np.float32)
    replacement.reshape(-1)[PITCH_INDICES] = REPAIRED_MARGIN_RAD
    replace_initializer(model, "guard_margin", replacement)
    assert np.array_equal(
        numpy_helper.to_array(model.graph.initializer[0]), replacement
    )
    assert np.array_equal(
        numpy_helper.to_array(model.graph.initializer[1]), other_before
    )


def test_v110_frozen_g3_margin_is_stricter_than_g1() -> None:
    assert float(REPAIRED_MARGIN_RAD) == float(np.float32(0.165))
    assert REPAIRED_MARGIN_RAD < SOURCE_MARGIN_RAD
    assert PITCH_INDICES.tolist() == [2, 3, 4, 11, 12, 13]


def test_v110_transform_contract_passes_without_behavior_authority() -> None:
    path = (
        ROOT
        / "outputs/analysis/winner_v110_pitch_guard_transform_contract.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "d48a2c6766f4e0fbd1771e686970d19c3ba93c618c2c8d3b2f64af836b318f5b"
    )
    assert payload["status"] == (
        "PASS_WINNER_V110_PITCH_GUARD_TRANSFORM_CONTRACT"
    )
    assert payload["failed_checks"] == []
    assert len(payload["policies"]) == 2
    assert all(row["pass"] for row in payload["policies"])
    assert all(
        row["changed_initializers"] == ["guard_margin"]
        for row in payload["policies"]
    )
    assert payload["authority"]["behavior_evaluation"] is False
    assert payload["authority"]["gate5"] is False
    assert payload["authority"]["robot_clearance"] is False
