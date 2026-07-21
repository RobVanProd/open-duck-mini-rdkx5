from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v20_joint_recurrent_support_cpu_result.py"
RESULT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v20_cpu_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_imported_result_preserves_the_exact_hold() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
    assert value["decision"] == "DO_NOT_TRAIN_JOINT_RECURRENT_SUPPORT_ARM"
    assert value["failed_checks"] == [
        "all_joint_gradients_nonzero",
        "all_joint_leaves_changed",
        "source_hidden_replay_at_most_1e_6",
    ]
    recurrent = {"obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias"}
    assert all(value["optimization"]["gradient_max_abs"][name] == 0.0 for name in recurrent)
    assert all(value["optimization"]["leaf_max_abs_delta"][name] == 0.0 for name in recurrent)
    assert value["repository_attribution"]["github_run_id"] == 29852380511
    assert value["repository_attribution"]["github_artifact_id"] == 8503945380
    assert value["authority"]["robot_clearance"] is False


def test_importer_rejects_extra_and_symlink_members(tmp_path: Path) -> None:
    importer = load()
    extra = tmp_path / "extra.zip"
    with zipfile.ZipFile(extra, "w") as archive:
        for name in (
            importer.RAW_RESULT_NAME,
            importer.RAW_RECEIPT_NAME,
            importer.SNAPSHOT_NAME,
            importer.GRAPH_NAME,
        ):
            archive.writestr(name, b"x")
        archive.writestr("extra", b"x")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(extra)
    symlink = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo(importer.RAW_RESULT_NAME)
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(symlink, "w") as archive:
        archive.writestr(link, "target")
        archive.writestr(importer.RAW_RECEIPT_NAME, b"x")
        archive.writestr(importer.SNAPSHOT_NAME, b"x")
        archive.writestr(importer.GRAPH_NAME, b"x")
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_result_artifact(symlink)


def test_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "onnxruntime" not in source
    assert "import jax" not in source
    assert "--hardware-authorized" not in source
