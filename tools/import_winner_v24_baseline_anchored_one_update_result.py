#!/usr/bin/env python3
"""Strictly import the first Winner-v24 baseline-anchored one-update proof."""

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
CONTRACT = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_contract.json"
ZERO_UPDATE = ANALYSIS / "winner_v24_baseline_anchored_cpu_result_v2.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
WORKFLOW = ROOT / ".github/workflows/winner-v24-baseline-anchored-one-update-cpu-proof.yml"
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_one_update_cpu_proof.py"
MECHANICS = ROOT / "patches/winner_v24_symmetric_support_failure_v2.py"
OUTPUT_JSON = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v24-baseline-anchored-one-update-result.json"
RAW_RECEIPT_NAME = "winner-v24-baseline-anchored-one-update-result.sha256"
SNAPSHOT_NAME = "winner_v24_baseline_anchored_update_101.npz"
GRAPH_NAME = "winner_v24_baseline_anchored_update_101.onnx"
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
RAW_FIELDS = {
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
    "source_snapshot",
    "sources",
    "status",
}
ATTRIBUTION_FIELDS = {
    "artifact_zip_bytes",
    "artifact_zip_sha256",
    "contract_lf_sha256",
    "github_artifact_digest",
    "github_artifact_id",
    "github_artifact_name",
    "github_run_attempt",
    "github_run_head_sha",
    "github_run_id",
    "graph_member_sha256",
    "importer_lf_sha256",
    "mechanics_lf_sha256",
    "raw_result_receipt_sha256",
    "raw_result_sha256",
    "repository",
    "runner_lf_sha256",
    "snapshot_member_sha256",
    "workflow_lf_sha256",
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


def read_artifact(path: Path) -> dict[str, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME, SNAPSHOT_NAME, GRAPH_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v24 one-update artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v24 one-update artifact exceeds size ceiling")
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
                raise ValueError("Winner-v24 one-update artifact has unsafe member")
        return {name: archive.read(name) for name in expected}


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v24 one-update artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name
        != f"winner-v24-baseline-anchored-one-update-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v24 one-update workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"Winner-v24 one-update {label} is not numeric")
    number = float(value)
    if not math.isfinite(number) or (positive and number <= 0.0):
        raise ValueError(f"Winner-v24 one-update {label} is invalid")
    return number


def _positive_tree(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, Mapping) or set(value) != GRADIENT_KEYS:
        raise ValueError(f"Winner-v24 one-update {label} tree changed")
    return {key: _finite(item, f"{label}.{key}", positive=True) for key, item in value.items()}


def final_snapshot_receipt() -> Mapping[str, Any]:
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or len(training.get("snapshot_manifest", [])) != 100
    ):
        raise ValueError("Winner-v24 one-update training source changed")
    return training["snapshot_manifest"][99]


def expected_objective() -> Mapping[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status")
        != "FROZEN_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT"
        or contract.get("decision")
        != "AUTHORIZE_EXACT_ONE_BASELINE_ANCHORED_OPTIMIZER_UPDATE_ONLY"
    ):
        raise ValueError("Winner-v24 one-update contract authority changed")
    return contract["objective"]


def validate_result(result: Mapping[str, Any]) -> None:
    if frozenset(result) not in {
        frozenset(RAW_FIELDS),
        frozenset(RAW_FIELDS | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v24.baseline_anchored_one_update_cpu_result.v1":
        raise ValueError("Winner-v24 one-update result schema changed")
    if "repository_attribution" in result:
        item = result["repository_attribution"]
        if (
            not isinstance(item, Mapping)
            or set(item) != ATTRIBUTION_FIELDS
            or item.get("repository") != EXPECTED_REPOSITORY
            or item.get("github_run_attempt") != 1
            or type(item.get("github_run_id")) is not int
            or item["github_run_id"] <= 0
            or HEX40_RE.fullmatch(str(item.get("github_run_head_sha"))) is None
            or type(item.get("github_artifact_id")) is not int
            or item["github_artifact_id"] <= 0
            or item.get("github_artifact_name")
            != f"winner-v24-baseline-anchored-one-update-{item['github_run_id']}"
            or item.get("github_artifact_digest")
            != f"sha256:{item.get('artifact_zip_sha256')}"
            or type(item.get("artifact_zip_bytes")) is not int
            or item["artifact_zip_bytes"] <= 0
            or any(
                HEX64_RE.fullmatch(str(item.get(name))) is None
                for name in ATTRIBUTION_FIELDS if name.endswith("sha256")
            )
            or item.get("contract_lf_sha256") != lf_sha256(CONTRACT)
            or item.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or item.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or item.get("mechanics_lf_sha256") != lf_sha256(MECHANICS)
            or item.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v24 one-update imported attribution changed")
    receipt = final_snapshot_receipt()
    zero_update = json.loads(ZERO_UPDATE.read_text(encoding="utf-8"))
    if (
        zero_update.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT"
        or zero_update.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_BASELINE_ANCHORED_CPU_PROOF_PREREGISTRATION_ONLY"
        or zero_update.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 one-update zero-update authority changed")
    if result.get("source_snapshot") != {
        "sha256": receipt["sha256"],
        "bytes": receipt["bytes"],
        "completed_updates": 100,
        "optimizer_count": 100,
    }:
        raise ValueError("Winner-v24 one-update source snapshot changed")
    if result.get("objective") != expected_objective():
        raise ValueError("Winner-v24 one-update objective changed")
    if result.get("execution") != {
        "rollout_episode_slots": 80,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "training_executed": False,
        "formal_support_gate_executed": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "manual_mass_com_inertia_measurements_required": False,
        "pass_authorizes_only": "a separate frozen baseline-anchored training preregistration",
    }:
        raise ValueError("Winner-v24 one-update execution or authority changed")
    environment = result.get("environment")
    if (
        not isinstance(environment, Mapping)
        or set(environment) != {"jax_backend", "jax_devices"}
        or environment.get("jax_backend") != "cpu"
        or not isinstance(environment.get("jax_devices"), list)
        or not environment["jax_devices"]
        or any("gpu" in str(device).lower() for device in environment["jax_devices"])
    ):
        raise ValueError("Winner-v24 one-update CPU environment changed")
    expected_sources = {
        "contract_lf_sha256": lf_sha256(CONTRACT),
        "zero_update_result_lf_sha256": lf_sha256(ZERO_UPDATE),
        "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
        "mechanics_lf_sha256": lf_sha256(MECHANICS),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }
    if result.get("sources") != expected_sources:
        raise ValueError("Winner-v24 one-update result sources changed")
    rollout = result.get("rollout")
    rollout_fields = {
        "action_boundary", "changed_batch_keys", "default_off_batch_bit_exact",
        "episode_receipts_sha256", "episode_slots", "objective_evidence",
        "objective_locality_exact", "pitch_margin_reward", "roll_pitch_failure_count",
        "sampled_count", "sampled_hidden_replay_max_abs_error", "settled_success_count",
        "stored_successor_mask_exact", "stored_successor_transition_count",
        "update_index", "valid_transition_count",
    }
    if (
        not isinstance(rollout, Mapping)
        or set(rollout) != rollout_fields
        or rollout["update_index"] != 100
        or rollout["episode_slots"] != 80
        or rollout["roll_pitch_failure_count"] != 12
        or rollout["settled_success_count"] != 22
        or rollout["changed_batch_keys"] != ["advantages", "returns", "rewards"]
        or not isinstance(rollout["action_boundary"], Mapping)
        or not isinstance(rollout["pitch_margin_reward"], Mapping)
        or rollout["default_off_batch_bit_exact"] is not True
        or rollout["objective_locality_exact"] is not True
        or rollout["stored_successor_mask_exact"] is not True
        or any(type(rollout[name]) is not int or rollout[name] <= 0 for name in (
            "sampled_count", "valid_transition_count", "stored_successor_transition_count"
        ))
    ):
        raise ValueError("Winner-v24 one-update rollout changed")
    require_sha256(rollout["episode_receipts_sha256"], "episode receipts")
    evidence = rollout["objective_evidence"]
    evidence_fields = {
        "anchor", "analytical_terminal_delta_max", "analytical_terminal_delta_min",
        "analytical_terminal_delta_nonzero_count", "analytical_terminal_delta_sha256",
        "baseline_raw_advantages_sha256", "enabled", "modified_batch_keys", "penalty",
        "roll_pitch_failure_count", "roll_pitch_failure_mask_sha256",
    }
    if (
        not isinstance(evidence, Mapping)
        or set(evidence) != evidence_fields
        or evidence["enabled"] is not True
        or evidence["anchor"] != "recorded_baseline_returns_and_rederived_values"
        or evidence["roll_pitch_failure_count"] != 12
        or evidence["penalty"] != -250.0
        or evidence["modified_batch_keys"] != ["advantages", "returns", "rewards"]
        or evidence["analytical_terminal_delta_nonzero_count"] <= 12
        or evidence["analytical_terminal_delta_min"] != -250.0
    ):
        raise ValueError("Winner-v24 one-update objective evidence changed")
    for name in (
        "analytical_terminal_delta_sha256", "baseline_raw_advantages_sha256",
        "roll_pitch_failure_mask_sha256",
    ):
        require_sha256(evidence[name], name)
    optimization = result.get("optimization")
    optimization_fields = {
        "all_finite", "combined_gradient_max_abs", "combined_loss", "leaf_max_abs_delta",
        "normalized_predictor_loss", "optimizer_count_after", "optimizer_count_before",
        "ppo_loss", "predictor_scale", "snapshot_readback_exact",
        "source_state_unchanged_before_update", "trainable_leaves",
    }
    if (
        not isinstance(optimization, Mapping)
        or set(optimization) != optimization_fields
        or optimization["optimizer_count_before"] != 100
        or optimization["optimizer_count_after"] != 101
        or optimization["predictor_scale"] != 380.9135437011719
        or optimization["all_finite"] is not True
        or optimization["snapshot_readback_exact"] is not True
        or optimization["source_state_unchanged_before_update"] is not True
        or set(optimization["trainable_leaves"]) != GRADIENT_KEYS
        or len(optimization["trainable_leaves"]) != 12
    ):
        raise ValueError("Winner-v24 one-update optimization changed")
    for name in ("ppo_loss", "normalized_predictor_loss", "combined_loss"):
        _finite(optimization[name], name)
    gradients = _positive_tree(
        optimization["combined_gradient_max_abs"], "combined gradients"
    )
    deltas = _positive_tree(optimization["leaf_max_abs_delta"], "leaf deltas")
    snapshot = result.get("snapshot")
    if (
        not isinstance(snapshot, Mapping)
        or set(snapshot)
        != {"path", "sha256", "bytes", "completed_updates", "state_payload_sha256", "metadata_payload_sha256"}
        or Path(str(snapshot["path"])).name != SNAPSHOT_NAME
        or snapshot["completed_updates"] != 101
        or type(snapshot["bytes"]) is not int
        or snapshot["bytes"] <= 0
    ):
        raise ValueError("Winner-v24 one-update snapshot receipt changed")
    for name in ("sha256", "state_payload_sha256", "metadata_payload_sha256"):
        require_sha256(snapshot[name], f"snapshot {name}")
    graph = result.get("graph")
    if (
        not isinstance(graph, Mapping)
        or set(graph) != {"path", "sha256", "bytes", "contract"}
        or Path(str(graph["path"])).name != GRAPH_NAME
        or type(graph["bytes"]) is not int
        or graph["bytes"] <= 0
        or not isinstance(graph["contract"], Mapping)
    ):
        raise ValueError("Winner-v24 one-update graph receipt changed")
    require_sha256(graph["sha256"], "graph")
    graph_contract = graph["contract"]
    checks = {
        "source_zero_update_result_exact": True,
        "source_snapshot_and_optimizer_count_100_exact": True,
        "exact_80_episode_population": rollout["episode_slots"] == 80,
        "episode_receipts_exact": bool(rollout["episode_receipts_sha256"]),
        "action_boundary_exact": rollout["action_boundary"].get(
            "realized_equals_numpy_bit_exact"
        )
        is True
        and rollout["action_boundary"].get("numpy_equals_jax_bit_exact") is True,
        "pitch_margin_reward_exact": rollout["pitch_margin_reward"].get(
            "reward_formula_bit_exact"
        )
        is True,
        "default_off_batch_bit_exact": rollout["default_off_batch_bit_exact"] is True,
        "failure_and_success_population_present": rollout["roll_pitch_failure_count"] > 0
        and rollout["settled_success_count"] > 0,
        "objective_locality_exact": rollout["objective_locality_exact"] is True,
        "analytic_delta_nonzero": evidence["analytical_terminal_delta_nonzero_count"]
        > rollout["roll_pitch_failure_count"],
        "sampled_hidden_replay_at_most_1e_6": _finite(
            rollout["sampled_hidden_replay_max_abs_error"], "hidden replay"
        )
        <= 1.0e-6,
        "stored_successor_mask_exact_nonzero": rollout[
            "stored_successor_transition_count"
        ] > 0
        and rollout["stored_successor_mask_exact"] is True,
        "all_12_combined_gradients_nonzero": all(value > 0.0 for value in gradients.values()),
        "all_12_trainable_leaves_changed": all(value > 0.0 for value in deltas.values()),
        "source_state_unchanged_before_update": optimization[
            "source_state_unchanged_before_update"
        ]
        is True,
        "exactly_one_optimizer_update_100_to_101": optimization["optimizer_count_after"] == 101,
        "all_losses_metrics_parameters_optimizer_finite": optimization["all_finite"]
        is True,
        "snapshot_readback_exact": optimization["snapshot_readback_exact"] is True,
        "onnx_abi_exact": graph_contract.get("abi_exact") is True,
        "onnx_training_only_tensors_absent": graph_contract.get("training_only_tensors_absent") is True,
        "onnx_jax_chain_at_most_1e_7": graph_contract.get("jax_onnx_at_most_1e_7") is True,
        "onnx_previous_action_chain_exact": graph_contract.get(
            "previous_action_out_equals_action_bit_exact"
        ) is True,
        "formal_support_locomotion_robot_zero": True,
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v24 one-update checks are not rederived")
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    if (
        result.get("failed_checks") != failed
        or result.get("status")
        != (
            "PASS_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
            if passed else "HOLD_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
        )
        or result.get("decision")
        != (
            "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_ONLY"
            if passed else "DO_NOT_TRAIN_WINNER_V24_BASELINE_ANCHORED_OBJECTIVE"
        )
    ):
        raise ValueError("Winner-v24 one-update decision changed")


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
        raise FileExistsError("Winner-v24 one-update result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id, run_attempt=args.run_attempt,
        run_head_sha=args.run_head_sha, artifact_id=args.artifact_id,
        artifact_name=args.artifact_name, artifact_digest=args.artifact_digest,
        artifact_zip_sha256=zip_sha,
    )
    members = read_artifact(args.artifact_zip)
    raw_bytes = members[RAW_RESULT_NAME]
    receipt_bytes = members[RAW_RECEIPT_NAME]
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v24 one-update raw receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    if (
        sha256_bytes(members[SNAPSHOT_NAME]) != result["snapshot"]["sha256"]
        or len(members[SNAPSHOT_NAME]) != result["snapshot"]["bytes"]
        or sha256_bytes(members[GRAPH_NAME]) != result["graph"]["sha256"]
        or len(members[GRAPH_NAME]) != result["graph"]["bytes"]
    ):
        raise ValueError("Winner-v24 one-update payload receipt changed")
    payload = dict(result)
    payload["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "snapshot_member_sha256": sha256_bytes(members[SNAPSHOT_NAME]),
        "graph_member_sha256": sha256_bytes(members[GRAPH_NAME]),
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
                "# Winner-v24 baseline-anchored one-update CPU result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Optimizer count: `100 -> 101`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "A pass authorizes only a separately frozen training preregistration.",
                "It does not itself authorize training, support evaluation, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
