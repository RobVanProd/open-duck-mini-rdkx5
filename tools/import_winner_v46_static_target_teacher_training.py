#!/usr/bin/env python3
"""Strictly import the sole Winner-v46 static-target-teacher training artifact."""

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
PREREGISTRATION = ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
V45_RESULT = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
RUNNER = ROOT / "tools/run_winner_v46_static_target_teacher_training.py"
OUTPUT_JSON = ANALYSIS / "winner_v46_static_target_teacher_training_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_RESULT_20260722.md"
RAW_RESULT = "winner-v46-static-target-teacher-training-result.json"
RAW_RECEIPT = "winner-v46-static-target-teacher-training-result.sha256"
WORK = "winner-v46-static-target-teacher-training-work"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GRADIENT_KEYS = {
    "action_bias", "action_weight", "auxiliary_action_weight", "auxiliary_bias",
    "auxiliary_hidden_weight", "hidden_bias", "hidden_weight", "obs_weight",
    "previous_action_weight", "training_only_log_std", "training_only_value_bias",
    "training_only_value_weight",
}
POLICY_KEYS = {
    "action_bias", "action_weight", "hidden_bias", "hidden_weight", "obs_weight",
    "previous_action_weight",
}
NONPOLICY_KEYS = GRADIENT_KEYS - POLICY_KEYS


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
    raise ValueError(f"nonfinite JSON constant: {value}")


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
        *(f"{WORK}/snapshots/snapshot_static_target_teacher_update_{index:03d}.npz" for index in range(253, 353)),
        f"{WORK}/graphs/winner_v46_half.onnx",
        f"{WORK}/graphs/winner_v46_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v46 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v46 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v46 artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def _positive_tree(value: Any, label: str) -> bool:
    if not isinstance(value, Mapping) or set(value) != GRADIENT_KEYS:
        raise ValueError(f"Winner-v46 {label} tree changed")
    if not all(type(item) in {int, float} and math.isfinite(float(item)) and item > 0 for item in value.values()):
        raise ValueError(f"Winner-v46 {label} tree is nonpositive")
    return True


def _policy_tree(value: Any, label: str) -> bool:
    if not isinstance(value, Mapping) or set(value) != GRADIENT_KEYS:
        raise ValueError(f"Winner-v46 {label} tree changed")
    if (
        not all(type(value[key]) in {int, float} and math.isfinite(float(value[key])) and value[key] > 0 for key in POLICY_KEYS)
        or not all(value[key] == 0 for key in NONPOLICY_KEYS)
    ):
        raise ValueError(f"Winner-v46 {label} support changed")
    return True


