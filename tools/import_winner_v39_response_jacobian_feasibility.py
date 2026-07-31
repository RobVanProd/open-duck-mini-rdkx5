#!/usr/bin/env python3
"""Safely import the sole Winner-v39 response-Jacobian feasibility result."""

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
PREREGISTRATION = ANALYSIS / "winner_v39_response_jacobian_feasibility_preregistration.json"
V38_RESULT = ANALYSIS / "winner_v38_mirrored_pitch_shooting_feasibility_result.json"
RUNNER = ROOT / "tools/run_winner_v39_response_jacobian_feasibility.py"
WORKFLOW = ROOT / ".github/workflows/winner-v39-response-jacobian-feasibility.yml"
OUTPUT_JSON = ANALYSIS / "winner_v39_response_jacobian_feasibility_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v39-response-jacobian-feasibility-result.json"
RAW_RECEIPT_NAME = "winner-v39-response-jacobian-feasibility-result.sha256"
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


def require_finite_vector(value: Any, length: int, label: str) -> list[float]:
    if (
        not isinstance(value, list) or len(value) != length
        or any(type(item) not in {int, float} or not math.isfinite(item) for item in value)
    ):
        raise ValueError(f"{label} vector changed")
    return [float(item) for item in value]


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v39 artifact inventory changed")
        if sum(item.file_size for item in infos) > 250_000_000:
            raise ValueError("Winner-v39 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v39 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v39 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v39-response-jacobian-feasibility-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v39 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _validate_rollout_receipt(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "valid_ticks", "terminal", "response", "action_sequence_sha256",
    }:
        raise ValueError(f"Winner-v39 {label} receipt changed")
    if type(value["valid_ticks"]) is not int or value["valid_ticks"] not in range(0, 9):
        raise ValueError(f"Winner-v39 {label} valid-tick count changed")
    if value["terminal"] is not None and not isinstance(value["terminal"], Mapping):
        raise ValueError(f"Winner-v39 {label} terminal changed")
    require_finite_vector(value["response"], 2, f"Winner-v39 {label} response")
    require_sha256(value["action_sequence_sha256"], f"Winner-v39 {label} actions")


def _validate_planning(value: Any) -> None:
    fields = {
        "baseline_target_sha256", "baseline", "finite_difference_steps",
        "perturbations", "jacobian_sha256", "jacobian_rank", "singular_values",
        "lstsq_residuals", "unclipped_correction_sha256", "clipped_correction",
        "target_sha256", "predicted_response",
    }
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("Winner-v39 planning receipt changed")
    for name in (
        "baseline_target_sha256", "jacobian_sha256",
        "unclipped_correction_sha256", "target_sha256",
    ):
        require_sha256(value[name], f"Winner-v39 {name}")
    _validate_rollout_receipt(value["baseline"], "baseline")
    steps = require_finite_vector(
        value["finite_difference_steps"], 3, "Winner-v39 finite-difference"
    )
    if any(step <= 0.0 for step in steps):
        raise ValueError("Winner-v39 finite-difference step changed")
    if type(value["jacobian_rank"]) is not int or value["jacobian_rank"] not in {0, 1, 2}:
        raise ValueError("Winner-v39 Jacobian rank changed")
    singular_values = require_finite_vector(
        value["singular_values"], 2, "Winner-v39 singular values"
    )
    if any(item < 0.0 for item in singular_values):
        raise ValueError("Winner-v39 singular values changed")
    if not isinstance(value["lstsq_residuals"], list) or value["lstsq_residuals"]:
        raise ValueError("Winner-v39 underdetermined least-squares residual changed")
    correction = require_finite_vector(
        value["clipped_correction"], 3, "Winner-v39 correction"
    )
    if any(abs(item) > step + 1.0e-12 for item, step in zip(correction, steps)):
        raise ValueError("Winner-v39 correction exceeds frozen bound")
    require_finite_vector(value["predicted_response"], 2, "Winner-v39 prediction")
    perturbations = value["perturbations"]
    if not isinstance(perturbations, list) or len(perturbations) != 3:
        raise ValueError("Winner-v39 perturbation count changed")
    for axis, perturbation in enumerate(perturbations):
        if not isinstance(perturbation, Mapping) or set(perturbation) != {
            "axis", "minus_target_sha256", "plus_target_sha256", "denominator",
            "minus", "plus",
        } or perturbation["axis"] != axis:
            raise ValueError("Winner-v39 perturbation identity changed")
        require_sha256(perturbation["minus_target_sha256"], "Winner-v39 minus target")
        require_sha256(perturbation["plus_target_sha256"], "Winner-v39 plus target")
        denominator = perturbation["denominator"]
        if type(denominator) not in {int, float} or not math.isfinite(denominator) or denominator <= 0:
            raise ValueError("Winner-v39 perturbation denominator changed")
        _validate_rollout_receipt(perturbation["minus"], f"axis-{axis} minus")
        _validate_rollout_receipt(perturbation["plus"], f"axis-{axis} plus")


