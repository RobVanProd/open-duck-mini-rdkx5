from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "training"))

import winner_v147_head_only_dagger as v147  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v147_preregisters_only_labeled_location_columns() -> None:
    prereg = load("winner_v147_head_only_dagger_cpu_preregistration.json")
    assert sha256(
        "winner_v147_head_only_dagger_cpu_preregistration.json"
    ) == "fbf497103ed758cee5d12c63d92cc659b9d6a625d4d9d7e126d928e7deebe00f"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V147_HEAD_ONLY_DAGGER_CPU_CONTRACT"
    )
    assert prereg["failed_checks"] == []
    assert prereg["mechanism"]["trainable_columns"] == [
        0,
        1,
        3,
        7,
        8,
        10,
        13,
    ]
    assert len(prereg["mechanism"]["trainable_leaves"]) == 2
    assert prereg["optimizer"]["updates"] == 2
    assert prereg["optimizer"]["search_or_retry"] is False
    assert prereg["authority"]["behavior"] is False


def test_v147_gradient_mask_freezes_trunk_and_unlabeled_columns() -> None:
    ones_bias = jnp.ones((14,), dtype=jnp.float32)
    ones_adapter = jnp.ones((64, 14), dtype=jnp.float32)
    ones_residual = jnp.ones((128, 14), dtype=jnp.float32)
    grads = {
        "params": {
            "adapter_location": {
                "bias": ones_bias,
                "kernel": ones_adapter,
            },
            "residual_location": {
                "bias": ones_bias,
                "kernel": ones_residual,
            },
            "residual_trunk": {
                "kernel": jnp.ones((115, 512), dtype=jnp.float32),
            },
            "scale_logits": {
                "bias": ones_bias,
                "kernel": ones_residual,
            },
        }
    }
    masked = v147.mask_head_gradients(grads)
    labeled = np.asarray(v147.LABELED_JOINTS)
    unlabeled = np.asarray(
        [index for index in range(14) if index not in v147.LABELED_JOINTS]
    )
    for name in v147.TRAINABLE_HEADS:
        layer = masked["params"][name]
        assert np.all(np.asarray(layer["bias"])[labeled] == 1)
        assert np.all(np.asarray(layer["bias"])[unlabeled] == 0)
        assert np.all(np.asarray(layer["kernel"])[:, labeled] == 1)
        assert np.all(np.asarray(layer["kernel"])[:, unlabeled] == 0)
    assert np.count_nonzero(
        np.asarray(masked["params"]["residual_trunk"]["kernel"])
    ) == 0
    assert np.count_nonzero(
        np.asarray(masked["params"]["scale_logits"]["kernel"])
    ) == 0
