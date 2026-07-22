#!/usr/bin/env python3
"""Safely import the sole Winner-v44 source-gradient CPU result."""

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
CONTRACT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_contract.json"
RUNNER = ROOT / "tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v44-static-target-teacher-source-gradient.yml"
OUTPUT_JSON = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v44-static-target-teacher-source-gradient-result.json"
RAW_RECEIPT_NAME = "winner-v44-static-target-teacher-source-gradient-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
CHECK_NAMES = {
    "cpu_only_environment_exact",
    "winner_v32_half_source_snapshot_and_graph_exact",
    "winner_v22_teacher_snapshot_exact",
    "source_selection_99_of_124_over_94_of_124_exact",
    "target_normalizer_bit_exact",
    "exact_80_episode_rollout_at_update_251",
    "episode_receipts_exact",
    "action_boundary_exact",
    "pitch_margin_reward_exact",
    "winner_v32_baseline_objective_transition_exact",
    "exact_22_training_teacher_configuration_plant_rows",
    "heldout_teacher_configuration_rows_excluded",
    "teacher_mask_has_valid_pitch_elements_only",
    "teacher_loss_finite_nonzero",
    "teacher_gradients_nonzero_on_all_six_policy_leaves",
    "teacher_gradients_zero_on_value_logstd_predictor_leaves",
    "baseline_composed_matches_direct_at_most_4e_6",
    "teacher_scale_finite_positive",
    "scaled_teacher_rms_matches_baseline_at_most_2e_6_relative",
    "default_off_combined_gradient_bit_exact",
    "enabled_changes_all_six_policy_gradient_leaves",
    "enabled_preserves_nonpolicy_gradients_bit_exact",
    "enabled_direct_loss_gradient_matches_composition_at_most_4e_6",
    "predictor_metrics_finite_and_successors_present",
    "ppo_metrics_finite_and_hidden_replay_exact",
    "prefix_anchor_metrics_finite_and_exact",
    "teacher_metrics_finite_and_mask_exact",
    "all_losses_metrics_gradients_finite",
    "transition_arrays_unchanged_by_teacher",
    "parameters_and_optimizer_unchanged_no_update",
    "optimizer_updates_zero",
    "formal_support_cells_zero",
    "locomotion_training_steps_zero",
    "deployable_graph_exports_zero",
    "robot_or_rdk_access_zero",
}
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "contract_lf_sha256", "workflow_lf_sha256",
    "runner_lf_sha256", "importer_lf_sha256",
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
    raise ValueError(f"nonfinite JSON value is forbidden: {value}")


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_result_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v44 artifact inventory changed")
        if sum(item.file_size for item in infos) > 20_000_000:
            raise ValueError("Winner-v44 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v44 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v44 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v44-static-target-teacher-source-gradient-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v44 workflow attribution changed")
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
    raw_fields = {
        "schema_version", "status", "decision", "checks", "failed_checks",
        "source_identity", "rollout_evidence", "objective_evidence", "execution",
        "environment", "sources", "source_manifest_sha256", "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v44.static_target_teacher_source_gradient_result.v1":
        raise ValueError("Winner-v44 result schema changed")
    if "repository_attribution" in result:
        attribution = result["repository_attribution"]
        if (
            not isinstance(attribution, Mapping) or set(attribution) != ATTRIBUTION_FIELDS
            or attribution.get("repository") != EXPECTED_REPOSITORY
            or attribution.get("github_run_attempt") != 1
            or type(attribution.get("github_run_id")) is not int
            or attribution["github_run_id"] <= 0
            or HEX40_RE.fullmatch(str(attribution.get("github_run_head_sha"))) is None
            or type(attribution.get("github_artifact_id")) is not int
            or attribution["github_artifact_id"] <= 0
            or attribution.get("github_artifact_name")
            != f"winner-v44-static-target-teacher-source-gradient-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(HEX64_RE.fullmatch(str(attribution.get(name))) is None for name in (
                "artifact_zip_sha256", "raw_result_sha256", "raw_result_receipt_sha256",
                "contract_lf_sha256", "workflow_lf_sha256", "runner_lf_sha256",
                "importer_lf_sha256",
            ))
            or attribution["contract_lf_sha256"] != lf_sha256(CONTRACT)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["runner_lf_sha256"] != lf_sha256(RUNNER)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v44 imported attribution changed")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        result.get("sources") != contract["sources"]
        or result.get("source_manifest_sha256") != contract["source_manifest_sha256"]
        or result.get("authority") != contract["authority"]
    ):
        raise ValueError("Winner-v44 source manifest or authority changed")
    checks = result.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != CHECK_NAMES or any(
        type(value) is not bool for value in checks.values()
    ):
        raise ValueError("Winner-v44 checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
            if passed else "HOLD_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_ONE_UPDATE_STATIC_TARGET_TEACHER_CPU_PROOF_PREREGISTRATION_ONLY"
            if passed else "DO_NOT_RUN_STATIC_TARGET_TEACHER_UPDATE"
        )
    ):
        raise ValueError("Winner-v44 decision changed")
    if result.get("source_identity") != {
        "label": "half", "completed_updates": 251,
        "snapshot": contract["artifact_inputs"]["winner_v32"]["half"]["snapshot"],
        "graph": contract["artifact_inputs"]["winner_v32"]["half"]["graph"],
        "teacher_snapshot": contract["artifact_inputs"]["winner_v22"]["snapshot"],
    }:
        raise ValueError("Winner-v44 source identity changed")
    rollout = result.get("rollout_evidence")
    if not isinstance(rollout, Mapping) or set(rollout) != {
        "rollout_update_index", "episode_slots", "episode_receipts_sha256",
        "roll_pitch_failure_count", "selected_teacher_rows",
        "selected_teacher_elements", "observations_sha256",
        "previous_actions_sha256", "teacher_raw_targets_sha256",
        "teacher_bounded_targets_sha256", "teacher_mask_sha256",
    }:
        raise ValueError("Winner-v44 rollout evidence schema changed")
    if (
        rollout["rollout_update_index"] != 251 or rollout["episode_slots"] != 80
        or rollout["selected_teacher_rows"] != 22
        or type(rollout["selected_teacher_elements"]) is not int
        or not 0 < rollout["selected_teacher_elements"] <= 45_000
        or type(rollout["roll_pitch_failure_count"]) is not int
        or rollout["roll_pitch_failure_count"] not in range(81)
    ):
        raise ValueError("Winner-v44 rollout dimensions changed")
    for name in (
        "episode_receipts_sha256", "observations_sha256", "previous_actions_sha256",
        "teacher_raw_targets_sha256", "teacher_bounded_targets_sha256",
        "teacher_mask_sha256",
    ):
        require_sha256(rollout[name], f"Winner-v44 {name}")
    objective = result.get("objective_evidence")
    if not isinstance(objective, Mapping) or set(objective) != {
        "ppo_loss", "normalized_predictor_loss", "prefix_anchor_loss",
        "static_target_teacher_loss", "predictor_scale", "prefix_anchor_scale",
        "teacher_scale", "balance", "teacher_gradient_max_abs",
        "baseline_composition_delta_max_abs", "enabled_composition_delta_max_abs",
        "enabled_gradient_delta_max_abs",
    }:
        raise ValueError("Winner-v44 objective evidence schema changed")
    for name in (
        "ppo_loss", "normalized_predictor_loss", "prefix_anchor_loss",
        "static_target_teacher_loss", "predictor_scale", "prefix_anchor_scale",
        "teacher_scale",
    ):
        value = objective[name]
        if type(value) not in {int, float} or not math.isfinite(value):
            raise ValueError(f"Winner-v44 {name} changed")
    if (
        objective["static_target_teacher_loss"] <= 0.0
        or objective["teacher_scale"] <= 0.0
        or objective["predictor_scale"] != 380.9135437011719
        or objective["prefix_anchor_scale"] != 197.3112030029297
    ):
        raise ValueError("Winner-v44 objective constants changed")
    for name in (
        "balance", "teacher_gradient_max_abs", "baseline_composition_delta_max_abs",
        "enabled_composition_delta_max_abs", "enabled_gradient_delta_max_abs",
    ):
        tree = objective[name]
        if not isinstance(tree, Mapping) or not tree or any(
            type(value) not in {int, float} or not math.isfinite(value)
            for value in tree.values()
        ):
            raise ValueError(f"Winner-v44 {name} changed")
    if result.get("execution") != {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20_000,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v44 execution changed")
    environment = result.get("environment")
    if (
        not isinstance(environment, Mapping)
        or environment.get("jax_backend") != "cpu"
        or environment.get("jax_devices") != ["cpu"]
        or not isinstance(environment.get("mujoco_version"), str)
        or not isinstance(environment.get("numpy_version"), str)
    ):
        raise ValueError("Winner-v44 CPU environment changed")


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
        raise FileExistsError("Winner-v44 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id, run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha, artifact_id=args.artifact_id,
        artifact_name=args.artifact_name, artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_result_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v44 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
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
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rollout = payload["rollout_evidence"]
    objective = payload["objective_evidence"]
    OUTPUT_MD.write_text(
        "\n".join([
            "# Winner-v44 static-target teacher source-gradient result", "",
            f"- Status: `{payload['status']}`",
            f"- Decision: `{payload['decision']}`",
            "- Source: `Winner-v32 half @ 251`",
            f"- Teacher loss / derived scale: `{objective['static_target_teacher_loss']:.9f} / {objective['teacher_scale']:.9f}`",
            f"- Selected teacher rows / elements: `{rollout['selected_teacher_rows']} / {rollout['selected_teacher_elements']}`",
            "- Optimizer / formal gate / training / export / robot: `0 / 0 / 0 / 0 / 0`", "",
            "The scale is evidence for a separate one-update CPU proof only. This",
            "result does not train, export, select deployment, or clear the robot.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
