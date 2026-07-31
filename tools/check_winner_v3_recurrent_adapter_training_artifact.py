#!/usr/bin/env python3
"""Independently validate the one-shot winner-v3 CPU training artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tarfile
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np
import onnx
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v3_recurrent_adapter_training_result.json"
ARTIFACT = ANALYSIS / "winner_v3_recurrent_adapter_artifacts.tar.gz"
OUT_JSON = ANALYSIS / "winner_v3_recurrent_adapter_training_artifact_check.json"
OUT_MD = ANALYSIS / "WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK_20260719.md"
EXPECTED_STAGES = (
    ("DOMAIN_25_PERCENT", 0.25, [0, 245_760]),
    ("DOMAIN_50_PERCENT", 0.5, [0, 245_760]),
    ("DOMAIN_100_PERCENT", 1.0, [0, 1_003_520, 2_007_040]),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def tree_error(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(right):
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def tree_finite(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def stage_path(extracted: Path, recorded: str) -> Path:
    recorded_path = Path(recorded)
    stage_name = recorded_path.parent.name
    return extracted / stage_name / recorded_path.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    work = args.work_root.resolve()
    if work.exists():
        raise FileExistsError(f"refusing to reuse artifact-check work root: {work}")
    if OUT_JSON.exists() or OUT_MD.exists():
        raise FileExistsError("refusing to overwrite formal artifact check")
    work.mkdir(parents=True)

    result = json.loads(RESULT.read_text())
    artifact_meta = result.get("artifact", {})
    with tarfile.open(ARTIFACT, "r:gz") as archive:
        members = archive.getmembers()
        safe_members = all(
            not member.issym()
            and not member.islnk()
            and not Path(member.name).is_absolute()
            and ".." not in Path(member.name).parts
            and member.name.rstrip("/") == str(Path(member.name))
            for member in members
        )
        one_root = bool(members) and all(
            Path(member.name).parts[0] == "winner_v3_recurrent_adapter_training"
            for member in members
        )
        archive.extractall(work, filter="data")
    extracted = work / "winner_v3_recurrent_adapter_training"
    internal = json.loads((extracted / "run_state.json").read_text())
    official_without_artifact = dict(result)
    official_without_artifact.pop("artifact", None)

    checkpointer = ocp.PyTreeCheckpointer()
    stage_checks = []
    restored = []
    for row, expected in zip(result.get("stages", []), EXPECTED_STAGES, strict=True):
        expected_id, expected_scale, expected_steps = expected
        checkpoint_rows = row.get("checkpoints", [])
        onnx_rows = row.get("onnx", [])
        checkpoint_paths = [stage_path(extracted, item["path"]) for item in checkpoint_rows]
        onnx_paths = [stage_path(extracted, item["path"]) for item in onnx_rows]
        checkpoint_values = [checkpointer.restore(str(path)) for path in checkpoint_paths]
        restored.append(checkpoint_values)
        onnx_checks = []
        for item, path in zip(onnx_rows, onnx_paths, strict=True):
            model = onnx.load(path)
            inputs = {
                value.name: [dim.dim_value for dim in value.type.tensor_type.shape.dim]
                for value in model.graph.input
            }
            outputs = {
                value.name: [dim.dim_value for dim in value.type.tensor_type.shape.dim]
                for value in model.graph.output
            }
            onnx_checks.append(
                {
                    "step": item["step"],
                    "hash_exact": sha256(path) == item["sha256"],
                    "abi_exact": inputs
                    == {"obs": [1, 115], "previous_action": [1, 14], "h_in": [1, 64]}
                    and outputs
                    == {
                        "continuous_actions": [1, 14],
                        "previous_action_out": [1, 14],
                        "h_out": [1, 64],
                    },
                    "initializers_finite": all(
                        np.all(np.isfinite(onnx.numpy_helper.to_array(value)))
                        for value in model.graph.initializer
                    ),
                }
            )
        stage_checks.append(
            {
                "id": row.get("id"),
                "id_exact": row.get("id") == expected_id,
                "scale_exact": row.get("deviation_scale") == expected_scale,
                "checkpoint_steps_exact": row.get("checkpoint_steps") == expected_steps,
                "onnx_steps_exact": row.get("onnx_steps") == expected_steps,
                "checkpoint_directory_hashes_exact": all(
                    sha256_directory(path) == item["directory_sha256"]
                    for item, path in zip(checkpoint_rows, checkpoint_paths, strict=True)
                ),
                "checkpoint_leaves_finite": all(tree_finite(value) for value in checkpoint_values),
                "onnx": onnx_checks,
            }
        )

    continuity = []
    for previous_index, current_index in ((0, 1), (1, 2)):
        structure, error = tree_error(
            restored[previous_index][-1], restored[current_index][0]
        )
        continuity.append(
            {
                "from": EXPECTED_STAGES[previous_index][0],
                "to": EXPECTED_STAGES[current_index][0],
                "tree_structure_exact": structure,
                "max_abs_error": error,
            }
        )

    training_log = extracted / "training.log"
    log_text = training_log.read_text(errors="replace")
    process_id = int(result["process_id"])
    start_pids = [int(value) for value in re.findall(r"WINNER_V3_STAGE_START=.*pid=(\d+)", log_text)]
    complete_pids = [int(value) for value in re.findall(r"WINNER_V3_STAGE_COMPLETE=.*pid=(\d+)", log_text)]
    checks = {
        "result_status_passed": result.get("status")
        == "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT",
        "artifact_sha256_exact": sha256(ARTIFACT) == artifact_meta.get("sha256"),
        "artifact_size_exact": ARTIFACT.stat().st_size == artifact_meta.get("bytes"),
        "tar_members_safe": safe_members and one_root,
        "internal_run_state_exact": internal == official_without_artifact,
        "training_log_hash_exact": sha256(training_log)
        == result.get("training_log", {}).get("sha256"),
        "all_stage_contracts_exact": all(
            row["id_exact"]
            and row["scale_exact"]
            and row["checkpoint_steps_exact"]
            and row["onnx_steps_exact"]
            and row["checkpoint_directory_hashes_exact"]
            and row["checkpoint_leaves_finite"]
            and all(
                item["hash_exact"]
                and item["abi_exact"]
                and item["initializers_finite"]
                for item in row["onnx"]
            )
            for row in stage_checks
        ),
        "stage_restore_continuity_exact": all(
            row["tree_structure_exact"] and row["max_abs_error"] == 0.0
            for row in continuity
        ),
        "one_logged_process_for_all_stages": start_pids
        == [process_id, process_id, process_id]
        and complete_pids == [process_id, process_id, process_id],
        "no_logged_failure": not any(
            token in log_text
            for token in ("Traceback (most recent call last)", "HOLD_WINNER_V3", "FAILED=")
        ),
        "cpu_only": bool(jax.devices())
        and all(device.platform == "cpu" for device in jax.devices()),
        "formal_behavior_cells_zero": result.get("formal_behavior_cells_executed") == 0,
        "training_reward_has_no_selection_weight": result.get(
            "training_reward_selection_weight"
        )
        == "NONE",
        "persistent_onnx_hashes_distinct": len(
            {
                item["sha256"]
                for item in result["stages"][-1]["onnx"]
                if item["step"] in (1_003_520, 2_007_040)
            }
        )
        == 2,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK"
        if not failed
        else "HOLD_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK"
    )
    payload = {
        "schema_version": "winner_v3.recurrent_adapter_training_artifact_check.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "devices": [str(device) for device in jax.devices()],
        "artifact": {
            "sha256": sha256(ARTIFACT),
            "bytes": ARTIFACT.stat().st_size,
            "member_count": len(members),
        },
        "result_sha256": sha256(RESULT),
        "stage_checks": stage_checks,
        "continuity": continuity,
        "persistent_onnx": [
            {"step": item["step"], "sha256": item["sha256"]}
            for item in result["stages"][-1]["onnx"]
            if item["step"] in (1_003_520, 2_007_040)
        ],
        "formal_behavior_cells_executed": 0,
        "authority": {
            "frozen_cpu_evaluation_after_pass": not failed,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "runtime_or_gate5": False,
            "robot_clearance": False,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        f"""# Winner-v3 Recurrent-Adapter Training Artifact Check — 2026-07-19

Status: `{status}`

- archive SHA-256: `{payload['artifact']['sha256']}`
- archive bytes / members: `{payload['artifact']['bytes']} / {payload['artifact']['member_count']}`
- JAX devices: `{payload['devices']}`
- stage restore continuity max errors: `{[row['max_abs_error'] for row in continuity]}`
- persistent ONNX: `{payload['persistent_onnx']}`
- formal behavior cells executed: `0`
- failed checks: `{failed}`

This is an independent CPU artifact/continuity/ABI check. A pass authorizes only
the already-frozen 1,024-cell CPU behavior evaluation. It is not behavior
evidence, a supported-configuration envelope, runtime acceptance, Gate 5,
deployment, or robot clearance. No hosted allocation, GPU/iGPU, RDK-X5, robot,
serial, torque or motion is authorized.
"""
    )
    print(status)
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
