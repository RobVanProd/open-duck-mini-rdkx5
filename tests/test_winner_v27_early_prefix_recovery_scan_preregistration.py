from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v27_early_prefix_recovery_scan_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
    assert value["decision"] == (
        "AUTHORIZE_ONE_ZERO_UPDATE_EARLY_PREFIX_RECOVERY_SCAN_ONLY"
    )
    diagnostic = value["diagnostic"]
    assert diagnostic["fork_ticks"] == [0, 4, 8, 12, 16, 20]
    assert diagnostic["absolute_end_tick"] == 52
    assert diagnostic["expected_candidate_prefixes"] == 40
    assert diagnostic["expected_forks"] == 240
    assert diagnostic["expected_branch_rollouts"] == 720
    assert value["execution_now"] == {
        "candidate_prefixes": 0,
        "forks": 0,
        "branch_rollouts": 0,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]


def test_workflow_is_dormant_and_cpu_only() -> None:
    source = (ROOT / ".github/workflows/winner-v27-early-prefix-recovery-scan.yml").read_text()
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v27_early_prefix_recovery_scan_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
