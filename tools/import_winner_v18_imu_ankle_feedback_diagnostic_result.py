#!/usr/bin/env python3
"""Strictly import one hosted Winner-v18 IMU ankle-feedback result."""

from __future__ import annotations

import argparse
from collections import Counter
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
PREREGISTRATION = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
HOLD_ATTRIBUTION = (
    ANALYSIS / "winner_v17_support_action_combination_hold_attribution.json"
)
BASE_RUNNER = ROOT / "tools/run_winner_v16_support_action_direction_diagnostic.py"
RUNNER = ROOT / "tools/run_winner_v18_imu_ankle_feedback_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v18-imu-ankle-feedback-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v18-imu-ankle-feedback-result.json"
RAW_RECEIPT_NAME = "winner-v18-imu-ankle-feedback-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")


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
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v18 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v18 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute()
                or ".." in member.parts
                or "." in member.parts
                or "\\" in info.filename
                or info.flag_bits & 1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v18 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *,
    run_id: int,
    run_attempt: int,
    run_head_sha: str,
    artifact_id: int,
    artifact_name: str,
    artifact_digest: str,
    artifact_zip_sha256: str,
) -> dict[str, Any]:
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v18-imu-ankle-feedback-{run_id}"
        or HEX64_RE.fullmatch(artifact_zip_sha256) is None
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v18 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_intervention_result(
    row: Mapping[str, Any], intervention: Mapping[str, Any]
) -> None:
    expected_fields = {
        "activation_maximum",
        "activation_mean",
        "activation_minimum",
        "all_action_boundaries_exact",
        "all_intervention_formulas_exact",
        "all_source_previous_action_outputs_exact",
        "baseline_matches_formal",
        "cells",
        "failure_pitch_rad_range",
        "failure_tick_range",
        "intervention",
        "maximum_abs_action_delta_from_source",
        "mean_squared_action_delta_from_source",
        "support_failure_configuration_counts",
        "support_failure_count",
        "support_pass_count",
    }
    if set(row) != expected_fields or row["intervention"] != intervention:
        raise ValueError("Winner-v18 intervention schema changed")
    cells = row["cells"]
    if not isinstance(cells, list) or len(cells) != 12:
        raise ValueError("Winner-v18 intervention population changed")
    if len({(cell["configuration_id"], cell["plant"]) for cell in cells}) != 12:
        raise ValueError("Winner-v18 cell identity population changed")
    evidence = [cell["intervention_evidence"] for cell in cells]
    for cell, item in zip(cells, evidence, strict=True):
        if (
            cell["condition"] is not None
            or cell["intervention"] != intervention
            or cell["source_previous_action_out_exact"] is not True
            or item["source_previous_action_out_exact"] is not True
            or item["intervention_formula_bit_exact"] is not True
            or cell["maximum_action_delta_excess"] > 5.0e-7
            or not (
                0.0
                <= item["activation_minimum"]
                <= item["activation_mean"]
                <= item["activation_maximum"]
                <= 1.0
            )
            or not all(
                math.isfinite(value)
                for value in (
                    item["activation_minimum"],
                    item["activation_mean"],
                    item["activation_maximum"],
                    *item["pitch_proxy_rad_range"],
                    *item["pitch_rate_rad_s_range"],
                )
            )
        ):
            raise ValueError("Winner-v18 feedback evidence failed")
    failed = [cell for cell in cells if not cell["support_pass"]]
    expected_baseline = True if intervention["id"] == "BASELINE" else None
    if (
        row["support_failure_count"] != len(failed)
        or row["support_pass_count"] != len(cells) - len(failed)
        or row["support_failure_configuration_counts"]
        != dict(sorted(Counter(cell["configuration_id"] for cell in failed).items()))
        or row["all_action_boundaries_exact"] is not True
        or row["all_intervention_formulas_exact"] is not True
        or row["all_source_previous_action_outputs_exact"] is not True
        or row["baseline_matches_formal"] is not expected_baseline
        or row["activation_minimum"]
        != min(item["activation_minimum"] for item in evidence)
        or row["activation_maximum"]
        != max(item["activation_maximum"] for item in evidence)
        or row["activation_mean"]
        != sum(item["activation_mean"] for item in evidence) / 12.0
    ):
        raise ValueError("Winner-v18 intervention summary is not rederived")


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "baseline_reproduction",
        "checkpoint_results",
        "decision",
        "execution",
        "failed_validity_checks",
        "full_pass_candidates",
        "intervention_summary",
        "schema_version",
        "selected_direction",
        "sources",
        "status",
        "validity_checks",
    }
    if (
        set(result) != expected_fields
        or result["schema_version"] != "winner_v18.imu_ankle_feedback_diagnostic_result.v1"
        or result["status"] != "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        or result["decision"]
        != "NO_ONE_SIDED_IMU_ANKLE_FEEDBACK_PASSES_STOP_WITH_ATTRIBUTION"
        or result["failed_validity_checks"] != []
        or result["full_pass_candidates"] != []
        or result["selected_direction"] is not None
    ):
        raise ValueError("Winner-v18 decision changed")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    interventions = preregistration["frozen_screen"]["interventions"]
    if result["baseline_reproduction"] != preregistration["baseline_reproduction"]:
        raise ValueError("Winner-v18 baseline contract changed")
    expected_validity = {
        "exact_168_cells",
        "baseline_reproduces_all_24_formal_cells",
        "all_action_boundaries_exact",
        "all_intervention_formulas_exact",
        "all_source_previous_action_outputs_exact",
        "all_values_finite",
        "optimizer_updates_zero",
        "locomotion_and_robot_access_zero",
    }
    if (
        set(result["validity_checks"]) != expected_validity
        or not all(result["validity_checks"].values())
        or result["execution"]
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 168,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or result["authority"]
        != {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate CPU-only selected-feedback contract preregistration"
            ),
        }
    ):
        raise ValueError("Winner-v18 validity or authority changed")
    if result["sources"] != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
        "formal_result_lf_sha256": lf_sha256(FORMAL_RESULT),
        "hold_attribution_lf_sha256": lf_sha256(HOLD_ATTRIBUTION),
        "base_runner_lf_sha256": lf_sha256(BASE_RUNNER),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v18 sources changed")

    checkpoints = result["checkpoint_results"]
    if [row.get("label") for row in checkpoints] != ["half", "final"]:
        raise ValueError("Winner-v18 checkpoint set changed")
    rows_by_name: dict[str, list[Mapping[str, Any]]] = {
        intervention["id"]: [] for intervention in interventions
    }
    total_cells = 0
    for checkpoint, label, update in zip(
        checkpoints, ("half", "final"), (50, 100), strict=True
    ):
        expected_artifact = preregistration["training_artifact"][label]
        if (
            checkpoint["update"] != update
            or checkpoint["checkpoint_sha256"]
            != expected_artifact["snapshot"]["sha256"]
            or checkpoint["onnx_sha256"] != expected_artifact["graph"]["sha256"]
            or len(checkpoint["intervention_results"]) != 7
        ):
            raise ValueError(f"Winner-v18 {label} checkpoint changed")
        for row, intervention in zip(
            checkpoint["intervention_results"], interventions, strict=True
        ):
            validate_intervention_result(row, intervention)
            rows_by_name[intervention["id"]].append(row)
            total_cells += len(row["cells"])
    if total_cells != 168:
        raise ValueError("Winner-v18 total population changed")

    for intervention in interventions:
        name = intervention["id"]
        rows = rows_by_name[name]
        summary = result["intervention_summary"][name]
        expected = {
            "intervention": intervention,
            "half_failure_count": rows[0]["support_failure_count"],
            "final_failure_count": rows[1]["support_failure_count"],
            "passes_both_checkpoints": all(
                row["support_failure_count"] == 0 for row in rows
            ),
            "maximum_abs_action_delta_from_source": max(
                row["maximum_abs_action_delta_from_source"] for row in rows
            ),
            "mean_squared_action_delta_from_source": sum(
                row["mean_squared_action_delta_from_source"] for row in rows
            )
            / 2.0,
            "activation_minimum": min(row["activation_minimum"] for row in rows),
            "activation_mean": sum(row["activation_mean"] for row in rows) / 2.0,
            "activation_maximum": max(row["activation_maximum"] for row in rows),
        }
        if summary != expected or summary["passes_both_checkpoints"] is not False:
            raise ValueError("Winner-v18 intervention summary changed")


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
        raise FileExistsError("Winner-v18 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha,
        artifact_id=args.artifact_id,
        artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v18 raw-result receipt changed")
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
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summaries = payload["intervention_summary"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v18 IMU ankle-feedback diagnostic result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Full pass candidates: `0`",
                "- Constant ankle failures half / final: "
                f"`{summaries['CONSTANT_ANKLE_POS']['half_failure_count']} / "
                f"{summaries['CONSTANT_ANKLE_POS']['final_failure_count']}`",
                "- Combined feedback failures half / final: "
                f"`{summaries['TILT_RATE_BACKWARD']['half_failure_count']} / "
                f"{summaries['TILT_RATE_BACKWARD']['final_failure_count']}`",
                "- Optimizer / robot access: `0 / 0`",
                "",
                "The deployable IMU feedback is valid but supplies less corrective action",
                "than the same-ceiling constant ankle intervention and does not pass the",
                "severe negative-X cells. No closest failing mode advances.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
