#!/usr/bin/env python3
"""Safely import one completed Winner-v21 predictor-preserving training arm."""

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
PREREGISTRATION = ANALYSIS / "winner_v21_predictor_preserving_training_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v21_predictor_preserving_two_update_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
RUNNER = ROOT / "tools/run_winner_v21_predictor_preserving_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v21-predictor-preserving-training.yml"
OUTPUT_JSON = ANALYSIS / "winner_v21_predictor_preserving_training_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_TRAINING_RESULT_20260721.md"
RAW_RESULT = "winner-v21-predictor-preserving-training-result.json"
RAW_RECEIPT = "winner-v21-predictor-preserving-training-result.sha256"
WORK_PREFIX = "winner-v21-predictor-preserving-training-work"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
TRAINABLE_KEYS = {
    "obs_weight",
    "previous_action_weight",
    "hidden_weight",
    "hidden_bias",
    "action_weight",
    "action_bias",
    "training_only_log_std",
    "training_only_value_weight",
    "training_only_value_bias",
    "auxiliary_hidden_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
}
CHECKS = {
    "exact_100_predictor_preserving_updates",
    "exact_100_atomic_snapshots",
    "half_and_final_graphs_present",
    "all_updates_finite",
    "all_sampled_hidden_replays_at_most_1e_6",
    "all_stored_successor_masks_nonempty",
    "all_action_boundaries_exact",
    "all_pitch_margin_rewards_exact",
    "pitch_margin_signal_nonzero_every_update",
    "all_updates_all_12_gradients_and_deltas_nonzero",
    "all_12_leaves_changed_cumulatively",
    "frozen_predictor_scale_exact",
    "formal_support_cells_zero",
    "locomotion_steps_zero",
    "robot_or_rdk_access_zero",
}
SNAPSHOT_KEYS = {
    "path",
    "sha256",
    "bytes",
    "completed_updates",
    "state_payload_sha256",
    "metadata_payload_sha256",
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
        *(
            f"{WORK_PREFIX}/snapshots/snapshot_predictor_preserving_update_{index:03d}.npz"
            for index in range(1, 101)
        ),
        f"{WORK_PREFIX}/graphs/winner_v21_half.onnx",
        f"{WORK_PREFIX}/graphs/winner_v21_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v21 training artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v21 training artifact exceeds size ceiling")
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
                raise ValueError("Winner-v21 training artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_snapshot(receipt: Mapping[str, Any], update: int) -> None:
    if (
        set(receipt) != SNAPSHOT_KEYS | {"update"}
        or receipt.get("update") != update
        or receipt.get("completed_updates") != update
        or PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
        != f"snapshot_predictor_preserving_update_{update:03d}.npz"
        or HEX64.fullmatch(str(receipt.get("sha256", ""))) is None
        or HEX64.fullmatch(str(receipt.get("state_payload_sha256", ""))) is None
        or HEX64.fullmatch(str(receipt.get("metadata_payload_sha256", ""))) is None
        or type(receipt.get("bytes")) is not int
        or receipt["bytes"] <= 0
    ):
        raise ValueError(f"Winner-v21 snapshot {update} changed")


def validate_graph(row: Mapping[str, Any], label: str, update: int) -> None:
    if set(row) != {"label", "update", "snapshot", "graph"}:
        raise ValueError(f"Winner-v21 {label} checkpoint schema changed")
    graph = row.get("graph", {})
    contract = graph.get("contract", {})
    if (
        row.get("label") != label
        or row.get("update") != update
        or set(row.get("snapshot", {})) != SNAPSHOT_KEYS
        or graph.get("label") != label
        or graph.get("update") != update
        or PurePosixPath(str(graph.get("path", "")).replace("\\", "/")).name
        != f"winner_v21_{label}.onnx"
        or HEX64.fullmatch(str(graph.get("sha256", ""))) is None
        or type(graph.get("bytes")) is not int
        or graph["bytes"] <= 0
        or contract.get("abi_exact") is not True
        or contract.get("training_only_tensors_absent") is not True
        or contract.get("jax_onnx_at_most_1e_7") is not True
        or contract.get("previous_action_out_equals_action_bit_exact") is not True
        or contract.get("sha256") != graph.get("sha256")
        or contract.get("bytes") != graph.get("bytes")
    ):
        raise ValueError(f"Winner-v21 {label} graph changed")


def validate_result(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v21.predictor_preserving_training_result.v1"
        or value.get("status")
        != "PASS_WINNER_V21_PREDICTOR_PRESERVING_TRAINING_ARTIFACT"
        or value.get("decision")
        != "AUTHORIZE_SEPARATE_UNCHANGED_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
    ):
        raise ValueError("Winner-v21 training did not pass")
    checks = value.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != CHECKS or not all(checks.values()):
        raise ValueError("Winner-v21 training checks changed")
    if value.get("source_stage1_snapshot") != {
        "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
        "bytes": 189027,
    } or value.get("predictor_scale") != 8.393629541414427e-11:
        raise ValueError("Winner-v21 source or scale changed")
    if value.get("execution") != {
        "optimizer_updates": 100,
        "scheduled_episode_slots": 2_000_000,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or value.get("authority") != {
        "formal_support_gate_executed": False,
        "locomotion_executed": False,
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a separately frozen unchanged support/context gate",
    }:
        raise ValueError("Winner-v21 execution or authority changed")
    if value.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v21 training sources changed")
    population = value.get("population", {})
    if (
        population.get("environments_per_update") != 80
        or population.get("cumulative_sampled_count", 0) <= 0
        or population.get("cumulative_valid_transition_count", 0) <= 0
        or population.get("cumulative_stored_successor_count", 0) <= 0
    ):
        raise ValueError("Winner-v21 training population changed")
    metrics = value.get("metrics")
    if (
        not isinstance(metrics, list)
        or len(metrics) != 100
        or [row.get("update") for row in metrics] != list(range(1, 101))
    ):
        raise ValueError("Winner-v21 update sequence changed")
    sampled_total = valid_total = stored_total = 0
    for index, row in enumerate(metrics, 1):
        gradients = row.get("combined_gradient_max_abs", {})
        deltas = row.get("leaf_max_abs_delta", {})
        sampled = row.get("sampled_count")
        valid = row.get("valid_transition_count")
        stored = row.get("stored_successor_transition_count")
        if (
            type(sampled) is not int
            or type(valid) is not int
            or type(stored) is not int
            or not sampled >= valid > 0
            or not stored > 0
            or HEX64.fullmatch(str(row.get("episode_receipts_sha256", ""))) is None
            or set(gradients) != TRAINABLE_KEYS
            or set(deltas) != TRAINABLE_KEYS
            or not all(type(item) is float and item > 0.0 for item in gradients.values())
            or not all(type(item) is float and item > 0.0 for item in deltas.values())
            or row.get("ppo_metrics", {}).get("sampled_hidden_replay_max_abs_error", 2.0)
            > 1.0e-6
            or row.get("predictor_metrics", {}).get("stored_successor_transition_count")
            != float(stored)
            or row.get("action_boundary", {}).get("realized_equals_numpy_bit_exact")
            is not True
            or row.get("action_boundary", {}).get("numpy_equals_jax_bit_exact") is not True
            or row.get("pitch_margin_reward", {}).get("reward_formula_bit_exact") is not True
            or row.get("pitch_margin_reward", {}).get("nonzero_penalty_count", 0) <= 0
        ):
            raise ValueError(f"Winner-v21 metric {index} changed")
        sampled_total += sampled
        valid_total += valid
        stored_total += stored
    if (
        sampled_total != population["cumulative_sampled_count"]
        or valid_total != population["cumulative_valid_transition_count"]
        or stored_total != population["cumulative_stored_successor_count"]
    ):
        raise ValueError("Winner-v21 cumulative counts changed")
    cumulative = value.get("joint_leaf_max_abs_delta", {})
    if set(cumulative) != TRAINABLE_KEYS or not all(
        type(item) is float and item > 0.0 for item in cumulative.values()
    ):
        raise ValueError("Winner-v21 cumulative leaf deltas changed")
    snapshots = value.get("snapshot_manifest")
    if not isinstance(snapshots, list) or len(snapshots) != 100:
        raise ValueError("Winner-v21 snapshot manifest changed")
    for index, receipt in enumerate(snapshots, 1):
        validate_snapshot(receipt, index)
    checkpoints = value.get("persistent_checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != 2:
        raise ValueError("Winner-v21 checkpoints changed")
    validate_graph(checkpoints[0], "half", 50)
    validate_graph(checkpoints[1], "final", 100)
    if checkpoints[0]["snapshot"] != {
        key: snapshots[49][key] for key in SNAPSHOT_KEYS
    } or checkpoints[1]["snapshot"] != {
        key: snapshots[99][key] for key in SNAPSHOT_KEYS
    }:
        raise ValueError("Winner-v21 checkpoint snapshot binding changed")
    if not finite_tree(value) or value.get("elapsed_seconds", 0.0) <= 0.0:
        raise ValueError("Winner-v21 training contains invalid numeric evidence")


def verify_payloads(members: Mapping[str, bytes], value: Mapping[str, Any]) -> None:
    for index, receipt in enumerate(value["snapshot_manifest"], 1):
        payload = members[
            f"{WORK_PREFIX}/snapshots/snapshot_predictor_preserving_update_{index:03d}.npz"
        ]
        if sha256_bytes(payload) != receipt["sha256"] or len(payload) != receipt["bytes"]:
            raise ValueError(f"Winner-v21 snapshot {index} payload changed")
    for row in value["persistent_checkpoints"]:
        graph = row["graph"]
        payload = members[f"{WORK_PREFIX}/graphs/winner_v21_{row['label']}.onnx"]
        if sha256_bytes(payload) != graph["sha256"] or len(payload) != graph["bytes"]:
            raise ValueError(f"Winner-v21 {row['label']} graph payload changed")


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
        raise FileExistsError("Winner-v21 training result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v21-predictor-preserving-training-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v21 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v21 result receipt changed")
    value = json.loads(
        members[RAW_RESULT].decode("utf-8"), parse_constant=reject_nonfinite
    )
    validate_result(value)
    verify_payloads(members, value)
    payload = dict(value)
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
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    half, final = payload["persistent_checkpoints"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v21 predictor-preserving training result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Half / final graph SHA-256: `{half['graph']['sha256']} / {final['graph']['sha256']}`",
                "- All twelve existing trainable leaves changed on all 100 updates",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "A pass authorizes only a separately frozen unchanged support/context gate",
                "over both checkpoints. It is not locomotion or robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
