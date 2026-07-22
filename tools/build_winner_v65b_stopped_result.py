#!/usr/bin/env python3
"""Record the fail-closed Winner-v65b count-575 boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CONTRACT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_preregistration.json"
OUTPUT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"
MARKDOWN = ANALYSIS / "WINNER_V65B_ISOLATED_PERSISTENT_TEACHER_STOPPED_RESULT_20260722.md"
CONTRACT_SHA256 = "03ef8930a7fed9bbd3c0fa2119c60a7fecd0e91f1aa53e6b1f9e472b02f504b4"
SOURCE_COUNT = 555
FIRST_COUNT = 556
LAST_DURABLE_COUNT = 574
FAILED_ATTEMPT_COUNT = 575
EXPECTED_COUNTS = tuple(range(FIRST_COUNT, LAST_DURABLE_COUNT + 1))

sys.path.insert(0, str(ROOT / "patches"))
import winner_v22_normalized_predictor_v2 as v22v2  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def snapshot_name(count: int) -> str:
    return f"snapshot_isolated_persistent_teacher_update_{count:03d}.npz"


def metadata_exact(metadata: Mapping[str, Any], count: int) -> bool:
    objective = metadata.get("objective", {})
    return bool(
        metadata.get("schema_version")
        == "winner_v21.predictor_preserving_snapshot.v1"
        and metadata.get("stage") == "isolated_persistent_teacher_joint_stage2"
        and metadata.get("completed_updates") == count
        and metadata.get("source_completed_updates") == SOURCE_COUNT
        and metadata.get("root_seed") == 120120
        and metadata.get("learning_rate") == 0.0001
        and metadata.get("formal_support_cells") == 0
        and metadata.get("locomotion_steps") == 0
        and metadata.get("robot_or_rdk_access") == 0
        and objective.get("update_gradient")
        == "full_action_persistent_teacher_only"
        and objective.get("attention_or_flat_transport_added") is False
        and objective.get("coefficient_or_length_search") is False
    )


def collect_snapshots(work_root: Path) -> list[dict[str, Any]]:
    snapshots = work_root / "snapshots"
    graphs = work_root / "graphs"
    if not snapshots.is_dir() or not graphs.is_dir():
        raise ValueError("Winner-v65b work-root schema changed")
    actual = sorted(path.name for path in snapshots.glob("*.npz"))
    expected = [snapshot_name(count) for count in EXPECTED_COUNTS]
    if actual != expected:
        raise ValueError(f"Winner-v65b durable snapshot range changed: {actual!r}")
    if any(graphs.iterdir()):
        raise ValueError("Winner-v65b unexpectedly exported an endpoint graph")
    receipts: list[dict[str, Any]] = []
    for count, name in zip(EXPECTED_COUNTS, expected, strict=True):
        path = snapshots / name
        loaded = v22v2.load_snapshot(path)
        with np.load(path, allow_pickle=False) as archive:
            raw_metadata = json.loads(str(archive["metadata_json"].item()))
        if (
            int(np.asarray(loaded["optimizer"]["count"])) != count
            or not metadata_exact(loaded["metadata"], count)
            or raw_metadata.get("state_payload_sha256") is None
            or raw_metadata.get("metadata_payload_sha256") is None
        ):
            raise ValueError(f"Winner-v65b snapshot {count} readback changed")
        receipts.append(
            {
                "completed_updates": count,
                "path": path.resolve().as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "state_payload_sha256": raw_metadata["state_payload_sha256"],
                "metadata_payload_sha256": raw_metadata[
                    "metadata_payload_sha256"
                ],
            }
        )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v65b result: {path}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        sha256(CONTRACT) != CONTRACT_SHA256
        or contract.get("status")
        != "PREREGISTERED_WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING"
        or contract.get("frozen_training", {}).get("source_completed_updates")
        != SOURCE_COUNT
        or contract.get("frozen_training", {}).get("persistent_checkpoints")
        != {"half": 605, "final": 655}
        or contract.get("v65b", {}).get("replacement_count") != 1
    ):
        raise ValueError("Winner-v65b frozen contract changed")
    receipts = collect_snapshots(args.work_root)
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "stopped_result_builder": Path(
                "tools/build_winner_v65b_stopped_result.py"
            ),
            "stopped_result_tests": Path(
                "tests/test_winner_v65b_stopped_result.py"
            ),
            "v65b_runner": Path(
                "tools/run_winner_v65b_preregistration_path_correction.py"
            ),
            "v65b_contract": Path(
                "outputs/analysis/winner_v65b_isolated_persistent_teacher_training_preregistration.json"
            ),
        }.items()
    }
    checks = {
        "frozen_v65b_contract_exact": True,
        "durable_snapshot_counts_556_through_574_exact": len(receipts)
        == len(EXPECTED_COUNTS)
        and [item["completed_updates"] for item in receipts]
        == list(EXPECTED_COUNTS),
        "all_durable_snapshots_round_trip_with_exact_optimizer_counts": True,
        "attempted_count_575_not_persisted": not (
            args.work_root / "snapshots" / snapshot_name(FAILED_ATTEMPT_COUNT)
        ).exists(),
        "half_and_final_endpoints_not_reached": LAST_DURABLE_COUNT < 605,
        "no_endpoint_graph_exported": not any((args.work_root / "graphs").iterdir()),
        "formal_support_deployment_gate5_robot_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v65b stopped evidence invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v65b.isolated_persistent_teacher_stopped_result.v1",
        "status": "STOPPED_WINNER_V65B_STRICT_DESCENT_AT_575",
        "decision": "PREREGISTER_WINNER_V66_FAILED_STEP_ATTRIBUTION_ONLY",
        "source": {
            "commit": "269b0858",
            "contract": {
                "path": CONTRACT.relative_to(ROOT).as_posix(),
                "bytes": CONTRACT.stat().st_size,
                "sha256": sha256(CONTRACT),
            },
        },
        "execution": {
            "source_optimizer_count": SOURCE_COUNT,
            "planned_optimizer_updates": 100,
            "successful_optimizer_updates": len(receipts),
            "last_durable_optimizer_count": LAST_DURABLE_COUNT,
            "failed_attempt_optimizer_count": FAILED_ATTEMPT_COUNT,
            "exception": (
                "ValueError: Winner-v65 same-batch teacher loss did not decrease "
                "at 575"
            ),
            "half_endpoint_605_produced": False,
            "final_endpoint_655_produced": False,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifacts": {
            "work_root": args.work_root.resolve().as_posix(),
            "snapshots": receipts,
            "snapshot_manifest_sha256": canonical_sha256(receipts),
            "graphs": [],
        },
        "checks": checks,
        "failed_checks": [],
        "stop_reason": {
            "invariant": "every update strictly reduces its own frozen same-batch persistent-teacher loss",
            "classification": "UNATTRIBUTED_STRICT_DESCENT_FAILURE",
            "retry_or_tuning_authorized": False,
        },
        "authority": {
            "next": "one zero-update fixed-batch attribution at source count 574",
            "attention_or_flat_transport_selected": False,
            "support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v65b stopped result",
                "",
                "- Status: `STOPPED_WINNER_V65B_STRICT_DESCENT_AT_575`",
                "- Durable optimizer counts: `556..574` (`19` updates)",
                "- Failed attempted count: `575`",
                "- Half/final endpoints `605/655`: `NOT_REACHED`",
                "- Endpoint ONNX graphs / support cells / deployment / robot: `0 / 0 / 0 / 0`",
                "- Next authority: one zero-update failed-step attribution only",
                f"- Snapshot manifest SHA-256: `{result['artifacts']['snapshot_manifest_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
