from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v24_baseline_anchored_support_gate_result.py"
RESULT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_support_gate_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_result_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v24-baseline-anchored-support-gate-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v24-baseline-anchored-support-gate-result.sha256"


def test_repository_attribution_is_strict() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v24-baseline-anchored-support-gate-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"


def test_imported_gate_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1


def test_imported_gate_rejects_unrecognized_fields_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value["unexpected"] = True
    with pytest.raises(ValueError, match="schema changed"):
        module.validate_result(value)


def test_v24_checkpoint_updates_are_not_aliased_to_v12() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert 'expected_update = {"half": 150, "final": 200}[label]' in source
    assert 'adapted["update"] = {"half": 50, "final": 100}[label]' in source


def test_existing_reviewed_result_schema_adapts_to_v24_updates(
    tmp_path, monkeypatch
) -> None:
    module = load()
    source_result = json.loads(
        (
            ROOT
            / "outputs/analysis/winner_v22_normalized_predictor_support_gate_result.json"
        ).read_text(encoding="utf-8")
    )
    source_result.pop("repository_attribution")
    rows = source_result["checkpoint_results"]
    for row, update in zip(rows, (150, 200), strict=True):
        row["update"] = update
    source_result["schema_version"] = (
        "winner_v24.baseline_anchored_support_gate_result.v1"
    )
    source_result["status"] = "HOLD_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
    source_result["decision"] = "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    source_result["authority"] = {
        "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }
    training_path = tmp_path / "training.json"
    prereg_path = tmp_path / "prereg.json"
    prereg_path.write_text("{}\n", encoding="utf-8")
    snapshots = [
        {
            "completed_updates": update,
            "sha256": (
                rows[0]["checkpoint_sha256"]
                if update == 150
                else rows[1]["checkpoint_sha256"]
                if update == 200
                else "c" * 64
            ),
        }
        for update in range(101, 201)
    ]
    training_path.write_text(
        json.dumps(
            {
                "status": "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT",
                "decision": "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_ONLY",
                "failed_checks": [],
                "repository_attribution": {
                    "repository": "RobVanProd/open-duck-mini-rdkx5"
                },
                "snapshot_manifest": snapshots,
                "persistent_checkpoints": [
                    {
                        "label": row["label"],
                        "completed_updates": row["update"],
                        "graph": {"sha256": row["onnx_sha256"]},
                    }
                    for row in rows
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "PREREGISTRATION", prereg_path)
    monkeypatch.setattr(module, "TRAINING_RESULT", training_path)
    source_result["sources"] = {
        "preregistration_lf_sha256": module.lf_sha256(prereg_path),
        "training_result_lf_sha256": module.lf_sha256(training_path),
        "training_preregistration_lf_sha256": module.lf_sha256(
            module.TRAINING_PREREGISTRATION
        ),
        "training_runner_lf_sha256": module.lf_sha256(module.TRAINING_RUNNER),
        "base_gate_runner_lf_sha256": module.lf_sha256(module.BASE_GATE_RUNNER),
        "gate_runner_lf_sha256": module.lf_sha256(module.RUNNER),
    }
    module.validate_result(source_result)
