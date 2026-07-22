from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v64b_preregistration_name_correction.py"
RUNNER = ROOT / "tools/run_winner_v64b_preregistration_name_correction.py"
INVALID = ROOT / "outputs/analysis/winner_v64_isolated_persistent_teacher_invalid_invocation.json"


def test_v64b_sources_compile_and_transform() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v64b_preregistration_name_correction as builder

    source, digest = builder.corrected_source()
    assert len(digest) == 64
    assert source.count("preregistration[\"v64\"][\"objective\"]") == 1
    assert "contract[\"v64\"][\"objective\"]" not in source


def test_v64b_builder_freezes_exact_two_reference_fragment(tmp_path: Path) -> None:
    output = tmp_path / "v64b.json"
    markdown = tmp_path / "v64b.md"
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output",
            str(output),
            "--markdown",
            str(markdown),
        ],
        cwd=ROOT,
        check=True,
    )
    value = json.loads(output.read_text(encoding="utf-8"))
    correction = value["v64b"]
    assert correction["identity"] == (
        "WINNER_V64B_PREREGISTRATION_LOCAL_NAME_CORRECTION"
    )
    assert correction["replacement_count"] == 1
    assert correction[
        "objective_rollout_gradient_adam_artifact_schema_or_authority_change"
    ] is False
    assert correction["invalid_invocation"]["sha256"] == hashlib.sha256(
        INVALID.read_bytes()
    ).hexdigest()
    assert value["v64"]["execution_future"]["optimizer_updates"] == 1
    assert value["v64"]["authority"]["continuation_training_authorized"] is False
    assert markdown.is_file()


def test_v64b_runner_delegates_to_frozen_v64() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "base.validate_contract(contract)" in source
    assert "base.transformed_source = lambda _value: corrected" in source
    assert "--one-update-authorized" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
