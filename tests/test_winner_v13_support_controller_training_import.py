from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_support_controller_training.py"
RESULT = ROOT / "outputs/analysis/winner_v13_support_controller_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_training_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_complete_and_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 105
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert module.RAW_LOG in members
    assert f"{module.WORK_PREFIX}/snapshots/snapshot_stage2_update_001.npz" in members
    assert f"{module.WORK_PREFIX}/snapshots/snapshot_stage2_update_100.npz" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v13_support_controller_half.onnx" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v13_support_controller_final.onnx" in members


def test_imported_training_result_is_exact_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"] == {
        "repository": "RobVanProd/open-duck-mini-rdkx5",
        "github_run_id": 29825555037,
        "github_run_attempt": 1,
        "github_run_head_sha": "7353a07d8b6573bfacf55a608e6e7588e6f961ae",
        "github_artifact_id": 8495297905,
        "github_artifact_name": (
            "winner-v13-support-controller-training-29825555037"
        ),
        "github_artifact_digest": (
            "sha256:f59d8471e14bf86eb3ca121877ad982c8e8005a15f7c84dd4f75699992a7345b"
        ),
        "artifact_zip_sha256": (
            "f59d8471e14bf86eb3ca121877ad982c8e8005a15f7c84dd4f75699992a7345b"
        ),
        "artifact_zip_bytes": 9877339,
        "raw_result_sha256": (
            "3c2c1b0bc973556949a0a3ce406529db4ee2850dfa0e9b1046b3a38bfba9c112"
        ),
        "raw_result_receipt_sha256": (
            "ebeda6020d6b3874e24979b3d034f7583a72c47bbdb5de52c9c56c1bfa8a103b"
        ),
        "log_sha256": (
            "4e21537cdf66b30a65ac96f26c33e38ccd054c547c76c1ebc479ff19dd2c7719"
        ),
        "preregistration_lf_sha256": module.lf_sha256(module.PREREGISTRATION),
        "workflow_lf_sha256": module.lf_sha256(module.WORKFLOW),
        "runner_lf_sha256": module.lf_sha256(module.RUNNER),
        "importer_lf_sha256": module.lf_sha256(module.Path(module.__file__)),
    }
    half, final = value["persistent_checkpoints"]
    assert half["graph"]["sha256"] == (
        "dc119b97562fb30de44090a65411c746d7d4dc2f3e90cd796a55be545c9aa774"
    )
    assert final["graph"]["sha256"] == (
        "a2ea7944e6be1ccf9d43bd5f343d861a4e872212846ebd1e09db16486a922d35"
    )
