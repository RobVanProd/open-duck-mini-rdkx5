from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "training"))

import winner_v145_on_policy_dagger as v145  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v145_preregisters_one_fixed_dataset_aggregation() -> None:
    prereg = load("winner_v145_on_policy_dagger_cpu_preregistration.json")
    assert sha256(
        "winner_v145_on_policy_dagger_cpu_preregistration.json"
    ) == "fbb1657b62e25c6b8fe3da5f1bd75bdfb8af15042140fcbe5ed659b90d0d448b"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V145_ON_POLICY_DAGGER_CPU_CONTRACT"
    )
    assert prereg["failed_checks"] == []
    assert prereg["dataset"]["rows"] == 5_400
    assert prereg["dataset"]["shadow_corrected_rows"] == 4
    assert prereg["dataset"]["joint_element_labels"] == 60
    assert prereg["optimizer"]["updates"] == 2
    assert prereg["optimizer"]["search_or_retry"] is False
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v145_changes_only_projected_joint_targets(monkeypatch) -> None:
    teacher = {
        "obs": np.zeros((4_800, 115), dtype=np.float32),
        "previous_action": np.zeros((4_800, 14), dtype=np.float32),
        "h_in": np.zeros((4_800, 64), dtype=np.float32),
        "target_action": np.ones((4_800, 14), dtype=np.float32),
        "keys": [str(index) for index in range(4_800)],
        "manifest": [],
    }
    teacher_mask = np.zeros((4_800, 14), dtype=np.bool_)
    teacher_mask[:17, 3] = True
    shadow_mask = np.zeros((600, 14), dtype=np.bool_)
    shadow_mask[:4, 13] = True
    shadow = {
        "obs": np.zeros((600, 115), dtype=np.float32),
        "previous_action": np.zeros((600, 14), dtype=np.float32),
        "h_in": np.zeros((600, 64), dtype=np.float32),
        "oracle_action": np.full((600, 14), 2.0, dtype=np.float32),
        "joint_mask": shadow_mask,
        "manifest": {},
        "recorded_base_action": np.zeros((600, 14), dtype=np.float32),
        "recorded_h_out": np.zeros((600, 64), dtype=np.float32),
    }
    monkeypatch.setattr(
        v145.v134, "load_teacher_dataset", lambda _: teacher
    )
    monkeypatch.setattr(
        v145, "_oracle_joint_masks", lambda *_: teacher_mask
    )
    monkeypatch.setattr(v145, "load_shadow_dataset", lambda _: shadow)
    teacher_base = np.zeros((4_800, 14), dtype=np.float32)
    teacher_hidden = np.zeros((4_800, 64), dtype=np.float32)
    shadow_base = np.zeros((600, 14), dtype=np.float32)
    shadow_hidden = np.zeros((600, 64), dtype=np.float32)
    dataset = v145.build_aggregated_dataset(
        teacher_root=Path("."),
        shadow_trace=Path("shadow.jsonl"),
        teacher_baseline_action=teacher_base,
        teacher_baseline_hidden=teacher_hidden,
        shadow_baseline_action=shadow_base,
        shadow_baseline_hidden=shadow_hidden,
    )
    assert dataset["obs"].shape == (5_400, 115)
    assert int(np.sum(dataset["corrected"])) == 21
    assert int(np.sum(dataset["joint_mask"])) == 21
    assert np.all(dataset["target_action"][:17, 3] == 1.0)
    assert np.all(dataset["target_action"][4_800:4_804, 13] == 2.0)
    assert np.count_nonzero(
        dataset["target_action"][~dataset["joint_mask"]]
    ) == 0
    assert dataset["correction_weight"] == 5_379 / 21
