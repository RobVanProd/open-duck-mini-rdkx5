#!/usr/bin/env python3
"""Strictly import the hosted Winner-v20 one-update CPU HOLD result."""

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
CONTRACT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_attribution.json"
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_cpu_contract.py"
WORKFLOW = (
    ROOT / ".github/workflows/winner-v20-joint-recurrent-support-cpu-contract.yml"
)
OUTPUT_JSON = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v20-joint-recurrent-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v20-joint-recurrent-cpu-result.sha256"
SNAPSHOT_NAME = (
    "winner-v20-joint-recurrent-cpu-work/"
    "winner_v20_joint_recurrent_update_001.npz"
)
GRAPH_NAME = (
    "winner-v20-joint-recurrent-cpu-work/"
    "winner_v20_joint_recurrent_update_001.onnx"
)
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")


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


def read_result_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME, SNAPSHOT_NAME, GRAPH_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v20 CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v20 CPU artifact exceeds size ceiling")
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
                raise ValueError("Winner-v20 CPU artifact has unsafe member")
        return {name: archive.read(name) for name in expected}


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
    if (
        run_id != 29852380511
        or run_attempt != 1
        or run_head_sha != "cc739b6aeefb60b0e74a9c2715d6f14fcabe31c6"
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id != 8503945380
        or artifact_name != f"winner-v20-joint-recurrent-cpu-{run_id}"
        or HEX64_RE.fullmatch(artifact_zip_sha256) is None
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v20 CPU workflow attribution changed")
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
    expected_fields = {
        "authority",
        "checks",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "graph",
        "optimization",
        "rollout",
        "schema_version",
        "snapshot",
        "source_snapshot",
        "sources",
        "status",
    }
    expected_failed = [
        "all_joint_gradients_nonzero",
        "all_joint_leaves_changed",
        "source_hidden_replay_at_most_1e_6",
    ]
    if (
        set(result) != expected_fields
        or result.get("schema_version")
        != "winner_v20.joint_recurrent_support_cpu_result.v1"
        or result.get("status")
        != "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or result.get("decision") != "DO_NOT_TRAIN_JOINT_RECURRENT_SUPPORT_ARM"
        or result.get("failed_checks") != expected_failed
    ):
        raise ValueError("Winner-v20 CPU decision changed")
    expected_checks = {
        "action_boundary_exact",
        "all_joint_gradients_nonzero",
        "all_joint_leaves_changed",
        "all_values_finite",
        "auxiliary_predictor_bit_exact_frozen",
        "complete_observation_capture_exact",
        "episode_receipts_exact",
        "exact_80_episode_population",
        "one_adam_update_exact",
        "onnx_abi_exact",
        "onnx_jax_chain_at_most_1e_7",
        "onnx_previous_action_chain_exact",
        "onnx_training_only_tensors_absent",
        "reward_formula_bit_exact",
        "reward_signal_nonzero",
        "snapshot_readback_exact",
        "source_hidden_replay_at_most_1e_6",
        "source_stage1_snapshot_exact",
        "winner_v15_rollout_reward_action_masks_bit_exact",
    }
    checks = result["checks"]
    if set(checks) != expected_checks or sorted(
        name for name, passed in checks.items() if not passed
    ) != expected_failed:
        raise ValueError("Winner-v20 CPU check pattern changed")
    if (
        result["execution"]
        != {
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or result["authority"]
        != {
            "robot_clearance": False,
            "joint_recurrent_training_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen 100-update joint-recurrent training preregistration"
            ),
        }
    ):
        raise ValueError("Winner-v20 execution or authority changed")
    if result["sources"] != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v20 CPU sources changed")
    recurrent = {"obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias"}
    gradients = result["optimization"]["gradient_max_abs"]
    deltas = result["optimization"]["leaf_max_abs_delta"]
    if (
        set(gradients) != set(result["optimization"]["trainable_leaves"])
        or set(deltas) != set(gradients)
        or any(gradients[name] != 0.0 or deltas[name] != 0.0 for name in recurrent)
        or any(
            value <= 0.0
            for name, value in gradients.items()
            if name not in recurrent
        )
        or any(
            value <= 0.0 for name, value in deltas.items() if name not in recurrent
        )
        or not math.isclose(
            result["rollout"]["source_hidden_replay_max_abs_error"],
            0.34119200706481934,
            rel_tol=0.0,
            abs_tol=0.0,
        )
    ):
        raise ValueError("Winner-v20 zero-gradient evidence changed")
    if (
        result["graph"]["sha256"]
        != "b375ca14dc9c5417f6c006e07efa30ebdaff3d5d3fe7a6d0d6e8d5089139ab5f"
        or result["graph"]["bytes"] != 54896
        or result["snapshot"]["sha256"]
        != "7371e93671d52982bdbb913a32c9070226b3387403654e013cf48a0591f427f8"
        or result["snapshot"]["bytes"] != 78649
    ):
        raise ValueError("Winner-v20 emitted artifact changed")


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
        raise FileExistsError("Winner-v20 CPU result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha,
        artifact_id=args.artifact_id,
        artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    members = read_result_artifact(args.artifact_zip)
    raw_bytes = members[RAW_RESULT_NAME]
    receipt_bytes = members[RAW_RECEIPT_NAME]
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v20 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    if (
        sha256_bytes(members[GRAPH_NAME]) != result["graph"]["sha256"]
        or len(members[GRAPH_NAME]) != result["graph"]["bytes"]
        or sha256_bytes(members[SNAPSHOT_NAME]) != result["snapshot"]["sha256"]
        or len(members[SNAPSHOT_NAME]) != result["snapshot"]["bytes"]
    ):
        raise ValueError("Winner-v20 embedded artifact receipt changed")
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
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v20 joint recurrent CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Recurrent gradient / delta at update 1: exact zero on all four leaves",
                "- Action-head gradient / delta at update 1: nonzero on both leaves",
                "- Formal support / robot: `0 / 0`",
                "",
                "The shared source intentionally has an exact-zero action head, so the",
                "first joint gradient cannot reach the recurrent core. The one-update",
                "contract therefore holds and grants no training authority.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
