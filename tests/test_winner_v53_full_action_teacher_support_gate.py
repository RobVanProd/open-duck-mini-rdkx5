from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v53_full_action_teacher_support_gate_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v53_full_action_teacher_support_gate.py"
PREREG = ROOT / "outputs/analysis/winner_v53_full_action_teacher_support_gate_preregistration.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v53_runner_test", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sources_compile_and_have_no_training_or_hardware_path() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"grounded_walking_authorized": False' in source


def test_runner_requires_explicit_cpu_gate_flags(monkeypatch, tmp_path: Path) -> None:
    module = load_runner()
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--training-work-root",
            str(tmp_path),
            "--playground-root",
            str(tmp_path),
            "--canonical-fit",
            str(tmp_path),
            "--output",
            str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def _snapshot(module, *, stage: str = "full_action_static_target_teacher_joint_stage2"):
    objective = {"frozen": "test-objective"}
    module._TRAINING_PREREG = {"objective": objective}
    module._TRAINING = {
        "source_snapshot": {"sha256": "source"},
        "teacher_snapshot": {"sha256": "teacher"},
    }
    module.smoke = SimpleNamespace()
    module.training = SimpleNamespace()
    module.v21 = SimpleNamespace(
        JOINT_TRAINABLE_KEYS=frozenset({"leaf"}),
        joint_trainable_parameters=lambda parameters: parameters,
    )
    return {
        "parameters": {"leaf": np.asarray([1.0], dtype=np.float32)},
        "optimizer": {
            "count": np.asarray(403, dtype=np.int64),
            "m": {"leaf": np.asarray([0.1], dtype=np.float32)},
            "v": {"leaf": np.asarray([0.2], dtype=np.float32)},
        },
        "metadata": {
            "schema_version": module.SNAPSHOT_SCHEMA,
            "stage": stage,
            "completed_updates": 403,
            "source_completed_updates": 353,
            "source_snapshot_sha256": "source",
            "teacher_snapshot_sha256": "teacher",
            "objective": objective,
            "root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "full_action_teacher_scale": 136.35153198242188,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "target_mean": np.zeros(50, dtype=np.float32),
        "target_std": np.ones(50, dtype=np.float32),
    }


def test_checkpoint_adapter_validates_then_projects_without_mutation() -> None:
    module = load_runner()
    source = _snapshot(module)
    module.v22v2 = SimpleNamespace(load_snapshot=lambda _path: source)
    module.normalized_support = SimpleNamespace(
        raw_coordinate_predictor_parameters=lambda parameters, _mean, _std: {
            "leaf": parameters["leaf"] * np.float32(2.0)
        }
    )
    adapted = module.load_snapshot_for_reviewed_gate(Path("unused.npz"))
    assert source["metadata"]["stage"] == "full_action_static_target_teacher_joint_stage2"
    assert adapted["metadata"]["stage"] == "stage2"
    np.testing.assert_array_equal(source["parameters"]["leaf"], [1.0])
    np.testing.assert_array_equal(adapted["parameters"]["leaf"], [2.0])
    module.validate_snapshot_for_reviewed_gate(adapted)


def test_checkpoint_paths_require_exact_training_receipts(tmp_path: Path) -> None:
    module = load_runner()
    snapshot = tmp_path / "snapshots/snapshot_full_action_teacher_update_403.npz"
    graph = tmp_path / "graphs/winner_v52_half.onnx"
    snapshot.parent.mkdir(parents=True)
    graph.parent.mkdir(parents=True)
    snapshot.write_bytes(b"snapshot")
    graph.write_bytes(b"graph")

    def receipt(path: Path) -> dict[str, object]:
        return {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    module._TRAINING = {
        "snapshot_manifest": [{"completed_updates": 403, **receipt(snapshot)}],
        "persistent_checkpoints": [
            {
                "label": "half",
                "completed_updates": 403,
                "graph": receipt(graph),
            }
        ],
    }
    assert module.checkpoint_paths(tmp_path, "half") == (snapshot, graph)
    graph.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="artifact bytes changed"):
        module.checkpoint_paths(tmp_path, "half")


def _reviewed_result(*, passed: bool) -> dict[str, object]:
    rows = []
    for label, update in (("half", 403), ("final", 453)):
        rows.append(
            {
                "label": label,
                "update": update,
                "checkpoint_sha256": f"snapshot-{label}",
                "onnx_sha256": f"onnx-{label}",
                "core_model_plant_cells": [{} for _ in range(112)],
                "sensor_transport_plant_cells": [{} for _ in range(12)],
                "failed_checks": [] if passed else ["all_support_cells_pass"],
            }
        )
    checks = {
        "both_checkpoints_evaluated": True,
        "all_248_main_cells_pass": passed,
        "formal_cell_count_exact": True,
    }
    return {
        "schema_version": "winner_v12.calibrator_support_gate_result.v1",
        "status": "unused",
        "decision": "unused",
        "checks": checks,
        "failed_checks": [] if passed else ["all_248_main_cells_pass"],
        "sources": {"base": "frozen"},
        "checkpoint_results": rows,
        "execution": {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {},
    }


def test_selection_occurs_only_after_both_checkpoints_pass(monkeypatch) -> None:
    module = load_runner()
    module._TRAINING = {
        "persistent_checkpoints": [
            {"snapshot": {"sha256": "snapshot-half"}, "graph": {"sha256": "onnx-half"}},
            {"snapshot": {"sha256": "snapshot-final"}, "graph": {"sha256": "onnx-final"}},
        ]
    }
    monkeypatch.setattr(module, "lf_sha256", lambda _path: "lf")
    monkeypatch.setattr(module, "sha256", lambda _path: "raw")

    held = module.finalize_result(_reviewed_result(passed=False), 1)
    module.validate_result(held)
    assert held["selected_checkpoint"] is None
    assert held["authority"]["robot_clearance"] is False

    selected = module.finalize_result(_reviewed_result(passed=True), 0)
    module.validate_result(selected)
    assert selected["selected_checkpoint"]["label"] == "final"
    assert selected["selected_checkpoint"]["completed_updates"] == 453
    assert selected["selected_checkpoint"]["onnx_sha256"] == "onnx-final"
    assert selected["authority"]["robot_clearance"] is True


def test_preregistered_selection_is_fixed_final_not_metric_ranked() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["future_frozen_support_gate"]["cells_per_checkpoint"] == 124
    assert value["pass_rule"]["closest_checkpoint_selection"] is False
    assert value["selection_rule"] == {
        "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
        "selected_checkpoint_if_pass": "final",
        "selected_update_if_pass": 453,
        "selection_basis": "fixed terminal endpoint after half/final persistence",
        "metric_ranking_or_closest_result": False,
        "no_selection_if_hold": True,
    }


def test_source_manifest_is_exact_when_preregistered() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
