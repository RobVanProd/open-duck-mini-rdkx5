from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v47_static_target_teacher_support_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v47_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checkpoint_constants_are_frozen() -> None:
    module = load()
    assert module.SOURCE_SNAPSHOT_SHA256 == "72c2e0bf895e8968a0d851ee1079435daca6125a572943b557fe766fc6e4832b"
    assert module.TEACHER_SNAPSHOT_SHA256 == "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"


def test_runner_requires_explicit_cpu_gate_flags(monkeypatch, tmp_path) -> None:
    module = load()
    monkeypatch.setattr("sys.argv", [
        str(RUNNER), "--training-work-root", str(tmp_path),
        "--playground-root", str(tmp_path), "--canonical-fit", str(tmp_path),
        "--output", str(tmp_path / "out.json"),
    ])
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        module.main()


def test_runner_has_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    assert "paramiko" not in source
    assert '"robot_clearance": False' in source


def _snapshot(module, *, stage: str = "static_target_teacher_joint_stage2"):
    objective = {"frozen": "test-objective"}
    module._TRAINING_PREREG = {"objective": objective}
    module.smoke = SimpleNamespace()
    module.training = SimpleNamespace()
    module.v21 = SimpleNamespace(
        JOINT_TRAINABLE_KEYS=frozenset({"leaf"}),
        joint_trainable_parameters=lambda parameters: parameters,
    )
    return {
        "parameters": {"leaf": np.asarray([1.0], dtype=np.float32)},
        "optimizer": {
            "count": np.asarray(302, dtype=np.int64),
            "m": {"leaf": np.asarray([0.1], dtype=np.float32)},
            "v": {"leaf": np.asarray([0.2], dtype=np.float32)},
        },
        "metadata": {
            "schema_version": module.SNAPSHOT_SCHEMA,
            "stage": stage,
            "completed_updates": 302,
            "source_completed_updates": 252,
            "source_snapshot_sha256": module.SOURCE_SNAPSHOT_SHA256,
            "teacher_snapshot_sha256": module.TEACHER_SNAPSHOT_SHA256,
            "objective": objective,
            "root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "static_target_teacher_scale": 58.436370849609375,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "target_mean": np.zeros(50, dtype=np.float32),
        "target_std": np.ones(50, dtype=np.float32),
    }


def test_checkpoint_adapter_validates_before_projecting_without_mutating_source() -> None:
    module = load()
    source = _snapshot(module)
    module.v22v2 = SimpleNamespace(load_snapshot=lambda _path: source)
    module.normalized_support = SimpleNamespace(
        raw_coordinate_predictor_parameters=lambda parameters, _mean, _std: {
            "leaf": parameters["leaf"] * np.float32(2.0)
        }
    )

    adapted = module.load_snapshot_for_reviewed_gate(Path("unused.npz"))

    assert source["metadata"]["stage"] == "static_target_teacher_joint_stage2"
    assert adapted["metadata"]["stage"] == "stage2"
    np.testing.assert_array_equal(source["parameters"]["leaf"], [1.0])
    np.testing.assert_array_equal(adapted["parameters"]["leaf"], [2.0])
    module.validate_snapshot_for_reviewed_gate(adapted)


def test_checkpoint_adapter_rejects_invalid_source_before_projection() -> None:
    module = load()
    source = _snapshot(module)
    source["target_std"][0] = np.float32(0.0)
    projected = False

    def project(*_arguments):
        nonlocal projected
        projected = True
        return source["parameters"]

    module.v22v2 = SimpleNamespace(load_snapshot=lambda _path: source)
    module.normalized_support = SimpleNamespace(
        raw_coordinate_predictor_parameters=project
    )

    with pytest.raises(ValueError, match="target_std is not positive"):
        module.load_snapshot_for_reviewed_gate(Path("unused.npz"))
    assert projected is False


def test_checkpoint_paths_require_exact_imported_bytes(tmp_path: Path) -> None:
    module = load()
    root = tmp_path / "training"
    snapshot = root / "snapshots/snapshot_static_target_teacher_update_302.npz"
    graph = root / "graphs/winner_v46_half.onnx"
    snapshot.parent.mkdir(parents=True)
    graph.parent.mkdir(parents=True)
    snapshot.write_bytes(b"snapshot-302")
    graph.write_bytes(b"graph-half")

    def receipt(path: Path) -> dict[str, object]:
        data = path.read_bytes()
        return {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    module._TRAINING = {
        "snapshot_manifest": [
            {"completed_updates": 302, **receipt(snapshot)},
        ],
        "persistent_checkpoints": [
            {"label": "half", "completed_updates": 302, "graph": receipt(graph)},
        ],
    }
    module.smoke = SimpleNamespace(
        sha256=lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    )

    assert module.checkpoint_paths(root, "half") == (snapshot, graph)
    graph.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="artifact bytes changed"):
        module.checkpoint_paths(root, "half")
