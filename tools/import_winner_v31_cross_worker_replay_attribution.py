#!/usr/bin/env python3
"""Strictly import the sole Winner-v31 saved-result attribution artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v31_cross_worker_replay_attribution_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v31_cross_worker_replay_attribution.py"
WORKFLOW = ROOT / ".github/workflows/winner-v31-cross-worker-replay-attribution.yml"
OUTPUT_JSON = ANALYSIS / "winner_v31_cross_worker_replay_attribution_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v31-cross-worker-replay-attribution-result.json"
RAW_RECEIPT_NAME = "winner-v31-cross-worker-replay-attribution-result.sha256"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant: {value}")


def read_artifact(path: Path) -> tuple[bytes, bytes]:
    with zipfile.ZipFile(path) as archive:
        items = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in items]
        if sorted(names) != sorted((RAW_RESULT_NAME, RAW_RECEIPT_NAME)):
            raise ValueError(f"Winner-v31 artifact inventory changed: {names}")
        if any(
            PurePosixPath(item.filename).is_absolute()
            or ".." in PurePosixPath(item.filename).parts
            or item.is_dir()
            or item.file_size > 4 * 1024 * 1024
            for item in items
        ):
            raise ValueError("Winner-v31 artifact contains unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def validate_result(value: Mapping[str, Any]) -> None:
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        value.get("schema_version")
        != "winner_v31.cross_worker_replay_attribution_result.v1"
        or value.get("status") != "PASS_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
        or value.get("classification") != "CROSS_WORKER_FLOAT_REPLAY_ONLY"
        or value.get("decision")
        != "AUTHORIZE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_USING_PRESERVED_COUNT_201_ARTIFACT_ONLY"
        or value.get("failed_checks") != []
        or not isinstance(value.get("checks"), Mapping)
        or not value["checks"]
        or not all(item is True for item in value["checks"].values())
        or value.get("execution")
        != {
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("sources") != prereg["sources"]
        or value.get("source_manifest_sha256") != prereg["source_manifest_sha256"]
    ):
        raise ValueError("Winner-v31 result changed")
    numeric = value.get("numeric_attribution", {})
    if set(numeric) != {
        "anchor_loss_before",
        "ppo_loss",
        "normalized_predictor_loss",
    } or not all(
        int(row.get("float32_ulp_distance", 999)) <= 8
        and float(row.get("absolute_delta", -1.0)) >= 0.0
        for row in numeric.values()
    ):
        raise ValueError("Winner-v31 numeric attribution changed")
    if float(value.get("anchor_improvement_to_cross_worker_delta_ratio", 0.0)) < 10_000.0:
        raise ValueError("Winner-v31 improvement ratio changed")
    artifacts = value.get("source_artifacts", {})
    if (
        set(artifacts)
        != {
            "winner_v29_result_lf_sha256",
            "winner_v30_hold_result_lf_sha256",
            "winner_v30_snapshot_sha256",
            "winner_v30_graph_sha256",
        }
        or not all(HEX64.fullmatch(str(item)) is not None for item in artifacts.values())
    ):
        raise ValueError("Winner-v31 source artifact identity changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "runtime_implementation_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "one separately frozen prefix right-pitch anchor training preregistration "
            "using the preserved count-201 artifact"
        ),
    }:
        raise ValueError("Winner-v31 authority changed")
    if "repository_attribution" in value:
        item = value["repository_attribution"]
        if (
            item.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
            or item.get("github_run_attempt") != 1
            or HEX40.fullmatch(str(item.get("github_run_head_sha"))) is None
            or HEX64.fullmatch(str(item.get("artifact_zip_sha256"))) is None
            or item.get("github_artifact_digest")
            != f"sha256:{item.get('artifact_zip_sha256')}"
            or item.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or item.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or item.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or item.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v31 repository attribution changed")


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
        raise FileExistsError("Winner-v31 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v31-cross-worker-replay-attribution-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v31 repository attribution changed")
    raw_bytes, receipt_bytes = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v31 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
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
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(result)
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v31 cross-worker replay attribution result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- Maximum loss ULP distance: `{max(row['float32_ulp_distance'] for row in result['numeric_attribution'].values())}`",
                f"- Improvement/discrepancy ratio: `{result['anchor_improvement_to_cross_worker_delta_ratio']}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Simulation / optimizer / support / locomotion / robot: `0 / 0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(result["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
