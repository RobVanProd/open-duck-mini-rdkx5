from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v165b_import_path_correction_when_present() -> None:
    path = ANALYSIS / "winner_v165b_import_path_correction.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "e3bc5be368bf060846e0c16e799656eeb6f75805099be1a0db2d2ee821ea7601"
    )
    assert value["status"] == "PASS_WINNER_V165B_IMPORT_PATH_CORRECTION"
    assert value["failed_checks"] == []
    assert value["observed_failure"]["behavior_cells_executed"] == 0
    assert value["observed_failure"]["result_written"] is False
    assert value["correction"]["mechanism_change"] is False
    assert value["correction"]["alpha_change"] is False
    assert value["correction"]["block_change"] is False
    assert value["correction"]["matrix_change"] is False
    assert value["correction"]["stop_rule_change"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["hosted_training"] is False
