from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v13_normalized_response_stage1_invalid_attribution.py"
RESULT = ROOT / "outputs/analysis/winner_v13_normalized_response_stage1_result.json"
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/winner_v13_normalized_response_stage1_invalid_attribution.json"
)


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_invalid_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_is_checker_only_but_not_promoted() -> None:
    module = load()
    raw = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_selected_failure(raw)
    assert all(
        row["checks"]["learned_prediction_beats_constant_per_plant"]
        for row in raw["checkpoint_results"]
    )
    assert raw["decision"] == "DO_NOT_TRAIN_SUPPORT_CONTROLLER"


def test_attribution_requires_fresh_corrected_run() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "INVALID_WINNER_V13_STAGE1_DECISION_CONTRACT"
    assert value["decision"] == "DO_NOT_ADVANCE_REVALIDATE_CORRECTED_CHECKER"
    assert value["required_correction"] == {
        "action_check": (
            "compare every ONNX action/output/state against networks.calibrator_step "
            "using the identical observation, externally realized previous_action, "
            "and identical h_in"
        ),
        "cpu_contract_before_rerun": True,
        "fresh_preregistration_and_fresh_run_required": True,
        "hidden_check": "same-input one-step JAX/ONNX maximum absolute error <=1e-7",
        "learning_rate": 0.0001,
    }
    assert value["authority"]["support_controller_training_authorized"] is False
    assert value["execution"]["additional_optimizer_updates"] == 0
