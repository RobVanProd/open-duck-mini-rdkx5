from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v12_full_calibrator_training_launch_contract.json"
CLAIM = ANALYSIS / "winner_v12_full_calibrator_training_authorization_claim.json"
RUNNER = ROOT / "tools/run_winner_v12_full_calibrator_training.py"
CPU_RESULT = ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract_result.json"
WORKFLOW = ROOT / ".github/workflows/winner-v12-full-calibrator-training.yml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_launch_authorizes_one_exact_logical_run_only() -> None:
    contract = load()
    assert contract["status"] == (
        "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN"
    )
    assert contract["decision"] == "AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN"
    assert contract["logical_run_id"] == "winner-v12-full-calibrator-seed-120120"
    assert contract["execution_before_launch"] == {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert contract["failed_checks"] == []
    assert contract["checks"] and all(contract["checks"].values())
    assert contract["artifact_policy"]["retry"] is False
    assert "does not authorize" in contract["pass_authorizes_only"]


def test_claim_binds_runner_result_and_exact_work_root() -> None:
    contract = load()
    claim = json.loads(CLAIM.read_text(encoding="utf-8"))
    assert claim == contract["authorization_claim_payload"]
    assert contract["authorization_claim"] == {
        "path": "outputs/analysis/winner_v12_full_calibrator_training_authorization_claim.json",
        "lf_sha256": lf_sha256(CLAIM),
    }
    assert claim["resolved_work_root"] == (
        "/tmp/winner-v12-full-calibrator-training-work"
    )
    assert claim["runner_lf_sha256"] == lf_sha256(RUNNER)
    assert claim["cpu_result_sha256"] == lf_sha256(CPU_RESULT)


def test_workflow_is_one_shot_exact_cpu_and_uploads_recovery() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" not in source
    assert "matrix:" not in source
    assert "codex/winner-v4-response-contract" in source
    assert "- .github/workflows/winner-v12-full-calibrator-training.yml" in source
    assert source.count("python tools/run_winner_v12_full_calibrator_training.py") == 1
    assert "--work-root /tmp/winner-v12-full-calibrator-training-work" in source
    assert "--training-authorized" in source
    assert "--offline-cpu-only" in source
    assert "--resume-snapshot" not in source
    assert 'python-version: "3.12.13"' in source
    assert "timeout-minutes: 240" in source
    assert 'test "${{ github.run_attempt }}" = "1"' in source
    assert "actions/upload-artifact@v4" in source
    assert "if: always()" in source
    assert "--gpu" not in source
    assert "cuda" not in source.lower()


def test_launch_hashes_every_direct_source() -> None:
    contract = load()
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = lf_sha256(path) if item["hash_mode"] == "lf" else sha256(path)
        assert observed == item["sha256"], item["path"]
