from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v31_cross_worker_replay_attribution_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
    assert value["decision"] == "AUTHORIZE_ONE_SAVED_RESULT_ONLY_REPLAY_ATTRIBUTION"
    assert value["attribution_rule"]["maximum_ulp_distance_each"] == 8
    assert value["attribution_rule"]["minimum_anchor_improvement_to_cross_worker_delta_ratio"] == 10_000.0
    assert value["attribution_rule"]["rerun_authorized"] is False
    assert not any(value["execution_now"].values())


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]


def test_workflow_is_saved_result_only() -> None:
    source = (
        ROOT / ".github/workflows/winner-v31-cross-worker-replay-attribution.yml"
    ).read_text(encoding="utf-8")
    assert "--saved-result-only-attribution-authorized" in source
    assert "mujoco" not in source.lower()
    assert "download-artifact" not in source
    assert 'test "${{ github.run_attempt }}" = "1"' in source
