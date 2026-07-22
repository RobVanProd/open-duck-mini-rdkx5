#!/usr/bin/env python3
"""Safely import the sole Winner-v43 static-target teacher ABI CPU result."""

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
CONTRACT = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_contract.json"
RUNNER = ROOT / "tools/run_winner_v43_static_target_teacher_abi_cpu_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v43-static-target-teacher-abi-cpu.yml"
OUTPUT_JSON = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v43-static-target-teacher-abi-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v43-static-target-teacher-abi-cpu-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
CONFIGURATION_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
)
CHECK_NAMES = {
    "cpu_only_environment_exact",
    "exact_15_configuration_table_bound",
    "selected_replay_raw_target_hashes_exact",
    "exact_30_two_plant_teacher_rows",
    "exact_250_tick_teacher_horizon",
    "exact_45000_valid_pitch_elements",
    "paired_plants_receive_identical_raw_target",
    "nonpitch_teacher_mask_exact_zero",
    "inherited_inward_boundary_bit_exact",
    "sequential_boundary_reaches_every_selected_raw_target",
    "teacher_loss_finite_nonzero",
    "teacher_gradient_nonzero_on_all_six_pitch_indices",
    "teacher_gradient_exact_zero_on_nonpitch_indices",
    "teacher_target_and_previous_action_paths_stopped",
    "default_off_loss_bit_exact",
    "default_off_gradient_bit_exact",
    "enabled_unit_scale_changes_pitch_gradients",
    "enabled_unit_scale_preserves_nonpitch_gradients_bit_exact",
    "all_arrays_losses_gradients_finite",
    "optimizer_updates_zero",
    "simulator_behavior_ticks_zero",
    "locomotion_training_steps_zero",
    "deployable_graph_exports_zero",
    "robot_or_rdk_access_zero",
}
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "contract_lf_sha256", "workflow_lf_sha256",
    "runner_lf_sha256", "importer_lf_sha256",
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
            raise ValueError("Winner-v43 artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("Winner-v43 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v43 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v43 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v43-static-target-teacher-abi-cpu-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v43 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "decision", "checks", "failed_checks",
        "teacher_evidence", "execution", "environment", "sources",
        "source_manifest_sha256", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v43.static_target_teacher_abi_cpu_result.v1":
        raise ValueError("Winner-v43 result schema changed")
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
            != f"winner-v43-static-target-teacher-abi-cpu-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(HEX64_RE.fullmatch(str(attribution.get(name))) is None for name in (
                "artifact_zip_sha256", "raw_result_sha256", "raw_result_receipt_sha256",
                "contract_lf_sha256", "workflow_lf_sha256", "runner_lf_sha256",
                "importer_lf_sha256",
            ))
            or attribution["contract_lf_sha256"] != lf_sha256(CONTRACT)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["runner_lf_sha256"] != lf_sha256(RUNNER)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v43 imported attribution changed")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        result.get("sources") != contract["sources"]
        or result.get("source_manifest_sha256") != contract["source_manifest_sha256"]
    ):
        raise ValueError("Winner-v43 source manifest changed")
    checks = result.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != CHECK_NAMES or any(
        type(value) is not bool for value in checks.values()
    ):
        raise ValueError("Winner-v43 checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
            if passed else "HOLD_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CPU_CONTRACT_ONLY"
            if passed else "DO_NOT_ATTACH_STATIC_TARGET_TEACHER_TO_POLICY"
        )
    ):
        raise ValueError("Winner-v43 decision changed")
    evidence = result.get("teacher_evidence")
    if not isinstance(evidence, Mapping) or set(evidence) != {
        "configuration_ids", "environment_rows", "duration_ticks",
        "supervised_action_indices", "selected_elements", "teacher_loss",
        "baseline_loss", "enabled_unit_scale_loss", "maximum_raw_target_abs",
        "maximum_bounded_target_abs", "raw_targets_sha256",
        "bounded_targets_sha256", "teacher_mask_sha256",
        "teacher_action_gradient_sha256", "teacher_previous_action_gradient_sha256",
    }:
        raise ValueError("Winner-v43 teacher evidence schema changed")
    if (
        evidence["configuration_ids"] != list(CONFIGURATION_IDS)
        or evidence["environment_rows"] != 30
        or evidence["duration_ticks"] != 250
        or evidence["supervised_action_indices"] != [2, 3, 4, 11, 12, 13]
        or evidence["selected_elements"] != 45_000
    ):
        raise ValueError("Winner-v43 teacher evidence dimensions changed")
    for name in (
        "teacher_loss", "baseline_loss", "enabled_unit_scale_loss",
        "maximum_raw_target_abs", "maximum_bounded_target_abs",
    ):
        value = evidence[name]
        if type(value) not in {int, float} or not math.isfinite(value):
            raise ValueError(f"Winner-v43 {name} changed")
    if (
        evidence["teacher_loss"] <= 0.0
        or evidence["maximum_raw_target_abs"] > 1.0
        or evidence["maximum_bounded_target_abs"] > 1.0
    ):
        raise ValueError("Winner-v43 teacher numeric bounds changed")
    for name in (
        "raw_targets_sha256", "bounded_targets_sha256", "teacher_mask_sha256",
        "teacher_action_gradient_sha256", "teacher_previous_action_gradient_sha256",
    ):
        require_sha256(evidence[name], f"Winner-v43 {name}")
    if result.get("execution") != {
        "synthetic_teacher_rows": 7_500,
        "optimizer_updates": 0,
        "simulator_behavior_ticks": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != contract["authority"]:
        raise ValueError("Winner-v43 execution or authority changed")
    environment = result.get("environment")
    if (
        not isinstance(environment, Mapping)
        or environment.get("jax_backend") != "cpu"
        or environment.get("jax_devices") != ["cpu"]
        or not isinstance(environment.get("numpy_version"), str)
    ):
        raise ValueError("Winner-v43 CPU environment changed")


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
        raise FileExistsError("Winner-v43 result is already imported")
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
        raise ValueError("Winner-v43 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    evidence = payload["teacher_evidence"]
    OUTPUT_MD.write_text(
        "\n".join([
            "# Winner-v43 static-target teacher ABI CPU result", "",
            f"- Status: `{payload['status']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Teacher loss: `{evidence['teacher_loss']:.9f}`",
            f"- Maximum raw / bounded target: `{evidence['maximum_raw_target_abs']:.6f} / {evidence['maximum_bounded_target_abs']:.6f}`",
            "- Configurations / rows / ticks / elements: `15 / 30 / 250 / 45,000`",
            "- Optimizer / simulator / training / export / robot: `0 / 0 / 0 / 0 / 0`", "",
            "The privileged table remains training-only and default-disabled. This",
            "result does not train, change an ONNX ABI, select a checkpoint, or clear the robot.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
