#!/usr/bin/env python3
"""Safely import one Winner-v24 symmetric support-failure CPU result."""

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
CONTRACT = ANALYSIS / "winner_v24_symmetric_failure_cpu_contract.json"
V23_RESULT = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
MECHANICS = ROOT / "patches/winner_v24_symmetric_support_failure.py"
RUNNER = ROOT / "tools/run_winner_v24_symmetric_failure_cpu_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v24-symmetric-failure-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v24_symmetric_failure_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V24_SYMMETRIC_FAILURE_CPU_RESULT_20260721.md"
RAW_RESULT_NAME = "winner-v24-symmetric-failure-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v24-symmetric-failure-cpu-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
GRADIENT_KEYS = {
    "action_bias",
    "action_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
    "auxiliary_hidden_weight",
    "hidden_bias",
    "hidden_weight",
    "obs_weight",
    "previous_action_weight",
    "training_only_log_std",
    "training_only_value_bias",
    "training_only_value_weight",
}
RECURRENT_KEYS = {"hidden_bias", "hidden_weight", "obs_weight", "previous_action_weight"}
RAW_FIELDS = {
    "authority",
    "batch_evidence",
    "checks",
    "decision",
    "environment",
    "execution",
    "failed_checks",
    "gradient_evidence",
    "objective",
    "population",
    "schema_version",
    "source_checkpoint",
    "sources",
    "status",
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
    "mechanics_lf_sha256",
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


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v24 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v24 artifact exceeds size ceiling")
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
                raise ValueError("Winner-v24 artifact has unsafe member")
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
    require_sha256(artifact_zip_sha256, "Winner-v24 artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v24-symmetric-failure-cpu-contract-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v24 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _finite(value: Any, label: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"Winner-v24 {label} is not numeric")
    result = float(value)
    if not math.isfinite(result) or (nonnegative and result < 0.0):
        raise ValueError(f"Winner-v24 {label} is invalid")
    return result


def _gradient_map(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, Mapping) or set(value) != GRADIENT_KEYS:
        raise ValueError(f"Winner-v24 {label} gradient schema changed")
    return {
        key: _finite(item, f"{label}.{key}", nonnegative=True)
        for key, item in value.items()
    }


def final_snapshot_receipt() -> Mapping[str, Any]:
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or len(training.get("snapshot_manifest", [])) != 100
    ):
        raise ValueError("Winner-v24 training source changed")
    return training["snapshot_manifest"][99]


def validate_result(result: Mapping[str, Any]) -> None:
    if frozenset(result) not in {
        frozenset(RAW_FIELDS),
        frozenset(RAW_FIELDS | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v24.symmetric_failure_cpu_result.v1":
        raise ValueError("Winner-v24 result schema changed")
    if "repository_attribution" in result:
        attribution = result["repository_attribution"]
        if (
            not isinstance(attribution, Mapping)
            or set(attribution) != ATTRIBUTION_FIELDS
            or attribution.get("repository") != EXPECTED_REPOSITORY
            or attribution.get("github_run_attempt") != 1
            or type(attribution.get("github_run_id")) is not int
            or attribution["github_run_id"] <= 0
            or HEX40_RE.fullmatch(str(attribution.get("github_run_head_sha"))) is None
            or type(attribution.get("github_artifact_id")) is not int
            or attribution["github_artifact_id"] <= 0
            or attribution.get("github_artifact_name")
            != f"winner-v24-symmetric-failure-cpu-contract-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or type(attribution.get("artifact_zip_bytes")) is not int
            or attribution["artifact_zip_bytes"] <= 0
            or any(
                HEX64_RE.fullmatch(str(attribution.get(name))) is None
                for name in ATTRIBUTION_FIELDS
                if name.endswith("sha256")
            )
            or attribution.get("contract_lf_sha256") != lf_sha256(CONTRACT)
            or attribution.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or attribution.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or attribution.get("mechanics_lf_sha256") != lf_sha256(MECHANICS)
            or attribution.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v24 imported attribution changed")
    receipt = final_snapshot_receipt()
    if result.get("source_checkpoint") != {
        "label": "final",
        "completed_updates": 100,
        "sha256": receipt["sha256"],
        "bytes": receipt["bytes"],
    }:
        raise ValueError("Winner-v24 source checkpoint changed")
    if result.get("objective") != {
        "settled_success_bonus": 250.0,
        "roll_pitch_failure_penalty": -250.0,
        "failure_selector": "terminal.checks.roll_pitch is false",
        "source_rollout_update_index": 100,
        "reads_hidden_configuration": False,
        "changes_rollout_or_policy_action": False,
        "modified_batch_keys": ["advantages", "returns", "rewards"],
        "combined_delta_tolerance": 2.0e-6,
    }:
        raise ValueError("Winner-v24 objective changed")
    if result.get("execution") != {
        "rollout_episode_slots": 80,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "manual_mass_com_inertia_measurements_required": False,
        "pass_authorizes_only": "a separate one-update symmetric-failure CPU-proof preregistration",
    }:
        raise ValueError("Winner-v24 execution or authority changed")
    environment = result.get("environment")
    if (
        not isinstance(environment, Mapping)
        or set(environment) != {"jax_backend", "jax_devices"}
        or environment.get("jax_backend") != "cpu"
        or not isinstance(environment.get("jax_devices"), list)
        or not environment["jax_devices"]
        or any("gpu" in str(device).lower() for device in environment["jax_devices"])
    ):
        raise ValueError("Winner-v24 CPU environment changed")
    if result.get("sources") != {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "v23_result_lf_sha256": lf_sha256(V23_RESULT),
        "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
        "mechanics_lf_sha256": lf_sha256(MECHANICS),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v24 result sources changed")
    population = result.get("population")
    if (
        not isinstance(population, Mapping)
        or set(population)
        != {
            "episode_slots",
            "roll_pitch_failure_count",
            "settled_success_count",
            "episode_receipts_sha256",
        }
        or population["episode_slots"] != 80
        or type(population["roll_pitch_failure_count"]) is not int
        or population["roll_pitch_failure_count"] <= 0
        or type(population["settled_success_count"]) is not int
        or population["settled_success_count"] <= 0
    ):
        raise ValueError("Winner-v24 population changed")
    require_sha256(population["episode_receipts_sha256"], "Winner-v24 episode receipts")
    batch = result.get("batch_evidence")
    expected_batch_fields = {
        "action_boundary",
        "baseline_reward",
        "disabled",
        "enabled",
        "changed_keys",
        "default_off_batch_bit_exact",
        "terminal_failure_penalty_exact",
        "all_other_rewards_bit_exact",
        "parameters_unchanged",
        "baseline_return_replay_max_abs_error",
        "baseline_advantage_replay_max_abs_error",
        "baseline_rewards_sha256",
        "symmetric_rewards_sha256",
        "baseline_returns_sha256",
        "symmetric_returns_sha256",
        "baseline_advantages_sha256",
        "symmetric_advantages_sha256",
    }
    if not isinstance(batch, Mapping) or set(batch) != expected_batch_fields:
        raise ValueError("Winner-v24 batch evidence changed")
    for name in (
        "baseline_rewards_sha256",
        "symmetric_rewards_sha256",
        "baseline_returns_sha256",
        "symmetric_returns_sha256",
        "baseline_advantages_sha256",
        "symmetric_advantages_sha256",
    ):
        require_sha256(batch[name], f"Winner-v24 {name}")
    if any(
        batch[left] == batch[right]
        for left, right in (
            ("baseline_rewards_sha256", "symmetric_rewards_sha256"),
            ("baseline_returns_sha256", "symmetric_returns_sha256"),
            ("baseline_advantages_sha256", "symmetric_advantages_sha256"),
        )
    ):
        raise ValueError("Winner-v24 enabled objective did not change its three arrays")
    disabled = batch["disabled"]
    enabled = batch["enabled"]
    evidence_fields = {
        "enabled",
        "roll_pitch_failure_count",
        "roll_pitch_failure_mask_sha256",
        "penalty",
        "modified_batch_keys",
    }
    if (
        not isinstance(disabled, Mapping)
        or not isinstance(enabled, Mapping)
        or set(disabled) != evidence_fields
        or set(enabled) != evidence_fields
        or disabled["enabled"] is not False
        or enabled["enabled"] is not True
        or disabled["roll_pitch_failure_count"]
        != population["roll_pitch_failure_count"]
        or enabled["roll_pitch_failure_count"]
        != population["roll_pitch_failure_count"]
        or disabled["roll_pitch_failure_mask_sha256"]
        != enabled["roll_pitch_failure_mask_sha256"]
        or disabled["penalty"] != -250.0
        or enabled["penalty"] != -250.0
        or disabled["modified_batch_keys"] != []
        or enabled["modified_batch_keys"] != ["advantages", "returns", "rewards"]
        or batch["changed_keys"] != ["advantages", "returns", "rewards"]
    ):
        raise ValueError("Winner-v24 objective evidence changed")
    require_sha256(disabled["roll_pitch_failure_mask_sha256"], "Winner-v24 failure mask")
    action = batch["action_boundary"]
    reward = batch["baseline_reward"]
    if (
        not isinstance(action, Mapping)
        or action.get("realized_equals_numpy_bit_exact") is not True
        or action.get("numpy_equals_jax_bit_exact") is not True
        or not isinstance(reward, Mapping)
        or reward.get("reward_formula_bit_exact") is not True
    ):
        raise ValueError("Winner-v24 baseline contract evidence changed")
    return_error = _finite(
        batch["baseline_return_replay_max_abs_error"], "return replay", nonnegative=True
    )
    advantage_error = _finite(
        batch["baseline_advantage_replay_max_abs_error"],
        "advantage replay",
        nonnegative=True,
    )
    gradient = result.get("gradient_evidence")
    expected_gradient_fields = {
        "baseline_ppo_loss",
        "symmetric_ppo_loss",
        "baseline_normalized_predictor_loss",
        "symmetric_normalized_predictor_loss",
        "baseline_ppo_gradient_max_abs",
        "symmetric_ppo_gradient_max_abs",
        "ppo_gradient_delta_max_abs",
        "combined_gradient_delta_max_abs",
        "combined_delta_minus_ppo_delta_max_abs_error",
        "predictor_gradients_bit_exact",
    }
    if not isinstance(gradient, Mapping) or set(gradient) != expected_gradient_fields:
        raise ValueError("Winner-v24 gradient evidence changed")
    for name in (
        "baseline_ppo_loss",
        "symmetric_ppo_loss",
        "baseline_normalized_predictor_loss",
        "symmetric_normalized_predictor_loss",
    ):
        _finite(gradient[name], name)
    baseline_grad = _gradient_map(
        gradient["baseline_ppo_gradient_max_abs"], "baseline PPO"
    )
    symmetric_grad = _gradient_map(
        gradient["symmetric_ppo_gradient_max_abs"], "symmetric PPO"
    )
    ppo_delta = _gradient_map(gradient["ppo_gradient_delta_max_abs"], "PPO delta")
    combined_delta = _gradient_map(
        gradient["combined_gradient_delta_max_abs"], "combined delta"
    )
    composition_error = _finite(
        gradient["combined_delta_minus_ppo_delta_max_abs_error"],
        "composition error",
        nonnegative=True,
    )
    all_finite = all(
        math.isfinite(value)
        for value in (
            *baseline_grad.values(),
            *symmetric_grad.values(),
            *ppo_delta.values(),
            *combined_delta.values(),
        )
    )
    checks = {
        "source_final_snapshot_exact": True,
        "exact_80_episode_population": population["episode_slots"] == 80,
        "episode_receipts_exact": bool(population["episode_receipts_sha256"]),
        "action_boundary_exact": action["realized_equals_numpy_bit_exact"]
        and action["numpy_equals_jax_bit_exact"],
        "baseline_pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "baseline_gae_replay_at_most_1e_6": max(return_error, advantage_error) <= 1.0e-6,
        "default_off_batch_bit_exact": batch["default_off_batch_bit_exact"] is True,
        "roll_pitch_failures_and_settled_successes_both_present": population[
            "roll_pitch_failure_count"
        ]
        > 0
        and population["settled_success_count"] > 0,
        "enabled_changes_only_rewards_returns_advantages": batch["changed_keys"]
        == ["advantages", "returns", "rewards"],
        "terminal_failure_penalty_exact": batch["terminal_failure_penalty_exact"]
        is True,
        "all_other_rewards_bit_exact": batch["all_other_rewards_bit_exact"] is True,
        "predictor_loss_and_gradients_bit_exact": gradient[
            "baseline_normalized_predictor_loss"
        ]
        == gradient["symmetric_normalized_predictor_loss"]
        and gradient["predictor_gradients_bit_exact"] is True,
        "ppo_action_head_gradient_changes": max(
            ppo_delta["action_weight"], ppo_delta["action_bias"]
        )
        > 0.0,
        "ppo_recurrent_gradient_changes": max(ppo_delta[key] for key in RECURRENT_KEYS)
        > 0.0,
        "combined_delta_matches_ppo_delta_at_most_2e_6": composition_error <= 2.0e-6,
        "all_losses_metrics_and_gradients_finite": all_finite,
        "parameters_unchanged_no_optimizer_step": batch["parameters_unchanged"] is True,
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v24 checks are not rederived")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
            if passed
            else "HOLD_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_SEPARATE_ONE_UPDATE_SYMMETRIC_FAILURE_CPU_PROOF_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_RUN_WINNER_V24_OPTIMIZER_UPDATE"
        )
    ):
        raise ValueError("Winner-v24 decision changed")


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
        raise FileExistsError("Winner-v24 CPU result is already imported")
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
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v24 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
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
        "mechanics_lf_sha256": lf_sha256(MECHANICS),
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
                "# Winner-v24 symmetric support-failure CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                f"- Roll/pitch failures / settled successes: `{payload['population']['roll_pitch_failure_count']} / {payload['population']['settled_success_count']}`",
                "- Optimizer / formal support / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                "This is a zero-update objective proof. A pass authorizes only a separately",
                "preregistered one-update CPU proof, not training or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
