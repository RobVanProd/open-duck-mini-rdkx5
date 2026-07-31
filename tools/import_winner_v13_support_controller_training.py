#!/usr/bin/env python3
"""Safely import a completed Winner-v13 support-controller training artifact."""

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
PREREGISTRATION = ANALYSIS / "winner_v13_support_controller_training_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v13_support_controller_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
RUNNER = ROOT / "tools/run_winner_v13_support_controller_training.py"
WORKFLOW = ROOT / ".github/workflows/winner-v13-support-controller-training.yml"
OUTPUT_JSON = ANALYSIS / "winner_v13_support_controller_training_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V13_SUPPORT_CONTROLLER_TRAINING_RESULT_20260721.md"
RAW_RESULT = "winner-v13-support-controller-training-result.json"
RAW_RECEIPT = "winner-v13-support-controller-training-result.sha256"
RAW_LOG = "winner-v13-support-controller-training.log"
WORK_PREFIX = "winner-v13-support-controller-training-work"
CHECKS = {
    "exact_100_stage2_updates",
    "exact_100_atomic_snapshots",
    "half_and_final_graphs_present",
    "stage1_tree_bit_exact_frozen",
    "all_stage2_leaves_changed",
    "all_updates_finite",
    "all_action_boundaries_exact",
    "formal_support_cells_zero",
    "locomotion_steps_zero",
    "robot_or_rdk_access_zero",
}
STAGE2_LEAVES = {
    "action_bias",
    "action_weight",
    "training_only_log_std",
    "training_only_value_bias",
    "training_only_value_weight",
}
METRIC_KEYS = {
    "update",
    "loss",
    "sampled_count",
    "valid_transition_count",
    "completed_episodes",
    "episode_receipts_sha256",
    "gradient_max_abs",
    "action_boundary",
    "entropy",
    "policy_loss",
    "ratio_max",
    "ratio_min",
    "value_loss",
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


def finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def artifact_members() -> set[str]:
    return {
        RAW_RESULT,
        RAW_RECEIPT,
        RAW_LOG,
        *(f"{WORK_PREFIX}/snapshots/snapshot_stage2_update_{index:03d}.npz" for index in range(1, 101)),
        f"{WORK_PREFIX}/graphs/winner_v13_support_controller_half.onnx",
        f"{WORK_PREFIX}/graphs/winner_v13_support_controller_final.onnx",
    }


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v13 support-training artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v13 support-training artifact exceeds size ceiling")
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
                raise ValueError("Winner-v13 support-training artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def validate_boundary(boundary: Any, sampled: int) -> None:
    if (
        not isinstance(boundary, dict)
        or boundary.get("attempted_samples") != sampled
        or boundary.get("realized_equals_numpy_bit_exact") is not True
        or boundary.get("numpy_equals_jax_bit_exact") is not True
        or boundary.get("maximum_realized_numpy_error") != 0.0
        or boundary.get("maximum_numpy_jax_error") != 0.0
    ):
        raise ValueError("Winner-v13 support-training action boundary changed")
    for name in (
        "raw_sha256",
        "previous_action_sha256",
        "realized_action_sha256",
        "numpy_expected_sha256",
        "jax_expected_sha256",
    ):
        if HEX64.fullmatch(str(boundary.get(name))) is None:
            raise ValueError("Winner-v13 support-training boundary hash changed")


def validate_graph(row: Mapping[str, Any], label: str, update: int) -> None:
    if row.get("label") != label or row.get("update") != update:
        raise ValueError(f"Winner-v13 support {label} checkpoint identity changed")
    graph = row.get("graph", {})
    if (
        graph.get("abi_exact") is not True
        or graph.get("all_initializers_finite") is not True
        or graph.get("all_chain_outputs_finite") is not True
        or graph.get("training_only_tensors_absent") is not True
        or graph.get("jax_onnx_at_most_1e_7") is not True
        or graph.get("previous_action_out_equals_action_bit_exact") is not True
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
        or not finite(graph.get("jax_onnx_max_abs_error"))
        or graph["jax_onnx_max_abs_error"] > 1e-7
        or HEX64.fullmatch(str(graph.get("sha256"))) is None
        or graph.get("bytes", 0) <= 0
    ):
        raise ValueError(f"Winner-v13 support {label} graph changed")


def validate_result(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v13.support_controller_training_result.v1"
        or value.get("status")
        != "PASS_WINNER_V13_SUPPORT_CONTROLLER_TRAINING_ARTIFACT"
        or value.get("decision")
        != "AUTHORIZE_SEPARATE_124_CELL_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
    ):
        raise ValueError("Winner-v13 support-controller training did not pass")
    checks = value.get("checks")
    if (
        not isinstance(checks, dict)
        or set(checks) != CHECKS
        or not all(item is True for item in checks.values())
    ):
        raise ValueError("Winner-v13 support-training checks changed")
    if value.get("execution") != {
        "stage2_optimizer_updates": 100,
        "scheduled_episode_slots": 2_000_000,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v13 support-training execution boundary changed")
    if value.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
        "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v13 support-training sources changed")
    authority = value.get("authority")
    if authority != {
        "formal_support_gate_executed": False,
        "locomotion_executed": False,
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a separately frozen 124-cell support/context gate",
    }:
        raise ValueError("Winner-v13 support-training authority changed")
    source = value.get("source_stage1_snapshot", {})
    if (
        source.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or source.get("bytes") != 189027
        or HEX64.fullmatch(str(source.get("frozen_stage1_tree_sha256"))) is None
    ):
        raise ValueError("Winner-v13 support-training Stage-1 source changed")
    population = value.get("population", {})
    if (
        population.get("environments_per_update") != 80
        or population.get("cumulative_sampled_count", 0) <= 0
        or population.get("cumulative_valid_transition_count", 0) <= 0
        or population["cumulative_valid_transition_count"]
        > population["cumulative_sampled_count"]
    ):
        raise ValueError("Winner-v13 support-training population changed")
    metrics = value.get("metrics")
    if (
        not isinstance(metrics, list)
        or len(metrics) != 100
        or [row.get("update") for row in metrics] != list(range(1, 101))
    ):
        raise ValueError("Winner-v13 support-training update sequence changed")
    sampled_total = 0
    valid_total = 0
    for row in metrics:
        if set(row) != METRIC_KEYS:
            raise ValueError("Winner-v13 support-training metric schema changed")
        sampled = row["sampled_count"]
        valid = row["valid_transition_count"]
        if (
            type(sampled) is not int
            or type(valid) is not int
            or not (sampled >= valid > 0)
            or HEX64.fullmatch(str(row["episode_receipts_sha256"])) is None
            or not all(
                finite(row[name])
                for name in (
                    "loss",
                    "entropy",
                    "policy_loss",
                    "ratio_max",
                    "ratio_min",
                    "value_loss",
                )
            )
            or not isinstance(row["gradient_max_abs"], dict)
            or set(row["gradient_max_abs"]) != STAGE2_LEAVES
            or not all(finite(item) for item in row["gradient_max_abs"].values())
        ):
            raise ValueError("Winner-v13 support-training metric changed")
        validate_boundary(row["action_boundary"], sampled)
        sampled_total += sampled
        valid_total += valid
    if (
        sampled_total != population["cumulative_sampled_count"]
        or valid_total != population["cumulative_valid_transition_count"]
    ):
        raise ValueError("Winner-v13 support-training cumulative counts changed")
    deltas = value.get("stage2_leaf_max_abs_delta")
    if (
        not isinstance(deltas, dict)
        or set(deltas) != STAGE2_LEAVES
        or not all(finite(item) and item > 0.0 for item in deltas.values())
    ):
        raise ValueError("Winner-v13 support-training leaf deltas changed")
    snapshots = value.get("snapshot_manifest")
    if not isinstance(snapshots, list) or len(snapshots) != 100:
        raise ValueError("Winner-v13 support-training snapshot manifest changed")
    for index, receipt in enumerate(snapshots, 1):
        if (
            PurePosixPath(str(receipt.get("path", "")).replace("\\", "/")).name
            != f"snapshot_stage2_update_{index:03d}.npz"
            or HEX64.fullmatch(str(receipt.get("sha256"))) is None
            or receipt.get("bytes", 0) <= 0
            or receipt.get("bit_exact_readback") is not True
        ):
            raise ValueError(f"Winner-v13 support snapshot {index} changed")
    checkpoints = value.get("persistent_checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != 2:
        raise ValueError("Winner-v13 support checkpoints changed")
    validate_graph(checkpoints[0], "half", 50)
    validate_graph(checkpoints[1], "final", 100)


def verify_payloads(members: Mapping[str, bytes], value: Mapping[str, Any]) -> None:
    for index, receipt in enumerate(value["snapshot_manifest"], 1):
        payload = members[
            f"{WORK_PREFIX}/snapshots/snapshot_stage2_update_{index:03d}.npz"
        ]
        if sha256_bytes(payload) != receipt["sha256"] or len(payload) != receipt["bytes"]:
            raise ValueError(f"Winner-v13 support snapshot {index} payload changed")
    for row in value["persistent_checkpoints"]:
        graph = row["graph"]
        payload = members[
            f"{WORK_PREFIX}/graphs/winner_v13_support_controller_{row['label']}.onnx"
        ]
        if sha256_bytes(payload) != graph["sha256"] or len(payload) != graph["bytes"]:
            raise ValueError(f"Winner-v13 support {row['label']} graph payload changed")


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
        raise FileExistsError("Winner-v13 support-training result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v13-support-controller-training-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v13 support-training repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v13 support-training result receipt changed")
    value = json.loads(members[RAW_RESULT].decode("utf-8"))
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
        "log_sha256": sha256_bytes(members[RAW_LOG]),
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
                "# Winner-v13 support-controller training result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Sampled / valid transitions: `{payload['population']['cumulative_sampled_count']} / {payload['population']['cumulative_valid_transition_count']}`",
                f"- Half / final graph SHA-256: `{half['graph']['sha256']} / {final['graph']['sha256']}`",
                "- Stage-1 tree: `bit-exact frozen through all 100 updates`",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This pass authorizes only a separate 124-cell-per-checkpoint",
                "support/context-gate preregistration. It is not robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
