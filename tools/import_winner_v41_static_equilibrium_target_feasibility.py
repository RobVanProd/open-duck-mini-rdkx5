#!/usr/bin/env python3
"""Safely import the sole Winner-v41 static-equilibrium feasibility result."""

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


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v41_static_equilibrium_target_feasibility_preregistration.json"
V40_RESULT = ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_result.json"
RUNNER = ROOT / "tools/run_winner_v41_static_equilibrium_target_feasibility.py"
WORKFLOW = ROOT / ".github/workflows/winner-v41-static-equilibrium-target-feasibility.yml"
OUTPUT_JSON = ANALYSIS / "winner_v41_static_equilibrium_target_feasibility_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v41-static-equilibrium-target-feasibility-result.json"
RAW_RECEIPT_NAME = "winner-v41-static-equilibrium-target-feasibility-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
GRID_VALUES = (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0)
EXPECTED_COORDINATES = list(itertools.product(GRID_VALUES, repeat=3))
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
            raise ValueError("Winner-v41 artifact inventory changed")
        if sum(item.file_size for item in infos) > 250_000_000:
            raise ValueError("Winner-v41 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v41 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v41 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v41-static-equilibrium-target-feasibility-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v41 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _validate_episode(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("Winner-v41 episode summary changed")
    for name in (
        "minimum_base_z_m", "maximum_abs_tilt_rad", "maximum_torque_nm",
        "maximum_current_a", "maximum_final_window_gyro_xy_norm_rad_s",
    ):
        item = value.get(name)
        if type(item) not in {int, float} or not math.isfinite(item):
            raise ValueError(f"Winner-v41 episode {name} changed")
    if type(value.get("valid_ticks")) is not int or value["valid_ticks"] not in range(0, 251):
        raise ValueError("Winner-v41 episode valid ticks changed")


def _validate_plant_result(value: Any, expected_plant: str, *, replay: bool) -> None:
    fields = {
        "plant", "terminal", "episode", "support_pass", "all_actions_bounded",
        "raw_target_sha256", "action_trace_sha256", "action_hash_chain_sha256",
    }
    if replay:
        fields.add("trace")
    if not isinstance(value, Mapping) or set(value) != fields or value["plant"] != expected_plant:
        raise ValueError("Winner-v41 plant result schema changed")
    if type(value["support_pass"]) is not bool or type(value["all_actions_bounded"]) is not bool:
        raise ValueError("Winner-v41 plant result boolean changed")
    for name in ("raw_target_sha256", "action_trace_sha256", "action_hash_chain_sha256"):
        require_sha256(value[name], f"Winner-v41 {name}")
    _validate_episode(value["episode"])
    terminal = value["terminal"]
    if terminal is not None and (
        not isinstance(terminal, Mapping) or type(terminal.get("tick")) is not int
        or terminal["tick"] not in range(0, 250)
    ):
        raise ValueError("Winner-v41 terminal changed")
    if value["support_pass"] and terminal is not None:
        raise ValueError("Winner-v41 terminal target cannot pass")
    if replay:
        trace = value["trace"]
        expected_length = 250 if terminal is None else terminal["tick"] + 1
        if not isinstance(trace, list) or len(trace) != expected_length:
            raise ValueError("Winner-v41 replay trace length changed")
        for tick, item in enumerate(trace):
            if (
                not isinstance(item, Mapping)
                or set(item) != {"tick", "action_sha256", "transition"}
                or item["tick"] != tick or not isinstance(item["transition"], Mapping)
            ):
                raise ValueError("Winner-v41 replay trace changed")
            require_sha256(item["action_sha256"], "Winner-v41 replay action")


def _candidate_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    plants = row["plant_results"]
    valid_ticks = [item["episode"]["valid_ticks"] for item in plants]
    support_count = sum(item["support_pass"] for item in plants)
    minimum_base_z = min(item["episode"]["minimum_base_z_m"] for item in plants)
    maximum_tilt = max(item["episode"]["maximum_abs_tilt_rad"] for item in plants)
    maximum_final_gyro = max(
        item["episode"]["maximum_final_window_gyro_xy_norm_rad_s"] for item in plants
    )
    coordinates = row["coordinates"]
    return (
        support_count,
        min(valid_ticks),
        sum(valid_ticks),
        minimum_base_z,
        -maximum_tilt,
        -maximum_final_gyro,
        -sum(float(value) ** 2 for value in coordinates),
        -int(row["candidate_index"]),
    )


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "screen", "candidate_results", "selection", "summary",
        "execution", "sources", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v41.static_equilibrium_target_feasibility_result.v1":
        raise ValueError("Winner-v41 result schema changed")
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
            != f"winner-v41-static-equilibrium-target-feasibility-{attribution['github_run_id']}"
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
            raise ValueError("Winner-v41 imported attribution changed")
    expected_screen = {
        "configuration_ids": ["COM_X_NEG"],
        "controlled_action_indices": [2, 3, 4, 11, 12, 13],
        "coordinate_order": ["hip_pitch_magnitude", "knee", "ankle"],
        "grid_values": list(GRID_VALUES),
        "grid_dimensions": 3,
        "candidate_count": 729,
        "duration_ticks": 250,
        "target_semantics": "one time-invariant raw action target for all 250 ticks",
        "plant_semantics": "one shared target must pass both measured actuator plants",
    }
    if result.get("screen") != expected_screen:
        raise ValueError("Winner-v41 screen changed")
    if result.get("execution") != {
        "static_target_candidates": 729,
        "candidate_plant_cells": 1458,
        "selected_target_replay_cells": 2,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "runtime_static_target_or_action_wrapper_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "one separately frozen static-target teacher contract",
    }:
        raise ValueError("Winner-v41 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v40_result_lf_sha256": lf_sha256(V40_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v41 sources changed")
    candidates = result.get("candidate_results")
    if not isinstance(candidates, list) or len(candidates) != 729:
        raise ValueError("Winner-v41 candidate count changed")
    for index, (candidate, coordinates) in enumerate(zip(candidates, EXPECTED_COORDINATES)):
        if not isinstance(candidate, Mapping) or set(candidate) != {
            "candidate_index", "coordinates", "coordinates_sha256", "plant_results",
            "shared_support_pass",
        } or candidate["candidate_index"] != index or tuple(candidate["coordinates"]) != coordinates:
            raise ValueError("Winner-v41 candidate identity changed")
        require_sha256(candidate["coordinates_sha256"], "Winner-v41 coordinates")
        plants = candidate["plant_results"]
        if not isinstance(plants, list) or len(plants) != 2:
            raise ValueError("Winner-v41 candidate plant count changed")
        for plant_result, plant in zip(plants, PLANTS):
            _validate_plant_result(plant_result, plant, replay=False)
        expected_shared = all(item["support_pass"] for item in plants)
        if type(candidate["shared_support_pass"]) is not bool or candidate["shared_support_pass"] != expected_shared:
            raise ValueError("Winner-v41 shared pass changed")
    passing = [row for row in candidates if row["shared_support_pass"]]
    selected = max(passing if passing else candidates, key=_candidate_key)
    selection = result.get("selection")
    if not isinstance(selection, Mapping) or set(selection) != {
        "kind", "candidate_index", "coordinates", "coordinates_sha256",
        "shared_support_pass_count", "replay_exact", "replay_results",
    }:
        raise ValueError("Winner-v41 selection schema changed")
    if (
        selection["kind"] != ("shared_support_pass" if passing else "diagnostic_best_not_promoted")
        or selection["candidate_index"] != selected["candidate_index"]
        or selection["coordinates"] != selected["coordinates"]
        or selection["coordinates_sha256"] != selected["coordinates_sha256"]
        or selection["shared_support_pass_count"] != len(passing)
        or selection["replay_exact"] is not True
        or not isinstance(selection["replay_results"], list)
        or len(selection["replay_results"]) != 2
    ):
        raise ValueError("Winner-v41 selection changed")
    for replay, original, plant in zip(
        selection["replay_results"], selected["plant_results"], PLANTS
    ):
        _validate_plant_result(replay, plant, replay=True)
        replay_without_trace = {name: replay[name] for name in original}
        if replay_without_trace != original:
            raise ValueError("Winner-v41 selected replay changed")
    checks = {
        "exact_729_static_targets": len(candidates) == 729,
        "exact_1458_candidate_plant_cells": sum(
            len(row["plant_results"]) for row in candidates
        ) == 1458,
        "all_candidate_actions_graph_bounded": all(
            item["all_actions_bounded"]
            for row in candidates for item in row["plant_results"]
        ),
        "selected_target_replay_exact": selection["replay_exact"],
        "at_least_one_shared_target_passes_both_plants": bool(passing),
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v41 checks are not rederived")
    summary = {
        "shared_support_pass_count": len(passing),
        "per_plant_support_pass_counts": {
            plant: sum(
                row["plant_results"][plant_index]["support_pass"] for row in candidates
            )
            for plant_index, plant in enumerate(PLANTS)
        },
        "selected_candidate_index": selected["candidate_index"],
        "selected_coordinates": selected["coordinates"],
        "selected_terminal_ticks": [
            None if row["terminal"] is None else row["terminal"]["tick"]
            for row in selection["replay_results"]
        ],
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v41 summary is not rederived")
    validity_names = {
        "exact_729_static_targets", "exact_1458_candidate_plant_cells",
        "all_candidate_actions_graph_bounded", "selected_target_replay_exact",
    }
    valid = all(checks[name] for name in validity_names)
    passed = valid and checks["at_least_one_shared_target_passes_both_plants"]
    if not valid:
        expected = (
            "INVALID_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY",
            "INVALID_STATIC_EQUILIBRIUM_SCREEN",
            "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        )
    elif passed:
        expected = (
            "PASS_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY",
            "SHARED_FULL_HORIZON_STATIC_SUPPORT_TARGET_EXISTS",
            "AUTHORIZE_STATIC_TARGET_TEACHER_CONTRACT_ONLY",
        )
    else:
        expected = (
            "HOLD_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY",
            "NO_SHARED_COARSE_GRID_STATIC_SUPPORT_TARGET",
            "CLOSE_STATIC_EQUILIBRIUM_TARGET_ROUTE",
        )
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or (result.get("status"), result.get("classification"), result.get("decision"))
        != expected
    ):
        raise ValueError("Winner-v41 decision changed")


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
        raise FileExistsError("Winner-v41 result is already imported")
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
        raise ValueError("Winner-v41 raw-result receipt changed")
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
            "# Winner-v41 static-equilibrium target feasibility result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Shared support targets: `{summary['shared_support_pass_count']} / 729`",
            f"- Selected coordinates: `{summary['selected_coordinates']}`",
            f"- Selected terminal ticks: `{summary['selected_terminal_ticks']}`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "This is a simulator equilibrium-feasibility result. It is not a runtime",
            "target, action wrapper, checkpoint, deployment, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
