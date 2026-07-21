#!/usr/bin/env python3
"""Safely import one Winner-v21 explicit-gradient two-update proof."""

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
CONTRACT = ANALYSIS / "winner_v21_predictor_preserving_two_update_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v21_gradient_composition_attribution.json"
RUNNER = ROOT / "tools/run_winner_v21_predictor_preserving_two_update_cpu_proof.py"
WORKFLOW = ROOT / ".github/workflows/winner-v21-predictor-preserving-two-update-cpu-proof.yml"
OUTPUT_JSON = ANALYSIS / "winner_v21_predictor_preserving_two_update_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v21-predictor-preserving-two-update-result.json"
RAW_RECEIPT_NAME = "winner-v21-predictor-preserving-two-update-result.sha256"
SNAPSHOT_NAME = (
    "winner-v21-predictor-preserving-two-update-work/"
    "winner_v21_predictor_preserving_update_002.npz"
)
GRAPH_NAME = (
    "winner-v21-predictor-preserving-two-update-work/"
    "winner_v21_predictor_preserving_update_002.onnx"
)
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
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
CHECK_NAMES = {
    "source_stage1_snapshot_exact",
    "both_exact_80_episode_populations",
    "both_winner_v15_rollouts_bit_exact",
    "both_episode_receipts_exact",
    "both_action_boundaries_exact",
    "both_reward_formulas_exact_and_nonzero",
    "both_sampled_hidden_replays_at_most_1e_6",
    "both_stored_successor_masks_exact",
    "frozen_predictor_scale_exact",
    "both_updates_all_12_gradients_and_deltas_nonzero",
    "cumulative_all_12_leaves_changed",
    "two_adam_updates_exact",
    "snapshot_readback_exact",
    "onnx_abi_exact",
    "onnx_training_only_tensors_absent",
    "onnx_jax_chain_at_most_1e_7",
    "onnx_previous_action_chain_exact",
    "formal_support_locomotion_robot_zero",
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


def read_result_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME, SNAPSHOT_NAME, GRAPH_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v21 two-update artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v21 two-update artifact exceeds size ceiling")
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
                raise ValueError("Winner-v21 two-update artifact has unsafe member")
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
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v21-predictor-preserving-two-update-{run_id}"
        or HEX64_RE.fullmatch(artifact_zip_sha256) is None
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v21 two-update workflow attribution changed")
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
        "schema_version",
        "status",
        "decision",
        "checks",
        "failed_checks",
        "environment",
        "source_snapshot",
        "predictor_scale",
        "rollouts",
        "optimization",
        "graph",
        "snapshot",
        "execution",
        "sources",
        "authority",
    }
    if set(result) not in {expected_fields, expected_fields | {"repository_attribution"}}:
        raise ValueError("Winner-v21 two-update result schema changed")
    if result.get("schema_version") != (
        "winner_v21.predictor_preserving_two_update_cpu_result.v1"
    ):
        raise ValueError("Winner-v21 two-update schema changed")
    checks = result.get("checks")
    if (
        not isinstance(checks, Mapping)
        or set(checks) != CHECK_NAMES
        or not all(type(value) is bool for value in checks.values())
    ):
        raise ValueError("Winner-v21 two-update checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_PROOF"
            if passed
            else "HOLD_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_PROOF"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_SEPARATE_100_UPDATE_PREDICTOR_PRESERVING_TRAINING_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_TRAIN_WINNER_V21"
        )
    ):
        raise ValueError("Winner-v21 two-update decision changed")
    if result.get("source_snapshot") != {
        "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
        "bytes": 189027,
    } or result.get("predictor_scale") != 8.393629541414427e-11:
        raise ValueError("Winner-v21 two-update source or scale changed")
    if result.get("execution") != {
        "optimizer_updates": 2,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "training_executed": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate frozen 100-update predictor-preserving training preregistration"
        ),
    }:
        raise ValueError("Winner-v21 two-update execution or authority changed")
    if result.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v21 two-update source identity changed")
    rollouts = result.get("rollouts")
    updates = result.get("optimization", {}).get("updates")
    if (
        not isinstance(rollouts, list)
        or not isinstance(updates, list)
        or [row.get("update") for row in rollouts] != [1, 2]
        or [row.get("update") for row in updates] != [1, 2]
        or set(result["optimization"].get("trainable_leaves", [])) != TRAINABLE_KEYS
        or len(result["optimization"].get("trainable_leaves", [])) != 12
        or result["optimization"].get("gradient_composition")
        != "explicit g_ppo + frozen_scale * g_predictor"
    ):
        raise ValueError("Winner-v21 two-update update schema changed")
    rederived = {
        "source_stage1_snapshot_exact": True,
        "both_exact_80_episode_populations": len(rollouts) == 2,
        "both_winner_v15_rollouts_bit_exact": all(
            row.get("winner_v15_transition_exact") is True for row in rollouts
        ),
        "both_episode_receipts_exact": all(
            isinstance(row.get("episode_receipts_sha256"), str)
            and HEX64_RE.fullmatch(row["episode_receipts_sha256"])
            for row in rollouts
        ),
        "both_action_boundaries_exact": all(
            row.get("action_boundary_exact") is True for row in rollouts
        ),
        "both_reward_formulas_exact_and_nonzero": all(
            row.get("reward_formula_exact_and_nonzero") is True for row in rollouts
        ),
        "both_sampled_hidden_replays_at_most_1e_6": all(
            type(row.get("sampled_hidden_replay_max_abs_error")) is float
            and 0.0 <= row["sampled_hidden_replay_max_abs_error"] <= 1.0e-6
            for row in rollouts
        ),
        "both_stored_successor_masks_exact": all(
            row.get("stored_successor_mask_exact") is True
            and type(row.get("stored_successor_transition_count")) is int
            and row["stored_successor_transition_count"] > 0
            for row in rollouts
        ),
        "frozen_predictor_scale_exact": result["predictor_scale"]
        == 8.393629541414427e-11,
        "both_updates_all_12_gradients_and_deltas_nonzero": all(
            set(row.get("combined_gradient_max_abs", {})) == TRAINABLE_KEYS
            and set(row.get("leaf_max_abs_delta", {})) == TRAINABLE_KEYS
            and all(value > 0.0 for value in row["combined_gradient_max_abs"].values())
            and all(value > 0.0 for value in row["leaf_max_abs_delta"].values())
            for row in updates
        ),
        "cumulative_all_12_leaves_changed": set(
            result["optimization"].get("cumulative_leaf_max_abs_delta", {})
        )
        == TRAINABLE_KEYS
        and all(
            value > 0.0
            for value in result["optimization"]["cumulative_leaf_max_abs_delta"].values()
        ),
        "two_adam_updates_exact": True,
        "snapshot_readback_exact": checks["snapshot_readback_exact"],
        "onnx_abi_exact": result.get("graph", {}).get("contract", {}).get("abi_exact")
        is True,
        "onnx_training_only_tensors_absent": result.get("graph", {})
        .get("contract", {})
        .get("training_only_tensors_absent")
        is True,
        "onnx_jax_chain_at_most_1e_7": result.get("graph", {})
        .get("contract", {})
        .get("jax_onnx_at_most_1e_7")
        is True,
        "onnx_previous_action_chain_exact": result.get("graph", {})
        .get("contract", {})
        .get("previous_action_out_equals_action_bit_exact")
        is True,
        "formal_support_locomotion_robot_zero": True,
    }
    if dict(checks) != rederived or not finite_tree(result):
        raise ValueError("Winner-v21 two-update evidence does not reproduce checks")
    for name in ("graph", "snapshot"):
        receipt = result.get(name, {})
        if (
            HEX64_RE.fullmatch(str(receipt.get("sha256", ""))) is None
            or type(receipt.get("bytes")) is not int
            or receipt["bytes"] <= 0
        ):
            raise ValueError(f"Winner-v21 two-update {name} receipt changed")


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
        raise FileExistsError("Winner-v21 two-update result is already imported")
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
        raise ValueError("Winner-v21 two-update raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(result)
    if (
        sha256_bytes(members[GRAPH_NAME]) != result["graph"]["sha256"]
        or len(members[GRAPH_NAME]) != result["graph"]["bytes"]
        or sha256_bytes(members[SNAPSHOT_NAME]) != result["snapshot"]["sha256"]
        or len(members[SNAPSHOT_NAME]) != result["snapshot"]["bytes"]
    ):
        raise ValueError("Winner-v21 two-update embedded artifact receipt changed")
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
                "# Winner-v21 predictor-preserving two-update CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Failed checks: `{len(payload['failed_checks'])}`",
                "- Optimizer updates / formal support / robot: `2 / 0 / 0`",
                "",
                "The optimizer consumed the explicit per-leaf sum of the frozen PPO",
                "and predictor gradients. A pass authorizes only a separately frozen",
                "100-update CPU training run; it does not authorize locomotion or robot use.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
