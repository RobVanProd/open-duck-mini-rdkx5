#!/usr/bin/env python3
"""Preregister the zero-update Winner-v73 update-638 contract attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v73_update638_contract_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION_PREREGISTRATION_20260722.md"
V71B_CONTRACT = ANALYSIS / "winner_v71b_full_loss_binding_correction.json"
WORK_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v71b-fresh-moment-safeguarded-continuation"
)
SOURCE_COUNT = 637
ATTEMPT_COUNT = 638
SOURCE_SNAPSHOT = (
    WORK_ROOT
    / "snapshots"
    / "snapshot_fresh_moment_safeguarded_update_637.npz"
)
SOURCE_GRAPH = WORK_ROOT / "graphs" / "winner_v71_half.onnx"
EXPECTED_SOURCE_SNAPSHOT_SHA256 = (
    "ab653455ee3d79b053d3f242192de02536e838accd5ba872042a959dde231d5b"
)
EXPECTED_SOURCE_GRAPH_SHA256 = (
    "e2b97fe6b18c09c69fd9a9d8a1fe9e39cfa6b2a806f20bd05a215253830d5eab"
)

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v71b_full_loss_binding_correction as v71b  # noqa: E402


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


def replace_exact(source: str, old: str, new: str, *, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v73 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v73 region changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v73.update638_contract_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_UPDATE638_CONTRACT_ATTRIBUTION_ONLY"
        or value.get("diagnostic", {}).get("source_optimizer_count") != 637
        or value.get("diagnostic", {}).get("attempted_optimizer_count") != 638
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v73 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v73 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v73 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v73 source manifest changed")


'''


VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v73 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "fresh_moment_safeguarded_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 602
        or metadata.get("source_snapshot_sha256")
        != "24fd0b25de5cd5e198a61288cff2d6e437e251a63fa1a05213d33d585838ec7b"
        or metadata.get("teacher_snapshot_sha256")
        != "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("accepted_backtracking_fraction") != 1.0
        or metadata.get("moment_reset_applied") is not False
        or metadata.get("reset_moment_keys") != []
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or metadata.get("objective", {}).get("update_gradient")
        != "full_action_persistent_teacher_only"
        or metadata.get("objective", {}).get("attention_or_flat_transport_added") is not False
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v73 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v73 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v73 source target_std is not positive")


'''


SOURCE_EVIDENCE = '''    source_result = preregistration["prior_invocation"]
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status")
        != "STOPPED_WINNER_V71B_REPLAY_TEACHER_CONTRACT_AT_638"
        or source_result.get("last_durable_optimizer_count") != SOURCE_COMPLETED_UPDATES
        or source_result.get("attempted_optimizer_count") != 638
        or source_result.get("result_written") is not False
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v73 source evidence changed")
'''


DIAGNOSTIC = '''        checks = {
            "sampled_hidden_replay_at_most_2e_6": float(
                ppo_metrics["sampled_hidden_replay_max_abs_error"]
            ) <= 2.0e-6,
            "stored_successor_transition_count_exact": int(
                predictor_metrics["stored_successor_transition_count"]
            ) == expected_stored,
            "expected_stored_positive": expected_stored > 0,
            "anchor_selected_elements_exact": int(anchor_metrics["selected_elements"])
            == v29.EXPECTED_ANCHOR_ELEMENTS,
            "teacher_selected_elements_exact": int(teacher_metrics["selected_elements"])
            == selected_elements,
            "teacher_rows_and_elements_exact": selected_rows == 22 and selected_elements > 0,
            "anchor_active_gradient_support_positive": all(
                anchor_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
            ),
            "anchor_nonactive_gradient_support_zero": all(
                anchor_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS
            ),
            "teacher_active_gradient_support_positive": all(
                teacher_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
            ),
            "teacher_nonactive_gradient_support_zero": all(
                teacher_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS
            ),
            "reset_sample_count_exact": int(reset_metrics["sample_count"]) == 44,
            "reset_selected_elements_exact": int(reset_metrics["selected_elements"]) == 616,
            "reset_active_gradient_keys_exact": sorted(
                key for key, value in reset_gradient_max.items() if value > 0.0
            ) == ["action_bias", "action_weight", "hidden_bias", "obs_weight"],
            "reset_nonactive_gradient_support_zero": not any(
                reset_gradient_max[key] != 0.0
                for key in reset_gradient_max
                if key not in {"action_bias", "action_weight", "hidden_bias", "obs_weight"}
            ),
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        if failed_checks == ["sampled_hidden_replay_at_most_2e_6"]:
            classification = "SAMPLED_HIDDEN_REPLAY_TOLERANCE_CROSSED"
            decision = "PREREGISTER_HIDDEN_REPLAY_TOLERANCE_CAUSAL_AUDIT_ONLY"
        elif not failed_checks:
            classification = "V71B_STOP_DID_NOT_REPRODUCE"
            decision = "STOP_REPRODUCTION_MISMATCH"
        else:
            classification = "MULTI_INVARIANT_REPLAY_TEACHER_CONTRACT_CHANGE"
            decision = "STOP_FOR_REVIEW"
        result = {
            "schema_version": "winner_v73.update638_contract_attribution_result.v1",
            "status": "PASS_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION",
            "classification": classification,
            "decision": decision,
            "source": {
                "snapshot": source_receipt,
                "graph": source_graph_receipt,
                "optimizer_count": int(np.asarray(optimizer["count"])),
                "rollout_update_index": rollout_update_index,
                "attempted_optimizer_count": completed_updates,
                "episode_receipts_sha256": episode_hash,
            },
            "contract_values": {
                "sampled_hidden_replay_max_abs_error": float(
                    ppo_metrics["sampled_hidden_replay_max_abs_error"]
                ),
                "sampled_hidden_replay_limit": 2.0e-6,
                "stored_successor_transition_count": int(
                    predictor_metrics["stored_successor_transition_count"]
                ),
                "expected_stored_successor_transition_count": expected_stored,
                "anchor_selected_elements": int(anchor_metrics["selected_elements"]),
                "expected_anchor_selected_elements": int(v29.EXPECTED_ANCHOR_ELEMENTS),
                "teacher_selected_elements": int(teacher_metrics["selected_elements"]),
                "reconstructed_teacher_selected_elements": selected_elements,
                "teacher_selected_rows": selected_rows,
                "anchor_gradient_max": anchor_gradient_max,
                "teacher_gradient_max": teacher_gradient_max,
                "reset_sample_count": int(reset_metrics["sample_count"]),
                "reset_selected_elements": int(reset_metrics["selected_elements"]),
                "reset_gradient_max": reset_gradient_max,
            },
            "checks": {name: bool(passed) for name, passed in checks.items()},
            "failed_checks": failed_checks,
            "execution": {
                "rollout_episode_slots": 80,
                "scheduled_rollout_ticks": 20000,
                "committed_optimizer_updates": 0,
                "snapshots_written": 0,
                "onnx_graphs_written": 0,
                "formal_support_cells": 0,
                "locomotion_training_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": preregistration["authority"],
            "sources": preregistration["sources"],
            "source_manifest_sha256": preregistration["source_manifest_sha256"],
        }
        if any((args.work_root / name).iterdir() for name in ("snapshots", "graphs")):
            raise ValueError("Winner-v73 diagnostic wrote a training artifact")
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        print(f"classification={classification}")
        print(f"decision={decision}")
        print(f"sha256={sha256(args.output)}")
        return 0
'''


def transformed_source() -> tuple[str, str]:
    source, _ = v71b.corrected_source()
    source = replace_exact(
        source,
        'import build_winner_v71_fresh_moment_safeguarded_continuation as v71_builder  # noqa: E402',
        'import build_winner_v73_update638_contract_attribution as v71_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v73_update638_contract_attribution_preregistration.json"',
    )
    source = replace_exact(source, "UPDATES = 53", "UPDATES = 1")
    source = replace_exact(
        source, "SOURCE_COMPLETED_UPDATES = 602", "SOURCE_COMPLETED_UPDATES = 637"
    )
    source = replace_exact(
        source, "HALF_COMPLETED_UPDATES = 605", "HALF_COMPLETED_UPDATES = 638"
    )
    source = replace_exact(
        source, "FINAL_COMPLETED_UPDATES = 655", "FINAL_COMPLETED_UPDATES = 638"
    )
    source = replace_region(
        source,
        "def validate_preregistration",
        "def validate_artifact",
        VALIDATE_PREREGISTRATION,
    )
    source = replace_region(
        source,
        "def validate_source_snapshot",
        "def graph_receipt",
        VALIDATE_SOURCE,
    )
    source = replace_region(
        source,
        '    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))',
        '    source_receipt = preregistration["source_checkpoint"]["snapshot"]',
        SOURCE_EVIDENCE,
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--isolated-persistent-teacher-training-authorized", action="store_true")',
        '    parser.add_argument("--update638-contract-attribution-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.isolated_persistent_teacher_training_authorized:",
        "if not args.offline_cpu_only or not args.update638_contract_attribution_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v71 requires --offline-cpu-only --isolated-persistent-teacher-training-authorized"',
        '"Winner-v73 requires --offline-cpu-only --update638-contract-attribution-authorized"',
    )
    source = replace_region(
        source,
        "        if (\n            float(ppo_metrics[\"sampled_hidden_replay_max_abs_error\"])",
        "        reset_keys = tuple(sorted(v29.ANCHOR_GRADIENT_KEYS))",
        DIAGNOSTIC,
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v73_update638_contract_attribution.py", "exec")
    return source, transformed_hash


def artifact(path: Path, **extra: Any) -> dict[str, Any]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        **extra,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v73 contract: {path}")
    snapshots = sorted((WORK_ROOT / "snapshots").glob("*.npz"))
    graphs = sorted((WORK_ROOT / "graphs").glob("*.onnx"))
    if (
        len(snapshots) != 35
        or [int(path.stem.rsplit("_", 1)[1]) for path in snapshots]
        != list(range(603, 638))
        or graphs != [SOURCE_GRAPH]
        or sha256(SOURCE_SNAPSHOT) != EXPECTED_SOURCE_SNAPSHOT_SHA256
        or sha256(SOURCE_GRAPH) != EXPECTED_SOURCE_GRAPH_SHA256
        or (ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_result.json").exists()
    ):
        raise ValueError("Winner-v71b stopped boundary changed")
    v71b_contract = json.loads(V71B_CONTRACT.read_text(encoding="utf-8"))
    if (
        sha256(V71B_CONTRACT)
        != "c15d9edd05b10979cef47bd43b3d05dabeba2bca21e3ed6978039e716324dc10"
        or v71b_contract.get("v71b", {}).get("replacement_count") != 1
    ):
        raise ValueError("Winner-v71b correction contract changed")
    transformed, transformed_hash = transformed_source()
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v73_update638_contract_attribution.py"),
            "runner": Path("tools/run_winner_v73_update638_contract_attribution.py"),
            "tests": Path("tests/test_winner_v73_update638_contract_attribution.py"),
            "v71b_builder": Path("tools/build_winner_v71b_full_loss_binding_correction.py"),
            "v71b_runner": Path("tools/run_winner_v71b_full_loss_binding_correction.py"),
            "v71b_contract": Path(
                "outputs/analysis/winner_v71b_full_loss_binding_correction.json"
            ),
        }.items()
    }
    teacher_checkpoint = v71b_contract["teacher_checkpoint"]
    value = {
        "schema_version": "winner_v73.update638_contract_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_UPDATE638_CONTRACT_ATTRIBUTION_ONLY",
        "prior_invocation": {
            "status": "STOPPED_WINNER_V71B_REPLAY_TEACHER_CONTRACT_AT_638",
            "exception": "ValueError: Winner-v71 replay/teacher contract changed at 638",
            "last_durable_optimizer_count": SOURCE_COUNT,
            "attempted_optimizer_count": ATTEMPT_COUNT,
            "durable_snapshot_count": len(snapshots),
            "durable_graph_count": len(graphs),
            "result_written": False,
        },
        "source_checkpoint": {
            "completed_updates": SOURCE_COUNT,
            "optimizer_count": SOURCE_COUNT,
            "snapshot": artifact(
                SOURCE_SNAPSHOT,
                completed_updates=SOURCE_COUNT,
                optimizer_count=SOURCE_COUNT,
            ),
            "graph": artifact(SOURCE_GRAPH, completed_updates=605, label="half"),
        },
        "teacher_checkpoint": teacher_checkpoint,
        "diagnostic": {
            "source_optimizer_count": SOURCE_COUNT,
            "rollout_update_index": SOURCE_COUNT,
            "attempted_optimizer_count": ATTEMPT_COUNT,
            "environments": 80,
            "ticks_per_environment": 250,
            "checks": [
                "sampled_hidden_replay_max_abs_error <= 2e-6",
                "stored successor transition count exact and positive",
                "anchor and teacher selected-element counts exact",
                "anchor, teacher, and reset gradient supports exact",
                "reset sample and selected-element counts exact",
            ],
            "threshold_or_architecture_change": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "stop_rules": [
            "write no optimizer update, snapshot, or ONNX graph",
            "do not relax the 2e-6 replay threshold",
            "classify the exact failed invariant before proposing any continuation",
        ],
        "authority": {
            "diagnostic_authorized": True,
            "optimizer_updates_authorized": 0,
            "formal_support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "v71b_corrected_source_sha256": v71b.corrected_source()[1],
            "transformed_source_sha256": transformed_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v73 update-638 contract attribution preregistration",
                "",
                "- Prior run: stopped before update `638`; last durable count `637`",
                "- Diagnostic: replay the exact count-638 batch and report every frozen invariant",
                "- Optimizer updates / snapshots / graphs / support cells / robot access: `0 / 0 / 0 / 0 / 0`",
                "- The `2e-6` hidden-replay threshold is measured, not relaxed",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
