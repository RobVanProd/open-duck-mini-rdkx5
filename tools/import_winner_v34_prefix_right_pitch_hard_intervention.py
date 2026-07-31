#!/usr/bin/env python3
"""Safely import the sole Winner-v34 direct prefix intervention result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_preregistration.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_TRAINING = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
RUNNER = ROOT / "tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"
WORKFLOW = ROOT / ".github/workflows/winner-v34-prefix-right-pitch-hard-intervention.yml"
OUTPUT_JSON = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v34-prefix-right-pitch-hard-intervention-result.json"
RAW_RECEIPT_NAME = "winner-v34-prefix-right-pitch-hard-intervention-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
CONFIGURATION_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_07",
    "HELDOUT_09",
    "HELDOUT_15",
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
CHECKPOINTS = (("half", 251), ("final", 301))
ARMS = ("CONTROL", "RIGHT_PITCH_REPLACED")
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
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
            raise ValueError("Winner-v34 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v34 artifact exceeds size ceiling")
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
                raise ValueError("Winner-v34 artifact has unsafe member")
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
    require_sha256(artifact_zip_sha256, "Winner-v34 artifact")
    if (
        run_id <= 0
        or run_attempt != 1
        or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v34-prefix-right-pitch-hard-intervention-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v34 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _expected_source_graph_sha256() -> str:
    source = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    value = next(
        row["graph"]["sha256"]
        for row in source["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    require_sha256(value, "Winner-v34 source graph")
    return value


def _validate_row(row: Mapping[str, Any]) -> None:
    expected_fields = {
        "configuration_id",
        "configuration_sha256",
        "plant",
        "condition",
        "arm",
        "replaced_action_indices",
        "replacement_ticks",
        "maximum_replaced_action_delta",
        "named_action_changed",
        "all_realized_actions_bounded",
        "terminal",
        "episode",
        "support_pass",
        "previous_action_chain_exact",
        "maximum_jax_onnx_hidden_error",
        "learned_normalized_prediction_mse",
        "constant_normalized_prediction_mse",
        "final_h_out",
        "trace_hashes",
        "checkpoint",
        "checkpoint_update",
        "original_v33_support_pass",
        "original_v33_terminal_tick",
        "control_replays_v33_exactly",
        "control_maximum_scalar_abs_difference",
    }
    if set(row) != expected_fields:
        raise ValueError("Winner-v34 cell schema changed")
    if (
        row["configuration_id"] not in CONFIGURATION_IDS
        or row["plant"] not in PLANTS
        or row["arm"] not in ARMS
        or (row["checkpoint"], row["checkpoint_update"]) not in CHECKPOINTS
        or row["condition"] is not None
        or type(row["support_pass"]) is not bool
        or type(row["original_v33_support_pass"]) is not bool
        or type(row["control_replays_v33_exactly"]) is not bool
        or not isinstance(row["control_maximum_scalar_abs_difference"], (int, float))
        or row["control_maximum_scalar_abs_difference"] < 0.0
        or len(row["final_h_out"]) != 64
    ):
        raise ValueError("Winner-v34 cell identity or type changed")
    expected_indices = [] if row["arm"] == "CONTROL" else [11, 12, 13]
    expected_ticks = 0 if row["arm"] == "CONTROL" else 8
    if (
        row["replaced_action_indices"] != expected_indices
        or row["replacement_ticks"] != expected_ticks
    ):
        raise ValueError("Winner-v34 cell intervention changed")
    hashes = row["trace_hashes"]
    if set(hashes) != {
        "observations",
        "actions",
        "candidate_actions",
        "predictions",
        "hidden",
    }:
        raise ValueError("Winner-v34 cell trace inventory changed")
    for name, value in hashes.items():
        require_sha256(value, f"Winner-v34 {name} trace")


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version",
        "status",
        "classification",
        "decision",
        "checks",
        "failed_checks",
        "configuration_ids",
        "candidate_checkpoints",
        "source_checkpoint",
        "arms",
        "replacement_ticks",
        "cell_results",
        "summary",
        "execution",
        "sources",
        "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields),
        frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != (
        "winner_v34.prefix_right_pitch_hard_intervention_result.v1"
    ):
        raise ValueError("Winner-v34 result schema changed")
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
            != f"winner-v34-prefix-right-pitch-hard-intervention-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
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
            or attribution["preregistration_lf_sha256"] != lf_sha256(PREREGISTRATION)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["runner_lf_sha256"] != lf_sha256(RUNNER)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v34 imported attribution changed")
    if result.get("configuration_ids") != list(CONFIGURATION_IDS):
        raise ValueError("Winner-v34 configuration set changed")
    if result.get("candidate_checkpoints") != [
        {"label": label, "update": update} for label, update in CHECKPOINTS
    ] or result.get("source_checkpoint") != {
        "label": "winner_v22_final",
        "update": 100,
        "onnx_sha256": _expected_source_graph_sha256(),
    }:
        raise ValueError("Winner-v34 checkpoint identity changed")
    if result.get("arms") != {
        "CONTROL": [],
        "RIGHT_PITCH_REPLACED": [11, 12, 13],
    } or result.get("replacement_ticks") != list(range(8)):
        raise ValueError("Winner-v34 intervention identity changed")
    if result.get("execution") != {
        "control_cells": 60,
        "replacement_cells": 60,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "runtime_action_wrapper_authorized": False,
        "pass_authorizes_only": "one separately frozen CPU objective contract",
    }:
        raise ValueError("Winner-v34 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
        "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
        "winner_v22_training_result_lf_sha256": lf_sha256(V22_TRAINING),
        "winner_v32_training_result_lf_sha256": lf_sha256(V32_TRAINING),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v34 result sources changed")
    rows = result.get("cell_results")
    if not isinstance(rows, list) or len(rows) != 120:
        raise ValueError("Winner-v34 cell count changed")
    for row in rows:
        _validate_row(row)
    identities = [
        (row["checkpoint"], row["configuration_id"], row["plant"], row["arm"])
        for row in rows
    ]
    expected = [
        (label, configuration, plant, arm)
        for label, _ in CHECKPOINTS
        for configuration in CONFIGURATION_IDS
        for plant in PLANTS
        for arm in ARMS
    ]
    if identities != expected or len(set(identities)) != 120:
        raise ValueError("Winner-v34 cell matrix changed")
    controls = [row for row in rows if row["arm"] == "CONTROL"]
    replacements = [row for row in rows if row["arm"] == "RIGHT_PITCH_REPLACED"]
    failing = [row for row in replacements if not row["original_v33_support_pass"]]
    passing = [row for row in replacements if row["original_v33_support_pass"]]
    derived_checks = {
        "exact_120_cells": len(rows) == 120,
        "exact_60_control_cells": len(controls) == 60,
        "exact_60_replacement_cells": len(replacements) == 60,
        "all_60_control_cells_replay_v33_exactly": all(
            row["control_replays_v33_exactly"] for row in controls
        ),
        "every_replacement_cell_changes_a_named_action": all(
            row["named_action_changed"] for row in replacements
        ),
        "all_realized_actions_obey_graph_boundary": all(
            row["all_realized_actions_bounded"] for row in rows
        ),
        "all_candidate_previous_action_outputs_exact": all(
            row["previous_action_chain_exact"] for row in rows
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            row["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for row in rows
        ),
        "all_60_replacement_cells_pass_support": all(
            row["support_pass"] for row in replacements
        ),
        "all_originally_failing_cells_recovered": bool(failing)
        and all(row["support_pass"] for row in failing),
        "all_originally_passing_cells_remain_passing": bool(passing)
        and all(row["support_pass"] for row in passing),
    }
    if result.get("checks") != derived_checks:
        raise ValueError("Winner-v34 checks are not rederived")
    summary = {
        "control_passes": sum(row["support_pass"] for row in controls),
        "replacement_passes": sum(row["support_pass"] for row in replacements),
        "originally_failing_cells": len(failing),
        "originally_failing_recovered": sum(row["support_pass"] for row in failing),
        "originally_passing_cells": len(passing),
        "originally_passing_preserved": sum(row["support_pass"] for row in passing),
        "maximum_replaced_action_delta": max(
            row["maximum_replaced_action_delta"] for row in replacements
        ),
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v34 summary is not rederived")
    validity_names = {
        "exact_120_cells",
        "exact_60_control_cells",
        "exact_60_replacement_cells",
        "all_60_control_cells_replay_v33_exactly",
        "every_replacement_cell_changes_a_named_action",
        "all_realized_actions_obey_graph_boundary",
        "all_candidate_previous_action_outputs_exact",
        "all_jax_onnx_hidden_errors_at_most_1e_7",
    }
    efficacy_names = set(derived_checks) - validity_names
    valid = all(derived_checks[name] for name in validity_names)
    passed = valid and all(derived_checks[name] for name in efficacy_names)
    if not valid:
        expected_status = "INVALID_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        expected_classification = "INVALID_DIRECT_PREFIX_INTERVENTION"
        expected_decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        expected_status = "PASS_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        expected_classification = "DIRECT_PREFIX_RIGHT_PITCH_REPLACEMENT_FULL_SUPPORT_RECOVERY"
        expected_decision = "AUTHORIZE_HARD_PREFIX_MECHANISM_OBJECTIVE_PREREGISTRATION_ONLY"
    else:
        expected_status = "HOLD_WINNER_V34_PREFIX_RIGHT_PITCH_HARD_INTERVENTION"
        expected_classification = "NO_FULL_DIRECT_PREFIX_SUPPORT_RECOVERY"
        expected_decision = "CLOSE_RIGHT_PITCH_PREFIX_REPLACEMENT_MECHANISM"
    if (
        result.get("failed_checks")
        != sorted(name for name, passed_value in derived_checks.items() if not passed_value)
        or result.get("status") != expected_status
        or result.get("classification") != expected_classification
        or result.get("decision") != expected_decision
    ):
        raise ValueError("Winner-v34 decision changed")


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
        raise FileExistsError("Winner-v34 result is already imported")
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
        raise ValueError("Winner-v34 raw-result receipt changed")
    result = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
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
    summary = payload["summary"]
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Winner-v34 direct right-pitch prefix intervention result",
                "",
                f"- Status: `{payload['status']}`",
                f"- Classification: `{payload['classification']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Control replay: `{payload['checks']['all_60_control_cells_replay_v33_exactly']}`",
                f"- Replacement support passes: `{summary['replacement_passes']} / 60`",
                (
                    "- Original failures recovered: "
                    f"`{summary['originally_failing_recovered']} / "
                    f"{summary['originally_failing_cells']}`"
                ),
                (
                    "- Original passes preserved: "
                    f"`{summary['originally_passing_preserved']} / "
                    f"{summary['originally_passing_cells']}`"
                ),
                "- Optimizer / locomotion training / robot: `0 / 0 / 0`",
                "",
                "This is a zero-update causal diagnostic. It does not authorize a runtime",
                "action wrapper, checkpoint selection, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
