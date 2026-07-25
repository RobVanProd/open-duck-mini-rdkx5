from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v137_preregistration_freezes_recurrent_sequence_contract() -> None:
    prereg = load("winner_v137_sequence_teacher_cpu_preregistration.json")
    assert sha256(
        "winner_v137_sequence_teacher_cpu_preregistration.json"
    ) == "38b8cc29561f4b20ef83b99082f0dcf608677346a752d5aefa84e7e516cbc256"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
    )
    assert prereg["failed_checks"] == []
    assert prereg["dataset"]["startup_rows"] == 256
    assert prereg["dataset"]["startup_corrected_rows"] == 15
    assert prereg["optimizer"]["updates"] == 2
    assert prereg["optimizer"]["search_or_retry"] is False
    assert prereg["authority"]["formal_training"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v137_sequence_teacher_closes_on_preservation_leakage() -> None:
    result = load("winner_v137_sequence_teacher_cpu_result.json")
    assert sha256(
        "winner_v137_sequence_teacher_cpu_result.json"
    ) == "7bcbc73aa4f325f45529001886640defebc2cf73d0b4a625be1df803111cf836"
    assert result["status"] == (
        "HOLD_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
    )
    assert result["failed_checks"] == [
        "full_preservation_leakage_within_one_percent"
    ]
    assert result["checks"]["startup_corrected_error_reduced_five_percent"]
    assert result["checks"]["full_corrected_error_reduced_five_percent"]
    assert result["checks"]["only_five_recurrent_adapter_leaves_changed"]
    assert result["checks"]["both_export_abis_exact"]
    assert result["checks"]["both_export_inference_contracts_pass"]
    metrics = result["smoke"]["full_metrics"]
    assert metrics["corrected_ratio_to_source"] < 0.95
    assert metrics["preservation_ratio_to_corrected_baseline"] > 0.05
    assert result["decision"] == "CLOSE_SEQUENCE_TEACHER_DISTILLATION"
    assert result["authority"]["formal_training"] is False
    assert result["authority"]["hosted_training"] is False
