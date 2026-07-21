#!/usr/bin/env python3
"""Safely import one Winner-v23 negative-X response-use diagnostic result."""

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
PREREGISTRATION = (
    ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_preregistration.json"
)
TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
HOLD_ATTRIBUTION = ANALYSIS / "winner_v22_support_hold_attribution.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
V22_GATE_RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_support_gate.py"
RUNNER = ROOT / "tools/run_winner_v23_negative_x_response_use_diagnostic.py"
WORKFLOW = ROOT / ".github/workflows/winner-v23-negative-x-response-use-diagnostic.yml"
OUTPUT_JSON = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_result.json"
OUTPUT_MD = (
    ANALYSIS / "WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC_RESULT_20260721.md"
)
RAW_RESULT_NAME = "winner-v23-negative-x-response-use-diagnostic-result.json"
RAW_RECEIPT_NAME = "winner-v23-negative-x-response-use-diagnostic-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
PAIR_IDS = (
    ("COM_X_NEG", "COM_X_POS"),
    ("COM_CORNER_00", "COM_CORNER_04"),
    ("COM_CORNER_01", "COM_CORNER_05"),
    ("COM_CORNER_02", "COM_CORNER_06"),
    ("COM_CORNER_03", "COM_CORNER_07"),
)
CHECKPOINTS = (("half", 50), ("final", 100))
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
EARLY_TICKS = 25
MIN_PERSISTENT_TICKS = 5
HIDDEN_LINF_THRESHOLD = 1.0e-7
FORK_ACTION_LINF_THRESHOLD = 1.0e-5
MIN_DECISION_CELLS = 16
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
RAW_FIELDS = {
    "aggregate",
    "authority",
    "checks",
    "classification",
    "decision",
    "execution",
    "failed_checks",
    "paired_results",
    "population",
    "schema_version",
    "sources",
    "status",
    "thresholds",
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
    "preregistration_lf_sha256",
    "workflow_lf_sha256",
    "runner_lf_sha256",
    "importer_lf_sha256",
}
PAIR_FIELDS = {
    "checkpoint",
    "update",
    "plant",
    "negative_configuration_id",
    "positive_configuration_id",
    "negative_support_pass",
    "positive_support_pass",
    "negative_terminal",
    "positive_terminal",
    "negative_trace_hashes",
    "positive_trace_hashes",
    "common_valid_transition_prefix_ticks",
    "early_analysis_ticks",
    "hidden_linf_by_tick",
    "actual_action_linf_by_tick",
    "same_input_hidden_fork_action_linf_by_tick",
    "hidden_first_persistent_crossing_tick",
    "fork_action_first_persistent_crossing_tick",
    "response_encoded_early",
    "response_used_by_action_early",
    "negative_early_learned_normalized_prediction_mse",
    "negative_early_constant_normalized_prediction_mse",
    "positive_early_learned_normalized_prediction_mse",
    "positive_early_constant_normalized_prediction_mse",
    "predictor_beats_constant_both_signs_early",
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
            raise ValueError("Winner-v23 diagnostic artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v23 diagnostic artifact exceeds size ceiling")
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
                raise ValueError("Winner-v23 diagnostic artifact has unsafe member")
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
    require_sha256(artifact_zip_sha256, "Winner-v23 diagnostic artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v23-negative-x-response-use-diagnostic-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v23 diagnostic workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def first_persistent_crossing(values: list[Any], threshold: float) -> int | None:
    if len(values) != EARLY_TICKS:
        raise ValueError("Winner-v23 diagnostic early series length changed")
    mask = [float(value) > threshold for value in values]
    for start in range(len(mask) - MIN_PERSISTENT_TICKS + 1):
        if all(mask[start : start + MIN_PERSISTENT_TICKS]):
            return start
    return None


def _finite_nonnegative(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"Winner-v23 {label} is not numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"Winner-v23 {label} is nonfinite or negative")
    return result


def _validate_trace_hashes(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "actions",
        "hidden",
        "observations",
        "predictions",
    }:
        raise ValueError(f"Winner-v23 {label} trace inventory changed")
    for name, digest in value.items():
        require_sha256(digest, f"Winner-v23 {label} {name}")


def validate_pair(row: Mapping[str, Any], expected: tuple[str, int, str, str, str]) -> None:
    if set(row) != PAIR_FIELDS:
        raise ValueError("Winner-v23 paired-result schema changed")
    checkpoint, update, plant, negative_id, positive_id = expected
    if (
        row.get("checkpoint") != checkpoint
        or row.get("update") != update
        or row.get("plant") != plant
        or row.get("negative_configuration_id") != negative_id
        or row.get("positive_configuration_id") != positive_id
        or type(row.get("negative_support_pass")) is not bool
        or type(row.get("positive_support_pass")) is not bool
        or type(row.get("common_valid_transition_prefix_ticks")) is not int
        or row["common_valid_transition_prefix_ticks"] < EARLY_TICKS
        or row.get("early_analysis_ticks") != EARLY_TICKS
    ):
        raise ValueError("Winner-v23 paired-result identity changed")
    for name in ("negative_terminal", "positive_terminal"):
        if row[name] is not None and not isinstance(row[name], Mapping):
            raise ValueError(f"Winner-v23 {name} schema changed")
    _validate_trace_hashes(row["negative_trace_hashes"], "negative")
    _validate_trace_hashes(row["positive_trace_hashes"], "positive")
    for name in (
        "hidden_linf_by_tick",
        "actual_action_linf_by_tick",
        "same_input_hidden_fork_action_linf_by_tick",
    ):
        values = row[name]
        if not isinstance(values, list) or len(values) != EARLY_TICKS:
            raise ValueError(f"Winner-v23 {name} length changed")
        for value in values:
            _finite_nonnegative(value, name)
    hidden_tick = first_persistent_crossing(
        row["hidden_linf_by_tick"], HIDDEN_LINF_THRESHOLD
    )
    fork_tick = first_persistent_crossing(
        row["same_input_hidden_fork_action_linf_by_tick"],
        FORK_ACTION_LINF_THRESHOLD,
    )
    if (
        row.get("hidden_first_persistent_crossing_tick") != hidden_tick
        or row.get("fork_action_first_persistent_crossing_tick") != fork_tick
        or row.get("response_encoded_early") is not (hidden_tick is not None)
        or row.get("response_used_by_action_early") is not (fork_tick is not None)
    ):
        raise ValueError("Winner-v23 persistent crossing is not rederived")
    neg_learned = _finite_nonnegative(
        row["negative_early_learned_normalized_prediction_mse"], "negative learned MSE"
    )
    neg_constant = _finite_nonnegative(
        row["negative_early_constant_normalized_prediction_mse"], "negative constant MSE"
    )
    pos_learned = _finite_nonnegative(
        row["positive_early_learned_normalized_prediction_mse"], "positive learned MSE"
    )
    pos_constant = _finite_nonnegative(
        row["positive_early_constant_normalized_prediction_mse"], "positive constant MSE"
    )
    predictor_pass = neg_learned < neg_constant and pos_learned < pos_constant
    if row.get("predictor_beats_constant_both_signs_early") is not predictor_pass:
        raise ValueError("Winner-v23 early predictor comparison is not rederived")


def _expected_sequence() -> list[tuple[str, int, str, str, str]]:
    return [
        (label, update, plant, negative_id, positive_id)
        for label, update in CHECKPOINTS
        for negative_id, positive_id in PAIR_IDS
        for plant in PLANTS
    ]


def _decision(encoded: int, predicted: int, used: int) -> tuple[str, str]:
    if encoded >= MIN_DECISION_CELLS and predicted >= MIN_DECISION_CELLS:
        if used >= MIN_DECISION_CELLS:
            return (
                "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE",
                "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY",
            )
        return (
            "RESPONSE_STATE_PRESENT_ACTION_COUPLING_DEFICIT",
            "AUTHORIZE_RESPONSE_ACTION_COUPLING_CPU_CONTRACT_ONLY",
        )
    return (
        "EARLY_RESPONSE_INFERENCE_DEFICIT",
        "AUTHORIZE_EARLY_RESPONSE_INFERENCE_CPU_CONTRACT_ONLY",
    )


def validate_result(result: Mapping[str, Any]) -> None:
    if frozenset(result) not in {
        frozenset(RAW_FIELDS),
        frozenset(RAW_FIELDS | {"repository_attribution"}),
    } or result.get("schema_version") != (
        "winner_v23.negative_x_response_use_diagnostic_result.v1"
    ):
        raise ValueError("Winner-v23 diagnostic result schema changed")
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
            != f"winner-v23-negative-x-response-use-diagnostic-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or type(attribution.get("artifact_zip_bytes")) is not int
            or attribution["artifact_zip_bytes"] <= 0
            or any(
                HEX64_RE.fullmatch(str(attribution.get(name))) is None
                for name in (
                    "artifact_zip_sha256",
                    "raw_result_sha256",
                    "raw_result_receipt_sha256",
                    "preregistration_lf_sha256",
                    "workflow_lf_sha256",
                    "runner_lf_sha256",
                    "importer_lf_sha256",
                )
            )
            or attribution.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or attribution.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or attribution.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or attribution.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v23 imported repository attribution changed")
    if result.get("population") != {
        "configuration_pairs": [list(pair) for pair in PAIR_IDS],
        "checkpoint_labels": ["half", "final"],
        "actuator_plants": list(PLANTS),
        "paired_cells": 20,
        "physics_rollouts": 40,
        "early_analysis_ticks": EARLY_TICKS,
    } or result.get("thresholds") != {
        "minimum_persistent_ticks": MIN_PERSISTENT_TICKS,
        "hidden_linf": HIDDEN_LINF_THRESHOLD,
        "same_input_hidden_fork_action_linf": FORK_ACTION_LINF_THRESHOLD,
        "minimum_cells_for_branch": MIN_DECISION_CELLS,
    }:
        raise ValueError("Winner-v23 population or thresholds changed")
    if result.get("execution") != {
        "paired_cells": 20,
        "physics_rollouts": 40,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "manual_mass_com_inertia_measurements_required": False,
        "pass_authorizes_only": "the single CPU contract named by the frozen decision tree",
    }:
        raise ValueError("Winner-v23 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
        "hold_attribution_lf_sha256": lf_sha256(HOLD_ATTRIBUTION),
        "domain_lf_sha256": lf_sha256(DOMAIN),
        "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
        "v22_gate_runner_lf_sha256": lf_sha256(V22_GATE_RUNNER),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v23 result sources changed")
    rows = result.get("paired_results")
    expected = _expected_sequence()
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("Winner-v23 paired-result count changed")
    for row, identity in zip(rows, expected, strict=True):
        if not isinstance(row, Mapping):
            raise ValueError("Winner-v23 paired result is not an object")
        validate_pair(row, identity)
    encoded = sum(row["response_encoded_early"] for row in rows)
    used = sum(row["response_used_by_action_early"] for row in rows)
    predicted = sum(row["predictor_beats_constant_both_signs_early"] for row in rows)
    negative_failures = sum(not row["negative_support_pass"] for row in rows)
    positive_failures = sum(not row["positive_support_pass"] for row in rows)
    aggregate = {
        "response_encoded_early_cells": encoded,
        "response_used_by_action_early_cells": used,
        "predictor_beats_constant_both_signs_early_cells": predicted,
        "negative_support_failure_cells": negative_failures,
        "positive_support_failure_cells": positive_failures,
    }
    if result.get("aggregate") != aggregate:
        raise ValueError("Winner-v23 aggregate is not rederived")
    checks = {
        "exact_20_paired_cells": len(rows) == 20,
        "exact_40_unchanged_physics_rollouts": len(rows) * 2 == 40,
        "all_25_tick_windows_present": all(
            row["early_analysis_ticks"] == EARLY_TICKS
            and row["common_valid_transition_prefix_ticks"] >= EARLY_TICKS
            for row in rows
        ),
        "all_metrics_finite": True,
        "all_positive_sign_controls_pass_support": positive_failures == 0,
        "at_least_16_negative_sign_cells_reproduce_support_failure": (
            negative_failures >= MIN_DECISION_CELLS
        ),
        "optimizer_updates_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v23 checks are not rederived")
    failed = sorted(name for name, passed in checks.items() if not passed)
    classification, decision = _decision(encoded, predicted, used)
    passed = not failed
    if not passed:
        decision = "DO_NOT_ADVANCE_WINNER_V23_DIAGNOSTIC"
    if (
        result.get("failed_checks") != failed
        or result.get("classification") != classification
        or result.get("decision") != decision
        or result.get("status")
        != (
            "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
            if passed
            else "HOLD_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        )
    ):
        raise ValueError("Winner-v23 diagnostic decision changed")


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
        raise FileExistsError("Winner-v23 diagnostic result is already imported")
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
        raise ValueError("Winner-v23 diagnostic raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"))
    validate_result(result)
    payload = dict(result)
    payload["repository_attribution"] = {
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
    validate_result(payload)
    OUTPUT_JSON.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v23 negative-X response-use diagnostic result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Classification: `{payload['classification']}`",
                f"- Decision: `{payload['decision']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Paired cells / unchanged-physics rollouts: `20 / 40`",
                f"- Encoded / predictor / action-use cells: `{payload['aggregate']['response_encoded_early_cells']} / {payload['aggregate']['predictor_beats_constant_both_signs_early_cells']} / {payload['aggregate']['response_used_by_action_early_cells']}`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This result authorizes only the one CPU contract selected by the frozen",
                "decision tree. It is not training, deployment selection, or robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["classification"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
