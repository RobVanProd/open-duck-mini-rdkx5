#!/usr/bin/env python3
"""Record the fail-closed Winner-v68 count-602 boundary."""

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
CONTRACT = ANALYSIS / "winner_v68_backtracked_adam_continuation_preregistration.json"
OUTPUT = ANALYSIS / "winner_v68_backtracked_adam_continuation_result.json"
MARKDOWN = ANALYSIS / "WINNER_V68_BACKTRACKED_ADAM_STOPPED_RESULT_20260722.md"
CONTRACT_SHA256 = "3482da83fef4ed3712da6f5cf9214e84fbc3710a05d6bdc6699dd84d30a68714"
SOURCE_COUNT = 575
FIRST_COUNT = 576
LAST_DURABLE_COUNT = 601
FAILED_ATTEMPT_COUNT = 602
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
    return f"snapshot_backtracked_adam_update_{count:03d}.npz"


def metadata_exact(metadata: Mapping[str, Any], count: int) -> bool:
    objective = metadata.get("objective", {})
    return bool(
        metadata.get("schema_version")
        == "winner_v21.predictor_preserving_snapshot.v1"
        and metadata.get("stage") == "backtracked_persistent_teacher_joint_stage2"
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
    )


def collect_snapshots(work_root: Path) -> list[dict[str, Any]]:
    snapshots = work_root / "snapshots"
    graphs = work_root / "graphs"
    if not snapshots.is_dir() or not graphs.is_dir():
        raise ValueError("Winner-v68 work-root schema changed")
    actual = sorted(path.name for path in snapshots.glob("*.npz"))
    expected = [snapshot_name(count) for count in EXPECTED_COUNTS]
    if actual != expected:
        raise ValueError(f"Winner-v68 durable snapshot range changed: {actual!r}")
    if any(graphs.iterdir()):
        raise ValueError("Winner-v68 unexpectedly exported an endpoint graph")
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
            raise ValueError(f"Winner-v68 snapshot {count} readback changed")
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
            raise FileExistsError(f"refusing to overwrite Winner-v68 result: {path}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        sha256(CONTRACT) != CONTRACT_SHA256
        or contract.get("status")
        != "PREREGISTERED_WINNER_V68_BACKTRACKED_ADAM_CONTINUATION"
        or contract.get("frozen_training", {}).get("source_completed_updates")
        != SOURCE_COUNT
        or contract.get("frozen_training", {}).get("persistent_checkpoints")
        != {"half": 605, "final": 655}
    ):
        raise ValueError("Winner-v68 frozen contract changed")
    receipts = collect_snapshots(args.work_root)
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "stopped_result_builder": Path("tools/build_winner_v68_stopped_result.py"),
            "stopped_result_tests": Path("tests/test_winner_v68_stopped_result.py"),
            "v68_runner": Path("tools/run_winner_v68_backtracked_adam_continuation.py"),
            "v68_contract": Path(
                "outputs/analysis/winner_v68_backtracked_adam_continuation_preregistration.json"
            ),
        }.items()
    }
    checks = {
        "frozen_v68_contract_exact": True,
        "durable_snapshot_counts_576_through_601_exact": len(receipts)
        == len(EXPECTED_COUNTS)
        and [item["completed_updates"] for item in receipts]
        == list(EXPECTED_COUNTS),
        "all_durable_snapshots_round_trip_with_exact_optimizer_counts": True,
        "accepted_fraction_history_not_claimed_from_absent_snapshot_metadata": True,
        "attempted_count_602_not_persisted": not (
            args.work_root / "snapshots" / snapshot_name(FAILED_ATTEMPT_COUNT)
        ).exists(),
        "half_and_final_endpoints_not_reached": LAST_DURABLE_COUNT < 605,
        "no_endpoint_graph_exported": not any((args.work_root / "graphs").iterdir()),
        "formal_support_deployment_gate5_robot_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v68 stopped evidence invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v68.backtracked_adam_stopped_result.v1",
        "status": "STOPPED_WINNER_V68_BACKTRACKING_GRID_EXHAUSTED_AT_602",
        "decision": "PREREGISTER_WINNER_V69_COUNT_602_DIRECTION_ATTRIBUTION_ONLY",
        "source": {
            "commit": "29b93993",
            "contract": {
                "path": CONTRACT.relative_to(ROOT).as_posix(),
                "bytes": CONTRACT.stat().st_size,
                "sha256": sha256(CONTRACT),
            },
        },
        "execution": {
            "source_optimizer_count": SOURCE_COUNT,
            "planned_optimizer_updates": 80,
            "successful_optimizer_updates": len(receipts),
            "last_durable_optimizer_count": LAST_DURABLE_COUNT,
            "failed_attempt_optimizer_count": FAILED_ATTEMPT_COUNT,
            "exception": (
                "ValueError: Winner-v68 backtracking found no strict descent at 602"
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
            "accepted_fraction_history": "NOT_PERSISTED_BEFORE_RESULT_STOP",
            "graphs": [],
        },
        "checks": checks,
        "failed_checks": [],
        "stop_reason": {
            "invariant": "one frozen backtracking fraction must strictly reduce same-batch teacher loss",
            "classification": "UNATTRIBUTED_BACKTRACKING_GRID_EXHAUSTION",
            "grid": [1.0, 0.5, 0.25, 0.125, 0.0625],
            "retry_or_grid_extension_authorized": False,
        },
        "authority": {
            "next": "one zero-update count-602 direction and plateau attribution",
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
                "# Winner-v68 stopped result",
                "",
                "- Status: `STOPPED_WINNER_V68_BACKTRACKING_GRID_EXHAUSTED_AT_602`",
                "- Durable optimizer counts: `576..601` (`26` updates)",
                "- Failed attempted count: `602`",
                "- Half/final endpoints `605/655`: `NOT_REACHED`",
                "- Endpoint ONNX / support / deployment / robot: `0 / 0 / 0 / 0`",
                "- Accepted-fraction history: `NOT_PERSISTED_BEFORE_RESULT_STOP`",
                "- Next authority: one zero-update count-602 direction/plateau attribution",
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
