from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs/analysis/winner_v47b_support_gate_execution_correction_preregistration.json"
)
WORKFLOW = (
    ROOT / ".github/workflows/winner-v47b-support-gate-execution-correction.yml"
)


def test_correction_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V47B_EXECUTION_CORRECTION"
    assert value["decision"] == "AUTHORIZE_ONE_V47B_FIRST_ATTEMPT_ONLY"
    assert value["failed_execution"]["github_run_id"] == 29914159165
    assert value["failed_execution"]["formal_support_cells_executed"] == 0
    assert value["failed_execution"]["artifact_count"] == 0
    assert (
        value["exact_correction"][
            "gate_population_threshold_seed_checkpoint_or_policy_change"
        ]
        is False
    )
    assert value["future_frozen_support_gate"]["cells_per_checkpoint"] == 124
    assert value["pass_rule"]["closest_checkpoint_selection"] is False
    assert not any(value["execution_now"].values())


def test_correction_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]


def test_correction_workflow_is_first_attempt_cpu_only() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v47b_support_gate_execution_correction_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert 'test "${{ github.run_attempt }}" = "1"' in source
    assert "--offline-cpu-only" in source
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source