def validate_result(value: Mapping[str, Any]) -> None:
    passed = value.get("status") == "PASS_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT"
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        value.get("schema_version") != "winner_v46.static_target_teacher_training_result.v1"
        or value.get("status") not in {
            "PASS_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT",
            "HOLD_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT",
        }
        or value.get("decision") != (
            "AUTHORIZE_STATIC_TARGET_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"
            if passed else "DO_NOT_EVALUATE_WINNER_V46_POLICY"
        )
        or value.get("objective") != prereg["objective"]
        or value.get("execution") != {
            "optimizer_updates": 100, "scheduled_episode_slots": 2_000_000,
            "formal_support_cells": 0, "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("authority") != {
            "robot_clearance": False,
            "training_executed": True,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate frozen static-target-teacher support gate preregistration",
        }
        or not finite_tree(value)
    ):
        raise ValueError("Winner-v46 result schema changed")
    source = prereg["source_checkpoint"]
    teacher = prereg["teacher_checkpoint"]
    if value.get("source_snapshot") != {
        "sha256": source["snapshot"]["sha256"], "bytes": source["snapshot"]["bytes"],
        "completed_updates": 252, "optimizer_count": 252,
    } or value.get("source_graph") != {
        "sha256": source["graph"]["sha256"], "bytes": source["graph"]["bytes"],
        "completed_updates": 252,
    } or value.get("teacher_snapshot") != {
        "sha256": teacher["snapshot"]["sha256"], "bytes": teacher["snapshot"]["bytes"],
        "completed_updates": 100, "optimizer_count": 100,
    }:
        raise ValueError("Winner-v46 source identities changed")
    if value.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "v45_result_lf_sha256": lf_sha256(V45_RESULT),
        "v42_result_lf_sha256": lf_sha256(V42_RESULT),
        "v22_result_lf_sha256": lf_sha256(V22_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v46 source hashes changed")
    metrics = value.get("metrics")
    snapshots = value.get("snapshot_manifest")
    checkpoints = value.get("persistent_checkpoints")
    if (
        not isinstance(metrics, list) or len(metrics) != 100
        or [row.get("local_update") for row in metrics] != list(range(1, 101))
        or [row.get("rollout_update_index") for row in metrics] != list(range(252, 352))
        or [row.get("completed_updates") for row in metrics] != list(range(253, 353))
        or [row.get("optimizer_count") for row in metrics] != list(range(253, 353))
        or not isinstance(snapshots, list) or len(snapshots) != 100
        or [row.get("completed_updates") for row in snapshots] != list(range(253, 353))
        or not isinstance(checkpoints, list)
        or [(row.get("label"), row.get("completed_updates")) for row in checkpoints]
        != [("half", 302), ("final", 352)]
    ):
        raise ValueError("Winner-v46 sequence changed")
    for row in metrics:
        if (
            HEX64.fullmatch(str(row.get("episode_receipts_sha256"))) is None
            or row.get("sampled_count", 0) <= 0
            or row.get("valid_transition_count", 0) <= 0
            or row.get("stored_successor_transition_count", 0) <= 0
            or row.get("roll_pitch_failure_count", -1) < 0
            or row.get("action_boundary_exact") is not True
            or row.get("pitch_margin_reward_exact") is not True
            or row.get("heldout_teacher_labels_absent") is not True
            or row.get("sampled_hidden_replay_max_abs_error", 2.0) > 1.0e-6
            or row.get("selected_anchor_elements") != 384
            or row.get("selected_teacher_rows") != 22
            or row.get("selected_teacher_elements", 0) <= 0
            or row.get("static_target_teacher_loss", -1.0) < 0.0
            or row.get("maximum_selected_teacher_action_delta", -1.0) < 0.0
            or not (
                (row.get("roll_pitch_failure_count", 0) > 0
                 and row.get("objective_evidence", {}).get("zero_failure_bit_exact_noop") is False)
                or (row.get("roll_pitch_failure_count") == 0
                    and row.get("objective_evidence", {}).get("zero_failure_bit_exact_noop") is True)
            )
            or not _policy_tree(row.get("anchor_gradient_max_abs"), "anchor gradient")
            or not _policy_tree(row.get("teacher_gradient_max_abs"), "teacher gradient")
            or not _positive_tree(row.get("combined_gradient_max_abs"), "combined gradient")
            or not _positive_tree(row.get("leaf_max_abs_delta"), "leaf delta")
        ):
            raise ValueError("Winner-v46 metric changed")
    if not _positive_tree(value.get("cumulative_leaf_max_abs_delta"), "cumulative delta"):
        raise ValueError("Winner-v46 cumulative delta changed")
    for row in snapshots:
        if (
            Path(str(row.get("path"))).name
            != f"snapshot_static_target_teacher_update_{row['completed_updates']:03d}.npz"
            or int(row.get("bytes", 0)) <= 0
            or HEX64.fullmatch(str(row.get("sha256"))) is None
        ):
            raise ValueError("Winner-v46 snapshot receipt changed")
    for row in checkpoints:
        graph = row.get("graph", {})
        contract = graph.get("contract", {})
        if (
            Path(str(graph.get("path"))).name != f"winner_v46_{row['label']}.onnx"
            or int(graph.get("bytes", 0)) <= 0
            or HEX64.fullmatch(str(graph.get("sha256"))) is None
            or graph.get("v46_forbidden_tokens_present") != []
            or contract.get("abi_exact") is not True
            or contract.get("training_only_tensors_absent") is not True
            or contract.get("jax_onnx_at_most_1e_7") is not True
            or contract.get("previous_action_out_equals_action_bit_exact") is not True
        ):
            raise ValueError("Winner-v46 checkpoint graph changed")
    checks = {
        "source_snapshot_graph_and_optimizer_count_252_exact": True,
        "teacher_snapshot_and_optimizer_count_100_exact": True,
        "teacher_trainable_leaves_unchanged": True,
        "frozen_parameter_leaves_unchanged": True,
        "exact_100_continuation_updates": True,
        "all_100_episode_receipts_present": True,
        "all_100_action_boundaries_exact": True,
        "all_100_pitch_margin_rewards_exact": True,
        "all_100_objective_failure_or_zero_failure_noop_contracts_exact": True,
        "all_100_static_teacher_contracts_exact": True,
        "all_100_prefix_anchor_contracts_exact": True,
        "all_100_hidden_replays_at_most_1e_6": True,
        "all_100_stored_successor_masks_nonempty": True,
        "all_100_updates_all_12_gradients_and_deltas_nonzero": True,
        "all_12_leaves_changed_cumulatively": True,
        "exact_100_atomic_snapshots": True,
        "optimizer_count_352_exact": metrics[-1]["optimizer_count"] == 352,
        "half_and_final_graphs_present": True,
        "all_updates_finite": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    if value.get("checks") != checks:
        raise ValueError("Winner-v46 checks are not rederived")
    failed = sorted(name for name, flag in checks.items() if flag is not True)
    if value.get("failed_checks") != failed or (passed and failed):
        raise ValueError("Winner-v46 classification changed")


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
        raise FileExistsError("Winner-v46 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0 or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None or args.artifact_id <= 0
        or args.artifact_name != f"winner-v46-static-target-teacher-training-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v46 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v46 raw receipt changed")
    raw = json.loads(members[RAW_RESULT].decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    for row in raw["snapshot_manifest"]:
        name = f"{WORK}/snapshots/snapshot_static_target_teacher_update_{row['completed_updates']:03d}.npz"
        if sha256_bytes(members[name]) != row["sha256"] or len(members[name]) != row["bytes"]:
            raise ValueError(f"Winner-v46 snapshot {row['completed_updates']} changed")
    for row in raw["persistent_checkpoints"]:
        name = f"{WORK}/graphs/winner_v46_{row['label']}.onnx"
        graph = row["graph"]
        if sha256_bytes(members[name]) != graph["sha256"] or len(members[name]) != graph["bytes"]:
            raise ValueError(f"Winner-v46 {row['label']} graph changed")
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
    OUTPUT_JSON.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    half, final = result["persistent_checkpoints"]
    OUTPUT_MD.write_text("\n".join([
        "# Winner-v46 static-target teacher training result", "",
        f"- Status: `{result['status']}`", f"- Decision: `{result['decision']}`",
        f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
        f"- Artifact ZIP SHA-256: `{zip_sha}`",
        f"- Half / final ONNX SHA-256: `{half['graph']['sha256']}` / `{final['graph']['sha256']}`",
        "- Source / final optimizer count: `252 / 352`",
        "- Formal support / robot: `0 / 0`", "",
        "A pass authorizes only a separately frozen support and context gate.", "",
    ]), encoding="utf-8")
    print(result["status"])
    print(f"HALF_ONNX_SHA256={half['graph']['sha256']}")
    print(f"FINAL_ONNX_SHA256={final['graph']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
