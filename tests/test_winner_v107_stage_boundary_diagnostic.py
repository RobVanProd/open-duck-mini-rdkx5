from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_winner_v107_stage_boundary_diagnostic import (  # noqa: E402
    cpu_environment_exact,
    stage_decision,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(flags: list[bool]) -> list[dict[str, object]]:
    return [
        {
            "id": f"C{index}",
            "cumulative_optimizer_steps": index,
            "all_four_cells_pass": passed,
        }
        for index, passed in enumerate(flags)
    ]


def test_v107_preregistration_is_the_exact_20_cell_diagnostic() -> None:
    path = (
        ROOT / "outputs/analysis/winner_v107_stage_boundary_preregistration.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert digest(path) == (
        "740fb79bda4be79e2d1d7739b917035bdb4c326f49142bd975fc1acdbf24eec8"
    )
    assert payload["status"] == (
        "PREREGISTERED_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
    )
    assert payload["failed_checks"] == []
    assert payload["matrix"]["cells"] == 20
    assert payload["matrix"]["sha256"] == (
        "0ee5b189aaba40c70e4f34b4aec00118ac5923536fe78bf56c61c085bed3704d"
    )
    assert len(payload["checkpoints"]) == 5
    assert payload["authority"]["formal_behavior_cells_authorized"] == 20
    assert payload["authority"]["hosted_training_authorized"] is False


def test_cpu_detection_uses_backend_and_platform_not_rendered_name() -> None:
    assert cpu_environment_exact("cpu", ["cpu"])
    assert cpu_environment_exact("cpu", ["cpu", "cpu"])
    assert not cpu_environment_exact("gpu", ["cpu"])
    assert not cpu_environment_exact("cpu", ["gpu"])
    assert not cpu_environment_exact("cpu", [])


def test_stage_decision_localizes_only_the_first_pass_to_fail_transition() -> None:
    initial = stage_decision(rows([False, False, False]))
    assert initial["status"] == "EXPANDED_INITIAL_FAILED"
    assert initial["selected_causal_boundary"] == (
        "EXPANSION_EXPORT_OR_CALIBRATION_PREFIX_INTEGRATION"
    )

    transition = stage_decision(rows([True, True, False, False]))
    assert transition == {
        "status": "FIRST_TRAINING_TRANSITION_LOCATED",
        "first_passing_checkpoint": "C1",
        "first_failing_checkpoint_after_pass": "C2",
        "selected_causal_boundary": "C1_TO_C2",
    }

    no_collapse = stage_decision(rows([True, True, True]))
    assert no_collapse == {
        "status": "NO_NOMINAL_COLLAPSE_AT_FROZEN_BOUNDARIES",
        "first_passing_checkpoint": "C0",
        "first_failing_checkpoint_after_pass": None,
        "selected_causal_boundary": None,
    }
