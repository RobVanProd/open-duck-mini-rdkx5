#!/usr/bin/env python3
"""Strictly import the sole Winner-v30 one-update CPU-proof artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
RUNNER = ROOT / "tools/run_winner_v30_prefix_right_pitch_anchor_one_update_cpu_proof.py"
WORKFLOW = ROOT / ".github/workflows/winner-v30-prefix-right-pitch-anchor-one-update-cpu-proof.yml"
OUTPUT_JSON = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v30-prefix-right-pitch-anchor-one-update-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v30-prefix-right-pitch-anchor-one-update-cpu-result.sha256"
SNAPSHOT_MEMBER = "winner-v30-prefix-anchor-work/winner_v30_prefix_right_pitch_anchor_update_201.npz"
GRAPH_MEMBER = "winner-v30-prefix-anchor-work/winner_v30_prefix_right_pitch_anchor_update_201.onnx"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_MEMBER_BYTES = 32 * 1024 * 1024


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


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME, SNAPSHOT_MEMBER, GRAPH_MEMBER}
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in members]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError(f"Winner-v30 artifact inventory changed: {names}")
        for item in members:
            member = PurePosixPath(item.filename)
            if (
                member.is_absolute()
                or ".." in member.parts
                or item.is_dir()
                or item.file_size > MAX_MEMBER_BYTES
                or item.compress_size > MAX_MEMBER_BYTES
            ):
                raise ValueError("Winner-v30 artifact contains unsafe member")
        return {name: archive.read(name) for name in expected}


def validate_result(
    value: Mapping[str, Any], *, snapshot_bytes: bytes | None = None, graph_bytes: bytes | None = None
) -> None:
    fields = {
        "authority",
        "checks",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "graph",
        "objective",
        "optimization",
        "rollout",
        "schema_version",
        "snapshot",
        "source_identity",
        "source_manifest_sha256",
        "sources",
        "status",
    }
    if set(value) not in (fields, fields | {"repository_attribution"}):
        raise ValueError("Winner-v30 result field inventory changed")
    if (
        value.get("schema_version")
        != "winner_v30.prefix_right_pitch_anchor_one_update_cpu_result.v1"
        or value.get("status")
        != "PASS_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or value.get("decision")
        != "AUTHORIZE_SEPARATE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
        or not isinstance(value.get("checks"), Mapping)
        or not value["checks"]
        or not all(item is True for item in value["checks"].values())
    ):
        raise ValueError("Winner-v30 result did not pass the frozen contract")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    zero = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    if (
        value.get("objective") != prereg["objective"]
        or value.get("sources") != prereg["sources"]
        or value.get("source_manifest_sha256") != prereg["source_manifest_sha256"]
        or value.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v30 source or execution boundary changed")
    expected_identity = {
        "teacher_snapshot": prereg["artifact_inputs"]["winner_v22_training"][
            "source_snapshot"
        ],
        "teacher_graph": prereg["artifact_inputs"]["winner_v22_training"][
            "source_graph"
        ],
        "candidate_snapshot": prereg["artifact_inputs"]["winner_v24_training"][
            "final"
        ]["snapshot"],
        "candidate_graph": prereg["artifact_inputs"]["winner_v24_training"][
            "final"
        ]["graph"],
    }
    if value.get("source_identity") != expected_identity:
        raise ValueError("Winner-v30 source identity changed")
    rollout = value.get("rollout", {})
    if (
        rollout.get("update_index") != 200
        or rollout.get("episode_slots") != 80
        or rollout.get("roll_pitch_failure_count")
        != zero["rollout_evidence"]["roll_pitch_failure_count"]
        or rollout.get("selected_anchor_elements") != 384
        or rollout.get("exact_v29_batch_reproduced") is not True
        or rollout.get("exact_v29_objective_reproduced") is not True
        or HEX64.fullmatch(str(rollout.get("episode_receipts_sha256"))) is None
        or int(rollout.get("sampled_count", 0)) <= 0
        or int(rollout.get("valid_transition_count", 0)) <= 0
        or int(rollout.get("stored_successor_transition_count", 0)) <= 0
    ):
        raise ValueError("Winner-v30 rollout changed")
    optimization = value.get("optimization", {})
    before = float(optimization.get("anchor_loss_before", math.nan))
    after = float(optimization.get("anchor_loss_after", math.nan))
    if (
        optimization.get("optimizer_count_before") != 200
        or optimization.get("optimizer_count_after") != 201
        or float(optimization.get("anchor_scale", math.nan)) != 197.3112030029297
        or before != zero["objective_evidence"]["raw_anchor_loss"]
        or not math.isfinite(after)
        or not after < before
        or float(optimization.get("anchor_loss_delta", math.nan)) != after - before
        or set(optimization.get("combined_gradient_max_abs", {}))
        != set(optimization.get("trainable_leaves", []))
        or set(optimization.get("leaf_max_abs_delta", {}))
        != set(optimization.get("trainable_leaves", []))
        or not all(float(item) > 0.0 for item in optimization["combined_gradient_max_abs"].values())
        or not all(float(item) > 0.0 for item in optimization["leaf_max_abs_delta"].values())
        or optimization.get("source_state_unchanged_before_update") is not True
        or optimization.get("snapshot_readback_exact") is not True
    ):
        raise ValueError("Winner-v30 optimization changed")
    snapshot = value.get("snapshot", {})
    graph = value.get("graph", {})
    if (
        snapshot.get("completed_updates") != 201
        or HEX64.fullmatch(str(snapshot.get("sha256"))) is None
        or int(snapshot.get("bytes", 0)) <= 0
        or HEX64.fullmatch(str(graph.get("sha256"))) is None
        or int(graph.get("bytes", 0)) <= 0
        or graph.get("contract", {}).get("abi_exact") is not True
        or graph.get("contract", {}).get("training_only_tensors_absent") is not True
        or graph.get("contract", {}).get("jax_onnx_at_most_1e_7") is not True
        or graph.get("contract", {}).get("previous_action_out_equals_action_bit_exact")
        is not True
    ):
        raise ValueError("Winner-v30 snapshot or graph receipt changed")
    if snapshot_bytes is not None and (
        len(snapshot_bytes) != snapshot["bytes"]
        or sha256_bytes(snapshot_bytes) != snapshot["sha256"]
    ):
        raise ValueError("Winner-v30 snapshot bytes changed")
    if graph_bytes is not None and (
        len(graph_bytes) != graph["bytes"] or sha256_bytes(graph_bytes) != graph["sha256"]
    ):
        raise ValueError("Winner-v30 graph bytes changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "training_executed": False,
        "formal_support_gate_executed": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate frozen prefix right-pitch anchor training preregistration"
        ),
    }:
        raise ValueError("Winner-v30 authority changed")
    if "repository_attribution" in value:
        item = value["repository_attribution"]
        if (
            not isinstance(item, Mapping)
            or item.get("repository") != EXPECTED_REPOSITORY
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
            raise ValueError("Winner-v30 repository attribution changed")


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
        raise FileExistsError("Winner-v30 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    expected_name = f"winner-v30-prefix-right-pitch-anchor-one-update-{args.run_id}"
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != expected_name
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v30 repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_bytes = members[RAW_RESULT_NAME]
    receipt_bytes = members[RAW_RECEIPT_NAME]
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v30 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(
        raw, snapshot_bytes=members[SNAPSHOT_MEMBER], graph_bytes=members[GRAPH_MEMBER]
    )
    result = dict(raw)
    result["repository_attribution"] = {
        "repository": EXPECTED_REPOSITORY,
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
        "snapshot_member": SNAPSHOT_MEMBER,
        "snapshot_sha256": sha256_bytes(members[SNAPSHOT_MEMBER]),
        "graph_member": GRAPH_MEMBER,
        "graph_sha256": sha256_bytes(members[GRAPH_MEMBER]),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(
        result, snapshot_bytes=members[SNAPSHOT_MEMBER], graph_bytes=members[GRAPH_MEMBER]
    )
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v30 prefix right-pitch anchor one-update CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- Optimizer count: `200 -> 201`",
                f"- Anchor loss: `{before} -> {after}`",
                f"- Snapshot SHA-256: `{result['snapshot']['sha256']}`",
                f"- ONNX SHA-256: `{result['graph']['sha256']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "A pass authorizes only a separately preregistered bounded training continuation.",
                "It does not authorize training by itself, checkpoint selection, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"SNAPSHOT_SHA256={result['snapshot']['sha256']}")
    print(f"ONNX_SHA256={result['graph']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
