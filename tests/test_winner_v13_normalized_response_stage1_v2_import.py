from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_normalized_response_stage1_v2.py"
RESULT = ROOT / "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_stage1_v2_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_has_all_recovery_state() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 105
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert module.RAW_LOG in members
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_stage1_update_001.npz"
        in members
    )
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_stage1_update_100.npz"
        in members
    )


def test_imported_result_is_exactly_valid() -> None:
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["status"] == "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
    assert value["failed_checks"] == []
    assert value["execution"]["stage2_optimizer_updates"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
