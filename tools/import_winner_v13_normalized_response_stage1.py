#!/usr/bin/env python3
"""Safely import one Winner-v13 normalized-response Stage-1 artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping, Sequence
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v13_normalized_response_stage1_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v13_normalized_response_cpu_contract_result.json"
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_stage1.py"
PRIMITIVES = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v13-normalized-response-stage1.yml"
OUTPUT_JSON = ANALYSIS / "winner_v13_normalized_response_stage1_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_STAGE1_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v13-normalized-response-stage1-result.json"
RAW_RECEIPT_NAME = "winner-v13-normalized-response-stage1-result.sha256"
RAW_LOG_NAME = "winner-v13-normalized-response-stage1.log"
WORK_PREFIX = "winner-v13-normalized-response-stage1-work"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
RUN_CHECKS = {
    "exact_100_optimizer_updates",
    "exact_100_immutable_snapshots",
    "half_and_final_evaluated",
    "both_checkpoints_pass_heldout_gate",
    "action_head_bit_exact",
}
CHECKPOINT_CHECKS = {
    "exact_32_heldout_cells",
    "heldout_repeat_bit_exact",
    "learned_prediction_beats_constant_per_plant",
    "all_16_plant_contexts_separate",
    "checker_onnx_action_exact_zero",
    "checker_onnx_hidden_at_most_1e_7",
    "deployable_onnx_abi_exact",
    "deployable_onnx_training_only_tensors_absent",
    "deployable_onnx_chain_at_most_1e_7",
}
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


def expected_artifact_members() -> set[str]:
    snapshots = {
        f"{WORK_PREFIX}/snapshots/snapshot_stage1_update_{index:03d}.npz"
        for index in range(1, 101)
    }
    graphs = {
        f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_half.onnx",
        f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_final.onnx",
    }
    return {RAW_RESULT_NAME, RAW_RECEIPT_NAME, RAW_LOG_NAME} | snapshots | graphs


def read_result_artifact(path: Path) -> dict[str, bytes]:
    expected = expected_artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            missing = sorted(expected - set(names))
            extra = sorted(set(names) - expected)
            raise ValueError(
                f"Winner-v13 Stage-1 artifact inventory changed: "
                f"missing={missing} extra={extra}"
            )
        if sum(item.file_size for item in infos) > 150_000_000:
            raise ValueError("Winner-v13 Stage-1 artifact exceeds the size ceiling")
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
                raise ValueError("Winner-v13 Stage-1 artifact has an unsafe member")
        return {name: archive.read(name) for name in names}


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
    require_sha256(artifact_zip_sha256, "Winner-v13 Stage-1 artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v13-normalized-response-stage1-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v13 Stage-1 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def validate_boolean_checks(
    checks: Any, expected: set[str], failed: Any, label: str
) -> list[str]:
    if (
        not isinstance(checks, dict)
        or set(checks) != expected
        or not all(type(value) is bool for value in checks.values())
    ):
        raise ValueError(f"{label} check schema changed")
    calculated = sorted(name for name, passed in checks.items() if not passed)
    if failed != calculated:
        raise ValueError(f"{label} failed-check list changed")
    return calculated


def finite_nonnegative(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and value >= 0


def validate_graph(graph: Mapping[str, Any], label: str) -> None:
    require_sha256(graph.get("sha256"), f"Winner-v13 {label} graph")
    if (
        graph.get("bytes", 0) <= 0
        or graph.get("abi_exact") is not True
        or graph.get("training_only_tensors_absent") is not True
        or graph.get("jax_onnx_at_most_1e_7") is not True
        or graph.get("previous_action_out_equals_action_bit_exact") is not True
        or graph.get("chain_ticks") != 256
        or graph.get("inputs")
        != [
            {"name": "obs", "shape": [1, 115]},
            {"name": "previous_action", "shape": [1, 14]},
            {"name": "h_in", "shape": [1, 64]},
        ]
        or graph.get("outputs")
        != [
            {"name": "calibration_actions", "shape": [1, 14]},
            {"name": "previous_action_out", "shape": [1, 14]},
            {"name": "h_out", "shape": [1, 64]},
        ]
    ):
        raise ValueError(f"Winner-v13 {label} graph contract changed")


def validate_checkpoint(row: Mapping[str, Any], label: str, update: int) -> None:
    if row.get("label") != label or row.get("update") != update:
        raise ValueError(f"Winner-v13 {label} checkpoint identity changed")
    validate_boolean_checks(
        row.get("checks"), CHECKPOINT_CHECKS, row.get("failed_checks"), label
    )
    plants = row.get("predictor_by_plant")
    if not isinstance(plants, dict) or set(plants) != set(PLANTS):
        raise ValueError(f"Winner-v13 {label} predictor plants changed")
    for plant in PLANTS:
        metric = plants[plant]
        learned = metric.get("learned_normalized_mse_all_50")
        baseline = metric.get("constant_normalized_mse_all_50")
        if (
            metric.get("valid_transition_count", 0) <= 0
            or not all(
                finite_nonnegative(metric.get(name))
                for name in (
                    "learned_normalized_mse_all_50",
                    "constant_normalized_mse_all_50",
                    "learned_normalized_mse_noncontact_48",
                    "constant_normalized_mse_noncontact_48",
                    "contact_normalized_mse",
                )
            )
            or metric.get("learned_strictly_below_constant") is not (learned < baseline)
        ):
            raise ValueError(f"Winner-v13 {label}/{plant} predictor metric changed")
    contexts = row.get("context_separation")
    if (
        not isinstance(contexts, list)
        or [item.get("configuration_id") for item in contexts]
        != [f"HELDOUT_{index:02d}" for index in range(16)]
    ):
        raise ValueError(f"Winner-v13 {label} context population changed")
    for context in contexts:
        separation = context.get("final_valid_h_out_linf_plant_separation")
        if not finite_nonnegative(separation) or context.get(
            "separation_above_1e_7"
        ) is not (separation > 1.0e-7):
            raise ValueError(f"Winner-v13 {label} context metric changed")
    for name in (
        "heldout_episode_receipts_sha256",
        "heldout_repeat_episode_receipts_sha256",
        "heldout_batch_sha256",
        "heldout_repeat_batch_sha256",
    ):
        require_sha256(row.get(name), f"Winner-v13 {label} {name}")
    if (
        row.get("checker_onnx_hidden_ticks", 0) <= 0
        or not finite_nonnegative(row.get("checker_onnx_hidden_max_abs_error"))
    ):
        raise ValueError(f"Winner-v13 {label} ONNX checker changed")
    validate_graph(row.get("graph_contract", {}), label)
    snapshot = row.get("snapshot", {})
    require_sha256(snapshot.get("sha256"), f"Winner-v13 {label} snapshot")
    if snapshot.get("bit_exact_readback") is not True:
        raise ValueError(f"Winner-v13 {label} snapshot readback changed")


def validate_result(result: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "checks",
        "decision",
        "execution",
        "failed_checks",
        "metrics",
        "checkpoint_results",
        "normalization",
        "snapshot_manifest",
        "sources",
        "elapsed_seconds",
        "schema_version",
        "status",
    }
    if (
        set(result) != expected_fields
        or result.get("schema_version")
        != "winner_v13.normalized_response_stage1_result.v1"
    ):
        raise ValueError("Winner-v13 Stage-1 result schema changed")
    failed = validate_boolean_checks(
        result.get("checks"), RUN_CHECKS, result.get("failed_checks"), "run"
    )
    expected_status = (
        "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        if not failed
        else "HOLD_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
    )
    expected_decision = (
        "AUTHORIZE_SUPPORT_CONTROLLER_PREREGISTRATION_ONLY"
        if not failed
        else "DO_NOT_TRAIN_SUPPORT_CONTROLLER"
    )
    if result.get("status") != expected_status or result.get("decision") != expected_decision:
        raise ValueError("Winner-v13 Stage-1 decision is inconsistent with its checks")
    if result.get("execution") != {
        "stage1_optimizer_updates": 100,
        "stage2_optimizer_updates": 0,
        "training_episode_slots": 2_000_000,
        "heldout_evaluation_cells": 64,
        "heldout_repeat_cells": 64,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v13 Stage-1 execution boundary changed")
    if result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a separate automatic support-controller preregistration",
    }:
        raise ValueError("Winner-v13 Stage-1 authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "v13_primitives_lf_sha256": lf_sha256(PRIMITIVES),
    }:
        raise ValueError("Winner-v13 Stage-1 source identities changed")
    metrics = result.get("metrics")
    if (
        not isinstance(metrics, list)
        or [row.get("update") for row in metrics] != list(range(1, 101))
        or any(
            not finite_nonnegative(row.get("loss"))
            or row.get("sampled_count", 0) <= 0
            or row.get("valid_transition_count", 0) <= 0
            or row.get("sampled_count") < row.get("valid_transition_count")
            for row in metrics
        )
    ):
        raise ValueError("Winner-v13 Stage-1 metric sequence changed")
    snapshots = result.get("snapshot_manifest")
    if not isinstance(snapshots, list) or len(snapshots) != 100:
        raise ValueError("Winner-v13 Stage-1 snapshot count changed")
    for index, receipt in enumerate(snapshots, 1):
        require_sha256(receipt.get("sha256"), f"Winner-v13 snapshot {index}")
        if (
            PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
            != f"snapshot_stage1_update_{index:03d}.npz"
            or receipt.get("bytes", 0) <= 0
            or receipt.get("array_count", 0) <= 0
            or receipt.get("bit_exact_readback") is not True
        ):
            raise ValueError(f"Winner-v13 snapshot {index} receipt changed")
    checkpoints = result.get("checkpoint_results")
    if not isinstance(checkpoints, list) or len(checkpoints) != 2:
        raise ValueError("Winner-v13 checkpoint count changed")
    validate_checkpoint(checkpoints[0], "half", 50)
    validate_checkpoint(checkpoints[1], "final", 100)
    normalization = result.get("normalization", {})
    require_sha256(normalization.get("target_mean_sha256"), "Winner-v13 target mean")
    require_sha256(normalization.get("target_std_sha256"), "Winner-v13 target std")
    if normalization.get("contact_mean") != [1.0, 1.0] or normalization.get(
        "contact_std"
    ) != [9.999999974752427e-07, 9.999999974752427e-07]:
        raise ValueError("Winner-v13 contact normalization changed")
    if not finite_nonnegative(result.get("elapsed_seconds")):
        raise ValueError("Winner-v13 elapsed time changed")


def verify_artifact_payloads(
    members: Mapping[str, bytes], result: Mapping[str, Any]
) -> None:
    for index, receipt in enumerate(result["snapshot_manifest"], 1):
        name = f"{WORK_PREFIX}/snapshots/snapshot_stage1_update_{index:03d}.npz"
        payload = members[name]
        if sha256_bytes(payload) != receipt["sha256"] or len(payload) != receipt["bytes"]:
            raise ValueError(f"Winner-v13 snapshot {index} artifact changed")
    for checkpoint in result["checkpoint_results"]:
        label = checkpoint["label"]
        name = f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_{label}.onnx"
        payload = members[name]
        graph = checkpoint["graph_contract"]
        if sha256_bytes(payload) != graph["sha256"] or len(payload) != graph["bytes"]:
            raise ValueError(f"Winner-v13 {label} graph artifact changed")


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
        raise FileExistsError("Winner-v13 Stage-1 result is already imported")
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
    members = read_result_artifact(args.result_artifact_zip)
    raw_bytes = members[RAW_RESULT_NAME]
    receipt_bytes = members[RAW_RECEIPT_NAME]
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v13 Stage-1 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    verify_artifact_payloads(members, result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": artifact_zip_sha,
        "artifact_zip_bytes": args.result_artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "log_sha256": sha256_bytes(members[RAW_LOG_NAME]),
        "preregistration_path": str(PREREGISTRATION.relative_to(ROOT)).replace("\\", "/"),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    half, final = payload["checkpoint_results"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v13 normalized-response Stage-1 result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{args.verification_run_id} / 1`",
                f"- Artifact ID / ZIP SHA-256: `{args.verification_artifact_id}` / `{artifact_zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                f"- Half loss / final loss: `{payload['metrics'][49]['loss']} / {payload['metrics'][99]['loss']}`",
                f"- Half failed checks: `{half['failed_checks']}`",
                f"- Final failed checks: `{final['failed_checks']}`",
                f"- Half graph SHA-256: `{half['graph_contract']['sha256']}`",
                f"- Final graph SHA-256: `{final['graph_contract']['sha256']}`",
                "- Stage-2 / formal support / locomotion / robot access: `0 / 0 / 0 / 0`",
                "",
                "A PASS authorizes only a separate support-controller preregistration.",
                "A HOLD forbids support-controller training. Neither outcome grants robot",
                "clearance, checkpoint selection, deployment, Gate 5, or hardware access.",
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
