#!/usr/bin/env python3
"""Import one exact Winner-v12 formal calibrator support-gate result."""

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
LAUNCH = ANALYSIS / "winner_v12_calibrator_support_gate_launch.json"
OUTPUT_JSON = ANALYSIS / "winner_v12_calibrator_support_gate_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V12_CALIBRATOR_SUPPORT_GATE_RESULT_20260721.md"
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-support-gate.yml"
RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
PREREGISTRATION = ANALYSIS / "winner_v12_calibrator_support_gate_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
TRAINING_RUNNER = ROOT / "tools/run_winner_v12_full_calibrator_training.py"
RAW_RESULT_NAME = "winner-v12-calibrator-support-gate-result.json"
RAW_RECEIPT_NAME = "winner-v12-calibrator-support-gate-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
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
            raise ValueError("formal support-gate artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("formal support-gate artifact exceeds the size ceiling")
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
                raise ValueError("formal support-gate artifact has an unsafe member")
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
    require_sha256(artifact_zip_sha256, "formal support-gate artifact")
    expected_name = f"winner-v12-calibrator-support-gate-{run_id}"
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != expected_name
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("formal support-gate workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_checkpoint_result(row: Mapping[str, Any], label: str) -> None:
    expected_fields = {
        "checks",
        "checkpoint_sha256",
        "core_model_plant_cells",
        "failed_checks",
        "heldout_context_separation",
        "heldout_prediction",
        "heldout_repeatability",
        "label",
        "onnx_sha256",
        "sensor_transport_plant_cells",
        "update",
    }
    if set(row) != expected_fields or row["label"] != label:
        raise ValueError(f"formal {label} checkpoint result schema changed")
    if row["update"] != {"half": 50, "final": 100}[label]:
        raise ValueError(f"formal {label} checkpoint boundary changed")
    require_sha256(row["checkpoint_sha256"], f"formal {label} checkpoint")
    require_sha256(row["onnx_sha256"], f"formal {label} ONNX")
    if (
        len(row["core_model_plant_cells"]) != 112
        or len(row["sensor_transport_plant_cells"]) != 12
        or len(row["heldout_repeatability"]) != 32
        or len(row["heldout_context_separation"]) != 16
        or len(row["heldout_prediction"]) != 2
    ):
        raise ValueError(f"formal {label} population changed")
    checks = row["checks"]
    expected_checks = {
        "all_16_heldout_contexts_separate",
        "all_32_heldout_repeats_bit_exact",
        "all_jax_onnx_hidden_errors_at_most_1e_7",
        "all_previous_action_chains_exact",
        "all_support_cells_pass",
        "exact_124_main_cells",
        "learned_prediction_beats_constant_per_plant",
    }
    if (
        not isinstance(checks, dict)
        or set(checks) != expected_checks
        or not all(type(value) is bool for value in checks.values())
        or row["failed_checks"]
        != sorted(name for name, passed in checks.items() if not passed)
    ):
        raise ValueError(f"formal {label} check accounting changed")
    if not all(item.get("bit_exact") is True for item in row["heldout_repeatability"]):
        raise ValueError(f"formal {label} repeatability failed")


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
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
    if set(result) != expected_fields:
        raise ValueError("formal support-gate result schema changed")
    if result["schema_version"] != "winner_v12.calibrator_support_gate_result.v1":
        raise ValueError("formal support-gate result version changed")
    checks = result["checks"]
    expected_checks = {
        "all_248_main_cells_pass",
        "both_checkpoints_evaluated",
        "formal_cell_count_exact",
    }
    if (
        not isinstance(checks, dict)
        or set(checks) != expected_checks
        or not all(type(value) is bool for value in checks.values())
    ):
        raise ValueError("formal support-gate global checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    if result["failed_checks"] != failed:
        raise ValueError("formal support-gate failure accounting changed")
    passed = not failed
    if result["status"] != (
        "PASS_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        if passed
        else "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
    ) or result["decision"] != (
        "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY"
        if passed
        else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    ):
        raise ValueError("formal support-gate status/decision changed")
    if result["execution"] != {
        "formal_support_cells": 248,
        "heldout_repeat_cells": 64,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("formal support-gate execution boundary changed")
    if result["authority"] != {
        "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("formal support-gate authority changed")
    if result["sources"] != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "domain_lf_sha256": lf_sha256(DOMAIN),
        "training_runner_lf_sha256": lf_sha256(TRAINING_RUNNER),
        "gate_runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("formal support-gate source identities changed")
    rows = result["checkpoint_results"]
    if not isinstance(rows, list) or [row.get("label") for row in rows] != [
        "half",
        "final",
    ]:
        raise ValueError("formal support-gate checkpoint set changed")
    for row, label in zip(rows, ("half", "final"), strict=True):
        validate_checkpoint_result(row, label)
    if passed and not all(
        all(row["checks"].values()) and row["failed_checks"] == [] for row in rows
    ):
        raise ValueError("formal global PASS has a failed checkpoint proof")


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
        raise FileExistsError("Winner-v12 formal support-gate result is already imported")
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
        raise ValueError("formal support-gate raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.result_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "launch_path": str(LAUNCH.relative_to(ROOT)).replace("\\", "/"),
        "launch_lf_sha256": lf_sha256(LAUNCH),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator formal support-gate result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run: `{args.verification_run_id}` attempt `1`",
                f"- Run head: `{args.verification_run_head_sha}`",
                f"- Result artifact ID: `{args.verification_artifact_id}`",
                f"- Result artifact ZIP SHA-256: `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Formal support cells / heldout repeats: `248 / 64`",
                "- Locomotion training / robot access: `0 / 0`",
                "",
                "A PASS authorizes only a separate response-conditioned locomotion",
                "preregistration. It does not authorize training, deployment, Gate 5,",
                "or robot access.",
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
