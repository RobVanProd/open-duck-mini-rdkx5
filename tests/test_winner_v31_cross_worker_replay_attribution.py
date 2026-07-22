from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v31_cross_worker_replay_attribution.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v31_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_float32_ulp_distance_is_exact() -> None:
    module = load()
    assert module.float32_ulp_distance(1.0, 1.0) == 0
    assert module.float32_ulp_distance(1.0, 1.0000001192092896) == 1
    with pytest.raises(ValueError, match="finite nonnegative"):
        module.float32_ulp_distance(-1.0, 1.0)


def test_attribution_constants_are_frozen() -> None:
    module = load()
    assert module.MAX_ULP_DISTANCE == 8
    assert module.MINIMUM_IMPROVEMENT_TO_REPLAY_DELTA_RATIO == 10_000.0
    assert module.REPLAY_CHECKS == (
        "exact_v29_anchor_loss_gradient_and_scale_reproduced",
        "exact_v29_update_200_batch_reproduced",
    )


def test_runner_has_no_simulation_or_optimizer_import() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    assert "mujoco" not in imported_roots
    assert "jax" not in imported_roots
    assert "adam_step" not in source
    assert "--saved-result-only-attribution-authorized" in source
