#!/usr/bin/env python3
"""Strictly import the sole Winner-v47b corrected support-gate artifact."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v47b_support_gate_execution_correction.py"
WORKFLOW = ROOT / ".github/workflows/winner-v47b-support-gate-execution-correction.yml"
OUTPUT_JSON = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
OUTPUT_MD = (
    ANALYSIS / "WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION_RESULT_20260722.md"
)
RAW_RESULT_NAME = "winner-v47b-support-gate-execution-correction-result.json"
RAW_RECEIPT_NAME = "winner-v47b-support-gate-execution-correction-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def _load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("winner_v47b_result_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v47b runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER_MODULE = _load_runner()


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
    raise ValueError(f"nonfinite JSON value: {value}")


def read_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v47b artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v47b artifact exceeds size ceiling")
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
                raise ValueError("Winner-v47b artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def validate_result(value: Mapping[str, Any]) -> None:
    raw = dict(value)
    attribution = raw.pop("repository_attribution", None)
    RUNNER_MODULE.validate_corrected_result(raw)
    if attribution is None:
        return
    expected_fields = {
        "repository",
        "github_run_id",
        "github_run_attempt",
        "github_run_head_sha",
        "github_artifact_id",
        "github_artifact_name",
        "github_artifact_digest",
        "artifact_zip_sha256",
        "artifact_zip_bytes",
        "raw_result_sha256",
        "raw_result_receipt_sha256",
        "preregistration_lf_sha256",
        "workflow_lf_sha256",
        "runner_lf_sha256",
        "importer_lf_sha256",
        "superseded_failed_run_id",
        "superseded_failed_run_log_sha256",
    }
    if (
        not isinstance(attribution, Mapping)
        or set(attribution) != expected_fields
        or attribution.get("repository") != EXPECTED_REPOSITORY
        or attribution.get("github_run_attempt") != 1
        or type(attribution.get("github_run_id")) is not int
        or attribution["github_run_id"] <= 0
        or HEX40.fullmatch(str(attribution.get("github_run_head_sha"))) is None
        or type(attribution.get("github_artifact_id")) is not int
        or attribution["github_artifact_id"] <= 0
        or attribution.get("github_artifact_name")
        != (
            "winner-v47b-support-gate-execution-correction-"
            f"{attribution['github_run_id']}"
        )
        or attribution.get("github_artifact_digest")
        != f"sha256:{attribution.get('artifact_zip_sha256')}"
        or any(
            HEX64.fullmatch(str(attribution.get(name))) is None
            for name in (
                "artifact_zip_sha256",
                "raw_result_sha256",
                "raw_result_receipt_sha256",
            )
        )
        or attribution.get("preregistration_lf_sha256")
        != lf_sha256(PREREGISTRATION)
        or attribution.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
        or attribution.get("runner_lf_sha256") != lf_sha256(RUNNER)
        or attribution.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        or attribution.get("superseded_failed_run_id") != 29914159165
        or attribution.get("superseded_failed_run_log_sha256")
        != "db26d7477565dfa7d2eb20d4634bdd760bafc75cadf78f9dba931f3bb47ab1d5"
    ):
        raise ValueError("Winner-v47b imported attribution changed")


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
        raise FileExistsError("Winner-v47b result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name
        != f"winner-v47b-support-gate-execution-correction-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v47b workflow attribution changed")
    raw_bytes, receipt_bytes = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v47b raw receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    payload = dict(raw)
    payload["repository_attribution"] = {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "github_run_head_sha": args.run_head_sha,
        "github_artifact_id": args.artifact_id,
        "github_artifact_name": args.artifact_name,
        "github_artifact_digest": args.artifact_digest,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
        "superseded_failed_run_id": 29914159165,
        "superseded_failed_run_log_sha256": (
            "db26d7477565dfa7d2eb20d4634bdd760bafc75cadf78f9dba931f3bb47ab1d5"
        ),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v47b corrected formal support-gate result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Main cells / heldout repeats: `248 / 64`",
                "- Superseded failed V47 formal cells: `0`",
                "- Locomotion training / robot: `0 / 0`",
                "",
                "The correction changes provenance routing only; the frozen gate is unchanged.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
