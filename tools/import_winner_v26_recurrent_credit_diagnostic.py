#!/usr/bin/env python3
"""Strictly import the sole Winner-v26 recurrent-credit diagnostic artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import statistics
import sys
from typing import Any, Mapping
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import run_winner_v26_recurrent_credit_diagnostic as runner  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_preregistration.json"
V25_RESULT = ANALYSIS / "winner_v25_directional_support_control_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v26_recurrent_credit_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v26-recurrent-credit-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v26-recurrent-credit-diagnostic-result.json"
RAW_RECEIPT_NAME = "winner-v26-recurrent-credit-diagnostic-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_RESULT_BYTES = 64 * 1024 * 1024
ATTRIBUTION_FIELDS = {
    "artifact_zip_bytes",
    "artifact_zip_sha256",
    "github_artifact_digest",
    "github_artifact_id",
    "github_artifact_name",
    "github_run_attempt",
    "github_run_head_sha",
    "github_run_id",
    "importer_lf_sha256",
    "preregistration_lf_sha256",
    "raw_result_receipt_sha256",
    "raw_result_sha256",
    "repository",
    "runner_lf_sha256",
    "workflow_lf_sha256",
}


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
    expected_name = f"winner-v26-recurrent-credit-diagnostic-{run_id}"
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != expected_name
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
        or HEX64.fullmatch(artifact_zip_sha256) is None
    ):
        raise ValueError("Winner-v26 repository attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def read_artifact(path: Path) -> tuple[bytes, bytes]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in members]
        if sorted(names) != sorted([RAW_RESULT_NAME, RAW_RECEIPT_NAME]):
            raise ValueError(f"Winner-v26 artifact inventory changed: {names}")
        for item in members:
            name = PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts or item.is_dir():
                raise ValueError("Winner-v26 artifact contains unsafe member")
            if item.file_size > MAX_RESULT_BYTES or item.compress_size > MAX_RESULT_BYTES:
                raise ValueError("Winner-v26 artifact member is oversized")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def expected_population() -> dict[str, Any]:
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    source_snapshot = v22["snapshot_manifest"][runner.SOURCE_UPDATE - 1]
    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == runner.SOURCE_UPDATE
    )
    snapshots = {row["completed_updates"]: row for row in v24["snapshot_manifest"]}
    checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    return {
        "source_checkpoint": {
            "label": "winner_v22_final",
            "update": runner.SOURCE_UPDATE,
            "snapshot_sha256": source_snapshot["sha256"],
            "onnx_sha256": source_graph["sha256"],
        },
        "candidate_checkpoints": {
            label: {
                "update": update,
                "snapshot_sha256": snapshots[update]["sha256"],
                "onnx_sha256": checkpoints[label]["graph"]["sha256"],
            }
            for label, update in runner.CANDIDATES
        },
        "configuration_ids": list(runner.CONFIGURATION_IDS),
        "actuator_plants": list(smoke.PLANTS),
        "base_prefix_ticks": runner.BASE_PREFIX_TICKS,
        "recurrent_horizon_ticks": runner.RECURRENT_HORIZON_TICKS,
    }


def finite_array(value: Any, width: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.shape != (width,) or not np.all(np.isfinite(array)):
        raise ValueError(f"Winner-v26 {name} changed")
    return array


def validate_trace(trace: Mapping[str, Any], initial_previous_action: np.ndarray) -> None:
    if set(trace) != {
        "actions",
        "attempted_ticks",
        "end_state_sha256",
        "hidden_outputs",
        "observations",
        "pitch_rad",
        "roll_rad",
        "terminal",
        "terminal_absolute_tick",
        "valid_ticks",
    }:
        raise ValueError("Winner-v26 trace schema changed")
    attempted = trace["attempted_ticks"]
    valid = trace["valid_ticks"]
    if type(attempted) is not int or type(valid) is not int or not 1 <= attempted <= 32:
        raise ValueError("Winner-v26 trace count changed")
    terminal = trace["terminal"]
    if terminal is None:
        if valid != attempted or attempted != runner.RECURRENT_HORIZON_TICKS:
            raise ValueError("Winner-v26 complete trace count changed")
        if trace["terminal_absolute_tick"] is not None:
            raise ValueError("Winner-v26 complete trace has terminal tick")
    else:
        if not isinstance(terminal, Mapping) or valid != attempted - 1:
            raise ValueError("Winner-v26 terminal trace count changed")
        expected_tick = runner.BASE_PREFIX_TICKS + valid
        if (
            trace["terminal_absolute_tick"] != expected_tick
            or terminal.get("absolute_tick") != expected_tick
            or terminal.get("relative_tick") != valid
        ):
            raise ValueError("Winner-v26 terminal tick changed")
    sequence_widths = {
        "observations": 115,
        "actions": 14,
        "hidden_outputs": 64,
    }
    arrays: dict[str, list[np.ndarray]] = {}
    for name, width in sequence_widths.items():
        rows = trace[name]
        if not isinstance(rows, list) or len(rows) != attempted:
            raise ValueError(f"Winner-v26 {name} length changed")
        arrays[name] = [finite_array(row, width, name) for row in rows]
    for name in ("roll_rad", "pitch_rad"):
        values = trace[name]
        if (
            not isinstance(values, list)
            or len(values) != attempted
            or not all(math.isfinite(float(value)) for value in values)
        ):
            raise ValueError(f"Winner-v26 {name} changed")
    previous = np.asarray(initial_previous_action, dtype=np.float32)
    for action in arrays["actions"]:
        action32 = action.astype(np.float32)
        if not np.array_equal(action32, smoke.bounded_action_numpy(action32, previous)):
            raise ValueError("Winner-v26 recorded action violates graph boundary")
        previous = action32
    if HEX64.fullmatch(str(trace["end_state_sha256"])) is None:
        raise ValueError("Winner-v26 end-state hash changed")


def validate_result(value: Mapping[str, Any]) -> None:
    fields = {
        "authority",
        "base_trajectories",
        "candidate_aggregates",
        "candidate_branches",
        "checks",
        "classification",
        "decision",
        "execution",
        "failed_checks",
        "population",
        "schema_version",
        "sources",
        "status",
        "thresholds",
    }
    if frozenset(value) not in {
        frozenset(fields),
        frozenset(fields | {"repository_attribution"}),
    } or value.get("schema_version") != "winner_v26.recurrent_credit_diagnostic_result.v1":
        raise ValueError("Winner-v26 result schema changed")
    if value.get("population") != expected_population() or value.get("thresholds") != {
        "regression_fraction": runner.REGRESSION_FRACTION_THRESHOLD,
        "minimum_median_lead_ticks": runner.MINIMUM_MEDIAN_LEAD_TICKS,
        "action_delta_epsilon": runner.ACTION_DELTA_EPS,
        "pitch_delta_epsilon_rad": runner.PITCH_DELTA_EPS_RAD,
    }:
        raise ValueError("Winner-v26 population or thresholds changed")
    bases = value.get("base_trajectories")
    branches = value.get("candidate_branches")
    if not isinstance(bases, list) or len(bases) != 20:
        raise ValueError("Winner-v26 base population changed")
    if not isinstance(branches, list) or len(branches) != 40:
        raise ValueError("Winner-v26 candidate population changed")
    base_lookup: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in bases:
        if set(row) != {
            "configuration_id",
            "h_in",
            "observation",
            "plant",
            "previous_action",
            "simulator_state_sha256",
            "source_clone_repeat_exact",
            "source_trace",
            "source_trace_sha256",
        }:
            raise ValueError("Winner-v26 base-row schema changed")
        key = (row["configuration_id"], row["plant"])
        if key in base_lookup:
            raise ValueError("Winner-v26 duplicate base row")
        finite_array(row["observation"], 115, "base observation")
        previous = finite_array(row["previous_action"], 14, "base previous action")
        finite_array(row["h_in"], 64, "base hidden input")
        if (
            HEX64.fullmatch(str(row["simulator_state_sha256"])) is None
            or row["source_clone_repeat_exact"] is not True
            or row["source_trace_sha256"] != runner.canonical_sha256(row["source_trace"])
        ):
            raise ValueError("Winner-v26 base identity changed")
        validate_trace(row["source_trace"], previous)
        base_lookup[key] = row
    expected_base_keys = {
        (configuration, plant)
        for configuration in runner.CONFIGURATION_IDS
        for plant in smoke.PLANTS
    }
    if set(base_lookup) != expected_base_keys:
        raise ValueError("Winner-v26 base identities changed")
    expected_branch_keys = {
        (label, configuration, plant)
        for label, _ in runner.CANDIDATES
        for configuration in runner.CONFIGURATION_IDS
        for plant in smoke.PLANTS
    }
    observed_branch_keys = set()
    for row in branches:
        if set(row) != {
            "candidate",
            "candidate_trace",
            "candidate_trace_sha256",
            "candidate_update",
            "comparison",
            "configuration_id",
            "plant",
            "shared_simulator_state_sha256",
        }:
            raise ValueError("Winner-v26 candidate-row schema changed")
        key = (row["candidate"], row["configuration_id"], row["plant"])
        observed_branch_keys.add(key)
        base = base_lookup[(row["configuration_id"], row["plant"])]
        expected_update = dict(runner.CANDIDATES).get(row["candidate"])
        previous = finite_array(base["previous_action"], 14, "base previous action")
        validate_trace(row["candidate_trace"], previous)
        if (
            row["candidate_update"] != expected_update
            or row["shared_simulator_state_sha256"] != base["simulator_state_sha256"]
            or row["candidate_trace_sha256"]
            != runner.canonical_sha256(row["candidate_trace"])
            or row["comparison"]
            != runner.compare_branches(base["source_trace"], row["candidate_trace"])
        ):
            raise ValueError("Winner-v26 candidate derivation changed")
    if observed_branch_keys != expected_branch_keys:
        raise ValueError("Winner-v26 candidate identities changed")
    aggregates = runner.aggregate_candidates(branches)
    if value.get("candidate_aggregates") != aggregates:
        raise ValueError("Winner-v26 aggregates are not rederived")
    execution = {
        "base_trajectories": 20,
        "candidate_branches": 40,
        "branch_rollouts": 80,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    checks = {
        "exact_20_base_trajectories": True,
        "all_20_tick_source_prefixes_valid": True,
        "exact_40_candidate_branches": True,
        "exact_80_branch_rollouts": True,
        "all_source_clone_repeats_bit_exact": True,
        "all_initial_candidate_actions_changed": all(
            row["comparison"]["initial_action_changed"] for row in branches
        ),
        "all_metrics_finite": True,
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    selected = all(
        row["meets_frozen_post_prefix_regression_rule"] for row in aggregates.values()
    )
    classification = (
        "POST_PREFIX_RECURRENT_CLOSED_LOOP_REGRESSION"
        if selected
        else "NO_DOMINANT_POST_PREFIX_RECURRENT_REGRESSION"
    )
    decision = (
        "AUTHORIZE_RECURRENT_PARAMETER_BLOCK_SWAP_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if selected
        else "AUTHORIZE_EARLY_PREFIX_DIVERGENCE_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    if failed:
        classification = "INVALID_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    if (
        value.get("execution") != execution
        or value.get("checks") != checks
        or value.get("failed_checks") != failed
        or value.get("status")
        != (
            "PASS_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
            if not failed
            else "HOLD_WINNER_V26_RECURRENT_CREDIT_DIAGNOSTIC"
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
            "v25_result_lf_sha256": lf_sha256(V25_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "runner_lf_sha256": lf_sha256(RUNNER),
        }
    ):
        raise ValueError("Winner-v26 classification or authority changed")
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
            raise ValueError("Winner-v26 imported attribution changed")


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
        raise FileExistsError("Winner-v26 result is already imported")
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
        raise ValueError("Winner-v26 raw-result receipt changed")
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
                "# Winner-v26 recurrent-credit diagnostic result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Base / candidate / rollout counts: `20 / 40 / 80`",
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
