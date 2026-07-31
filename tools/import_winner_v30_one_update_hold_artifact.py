#!/usr/bin/env python3
"""Preserve and strictly import the sole held Winner-v30 first-attempt artifact."""

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
CORRECTION = ANALYSIS / "winner_v30_one_update_hold_import_correction.json"
CONTRACT = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
OUTPUT_JSON = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_HOLD_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v30-prefix-right-pitch-anchor-one-update-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v30-prefix-right-pitch-anchor-one-update-cpu-result.sha256"
SNAPSHOT_MEMBER = "winner-v30-prefix-anchor-work/winner_v30_prefix_right_pitch_anchor_update_201.npz"
GRAPH_MEMBER = "winner-v30-prefix-anchor-work/winner_v30_prefix_right_pitch_anchor_update_201.onnx"
EXPECTED_FAILED_CHECKS = [
    "exact_v29_anchor_loss_gradient_and_scale_reproduced",
    "exact_v29_update_200_batch_reproduced",
]
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


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
        items = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in items]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError(f"Winner-v30 hold artifact inventory changed: {names}")
        for item in items:
            member = PurePosixPath(item.filename)
            if (
                member.is_absolute()
                or ".." in member.parts
                or item.is_dir()
                or item.file_size > 32 * 1024 * 1024
                or item.compress_size > 32 * 1024 * 1024
            ):
                raise ValueError("Winner-v30 hold artifact contains unsafe member")
        return {name: archive.read(name) for name in expected}


