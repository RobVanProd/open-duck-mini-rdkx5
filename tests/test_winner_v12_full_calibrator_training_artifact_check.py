from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_winner_v12_full_calibrator_training_artifact.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("winner_v12_artifact_check", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_success_inventory_is_exact() -> None:
    checker = load_checker()
    files = checker.expected_artifact_files()
    assert len(files) == 415
    assert checker.ROOT_LOG_NAME in files
    assert checker.ROOT_RESULT_HASH_NAME in files
    assert f"{checker.WORK_ROOT_NAME}/snapshots/snapshot_stage1_update_001.npz" in files
    assert (
        f"{checker.WORK_ROOT_NAME}/snapshots/snapshot_stage2_update_100.receipt.json"
        in files
    )


def test_safe_zip_extracts_regular_relative_members(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "safe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("root/file.txt", b"safe")
    destination = tmp_path / "extracted"
    assert checker.safe_extract_zip(archive, destination) == ["root/file.txt"]
    assert (destination / "root/file.txt").read_bytes() == b"safe"


@pytest.mark.parametrize("name", ["../escape", "/absolute"])
def test_safe_zip_rejects_traversal_or_non_posix_path(
    tmp_path: Path, name: str
) -> None:
    checker = load_checker()
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(name, b"unsafe")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")


def test_safe_zip_rejects_duplicate_member(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("same", b"one")
        stream.writestr("same", b"two")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")


def test_safe_zip_rejects_symlink(tmp_path: Path) -> None:
    checker = load_checker()
    archive = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr(link, "target")
    with pytest.raises(ValueError):
        checker.safe_extract_zip(archive, tmp_path / "extracted")
