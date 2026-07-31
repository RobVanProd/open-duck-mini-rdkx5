from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v44_static_target_teacher_source_gradient_contract.json"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_SOURCE_GRADIENT_CPU_PROOF_ONLY"
    assert value["source_selection"]["selected_label"] == "half"
    assert value["source_selection"]["selected_update"] == 251
    assert value["source_selection"]["candidate_checkpoints"] == {
        "half": {"passes": 99, "failures": 25, "cells": 124},
        "final": {"passes": 94, "failures": 30, "cells": 124},
    }
    assert value["objective"]["unit_scale_carried_from_v43"] is False
    assert value["execution_now"] == {
        "rollout_episode_slots": 0,
        "scheduled_rollout_ticks": 0,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
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