def _validate_row(row: Mapping[str, Any]) -> None:
    fields = {
        "configuration_id", "configuration_sha256", "plant",
        "controlled_action_indices", "terminal", "episode", "support_pass",
        "all_actions_bounded", "all_jacobians_full_row_rank", "any_nonzero_action",
        "action_trace_sha256", "trace",
    }
    if set(row) != fields:
        raise ValueError("Winner-v39 cell schema changed")
    if (
        row["configuration_id"] != "COM_X_NEG" or row["plant"] not in PLANTS
        or row["controlled_action_indices"] != [2, 3, 4, 11, 12, 13]
        or any(type(row[name]) is not bool for name in (
            "support_pass", "all_actions_bounded",
            "all_jacobians_full_row_rank", "any_nonzero_action",
        ))
        or not isinstance(row["episode"], Mapping)
        or not isinstance(row["trace"], list)
        or len(row["trace"]) not in range(1, 251)
    ):
        raise ValueError("Winner-v39 cell identity or type changed")
    require_sha256(row["configuration_sha256"], "Winner-v39 configuration")
    require_sha256(row["action_trace_sha256"], "Winner-v39 action trace")
    if row["terminal"] is None:
        if len(row["trace"]) != 250:
            raise ValueError("Winner-v39 unterminated cell length changed")
    elif not isinstance(row["terminal"], Mapping) or row["terminal"].get("tick") != len(row["trace"]) - 1:
        raise ValueError("Winner-v39 terminal tick changed")
    if row["support_pass"] and row["terminal"] is not None:
        raise ValueError("Winner-v39 terminal cell cannot pass")
    for tick, item in enumerate(row["trace"]):
        if set(item) != {"tick", "action_sha256", "planning", "transition"} or item["tick"] != tick:
            raise ValueError("Winner-v39 tick trace changed")
        require_sha256(item["action_sha256"], "Winner-v39 tick action")
        if not isinstance(item["transition"], Mapping):
            raise ValueError("Winner-v39 transition receipt changed")
        _validate_planning(item["planning"])
    for name in ("maximum_abs_tilt_rad", "maximum_current_a", "maximum_torque_nm"):
        value = row["episode"].get(name)
        if type(value) not in {int, float} or not math.isfinite(value):
            raise ValueError(f"Winner-v39 episode {name} changed")


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "controller", "cell_results", "summary", "execution",
        "sources", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v39.response_jacobian_feasibility_result.v1":
        raise ValueError("Winner-v39 result schema changed")
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
            != f"winner-v39-response-jacobian-feasibility-{attribution['github_run_id']}"
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
            raise ValueError("Winner-v39 imported attribution changed")
    expected_controller = {
        "configuration_ids": ["COM_X_NEG"],
        "controlled_action_indices": [2, 3, 4, 11, 12, 13],
        "response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"],
        "control_dimensions": ["hip_pitch_magnitude", "knee", "ankle"],
        "duration_ticks": 250,
        "response_horizon_ticks": 8,
        "finite_difference_scale": "minimum paired graph action delta per mirrored axis",
        "solver": "numpy.linalg.lstsq(rcond=None), minimum-norm correction",
        "correction_bound": "one finite-difference step per mirrored axis",
    }
    if result.get("controller") != expected_controller:
        raise ValueError("Winner-v39 controller changed")
    if result.get("execution") != {
        "response_jacobian_cells": 2, "optimizer_updates": 0,
        "locomotion_training_steps": 0, "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "runtime_oracle_or_action_wrapper_authorized": False,
        "pass_authorizes_only": "one separately frozen response-Jacobian teacher contract",
    }:
        raise ValueError("Winner-v39 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v38_result_lf_sha256": lf_sha256(V38_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v39 sources changed")
    rows = result.get("cell_results")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("Winner-v39 cell count changed")
    for row in rows:
        _validate_row(row)
    if [row["plant"] for row in rows] != list(PLANTS):
        raise ValueError("Winner-v39 plant order changed")
    checks = {
        "exact_2_anchor_cells": len(rows) == 2,
        "all_response_jacobians_full_row_rank": all(
            row["all_jacobians_full_row_rank"] for row in rows
        ),
        "all_selected_actions_graph_bounded": all(row["all_actions_bounded"] for row in rows),
        "all_cells_use_nonzero_control": all(row["any_nonzero_action"] for row in rows),
        "both_plants_pass_full_250_tick_support_gate": all(row["support_pass"] for row in rows),
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v39 checks are not rederived")
    v38 = json.loads(V38_RESULT.read_text(encoding="utf-8"))
    summary = {
        "support_passes": sum(row["support_pass"] for row in rows),
        "terminal_ticks": [
            None if row["terminal"] is None else row["terminal"]["tick"] for row in rows
        ],
        "v38_terminal_ticks": v38["summary"]["terminal_ticks"],
        "maximum_abs_tilt_rad": max(row["episode"]["maximum_abs_tilt_rad"] for row in rows),
        "maximum_current_a": max(row["episode"]["maximum_current_a"] for row in rows),
        "maximum_torque_nm": max(row["episode"]["maximum_torque_nm"] for row in rows),
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v39 summary is not rederived")
    validity_names = {
        "exact_2_anchor_cells", "all_response_jacobians_full_row_rank",
        "all_selected_actions_graph_bounded", "all_cells_use_nonzero_control",
    }
    valid = all(checks[name] for name in validity_names)
    passed = valid and checks["both_plants_pass_full_250_tick_support_gate"]
    if not valid:
        status = "INVALID_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "INVALID_RESPONSE_JACOBIAN_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "LOCAL_RESPONSE_JACOBIAN_COM_X_NEG_CONTROL_FEASIBLE"
        decision = "AUTHORIZE_RESPONSE_JACOBIAN_TEACHER_CONTRACT_ONLY"
    else:
        status = "HOLD_WINNER_V39_RESPONSE_JACOBIAN_FEASIBILITY"
        classification = "LOCAL_RESPONSE_JACOBIAN_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_LOCAL_RESPONSE_JACOBIAN_CONTROLLER"
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or result.get("status") != status or result.get("classification") != classification
        or result.get("decision") != decision
    ):
        raise ValueError("Winner-v39 decision changed")


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
        raise FileExistsError("Winner-v39 result is already imported")
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
        raise ValueError("Winner-v39 raw-result receipt changed")
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
            "# Winner-v39 response-Jacobian feasibility result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Full support passes: `{summary['support_passes']} / 2`",
            f"- Terminal ticks: `{summary['terminal_ticks']}`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "This is a simulator-oracle controller-family result. It is not a",
            "deployable controller, checkpoint, runtime wrapper, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
