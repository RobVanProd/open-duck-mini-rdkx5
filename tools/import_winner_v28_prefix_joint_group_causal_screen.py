#!/usr/bin/env python3
"""Strictly import the sole Winner-v28 prefix joint-group causal artifact."""

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


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import import_winner_v27_early_prefix_recovery_scan as v27_import  # noqa: E402
import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import run_winner_v28_prefix_joint_group_causal_screen as runner  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_preregistration.json"
V27_RESULT = ANALYSIS / "winner_v27_early_prefix_recovery_scan_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V24_SUPPORT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v28_prefix_joint_group_causal_screen.py"
WORKFLOW = ROOT / ".github/workflows/winner-v28-prefix-joint-group-causal-screen.yml"
OUTPUT_JSON = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v28-prefix-joint-group-causal-screen-result.json"
RAW_RECEIPT_NAME = "winner-v28-prefix-joint-group-causal-screen-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_RESULT_BYTES = 64 * 1024 * 1024
ATTRIBUTION_FIELDS = {
    "artifact_zip_bytes", "artifact_zip_sha256", "github_artifact_digest",
    "github_artifact_id", "github_artifact_name", "github_run_attempt",
    "github_run_head_sha", "github_run_id", "importer_lf_sha256",
    "preregistration_lf_sha256", "raw_result_receipt_sha256",
    "raw_result_sha256", "repository", "runner_lf_sha256", "workflow_lf_sha256",
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
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    if (
        run_id <= 0 or run_attempt != 1 or HEX40.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v28-prefix-joint-group-causal-screen-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
        or HEX64.fullmatch(artifact_zip_sha256) is None
    ):
        raise ValueError("Winner-v28 repository attribution changed")
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
            raise ValueError(f"Winner-v28 artifact inventory changed: {names}")
        for item in members:
            member = PurePosixPath(item.filename)
            if member.is_absolute() or ".." in member.parts or item.is_dir():
                raise ValueError("Winner-v28 artifact contains unsafe member")
            if item.file_size > MAX_RESULT_BYTES or item.compress_size > MAX_RESULT_BYTES:
                raise ValueError("Winner-v28 artifact member is oversized")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def expected_population() -> dict[str, Any]:
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    source = next(
        row["graph"] for row in v22["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    checkpoints = {row["label"]: row for row in v24["persistent_checkpoints"]}
    return {
        "source_checkpoint": {
            "label": "winner_v22_final", "update": 100, "onnx_sha256": source["sha256"]
        },
        "candidate_checkpoints": {
            label: {"update": update, "onnx_sha256": checkpoints[label]["graph"]["sha256"]}
            for label, update in runner.CANDIDATES
        },
        "configuration_ids": list(runner.CONFIGURATION_IDS),
        "actuator_plants": list(smoke.PLANTS),
        "repair_ticks": runner.REPAIR_TICKS,
        "absolute_end_tick": runner.ABSOLUTE_END_TICK,
        "arms": {"CONTROL": [], **{name: list(indices) for name, indices in runner.GROUPS.items()}},
    }


def validate_result(value: Mapping[str, Any]) -> None:
    fields = {
        "arm_results", "authority", "candidate_aggregates", "checks",
        "classification", "decision", "execution", "failed_checks", "population",
        "schema_version", "selected_group", "sources", "status", "thresholds",
    }
    if frozenset(value) not in {
        frozenset(fields), frozenset(fields | {"repository_attribution"})
    } or value.get("schema_version") != "winner_v28.prefix_joint_group_causal_screen_result.v1":
        raise ValueError("Winner-v28 result schema changed")
    if value.get("population") != expected_population() or value.get("thresholds") != {
        "minimum_recovery_gain": runner.MINIMUM_RECOVERY_GAIN,
        "action_delta_epsilon": runner.ACTION_DELTA_EPS,
        "control_replay_pose_atol_rad": runner.CONTROL_REPLAY_POSE_ATOL_RAD,
    }:
        raise ValueError("Winner-v28 population or thresholds changed")
    rows = value.get("arm_results")
    if not isinstance(rows, list) or len(rows) != 240:
        raise ValueError("Winner-v28 arm population changed")
    expected_keys = {
        (label, configuration, plant, arm)
        for label, _ in runner.CANDIDATES
        for configuration in runner.CONFIGURATION_IDS
        for plant in smoke.PLANTS
        for arm in runner.ARMS
    }
    observed = set()
    support = json.loads(V24_SUPPORT.read_text(encoding="utf-8"))
    terminals = {
        label: runner.v27.support_terminal_lookup(support, label, update)
        for label, update in runner.CANDIDATES
    }
    v27_result = json.loads(V27_RESULT.read_text(encoding="utf-8"))
    v27_tick8 = {
        (row["candidate"], row["configuration_id"], row["plant"]): row
        for row in v27_result["fork_results"] if row["fork_tick"] == 8
    }
    for row in rows:
        if set(row) != {
            "arm", "candidate", "candidate_support_terminal_tick", "candidate_update",
            "comparison", "configuration_id", "maximum_replaced_action_delta", "plant",
            "replaced_action_indices", "source_recovery_trace", "source_repeat_exact",
            "tick8_snapshot_state_sha256",
        }:
            raise ValueError("Winner-v28 arm-row schema changed")
        key = (row["candidate"], row["configuration_id"], row["plant"], row["arm"])
        observed.add(key)
        arm = row["arm"]
        expected_indices = [] if arm == "CONTROL" else list(runner.GROUPS[arm])
        expected_terminal = terminals[row["candidate"]][
            (row["configuration_id"], row["plant"])
        ]
        if (
            row["candidate_update"] != dict(runner.CANDIDATES).get(row["candidate"])
            or row["replaced_action_indices"] != expected_indices
            or row["candidate_support_terminal_tick"] != expected_terminal
            or HEX64.fullmatch(str(row["tick8_snapshot_state_sha256"])) is None
            or row["source_repeat_exact"] is not True
            or not math.isfinite(float(row["maximum_replaced_action_delta"]))
            or (arm == "CONTROL" and row["maximum_replaced_action_delta"] != 0.0)
            or (arm != "CONTROL" and row["maximum_replaced_action_delta"] <= runner.ACTION_DELTA_EPS)
        ):
            raise ValueError("Winner-v28 arm identity changed")
        v27_import.validate_trace(row["source_recovery_trace"], runner.REPAIR_TICKS)
        if row["comparison"] != runner.recovery_against_terminal(
            expected_terminal, row["source_recovery_trace"]
        ):
            raise ValueError("Winner-v28 comparison changed")
        if arm == "CONTROL" and not runner.control_replays_v27(
            row["source_recovery_trace"],
            v27_tick8[(row["candidate"], row["configuration_id"], row["plant"])][
                "source_recovery_trace"
            ],
        ):
            raise ValueError("Winner-v28 control no longer replays Winner-v27")
    if observed != expected_keys:
        raise ValueError("Winner-v28 arm identities changed")
    aggregates, selected_group = runner.aggregate_screen(rows)
    if value.get("candidate_aggregates") != aggregates or value.get("selected_group") != selected_group:
        raise ValueError("Winner-v28 selection is not rederived")
    execution = {
        "prefix_arms": 240, "source_recovery_rollouts": 480,
        "optimizer_updates": 0, "locomotion_steps": 0, "robot_or_rdk_access": 0,
    }
    checks = {
        "exact_240_prefix_arms": True,
        "all_prefix_arms_valid_through_tick_8": True,
        "exact_480_source_recovery_rollouts": True,
        "all_source_recovery_repeats_bit_exact": True,
        "all_control_arms_reproduce_winner_v27_tick8": True,
        "all_group_interventions_change_named_action": True,
        "all_metrics_finite": True,
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    classification = (
        "SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
        if selected_group is not None else "NO_SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
    )
    decision = (
        "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if selected_group is not None
        else "AUTHORIZE_PREFIX_GROUP_INTERACTION_DIAGNOSTIC_PREREGISTRATION_ONLY"
    )
    if failed:
        classification = "INVALID_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        selected_group = None
    if (
        value.get("execution") != execution or value.get("checks") != checks
        or value.get("failed_checks") != failed
        or value.get("status") != (
            "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN" if not failed
            else "HOLD_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        )
        or value.get("classification") != classification or value.get("decision") != decision
        or value.get("selected_group") != selected_group
        or value.get("authority") != {
            "robot_clearance": False, "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
        }
        or value.get("sources") != {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v27_result_lf_sha256": lf_sha256(V27_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "v24_training_lf_sha256": lf_sha256(V24_TRAINING),
            "v24_support_lf_sha256": lf_sha256(V24_SUPPORT),
            "domain_lf_sha256": lf_sha256(DOMAIN),
            "runner_lf_sha256": lf_sha256(RUNNER),
        }
    ):
        raise ValueError("Winner-v28 classification or authority changed")
    if "repository_attribution" in value:
        item = value["repository_attribution"]
        if (
            not isinstance(item, Mapping) or set(item) != ATTRIBUTION_FIELDS
            or item.get("repository") != EXPECTED_REPOSITORY
            or item.get("github_run_attempt") != 1
            or HEX40.fullmatch(str(item.get("github_run_head_sha"))) is None
            or item.get("github_artifact_digest") != f"sha256:{item.get('artifact_zip_sha256')}"
            or item.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or item.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or item.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or item.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v28 imported attribution changed")


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
        raise FileExistsError("Winner-v28 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    attribution = repository_attribution(
        run_id=args.run_id, run_attempt=args.run_attempt, run_head_sha=args.run_head_sha,
        artifact_id=args.artifact_id, artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest, artifact_zip_sha256=zip_sha,
    )
    raw_bytes, receipt_bytes = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v28 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    result = dict(raw)
    result["repository_attribution"] = {
        **attribution, "artifact_zip_sha256": zip_sha,
        "artifact_zip_bytes": args.artifact_zip.stat().st_size,
        "raw_result_sha256": raw_sha,
        "raw_result_receipt_sha256": sha256_bytes(receipt_bytes),
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "workflow_lf_sha256": lf_sha256(WORKFLOW),
        "runner_lf_sha256": lf_sha256(RUNNER),
        "importer_lf_sha256": lf_sha256(Path(__file__)),
    }
    validate_result(result)
    OUTPUT_JSON.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v28 prefix joint-group causal screen result", "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Selected group: `{result['selected_group']}`",
                f"- Decision: `{result['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Prefix arms / recovery rollouts: `240 / 480`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`", "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(result["classification"])
    print(f"SELECTED_GROUP={result['selected_group']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
