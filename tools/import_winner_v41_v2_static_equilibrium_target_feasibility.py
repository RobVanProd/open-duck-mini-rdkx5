#!/usr/bin/env python3
"""Safely import the sole corrected Winner-v41-v2 static-equilibrium result."""

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
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
import sys
sys.path.insert(0, str(TOOLS))

import import_winner_v41_static_equilibrium_target_feasibility as base_import  # noqa: E402


BASE_PREREGISTRATION = (
    ANALYSIS / "winner_v41_static_equilibrium_target_feasibility_preregistration.json"
)
BASE_RUNNER = ROOT / "tools/run_winner_v41_static_equilibrium_target_feasibility.py"
CORRECTION = ANALYSIS / "winner_v41_v2_runner_correction_preregistration.json"
CORRECTION_RUNNER = ROOT / "tools/run_winner_v41_v2_static_equilibrium_target_feasibility.py"
FAILURE_RECEIPT = ANALYSIS / "winner_v41_first_attempt_failure_receipt.json"
WORKFLOW = ROOT / ".github/workflows/winner-v41-v2-static-equilibrium-target-feasibility.yml"
OUTPUT_JSON = ANALYSIS / "winner_v41_v2_static_equilibrium_target_feasibility_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V41_V2_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v41-v2-static-equilibrium-target-feasibility-result.json"
RAW_RECEIPT_NAME = "winner-v41-v2-static-equilibrium-target-feasibility-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "base_preregistration_lf_sha256",
    "base_runner_lf_sha256", "correction_preregistration_lf_sha256",
    "correction_runner_lf_sha256", "first_attempt_failure_receipt_lf_sha256",
    "workflow_lf_sha256", "importer_lf_sha256",
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
            raise ValueError("Winner-v41-v2 artifact inventory changed")
        if sum(item.file_size for item in infos) > 250_000_000:
            raise ValueError("Winner-v41-v2 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v41-v2 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v41-v2 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v41-v2-static-equilibrium-target-feasibility-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v41-v2 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def base_value(value: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("repository_attribution", None)
    result.pop("correction", None)
    result["schema_version"] = "winner_v41.static_equilibrium_target_feasibility_result.v1"
    sources = dict(result["sources"])
    sources.pop("correction_preregistration_lf_sha256", None)
    sources.pop("correction_runner_lf_sha256", None)
    sources.pop("first_attempt_failure_receipt_lf_sha256", None)
    result["sources"] = sources
    return result


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "screen", "candidate_results", "selection", "summary",
        "execution", "sources", "authority", "correction",
    }
    if frozenset(result) not in {
        frozenset(expected_fields), frozenset(expected_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v41.static_equilibrium_target_feasibility_result.v2":
        raise ValueError("Winner-v41-v2 result schema changed")
    correction = result.get("correction")
    if correction != {
        "first_attempt_run_id": 29901924055,
        "first_attempt_candidate_plant_cells": 0,
        "failure_receipt_lf_sha256": lf_sha256(FAILURE_RECEIPT),
        "correction_preregistration_lf_sha256": lf_sha256(CORRECTION),
        "correction_runner_lf_sha256": lf_sha256(CORRECTION_RUNNER),
        "scope": "single-target mirror expansion shape only",
    }:
        raise ValueError("Winner-v41-v2 correction attribution changed")
    expected_sources = {
        **base_value(result)["sources"],
        "correction_preregistration_lf_sha256": lf_sha256(CORRECTION),
        "correction_runner_lf_sha256": lf_sha256(CORRECTION_RUNNER),
        "first_attempt_failure_receipt_lf_sha256": lf_sha256(FAILURE_RECEIPT),
    }
    if result.get("sources") != expected_sources:
        raise ValueError("Winner-v41-v2 sources changed")
    base_import.validate_result(base_value(result))
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
            != f"winner-v41-v2-static-equilibrium-target-feasibility-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(HEX64_RE.fullmatch(str(attribution.get(name))) is None for name in (
                "artifact_zip_sha256", "raw_result_sha256", "raw_result_receipt_sha256",
                "base_preregistration_lf_sha256", "base_runner_lf_sha256",
                "correction_preregistration_lf_sha256", "correction_runner_lf_sha256",
                "first_attempt_failure_receipt_lf_sha256", "workflow_lf_sha256",
                "importer_lf_sha256",
            ))
            or attribution["base_preregistration_lf_sha256"] != lf_sha256(BASE_PREREGISTRATION)
            or attribution["base_runner_lf_sha256"] != lf_sha256(BASE_RUNNER)
            or attribution["correction_preregistration_lf_sha256"] != lf_sha256(CORRECTION)
            or attribution["correction_runner_lf_sha256"] != lf_sha256(CORRECTION_RUNNER)
            or attribution["first_attempt_failure_receipt_lf_sha256"] != lf_sha256(FAILURE_RECEIPT)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v41-v2 imported attribution changed")


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
        raise FileExistsError("Winner-v41-v2 result is already imported")
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
        raise ValueError("Winner-v41-v2 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "base_preregistration_lf_sha256": lf_sha256(BASE_PREREGISTRATION),
        "base_runner_lf_sha256": lf_sha256(BASE_RUNNER),
        "correction_preregistration_lf_sha256": lf_sha256(CORRECTION),
        "correction_runner_lf_sha256": lf_sha256(CORRECTION_RUNNER),
        "first_attempt_failure_receipt_lf_sha256": lf_sha256(FAILURE_RECEIPT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
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
            "# Winner-v41-v2 static-equilibrium target feasibility result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            "- Preserved failed run: `29901924055`, zero candidates",
            f"- Shared support targets: `{summary['shared_support_pass_count']} / 729`",
            f"- Selected coordinates: `{summary['selected_coordinates']}`",
            f"- Selected terminal ticks: `{summary['selected_terminal_ticks']}`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "Only the first-attempt target-expansion shape defect is corrected. This",
            "is not a runtime target, checkpoint, deployment, or robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
