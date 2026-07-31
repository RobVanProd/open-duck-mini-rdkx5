#!/usr/bin/env python3
"""Strictly import the Winner-v15 pitch-margin CPU contract artifact."""

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
CONTRACT = ANALYSIS / "winner_v15_pitch_margin_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v15_pitch_margin_objective_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
RUNNER = ROOT / "tools/run_winner_v15_pitch_margin_cpu_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v15-pitch-margin-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v15_pitch_margin_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V15_PITCH_MARGIN_CPU_RESULT_20260721.md"
RAW_RESULT = "winner-v15-pitch-margin-cpu-result.json"
RAW_RECEIPT = "winner-v15-pitch-margin-cpu-result.sha256"
WORK_PREFIX = "winner-v15-pitch-margin-cpu-work"
RAW_GRAPH = f"{WORK_PREFIX}/winner_v15_pitch_margin_update_001.onnx"
RAW_SNAPSHOT = f"{WORK_PREFIX}/winner_v15_pitch_margin_update_001.npz"
CHECKS = {
    "action_boundary_exact",
    "all_stage2_gradients_nonzero",
    "all_stage2_leaves_changed",
    "all_values_finite",
    "default_off_batch_episode_observation_bit_exact",
    "default_off_reward_bit_exact",
    "enabled_changes_only_returns_and_advantages",
    "enabled_penalty_formula_bit_exact",
    "enabled_penalty_nonzero",
    "enabled_reward_and_penalty_bounded",
    "enabled_reward_formula_bit_exact",
    "enabled_transition_action_episode_observation_bit_exact",
    "exact_80_episode_population",
    "one_adam_update_exact",
    "onnx_abi_exact",
    "onnx_jax_chain_at_most_1e_7",
    "onnx_previous_action_chain_exact",
    "onnx_training_only_tensors_absent",
    "snapshot_readback_exact",
    "source_stage1_snapshot_exact",
    "stage1_tree_bit_exact_frozen",
    "stage2_masks_exact",
}
STAGE2_LEAVES = {
    "action_bias",
    "action_weight",
    "training_only_log_std",
    "training_only_value_bias",
    "training_only_value_weight",
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
    return {RAW_RESULT, RAW_RECEIPT, RAW_GRAPH, RAW_SNAPSHOT}


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = artifact_members()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v15 pitch-margin CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 10_000_000:
            raise ValueError("Winner-v15 pitch-margin CPU artifact exceeds size ceiling")
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
                raise ValueError("Winner-v15 pitch-margin CPU artifact has unsafe member")
        return {name: archive.read(name) for name in names}


def finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def validate_result(value: Mapping[str, Any]) -> None:
    if value.get("schema_version") != "winner_v15.pitch_margin_cpu_result.v1":
        raise ValueError("Winner-v15 pitch-margin CPU result schema changed")
    if (
        value.get("status") != "PASS_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_PITCH_MARGIN_SUPPORT_TRAINING_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
    ):
        raise ValueError("Winner-v15 pitch-margin CPU contract did not pass")
    checks = value.get("checks")
    if (
        not isinstance(checks, dict)
        or set(checks) != CHECKS
        or not all(item is True for item in checks.values())
    ):
        raise ValueError("Winner-v15 pitch-margin CPU checks changed")
    if value.get("execution") != {
        "stage2_optimizer_updates": 1,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v15 pitch-margin CPU execution boundary changed")
    if value.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v15 pitch-margin CPU source identities changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": "a separate pitch-margin support-training preregistration",
    }:
        raise ValueError("Winner-v15 pitch-margin CPU authority changed")
    proof = value.get("proof")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = contract["source_artifact"]
    if (
        not isinstance(proof, dict)
        or proof.get("source_snapshot_sha256") != source["snapshot_sha256"]
        or proof.get("source_snapshot_bytes") != source["snapshot_bytes"]
        or proof.get("sampled_count") != 18251
        or proof.get("valid_transition_count") != 18243
        or not finite(proof.get("loss"))
    ):
        raise ValueError("Winner-v15 pitch-margin restored proof changed")
    reward = proof.get("reward", {})
    if (
        reward.get("valid_transition_count") != 18243
        or reward.get("nonzero_penalty_count") != 5911
        or reward.get("settled_bonus_count") != 36
        or reward.get("reward_formula_bit_exact") is not True
        or reward.get("penalty_formula_bit_exact") is not True
        or reward.get("only_zero_or_settled_bonus") is not True
        or reward.get("all_rewards_nonnegative") is not True
        or reward.get("all_penalties_in_unit_interval") is not True
        or not all(
            finite(reward.get(name))
            for name in (
                "reward_min",
                "reward_max_without_terminal_bonus",
                "penalty_min",
                "penalty_max",
            )
        )
        or not 0.0 <= reward["reward_min"] <= 1.0
        or reward["reward_max_without_terminal_bonus"] != 1.0
        or not 0.0 <= reward["penalty_min"] <= reward["penalty_max"] <= 1.0
    ):
        raise ValueError("Winner-v15 pitch-margin reward proof changed")
    for name in ("gradient_max_abs", "stage2_leaf_max_abs_delta"):
        rows = proof.get(name)
        if (
            not isinstance(rows, dict)
            or set(rows) != STAGE2_LEAVES
            or not all(finite(item) and item > 0.0 for item in rows.values())
        ):
            raise ValueError(f"Winner-v15 pitch-margin {name} changed")
    boundary = proof.get("action_boundary", {})
    if (
        boundary.get("attempted_samples") != proof.get("sampled_count")
        or boundary.get("numpy_equals_jax_bit_exact") is not True
        or boundary.get("realized_equals_numpy_bit_exact") is not True
        or boundary.get("maximum_numpy_jax_error") != 0.0
        or boundary.get("maximum_realized_numpy_error") != 0.0
    ):
        raise ValueError("Winner-v15 pitch-margin action boundary changed")
    graph = proof.get("graph_contract", {})
    if (
        graph.get("abi_exact") is not True
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
        or graph["jax_onnx_max_abs_error"] > 1.0e-7
        or HEX64.fullmatch(str(graph.get("sha256"))) is None
        or graph.get("bytes", 0) <= 0
    ):
        raise ValueError("Winner-v15 pitch-margin graph proof changed")
    snapshot = proof.get("snapshot", {})
    if (
        snapshot.get("bit_exact_readback") is not True
        or HEX64.fullmatch(str(snapshot.get("sha256"))) is None
        or snapshot.get("bytes", 0) <= 0
    ):
        raise ValueError("Winner-v15 pitch-margin snapshot proof changed")


def verify_payloads(members: Mapping[str, bytes], value: Mapping[str, Any]) -> None:
    graph = value["proof"]["graph_contract"]
    snapshot = value["proof"]["snapshot"]
    if (
        sha256_bytes(members[RAW_GRAPH]) != graph["sha256"]
        or len(members[RAW_GRAPH]) != graph["bytes"]
    ):
        raise ValueError("Winner-v15 pitch-margin graph payload changed")
    if (
        sha256_bytes(members[RAW_SNAPSHOT]) != snapshot["sha256"]
        or len(members[RAW_SNAPSHOT]) != snapshot["bytes"]
    ):
        raise ValueError("Winner-v15 pitch-margin snapshot payload changed")


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
        raise FileExistsError("Winner-v15 pitch-margin CPU result is already imported")
    zip_sha = sha256(args.artifact_zip)
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != f"winner-v15-pitch-margin-cpu-{args.run_id}"
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v15 pitch-margin CPU repository attribution changed")
    members = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(members[RAW_RESULT])
    if members[RAW_RECEIPT] != f"{raw_sha}  /tmp/{RAW_RESULT}\n".encode():
        raise ValueError("Winner-v15 pitch-margin result receipt changed")
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
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    proof = payload["proof"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v15 pitch-margin CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Sampled / valid transitions: `{proof['sampled_count']} / {proof['valid_transition_count']}`",
                f"- Nonzero pitch penalties / settled bonuses: `{proof['reward']['nonzero_penalty_count']} / {proof['reward']['settled_bonus_count']}`",
                f"- One-update graph / snapshot SHA-256: `{proof['graph_contract']['sha256']} / {proof['snapshot']['sha256']}`",
                "- Default-off / reward-only transition identity: `bit exact / bit exact`",
                "- Stage-1 tree: `bit exact frozen`",
                "- Stage-2 leaves: `all nonzero-gradient and all changed`",
                "- Formal support / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This pass authorizes only a separate 100-update pitch-margin support",
                "training preregistration. It does not authorize training execution,",
                "formal support evaluation, locomotion, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
