#!/usr/bin/env python3
"""Safely import one Winner-v22 normalized-predictor CPU result."""

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
CONTRACT = ANALYSIS / "winner_v22_normalized_predictor_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v21_normalized_semantics_attribution.json"
RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_cpu_contract.py"
OUTPUT_JSON = ANALYSIS / "winner_v22_normalized_predictor_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V22_NORMALIZED_PREDICTOR_CPU_RESULT_20260721.md"
RAW_RESULT = "winner-v22-normalized-predictor-cpu-result.json"
RAW_RECEIPT = "winner-v22-normalized-predictor-cpu-result.sha256"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


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


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    if type(value) is float:
        return math.isfinite(value)
    return True


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT, RAW_RECEIPT}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v22 CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 5_000_000:
            raise ValueError("Winner-v22 CPU artifact exceeds size ceiling")
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
                raise ValueError("Winner-v22 CPU artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_result(value: Mapping[str, Any]) -> None:
    status = value.get("status")
    decision = value.get("decision")
    passed = status == "PASS_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
    held = status == "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
    if (
        value.get("schema_version") != "winner_v22.normalized_predictor_cpu_result.v1"
        or not (passed or held)
        or decision
        != (
            "AUTHORIZE_SEPARATE_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_UPDATE_OR_TRAIN_WINNER_V22"
        )
        or value.get("source_snapshot")
        != {
            "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
            "bytes": 189027,
        }
        or value.get("execution")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("authority", {}).get("robot_clearance") is not False
        or value.get("authority", {}).get("training_executed") is not False
    ):
        raise ValueError("Winner-v22 CPU result schema changed")
    checks = value.get("checks")
    failed = value.get("failed_checks")
    if not isinstance(checks, Mapping) or not checks or not isinstance(failed, list):
        raise ValueError("Winner-v22 CPU checks changed")
    expected_failed = sorted(name for name, flag in checks.items() if flag is not True)
    if failed != expected_failed or (passed and failed):
        raise ValueError("Winner-v22 CPU classification does not match checks")
    if value.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v22 CPU result source identities changed")
    if not finite_tree(value):
        raise ValueError("Winner-v22 CPU result contains non-finite values")


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
        raise FileExistsError("refusing to overwrite Winner-v22 imported result")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v22-normalized-predictor-cpu-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v22 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    receipt = members[RAW_RECEIPT].decode("utf-8").strip().split()
    if len(receipt) != 2 or receipt[0] != raw_sha or PurePosixPath(receipt[1]).name != RAW_RESULT:
        raise ValueError("Winner-v22 raw-result receipt changed")
    raw = json.loads(members[RAW_RESULT].decode("utf-8"), parse_constant=reject_nonfinite)
    if not isinstance(raw, dict):
        raise ValueError("Winner-v22 raw result is not an object")
    validate_result(raw)
    result = dict(raw)
    result["repository_attribution"] = {
        "repository": "RobVanProd/open-duck-mini-rdkx5",
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "github_run_head_sha": args.run_head_sha,
        "github_artifact_id": args.artifact_id,
        "github_artifact_name": args.artifact_name,
        "github_artifact_digest": args.artifact_digest,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(members[RAW_RECEIPT]),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    objective = result.get("objective", {})
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v22 normalized-predictor CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                (
                    "- Corrected / old predictor loss: "
                    f"`{objective.get('corrected_predictor_loss', 0):.8g}` / "
                    f"`{objective.get('old_raw_coordinate_loss', 0):.8g}`"
                ),
                f"- Frozen corrected predictor scale: `{objective.get('balance', {}).get('predictor_scale')}`",
                "- Optimizer updates / support cells / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                "A pass authorizes only a separately frozen two-update CPU proof.",
                "It is not support training, locomotion, deployment, or robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
