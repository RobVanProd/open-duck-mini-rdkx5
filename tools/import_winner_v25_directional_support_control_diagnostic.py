#!/usr/bin/env python3
"""Strictly import one Winner-v25 directional diagnostic artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import statistics
from typing import Any, Mapping
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v25_directional_support_control_diagnostic_preregistration.json"
ATTRIBUTION = ANALYSIS / "winner_v24_support_regression_attribution.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
V22_GATE_RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_support_gate.py"
V24_GATE_RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_support_gate.py"
RUNNER = ROOT / "tools/run_winner_v25_directional_support_control_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v25-directional-support-control-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v25_directional_support_control_diagnostic_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v25-directional-support-control-diagnostic-result.json"
RAW_RECEIPT_NAME = "winner-v25-directional-support-control-diagnostic-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "DISCOVERY_03",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_09",
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
CANDIDATES = (("half", 150), ("final", 200))
BASE_TICKS = 20
HORIZON = 5
PITCH_EPS = 1.0e-6
ACTION_EPS = 1.0e-6
FRACTION_THRESHOLD = 0.75
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
    "preregistration_lf_sha256",
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


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON is forbidden: {value}")


def require_sha(value: Any, label: str) -> None:
    if HEX64.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def read_artifact(path: Path) -> tuple[bytes, bytes]:
    expected = {RAW_RESULT_NAME, RAW_RECEIPT_NAME}
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Winner-v25 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v25 artifact exceeds size ceiling")
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
                raise ValueError("Winner-v25 artifact has unsafe member")
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
    require_sha(artifact_zip_sha256, "Winner-v25 artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v25-directional-support-control-diagnostic-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v25 repository attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def expected_population() -> dict[str, Any]:
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    source_snapshot = v22["snapshot_manifest"][99]
    source_graph = next(
        row["graph"] for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    snapshots = {row["completed_updates"]: row for row in v24["snapshot_manifest"]}
    checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    return {
        "source_checkpoint": {
            "label": "winner_v22_final",
            "update": 100,
            "snapshot_sha256": source_snapshot["sha256"],
            "onnx_sha256": source_graph["sha256"],
        },
        "candidate_checkpoints": {
            label: {
                "update": update,
                "snapshot_sha256": snapshots[update]["sha256"],
                "onnx_sha256": checkpoints[label]["graph"]["sha256"],
            }
            for label, update in CANDIDATES
        },
        "configuration_ids": list(CONFIGURATION_IDS),
        "actuator_plants": list(PLANTS),
        "base_prefix_ticks": BASE_TICKS,
        "fork_horizon_ticks": HORIZON,
    }


def validate_row(row: Mapping[str, Any]) -> None:
    expected_fields = {
        "candidate",
        "candidate_update",
        "configuration_id",
        "plant",
        "base_tick",
        "same_input_observation_sha256",
        "same_input_previous_action_sha256",
        "same_input_h_in_sha256",
        "simulator_state_sha256",
        "source_action",
        "candidate_action",
        "action_delta",
        "action_delta_linf",
        "action_changed",
        "source_end_pitch_rad",
        "candidate_end_pitch_rad",
        "abs_pitch_delta_rad",
        "candidate_locally_destabilizing",
        "source_completed_horizon_ticks",
        "candidate_completed_horizon_ticks",
        "source_end_state_sha256",
        "candidate_end_state_sha256",
        "source_clone_repeat_exact",
    }
    if (
        set(row) != expected_fields
        or (row.get("candidate"), row.get("candidate_update")) not in CANDIDATES
        or row.get("configuration_id") not in CONFIGURATION_IDS
        or row.get("plant") not in PLANTS
        or type(row.get("base_tick")) is not int
        or not 0 <= row["base_tick"] < BASE_TICKS
        or any(
            HEX64.fullmatch(str(row.get(name))) is None
            for name in (
                "same_input_observation_sha256",
                "same_input_previous_action_sha256",
                "same_input_h_in_sha256",
                "simulator_state_sha256",
                "source_end_state_sha256",
                "candidate_end_state_sha256",
            )
        )
        or row.get("source_clone_repeat_exact") is not True
    ):
        raise ValueError("Winner-v25 fork-row schema changed")
    arrays = []
    for name in ("source_action", "candidate_action", "action_delta"):
        value = np.asarray(row[name], dtype=np.float32)
        if value.shape != (14,) or not np.all(np.isfinite(value)):
            raise ValueError(f"Winner-v25 {name} changed")
        arrays.append(value)
    source, candidate, recorded_delta = arrays
    delta = (candidate - source).astype(np.float32)
    if not np.array_equal(delta, recorded_delta):
        raise ValueError("Winner-v25 action delta is not rederived")
    linf = float(np.max(np.abs(delta)))
    scalar_names = (
        "action_delta_linf",
        "source_end_pitch_rad",
        "candidate_end_pitch_rad",
        "abs_pitch_delta_rad",
    )
    if not all(math.isfinite(float(row[name])) for name in scalar_names):
        raise ValueError("Winner-v25 fork scalar is nonfinite")
    pitch_delta = abs(float(row["candidate_end_pitch_rad"])) - abs(
        float(row["source_end_pitch_rad"])
    )
    early_terminal = (
        row["candidate_completed_horizon_ticks"] < HORIZON
        and row["source_completed_horizon_ticks"] == HORIZON
    )
    if (
        float(row["action_delta_linf"]) != linf
        or row["action_changed"] is not (linf > ACTION_EPS)
        or float(row["abs_pitch_delta_rad"]) != pitch_delta
        or row["candidate_locally_destabilizing"]
        is not (early_terminal or pitch_delta > PITCH_EPS)
        or type(row["source_completed_horizon_ticks"]) is not int
        or type(row["candidate_completed_horizon_ticks"]) is not int
        or not 0 <= row["source_completed_horizon_ticks"] <= HORIZON
        or not 0 <= row["candidate_completed_horizon_ticks"] <= HORIZON
    ):
        raise ValueError("Winner-v25 fork-row derivation changed")


def rederive_aggregates(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for label, update in CANDIDATES:
        selected = [row for row in rows if row["candidate"] == label]
        pitch = [float(row["abs_pitch_delta_rad"]) for row in selected]
        changed = sum(row["action_changed"] for row in selected)
        destabilizing = sum(row["candidate_locally_destabilizing"] for row in selected)
        fraction = destabilizing / len(selected)
        median = float(statistics.median(pitch))
        values[label] = {
            "update": update,
            "fork_points": len(selected),
            "action_changed_points": changed,
            "action_changed_fraction": changed / len(selected),
            "locally_destabilizing_points": destabilizing,
            "locally_destabilizing_fraction": fraction,
            "abs_pitch_delta_rad": {
                "minimum": min(pitch),
                "median": median,
                "mean": float(statistics.fmean(pitch)),
                "maximum": max(pitch),
            },
            "meets_frozen_local_destabilization_rule": bool(
                fraction >= FRACTION_THRESHOLD and median > PITCH_EPS
            ),
        }
    return values


def validate_result(value: Mapping[str, Any]) -> None:
    raw_fields = {
        "authority",
        "candidate_aggregates",
        "checks",
        "classification",
        "decision",
        "execution",
        "failed_checks",
        "fork_results",
        "population",
        "schema_version",
        "sources",
        "status",
        "thresholds",
    }
    if frozenset(value) not in {
        frozenset(raw_fields),
        frozenset(raw_fields | {"repository_attribution"}),
    } or value.get("schema_version") != (
        "winner_v25.directional_support_control_diagnostic_result.v1"
    ):
        raise ValueError("Winner-v25 result schema changed")
    if value.get("population") != expected_population() or value.get("thresholds") != {
        "pitch_delta_epsilon_rad": PITCH_EPS,
        "action_delta_epsilon": ACTION_EPS,
        "destabilizing_fraction": FRACTION_THRESHOLD,
    }:
        raise ValueError("Winner-v25 population or thresholds changed")
    rows = value.get("fork_results")
    if not isinstance(rows, list) or len(rows) != 800:
        raise ValueError("Winner-v25 fork population changed")
    for row in rows:
        validate_row(row)
    keys = [
        (
            row["candidate"],
            row["configuration_id"],
            row["plant"],
            row["base_tick"],
        )
        for row in rows
    ]
    expected_keys = [
        (label, configuration, plant, tick)
        for label, _ in CANDIDATES
        for configuration in CONFIGURATION_IDS
        for plant in PLANTS
        for tick in range(BASE_TICKS)
    ]
    if sorted(keys) != sorted(expected_keys):
        raise ValueError("Winner-v25 fork identities changed")
    aggregates = rederive_aggregates(rows)
    if value.get("candidate_aggregates") != aggregates:
        raise ValueError("Winner-v25 aggregates are not rederived")
    execution = {
        "base_trajectories": 20,
        "fork_points": 800,
        "short_horizon_rollouts": 1600,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    checks = {
        "exact_20_base_trajectories": True,
        "all_20_tick_base_prefixes_valid": True,
        "exact_800_candidate_fork_points": True,
        "exact_1600_short_horizon_rollouts": True,
        "all_source_clone_repeats_bit_exact": all(
            row["source_clone_repeat_exact"] for row in rows
        ),
        "all_source_forks_complete_five_ticks": all(
            row["source_completed_horizon_ticks"] == HORIZON for row in rows
        ),
        "all_metrics_finite": True,
        "both_candidates_change_action_on_at_least_95_percent_of_forks": all(
            row["action_changed_fraction"] >= 0.95 for row in aggregates.values()
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    if value.get("execution") != execution or value.get("checks") != checks:
        raise ValueError("Winner-v25 execution or checks changed")
    failed = sorted(name for name, passed in checks.items() if not passed)
    local = all(
        row["meets_frozen_local_destabilization_rule"] for row in aggregates.values()
    )
    classification = (
        "SAME_STATE_ACTION_CHANGE_LOCALLY_DESTABILIZING"
        if local else "NO_DOMINANT_SAME_STATE_LOCAL_DESTABILIZATION"
    )
    decision = (
        "AUTHORIZE_DIRECTIONAL_COUNTERFACTUAL_OBJECTIVE_CPU_CONTRACT_ONLY"
        if local
        else "AUTHORIZE_LONGER_HORIZON_RECURRENT_CREDIT_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    if failed:
        classification = "INVALID_WINNER_V25_DIRECTIONAL_DIAGNOSTIC"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    if (
        value.get("failed_checks") != failed
        or value.get("status")
        != (
            "PASS_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
        )
        or value.get("classification") != classification
        or value.get("decision") != decision
        or value.get("authority")
        != {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
        }
        or value.get("sources")
        != {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
            "v22_gate_runner_lf_sha256": lf_sha256(V22_GATE_RUNNER),
            "v24_gate_runner_lf_sha256": lf_sha256(V24_GATE_RUNNER),
            "runner_lf_sha256": lf_sha256(RUNNER),
        }
    ):
        raise ValueError("Winner-v25 classification or authority changed")
    if "repository_attribution" in value:
        item = value["repository_attribution"]
        if (
            not isinstance(item, Mapping)
            or set(item) != ATTRIBUTION_FIELDS
            or item.get("repository") != EXPECTED_REPOSITORY
            or item.get("github_run_attempt") != 1
            or HEX40.fullmatch(str(item.get("github_run_head_sha"))) is None
            or item.get("github_artifact_digest")
            != f"sha256:{item.get('artifact_zip_sha256')}"
            or item.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or item.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or item.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or item.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v25 imported attribution changed")


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
        raise FileExistsError("Winner-v25 result is already imported")
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
    raw_bytes, receipt_bytes = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v25 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    result = dict(raw)
    result["repository_attribution"] = {
        **attribution,
        "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(result)
    OUTPUT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v25 directional support-control diagnostic result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Fork points / five-tick rollouts: `800 / 1,600`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This result selects only the next offline CPU evidence contract.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(result["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
