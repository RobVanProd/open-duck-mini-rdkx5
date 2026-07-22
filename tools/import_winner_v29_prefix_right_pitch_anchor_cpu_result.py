#!/usr/bin/env python3
"""Strictly import the sole Winner-v29 prefix-anchor CPU-proof artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_contract.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
RUNNER = ROOT / "tools/run_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"
WORKFLOW = ROOT / ".github/workflows/winner-v29-prefix-right-pitch-anchor-cpu-contract.yml"
OUTPUT_JSON = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
OUTPUT_MD = ANALYSIS / "WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_RESULT_20260722.md"
RAW_RESULT_NAME = "winner-v29-prefix-right-pitch-anchor-cpu-result.json"
RAW_RECEIPT_NAME = "winner-v29-prefix-right-pitch-anchor-cpu-result.sha256"
EXPECTED_REPOSITORY = "RobVanProd/open-duck-mini-rdkx5"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_RESULT_BYTES = 32 * 1024 * 1024


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


def read_artifact(path: Path) -> tuple[bytes, bytes]:
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = [PurePosixPath(item.filename).as_posix() for item in members]
        if sorted(names) != sorted((RAW_RESULT_NAME, RAW_RECEIPT_NAME)):
            raise ValueError(f"Winner-v29 artifact inventory changed: {names}")
        for item in members:
            member = PurePosixPath(item.filename)
            if (
                member.is_absolute()
                or ".." in member.parts
                or item.is_dir()
                or item.file_size > MAX_RESULT_BYTES
                or item.compress_size > MAX_RESULT_BYTES
            ):
                raise ValueError("Winner-v29 artifact contains unsafe member")
        return archive.read(RAW_RESULT_NAME), archive.read(RAW_RECEIPT_NAME)


def validate_result(value: Mapping[str, Any]) -> None:
    expected_fields = {
        "authority",
        "checks",
        "decision",
        "environment",
        "execution",
        "failed_checks",
        "objective_evidence",
        "rollout_evidence",
        "schema_version",
        "source_identity",
        "source_manifest_sha256",
        "sources",
        "status",
    }
    if set(value) not in (expected_fields, expected_fields | {"repository_attribution"}):
        raise ValueError("Winner-v29 result field inventory changed")
    if (
        value.get("schema_version")
        != "winner_v29.prefix_right_pitch_anchor_cpu_result.v1"
        or value.get("status")
        != "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_PREREGISTRATION_ONLY"
        or value.get("failed_checks") != []
    ):
        raise ValueError("Winner-v29 result did not pass the frozen contract")
    checks = value.get("checks")
    if (
        not isinstance(checks, Mapping)
        or not checks
        or not all(item is True for item in checks.values())
    ):
        raise ValueError("Winner-v29 checks changed")
    if value.get("execution") != {
        "rollout_episode_slots": 80,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v29 execution boundary changed")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        value.get("sources") != prereg["sources"]
        or value.get("source_manifest_sha256") != prereg["source_manifest_sha256"]
        or value.get("source_identity")
        != {
            "winner_v22_snapshot": prereg["artifact_inputs"]["winner_v22_training"][
                "source_snapshot"
            ],
            "winner_v22_graph": prereg["artifact_inputs"]["winner_v22_training"][
                "source_graph"
            ],
            "winner_v24_final_snapshot": prereg["artifact_inputs"][
                "winner_v24_training"
            ]["final"]["snapshot"],
            "winner_v24_final_graph": prereg["artifact_inputs"]["winner_v24_training"][
                "final"
            ]["graph"],
        }
    ):
        raise ValueError("Winner-v29 source identity changed")
    rollout = value.get("rollout_evidence", {})
    if (
        rollout.get("rollout_update_index") != 200
        or rollout.get("episode_slots") != 80
        or rollout.get("selected_configuration_ids")
        != prereg["objective"]["selected_training_configuration_ids"]
        or rollout.get("selected_episode_slots") != 16
        or rollout.get("prefix_ticks") != list(range(8))
        or rollout.get("action_indices") != [11, 12, 13]
        or rollout.get("selected_elements") != 384
        or HEX64.fullmatch(str(rollout.get("episode_receipts_sha256"))) is None
        or HEX64.fullmatch(str(rollout.get("anchor_mask_sha256"))) is None
        or HEX64.fullmatch(str(rollout.get("observations_sha256"))) is None
        or HEX64.fullmatch(str(rollout.get("previous_actions_sha256"))) is None
        or not isinstance(rollout.get("transition_hashes"), Mapping)
        or not rollout["transition_hashes"]
        or not all(
            HEX64.fullmatch(str(item)) is not None
            for item in rollout["transition_hashes"].values()
        )
    ):
        raise ValueError("Winner-v29 rollout evidence changed")
    objective = value.get("objective_evidence", {})
    balance = objective.get("balance", {})
    graph = objective.get("graph_replay", {})
    if (
        not math.isfinite(float(objective.get("raw_anchor_loss", math.nan)))
        or float(objective["raw_anchor_loss"]) <= 0.0
        or not math.isfinite(float(objective.get("anchor_scale", math.nan)))
        or float(objective["anchor_scale"]) <= 0.0
        or objective.get("gradient_balance_keys")
        != prereg["objective"]["gradient_balance_keys"]
        or float(objective.get("frozen_predictor_scale", math.nan))
        != 380.9135437011719
        or not isinstance(balance, Mapping)
        or float(balance.get("anchor_scale", math.nan)) != float(objective["anchor_scale"])
        or abs(
            float(balance.get("scaled_anchor_policy_gradient_rms", math.nan))
            - float(balance.get("baseline_policy_gradient_rms", math.nan))
        )
        / float(balance.get("baseline_policy_gradient_rms", math.nan))
        > 2.0e-6
        or graph.get("rows") != 128
        or set(graph.get("maximum_abs_error", {}))
        != {"source_action", "source_hidden", "candidate_action", "candidate_hidden"}
        or max(float(item) for item in graph["maximum_abs_error"].values()) > 1.0e-7
    ):
        raise ValueError("Winner-v29 objective evidence changed")
    if value.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "one_update_authorized": False,
        "runtime_implementation_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "one separately preregistered CPU-only one-update proof using the exact "
            "recorded anchor scale"
        ),
    }:
        raise ValueError("Winner-v29 authority changed")
    if "repository_attribution" in value:
        item = value["repository_attribution"]
        if (
            not isinstance(item, Mapping)
            or item.get("repository") != EXPECTED_REPOSITORY
            or item.get("github_run_attempt") != 1
            or HEX40.fullmatch(str(item.get("github_run_head_sha"))) is None
            or HEX64.fullmatch(str(item.get("artifact_zip_sha256"))) is None
            or item.get("github_artifact_digest")
            != f"sha256:{item.get('artifact_zip_sha256')}"
            or item.get("preregistration_lf_sha256") != lf_sha256(PREREGISTRATION)
            or item.get("runner_lf_sha256") != lf_sha256(RUNNER)
            or item.get("workflow_lf_sha256") != lf_sha256(WORKFLOW)
            or item.get("importer_lf_sha256") != lf_sha256(Path(__file__))
        ):
            raise ValueError("Winner-v29 repository attribution changed")


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
        raise FileExistsError("Winner-v29 result is already imported")
    zip_sha = sha256(args.artifact_zip)
    expected_name = f"winner-v29-prefix-right-pitch-anchor-cpu-contract-{args.run_id}"
    if (
        args.run_id <= 0
        or args.run_attempt != 1
        or HEX40.fullmatch(args.run_head_sha) is None
        or args.artifact_id <= 0
        or args.artifact_name != expected_name
        or HEX64.fullmatch(zip_sha) is None
        or args.artifact_digest != f"sha256:{zip_sha}"
    ):
        raise ValueError("Winner-v29 repository attribution changed")
    raw_bytes, receipt_bytes = read_artifact(args.artifact_zip)
    raw_sha = sha256_bytes(raw_bytes)
    if receipt_bytes != f"{raw_sha}  /tmp/{RAW_RESULT_NAME}\n".encode():
        raise ValueError("Winner-v29 raw-result receipt changed")
    raw = json.loads(raw_bytes.decode("utf-8"), parse_constant=reject_nonfinite)
    validate_result(raw)
    result = dict(raw)
    result["repository_attribution"] = {
        "repository": EXPECTED_REPOSITORY,
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "github_run_head_sha": args.run_head_sha,
        "github_artifact_id": args.artifact_id,
        "github_artifact_name": args.artifact_name,
        "github_artifact_digest": args.artifact_digest,
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
                "# Winner-v29 prefix right-pitch anchor CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Anchor scale: `{result['objective_evidence']['anchor_scale']}`",
                f"- GitHub run / artifact: `{args.run_id}` / `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{zip_sha}`",
                "- Rollout slots / optimizer updates: `80 / 0`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                "A pass authorizes only a separately preregistered one-update CPU proof.",
                "It does not authorize training, checkpoint selection, deployment, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"ANCHOR_SCALE={result['objective_evidence']['anchor_scale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
