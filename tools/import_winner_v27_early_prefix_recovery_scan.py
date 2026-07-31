#!/usr/bin/env python3
"""Strictly import the sole Winner-v27 early-prefix recovery artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import run_winner_v27_early_prefix_recovery_scan as runner  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v27_early_prefix_recovery_scan_preregistration.json"
V26_RESULT = ANALYSIS / "winner_v26_recurrent_credit_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V22_SUPPORT = ANALYSIS / "winner_v22_normalized_predictor_support_gate_result.json"
V24_SUPPORT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v27_early_prefix_recovery_scan.py"
WORKFLOW = ROOT / ".github/workflows/winner-v27-early-prefix-recovery-scan.yml"
OUTPUT_JSON = ANALYSIS / "winner_v27_early_prefix_recovery_scan_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v27-early-prefix-recovery-scan-result.json"
RAW_RECEIPT_NAME = "winner-v27-early-prefix-recovery-scan-result.sha256"
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
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v27-early-prefix-recovery-scan-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
        or HEX64.fullmatch(artifact_zip_sha256) is None
    ):
        raise ValueError("Winner-v27 repository attribution changed")
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
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in members]
        if sorted(names) != sorted([RAW_RESULT_NAME, RAW_RECEIPT_NAME]):
            raise ValueError(f"Winner-v27 artifact inventory changed: {names}")
        for item in members:
            member = PurePosixPath(item.filename)
            if member.is_absolute() or ".." in member.parts or item.is_dir():
                raise ValueError("Winner-v27 artifact contains unsafe member")
            if item.file_size > MAX_RESULT_BYTES or item.compress_size > MAX_RESULT_BYTES:
                raise ValueError("Winner-v27 artifact member is oversized")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def expected_population() -> dict[str, Any]:
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    source_graph = next(
        row["graph"]
        for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    return {
        "source_checkpoint": {
            "label": "winner_v22_final",
            "update": 100,
            "onnx_sha256": source_graph["sha256"],
        },
        "candidate_checkpoints": {
            label: {
                "update": update,
                "onnx_sha256": checkpoints[label]["graph"]["sha256"],
            }
            for label, update in runner.CANDIDATES
        },
        "configuration_ids": list(runner.CONFIGURATION_IDS),
        "actuator_plants": list(smoke.PLANTS),
        "fork_ticks": list(runner.FORK_TICKS),
        "absolute_end_tick": runner.ABSOLUTE_END_TICK,
    }


def validate_trace(trace: Mapping[str, Any], fork_tick: int) -> None:
    if set(trace) != {
        "actions_sha256",
        "attempted_ticks",
        "end_state_sha256",
        "hidden_outputs_sha256",
        "initial_action",
        "observations_sha256",
        "pitch_rad",
        "roll_rad",
        "terminal",
        "terminal_absolute_tick",
        "valid_ticks",
    }:
        raise ValueError("Winner-v27 trace schema changed")
    attempted = trace["attempted_ticks"]
    valid = trace["valid_ticks"]
    horizon = runner.ABSOLUTE_END_TICK - fork_tick
    if type(attempted) is not int or type(valid) is not int or not 1 <= attempted <= horizon:
        raise ValueError("Winner-v27 trace count changed")
    terminal = trace["terminal"]
    if terminal is None:
        if attempted != horizon or valid != horizon or trace["terminal_absolute_tick"] is not None:
            raise ValueError("Winner-v27 complete trace changed")
    else:
        expected_tick = fork_tick + valid
        if (
            not isinstance(terminal, Mapping)
            or valid != attempted - 1
            or trace["terminal_absolute_tick"] != expected_tick
            or terminal.get("absolute_tick") != expected_tick
            or terminal.get("relative_tick") != valid
        ):
            raise ValueError("Winner-v27 terminal trace changed")
    action = np.asarray(trace["initial_action"], dtype=np.float64)
    if action.shape != (14,) or not np.all(np.isfinite(action)):
        raise ValueError("Winner-v27 initial action changed")
    for name in (
        "actions_sha256",
        "end_state_sha256",
        "hidden_outputs_sha256",
        "observations_sha256",
    ):
        if HEX64.fullmatch(str(trace[name])) is None:
            raise ValueError(f"Winner-v27 {name} changed")
    for name in ("pitch_rad", "roll_rad"):
        values = trace[name]
        if (
            not isinstance(values, list)
            or len(values) != attempted
            or not all(math.isfinite(float(value)) for value in values)
        ):
            raise ValueError(f"Winner-v27 {name} changed")


def validate_result(value: Mapping[str, Any]) -> None:
    fields = {
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
        frozenset(fields),
        frozenset(fields | {"repository_attribution"}),
    } or value.get("schema_version") != "winner_v27.early_prefix_recovery_scan_result.v1":
        raise ValueError("Winner-v27 result schema changed")
    if value.get("population") != expected_population() or value.get("thresholds") != {
        "tick0_required_recovery_fraction": runner.TICK0_RECOVERY_FRACTION,
        "tick20_max_recovery_fraction_for_lock_in": runner.TICK20_MAX_RECOVERY_FRACTION,
        "action_delta_epsilon": runner.ACTION_DELTA_EPS,
    }:
        raise ValueError("Winner-v27 population or thresholds changed")
    rows = value.get("fork_results")
    if not isinstance(rows, list) or len(rows) != 240:
        raise ValueError("Winner-v27 fork population changed")
    expected_keys = {
        (label, configuration, plant, tick)
        for label, _ in runner.CANDIDATES
        for configuration in runner.CONFIGURATION_IDS
        for plant in smoke.PLANTS
        for tick in runner.FORK_TICKS
    }
    observed_keys = set()
    v22_support = json.loads(V22_SUPPORT.read_text(encoding="utf-8"))
    v24_support = json.loads(V24_SUPPORT.read_text(encoding="utf-8"))
    source_terminals = runner.support_terminal_lookup(v22_support, "final", 100)
    candidate_terminals = {
        label: runner.support_terminal_lookup(v24_support, label, update)
        for label, update in runner.CANDIDATES
    }
    for row in rows:
        if set(row) != {
            "candidate",
            "candidate_h_sha256",
            "candidate_trace",
            "candidate_update",
            "comparison",
            "configuration_id",
            "fork_tick",
            "observation_sha256",
            "plant",
            "previous_action_sha256",
            "snapshot_state_sha256",
            "source_recovery_trace",
            "source_repeat_exact",
            "source_shadow_h_sha256",
        }:
            raise ValueError("Winner-v27 fork-row schema changed")
        key = (
            row["candidate"],
            row["configuration_id"],
            row["plant"],
            row["fork_tick"],
        )
        observed_keys.add(key)
        if row["candidate_update"] != dict(runner.CANDIDATES).get(row["candidate"]):
            raise ValueError("Winner-v27 candidate update changed")
        for name in (
            "candidate_h_sha256",
            "observation_sha256",
            "previous_action_sha256",
            "snapshot_state_sha256",
            "source_shadow_h_sha256",
        ):
            if HEX64.fullmatch(str(row[name])) is None:
                raise ValueError(f"Winner-v27 {name} changed")
        validate_trace(row["candidate_trace"], row["fork_tick"])
        validate_trace(row["source_recovery_trace"], row["fork_tick"])
        if row["source_repeat_exact"] is not True:
            raise ValueError("Winner-v27 source repeat changed")
        if row["comparison"] != runner.compare_recovery(
            row["candidate_trace"], row["source_recovery_trace"]
        ):
            raise ValueError("Winner-v27 comparison changed")
        expected_candidate = candidate_terminals[row["candidate"]][
            (row["configuration_id"], row["plant"])
        ]
        if row["candidate_trace"]["terminal_absolute_tick"] != expected_candidate:
            raise ValueError("Winner-v27 candidate continuation no longer replays support")
        if row["fork_tick"] == 0 and row["source_recovery_trace"][
            "terminal_absolute_tick"
        ] != runner.right_censor_terminal(
            source_terminals[(row["configuration_id"], row["plant"])]
        ):
            raise ValueError("Winner-v27 fork-zero source no longer replays support")
    if observed_keys != expected_keys:
        raise ValueError("Winner-v27 fork identities changed")
    aggregates = runner.aggregate_scan(rows)
    if value.get("candidate_aggregates") != aggregates:
        raise ValueError("Winner-v27 aggregates are not rederived")
    execution = {
        "candidate_prefixes": 40,
        "forks": 240,
        "branch_rollouts": 720,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    checks = {
        "exact_40_candidate_prefixes": True,
        "all_candidate_prefixes_valid_through_tick_20": True,
        "exact_240_forks": True,
        "exact_720_branch_rollouts": True,
        "all_source_recovery_repeats_bit_exact": True,
        "all_candidate_continuations_reproduce_support_terminal": True,
        "all_fork0_source_replays_reproduce_v22_support_terminal": True,
        "all_initial_source_candidate_actions_changed": all(
            row["comparison"]["initial_action_changed"] for row in rows
        ),
        "all_metrics_finite": True,
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    lock_in = all(
        row["meets_frozen_early_state_lock_in_rule"] for row in aggregates.values()
    )
    classification = (
        "EARLY_PREFIX_PHYSICAL_STATE_LOCK_IN"
        if lock_in
        else "EARLY_PREFIX_STATE_REMAINS_SOURCE_RECOVERABLE"
    )
    decision = (
        "AUTHORIZE_PREFIX_JOINT_GROUP_ACTION_CAUSAL_SCREEN_PREREGISTRATION_ONLY"
        if lock_in
        else "AUTHORIZE_STATE_CONTROLLER_CROSS_SWAP_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    if failed:
        classification = "INVALID_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    if (
        value.get("execution") != execution
        or value.get("checks") != checks
        or value.get("failed_checks") != failed
        or value.get("status")
        != (
            "PASS_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
            if not failed
            else "HOLD_WINNER_V27_EARLY_PREFIX_RECOVERY_SCAN"
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
            "v26_result_lf_sha256": lf_sha256(V26_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "v22_support_lf_sha256": lf_sha256(V22_SUPPORT),
            "v24_support_lf_sha256": lf_sha256(V24_SUPPORT),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "runner_lf_sha256": lf_sha256(RUNNER),
        }
    ):
        raise ValueError("Winner-v27 classification or authority changed")
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
            raise ValueError("Winner-v27 imported attribution changed")


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
        raise FileExistsError("Winner-v27 result is already imported")
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
        raise ValueError("Winner-v27 raw-result receipt changed")
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
                "# Winner-v27 early-prefix recovery scan result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Candidate prefixes / forks / branch rollouts: `40 / 240 / 720`",
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
