from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "training"))

import winner_v143_torque_only_actor_distillation as v143  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v143_preregisters_torque_only_targets_without_search() -> None:
    prereg = load("winner_v143_torque_only_actor_cpu_preregistration.json")
    assert sha256(
        "winner_v143_torque_only_actor_cpu_preregistration.json"
    ) == "aecf3af9cad0744ff7e9e42351df8a2d9a89ff594ec8a26970792f6921542e3b"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_CONTRACT"
    )
    assert prereg["failed_checks"] == []
    assert prereg["dataset"]["torque_corrected_rows"] == 17
    assert prereg["dataset"]["preservation_rows"] == 4_783
    assert prereg["optimizer"]["identical_to_v134"] is True
    assert prereg["optimizer"]["search_or_retry"] is False
    assert prereg["authority"]["behavior_evaluation"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v143_resets_every_non_torque_target_to_source(monkeypatch) -> None:
    torque = np.zeros(4_800, dtype=np.bool_)
    torque[:17] = True
    old_corrected = torque.copy()
    old_corrected[17:71] = True
    base = np.zeros((4_800, 14), dtype=np.float32)
    old_target = np.ones((4_800, 14), dtype=np.float32)
    source = {
        "base_action": base,
        "target_action": old_target,
        "corrected": old_corrected,
        "torque_projected": torque,
    }
    monkeypatch.setattr(v143.v134, "load_teacher_dataset", lambda _: source)
    dataset = v143.load_teacher_dataset(Path("."))
    assert np.array_equal(dataset["target_action"][:17], old_target[:17])
    assert np.array_equal(dataset["target_action"][17:], base[17:])
    assert int(np.sum(dataset["corrected"])) == 17
    assert int(np.sum(dataset["supreme_only_reset_to_source"])) == 54
    assert dataset["correction_weight"] == 4_783 / 17
