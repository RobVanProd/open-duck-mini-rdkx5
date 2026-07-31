#!/usr/bin/env python3
"""Import one exact Winner-v12 calibrator HOLD diagnostic result."""

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
PREREGISTRATION = ANALYSIS / "winner_v12_calibrator_hold_diagnostic_preregistration.json"
FORMAL_RESULT = ANALYSIS / "winner_v12_calibrator_support_gate_result.json"
RUNNER = ROOT / "tools/run_winner_v12_calibrator_hold_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-hold-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v12_calibrator_hold_diagnostic_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v12-calibrator-hold-diagnostic-result.json"
RAW_RECEIPT_NAME = "winner-v12-calibrator-hold-diagnostic-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def lf_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("HOLD diagnostic artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("HOLD diagnostic artifact exceeds the size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if (
                member.is_absolute()
                or ".." in member.parts
                or "." in member.parts
                or "\\" in info.filename
                or info.flag_bits & 0x1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("HOLD diagnostic artifact has an unsafe member")
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
    require_sha256(artifact_zip_sha256, "HOLD diagnostic artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v12-calibrator-hold-diagnostic-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("HOLD diagnostic workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_predictor(row: Mapping[str, Any]) -> None:
    dimensions = row.get("per_dimension")
    if not isinstance(dimensions, list) or len(dimensions) != 50:
        raise ValueError("HOLD diagnostic predictor dimension set changed")
    expected_observations = list(range(0, 6)) + list(range(13, 41)) + list(
        range(83, 99)
    )
    expected_groups = (
        ["imu"] * 6
        + ["joint_position"] * 14
        + ["joint_velocity"] * 14
        + ["applied_target"] * 14
        + ["foot_contact"] * 2
    )
    for index, (dimension, observation_index, group) in enumerate(
        zip(dimensions, expected_observations, expected_groups, strict=True)
    ):
        if (
            dimension.get("auxiliary_index") != index
            or dimension.get("observation_index") != observation_index
            or dimension.get("group") != group
            or not all(
                isinstance(dimension.get(name), (int, float))
                and float(dimension[name]) >= 0.0
                for name in (
                    "target_std",
                    "learned_normalized_mse",
                    "constant_normalized_mse",
                )
            )
        ):
            raise ValueError("HOLD diagnostic predictor mapping changed")
    if (
        row.get("cell_count") != 16
        or int(row.get("adjacent_transition_count", 0)) <= 0
        or type(row.get("all_contact_targets_exactly_one")) is not bool
        or type(row.get("contact_target_std_exactly_1e_6")) is not bool
        or type(row.get("contact_fraction_at_least_0_99")) is not bool
        or type(row.get("learned_noncontact_strictly_below_constant")) is not bool
    ):
        raise ValueError("HOLD diagnostic predictor aggregate changed")


def validate_cell(row: Mapping[str, Any], *, zero_action: bool) -> None:
    require_sha256(row.get("trace_hashes", {}).get("observations"), "observation trace")
    require_sha256(row.get("trace_hashes", {}).get("actions"), "action trace")
    actions = row.get("action_statistics", {})
    if (
        type(row.get("support_pass")) is not bool
        or actions.get("tick_count", 0) <= 0
        or len(actions.get("peak_abs_by_joint", [])) != 14
        or len(actions.get("rms_by_joint", [])) != 14
        or len(actions.get("peak_abs_step_by_joint", [])) != 14
        or type(actions.get("all_zero")) is not bool
        or (zero_action and actions["all_zero"] is not True)
    ):
        raise ValueError("HOLD diagnostic cell schema changed")
    if not zero_action and type(row.get("formal_outcome_match")) is not bool:
        raise ValueError("HOLD diagnostic graph-formal comparison changed")


def validate_checkpoint(row: Mapping[str, Any], label: str) -> None:
    if row.get("label") != label or row.get("update") != {"half": 50, "final": 100}[label]:
        raise ValueError(f"HOLD diagnostic {label} checkpoint changed")
    require_sha256(row.get("checkpoint_sha256"), f"HOLD diagnostic {label} checkpoint")
    require_sha256(row.get("onnx_sha256"), f"HOLD diagnostic {label} ONNX")
    graph = row.get("graph_cells")
    zero = row.get("zero_action_cells")
    predictor = row.get("predictor_by_plant")
    classification = row.get("support_classification")
    if (
        not isinstance(graph, list)
        or len(graph) != 44
        or not isinstance(zero, list)
        or len(zero) != 16
        or not isinstance(predictor, dict)
        or set(predictor) != set(PLANTS)
        or not isinstance(classification, dict)
        or set(classification)
        != {
            "graph_fail_zero_pass",
            "graph_fail_zero_fail",
            "graph_pass_zero_pass",
            "graph_pass_zero_fail",
        }
    ):
        raise ValueError(f"HOLD diagnostic {label} population changed")
    for cell in graph:
        validate_cell(cell, zero_action=False)
    for cell in zero:
        validate_cell(cell, zero_action=True)
    for plant in PLANTS:
        validate_predictor(predictor[plant])
    classified = sum(len(value) for value in classification.values())
    if classified != 16 or len({tuple(pair) for values in classification.values() for pair in values}) != 16:
        raise ValueError(f"HOLD diagnostic {label} classification changed")
    expected_graph_failures = 16 if label == "half" else 14
    if (
        len(classification["graph_fail_zero_pass"])
        + len(classification["graph_fail_zero_fail"])
        != expected_graph_failures
    ):
        raise ValueError(f"HOLD diagnostic {label} formal failure count changed")
    checks = row.get("checks")
    if (
        not isinstance(checks, dict)
        or set(checks)
        != {
            "all_graph_outcomes_match_formal",
            "all_zero_action_cells_exactly_zero",
            "predictor_contact_std_exactly_1e_6",
            "predictor_contact_targets_exactly_one",
        }
        or not all(type(value) is bool for value in checks.values())
        or not all(checks.values())
    ):
        raise ValueError(f"HOLD diagnostic {label} checks changed")


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "checkpoint_results",
        "checks",
        "decision",
        "execution",
        "failed_checks",
        "findings",
        "schema_version",
        "sources",
        "status",
    }
    if set(result) != expected_fields:
        raise ValueError("HOLD diagnostic result schema changed")
    checks = result.get("checks")
    if (
        result.get("schema_version")
        != "winner_v12.calibrator_hold_diagnostic_result.v1"
        or result.get("status") != "PASS_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
        or result.get("decision") != "DIAGNOSTIC_ONLY_DO_NOT_TRAIN_OR_DEPLOY"
        or not isinstance(checks, dict)
        or not checks
        or not all(type(value) is bool for value in checks.values())
        or not all(checks.values())
        or result.get("failed_checks") != []
    ):
        raise ValueError("HOLD diagnostic result did not complete exactly")
    if result.get("execution") != {
        "graph_diagnostic_cells": 88,
        "zero_action_diagnostic_cells": 32,
        "training_steps": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("HOLD diagnostic execution boundary changed")
    if result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "result_authorizes": (
            "causal diagnosis and a separate prospective mechanism preregistration only"
        ),
    }:
        raise ValueError("HOLD diagnostic authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "formal_result_lf_sha256": lf_sha256(FORMAL_RESULT),
        "diagnostic_runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("HOLD diagnostic source identities changed")
    checkpoints = result.get("checkpoint_results")
    if not isinstance(checkpoints, list) or [row.get("label") for row in checkpoints] != [
        "half",
        "final",
    ]:
        raise ValueError("HOLD diagnostic checkpoint set changed")
    for row, label in zip(checkpoints, ("half", "final"), strict=True):
        validate_checkpoint(row, label)
    findings = result.get("findings")
    if (
        not isinstance(findings, dict)
        or set(findings)
        != {
            "all_formal_failed_pairs_pass_with_zero_action",
            "contact_floor_dominates_all_predictor_aggregates",
            "graph_fail_zero_fail_count",
            "graph_fail_zero_pass_count",
            "noncontact_predictor_beats_constant_all_aggregates",
        }
        or findings["graph_fail_zero_fail_count"]
        + findings["graph_fail_zero_pass_count"]
        != 30
        or findings["all_formal_failed_pairs_pass_with_zero_action"]
        is not (
            findings["graph_fail_zero_pass_count"] == 30
            and findings["graph_fail_zero_fail_count"] == 0
        )
    ):
        raise ValueError("HOLD diagnostic finding accounting changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-artifact-zip", type=Path, required=True)
    parser.add_argument("--verification-run-id", type=int, required=True)
    parser.add_argument("--verification-run-attempt", type=int, required=True)
    parser.add_argument("--verification-run-head-sha", required=True)
    parser.add_argument("--verification-artifact-id", type=int, required=True)
    parser.add_argument("--verification-artifact-name", required=True)
    parser.add_argument("--verification-artifact-digest", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v12 HOLD diagnostic is already imported")
    artifact_zip_sha = sha256(args.result_artifact_zip)
    attribution = repository_attribution(
        run_id=args.verification_run_id,
        run_attempt=args.verification_run_attempt,
        run_head_sha=args.verification_run_head_sha,
        artifact_id=args.verification_artifact_id,
        artifact_name=args.verification_artifact_name,
        artifact_digest=args.verification_artifact_digest,
        artifact_zip_sha256=artifact_zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.result_artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("HOLD diagnostic raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.result_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    findings = payload["findings"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator HOLD diagnostic result",
                "",
                f"- Status: `{payload['status']}`",
                f"- GitHub run: `{args.verification_run_id}` attempt `1`",
                f"- Run head: `{args.verification_run_head_sha}`",
                f"- Artifact ID / ZIP SHA-256: `{args.verification_artifact_id}` / `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Graph / zero-action cells: `88 / 32`",
                "- Training / locomotion / robot access: `0 / 0 / 0`",
                "",
                "## Frozen findings",
                "",
                f"- Contact floor dominates every predictor aggregate: `{findings['contact_floor_dominates_all_predictor_aggregates']}`",
                f"- Noncontact predictor beats constant everywhere: `{findings['noncontact_predictor_beats_constant_all_aggregates']}`",
                f"- Graph-fail / zero-pass pairs: `{findings['graph_fail_zero_pass_count']}`",
                f"- Graph-fail / zero-fail pairs: `{findings['graph_fail_zero_fail_count']}`",
                "",
                "The completed formal support gate remains HOLD. This diagnostic",
                "authorizes only a separate prospective mechanism preregistration;",
                "it does not authorize training, deployment, Gate 5, or hardware access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"IMPORTED_SHA256={sha256(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
