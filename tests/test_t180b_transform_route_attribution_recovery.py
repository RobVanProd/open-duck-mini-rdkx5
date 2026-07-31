from __future__ import annotations

import pytest

from tools.build_t180b_transform_route_attribution_preregistration import (
    select_block,
)


def _block(condition: str, checkpoint: str, fit: str) -> dict:
    return {
        "condition_id": condition,
        "checkpoint_id": checkpoint,
        "fit_id": fit,
    }


def test_select_block_requires_condition_checkpoint_and_fit() -> None:
    blocks = [
        _block("FLOOR_FRICTION_LO", "half", "p30"),
        _block("TORSO_COM_Z_POS", "half", "p30"),
    ]
    result = select_block(
        blocks,
        condition_id="TORSO_COM_Z_POS",
        checkpoint_id="half",
        fit_id="p30",
    )
    assert result["condition_id"] == "TORSO_COM_Z_POS"


def test_select_block_rejects_nonunique_binding() -> None:
    blocks = [
        _block("TORSO_COM_Z_POS", "half", "p30"),
        _block("TORSO_COM_Z_POS", "half", "p30"),
    ]
    with pytest.raises(RuntimeError, match="not unique"):
        select_block(
            blocks,
            condition_id="TORSO_COM_Z_POS",
            checkpoint_id="half",
            fit_id="p30",
        )
