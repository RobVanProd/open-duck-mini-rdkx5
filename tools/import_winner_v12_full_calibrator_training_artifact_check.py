#!/usr/bin/env python3
"""Import one exact Winner-v12 full-calibrator artifact-check result."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
DEFAULT_LAUNCH = (
    ANALYSIS / "winner_v12_full_calibrator_training_artifact_check_launch.json"
)
OUTPUT_JSON = (
    ANALYSIS / "winner_v12_full_calibrator_training_artifact_check.json"
)
OUTPUT_MD = (
    ANALYSIS
    / "WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK_RESULT_20260721.md"
)
WORKFLOW = (
    ROOT
    / ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
)
RAW_RESULT_NAME = "winner-v12-full-calibrator-training-artifact-check-result.json"
RAW_RECEIPT_NAME = "winner-v12-full-calibrator-training-artifact-check-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
EXPECTED_CHECKS = frozenset(
    {
        "all_201_snapshots_restore_and_validate",
        "all_snapshot_receipts_exact",
        "artifact_file_inventory_exact",
        "artifact_manifest_exact",
        "artifact_zip_hash_exact",
        "artifact_zip_members_safe_unique",
        "authorization_claim_receipt_exact",
        "authority_source_exact",
        "formal_support_locomotion_robot_all_zero",
        "half_and_final_identities_exposed_for_gate",
        "half_and_final_onnx_independently_exact",
        "latest_pointer_equals_final_snapshot",
        "no_logged_traceback_or_hold",
        "repository_attribution_exact",
        "result_metrics_equal_final_snapshot",
        "stage1_active_leaves_all_changed",
        "stage1_optimizer_moments_all_nonzero",
        "stage2_active_leaves_all_changed",
        "stage2_optimizer_moments_all_nonzero",
        "training_environment_exact_cpu_only",
        "training_population_and_accounting_exact",
        "training_result_hash_receipt_exact",
    }
)
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


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_verification_artifact(archive_path: Path) -> tuple[bytes, bytes]:
    """Read the two exact regular files from a GitHub verification artifact."""
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("verification artifact file inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("verification artifact exceeds the frozen size ceiling")
        for info in infos:
            path = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "." in path.parts
                or "\\" in info.filename
                or info.flag_bits & 0x1
                or info.is_dir()
                or file_type == stat.S_IFLNK
                or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("verification artifact contains an unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def validate_launch(launch: Mapping[str, Any]) -> None:
    expected_top_level = {
        "authority",
        "decision",
        "execution_now",
        "expected_hashes",
        "repository_attribution",
        "schema_version",
        "source_manifest_sha256",
        "sources",
        "status",
    }
    if set(launch) != expected_top_level:
        raise ValueError("artifact-check launch schema changed")
    if (
        launch["schema_version"]
        != "winner_v12.full_calibrator_training_artifact_check_launch.v1"
        or launch["status"]
        != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK_LAUNCH_FROZEN"
        or launch["decision"]
        != "AUTHORIZE_ONE_RAW_ZIP_ARTIFACT_VERIFICATION_ONLY"
    ):
        raise ValueError("artifact-check launch did not pass exactly")
    if launch["execution_now"] != {
        "artifact_verifications": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("artifact-check launch execution authority changed")
    if launch["authority"] != {
        "pass_authorizes_only": "the already preregistered zero-cell support-gate CPU contract",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("artifact-check launch authority changed")
    if canonical_sha256(launch["sources"]) != launch["source_manifest_sha256"]:
        raise ValueError("artifact-check source manifest changed")
    for source in launch["sources"].values():
        if set(source) != {"hash_mode", "path", "sha256"} or source["hash_mode"] != "lf":
            raise ValueError("artifact-check source identity schema changed")
        relative = Path(source["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("artifact-check source path escaped the repository")
        path = ROOT / relative
        if not path.is_file() or lf_sha256(path) != source["sha256"]:
            raise ValueError(f"artifact-check frozen source changed: {relative}")


def validate_result_binding(
    raw: Mapping[str, Any], launch: Mapping[str, Any]
) -> None:
    expected_top_level = {
        "artifact_zip",
        "authority",
        "checks",
        "decision",
        "execution",
        "failed_checks",
        "limitation",
        "optimizer_moments",
        "parameter_deltas",
        "repository_attribution",
        "schema_version",
        "status",
        "training_result_sha256",
        "verified_checkpoints",
    }
    if set(raw) != expected_top_level:
        raise ValueError("raw artifact-check result schema changed")
    sys.path.insert(0, str(TOOLS))
    import build_winner_v12_calibrator_support_gate_cpu_contract as support_builder

    support_builder.validate_artifact_check(
        raw, require_verification_attribution=False
    )
    checks = raw["checks"]
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise ValueError("raw artifact-check check set changed")
    if raw["artifact_zip"] != {
        "path": "/tmp/winner-v12-full-calibrator-training.zip",
        "sha256": raw["artifact_zip"].get("sha256"),
        "bytes": raw["artifact_zip"].get("bytes"),
        "member_count": 415,
    }:
        raise ValueError("raw training artifact ZIP identity changed")
    if raw["authority"] != {
        "artifact_verification_only": True,
        "pass_authorizes_only": "the separately frozen 124-cell calibrator support/context gate",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("raw artifact-check authority changed")
    if raw["execution"] != {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("raw artifact-check execution boundary changed")
    for family in ("parameter_deltas", "optimizer_moments"):
        value = raw[family]
        if not isinstance(value, dict) or set(value) != {"stage1", "stage2"}:
            raise ValueError(f"raw {family} schema changed")
        if not value["stage1"] or not value["stage2"]:
            raise ValueError(f"raw {family} proof is empty")
    for row in raw["parameter_deltas"]["stage1"] + raw["parameter_deltas"]["stage2"]:
        if (
            set(row) != {"changed", "key", "max_abs_delta"}
            or row["changed"] is not True
            or not math.isfinite(float(row["max_abs_delta"]))
            or float(row["max_abs_delta"]) <= 0.0
        ):
            raise ValueError("raw parameter-delta proof changed")
    for row in raw["optimizer_moments"]["stage1"] + raw["optimizer_moments"]["stage2"]:
        if (
            set(row) != {"key", "m_nonzero", "v_nonzero"}
            or row["m_nonzero"] is not True
            or row["v_nonzero"] is not True
        ):
            raise ValueError("raw optimizer-moment proof changed")
    if raw["repository_attribution"] != launch["repository_attribution"]:
        raise ValueError("raw result is not from the frozen training artifact")
    if raw["artifact_zip"]["sha256"] != launch["expected_hashes"][
        "artifact_zip_sha256"
    ] or raw["training_result_sha256"] != launch["expected_hashes"][
        "training_result_sha256"
    ]:
        raise ValueError("raw result hashes differ from the frozen launch")


def verification_attribution(
    *,
    run_id: int,
    run_attempt: int,
    run_head_sha: str,
    artifact_id: int,
    artifact_name: str,
    artifact_digest: str,
    artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "verification artifact ZIP")
    expected_name = f"winner-v12-full-calibrator-training-artifact-check-{run_id}"
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != expected_name
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("verification workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification-artifact-zip", type=Path, required=True)
    parser.add_argument("--artifact-check-launch", type=Path, default=DEFAULT_LAUNCH)
    parser.add_argument("--verification-run-id", type=int, required=True)
    parser.add_argument("--verification-run-attempt", type=int, required=True)
    parser.add_argument("--verification-run-head-sha", required=True)
    parser.add_argument("--verification-artifact-id", type=int, required=True)
    parser.add_argument("--verification-artifact-name", required=True)
    parser.add_argument("--verification-artifact-digest", required=True)
    args = parser.parse_args()
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("Winner-v12 artifact-check result is already imported")
    if args.artifact_check_launch.resolve() != DEFAULT_LAUNCH.resolve():
        raise ValueError("artifact-check launch must be the repository-frozen path")
    launch = json.loads(DEFAULT_LAUNCH.read_text(encoding="utf-8"))
    validate_launch(launch)
    artifact_zip_sha = sha256(args.verification_artifact_zip)
    attribution = verification_attribution(
        run_id=args.verification_run_id,
        run_attempt=args.verification_run_attempt,
        run_head_sha=args.verification_run_head_sha,
        artifact_id=args.verification_artifact_id,
        artifact_name=args.verification_artifact_name,
        artifact_digest=args.verification_artifact_digest,
        artifact_zip_sha256=artifact_zip_sha,
    )
    raw_bytes, receipt_bytes = read_verification_artifact(
        args.verification_artifact_zip
    )
    raw_sha = sha256_bytes(raw_bytes)
    expected_receipt = f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode()
    if receipt_bytes != expected_receipt:
        raise ValueError("verification artifact result hash receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"))
    validate_result_binding(raw, launch)
    payload = dict(raw)
    payload["verification_repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.verification_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "artifact_check_launch_path": str(DEFAULT_LAUNCH.relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "artifact_check_launch_lf_sha256": lf_sha256(DEFAULT_LAUNCH),
        "workflow_path": str(WORKFLOW.relative_to(ROOT)).replace("\\", "/"),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v12 full-calibrator artifact-check result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Verification run: `{args.verification_run_id}` attempt `1`",
                f"- Verification head: `{args.verification_run_head_sha}`",
                f"- Verification artifact ID: `{args.verification_artifact_id}`",
                f"- Verification artifact ZIP SHA-256: `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                f"- Training artifact ZIP SHA-256: `{payload['artifact_zip']['sha256']}`",
                f"- Training result SHA-256: `{payload['training_result_sha256']}`",
                "- Verified checkpoints: `half / final`",
                "- Formal support cells / locomotion / robot access: `0 / 0 / 0`",
                "",
                "The committed result is imported from the exact independently verified",
                "GitHub artifact and is bound to the frozen training artifact launch.",
                "It authorizes only the already-preregistered zero-cell support-gate CPU",
                "contract; it does not authorize formal cells, locomotion, deployment,",
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
