#!/usr/bin/env python3
"""Safely import one Winner-v22 100-update normalized-predictor artifact."""

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
PREREGISTRATION = ANALYSIS / "winner_v22_normalized_predictor_training_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v22_normalized_predictor_two_update_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_training.py"
OUTPUT_JSON = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_RESULT_20260721.md"
RAW_RESULT = "winner-v22-normalized-predictor-training-result.json"
RAW_RECEIPT = "winner-v22-normalized-predictor-training-result.sha256"
WORK = "winner-v22-normalized-predictor-training-work"
HEX40 = re.compile(r"[0-9a-f]{40}")


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


def artifact_members() -> set[str]:
    return {
        RAW_RESULT,
        RAW_RECEIPT,
        *(f"{WORK}/snapshots/snapshot_normalized_predictor_update_{i:03d}.npz" for i in range(1, 101)),
        f"{WORK}/graphs/winner_v22_half.onnx",
        f"{WORK}/graphs/winner_v22_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v22 training artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v22 training artifact exceeds size ceiling")
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
                raise ValueError("Winner-v22 training artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_result(value: Mapping[str, Any]) -> None:
    passed = value.get("status") == "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
    if (
        value.get("schema_version") != "winner_v22.normalized_predictor_training_result.v1"
        or value.get("status")
        not in {
            "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT",
            "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT",
        }
        or value.get("decision")
        != (
            "AUTHORIZE_SEPARATE_CORRECTED_SUPPORT_GATE_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_EVALUATE_WINNER_V22_NORMALIZED_PREDICTOR_CONTROLLER"
        )
        or value.get("source_stage1_snapshot")
        != {
            "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
            "bytes": 189027,
        }
        or value.get("predictor_scale") != 380.9135437011719
        or value.get("execution")
        != {
            "optimizer_updates": 100,
            "scheduled_episode_slots": 2_000_000,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("authority", {}).get("formal_support_gate_executed") is not False
        or value.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v22 training result schema changed")
    checks = value.get("checks")
    failed = value.get("failed_checks")
    if not isinstance(checks, Mapping) or not checks or not isinstance(failed, list):
        raise ValueError("Winner-v22 training checks changed")
    if failed != sorted(name for name, flag in checks.items() if flag is not True):
        raise ValueError("Winner-v22 training classification does not match checks")
    if passed and failed:
        raise ValueError("Winner-v22 passing training has failed checks")
    if value.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v22 training source identities changed")
    snapshots = value.get("snapshot_manifest")
    checkpoints = value.get("persistent_checkpoints")
    metrics = value.get("metrics")
    if (
        not isinstance(snapshots, list)
        or len(snapshots) != 100
        or [row.get("update") for row in snapshots] != list(range(1, 101))
        or not isinstance(metrics, list)
        or [row.get("update") for row in metrics] != list(range(1, 101))
        or not isinstance(checkpoints, list)
        or [(row.get("label"), row.get("update")) for row in checkpoints]
        != [("half", 50), ("final", 100)]
        or not finite_tree(value)
    ):
        raise ValueError("Winner-v22 training sequence changed")


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
        raise FileExistsError("Winner-v22 training result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v22-normalized-predictor-training-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v22 training repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v22 training raw receipt changed")
    raw = json.loads(members[RAW_RESULT].decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    for row in raw["snapshot_manifest"]:
        name = f"{WORK}/snapshots/snapshot_normalized_predictor_update_{row['update']:03d}.npz"
        if sha256_bytes(members[name]) != row["sha256"] or len(members[name]) != row["bytes"]:
            raise ValueError(f"Winner-v22 snapshot {row['update']} changed")
    for row in raw["persistent_checkpoints"]:
        name = f"{WORK}/graphs/winner_v22_{row['label']}.onnx"
        graph = row["graph"]
        if sha256_bytes(members[name]) != graph["sha256"] or len(members[name]) != graph["bytes"]:
            raise ValueError(f"Winner-v22 {row['label']} graph changed")
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
    half, final = result["persistent_checkpoints"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v22 normalized-predictor training result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Half / final ONNX SHA-256: `{half['graph']['sha256']}` / `{final['graph']['sha256']}`",
                "- Updates / formal support / locomotion / robot: `100 / 0 / 0 / 0`",
                "",
                "A pass authorizes only a separately frozen corrected support/context gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
