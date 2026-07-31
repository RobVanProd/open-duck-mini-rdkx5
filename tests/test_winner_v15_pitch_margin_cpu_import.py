from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v15_pitch_margin_cpu_result.py"
RESULT = ROOT / "outputs/analysis/winner_v15_pitch_margin_cpu_result.json"


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v15_pitch_cpu_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_exact() -> None:
    module = load_importer()
    assert module.artifact_members() == {
        module.RAW_RESULT,
        module.RAW_RECEIPT,
        module.RAW_GRAPH,
        module.RAW_SNAPSHOT,
    }


def test_imported_result_is_exactly_valid() -> None:
    module = load_importer()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["status"] == "PASS_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["proof"]["reward"]["nonzero_penalty_count"] == 5911
    assert value["proof"]["reward"]["settled_bonus_count"] == 36
    assert value["repository_attribution"]["github_run_id"] == 29836822343
    assert value["repository_attribution"]["github_artifact_id"] == 8497744413
    assert value["repository_attribution"]["artifact_zip_sha256"] == (
        "27f1c4776a5cb58aa73a2f17dad8e993b71e3c6ef768f2e3841c707587af0db1"
    )
    assert value["authority"]["robot_clearance"] is False
