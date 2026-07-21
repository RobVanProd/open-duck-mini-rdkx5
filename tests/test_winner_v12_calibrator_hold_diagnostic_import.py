from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v12_calibrator_hold_diagnostic.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v12_hold_import", IMPORTER)
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


def predictor_row() -> dict:
    observations = list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99))
    groups = (
        ["imu"] * 6
        + ["joint_position"] * 14
        + ["joint_velocity"] * 14
        + ["applied_target"] * 14
        + ["foot_contact"] * 2
    )
    return {
        "cell_count": 16,
        "adjacent_transition_count": 100,
        "all_contact_targets_exactly_one": True,
        "contact_target_std_exactly_1e_6": True,
        "contact_fraction_at_least_0_99": True,
        "learned_noncontact_strictly_below_constant": False,
        "learned_normalized_mse_all_50": 10.0,
        "constant_normalized_mse_all_50": 1.0,
        "learned_normalized_mse_noncontact_48": 2.0,
        "constant_normalized_mse_noncontact_48": 1.0,
        "contact_fraction_of_learned_normalized_sse": 0.999,
        "contact_prediction_mean": 0.7,
        "contact_prediction_min": 0.5,
        "contact_prediction_max": 0.8,
        "per_dimension": [
            {
                "auxiliary_index": index,
                "observation_index": observation,
                "group": group,
                "target_std": 1.0,
                "learned_normalized_mse": 1.0,
                "constant_normalized_mse": 1.0,
            }
            for index, (observation, group) in enumerate(
                zip(observations, groups, strict=True)
            )
        ],
    }


def cell(*, zero: bool, configuration: int, plant: str) -> dict:
    value = {
        "configuration_id": f"CONFIG_{configuration:02d}",
        "plant": plant,
        "support_pass": zero,
        "terminal": None,
        "episode": {},
        "action_statistics": {
            "tick_count": 250,
            "all_zero": zero,
            "peak_abs_by_joint": [0.0] * 14,
            "rms_by_joint": [0.0] * 14,
            "peak_abs_step_by_joint": [0.0] * 14,
        },
        "trace_hashes": {
            "observations": "a" * 64,
            "actions": "b" * 64,
            "predictions": "c" * 64,
            "hidden": "d" * 64,
        },
    }
    if not zero:
        value["formal_outcome_match"] = True
    return value


def checkpoint(label: str) -> dict:
    plants = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
    zero_cells = [
        cell(zero=True, configuration=index, plant=plant)
        for index in range(8)
        for plant in plants
    ]
    graph_cells = [
        cell(zero=False, configuration=index, plant=plants[index % 2])
        for index in range(44)
    ]
    failure_count = 16 if label == "half" else 14
    fail_zero_pass = [[f"CONFIG_{index:02d}", plants[index % 2]] for index in range(failure_count)]
    pass_zero_pass = [
        [f"CONFIG_{index:02d}", plants[index % 2]]
        for index in range(failure_count, 16)
    ]
    return {
        "label": label,
        "update": {"half": 50, "final": 100}[label],
        "checkpoint_sha256": "e" * 64,
        "onnx_sha256": "f" * 64,
        "graph_cells": graph_cells,
        "zero_action_cells": zero_cells,
        "predictor_by_plant": {plant: predictor_row() for plant in plants},
        "support_classification": {
            "graph_fail_zero_pass": fail_zero_pass,
            "graph_fail_zero_fail": [],
            "graph_pass_zero_pass": pass_zero_pass,
            "graph_pass_zero_fail": [],
        },
        "checks": {
            "all_graph_outcomes_match_formal": True,
            "all_zero_action_cells_exactly_zero": True,
            "predictor_contact_std_exactly_1e_6": True,
            "predictor_contact_targets_exactly_one": True,
        },
    }


def valid_result(importer) -> dict:
    return {
        "schema_version": "winner_v12.calibrator_hold_diagnostic_result.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC",
        "decision": "DIAGNOSTIC_ONLY_DO_NOT_TRAIN_OR_DEPLOY",
        "checks": {
            "both_checkpoints_evaluated": True,
            "all_graph_outcomes_match_formal": True,
            "all_zero_action_cells_exactly_zero": True,
            "contact_floor_conditions_confirmed": True,
        },
        "failed_checks": [],
        "findings": {
            "all_formal_failed_pairs_pass_with_zero_action": True,
            "contact_floor_dominates_all_predictor_aggregates": True,
            "graph_fail_zero_fail_count": 0,
            "graph_fail_zero_pass_count": 30,
            "noncontact_predictor_beats_constant_all_aggregates": False,
        },
        "checkpoint_results": [checkpoint("half"), checkpoint("final")],
        "sources": {
            "preregistration_lf_sha256": importer.lf_sha256(importer.PREREGISTRATION),
            "formal_result_lf_sha256": importer.lf_sha256(importer.FORMAL_RESULT),
            "diagnostic_runner_lf_sha256": importer.lf_sha256(importer.RUNNER),
        },
        "execution": {
            "graph_diagnostic_cells": 88,
            "zero_action_diagnostic_cells": 32,
            "training_steps": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": (
                "causal diagnosis and a separate prospective mechanism preregistration only"
            ),
        },
    }


def test_reads_exact_diagnostic_artifact(tmp_path: Path) -> None:
    importer = load_importer()
    archive = tmp_path / "result.zip"
    expected = b'{"status":"PASS"}\n'
    digest = write_artifact(archive, expected)
    raw, receipt = importer.read_result_artifact(archive)
    assert raw == expected
    assert receipt == f"{digest}  /tmp/{importer.RAW_RESULT_NAME}\n".encode()


def test_rejects_extra_or_symlink_members(tmp_path: Path) -> None:
    importer = load_importer()
    extra = tmp_path / "extra.zip"
    write_artifact(extra)
    with zipfile.ZipFile(extra, "a") as archive:
        archive.writestr("extra", b"x")
    with pytest.raises(ValueError, match="inventory"):
        importer.read_result_artifact(extra)

    symlink = tmp_path / "symlink.zip"
    link = zipfile.ZipInfo(importer.RAW_RESULT_NAME)
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(symlink, "w") as archive:
        archive.writestr(link, "target")
        archive.writestr(importer.RAW_RECEIPT_NAME, b"bad")
    with pytest.raises(ValueError, match="unsafe"):
        importer.read_result_artifact(symlink)


def test_validates_complete_diagnostic_without_advancement() -> None:
    importer = load_importer()
    importer.validate_result(valid_result(importer))


def test_rejects_bad_finding_accounting() -> None:
    importer = load_importer()
    result = valid_result(importer)
    result["findings"]["graph_fail_zero_fail_count"] = 1
    with pytest.raises(ValueError, match="finding"):
        importer.validate_result(result)


def test_repository_attribution_is_exact() -> None:
    importer = load_importer()
    value = importer.repository_attribution(
        run_id=42,
        run_attempt=1,
        run_head_sha="a" * 40,
        artifact_id=73,
        artifact_name="winner-v12-calibrator-hold-diagnostic-42",
        artifact_digest=f"sha256:{'b' * 64}",
        artifact_zip_sha256="b" * 64,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"


def test_importer_cannot_run_training_or_hardware() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "--hold-diagnostic-authorized" not in source
    assert "--hardware-authorized" not in source
    assert "onnxruntime" not in source

