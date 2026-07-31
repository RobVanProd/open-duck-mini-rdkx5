#!/usr/bin/env python3
"""Safely import the sole Winner-v37 warm-started shooting result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v37_warm_started_shooting_feasibility_preregistration.json"
V36_RESULT = ANALYSIS / "winner_v36_support_oracle_shooting_feasibility_result.json"
RUNNER = ROOT / "tools/run_winner_v37_warm_started_shooting_feasibility.py"
WORKFLOW = ROOT / ".github/workflows/winner-v37-warm-started-shooting-feasibility.yml"
OUTPUT_JSON = ANALYSIS / "winner_v37_warm_started_shooting_feasibility_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v37-warm-started-shooting-feasibility-result.json"
RAW_RECEIPT_NAME = "winner-v37-warm-started-shooting-feasibility-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "preregistration_lf_sha256",
    "workflow_lf_sha256", "runner_lf_sha256", "importer_lf_sha256",
}
PROPOSAL_MEMORY = {
    "first_tick": "exact Winner-v36 cold mean",
    "later_ticks": (
        "shift prior winning raw eight-tick plan left by one tick, repeat its "
        "terminal action, then average adjacent pairs into four two-tick blocks"
    ),
    "covariance": "reset every tick to the unchanged 0.20 initial standard deviation",
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
            raise ValueError("Winner-v37 artifact inventory changed")
        if sum(item.file_size for item in infos) > 250_000_000:
            raise ValueError("Winner-v37 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v37 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v37 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v37-warm-started-shooting-feasibility-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v37 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _validate_row(row: Mapping[str, Any], expected_v36_first_action: str) -> None:
    fields = {
        "configuration_id", "configuration_sha256", "plant",
        "controlled_action_indices", "terminal", "episode", "support_pass",
        "all_actions_bounded", "any_nonzero_action", "first_action_matches_v36",
        "warm_active_after_tick0", "any_warm_mean_differs_from_cold",
        "action_trace_sha256", "warm_mean_trace_sha256", "trace", "prng",
    }
    if set(row) != fields:
        raise ValueError("Winner-v37 cell schema changed")
    if (
        row["configuration_id"] != "COM_X_NEG" or row["plant"] not in PLANTS
        or row["controlled_action_indices"] != [2, 3, 4, 11, 12, 13]
        or any(
            type(row[name]) is not bool for name in (
                "support_pass", "all_actions_bounded", "any_nonzero_action",
                "first_action_matches_v36", "warm_active_after_tick0",
                "any_warm_mean_differs_from_cold",
            )
        )
        or not isinstance(row["trace"], list)
        or len(row["trace"]) not in range(1, 251)
    ):
        raise ValueError("Winner-v37 cell identity or type changed")
    require_sha256(row["configuration_sha256"], "Winner-v37 configuration")
    require_sha256(row["action_trace_sha256"], "Winner-v37 action trace")
    require_sha256(row["warm_mean_trace_sha256"], "Winner-v37 warm-mean trace")
    for tick, item in enumerate(row["trace"]):
        if set(item) != {"tick", "action_sha256", "planning", "transition"} or item["tick"] != tick:
            raise ValueError("Winner-v37 tick trace changed")
        require_sha256(item["action_sha256"], "Winner-v37 tick action")
        planning = item["planning"]
        if set(planning) != {
            "warm_start_active", "input_mean_sha256", "cold_mean_sha256",
            "input_mean_differs_from_cold", "next_warm_mean_sha256",
            "winning_raw_blocks_sha256", "winning_rank", "winning_horizon",
            "winning_sequence_sha256", "iteration_receipts",
        } or len(planning["iteration_receipts"]) != 4:
            raise ValueError("Winner-v37 planning receipt changed")
        if (
            type(planning["warm_start_active"]) is not bool
            or type(planning["input_mean_differs_from_cold"]) is not bool
            or planning["warm_start_active"] is not (tick > 0)
            or (tick == 0 and planning["input_mean_differs_from_cold"])
        ):
            raise ValueError("Winner-v37 proposal-state sequence changed")
        for name in (
            "input_mean_sha256", "cold_mean_sha256", "next_warm_mean_sha256",
            "winning_raw_blocks_sha256", "winning_sequence_sha256",
        ):
            require_sha256(planning[name], f"Winner-v37 {name}")
    if row["trace"][0]["action_sha256"] != expected_v36_first_action:
        raise ValueError("Winner-v37 first action does not reproduce Winner-v36")


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "controller", "cell_results", "summary", "execution",
        "sources", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v37.warm_started_shooting_feasibility_result.v1":
        raise ValueError("Winner-v37 result schema changed")
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
            != f"winner-v37-warm-started-shooting-feasibility-{attribution['github_run_id']}"
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
            raise ValueError("Winner-v37 imported attribution changed")
    expected_controller = {
        "configuration_ids": ["COM_X_NEG"],
        "controlled_action_indices": [2, 3, 4, 11, 12, 13],
        "duration_ticks": 250,
        "horizon_ticks": 8,
        "action_block_ticks": 2,
        "population": 64,
        "elites": 8,
        "iterations": 4,
        "initial_std": 0.20,
        "minimum_std": 0.03,
        "root_seed": 120120,
        "proposal_memory": PROPOSAL_MEMORY,
        "objective": (
            "lexicographic(survival_ticks,-maximum_abs_tilt,+minimum_base_z,"
            "-final_abs_tilt,-final_gyro,-action_delta_energy,-action_energy)"
        ),
    }
    if result.get("controller") != expected_controller:
        raise ValueError("Winner-v37 controller changed")
    if result.get("execution") != {
        "oracle_support_cells": 2, "optimizer_updates": 0,
        "locomotion_training_steps": 0, "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "runtime_oracle_or_action_wrapper_authorized": False,
        "pass_authorizes_only": (
            "one separately frozen full-configuration CPU warm-started oracle screen"
        ),
    }:
        raise ValueError("Winner-v37 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v36_result_lf_sha256": lf_sha256(V36_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v37 sources changed")
    v36 = json.loads(V36_RESULT.read_text(encoding="utf-8"))
    expected_first = {
        row["plant"]: row["trace"][0]["action_sha256"]
        for row in v36["cell_results"]
    }
    rows = result.get("cell_results")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("Winner-v37 cell count changed")
    for row in rows:
        _validate_row(row, expected_first[row["plant"]])
    if [row["plant"] for row in rows] != list(PLANTS):
        raise ValueError("Winner-v37 plant order changed")
    checks = {
        "exact_2_anchor_cells": len(rows) == 2,
        "all_first_actions_match_v36": all(row["first_action_matches_v36"] for row in rows),
        "all_later_ticks_use_warm_start": all(row["warm_active_after_tick0"] for row in rows),
        "all_cells_exercise_nontrivial_warm_mean": all(
            row["any_warm_mean_differs_from_cold"] for row in rows
        ),
        "all_selected_actions_graph_bounded": all(row["all_actions_bounded"] for row in rows),
        "all_cells_use_nonzero_control": all(row["any_nonzero_action"] for row in rows),
        "both_plants_pass_full_250_tick_support_gate": all(row["support_pass"] for row in rows),
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v37 checks are not rederived")
    terminal_ticks = [
        None if row["terminal"] is None else row["terminal"]["tick"] for row in rows
    ]
    v36_ticks = v36["summary"]["terminal_ticks"]
    summary = {
        "support_passes": sum(row["support_pass"] for row in rows),
        "terminal_ticks": terminal_ticks,
        "v36_terminal_ticks": v36_ticks,
        "terminal_tick_deltas_vs_v36": [
            (250 if tick is None else tick) - base
            for tick, base in zip(terminal_ticks, v36_ticks, strict=True)
        ],
        "maximum_abs_tilt_rad": max(row["episode"]["maximum_abs_tilt_rad"] for row in rows),
        "maximum_current_a": max(row["episode"]["maximum_current_a"] for row in rows),
        "maximum_torque_nm": max(row["episode"]["maximum_torque_nm"] for row in rows),
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v37 summary is not rederived")
    validity_names = {
        "exact_2_anchor_cells", "all_first_actions_match_v36",
        "all_later_ticks_use_warm_start", "all_cells_exercise_nontrivial_warm_mean",
        "all_selected_actions_graph_bounded", "all_cells_use_nonzero_control",
    }
    valid = all(checks[name] for name in validity_names)
    passed = valid and checks["both_plants_pass_full_250_tick_support_gate"]
    if not valid:
        status = "INVALID_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "INVALID_WARM_STARTED_SHOOTING_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "STATEFUL_PROPOSAL_COM_X_NEG_CONTROL_FEASIBLE"
        decision = "AUTHORIZE_FULL_CONFIGURATION_WARM_STARTED_ORACLE_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V37_WARM_STARTED_SHOOTING_FEASIBILITY"
        classification = "STATEFUL_PROPOSAL_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_WARM_STARTED_SHOOTING_PROPOSAL_MECHANISM"
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or result.get("status") != status or result.get("classification") != classification
        or result.get("decision") != decision
    ):
        raise ValueError("Winner-v37 decision changed")


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
        raise FileExistsError("Winner-v37 result is already imported")
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
        raise ValueError("Winner-v37 raw-result receipt changed")
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
            "# Winner-v37 warm-started shooting feasibility result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Full support passes: `{summary['support_passes']} / 2`",
            f"- Terminal ticks: `{summary['terminal_ticks']}`",
            f"- Terminal deltas versus V36: `{summary['terminal_tick_deltas_vs_v36']}`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "This is a simulator-oracle mechanism result. It is not a deployable",
            "controller, checkpoint, runtime wrapper, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
