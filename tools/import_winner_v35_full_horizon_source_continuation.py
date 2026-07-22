#!/usr/bin/env python3
"""Safely import the sole Winner-v35 full-horizon source-continuation result."""

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
PREREGISTRATION = ANALYSIS / "winner_v35_full_horizon_source_continuation_preregistration.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V34_RESULT = ANALYSIS / "winner_v34_prefix_right_pitch_hard_intervention_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_TRAINING = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
RUNNER = ROOT / "tools/run_winner_v35_full_horizon_source_continuation.py"
WORKFLOW = ROOT / ".github/workflows/winner-v35-full-horizon-source-continuation.yml"
OUTPUT_JSON = ANALYSIS / "winner_v35_full_horizon_source_continuation_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v35-full-horizon-source-continuation-result.json"
RAW_RECEIPT_NAME = "winner-v35-full-horizon-source-continuation-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
CONFIGURATION_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
CHECKPOINTS = (("half", 251), ("final", 301))
HEX40_RE = re.compile(r"[0-9a-f]{40}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
ATTRIBUTION_FIELDS = {
    "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
    "github_artifact_id", "github_artifact_name", "github_artifact_digest",
    "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
    "raw_result_receipt_sha256", "preregistration_lf_sha256",
    "workflow_lf_sha256", "runner_lf_sha256", "importer_lf_sha256",
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
            raise ValueError("Winner-v35 artifact inventory changed")
        if sum(item.file_size for item in infos) > 100_000_000:
            raise ValueError("Winner-v35 artifact exceeds size ceiling")
        for info in infos:
            member = PurePosixPath(info.filename)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                member.is_absolute() or ".." in member.parts or "." in member.parts
                or "\\" in info.filename or info.flag_bits & 1 or info.is_dir()
                or file_type == stat.S_IFLNK or file_type not in {0, stat.S_IFREG}
            ):
                raise ValueError("Winner-v35 artifact has unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def repository_attribution(
    *, run_id: int, run_attempt: int, run_head_sha: str, artifact_id: int,
    artifact_name: str, artifact_digest: str, artifact_zip_sha256: str,
) -> dict[str, Any]:
    require_sha256(artifact_zip_sha256, "Winner-v35 artifact")
    if (
        run_id <= 0 or run_attempt != 1 or HEX40_RE.fullmatch(run_head_sha) is None
        or artifact_id <= 0
        or artifact_name != f"winner-v35-full-horizon-source-continuation-{run_id}"
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("Winner-v35 workflow attribution changed")
    return {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def _source_graph_sha256() -> str:
    source = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    value = next(
        row["graph"]["sha256"] for row in source["persistent_checkpoints"]
        if row["label"] == "final" and row["update"] == 100
    )
    require_sha256(value, "Winner-v35 source graph")
    return value


def _validate_row(row: Mapping[str, Any]) -> None:
    fields = {
        "configuration_id", "configuration_sha256", "plant",
        "prefix_replaced_action_indices", "prefix_ticks",
        "source_continuation_first_tick", "maximum_prefix_replaced_action_delta",
        "tick8_handoff_action_delta", "tick8_handoff_changes_action",
        "all_actions_bounded", "terminal", "episode", "support_pass",
        "trace_hashes", "checkpoint", "checkpoint_update", "v34_support_pass",
        "v34_terminal_tick",
    }
    if set(row) != fields:
        raise ValueError("Winner-v35 cell schema changed")
    if (
        row["configuration_id"] not in CONFIGURATION_IDS
        or row["plant"] not in PLANTS
        or (row["checkpoint"], row["checkpoint_update"]) not in CHECKPOINTS
        or row["prefix_replaced_action_indices"] != [11, 12, 13]
        or row["prefix_ticks"] != 8
        or row["source_continuation_first_tick"] != 8
        or type(row["support_pass"]) is not bool
        or type(row["v34_support_pass"]) is not bool
        or type(row["tick8_handoff_changes_action"]) is not bool
        or type(row["all_actions_bounded"]) is not bool
        or not isinstance(row["tick8_handoff_action_delta"], (int, float))
        or row["tick8_handoff_action_delta"] < 0.0
    ):
        raise ValueError("Winner-v35 cell identity or type changed")
    hashes = row["trace_hashes"]
    if set(hashes) != {"observations", "actions", "source_hidden"}:
        raise ValueError("Winner-v35 trace inventory changed")
    for name, value in hashes.items():
        require_sha256(value, f"Winner-v35 {name} trace")


def validate_result(result: Mapping[str, Any]) -> None:
    raw_fields = {
        "schema_version", "status", "classification", "decision", "checks",
        "failed_checks", "configuration_ids", "candidate_checkpoints",
        "source_checkpoint", "cell_results", "summary", "execution", "sources",
        "authority",
    }
    if frozenset(result) not in {
        frozenset(raw_fields), frozenset(raw_fields | {"repository_attribution"}),
    } or result.get("schema_version") != "winner_v35.full_horizon_source_continuation_result.v1":
        raise ValueError("Winner-v35 result schema changed")
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
            != f"winner-v35-full-horizon-source-continuation-{attribution['github_run_id']}"
            or attribution.get("github_artifact_digest")
            != f"sha256:{attribution.get('artifact_zip_sha256')}"
            or any(HEX64_RE.fullmatch(str(attribution.get(name))) is None for name in (
                "artifact_zip_sha256", "raw_result_sha256", "raw_result_receipt_sha256",
                "preregistration_lf_sha256", "workflow_lf_sha256",
                "runner_lf_sha256", "importer_lf_sha256",
            ))
            or attribution["preregistration_lf_sha256"] != lf_sha256(PREREGISTRATION)
            or attribution["workflow_lf_sha256"] != lf_sha256(WORKFLOW)
            or attribution["runner_lf_sha256"] != lf_sha256(RUNNER)
            or attribution["importer_lf_sha256"] != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v35 imported attribution changed")
    if result.get("configuration_ids") != list(CONFIGURATION_IDS):
        raise ValueError("Winner-v35 configuration set changed")
    if result.get("candidate_checkpoints") != [
        {"label": label, "update": update} for label, update in CHECKPOINTS
    ] or result.get("source_checkpoint") != {
        "label": "winner_v22_final", "update": 100, "onnx_sha256": _source_graph_sha256(),
    }:
        raise ValueError("Winner-v35 checkpoint identity changed")
    if result.get("execution") != {
        "hybrid_support_cells": 60, "optimizer_updates": 0,
        "locomotion_training_steps": 0, "robot_or_rdk_access": 0,
    } or result.get("authority") != {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "runtime_hybrid_or_action_wrapper_authorized": False,
        "pass_authorizes_only": "one separately frozen CPU teacher-representation contract",
    }:
        raise ValueError("Winner-v35 execution or authority changed")
    if result.get("sources") != {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "winner_v28_result_lf_sha256": lf_sha256(V28_RESULT),
        "winner_v34_result_lf_sha256": lf_sha256(V34_RESULT),
        "winner_v22_training_result_lf_sha256": lf_sha256(V22_TRAINING),
        "winner_v32_training_result_lf_sha256": lf_sha256(V32_TRAINING),
        "runner_lf_sha256": lf_sha256(RUNNER),
    }:
        raise ValueError("Winner-v35 result sources changed")
    rows = result.get("cell_results")
    if not isinstance(rows, list) or len(rows) != 60:
        raise ValueError("Winner-v35 cell count changed")
    for row in rows:
        _validate_row(row)
    identities = [
        (row["checkpoint"], row["configuration_id"], row["plant"]) for row in rows
    ]
    expected = [
        (label, configuration, plant) for label, _ in CHECKPOINTS
        for configuration in CONFIGURATION_IDS for plant in PLANTS
    ]
    if identities != expected or len(set(identities)) != 60:
        raise ValueError("Winner-v35 cell matrix changed")
    failing = [row for row in rows if not row["v34_support_pass"]]
    passing = [row for row in rows if row["v34_support_pass"]]
    checks = {
        "exact_60_hybrid_cells": len(rows) == 60,
        "every_tick8_handoff_changes_an_action": all(
            row["tick8_handoff_changes_action"] for row in rows
        ),
        "all_actions_obey_graph_boundary": all(row["all_actions_bounded"] for row in rows),
        "all_60_hybrid_cells_pass_support": all(row["support_pass"] for row in rows),
        "all_55_v34_failures_recovered": len(failing) == 55
        and all(row["support_pass"] for row in failing),
        "all_5_v34_passes_preserved": len(passing) == 5
        and all(row["support_pass"] for row in passing),
    }
    if result.get("checks") != checks:
        raise ValueError("Winner-v35 checks are not rederived")
    summary = {
        "hybrid_support_passes": sum(row["support_pass"] for row in rows),
        "v34_failing_cells": len(failing),
        "v34_failures_recovered": sum(row["support_pass"] for row in failing),
        "v34_passing_cells": len(passing),
        "v34_passes_preserved": sum(row["support_pass"] for row in passing),
        "minimum_tick8_handoff_action_delta": min(
            row["tick8_handoff_action_delta"] for row in rows
        ),
        "maximum_tick8_handoff_action_delta": max(
            row["tick8_handoff_action_delta"] for row in rows
        ),
    }
    if result.get("summary") != summary:
        raise ValueError("Winner-v35 summary is not rederived")
    validity = {
        "exact_60_hybrid_cells", "every_tick8_handoff_changes_an_action",
        "all_actions_obey_graph_boundary",
    }
    valid = all(checks[name] for name in validity)
    passed = valid and all(checks[name] for name in set(checks) - validity)
    if not valid:
        status = "INVALID_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "INVALID_SOURCE_CONTINUATION_FEASIBILITY"
        decision = "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
    elif passed:
        status = "PASS_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "FULL_HORIZON_HYBRID_TEACHER_FEASIBLE"
        decision = "AUTHORIZE_HYBRID_TEACHER_REPRESENTATION_CPU_CONTRACT_PREREGISTRATION_ONLY"
    else:
        status = "HOLD_WINNER_V35_FULL_HORIZON_SOURCE_CONTINUATION"
        classification = "HYBRID_TEACHER_NOT_FULL_HORIZON_FEASIBLE"
        decision = "CLOSE_V28_HYBRID_TEACHER_ROUTE"
    if (
        result.get("failed_checks") != sorted(name for name, value in checks.items() if not value)
        or result.get("status") != status or result.get("classification") != classification
        or result.get("decision") != decision
    ):
        raise ValueError("Winner-v35 decision changed")


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
        raise FileExistsError("Winner-v35 result is already imported")
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
        raise ValueError("Winner-v35 raw-result receipt changed")
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
        "\n".join([
            "# Winner-v35 full-horizon source-continuation result", "",
            f"- Status: `{payload['status']}`",
            f"- Classification: `{payload['classification']}`",
            f"- Decision: `{payload['decision']}`",
            f"- Hybrid support passes: `{summary['hybrid_support_passes']} / 60`",
            f"- V34 failures recovered: `{summary['v34_failures_recovered']} / 55`",
            f"- V34 passes preserved: `{summary['v34_passes_preserved']} / 5`",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "This is a feasibility diagnostic. The hybrid itself is not authorized as a",
            "runtime wrapper, deployment policy, or robot policy.", "",
        ]),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
