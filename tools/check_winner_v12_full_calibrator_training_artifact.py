#!/usr/bin/env python3
"""Independently verify a completed Winner-v12 full-calibrator training ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
from typing import Any, Mapping
import zipfile


os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = (
    ANALYSIS / "winner_v12_full_calibrator_training_cpu_contract_result_v2.json"
)
LAUNCH_CONTRACT = ANALYSIS / "winner_v12_full_calibrator_training_launch_contract.json"
CLAIM = ANALYSIS / "winner_v12_full_calibrator_training_authorization_claim.json"
PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
WORK_ROOT_NAME = "winner-v12-full-calibrator-training-work"
RESULT_NAME = "winner_v12_full_calibrator_training_result.json"
ROOT_LOG_NAME = "winner-v12-full-calibrator-training.log"
ROOT_RESULT_HASH_NAME = "winner-v12-full-calibrator-training-result.sha256"
HEX64_RE = re.compile(r"[0-9a-f]{64}")
GIT_OID_RE = re.compile(r"[0-9a-f]{40}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def require_sha256(value: Any, label: str) -> None:
    if HEX64_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} SHA-256 is malformed")


def require_git_oid(value: Any, label: str) -> None:
    if GIT_OID_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{label} Git object ID is malformed")


def repository_attribution(
    *,
    run_id: int,
    run_attempt: int,
    run_head_sha: str,
    artifact_id: int,
    artifact_name: str,
    artifact_digest: str,
    expected_zip_sha256: str,
) -> dict[str, Any]:
    require_git_oid(run_head_sha, "GitHub run head")
    expected_name = f"winner-v12-full-calibrator-training-{run_id}"
    expected_digest = f"sha256:{expected_zip_sha256}"
    if (
        run_id <= 0
        or run_attempt != 1
        or artifact_id <= 0
        or artifact_name != expected_name
        or artifact_digest != expected_digest
    ):
        raise ValueError("GitHub training artifact attribution changed")
    return {
        "repository": "RobVanProd/open-duck-mini-rdkx5",
        "github_run_id": run_id,
        "github_run_attempt": run_attempt,
        "github_run_head_sha": run_head_sha,
        "github_artifact_id": artifact_id,
        "github_artifact_name": artifact_name,
        "github_artifact_digest": artifact_digest,
    }


def safe_extract_zip(archive_path: Path, destination: Path) -> list[str]:
    """Extract only unique, regular, relative POSIX paths into a new directory."""
    if destination.exists():
        raise FileExistsError(f"refusing to reuse extraction root: {destination}")
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if not infos or len(names) != len(set(names)):
            raise ValueError("artifact ZIP is empty or contains duplicate members")
        if sum(item.file_size for item in infos) > 2_000_000_000:
            raise ValueError(
                "artifact ZIP uncompressed size exceeds the frozen ceiling"
            )
        validated: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
        for info in infos:
            name = info.filename
            relative = PurePosixPath(name)
            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if (
                not name
                or "\\" in name
                or relative.is_absolute()
                or ".." in relative.parts
                or "." in relative.parts
                or info.flag_bits & 0x1
                or file_type == stat.S_IFLNK
                or (file_type not in {0, stat.S_IFREG, stat.S_IFDIR})
            ):
                raise ValueError(f"unsafe artifact ZIP member: {name!r}")
            if info.is_dir() != name.endswith("/"):
                raise ValueError(f"ambiguous artifact ZIP member type: {name!r}")
            validated.append((info, relative))
        destination.mkdir(parents=True)
        resolved_root = destination.resolve()
        for info, relative in validated:
            target = destination.joinpath(*relative.parts)
            resolved_target = target.resolve()
            if os.path.commonpath((str(resolved_root), str(resolved_target))) != str(
                resolved_root
            ):
                raise ValueError("artifact ZIP member escaped extraction root")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
    return names


def expected_artifact_files() -> set[str]:
    files = {ROOT_LOG_NAME, ROOT_RESULT_HASH_NAME}
    prefix = f"{WORK_ROOT_NAME}/"
    files.update(
        {
            prefix + "winner_v12_full_calibrator_training_claim_receipt.json",
            prefix + "winner_v12_calibrator_stage1_final.npz",
            prefix + "winner_v12_calibrator_stage1_final_receipt.json",
            prefix + "winner_v12_calibrator_half.npz",
            prefix + "winner_v12_calibrator_half.onnx",
            prefix + "winner_v12_calibrator_half_receipt.json",
            prefix + "winner_v12_calibrator_final.npz",
            prefix + "winner_v12_calibrator_final.onnx",
            prefix + "winner_v12_calibrator_final_receipt.json",
            prefix + "winner_v12_full_calibrator_latest.npz",
            prefix + RESULT_NAME,
        }
    )
    for stage, updates in (("stage1", range(1, 101)), ("stage2", range(0, 101))):
        for update in updates:
            stem = f"snapshot_{stage}_update_{update:03d}"
            files.add(prefix + f"snapshots/{stem}.npz")
            files.add(prefix + f"snapshots/{stem}.receipt.json")
    return files


def strict_result_schema(result: Mapping[str, Any]) -> None:
    expected = {
        "artifact_manifest",
        "artifact_manifest_sha256",
        "authority",
        "authority_source",
        "checks",
        "decision",
        "elapsed_seconds_this_process",
        "environment",
        "execution",
        "failed_checks",
        "logical_run_id",
        "metrics",
        "parameter_tree_sha256",
        "persistent_artifacts",
        "population",
        "schema_version",
        "stage1_final_artifact",
        "stage1_tree_sha256",
        "status",
        "training_reward_selection_weight",
    }
    if set(result) != expected:
        raise ValueError("full-training result schema changed")
    if result["schema_version"] != "winner_v12.full_calibrator_training_result.v1":
        raise ValueError("full-training result version changed")
    if result["status"] != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT":
        raise ValueError("full-training result did not pass")
    if result["decision"] != "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY":
        raise ValueError("full-training result authority changed")
    expected_checks = {
        "exact_100_stage1_updates",
        "exact_100_stage2_updates",
        "exact_201_immutable_snapshots",
        "formal_support_cells_zero",
        "half_and_final_checkpoint_graphs_present",
        "latest_pointer_matches_final",
        "locomotion_training_steps_zero",
        "robot_or_rdk_access_zero",
        "stage1_final_checkpoint_present",
    }
    if (
        not isinstance(result["checks"], dict)
        or set(result["checks"]) != expected_checks
        or not all(type(value) is bool for value in result["checks"].values())
        or not all(result["checks"].values())
        or result["failed_checks"] != []
    ):
        raise ValueError("full-training result check set changed")
    if result["execution"] != {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
        "stage1_optimizer_updates": 100,
        "stage2_optimizer_updates": 100,
    }:
        raise ValueError("full-training execution counters changed")
    if result["authority"] != {
        "formal_support_gate_executed": False,
        "locomotion_training_or_behavior_executed": False,
        "pass_authorizes_only": "the separately frozen 124-cell calibrator support/context gate",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }:
        raise ValueError("full-training authority block changed")
    if result["training_reward_selection_weight"] != "NONE":
        raise ValueError("full-training reward acquired selection authority")


def validate_snapshot_receipt(
    receipt: Mapping[str, Any], path: Path, *, stage: str, update: int
) -> None:
    if set(receipt) != {
        "bytes",
        "completed_updates",
        "metadata_payload_sha256",
        "optimizer_count",
        "path",
        "schema_version",
        "sha256",
        "stage",
        "state_payload_sha256",
    }:
        raise ValueError("snapshot receipt schema changed")
    if (
        receipt["schema_version"] != "winner_v12.full_calibrator_snapshot_receipt.v1"
        or receipt["stage"] != stage
        or receipt["completed_updates"] != update
        or receipt["optimizer_count"] != update
        or receipt["bytes"] != path.stat().st_size
        or receipt["sha256"] != sha256(path)
        or Path(receipt["path"]).name != path.name
    ):
        raise ValueError(f"snapshot receipt changed: {path.name}")
    for key in ("sha256", "state_payload_sha256", "metadata_payload_sha256"):
        require_sha256(receipt[key], f"snapshot receipt {key}")


def normalized_path_value(value: Any) -> Any:
    """Replace recorded absolute artifact paths with their basename recursively."""
    if isinstance(value, dict):
        return {
            key: (
                Path(item).name
                if key == "path" and isinstance(item, str)
                else normalized_path_value(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [normalized_path_value(item) for item in value]
    return value


def parameter_delta_rows(
    initial: Mapping[str, Any], final: Mapping[str, Any], keys: list[str]
) -> list[dict[str, Any]]:
    import numpy as np

    return [
        {
            "key": key,
            "changed": not np.array_equal(initial[key], final[key]),
            "max_abs_delta": float(
                np.max(np.abs(np.asarray(final[key]) - np.asarray(initial[key])))
            ),
        }
        for key in keys
    ]


def optimizer_rows(
    optimizer: Mapping[str, Any], keys: list[str]
) -> list[dict[str, Any]]:
    import numpy as np

    return [
        {
            "key": key,
            "m_nonzero": bool(np.any(np.asarray(optimizer["m"][key]) != 0)),
            "v_nonzero": bool(np.any(np.asarray(optimizer["v"][key]) != 0)),
        }
        for key in keys
    ]


def verified_checkpoint_identity(
    *,
    label: str,
    update: int,
    checkpoint_path: Path,
    graph_path: Path,
    receipt_path: Path,
    graph_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the exact identities the next frozen gate contract must consume."""
    required_graph_fields = {
        "abi_exact",
        "all_chain_outputs_finite",
        "all_initializers_finite",
        "inputs",
        "jax_onnx_at_most_1e_7",
        "jax_onnx_max_abs_error",
        "outputs",
        "previous_action_out_equals_action_bit_exact",
        "training_only_tensors_absent",
    }
    expected_updates = {"half": 50, "final": 100}
    if label not in expected_updates or update != expected_updates[label]:
        raise ValueError("verified checkpoint boundary changed")
    if not required_graph_fields <= set(graph_contract):
        raise ValueError("verified graph contract is incomplete")
    expected_inputs = [
        {"name": "obs", "shape": [1, 115]},
        {"name": "previous_action", "shape": [1, 14]},
        {"name": "h_in", "shape": [1, 64]},
    ]
    expected_outputs = [
        {"name": "calibration_actions", "shape": [1, 14]},
        {"name": "previous_action_out", "shape": [1, 14]},
        {"name": "h_out", "shape": [1, 64]},
    ]
    if (
        graph_contract["inputs"] != expected_inputs
        or graph_contract["outputs"] != expected_outputs
        or graph_contract["abi_exact"] is not True
        or graph_contract["all_initializers_finite"] is not True
        or graph_contract["all_chain_outputs_finite"] is not True
        or graph_contract["training_only_tensors_absent"] is not True
        or graph_contract["jax_onnx_at_most_1e_7"] is not True
        or graph_contract["previous_action_out_equals_action_bit_exact"] is not True
    ):
        raise ValueError("verified graph contract did not pass exactly")
    return {
        "label": label,
        "update": update,
        "checkpoint": {
            "file": checkpoint_path.name,
            "sha256": sha256(checkpoint_path),
            "bytes": checkpoint_path.stat().st_size,
        },
        "onnx": {
            "file": graph_path.name,
            "sha256": sha256(graph_path),
            "bytes": graph_path.stat().st_size,
            "inputs": graph_contract["inputs"],
            "outputs": graph_contract["outputs"],
            "abi_exact": graph_contract["abi_exact"],
            "all_initializers_finite": graph_contract["all_initializers_finite"],
            "all_chain_outputs_finite": graph_contract["all_chain_outputs_finite"],
            "training_only_tensors_absent": graph_contract[
                "training_only_tensors_absent"
            ],
            "jax_onnx_max_abs_error": graph_contract["jax_onnx_max_abs_error"],
            "jax_onnx_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
            "previous_action_out_equals_action_bit_exact": graph_contract[
                "previous_action_out_equals_action_bit_exact"
            ],
        },
        "receipt": {
            "file": receipt_path.name,
            "sha256": sha256(receipt_path),
            "bytes": receipt_path.stat().st_size,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--extract-root", type=Path, required=True)
    parser.add_argument("--expected-zip-sha256", required=True)
    parser.add_argument("--expected-result-sha256", required=True)
    parser.add_argument("--expected-github-run-id", type=int, required=True)
    parser.add_argument("--expected-github-run-attempt", type=int, required=True)
    parser.add_argument("--expected-github-run-head-sha", required=True)
    parser.add_argument("--expected-github-artifact-id", type=int, required=True)
    parser.add_argument("--expected-github-artifact-name", required=True)
    parser.add_argument("--expected-github-artifact-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite artifact check: {args.output}")
    require_sha256(args.expected_zip_sha256, "expected artifact ZIP")
    require_sha256(args.expected_result_sha256, "expected training result")
    attribution = repository_attribution(
        run_id=args.expected_github_run_id,
        run_attempt=args.expected_github_run_attempt,
        run_head_sha=args.expected_github_run_head_sha,
        artifact_id=args.expected_github_artifact_id,
        artifact_name=args.expected_github_artifact_name,
        artifact_digest=args.expected_github_artifact_digest,
        expected_zip_sha256=args.expected_zip_sha256,
    )
    if sha256(args.artifact_zip) != args.expected_zip_sha256:
        raise ValueError("artifact ZIP differs from the frozen GitHub digest")
    members = safe_extract_zip(args.artifact_zip, args.extract_root)
    extracted_files = {
        str(path.relative_to(args.extract_root)).replace("\\", "/")
        for path in args.extract_root.rglob("*")
        if path.is_file()
    }
    if extracted_files != expected_artifact_files():
        raise ValueError("full-training artifact file inventory changed")

    sys.path.insert(0, str(PATCHES))
    sys.path.insert(0, str(TOOLS))
    import jax
    import numpy as np
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as runner
    import winner_v12_calibrator_training as training

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("artifact verification requires CPU-only JAX")
    work = args.extract_root / WORK_ROOT_NAME
    result_path = work / RESULT_NAME
    if sha256(result_path) != args.expected_result_sha256:
        raise ValueError("training result differs from the frozen result hash")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    strict_result_schema(result)

    expected_versions = {
        "jax": "0.7.2",
        "jaxlib": "0.7.2",
        "mujoco": "3.9.0",
        "numpy": "2.0.2",
        "onnx": "1.22.0",
        "onnxruntime": "1.27.0",
        "python": "3.12.13",
    }
    environment_exact = result["environment"] == {
        "jax_devices": ["TFRT_CPU_0"],
        "software_versions": {
            "exact": True,
            "expected": expected_versions,
            "observed": expected_versions,
        },
    }
    authority_source_exact = result["authority_source"] == {
        "claim_lf_sha256": smoke.lf_sha256(CLAIM),
        "cpu_result_sha256": smoke.sha256(CPU_RESULT),
        "cpu_result_status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT",
        "launch_contract_lf_sha256": smoke.lf_sha256(LAUNCH_CONTRACT),
    }
    claim_receipt = json.loads(
        (work / "winner_v12_full_calibrator_training_claim_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    claim_receipt_exact = claim_receipt == {
        "schema_version": "winner_v12.full_calibrator_training_claim_receipt.v1",
        "logical_run_id": "winner-v12-full-calibrator-seed-120120",
        "resolved_work_root": "/tmp/winner-v12-full-calibrator-training-work",
        "claim_lf_sha256": smoke.lf_sha256(CLAIM),
        "cpu_result_sha256": smoke.sha256(CPU_RESULT),
        "runner_lf_sha256": smoke.lf_sha256(
            ROOT / "tools/run_winner_v12_full_calibrator_training.py"
        ),
    }

    expected_names = [
        *(f"snapshot_stage1_update_{update:03d}.npz" for update in range(1, 101)),
        *(f"snapshot_stage2_update_{update:03d}.npz" for update in range(0, 101)),
    ]
    snapshots = []
    snapshot_receipts = []
    for name in expected_names:
        path = work / "snapshots" / name
        snapshot = runner.load_snapshot(path)
        runner.validate_resume(snapshot)
        runner.validate_stage2_lineage(snapshot, work)
        stage = snapshot["metadata"]["stage"]
        update = int(snapshot["metadata"]["completed_updates"])
        receipt_path = path.with_suffix(".receipt.json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        validate_snapshot_receipt(receipt, path, stage=stage, update=update)
        snapshots.append(snapshot)
        snapshot_receipts.append(receipt)

    stage1_final = snapshots[99]
    stage2_final = snapshots[-1]
    initial = training.initialize_training_parameters(seed=runner.PARAMETER_SEED)
    stage1_keys = list(training.ENCODER_AUXILIARY_KEYS)
    stage2_keys = list(
        training.DEPLOYABLE_ACTION_KEYS + training.TRAINING_ONLY_STAGE2_KEYS
    )
    stage1_deltas = parameter_delta_rows(
        initial, stage1_final["parameters"], stage1_keys
    )
    stage2_deltas = parameter_delta_rows(
        initial, stage2_final["parameters"], stage2_keys
    )
    stage1_moments = optimizer_rows(stage1_final["optimizer"], stage1_keys)
    stage2_moments = optimizer_rows(stage2_final["optimizer"], stage2_keys)

    def validate_checkpoint_copy(label: str, source_snapshot: Mapping[str, Any]):
        path = work / f"winner_v12_calibrator_{label}.npz"
        loaded = runner.load_snapshot(path)
        runner.validate_resume(loaded)
        if not runner.state_equal(loaded, source_snapshot):
            raise ValueError(f"{label} checkpoint differs from its source snapshot")
        return path, loaded

    stage1_path, _ = validate_checkpoint_copy("stage1_final", stage1_final)
    half_snapshot = snapshots[150]
    half_path, _ = validate_checkpoint_copy("half", half_snapshot)
    final_path, _ = validate_checkpoint_copy("final", stage2_final)
    persistent_contracts = []
    verified_checkpoints = {}
    for label, update, snapshot, checkpoint_path in (
        ("half", 50, half_snapshot, half_path),
        ("final", 100, stage2_final, final_path),
    ):
        graph_path = work / f"winner_v12_calibrator_{label}.onnx"
        flat = np.arange(runner.EPISODE_TICKS * training.OBS_SIZE, dtype=np.int64)
        observations = (
            ((flat + update * 17) % 257).astype(np.float32) - np.float32(128.0)
        ).reshape(runner.EPISODE_TICKS, training.OBS_SIZE) / np.float32(128.0)
        observed_graph = smoke.onnx_contract(
            graph_path,
            training.deployable_parameters(snapshot["parameters"]),
            observations,
        )
        receipt_path = work / f"winner_v12_calibrator_{label}_receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if normalized_path_value(receipt["graph"]) != normalized_path_value(
            observed_graph
        ):
            raise ValueError(f"{label} independently verified ONNX receipt changed")
        if receipt["checkpoint"]["sha256"] != sha256(checkpoint_path):
            raise ValueError(f"{label} checkpoint receipt hash changed")
        persistent_contracts.append(receipt)
        verified_checkpoints[label] = verified_checkpoint_identity(
            label=label,
            update=update,
            checkpoint_path=checkpoint_path,
            graph_path=graph_path,
            receipt_path=receipt_path,
            graph_contract=observed_graph,
        )

    stage1_receipt = json.loads(
        (work / "winner_v12_calibrator_stage1_final_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    if stage1_receipt["checkpoint"]["sha256"] != sha256(stage1_path):
        raise ValueError("Stage-1 final checkpoint receipt hash changed")
    manifest = result["artifact_manifest"]
    claim_receipt_path = work / "winner_v12_full_calibrator_training_claim_receipt.json"
    manifest_claim_exact = manifest["authorization_claim_receipt"] == {
        "path": "/tmp/winner-v12-full-calibrator-training-work/winner_v12_full_calibrator_training_claim_receipt.json",
        "sha256": sha256(claim_receipt_path),
    }
    manifest_exact = (
        canonical_sha256(manifest) == result["artifact_manifest_sha256"]
        and manifest_claim_exact
        and manifest["snapshots"] == snapshot_receipts
        and manifest["stage1_final"] == stage1_receipt
        and manifest["persistent"] == persistent_contracts
        and manifest["recovery_events"] == []
        and result["stage1_final_artifact"] == stage1_receipt
        and result["persistent_artifacts"] == persistent_contracts
    )
    latest = work / "winner_v12_full_calibrator_latest.npz"
    latest_exact = (
        sha256(latest) == sha256(work / "snapshots/snapshot_stage2_update_100.npz")
        and manifest["latest_snapshot"]["sha256"] == sha256(latest)
        and manifest["latest_snapshot"]["bytes"] == latest.stat().st_size
    )
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    population_exact = (
        result["logical_run_id"] == "winner-v12-full-calibrator-seed-120120"
        and result["population"]["episodes_per_update"] == 80
        and result["population"]["configuration_ids"]
        == preregistration["population"]["training_configuration_ids"]
        and result["population"]["hidden_plants"] == list(smoke.PLANTS)
        and 0
        < result["population"]["cumulative_valid_transition_count"]
        <= result["population"]["cumulative_sampled_count"]
        <= 4_000_000
    )
    final_state_exact = (
        result["metrics"] == stage2_final["metadata"]["metrics"]
        and result["parameter_tree_sha256"]
        == smoke.tree_sha256(stage2_final["parameters"])
        and result["stage1_tree_sha256"]
        == smoke.tree_sha256(training.stage1_parameters(stage2_final["parameters"]))
    )
    hash_receipt_text = (args.extract_root / ROOT_RESULT_HASH_NAME).read_text(
        encoding="utf-8"
    )
    root_result_hash_exact = hash_receipt_text == (
        f"{args.expected_result_sha256}  /tmp/{WORK_ROOT_NAME}/{RESULT_NAME}\n"
    )
    log_text = (args.extract_root / ROOT_LOG_NAME).read_text(
        encoding="utf-8", errors="replace"
    )
    checks = {
        "artifact_zip_hash_exact": sha256(args.artifact_zip)
        == args.expected_zip_sha256,
        "artifact_zip_members_safe_unique": len(members) == len(set(members)),
        "artifact_file_inventory_exact": extracted_files == expected_artifact_files(),
        "repository_attribution_exact": attribution["github_artifact_digest"]
        == f"sha256:{args.expected_zip_sha256}",
        "training_result_hash_receipt_exact": root_result_hash_exact,
        "training_environment_exact_cpu_only": environment_exact,
        "authority_source_exact": authority_source_exact,
        "authorization_claim_receipt_exact": claim_receipt_exact,
        "all_201_snapshots_restore_and_validate": len(snapshots) == 201,
        "all_snapshot_receipts_exact": len(snapshot_receipts) == 201,
        "result_metrics_equal_final_snapshot": final_state_exact,
        "artifact_manifest_exact": manifest_exact,
        "latest_pointer_equals_final_snapshot": latest_exact,
        "stage1_active_leaves_all_changed": all(
            row["changed"] for row in stage1_deltas
        ),
        "stage2_active_leaves_all_changed": all(
            row["changed"] for row in stage2_deltas
        ),
        "stage1_optimizer_moments_all_nonzero": all(
            row["m_nonzero"] and row["v_nonzero"] for row in stage1_moments
        ),
        "stage2_optimizer_moments_all_nonzero": all(
            row["m_nonzero"] and row["v_nonzero"] for row in stage2_moments
        ),
        "half_and_final_onnx_independently_exact": len(persistent_contracts) == 2,
        "half_and_final_identities_exposed_for_gate": set(verified_checkpoints)
        == {"half", "final"}
        and verified_checkpoints["half"]["update"] == 50
        and verified_checkpoints["final"]["update"] == 100,
        "training_population_and_accounting_exact": population_exact,
        "no_logged_traceback_or_hold": "Traceback (most recent call last)"
        not in log_text
        and "HOLD_WINNER_V12" not in log_text,
        "formal_support_locomotion_robot_all_zero": result["execution"][
            "formal_support_cells"
        ]
        == result["execution"]["locomotion_training_steps"]
        == result["execution"]["robot_or_rdk_access"]
        == 0,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v12.full_calibrator_training_artifact_check.v1",
        "status": (
            "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK"
            if not failed
            else "HOLD_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK"
        ),
        "decision": (
            "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY"
            if not failed
            else "DO_NOT_RUN_124_CELL_CALIBRATOR_GATE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "artifact_zip": {
            "path": str(args.artifact_zip.resolve()),
            "sha256": sha256(args.artifact_zip),
            "bytes": args.artifact_zip.stat().st_size,
            "member_count": len(members),
        },
        "repository_attribution": attribution,
        "training_result_sha256": sha256(result_path),
        "verified_checkpoints": verified_checkpoints,
        "parameter_deltas": {"stage1": stage1_deltas, "stage2": stage2_deltas},
        "optimizer_moments": {"stage1": stage1_moments, "stage2": stage2_moments},
        "execution": {
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "artifact_verification_only": True,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the separately frozen 124-cell calibrator support/context gate",
        },
        "limitation": "per-update episode receipts are represented by immutable SHA-256 values in each metric row; raw per-update episode payloads were not retained by the frozen trainer",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
