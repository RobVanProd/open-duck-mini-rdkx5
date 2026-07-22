from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v43_static_target_teacher_abi_cpu_contract.json"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_STATIC_TARGET_TEACHER_ABI_CPU_PROOF_ONLY"
    assert value["teacher_abi"]["supervised_action_indices"] == [2, 3, 4, 11, 12, 13]
    assert value["teacher_abi"]["supervised_elements"] == 45_000
    assert value["teacher_abi"]["deployable_graph_inputs_or_outputs_added"] == []
    assert value["execution_now"] == {
        "synthetic_teacher_rows": 0,
        "optimizer_updates": 0,
        "simulator_behavior_ticks": 0,
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
