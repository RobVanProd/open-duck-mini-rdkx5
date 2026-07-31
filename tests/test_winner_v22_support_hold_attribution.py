from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v22_support_hold_attribution.json"


def test_attribution_closes_training_and_selects_only_read_only_diagnostic() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V22_SUPPORT_HOLD_ATTRIBUTION"
    assert value["decision"] == (
        "AUTHORIZE_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"] == {
        "new_simulation_cells": 0,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["response_conditioned_locomotion_training_authorized"] is False
    assert value["authority"]["manual_mass_com_inertia_measurements_required"] is False


def test_attribution_proves_predictor_fix_and_physical_hold_separately() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["lineage"]["winner_v22"]
    assert [half["physical_support_failures"], final["physical_support_failures"]] == [15, 14]
    assert half["learned_prediction_beats_constant_both_plants"] is True
    assert final["learned_prediction_beats_constant_both_plants"] is True
    assert half["failure_reasons"] == ["roll_pitch"]
    assert final["failure_reasons"] == ["roll_pitch"]
    assert half["all_physical_failures_have_negative_torso_com_x"] is True
    assert final["all_physical_failures_have_negative_torso_com_x"] is True


def test_attribution_has_no_training_or_hardware_surface() -> None:
    source = (ROOT / "tools/build_winner_v22_support_hold_attribution.py").read_text(
        encoding="utf-8"
    )
    assert "import jax" not in source
    assert "mujoco" not in source
    assert "onnxruntime" not in source
    assert "--hardware-authorized" not in source


def test_attribution_source_manifest_is_exact() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        payload = (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert item["hash_mode"] == "lf"
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(
            value["sources"], sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]
