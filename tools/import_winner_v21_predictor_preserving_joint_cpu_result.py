#!/usr/bin/env python3
"""Safely import one Winner-v21 zero-update CPU-contract result."""

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
CONTRACT = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_failure_attribution.json"
RUNNER = ROOT / "tools/run_winner_v21_predictor_preserving_joint_cpu_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v21-predictor-preserving-joint-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v21-predictor-preserving-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v21-predictor-preserving-cpu-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
RECURRENT_KEYS = {
    "obs_weight",
    "previous_action_weight",
    "hidden_weight",
    "hidden_bias",
}
PREDICTOR_KEYS = {
    "auxiliary_hidden_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
}
PPO_ONLY_KEYS = {
    "action_weight",
    "action_bias",
    "training_only_log_std",
    "training_only_value_weight",
    "training_only_value_bias",
}
TRAINABLE_KEYS = RECURRENT_KEYS | PREDICTOR_KEYS | PPO_ONLY_KEYS
CHECKS = {
    "source_stage1_snapshot_exact",
    "exact_80_episode_population",
    "winner_v15_rollout_bit_exact",
    "episode_receipts_exact",
    "action_boundary_exact",
    "reward_formula_exact_and_nonzero",
    "sampled_hidden_replay_at_most_1e_6",
    "stored_successor_mask_exact",
    "ppo_gradient_partition_exact",
    "predictor_gradient_partition_exact",
    "gradient_balance_scale_finite_positive",
    "combined_all_12_gradients_nonzero",
    "combined_gradient_is_exact_sum_at_most_1e_6",
    "all_losses_gradients_and_metrics_finite",
    "parameters_bit_exact_unchanged",
    "optimizer_updates_zero",
    "formal_support_locomotion_robot_zero",
}
RAW_FIELDS = {
    "schema_version",
    "status",
    "decision",
    "checks",
    "failed_checks",
    "environment",
    "source_snapshot",
    "rollout",
    "objective",
    "execution",
    "sources",
    "authority",
}
ATTRIBUTION_FIELDS = {
    "repository",
    "github_run_id",
    "github_run_attempt",
    "github_run_head_sha",
    "github_artifact_id",
    "github_artifact_name",
    "github_artifact_digest",
    "artifact_zip_sha256",
    "artifact_zip_bytes",
    "raw_result_sha256",
    "raw_result_receipt_sha256",
    "contract_lf_sha256",
    "workflow_lf_sha256",
    "runner_lf_sha256",
    "importer_lf_sha256",
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


def finite(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v21 CPU artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v21 CPU artifact exceeds size ceiling")
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
                raise ValueError("Winner-v21 CPU artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


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
        or artifact_name != f"winner-v21-predictor-preserving-cpu-{run_id}"
        or HEX64_RE.fullmatch(artifact_zip_sha256) is None
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v21 CPU workflow attribution changed")
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
    observed = frozenset(result)
    if observed not in {
        frozenset(RAW_FIELDS),
        frozenset(RAW_FIELDS | {"repository_attribution"}),
    }:
        raise ValueError("Winner-v21 CPU result schema changed")
    if result.get("schema_version") != "winner_v21.predictor_preserving_joint_cpu_result.v1":
        raise ValueError("Winner-v21 CPU result version changed")
    checks = result.get("checks")
    if (
        not isinstance(checks, Mapping)
        or set(checks) != CHECKS
        or not all(type(value) is bool for value in checks.values())
    ):
        raise ValueError("Winner-v21 CPU checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
            if passed
            else "HOLD_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_SEPARATE_TWO_UPDATE_PREDICTOR_PRESERVING_PROOF_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_UPDATE_OR_TRAIN_WINNER_V21"
        )
    ):
        raise ValueError("Winner-v21 CPU decision changed")
    if result.get("execution") != {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "training_executed": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate frozen two-update predictor-preserving CPU proof"
        ),
    }:
        raise ValueError("Winner-v21 CPU execution or authority changed")
    if result.get("source_snapshot") != {
        "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
        "bytes": 189027,
    } or result.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v21 CPU source identity changed")
    rollout = result.get("rollout", {})
    if (
        rollout.get("sampled_count", 0) <= 0
        or rollout.get("valid_transition_count", 0) <= 0
        or rollout.get("stored_successor_transition_count", 0) <= 0
        or rollout.get("winner_v15_transition_exact") is not True
        or rollout.get("action_boundary_exact") is not True
        or not finite(rollout.get("sampled_hidden_replay_max_abs_error"))
    ):
        raise ValueError("Winner-v21 CPU rollout evidence changed")
    objective = result.get("objective", {})
    if set(objective.get("trainable_leaves", [])) != TRAINABLE_KEYS or len(
        objective.get("trainable_leaves", [])
    ) != 12:
        raise ValueError("Winner-v21 trainable leaf set changed")
    balance = objective.get("balance", {})
    if (
        not all(
            finite(balance.get(name)) and balance[name] > 0.0
            for name in (
                "ppo_action_head_gradient_rms",
                "predictor_head_gradient_rms",
                "predictor_scale",
            )
        )
        or not all(
            finite(objective.get(name))
            for name in ("ppo_loss", "predictor_loss", "combined_loss")
        )
        or not finite(objective.get("combined_gradient_max_abs_error_from_sum"))
    ):
        raise ValueError("Winner-v21 objective receipt changed")
    ppo = objective.get("ppo_gradient_max_abs", {})
    predictor = objective.get("predictor_gradient_max_abs", {})
    combined = objective.get("combined_gradient_max_abs", {})
    if set(ppo) != TRAINABLE_KEYS or set(predictor) != TRAINABLE_KEYS or set(combined) != TRAINABLE_KEYS:
        raise ValueError("Winner-v21 gradient tree changed")
    if (
        not all(finite(value) and value >= 0.0 for tree in (ppo, predictor, combined) for value in tree.values())
        or not all(ppo[name] == 0.0 for name in RECURRENT_KEYS | PREDICTOR_KEYS)
        or not all(ppo[name] > 0.0 for name in PPO_ONLY_KEYS)
        or not all(predictor[name] > 0.0 for name in RECURRENT_KEYS | PREDICTOR_KEYS)
        or not all(predictor[name] == 0.0 for name in PPO_ONLY_KEYS)
        or not all(combined[name] > 0.0 for name in TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v21 gradient partition changed")
    if "repository_attribution" in result:
        attribution = result["repository_attribution"]
        if (
            not isinstance(attribution, Mapping)
            or set(attribution) != ATTRIBUTION_FIELDS
            or attribution.get("repository") != EXPECTED_REPOSITORY
            or attribution.get("github_run_attempt") != 1
            or attribution.get("github_artifact_name")
            != f"winner-v21-predictor-preserving-cpu-{attribution.get('github_run_id')}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or attribution.get("contract_lf_sha256") != lf_sha256(CONTRACT)
            or attribution.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or attribution.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or attribution.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v21 imported attribution changed")


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
        raise FileExistsError("Winner-v21 CPU result is already imported")
    zip_sha = sha256(args.artifact_zip)
    base_attribution = repository_attribution(
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha,
        artifact_id=args.artifact_id,
        artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v21 CPU raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
        **base_attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v21 predictor-preserving joint CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Predictor scale: `{payload['objective']['balance']['predictor_scale']}`",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
                "",
                "A PASS authorizes only a separately preregistered two-update CPU proof.",
                "It does not authorize support training, locomotion, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
