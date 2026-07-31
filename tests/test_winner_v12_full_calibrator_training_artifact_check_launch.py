from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT / "tools/build_winner_v12_full_calibrator_training_artifact_check_launch.py"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v12_artifact_launch", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_arguments(builder) -> dict:
    return {
        "artifact_id": 123,
        "artifact_name": builder.EXPECTED_ARTIFACT_NAME,
        "artifact_digest": f"sha256:{'a' * 64}",
        "artifact_zip_sha256": "a" * 64,
        "training_result_sha256": "b" * 64,
    }


def test_launch_is_fixed_to_original_training_run_and_head() -> None:
    builder = load_builder()
    builder.validate_launch_inputs(**valid_arguments(builder))
    assert builder.EXPECTED_RUN_ID == 29808732634
    assert builder.EXPECTED_RUN_ATTEMPT == 1
    assert builder.EXPECTED_RUN_HEAD_SHA == ("30ba44b2461d0f11da77ebfe42ac30446682c22d")


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("artifact_id", 0),
        ("artifact_name", "wrong"),
        ("artifact_digest", f"sha256:{'c' * 64}"),
    ],
)
def test_launch_rejects_artifact_attribution_drift(key: str, value: object) -> None:
    builder = load_builder()
    arguments = valid_arguments(builder)
    arguments[key] = value
    with pytest.raises(ValueError):
        builder.validate_launch_inputs(**arguments)


def test_workflow_stays_dormant_until_launch_contract_commit() -> None:
    workflow = (
        ROOT
        / ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
    )
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert workflow.name not in trigger
    assert "winner_v12_full_calibrator_training_artifact_check_launch.json" in trigger
    assert "actions/artifacts/${artifact_id}/zip" in source
    assert "--expected-github-artifact-digest" in source
    assert "--formal-gate-authorized" not in source
