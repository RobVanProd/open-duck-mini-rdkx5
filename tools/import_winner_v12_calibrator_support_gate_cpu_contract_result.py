#!/usr/bin/env python3
"""Import one exact Winner-v12 zero-cell support-gate CPU result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
CPU_CONTRACT = ANALYSIS / "winner_v12_calibrator_support_gate_cpu_contract.json"
OUTPUT_JSON = (
    ANALYSIS / "winner_v12_calibrator_support_gate_cpu_contract_result.json"
)
OUTPUT_MD = (
    ANALYSIS / "WINNER_V12_CALIBRATOR_SUPPORT_GATE_CPU_CONTRACT_RESULT_20260721.md"
)
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-support-gate-cpu-contract.yml"
CHECKER = ROOT / "tools/check_winner_v12_calibrator_support_gate_cpu_contract.py"
RAW_RESULT_NAME = "winner-v12-calibrator-support-gate-cpu-contract-result.json"
RAW_RECEIPT_NAME = "winner-v12-calibrator-support-gate-cpu-contract-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
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
            raise ValueError("zero-cell result artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("zero-cell result artifact exceeds the size ceiling")
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
                raise ValueError("zero-cell result artifact contains an unsafe member")
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
    require_sha256(artifact_zip_sha256, "zero-cell result artifact")
    expected_name = f"winner-v12-calibrator-support-gate-cpu-contract-{run_id}"
    if (
        run_id <= 0
        or run_attempt != 1
        or GIT_OID_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != expected_name
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("zero-cell workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_raw_result(raw: dict[str, Any]) -> None:
    expected_fields = {
        "authority",
        "checkpoint_graph_contracts",
        "checks",
        "contract_lf_sha256",
        "decision",
        "execution",
        "failed_checks",
        "immutable_inputs",
        "schema_version",
        "software_versions",
        "status",
        "training_files",
        "transport_primitives",
    }
    if set(raw) != expected_fields:
        raise ValueError("raw zero-cell result schema changed")
    sys.path.insert(0, str(TOOLS))
    import build_winner_v12_calibrator_support_gate_launch as launch_builder

    launch_builder.validate_zero_cell_result(
        raw,
        lf_sha256(CPU_CONTRACT),
        require_repository_attribution=False,
    )


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
        raise FileExistsError("Winner-v12 zero-cell result is already imported")
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
    expected_receipt = f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode()
    if receipt_bytes != expected_receipt:
        raise ValueError("zero-cell raw result hash receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"))
    validate_raw_result(raw)
    payload = dict(raw)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.result_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "cpu_contract_path": str(CPU_CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "cpu_contract_lf_sha256": lf_sha256(CPU_CONTRACT),
        "workflow_path": str(WORKFLOW.relative_to(ROOT)).replace("\\", "/"),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "checker_lf_sha256": lf_sha256(CHECKER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator support-gate zero-cell result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Verification run: `{args.verification_run_id}` attempt `1`",
                f"- Verification head: `{args.verification_run_head_sha}`",
                f"- Verification artifact ID: `{args.verification_artifact_id}`",
                f"- Artifact ZIP SHA-256: `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                f"- CPU contract SHA-256: `{lf_sha256(CPU_CONTRACT)}`",
                "- Formal/heldout cells, locomotion, robot access: `0 / 0 / 0 / 0`",
                "",
                "The committed result is bound to the exact zero-cell Actions artifact",
                "and frozen CPU contract. It authorizes only the separately frozen",
                "offline support gate; it does not authorize locomotion, deployment,",
                "Gate 5, or robot access.",
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
