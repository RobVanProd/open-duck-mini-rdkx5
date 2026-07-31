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


def test_v134_protocol_repairs_precede_any_gradient() -> None:
    v2 = load("winner_v134_full_actor_teacher_cpu_preregistration_v2.json")
    v3 = load("winner_v134_full_actor_teacher_cpu_preregistration_v3.json")
    assert v2["supersedes"]["artifact"] == (
        "winner_v134_full_actor_teacher_cpu_preregistration.json"
    )
    assert "71 rows" in v2["supersedes"]["reason"]
    assert v2["dataset"]["corrected_rows"] == 71
    assert v2["dataset"]["torque_projected_rows"] == 17
    assert v2["dataset"]["supreme_only_corrected_rows"] == 54
    assert v3["supersedes"]["artifact"] == (
        "winner_v134_full_actor_teacher_cpu_preregistration_v2.json"
    )
    assert "RunningStatisticsState" in v3["supersedes"]["reason"]
    assert v3["dataset"] == v2["dataset"]
    assert v3["optimizer"] == v2["optimizer"]
    assert v3["pass_rule"] == v2["pass_rule"]
    assert sha256(
        "winner_v134_full_actor_teacher_cpu_preregistration_v3.json"
    ) == "1d18952d2029066903298075f38da573cdcdfd3df4db71e5dd52423568c798de"


def test_v134_full_actor_smoke_closes_without_formal_training() -> None:
    result = load("winner_v134_full_actor_teacher_cpu_result_v3.json")
    assert sha256("winner_v134_full_actor_teacher_cpu_result_v3.json") == (
        "e25691c219eec4b76dea0f18b14e47b6fd840b6c0bc53c6c1817cdd5fbf3f387"
    )
    assert result["status"] == (
        "HOLD_WINNER_V134_FULL_ACTOR_TEACHER_CPU_CONTRACT"
    )
    assert result["failed_checks"] == [
        "preservation_leakage_within_one_percent"
    ]
    assert result["checks"]["step_zero_matches_v121_final_deployment"] is True
    assert result["checks"]["all_non_scale_actor_leaves_changed"] is True
    assert result["checks"]["scale_logits_frozen"] is True
    assert result["checks"]["both_export_abis_exact"] is True
    assert (
        result["checks"]["both_export_inference_contracts_pass"] is True
    )
    metrics = result["smoke"]["metrics"]
    assert metrics["corrected_ratio_to_zero_predictor"] < 0.90
    assert metrics["preservation_ratio_to_corrected_baseline"] > 0.01
    assert metrics["preservation_ratio_to_corrected_baseline"] < 0.014
    assert result["decision"] == "NO_FULL_ACTOR_TEACHER_DISTILLATION"
    assert result["authority"]["formal_cpu_distillation_preregistration"] is False
    assert result["authority"]["behavior_evaluation"] is False
