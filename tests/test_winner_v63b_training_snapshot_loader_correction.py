from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v63b_training_snapshot_loader_correction.py"
RUNNER = ROOT / "tools/run_winner_v63b_training_snapshot_loader_correction.py"
BASE_RUNNER = ROOT / "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
INVALID = ROOT / "outputs/analysis/winner_v63_persistent_teacher_conflict_invalid_invocation.json"


def test_v63b_sources_compile() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_v63b_builder_freezes_one_loader_fragment(tmp_path: Path) -> None:
    output = tmp_path / "v63b.json"
    markdown = tmp_path / "v63b.md"
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
    correction = value["correction"]
    assert correction["identity"] == (
        "WINNER_V63B_EXACT_TRAINING_SNAPSHOT_LOADER_CORRECTION"
    )
    assert correction["replacement_count"] == 1
    assert correction[
        "objective_rollout_gradient_adam_classification_or_authority_change"
    ] is False
    assert correction["frozen_runner_lf_sha256"] == hashlib.sha256(
        BASE_RUNNER.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    assert correction["invalid_invocation"]["sha256"] == hashlib.sha256(
        INVALID.read_bytes()
    ).hexdigest()
    assert value["frozen_execution"]["committed_optimizer_updates"] == 0
    assert markdown.is_file()


def test_v63b_runner_executes_only_the_frozen_correction() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "source.count(OLD_FRAGMENT) != 1" in source
    assert "corrected_source_sha256" in source
    assert "winner_v22_normalized_predictor_v2.load_snapshot" not in source
    assert "snapshot = v22v2.load_snapshot(checkpoint_path)" in source
    assert "--conflict-attribution-authorized" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
