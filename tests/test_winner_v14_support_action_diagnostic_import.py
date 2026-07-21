from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v14_support_action_diagnostic_result.py"
RESULT = ROOT / "outputs/analysis/winner_v14_support_action_diagnostic_result.json"


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v14_diagnostic_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_artifact(path: Path, raw: bytes = b"{}") -> str:
    importer = load_importer()
    digest = importer.sha256_bytes(raw)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(importer.RAW_RESULT_NAME, raw)
        archive.writestr(
            importer.RAW_RECEIPT_NAME,
            f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode(),
        )
    return digest


def test_reads_exact_artifact(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "diagnostic.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_result_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_or_symlink_artifact_member(tmp_path: Path) -> None:
    importer = load_importer()
    extra = tmp_path / "extra.zip"
    write_artifact(extra)
    with zipfile.ZipFile(extra, "a") as archive:
        archive.writestr("extra", b"unexpected")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(extra)

    symlink = tmp_path / "symlink.zip"
    member = zipfile.ZipInfo(importer.RAW_RESULT_NAME)
    member.create_system = 3
    member.external_attr = (stat.S_IFLNK | 0o777) << 16
    receipt = "0" * 64 + f"  /tmp/{importer.RAW_RESULT_NAME}\n"
    with zipfile.ZipFile(symlink, "w") as archive:
        archive.writestr(member, "target")
        archive.writestr(importer.RAW_RECEIPT_NAME, receipt)
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_result_artifact(symlink)


def test_repository_attribution_is_exact() -> None:
    importer = load_importer()
    result = importer.repository_attribution(
        run_id=42,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=73,
        artifact_name="winner-v14-support-action-diagnostic-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert result["repository"] == importer.EXPECTED_REPOSITORY


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("run_attempt", 2),
        ("run_head_sha", "a" * 39),
        ("artifact_id", 0),
        ("artifact_name", "wrong"),
        ("artifact_digest", f"sha256:{'c' * 64}"),
    ],
)
def test_repository_attribution_rejects_drift(key: str, value: object) -> None:
    importer = load_importer()
    arguments = {
        "run_id": 42,
        "run_attempt": 1,
        "run_head_sha": "a" * 40,
        "artifact_id": 73,
        "artifact_name": "winner-v14-support-action-diagnostic-42",
        "artifact_digest": f"sha256:{'b' * 64}",
        "artifact_zip_sha256": "b" * 64,
    }
    arguments[key] = value
    with pytest.raises(ValueError, match="attribution"):
        importer.repository_attribution(**arguments)


def test_imported_result_closes_scale_repair_with_exact_provenance() -> None:
    importer = load_importer()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC"
    assert value["decision"] == "NO_SCALE_PASSES_PREREGISTER_SUPPORT_OBJECTIVE_REPAIR"
    assert value["selected_scale"] is None
    assert value["passing_scales"] == []
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["execution"] == {
        "optimizer_updates": 0,
        "main_cells": 1240,
        "repeat_cells": 320,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert [row["scale"] for row in value["scale_summary"]] == [
        0.0,
        0.25,
        0.5,
        0.75,
        1.0,
    ]
    assert not any(row["complete_pass"] for row in value["scale_summary"])
    failure_counts = [
        [checkpoint["support_failure_count"] for checkpoint in row["checkpoint_results"]]
        for row in value["scale_summary"]
    ]
    assert failure_counts == [[10, 10], [10, 11], [11, 10], [12, 10], [15, 11]]
    for row in value["scale_summary"]:
        for checkpoint in row["checkpoint_results"]:
            assert checkpoint["terminal_failed_check_counts"] == {
                "roll_pitch": checkpoint["support_failure_count"]
            }
            assert checkpoint["checks"][
                "corrected_prediction_beats_constant_per_plant"
            ] is True
            assert checkpoint["checks"]["all_support_cells_pass"] is False
            assert checkpoint["checks"]["all_32_heldout_repeats_bit_exact"] is True
    for row in value["scale_summary"][1:]:
        assert all(
            checkpoint["checks"]["all_16_heldout_contexts_separate"]
            for checkpoint in row["checkpoint_results"]
        )
    assert all(
        not checkpoint["checks"]["all_16_heldout_contexts_separate"]
        for checkpoint in value["scale_summary"][0]["checkpoint_results"]
    )
    attribution = value["repository_attribution"]
    assert attribution["github_run_id"] == 29834084968
    assert attribution["github_run_attempt"] == 1
    assert attribution["github_run_head_sha"] == "288c5f87cbc6d4af6a1f127bdc9bd29026d80262"
    assert attribution["github_artifact_id"] == 8496883752
    assert attribution["artifact_zip_sha256"] == "a638437b3da6700527f0c1b9aa98226bb9d983fa6f58d4ca58b23da1b141b61b"
    assert attribution["raw_result_sha256"] == "cc7bc883d0672a72d66851c96b82c2de4e14ec8b7bb15cd87ccabc8a37a418c6"
    assert attribution["importer_lf_sha256"] == importer.lf_sha256(IMPORTER)
    assert value["authority"]["robot_clearance"] is False
