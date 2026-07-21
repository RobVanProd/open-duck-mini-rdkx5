from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v20_joint_recurrent_support_training.py"
RESULT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location(
        "winner_v20_joint_recurrent_support_training_import", IMPORTER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_complete_and_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 104
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_001.npz"
        in members
    )
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_joint_recurrent_update_100.npz"
        in members
    )
    assert f"{module.WORK_PREFIX}/graphs/winner_v20_half.onnx" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v20_final.onnx" in members


def test_imported_training_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    attribution = value["repository_attribution"]
    assert attribution["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    assert attribution["github_run_attempt"] == 1
    assert attribution["artifact_zip_sha256"] == attribution[
        "github_artifact_digest"
    ].removeprefix("sha256:")
    assert attribution["preregistration_lf_sha256"] == module.lf_sha256(
        module.PREREGISTRATION
    )
    assert attribution["workflow_lf_sha256"] == module.lf_sha256(module.WORKFLOW)
    assert attribution["runner_lf_sha256"] == module.lf_sha256(module.RUNNER)
    assert attribution["v15_importer_lf_sha256"] == module.lf_sha256(
        module.V15_IMPORTER
    )
    assert attribution["importer_lf_sha256"] == module.lf_sha256(
        module.Path(module.__file__)
    )
