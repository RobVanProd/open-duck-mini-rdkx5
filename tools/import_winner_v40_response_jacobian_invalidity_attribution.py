#!/usr/bin/env python3
"""Safely import the sole Winner-v40 saved-result invalidity attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_preregistration.json"
)
V39_RESULT = ANALYSIS / "winner_v39_response_jacobian_feasibility_result.json"
RUNNER = ROOT / "tools/run_winner_v40_response_jacobian_invalidity_attribution.py"
WORKFLOW = ROOT / ".github/workflows/winner-v40-response-jacobian-invalidity-attribution.yml"
OUTPUT_JSON = ANALYSIS / "winner_v40_response_jacobian_invalidity_attribution_result.json"
OUTPUT_MD = (
    ANALYSIS / "WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION_RESULT_20260722.md"
)
RAW_RESULT_NAME = "winner-v40-response-jacobian-invalidity-attribution-result.json"
RAW_RECEIPT_NAME = "winner-v40-response-jacobian-invalidity-attribution-result.sha256"
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
            raise ValueError("Winner-v40 artifact inventory changed")
        if sum(item.file_size for item in infos) > 5_000_000:
            raise ValueError("Winner-v40 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v40 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v40 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v40-response-jacobian-invalidity-attribution-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v40 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _validate_event(event: Mapping[str, Any]) -> None:
    if set(event) != {
        "tick", "jacobian_rank", "singular_values", "zero_response_axes",
        "terminal_truncated_zero_response_axes",
        "minimum_zero_columns_for_recorded_rank",
        "terminal_truncation_accounts_for_rank_loss",
    } or type(event["tick"]) is not int or event["tick"] < 0:
        raise ValueError("Winner-v40 rank-loss event changed")
    rank = event["jacobian_rank"]
    if type(rank) is not int or rank not in {0, 1}:
        raise ValueError("Winner-v40 rank-loss value changed")
    singular = event["singular_values"]
    if (
        not isinstance(singular, list) or len(singular) != 2
        or any(type(value) not in {int, float} or not math.isfinite(value) for value in singular)
    ):
        raise ValueError("Winner-v40 singular values changed")
    for name in ("zero_response_axes", "terminal_truncated_zero_response_axes"):
        axes = event[name]
        if not isinstance(axes, list) or sorted(set(axes)) != axes or any(
            type(axis) is not int or axis not in {0, 1, 2} for axis in axes
        ):
            raise ValueError("Winner-v40 zero-response axes changed")
    if (
        event["minimum_zero_columns_for_recorded_rank"] != 3 - rank
        or type(event["terminal_truncation_accounts_for_rank_loss"]) is not bool
        or event["terminal_truncation_accounts_for_rank_loss"]
        != (
            len(event["terminal_truncated_zero_response_axes"])
            >= event["minimum_zero_columns_for_recorded_rank"]
        )
    ):
        raise ValueError("Winner-v40 rank-loss attribution changed")


def _validate_row(row: Mapping[str, Any]) -> None:
    if set(row) != {
        "plant", "source_support_pass", "source_terminal_tick", "v38_terminal_tick",
        "terminal_tick_delta_vs_v38", "first_rank_loss_tick", "rank_loss_ticks",
        "ticks_from_first_rank_loss_to_terminal", "all_pre_loss_jacobians_full_row_rank",
        "all_rank_losses_in_terminal_fringe",
        "all_rank_losses_accounted_for_by_terminal_truncation",
        "source_actions_graph_bounded", "source_used_nonzero_control",
        "source_terminated_earlier_than_v38", "rank_loss_events",
    } or row["plant"] not in PLANTS:
        raise ValueError("Winner-v40 cell attribution schema changed")
    for name in (
        "source_support_pass", "all_pre_loss_jacobians_full_row_rank",
        "all_rank_losses_in_terminal_fringe",
        "all_rank_losses_accounted_for_by_terminal_truncation",
        "source_actions_graph_bounded", "source_used_nonzero_control",
        "source_terminated_earlier_than_v38",
    ):
        if type(row[name]) is not bool:
            raise ValueError("Winner-v40 cell attribution type changed")
    for name in (
        "source_terminal_tick", "v38_terminal_tick", "terminal_tick_delta_vs_v38",
        "first_rank_loss_tick", "ticks_from_first_rank_loss_to_terminal",
    ):
        if type(row[name]) is not int:
            raise ValueError("Winner-v40 cell attribution integer changed")
    events = row["rank_loss_events"]
    if not isinstance(events, list) or not events:
        raise ValueError("Winner-v40 rank-loss events absent")
    for event in events:
        _validate_event(event)
    if (
        row["rank_loss_ticks"] != [event["tick"] for event in events]
        or row["first_rank_loss_tick"] != row["rank_loss_ticks"][0]
        or row["terminal_tick_delta_vs_v38"]
        != row["source_terminal_tick"] - row["v38_terminal_tick"]
        or row["ticks_from_first_rank_loss_to_terminal"]
        != row["source_terminal_tick"] - row["first_rank_loss_tick"]
    ):
        raise ValueError("Winner-v40 cell attribution arithmetic changed")


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "cell_attribution", "summary", "execution", "sources",
        "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != (
        "winner_v40.response_jacobian_invalidity_attribution_result.v1"
    ):
        raise ValueError("Winner-v40 result schema changed")
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
            != f"winner-v40-response-jacobian-invalidity-attribution-{attribution['github_run_id']}"
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
            raise ValueError("Winner-v40 imported attribution changed")
    if result.get("execution") != {
        "saved_result_audits": 1, "simulation_cells": 0, "optimizer_updates": 0,
        "locomotion_training_steps": 0, "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "v39_rerun_authorized": False,
        "simulation_or_training_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separately frozen nonlocal support-controller feasibility design"
        ),
    }:
        raise ValueError("Winner-v40 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v39_result_lf_sha256": lf_sha256(V39_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v40 sources changed")
    rows = result.get("cell_attribution")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("Winner-v40 cell attribution count changed")
    for row in rows:
        _validate_row(row)
    if [row["plant"] for row in rows] != list(PLANTS):
        raise ValueError("Winner-v40 plant order changed")
    checks = {
        "exact_two_saved_source_cells": len(rows) == 2,
        "all_pre_loss_jacobians_full_row_rank": all(
            row["all_pre_loss_jacobians_full_row_rank"] for row in rows
        ),
        "all_rank_losses_in_final_two_tick_terminal_fringe": all(
            row["all_rank_losses_in_terminal_fringe"] for row in rows
        ),
        "all_rank_losses_accounted_for_by_terminal_truncated_identical_responses": all(
            row["all_rank_losses_accounted_for_by_terminal_truncation"] for row in rows
        ),
        "both_recorded_controllers_used_bounded_nonzero_actions": all(
            row["source_actions_graph_bounded"] and row["source_used_nonzero_control"]
            for row in rows
        ),
        "both_recorded_controllers_failed_support": all(
            not row["source_support_pass"] for row in rows
        ),
        "both_recorded_controllers_terminate_earlier_than_v38": all(
            row["source_terminated_earlier_than_v38"] for row in rows
        ),
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v40 checks are not rederived")
    v39 = json.loads(V39_RESULT.read_text(encoding="utf-8"))
    summary = {
        "source_support_passes": v39["summary"]["support_passes"],
        "source_terminal_ticks": v39["summary"]["terminal_ticks"],
        "v38_terminal_ticks": v39["summary"]["v38_terminal_ticks"],
        "first_rank_loss_ticks": [row["first_rank_loss_tick"] for row in rows],
        "rank_loss_tick_counts": [len(row["rank_loss_ticks"]) for row in rows],
        "terminal_tick_deltas_vs_v38": [
            row["terminal_tick_delta_vs_v38"] for row in rows
        ],
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v40 summary is not rederived")
    passed = all(checks.values())
    expected = (
        (
            "PASS_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION",
            "TERMINAL_TRUNCATION_EXPLAINS_RANK_INVALIDITY_NOT_SUPPORT_FAILURE",
            "CLOSE_EXACT_V39_CONTROLLER_WITHOUT_RERUN",
        )
        if passed else (
            "HOLD_WINNER_V40_RESPONSE_JACOBIAN_INVALIDITY_ATTRIBUTION",
            "V39_INVALIDITY_NOT_FULLY_ATTRIBUTED",
            "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        )
    )
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or (result.get("status"), result.get("classification"), result.get("decision"))
        != expected
    ):
        raise ValueError("Winner-v40 decision changed")


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
        raise FileExistsError("Winner-v40 result is already imported")
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
        raise ValueError("Winner-v40 raw-result receipt changed")
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
            "# Winner-v40 response-Jacobian invalidity attribution result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- First rank-loss ticks: `{summary['first_rank_loss_ticks']}`",
            f"- Source terminal ticks: `{summary['source_terminal_ticks']}`",
            "- Simulation / optimizer / locomotion / robot: `0 / 0 / 0 / 0`", "",
            "This attributes a committed result only. It does not rerun V39, select a",
            "checkpoint, authorize training or simulation, or grant robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