def validate_raw(
    value: Mapping[str, Any], *, snapshot_bytes: bytes, graph_bytes: bytes
) -> None:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    v29 = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    checks = value.get("checks")
    if (
        value.get("schema_version")
        != "winner_v30.prefix_right_pitch_anchor_one_update_cpu_result.v1"
        or value.get("status")
        != "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or value.get("decision") != "DO_NOT_TRAIN_PREFIX_RIGHT_PITCH_ANCHOR_OBJECTIVE"
        or value.get("failed_checks") != EXPECTED_FAILED_CHECKS
        or not isinstance(checks, Mapping)
        or sorted(name for name, passed in checks.items() if not passed)
        != EXPECTED_FAILED_CHECKS
        or not all(
            passed is True
            for name, passed in checks.items()
            if name not in EXPECTED_FAILED_CHECKS
        )
        or value.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("objective") != contract["objective"]
        or value.get("sources") != contract["sources"]
        or value.get("source_manifest_sha256") != contract["source_manifest_sha256"]
    ):
        raise ValueError("Winner-v30 raw HOLD result changed")
    rollout = value.get("rollout", {})
    if (
        rollout.get("update_index") != 200
        or rollout.get("episode_slots") != 80
        or rollout.get("roll_pitch_failure_count")
        != v29["rollout_evidence"]["roll_pitch_failure_count"]
        or rollout.get("selected_anchor_elements") != 384
        or rollout.get("exact_v29_batch_reproduced") is not False
        or rollout.get("exact_v29_objective_reproduced") is not False
        or int(rollout.get("sampled_count", 0)) <= 0
        or int(rollout.get("valid_transition_count", 0)) <= 0
        or int(rollout.get("stored_successor_transition_count", 0)) <= 0
        or HEX64.fullmatch(str(rollout.get("episode_receipts_sha256"))) is None
    ):
        raise ValueError("Winner-v30 raw HOLD rollout changed")
    optimization = value.get("optimization", {})
    before = float(optimization.get("anchor_loss_before", math.nan))
    after = float(optimization.get("anchor_loss_after", math.nan))
    if (
        optimization.get("optimizer_count_before") != 200
        or optimization.get("optimizer_count_after") != 201
        or float(optimization.get("anchor_scale", math.nan)) != 197.3112030029297
        or not math.isfinite(before)
        or not math.isfinite(after)
        or not after < before
        or optimization.get("source_state_unchanged_before_update") is not True
        or optimization.get("snapshot_readback_exact") is not True
        or not all(
            float(item) > 0.0
            for item in optimization.get("combined_gradient_max_abs", {}).values()
        )
        or not all(
            float(item) > 0.0
            for item in optimization.get("leaf_max_abs_delta", {}).values()
        )
        or len(optimization.get("combined_gradient_max_abs", {})) != 12
        or len(optimization.get("leaf_max_abs_delta", {})) != 12
    ):
        raise ValueError("Winner-v30 raw HOLD optimizer evidence changed")
    snapshot = value.get("snapshot", {})
    graph = value.get("graph", {})
    if (
        snapshot.get("completed_updates") != 201
        or snapshot.get("bytes") != len(snapshot_bytes)
        or snapshot.get("sha256") != sha256_bytes(snapshot_bytes)
        or graph.get("bytes") != len(graph_bytes)
        or graph.get("sha256") != sha256_bytes(graph_bytes)
        or graph.get("contract", {}).get("abi_exact") is not True
        or graph.get("contract", {}).get("training_only_tensors_absent") is not True
        or graph.get("contract", {}).get("jax_onnx_at_most_1e_7") is not True
        or graph.get("contract", {}).get("previous_action_out_equals_action_bit_exact")
        is not True
    ):
        raise ValueError("Winner-v30 raw HOLD artifacts changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "training_executed": False,
        "formal_support_gate_executed": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate frozen prefix right-pitch anchor training preregistration"
        ),
    }:
        raise ValueError("Winner-v30 raw HOLD authority changed")
    if correction.get("expected_raw") != {
        "status": value["status"],
        "decision": value["decision"],
        "failed_checks": EXPECTED_FAILED_CHECKS,
        "optimizer_count_before": 200,
        "optimizer_count_after": 201,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v30 hold correction changed")


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
        raise FileExistsError("Winner-v30 HOLD result is already imported")
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    zip_sha = sha256(args.artifact_zip)
    expected = correction["repository_attribution"]
    if (
        args.run_id != expected["github_run_id"]
        or args.run_attempt != expected["github_run_attempt"]
        or args.run_head_sha != expected["github_run_head_sha"]
        or args.artifact_id != expected["github_artifact_id"]
        or args.artifact_name != expected["github_artifact_name"]
        or args.artifact_digest != expected["github_artifact_digest"]
        or zip_sha != expected["artifact_zip_sha256"]
        or args.artifact_zip.stat().st_size != expected["artifact_zip_bytes"]
        or HEX40.fullmatch(args.run_head_sha) is None
        or HEX64.fullmatch(zip_sha) is None
    ):
        raise ValueError("Winner-v30 HOLD repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_bytes = members[RAW_RESULT_NAME]
    receipt_bytes = members[RAW_RECEIPT_NAME]
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v30 HOLD raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_raw(
        raw, snapshot_bytes=members[SNAPSHOT_MEMBER], graph_bytes=members[GRAPH_MEMBER]
    )
    result = dict(raw)
    result["repository_attribution"] = {
        **expected,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "snapshot_member": SNAPSHOT_MEMBER,
        "snapshot_sha256": sha256_bytes(members[SNAPSHOT_MEMBER]),
        "graph_member": GRAPH_MEMBER,
        "graph_sha256": sha256_bytes(members[GRAPH_MEMBER]),
        "correction_lf_sha256": lf_sha256(CORRECTION),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v30 prefix right-pitch anchor one-update HOLD result",
                "",
                f"- Status: `{result['status']}`",
                f"- Failed checks: `{', '.join(result['failed_checks'])}`",
                "- Optimizer count: `200 -> 201`",
                f"- Anchor loss: `{result['optimization']['anchor_loss_before']} -> {result['optimization']['anchor_loss_after']}`",
                f"- Snapshot SHA-256: `{result['snapshot']['sha256']}`",
                f"- ONNX SHA-256: `{result['graph']['sha256']}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "",
                "The first-attempt HOLD artifact is preserved unchanged. It authorizes no rerun,",
                "training, checkpoint selection, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
