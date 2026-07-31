#!/usr/bin/env python3
"""Safely import the fresh corrected Winner-v13 Stage-1 v2 artifact."""

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
PREREG = ANALYSIS / "winner_v13_normalized_response_stage1_v2_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v13_normalized_response_cpu_contract_result.json"
CHECKER_RESULT = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_result.json"
INVALID_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_result.json"
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_stage1_v2.py"
PRIMITIVES = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v13-normalized-response-stage1-v2.yml"
OUTPUT_JSON = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V13_NORMALIZED_RESPONSE_STAGE1_V2_RESULT_20260721.md"
RAW_RESULT = "winner-v13-normalized-response-stage1-v2-result.json"
RAW_RECEIPT = "winner-v13-normalized-response-stage1-v2-result.sha256"
RAW_LOG = "winner-v13-normalized-response-stage1-v2.log"
WORK_PREFIX = "winner-v13-normalized-response-stage1-v2-work"
PLANTS = {"P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"}
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
    "checker_same_input_all_outputs_at_most_1e_7",
    "checker_previous_action_out_equals_action_bit_exact",
    "checker_nonzero_bounded_action_observed",
    "checker_zero_previous_action_exact_zero",
    "deployable_onnx_abi_exact",
    "deployable_onnx_training_only_tensors_absent",
    "deployable_onnx_chain_at_most_1e_7",
}
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


def artifact_members() -> set[str]:
    return {
        RAW_RESULT,
        RAW_RECEIPT,
        RAW_LOG,
        *(
            f"{WORK_PREFIX}/snapshots/snapshot_stage1_update_{index:03d}.npz"
            for index in range(1, 101)
        ),
        f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_half.onnx",
        f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v13 Stage-1 v2 artifact inventory changed")
        if sum(item.file_size for item in infos) > 150_000_000:
            raise ValueError("Winner-v13 Stage-1 v2 artifact exceeds size ceiling")
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
                raise ValueError("Winner-v13 Stage-1 v2 artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def validate_checks(checks: Any, expected: set[str], failed: Any) -> None:
    if (
        not isinstance(checks, dict)
        or set(checks) != expected
        or not all(type(value) is bool for value in checks.values())
        or failed != sorted(name for name, passed in checks.items() if not passed)
    ):
        raise ValueError("Winner-v13 Stage-1 v2 check schema changed")


def validate_checkpoint(row: Mapping[str, Any], label: str, update: int) -> None:
    if row.get("label") != label or row.get("update") != update:
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} identity changed")
    validate_checks(row.get("checks"), CHECKPOINT_CHECKS, row.get("failed_checks"))
    if row.get("failed_checks") != []:
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} did not pass")
    plants = row.get("predictor_by_plant")
    if not isinstance(plants, dict) or set(plants) != PLANTS:
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} plants changed")
    for metric in plants.values():
        learned = metric.get("learned_normalized_mse_all_50")
        baseline = metric.get("constant_normalized_mse_all_50")
        if (
            metric.get("valid_transition_count", 0) <= 0
            or not finite(learned)
            or not finite(baseline)
            or metric.get("learned_strictly_below_constant") is not (learned < baseline)
        ):
            raise ValueError(f"Winner-v13 Stage-1 v2 {label} predictor changed")
    contexts = row.get("context_separation")
    if (
        not isinstance(contexts, list)
        or [item.get("configuration_id") for item in contexts]
        != [f"HELDOUT_{index:02d}" for index in range(16)]
        or not all(item.get("separation_above_1e_7") is True for item in contexts)
    ):
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} contexts changed")
    errors = row.get("checker_same_input_max_abs_errors", {})
    if (
        set(errors) != {"action", "previous_action_out", "hidden"}
        or not all(finite(value) and 0 <= value <= 1e-7 for value in errors.values())
        or row.get("checker_onnx_ticks", 0) <= 0
        or row.get("checker_nonzero_bounded_action_ticks", 0) <= 0
    ):
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} checker changed")
    graph = row.get("graph_contract", {})
    if (
        graph.get("abi_exact") is not True
        or graph.get("training_only_tensors_absent") is not True
        or graph.get("jax_onnx_at_most_1e_7") is not True
        or graph.get("previous_action_out_equals_action_bit_exact") is not True
        or HEX64.fullmatch(str(graph.get("sha256"))) is None
        or graph.get("bytes", 0) <= 0
    ):
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} graph changed")
    snapshot = row.get("snapshot", {})
    if (
        HEX64.fullmatch(str(snapshot.get("sha256"))) is None
        or snapshot.get("bytes", 0) <= 0
        or snapshot.get("bit_exact_readback") is not True
    ):
        raise ValueError(f"Winner-v13 Stage-1 v2 {label} snapshot changed")


