#!/usr/bin/env python3
"""Safely import one Winner-v24 baseline-anchored support-gate result."""

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
PREREGISTRATION = ANALYSIS / "winner_v24_baseline_anchored_support_gate_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
TRAINING_PREREGISTRATION = ANALYSIS / "winner_v24_baseline_anchored_training_preregistration.json"
TRAINING_RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_training.py"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_support_gate.py"
WORKFLOW = ROOT / ".github/workflows/winner-v24-baseline-anchored-support-gate.yml"
V15_IMPORTER = ROOT / "tools/import_winner_v15_pitch_margin_support_gate_result.py"
OUTPUT_JSON = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v24-baseline-anchored-support-gate-result.json"
RAW_RECEIPT_NAME = "winner-v24-baseline-anchored-support-gate-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
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
    "v15_importer_lf_sha256",
    "importer_lf_sha256",
}


def _load_v15_importer():
    spec = importlib.util.spec_from_file_location(
        "winner_v15_support_gate_import_helpers_v24", V15_IMPORTER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reviewed Winner-v15 gate importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V15 = _load_v15_importer()


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


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON value is forbidden: {value}")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v24 support-gate artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v24 support-gate artifact exceeds size ceiling")
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
                raise ValueError("Winner-v24 support-gate artifact has unsafe member")
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
    require_sha256(artifact_zip_sha256, "Winner-v24 support-gate artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v24-baseline-anchored-support-gate-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v24 support-gate workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def checkpoint_identities() -> dict[str, dict[str, str]]:
    source = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        source.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
        or source.get("decision")
        != "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or source.get("failed_checks") != []
        or source.get("repository_attribution", {}).get("repository")
        != EXPECTED_REPOSITORY
    ):
        raise ValueError("Winner-v24 training source is not verified")
    snapshots = source.get("snapshot_manifest")
    checkpoints = source.get("persistent_checkpoints")
    if (
        not isinstance(snapshots, list)
        or len(snapshots) != 100
        or not isinstance(checkpoints, list)
        or [(row.get("label"), row.get("completed_updates")) for row in checkpoints]
        != [("half", 150), ("final", 200)]
    ):
        raise ValueError("Winner-v24 checkpoint set changed")
    identities: dict[str, dict[str, str]] = {}
    for label, update, checkpoint in zip(
        ("half", "final"), (150, 200), checkpoints, strict=True
    ):
        snapshot = next(
            row for row in snapshots if row.get("completed_updates") == update
        )
        snapshot_sha = snapshot.get("sha256")
        graph_sha = checkpoint.get("graph", {}).get("sha256")
        require_sha256(snapshot_sha, f"Winner-v24 {label} snapshot")
        require_sha256(graph_sha, f"Winner-v24 {label} graph")
        identities[label] = {
            "checkpoint_sha256": str(snapshot_sha),
            "onnx_sha256": str(graph_sha),
        }
    return identities


def _validate_checkpoint_result(
    row: Mapping[str, Any], label: str, expected_identity: Mapping[str, str]
) -> None:
    expected_update = {"half": 150, "final": 200}[label]
    if row.get("update") != expected_update:
        raise ValueError(f"Winner-v24 formal {label} update changed")
    adapted = dict(row)
    adapted["update"] = {"half": 50, "final": 100}[label]
    V15.validate_checkpoint_result(adapted, label, expected_identity)


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "authority",
        "checkpoint_results",
        "checks",
        "decision",
        "execution",
        "failed_checks",
        "schema_version",
        "sources",
        "status",
    }
    if frozenset(result) not in {
        frozenset(raw_fields),
        frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != (
        "winner_v24.baseline_anchored_support_gate_result.v1"
    ):
        raise ValueError("Winner-v24 formal gate result schema changed")
    if "repository_attribution" in result:
        attribution = result["repository_attribution"]
        if (
            not isinstance(attribution, Mapping)
            or set(attribution) != ATTRIBUTION_FIELDS
            or attribution.get("repository") != EXPECTED_REPOSITORY
            or attribution.get("github_run_attempt") != 1
            or type(attribution.get("github_run_id")) is not int
            or attribution["github_run_id"] <= 0
            or HEX40_RE.fullmatch(str(attribution.get("github_run_head_sha"))) is None
            or type(attribution.get("github_artifact_id")) is not int
            or attribution["github_artifact_id"] <= 0
            or attribution.get("github_artifact_name")
            != f"winner-v24-baseline-anchored-support-gate-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(
                HEX64_RE.fullmatch(str(attribution.get(name))) is None
                for name in (
                    "artifact_zip_sha256",
                    "raw_result_sha256",
                    "raw_result_receipt_sha256",
                )
            )
            or attribution.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or attribution.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or attribution.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or attribution.get("v15_importer_lf_sha256") != lf_sha256(V15_IMPORTER)
            or attribution.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v24 imported repository attribution changed")
    checks = result.get("checks")
    expected_checks = {
        "all_248_main_cells_pass",
        "both_checkpoints_evaluated",
        "formal_cell_count_exact",
    }
    if (
        not isinstance(checks, Mapping)
        or set(checks) != expected_checks
        or not all(type(value) is bool for value in checks.values())
    ):
        raise ValueError("Winner-v24 formal gate checks changed")
    if result.get("execution") != {
        "formal_support_cells": 248,
        "heldout_repeat_cells": 64,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("Winner-v24 formal gate execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
        "training_preregistration_lf_sha256": lf_sha256(TRAINING_PREREGISTRATION),
        "training_runner_lf_sha256": lf_sha256(TRAINING_RUNNER),
        "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
        "gate_runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v24 formal gate sources changed")
    rows = result.get("checkpoint_results")
    if not isinstance(rows, list) or [row.get("label") for row in rows] != [
        "half",
        "final",
    ]:
        raise ValueError("Winner-v24 formal gate checkpoint set changed")
    identities = checkpoint_identities()
    for row, label in zip(rows, ("half", "final"), strict=True):
        _validate_checkpoint_result(row, label, identities[label])
    derived = {
        "both_checkpoints_evaluated": [row["label"] for row in rows]
        == ["half", "final"],
        "all_248_main_cells_pass": all(not row["failed_checks"] for row in rows),
        "formal_cell_count_exact": sum(
            len(row["core_model_plant_cells"])
            + len(row["sensor_transport_plant_cells"])
            for row in rows
        )
        == 248,
    }
    if checks != derived:
        raise ValueError("Winner-v24 formal gate summary is not rederived")
    failed = sorted(name for name, passed in derived.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
            if passed
            else "HOLD_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        )
    ):
        raise ValueError("Winner-v24 formal gate decision changed")


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
        raise FileExistsError("Winner-v24 support-gate result is already imported")
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
        raise ValueError("Winner-v24 support-gate raw-result receipt changed")
    result = json.loads(
        raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite
    )
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
        "v15_importer_lf_sha256": lf_sha256(V15_IMPORTER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v24 baseline-anchored formal support-gate result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Formal support cells / heldout repeats: `248 / 64`",
                "- Locomotion training / robot access: `0 / 0`",
                "",
                "A pass requires every frozen support and response-context check at both",
                "checkpoints. It authorizes only a separate locomotion preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
