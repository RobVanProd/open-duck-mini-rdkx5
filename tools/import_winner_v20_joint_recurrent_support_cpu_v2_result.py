#!/usr/bin/env python3
"""Strictly import the passing Winner-v20 two-update CPU proof."""

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
CPU_HOLD = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_hold_attribution.json"
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_cpu_contract.py"
WORKFLOW = (
    ROOT / ".github/workflows/winner-v20-joint-recurrent-support-cpu-contract.yml"
)
OUTPUT_JSON = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_v2_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_V2_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v20-joint-recurrent-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v20-joint-recurrent-cpu-result.sha256"
SNAPSHOT_NAME = (
    "winner-v20-joint-recurrent-cpu-work/"
    "winner_v20_joint_recurrent_update_002.npz"
)
GRAPH_NAME = (
    "winner-v20-joint-recurrent-cpu-work/"
    "winner_v20_joint_recurrent_update_002.onnx"
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
            raise ValueError("Winner-v20 v2 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v20 v2 artifact exceeds size ceiling")
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
                raise ValueError("Winner-v20 v2 artifact has unsafe member")
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
        run_id != 29853236226
        or run_attempt != 1
        or run_head_sha != "489cd0be67f9599389aa1625d1b8d1e1617f7112"
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id != 8504369891
        or artifact_name != f"winner-v20-joint-recurrent-cpu-{run_id}"
        or HEX64_RE.fullmatch(artifact_zip_sha256) is None
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v20 v2 workflow attribution changed")
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
        "rollouts",
        "schema_version",
        "snapshot",
        "source_snapshot",
        "sources",
        "status",
    }
    if (
        set(result) != expected_fields
        or result.get("schema_version")
        != "winner_v20.joint_recurrent_support_cpu_result.v2"
        or result.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or result.get("decision")
        != "AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY"
        or result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v20 v2 decision changed")
    checks = result["checks"]
    expected_checks = {
        "all_values_finite",
        "auxiliary_predictor_bit_exact_frozen",
        "both_action_boundaries_exact",
        "both_episode_receipts_exact",
        "both_observation_captures_exact",
        "both_reward_formulas_exact_and_nonzero",
        "both_sampled_hidden_replays_at_most_1e_6",
        "both_winner_v15_rollouts_bit_exact",
        "cumulative_all_joint_leaves_changed",
        "exact_two_80_episode_populations",
        "onnx_abi_exact",
        "onnx_jax_chain_at_most_1e_7",
        "onnx_previous_action_chain_exact",
        "onnx_training_only_tensors_absent",
        "snapshot_readback_exact",
        "source_stage1_snapshot_exact",
        "two_adam_updates_exact",
        "update_1_other_deltas_nonzero",
        "update_1_other_gradients_nonzero",
        "update_1_recurrent_deltas_exact_zero",
        "update_1_recurrent_gradients_exact_zero",
        "update_2_all_joint_gradients_nonzero",
        "update_2_all_joint_leaves_changed",
    }
    if set(checks) != expected_checks or not all(checks.values()):
        raise ValueError("Winner-v20 v2 checks changed")
    if (
        result["execution"]
        != {
            "optimizer_updates": 2,
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
        raise ValueError("Winner-v20 v2 execution or authority changed")
    if result["sources"] != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "cpu_hold_attribution_lf_sha256": lf_sha256(CPU_HOLD),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v20 v2 sources changed")
    rollouts = result["rollouts"]
    if (
        [row.get("update") for row in rollouts] != [1, 2]
        or [row.get("sampled_hidden_replay_max_abs_error") for row in rollouts]
        != [2.980232238769531e-07, 3.5762786865234375e-07]
        or any(
            not row["winner_v15_transition_exact"]
            or not row["observation_capture_exact"]
            or not row["action_boundary_exact"]
            for row in rollouts
        )
    ):
        raise ValueError("Winner-v20 v2 rollout evidence changed")
    updates = result["optimization"]["updates"]
    if [row.get("update") for row in updates] != [1, 2]:
        raise ValueError("Winner-v20 v2 update set changed")
    recurrent = {"obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias"}
    for name in recurrent:
        if (
            updates[0]["gradient_max_abs"][name] != 0.0
            or updates[0]["leaf_max_abs_delta"][name] != 0.0
            or updates[1]["gradient_max_abs"][name] <= 0.0
            or updates[1]["leaf_max_abs_delta"][name] <= 0.0
        ):
            raise ValueError("Winner-v20 v2 recurrent opening changed")
    if not all(
        math.isfinite(value) and value > 0.0
        for value in result["optimization"]["cumulative_leaf_max_abs_delta"].values()
    ):
        raise ValueError("Winner-v20 v2 cumulative update changed")
    if (
        result["graph"]["sha256"]
        != "2149960ff1e3e82fb9a5dfce4ee76597aad4a9493808c54b9d6172e46f6f1c6b"
        or result["graph"]["bytes"] != 54896
        or result["snapshot"]["sha256"]
        != "45f73dc842e77f67edb05f7e8e4d1613b8238a924ab48aefffe9251f456c8bf4"
        or result["snapshot"]["bytes"] != 162570
    ):
        raise ValueError("Winner-v20 v2 emitted artifact changed")


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
        raise FileExistsError("Winner-v20 v2 result is already imported")
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
        raise ValueError("Winner-v20 v2 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    if (
        sha256_bytes(members[GRAPH_NAME]) != result["graph"]["sha256"]
        or len(members[GRAPH_NAME]) != result["graph"]["bytes"]
        or sha256_bytes(members[SNAPSHOT_NAME]) != result["snapshot"]["sha256"]
        or len(members[SNAPSHOT_NAME]) != result["snapshot"]["bytes"]
    ):
        raise ValueError("Winner-v20 v2 embedded artifact receipt changed")
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
                "# Winner-v20 joint recurrent CPU v2 result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Raw result SHA-256: `{raw_sha}`",
                "- Sampled replay error update 1 / 2: `2.98e-7 / 3.58e-7`",
                "- Update-2 recurrent gradients/deltas: all nonzero",
                "- Formal support / robot: `0 / 0`",
                "",
                "The existing recurrent core is trainable once the exact-zero action head",
                "opens on update 1. Every frozen two-update mechanics check passes. This",
                "authorizes only a separate 100-update training preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