def validate_result(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v13.normalized_response_stage1_result.v2"
    ):
        raise ValueError("Winner-v13 Stage-1 v2 schema changed")
    if (
        value.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or value.get("decision")
        != "AUTHORIZE_SUPPORT_CONTROLLER_PREREGISTRATION_ONLY"
    ):
        raise ValueError("Winner-v13 Stage-1 v2 did not pass")
    validate_checks(value.get("checks"), RUN_CHECKS, value.get("failed_checks"))
    if value.get("failed_checks") != []:
        raise ValueError("Winner-v13 Stage-1 v2 run checks failed")
    if value.get("execution") != {
        "stage1_optimizer_updates": 100,
        "stage2_optimizer_updates": 0,
        "training_episode_slots": 2_000_000,
        "heldout_evaluation_cells": 64,
        "heldout_repeat_cells": 64,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v13 Stage-1 v2 execution boundary changed")
    expected_sources = {
        "preregistration_lf_sha256": lf_sha256(PREREG),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "checker_v2_cpu_result_lf_sha256": lf_sha256(CHECKER_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "v13_primitives_lf_sha256": lf_sha256(PRIMITIVES),
    }
    if value.get("sources") != expected_sources:
        raise ValueError("Winner-v13 Stage-1 v2 source identities changed")
    metrics = value.get("metrics")
    snapshots = value.get("snapshot_manifest")
    checkpoints = value.get("checkpoint_results")
    if (
        not isinstance(metrics, list)
        or [row.get("update") for row in metrics] != list(range(1, 101))
        or not isinstance(snapshots, list)
        or len(snapshots) != 100
        or not isinstance(checkpoints, list)
        or len(checkpoints) != 2
    ):
        raise ValueError("Winner-v13 Stage-1 v2 sequence changed")
    for index, receipt in enumerate(snapshots, 1):
        if (
            PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
            != f"snapshot_stage1_update_{index:03d}.npz"
            or HEX64.fullmatch(str(receipt.get("sha256"))) is None
            or receipt.get("bytes", 0) <= 0
            or receipt.get("bit_exact_readback") is not True
        ):
            raise ValueError(f"Winner-v13 Stage-1 v2 snapshot {index} changed")
    validate_checkpoint(checkpoints[0], "half", 50)
    validate_checkpoint(checkpoints[1], "final", 100)


def cross_run_diagnostic(
    value: Mapping[str, Any], invalid: Mapping[str, Any]
) -> dict[str, Any]:
    metrics = value["metrics"]
    old_metrics = invalid["metrics"]
    checkpoint_rows = value["checkpoint_results"]
    old_checkpoint_rows = invalid["checkpoint_results"]
    loss_deltas = [
        abs(float(left["loss"]) - float(right["loss"]))
        for left, right in zip(metrics, old_metrics)
    ]
    predictor_deltas = []
    for left_checkpoint, right_checkpoint in zip(
        checkpoint_rows, old_checkpoint_rows
    ):
        for plant in sorted(PLANTS):
            left = left_checkpoint["predictor_by_plant"][plant]
            right = right_checkpoint["predictor_by_plant"][plant]
            for name, left_value in left.items():
                right_value = right[name]
                if type(left_value) in {int, float} and type(right_value) in {
                    int,
                    float,
                }:
                    predictor_deltas.append(abs(float(left_value) - float(right_value)))
    context_deltas = [
        abs(
            float(left_context["final_valid_h_out_linf_plant_separation"])
            - float(right_context["final_valid_h_out_linf_plant_separation"])
        )
        for left_checkpoint, right_checkpoint in zip(
            checkpoint_rows, old_checkpoint_rows
        )
        for left_context, right_context in zip(
            left_checkpoint["context_separation"],
            right_checkpoint["context_separation"],
        )
    ]
    metric_counts_exact = all(
        all(left[name] == right[name] for name in (
            "update",
            "sampled_count",
            "valid_transition_count",
            "completed_episodes",
        ))
        for left, right in zip(metrics, old_metrics)
    )
    gate_outcomes_exact = [row["checks"] for row in checkpoint_rows] == [
        {
            **{
                name: old["checks"][name]
                for name in (
                    "exact_32_heldout_cells",
                    "heldout_repeat_bit_exact",
                    "learned_prediction_beats_constant_per_plant",
                    "all_16_plant_contexts_separate",
                    "deployable_onnx_abi_exact",
                    "deployable_onnx_training_only_tensors_absent",
                    "deployable_onnx_chain_at_most_1e_7",
                )
            },
            "checker_same_input_all_outputs_at_most_1e_7": True,
            "checker_previous_action_out_equals_action_bit_exact": True,
            "checker_nonzero_bounded_action_observed": True,
            "checker_zero_previous_action_exact_zero": True,
        }
        for old in old_checkpoint_rows
    ]
    return {
        "role": "diagnostic_only_not_a_post_hoc_gate",
        "normalization_exact": value["normalization"] == invalid["normalization"],
        "training_population_counts_exact": metric_counts_exact,
        "scientific_and_deployable_gate_outcomes_exact": gate_outcomes_exact,
        "episode_receipt_hashes_exact": [
            row["episode_receipts_sha256"] for row in metrics
        ]
        == [row["episode_receipts_sha256"] for row in old_metrics],
        "half_final_graph_sha256_exact": [
            row["graph_contract"]["sha256"] for row in checkpoint_rows
        ]
        == [row["graph_contract"]["sha256"] for row in old_checkpoint_rows],
        "training_loss_max_abs_delta": max(loss_deltas),
        "heldout_predictor_metric_max_abs_delta": max(predictor_deltas),
        "heldout_context_separation_max_abs_delta": max(context_deltas),
    }


def verify_payloads(members: Mapping[str, bytes], value: Mapping[str, Any]) -> None:
    for index, receipt in enumerate(value["snapshot_manifest"], 1):
        payload = members[
            f"{WORK_PREFIX}/snapshots/snapshot_stage1_update_{index:03d}.npz"
        ]
        if sha256_bytes(payload) != receipt["sha256"] or len(payload) != receipt["bytes"]:
            raise ValueError(f"Winner-v13 Stage-1 v2 snapshot {index} artifact changed")
    for checkpoint in value["checkpoint_results"]:
        label = checkpoint["label"]
        payload = members[
            f"{WORK_PREFIX}/graphs/winner_v13_normalized_response_{label}.onnx"
        ]
        graph = checkpoint["graph_contract"]
        if sha256_bytes(payload) != graph["sha256"] or len(payload) != graph["bytes"]:
            raise ValueError(f"Winner-v13 Stage-1 v2 {label} graph artifact changed")


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
        raise FileExistsError("Winner-v13 Stage-1 v2 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name
        != f"winner-v13-normalized-response-stage1-v2-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v13 Stage-1 v2 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v13 Stage-1 v2 result receipt changed")
    value = json.loads(members[RAW_RESULT].decode("utf-8"))
    validate_result(value)
    verify_payloads(members, value)
    payload = dict(value)
    payload["cross_run_diagnostic"] = cross_run_diagnostic(
        value, json.loads(INVALID_RESULT.read_text(encoding="utf-8"))
    )
    payload["repository_attribution"] = {
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
        "log_sha256": sha256_bytes(members[RAW_LOG]),
        "preregistration_lf_sha256": lf_sha256(PREREG),
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
                "# Winner-v13 normalized-response Stage-1 v2 result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / attempt: `{args.run_id} / 1`",
                f"- Artifact ID / ZIP SHA-256: `{args.artifact_id}` / `{zip_sha}`",
                f"- Half / final loss: `{payload['metrics'][49]['loss']} / {payload['metrics'][99]['loss']}`",
                f"- Half / final graph SHA-256: `{half['graph_contract']['sha256']} / {final['graph_contract']['sha256']}`",
                f"- Cross-run max loss / predictor / context delta: `{payload['cross_run_diagnostic']['training_loss_max_abs_delta']} / {payload['cross_run_diagnostic']['heldout_predictor_metric_max_abs_delta']} / {payload['cross_run_diagnostic']['heldout_context_separation_max_abs_delta']}`",
                "- Cross-run comparison role: `diagnostic only; not a post-hoc gate`",
                "- Stage-2 / formal support / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                "A pass authorizes only a separate support-controller preregistration.",
                "It does not authorize locomotion, checkpoint selection, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
