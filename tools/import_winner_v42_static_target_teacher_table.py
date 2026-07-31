#!/usr/bin/env python3
"""Safely import the sole Winner-v42 static-target teacher-table result."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
import sys
sys.path.insert(0, str(TOOLS))

import import_winner_v41_static_equilibrium_target_feasibility as v41_import  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v42_static_target_teacher_table_preregistration.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V41_RESULT = ANALYSIS / "winner_v41_v2_static_equilibrium_target_feasibility_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v42_static_target_teacher_table.py"
WORKFLOW = ROOT / ".github/workflows/winner-v42-static-target-teacher-table.yml"
OUTPUT_JSON = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V42_STATIC_TARGET_TEACHER_TABLE_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v42-static-target-teacher-table-result.json"
RAW_RECEIPT_NAME = "winner-v42-static-target-teacher-table-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
CONFIGURATION_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
GRID_VALUES = (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0)
EXPECTED_COORDINATES = tuple(itertools.product(GRID_VALUES, repeat=3))
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "preregistration_lf_sha256",
    "workflow_lf_sha256", "runner_lf_sha256", "importer_lf_sha256",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON value is forbidden: {value}")


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v42 artifact inventory changed")
        if sum(item.file_size for item in infos) > 250_000_000:
            raise ValueError("Winner-v42 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v42 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v42 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v42-static-target-teacher-table-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v42 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def configuration_hashes() -> dict[str, str]:
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    rows = [
        *matrix["fixed_anchors"],
        *matrix["discovery_samples"],
        *matrix["heldout_samples"],
    ]
    lookup = {str(row["id"]): row for row in rows}
    if not set(CONFIGURATION_IDS).issubset(lookup):
        raise ValueError("Winner-v42 configurations are absent")
    return {name: canonical_sha256(lookup[name]) for name in CONFIGURATION_IDS}


def validate_compact_plant(value: Any, expected_plant: str) -> None:
    fields = {
        "plant", "support_pass", "terminal_tick", "valid_ticks",
        "minimum_base_z_m", "maximum_abs_tilt_rad",
        "maximum_final_window_gyro_xy_norm_rad_s", "maximum_current_a",
        "maximum_torque_nm", "all_actions_bounded", "raw_target_sha256",
        "action_trace_sha256", "action_hash_chain_sha256",
    }
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("Winner-v42 compact plant schema changed")
    if value["plant"] != expected_plant:
        raise ValueError("Winner-v42 compact plant order changed")
    if type(value["support_pass"]) is not bool or type(value["all_actions_bounded"]) is not bool:
        raise ValueError("Winner-v42 compact plant boolean changed")
    terminal = value["terminal_tick"]
    if terminal is not None and (type(terminal) is not int or terminal not in range(250)):
        raise ValueError("Winner-v42 compact terminal changed")
    if type(value["valid_ticks"]) is not int or value["valid_ticks"] not in range(251):
        raise ValueError("Winner-v42 compact valid ticks changed")
    if terminal is not None and value["valid_ticks"] != terminal:
        raise ValueError("Winner-v42 compact terminal/valid-tick relation changed")
    if value["support_pass"] and (terminal is not None or value["valid_ticks"] != 250):
        raise ValueError("Winner-v42 compact support pass changed")
    for name in (
        "minimum_base_z_m", "maximum_abs_tilt_rad",
        "maximum_final_window_gyro_xy_norm_rad_s", "maximum_current_a",
        "maximum_torque_nm",
    ):
        item = value[name]
        if type(item) not in {int, float} or not math.isfinite(item):
            raise ValueError(f"Winner-v42 compact {name} changed")
    for name in ("raw_target_sha256", "action_trace_sha256", "action_hash_chain_sha256"):
        require_sha256(value[name], f"Winner-v42 {name}")


def compact_replay(value: Mapping[str, Any]) -> dict[str, Any]:
    terminal = value["terminal"]
    episode = value["episode"]
    return {
        "plant": value["plant"],
        "support_pass": value["support_pass"],
        "terminal_tick": None if terminal is None else terminal["tick"],
        "valid_ticks": episode["valid_ticks"],
        "minimum_base_z_m": episode["minimum_base_z_m"],
        "maximum_abs_tilt_rad": episode["maximum_abs_tilt_rad"],
        "maximum_final_window_gyro_xy_norm_rad_s": (
            episode["maximum_final_window_gyro_xy_norm_rad_s"]
        ),
        "maximum_current_a": episode["maximum_current_a"],
        "maximum_torque_nm": episode["maximum_torque_nm"],
        "all_actions_bounded": value["all_actions_bounded"],
        "raw_target_sha256": value["raw_target_sha256"],
        "action_trace_sha256": value["action_trace_sha256"],
        "action_hash_chain_sha256": value["action_hash_chain_sha256"],
    }


def candidate_key(row: Mapping[str, Any], coordinates: tuple[float, ...]) -> tuple[Any, ...]:
    plants = row["plant_results"]
    valid_ticks = [item["valid_ticks"] for item in plants]
    return (
        sum(item["support_pass"] for item in plants),
        min(valid_ticks),
        sum(valid_ticks),
        min(item["minimum_base_z_m"] for item in plants),
        -max(item["maximum_abs_tilt_rad"] for item in plants),
        -max(item["maximum_final_window_gyro_xy_norm_rad_s"] for item in plants),
        -sum(float(item) ** 2 for item in coordinates),
        -int(row["candidate_index"]),
    )


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "screen", "configuration_results", "teacher_table",
        "summary", "execution", "sources", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v42.static_target_teacher_table_result.v1":
        raise ValueError("Winner-v42 result schema changed")
    if "repository_attribution" in result:
        attribution = result["repository_attribution"]
        if (
            not isinstance(attribution, Mapping) or set(attribution) != ATTRIBUTION_FIELDS
            or attribution.get("repository") != EXPECTED_REPOSITORY
            or attribution.get("github_run_attempt") != 1
            or type(attribution.get("github_run_id")) is not int
            or attribution["github_run_id"] <= 0
            or HEX40_RE.fullmatch(str(attribution.get("github_run_head_sha"))) is None
            or type(attribution.get("github_artifact_id")) is not int
            or attribution["github_artifact_id"] <= 0
            or attribution.get("github_artifact_name")
            != f"winner-v42-static-target-teacher-table-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(HEX64_RE.fullmatch(str(attribution.get(name))) is None for name in (
                "artifact_zip_sha256", "raw_result_sha256", "raw_result_receipt_sha256",
                "preregistration_lf_sha256", "workflow_lf_sha256",
                "runner_lf_sha256", "importer_lf_sha256",
            ))
            or attribution["preregistration_lf_sha256"] != lf_sha256(PREREGISTRATION)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["runner_lf_sha256"] != lf_sha256(RUNNER)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v42 imported attribution changed")
    expected_screen = {
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": list(PLANTS),
        "grid_values": list(GRID_VALUES),
        "targets_per_configuration": 729,
        "maximum_candidate_plant_cells": 21_870,
        "duration_ticks": 250,
        "selection": "unchanged Winner-v41 deterministic shared-target key",
        "target_semantics": "one selected time-invariant target per configuration",
    }
    if result.get("screen") != expected_screen:
        raise ValueError("Winner-v42 screen changed")
    if result.get("execution") != {
        "configuration_tables": 15, "static_target_candidates": 10_935,
        "candidate_plant_cells": 21_870, "selected_target_replay_cells": 30,
        "optimizer_updates": 0, "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False, "training_authorized": False,
        "runtime_static_target_or_action_wrapper_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "one separately frozen static-target teacher ABI CPU contract",
    }:
        raise ValueError("Winner-v42 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
        "winner_v41_result_lf_sha256": lf_sha256(V41_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v42 sources changed")

    rows = result.get("configuration_results")
    if not isinstance(rows, list) or [row.get("configuration_id") for row in rows] != list(CONFIGURATION_IDS):
        raise ValueError("Winner-v42 configuration table set changed")
    expected_config_hashes = configuration_hashes()
    derived_table: dict[str, Any] = {}
    shared_counts: dict[str, int] = {}
    selected_coordinates: dict[str, Any] = {}
    all_actions_bounded = True
    all_replays_exact = True
    hold_ids: list[str] = []
    for row in rows:
        fields = {
            "configuration_id", "configuration_sha256", "candidate_receipts",
            "shared_support_pass_count", "per_plant_support_pass_counts",
            "selected_kind", "selected_candidate_index", "selected_coordinates",
            "selected_coordinates_sha256", "selected_replay_exact",
            "selected_replay_results",
        }
        if not isinstance(row, Mapping) or set(row) != fields:
            raise ValueError("Winner-v42 configuration result schema changed")
        configuration_id = row["configuration_id"]
        if row["configuration_sha256"] != expected_config_hashes[configuration_id]:
            raise ValueError("Winner-v42 configuration hash changed")
        receipts = row["candidate_receipts"]
        if not isinstance(receipts, list) or len(receipts) != 729:
            raise ValueError("Winner-v42 candidate receipt count changed")
        passing: list[Mapping[str, Any]] = []
        for index, (receipt, coordinates) in enumerate(zip(receipts, EXPECTED_COORDINATES)):
            if not isinstance(receipt, Mapping) or set(receipt) != {
                "candidate_index", "coordinates_sha256", "shared_support_pass",
                "plant_results",
            } or receipt["candidate_index"] != index:
                raise ValueError("Winner-v42 candidate receipt identity changed")
            expected_hash = array_sha256(np.asarray(coordinates, dtype=np.float32))
            if receipt["coordinates_sha256"] != expected_hash:
                raise ValueError("Winner-v42 coordinates hash changed")
            plants = receipt["plant_results"]
            if not isinstance(plants, list) or len(plants) != 2:
                raise ValueError("Winner-v42 candidate plant count changed")
            for plant_result, plant in zip(plants, PLANTS, strict=True):
                validate_compact_plant(plant_result, plant)
                all_actions_bounded &= plant_result["all_actions_bounded"]
            expected_shared = all(item["support_pass"] for item in plants)
            if type(receipt["shared_support_pass"]) is not bool or receipt["shared_support_pass"] != expected_shared:
                raise ValueError("Winner-v42 candidate shared pass changed")
            if expected_shared:
                passing.append(receipt)
        selected = max(
            passing if passing else receipts,
            key=lambda item: candidate_key(item, EXPECTED_COORDINATES[item["candidate_index"]]),
        )
        selected_index = selected["candidate_index"]
        coordinates = list(EXPECTED_COORDINATES[selected_index])
        counts = {
            plant: sum(
                receipt["plant_results"][plant_index]["support_pass"]
                for receipt in receipts
            )
            for plant_index, plant in enumerate(PLANTS)
        }
        if (
            row["shared_support_pass_count"] != len(passing)
            or row["per_plant_support_pass_counts"] != counts
            or row["selected_kind"] != ("shared_support_pass" if passing else "diagnostic_best_not_promoted")
            or row["selected_candidate_index"] != selected_index
            or row["selected_coordinates"] != coordinates
            or row["selected_coordinates_sha256"] != selected["coordinates_sha256"]
            or row["selected_replay_exact"] is not True
        ):
            raise ValueError("Winner-v42 selected target changed")
        replays = row["selected_replay_results"]
        if not isinstance(replays, list) or len(replays) != 2:
            raise ValueError("Winner-v42 selected replay count changed")
        for replay, original, plant in zip(replays, selected["plant_results"], PLANTS, strict=True):
            v41_import._validate_plant_result(replay, plant, replay=True)
            if compact_replay(replay) != original:
                raise ValueError("Winner-v42 selected replay changed")
        all_replays_exact &= row["selected_replay_exact"]
        shared_counts[configuration_id] = len(passing)
        selected_coordinates[configuration_id] = coordinates
        if not passing:
            hold_ids.append(configuration_id)
        derived_table[configuration_id] = {
            "candidate_index": selected_index,
            "coordinates": coordinates,
            "coordinates_sha256": selected["coordinates_sha256"],
            "shared_support_pass": bool(passing),
        }

    checks = {
        "exact_15_configuration_tables": len(rows) == 15,
        "exact_729_targets_per_configuration": all(
            len(row["candidate_receipts"]) == 729 for row in rows
        ),
        "exact_21870_candidate_plant_cells": sum(
            len(row["candidate_receipts"]) * 2 for row in rows
        ) == 21_870,
        "all_candidate_actions_graph_bounded": bool(all_actions_bounded),
        "all_selected_target_replays_exact": bool(all_replays_exact),
        "every_configuration_has_a_shared_two_plant_support_target": not hold_ids,
    }
    if result.get("checks") != checks or result.get("teacher_table") != derived_table:
        raise ValueError("Winner-v42 checks or teacher table are not rederived")
    summary = {
        "configuration_pass_count": 15 - len(hold_ids),
        "configuration_hold_ids": hold_ids,
        "shared_target_counts": shared_counts,
        "selected_coordinates": selected_coordinates,
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v42 summary is not rederived")
    validity_names = {
        "exact_15_configuration_tables", "exact_729_targets_per_configuration",
        "exact_21870_candidate_plant_cells", "all_candidate_actions_graph_bounded",
        "all_selected_target_replays_exact",
    }
    valid = all(checks[name] for name in validity_names)
    passed = valid and checks["every_configuration_has_a_shared_two_plant_support_target"]
    if not valid:
        expected = (
            "INVALID_WINNER_V42_STATIC_TARGET_TEACHER_TABLE",
            "INVALID_STATIC_TARGET_TEACHER_TABLE", "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        )
    elif passed:
        expected = (
            "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE",
            "FULL_FAILURE_SET_STATIC_TARGET_TEACHER_TABLE_EXISTS",
            "AUTHORIZE_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_ONLY",
        )
    else:
        expected = (
            "HOLD_WINNER_V42_STATIC_TARGET_TEACHER_TABLE",
            "STATIC_TARGET_TEACHER_TABLE_INCOMPLETE", "CLOSE_STATIC_TARGET_TEACHER_TABLE_ROUTE",
        )
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or (result.get("status"), result.get("classification"), result.get("decision")) != expected
    ):
        raise ValueError("Winner-v42 decision changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    parser.add_argument("--run-head-sha", required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--artifact-digest", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v42 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id, run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha, artifact_id=args.artifact_id,
        artifact_name=args.artifact_name, artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v42 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = payload["summary"]
    OUTPUT_MD.write_text(
        "\n".join([
            "# Winner-v42 static-target teacher-table result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Configuration passes: `{summary['configuration_pass_count']} / 15`",
            f"- Holds: `{summary['configuration_hold_ids']}`",
            "- Candidate-plant cells / selected replays: `21,870 / 30`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "This is a simulator teacher-table feasibility result. It is not a runtime",
            "target, action wrapper, checkpoint, deployment, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
