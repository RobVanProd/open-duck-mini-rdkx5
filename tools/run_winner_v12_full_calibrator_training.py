#!/usr/bin/env python3
"""Run the single frozen Winner-v12 full automatic-calibrator training."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import winner_v12_calibrator_training as training  # noqa: E402


PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
)
CPU_CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract.json"
)
CPU_RESULT = (
    ROOT
    / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_result_v2.json"
)
LAUNCH_CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_launch_contract.json"
)
DOMAIN = (
    ROOT
    / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
)
ROOT_SEED = 120120
PARAMETER_SEED = 60720
EPISODE_TICKS = 250
STAGE1_UPDATES = 100
STAGE2_UPDATES = 100
SCHEDULED_TICK_SLOTS_PER_UPDATE = 20_000
SNAPSHOT_NAME = "winner_v12_full_calibrator_latest.npz"
RESULT_NAME = "winner_v12_full_calibrator_training_result.json"
PERSISTENT = {50: "half", 100: "final"}
COMMITTED_SNAPSHOT_RE = re.compile(r"snapshot_(stage1|stage2)_update_(\d{3})\.npz")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SNAPSHOT_METADATA_KEYS = frozenset(
    {
        "schema_version",
        "logical_run_id",
        "stage",
        "completed_updates",
        "root_seed",
        "parameter_seed",
        "preregistration_lf_sha256",
        "cpu_contract_lf_sha256",
        "cpu_contract_result_sha256",
        "runner_lf_sha256",
        "metrics",
        "stage_scheduled_tick_slots",
        "total_scheduled_tick_slots",
        "cumulative_sampled_count",
        "cumulative_valid_transition_count",
        "frozen_stage1_tree_sha256",
        "state_payload_sha256",
        "metadata_payload_sha256",
    }
)
STAGE1_METRIC_KEYS = frozenset(
    {
        "stage",
        "update",
        "loss",
        "sampled_count",
        "valid_transition_count",
        "episode_receipts_sha256",
        "frozen_target_mean_sha256",
        "frozen_target_std_sha256",
        "completed_episodes",
    }
)
STAGE2_LOSS_METRIC_KEYS = frozenset(
    {"policy_loss", "value_loss", "entropy", "ratio_min", "ratio_max"}
)
STAGE2_METRIC_KEYS = frozenset(
    {
        "stage",
        "update",
        "loss",
        "sampled_count",
        "valid_transition_count",
        "episode_receipts_sha256",
        "action_boundary",
        "completed_episodes",
        *STAGE2_LOSS_METRIC_KEYS,
    }
)
ACTION_BOUNDARY_KEYS = frozenset(
    {
        "attempted_samples",
        "raw_sha256",
        "previous_action_sha256",
        "realized_action_sha256",
        "numpy_expected_sha256",
        "jax_expected_sha256",
        "realized_equals_numpy_bit_exact",
        "numpy_equals_jax_bit_exact",
        "maximum_realized_numpy_error",
        "maximum_numpy_jax_error",
    }
)


def validate_source_manifest(source_manifest: Mapping[str, Any]) -> None:
    for item in source_manifest.values():
        path = ROOT / item["path"]
        observed = (
            smoke.lf_sha256(path) if item["hash_mode"] == "lf" else smoke.sha256(path)
        )
        if observed != item["sha256"]:
            raise ValueError(f"training source hash mismatch: {item['path']}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if value.get("status") != "PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING":
        raise ValueError("full calibrator training is not preregistered")
    if (
        value.get("decision")
        != "AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY"
    ):
        raise ValueError("full calibrator preregistration authority changed")
    if not all(value.get("checks", {}).values()):
        raise ValueError("full calibrator preregistration has failed checks")
    validate_source_manifest(value["sources"])
    return value


def validate_training_authority() -> dict[str, Any]:
    if not CPU_RESULT.is_file():
        raise FileNotFoundError("full calibrator CPU contract result is absent")
    result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if result.get("status") != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT":
        raise ValueError("full calibrator CPU contract did not pass")
    if (
        result.get("decision")
        != "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
    ):
        raise ValueError("full calibrator CPU contract authority changed")
    if result.get("failed_checks") != [] or not all(result.get("checks", {}).values()):
        raise ValueError("full calibrator CPU result has failed checks")
    if result.get("execution") != {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("CPU contract exceeded its zero-update authority")
    contract = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    if result.get("contract_lf_sha256") != smoke.lf_sha256(CPU_CONTRACT):
        raise ValueError("CPU result is not bound to the current contract")
    validate_source_manifest(contract["sources"])
    if not LAUNCH_CONTRACT.is_file():
        raise FileNotFoundError("full calibrator launch contract is absent")
    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    if launch.get("status") != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN":
        raise ValueError("full calibrator launch is not frozen")
    if launch.get("decision") != "AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN":
        raise ValueError("full calibrator launch authority changed")
    if launch.get("failed_checks") != [] or not all(launch.get("checks", {}).values()):
        raise ValueError("full calibrator launch has failed checks")
    if launch.get("cpu_result_sha256") != smoke.sha256(CPU_RESULT):
        raise ValueError("launch contract CPU-result identity changed")
    if launch.get("runner_lf_sha256") != smoke.lf_sha256(Path(__file__)):
        raise ValueError("launch contract runner identity changed")
    claim_item = launch.get("authorization_claim") or {}
    claim_path = ROOT / str(claim_item.get("path", ""))
    if not claim_path.is_file() or smoke.lf_sha256(claim_path) != claim_item.get(
        "lf_sha256"
    ):
        raise ValueError("launch authorization claim identity changed")
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    if claim != launch.get("authorization_claim_payload"):
        raise ValueError("launch authorization claim payload changed")
    if claim.get("logical_run_id") != "winner-v12-full-calibrator-seed-120120":
        raise ValueError("launch authorization logical run changed")
    if claim.get("cpu_result_sha256") != smoke.sha256(CPU_RESULT):
        raise ValueError("launch authorization CPU result changed")
    if claim.get("runner_lf_sha256") != smoke.lf_sha256(Path(__file__)):
        raise ValueError("launch authorization runner changed")
    return {"cpu_result": result, "launch": launch, "claim": claim}


def claim_receipt_payload(claim: Mapping[str, Any], work_root: Path) -> dict[str, Any]:
    resolved_work_root = str(work_root.resolve())
    if claim.get("resolved_work_root") != resolved_work_root:
        raise ValueError("launch claim does not authorize this resolved work root")
    return {
        "schema_version": "winner_v12.full_calibrator_training_claim_receipt.v1",
        "logical_run_id": claim["logical_run_id"],
        "resolved_work_root": resolved_work_root,
        "claim_lf_sha256": smoke.lf_sha256(
            ROOT / claim["repository_relative_claim_path"]
        ),
        "cpu_result_sha256": smoke.sha256(CPU_RESULT),
        "runner_lf_sha256": smoke.lf_sha256(Path(__file__)),
    }


def consume_or_validate_claim(
    claim: Mapping[str, Any], work_root: Path, *, fresh: bool
) -> dict[str, Any]:
    receipt = claim_receipt_payload(claim, work_root)
    receipt_path = work_root / "winner_v12_full_calibrator_training_claim_receipt.json"
    if fresh:
        write_json_exclusive(receipt_path, receipt)
    else:
        if not receipt_path.is_file():
            raise FileNotFoundError("logical-run authorization receipt is absent")
        if json.loads(receipt_path.read_text(encoding="utf-8")) != receipt:
            raise ValueError("logical-run authorization receipt changed")
    return receipt


def training_population(
    preregistration: Mapping[str, Any], domain: Mapping[str, Any]
) -> list[dict[str, Any]]:
    matrix = domain["evaluation_matrix"]
    configurations = matrix["fixed_anchors"] + matrix["discovery_samples"]
    if [row["id"] for row in configurations] != preregistration["population"][
        "training_configuration_ids"
    ]:
        raise ValueError("training configuration order changed")
    heldout = {row["id"] for row in matrix["heldout_samples"]}
    if heldout & {row["id"] for row in configurations}:
        raise ValueError("heldout configuration entered training")
    population = []
    for configuration in configurations:
        population.extend([dict(configuration), dict(configuration)])
    if len(population) != 80:
        raise ValueError("full training population is not 40x2")
    return population


def prng_for_update(
    stage: int, update_index: int, environment_index: int
) -> tuple[np.random.Generator, dict[str, Any]]:
    entropy = [ROOT_SEED, stage, update_index, environment_index]
    sequence = np.random.SeedSequence(entropy)
    receipt = {
        "algorithm": "NumPy PCG64",
        "seed_sequence_entropy": entropy,
        "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
    }
    return np.random.Generator(np.random.PCG64(sequence)), receipt


def validate_episode_receipts(
    episodes: Sequence[Mapping[str, Any]],
    population: Sequence[Mapping[str, Any]],
    *,
    stage: int,
    update_index: int,
) -> str:
    if len(episodes) != 80 or len(population) != 80:
        raise ValueError("per-update episode population changed")
    observed_seed_states = set()
    for environment, (receipt, configuration) in enumerate(
        zip(episodes, population, strict=True)
    ):
        expected_entropy = [ROOT_SEED, stage, update_index, environment]
        expected_plant = smoke.PLANTS[environment % 2]
        if receipt.get("environment") != environment:
            raise ValueError("episode environment order changed")
        if receipt.get("configuration_id") != configuration["id"]:
            raise ValueError("episode configuration order changed")
        if receipt.get("plant") != expected_plant:
            raise ValueError("episode hidden-plant order changed")
        prng = receipt.get("prng", {})
        if prng.get("algorithm") != "NumPy PCG64":
            raise ValueError("episode PRNG algorithm changed")
        if prng.get("seed_sequence_entropy") != expected_entropy:
            raise ValueError("episode seed derivation changed")
        seed_state = tuple(prng.get("seed_sequence_state_u32", []))
        if len(seed_state) != 4 or seed_state in observed_seed_states:
            raise ValueError("episode seed-state receipt is malformed or repeated")
        observed_seed_states.add(seed_state)
    return smoke.canonical_sha256(episodes)


def validate_stage2_masks(
    batch: Mapping[str, np.ndarray], episodes: Sequence[Mapping[str, Any]]
) -> None:
    sample_mask = np.asarray(batch["valid_mask"])
    transition_mask = np.asarray(batch["valid_transition_mask"])
    done = np.asarray(batch["done"])
    expected_shape = (80, EPISODE_TICKS)
    if (
        sample_mask.shape != expected_shape
        or transition_mask.shape != expected_shape
        or done.shape != expected_shape
    ):
        raise ValueError("Stage-2 terminal-mask shape changed")
    for environment, receipt in enumerate(episodes):
        samples = int(np.sum(sample_mask[environment]))
        valid = int(np.sum(transition_mask[environment]))
        done_indices = np.flatnonzero(done[environment])
        terminal = receipt["terminal"]
        if terminal is None:
            exact = samples == valid == EPISODE_TICKS and np.array_equal(
                done_indices, np.asarray([EPISODE_TICKS - 1])
            )
        else:
            terminal_tick = int(terminal["tick"])
            exact = samples == valid + 1 == terminal_tick + 1 and np.array_equal(
                done_indices, np.asarray([terminal_tick])
            )
        if not exact:
            raise ValueError(
                f"Stage-2 terminal mask changed for environment {environment}"
            )
        if not np.array_equal(
            sample_mask[environment, :samples],
            np.ones((samples,), dtype=sample_mask.dtype),
        ):
            raise ValueError("Stage-2 sample-mask active prefix is not exact one")
        if np.any(sample_mask[environment, samples:] != 0.0):
            raise ValueError("Stage-2 sample mask has post-terminal entries")
        if not np.array_equal(
            transition_mask[environment, :valid],
            np.ones((valid,), dtype=transition_mask.dtype),
        ):
            raise ValueError("Stage-2 transition-mask active prefix is not exact one")
        if np.any(transition_mask[environment, valid:] != 0.0):
            raise ValueError("Stage-2 transition mask has post-terminal entries")
        expected_done = np.zeros((EPISODE_TICKS,), dtype=done.dtype)
        expected_done[int(done_indices[0])] = 1.0
        if not np.array_equal(done[environment], expected_done):
            raise ValueError("Stage-2 done mask is not exact one-hot")


def validate_log_std(parameters: Mapping[str, Any]) -> None:
    value = np.asarray(parameters["training_only_log_std"])
    if not np.all(np.isfinite(value)):
        raise FloatingPointError("Stage-2 log_std is nonfinite")
    if np.any(value < np.float32(training.LOG_STD_MIN)) or np.any(
        value > np.float32(training.LOG_STD_MAX)
    ):
        raise ValueError("Stage-2 log_std clamp changed")


@contextmanager
def frozen_rollout_context(update_index: int):
    old_count = smoke.SMOKE_ENVIRONMENTS
    old_ticks = smoke.SMOKE_TICKS
    old_prng = smoke.prng_for

    def bound_prng(stage: int, environment: int):
        return prng_for_update(stage, update_index, environment)

    smoke.SMOKE_ENVIRONMENTS = 80
    smoke.SMOKE_TICKS = EPISODE_TICKS
    smoke.prng_for = bound_prng
    try:
        yield
    finally:
        smoke.SMOKE_ENVIRONMENTS = old_count
        smoke.SMOKE_TICKS = old_ticks
        smoke.prng_for = old_prng


def stage1_rollout(
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    update_index: int,
):
    with frozen_rollout_context(update_index):
        return smoke.stage1_rollout(
            mujoco, scene, population, design, observer_type, canonical_fit
        )


def validate_stage1_normalization(
    normalization: Mapping[str, Any], batch: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray]:
    """Validate the mixed-type receipt and return its numeric float32 arrays."""
    expected_keys = {
        "population",
        "heldout_rows",
        "dtype",
        "valid_rows",
        "mean_float64_sha256",
        "empirical_std_float64_sha256",
        "floored_std_float64_sha256",
        "floored_fields",
        "mean",
        "std",
    }
    if set(normalization) != expected_keys:
        raise ValueError("Stage-1 normalization schema changed")
    if normalization["population"] != "all valid Stage-1 smoke transitions only":
        raise ValueError("Stage-1 normalization population changed")
    if normalization["heldout_rows"] != 0:
        raise ValueError("heldout rows entered Stage-1 normalization")
    if normalization["dtype"] != (
        "float64 population mean/std (ddof=0), floor 1e-6, cast float32"
    ):
        raise ValueError("Stage-1 normalization arithmetic changed")
    valid_mask = np.asarray(batch["valid_mask"], dtype=bool)
    valid_targets = np.asarray(batch["targets"])[valid_mask].astype(np.float64)
    if valid_targets.size == 0:
        raise ValueError("Stage-1 normalization has no valid targets")
    if normalization["valid_rows"] != int(valid_targets.shape[0]):
        raise ValueError("Stage-1 normalization valid-row count changed")
    mean64 = np.mean(valid_targets, axis=0, dtype=np.float64)
    empirical_std64 = np.std(valid_targets, axis=0, dtype=np.float64, ddof=0)
    floored_std64 = np.maximum(empirical_std64, 1.0e-6)
    mean = np.asarray(normalization["mean"])
    std = np.asarray(normalization["std"])
    expected_shape = (int(training.AUXILIARY_INDICES.size),)
    if (
        mean.shape != expected_shape
        or std.shape != expected_shape
        or mean.dtype != np.dtype("float32")
        or std.dtype != np.dtype("float32")
    ):
        raise ValueError("Stage-1 normalization array layout changed")
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(std)):
        raise FloatingPointError("Stage-1 normalization contains nonfinite values")
    checks = {
        "mean_hash": normalization["mean_float64_sha256"] == smoke.array_sha256(mean64),
        "empirical_std_hash": normalization["empirical_std_float64_sha256"]
        == smoke.array_sha256(empirical_std64),
        "floored_std_hash": normalization["floored_std_float64_sha256"]
        == smoke.array_sha256(floored_std64),
        "floored_fields": normalization["floored_fields"]
        == int(np.sum(empirical_std64 < 1.0e-6)),
        "mean_float32": np.array_equal(mean, mean64.astype(np.float32)),
        "std_float32": np.array_equal(std, floored_std64.astype(np.float32)),
        "std_floor": bool(np.all(std >= np.float32(1.0e-6))),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"Stage-1 normalization proof failed: {failed}")
    return mean, std


def stage2_rollout(
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    parameters: Mapping[str, Any],
    update_index: int,
):
    captured: list[tuple[np.ndarray, np.ndarray]] = []
    original_step = smoke.Episode.step

    def captured_step(episode, action):
        captured.append(
            (
                np.asarray(episode.previous_action, dtype=np.float32).copy(),
                np.asarray(action, dtype=np.float32).copy(),
            )
        )
        return original_step(episode, action)

    with frozen_rollout_context(update_index):
        smoke.Episode.step = captured_step
        try:
            batch, episodes, observations = smoke.stage2_rollout(
                mujoco,
                scene,
                population,
                design,
                observer_type,
                canonical_fit,
                parameters,
            )
        finally:
            smoke.Episode.step = original_step
    active = np.asarray(batch["valid_mask"], dtype=bool)
    if len(captured) != int(np.sum(active)):
        raise ValueError("Stage-2 action-capture count changed")
    previous_actions = np.zeros_like(batch["raw_samples"], dtype=np.float32)
    realized_actions = np.zeros_like(batch["raw_samples"], dtype=np.float32)
    cursor = 0
    for environment in range(active.shape[0]):
        for tick in np.flatnonzero(active[environment]):
            previous_actions[environment, tick] = captured[cursor][0]
            realized_actions[environment, tick] = captured[cursor][1]
            cursor += 1
    batch = dict(batch)
    batch["previous_actions"] = previous_actions
    batch["realized_actions"] = realized_actions
    return batch, episodes, observations


def stage2_action_boundary_evidence(
    batch: Mapping[str, np.ndarray],
) -> dict[str, Any]:
    import jax.numpy as jnp

    active = np.asarray(batch["valid_mask"], dtype=bool)
    raw = np.asarray(batch["raw_samples"], dtype=np.float32)[active]
    previous = np.asarray(batch["previous_actions"], dtype=np.float32)[active]
    realized = np.asarray(batch["realized_actions"], dtype=np.float32)[active]
    if raw.shape != previous.shape or raw.shape != realized.shape or raw.shape[0] == 0:
        raise ValueError("Stage-2 action-boundary evidence shape changed")
    expected_numpy = smoke.bounded_action_numpy(raw, previous)
    expected_jax = np.asarray(
        training.bounded_action(jnp.asarray(raw), jnp.asarray(previous)),
        dtype=np.float32,
    )
    return {
        "attempted_samples": int(raw.shape[0]),
        "raw_sha256": smoke.array_sha256(raw),
        "previous_action_sha256": smoke.array_sha256(previous),
        "realized_action_sha256": smoke.array_sha256(realized),
        "numpy_expected_sha256": smoke.array_sha256(expected_numpy),
        "jax_expected_sha256": smoke.array_sha256(expected_jax),
        "realized_equals_numpy_bit_exact": bool(
            np.array_equal(realized, expected_numpy)
        ),
        "numpy_equals_jax_bit_exact": bool(
            np.array_equal(expected_numpy, expected_jax)
        ),
        "maximum_realized_numpy_error": float(
            np.max(np.abs(realized - expected_numpy))
        ),
        "maximum_numpy_jax_error": float(np.max(np.abs(expected_numpy - expected_jax))),
    }


def _numeric_state_arrays(
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    target_mean: np.ndarray | None,
    target_std: np.ndarray | None,
) -> dict[str, np.ndarray]:
    arrays = {
        f"parameter.{key}": np.asarray(value)
        for key, value in sorted(parameters.items())
    }
    arrays["optimizer.count"] = np.asarray(optimizer["count"])
    for moment in ("m", "v"):
        arrays.update(
            {
                f"optimizer.{moment}.{key}": np.asarray(value)
                for key, value in sorted(optimizer[moment].items())
            }
        )
    if target_mean is not None and target_std is not None:
        arrays["target_mean"] = np.asarray(target_mean, dtype=np.float32)
        arrays["target_std"] = np.asarray(target_std, dtype=np.float32)
    return arrays


def array_manifest_sha256(arrays: Mapping[str, Any]) -> str:
    manifest = {
        name: {
            "dtype": str(np.asarray(value).dtype),
            "shape": list(np.asarray(value).shape),
            "sha256": smoke.array_sha256(value),
        }
        for name, value in sorted(arrays.items())
    }
    return smoke.canonical_sha256(manifest)


def _state_arrays(
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    metadata: Mapping[str, Any],
    target_mean: np.ndarray | None,
    target_std: np.ndarray | None,
) -> dict[str, np.ndarray]:
    arrays = _numeric_state_arrays(parameters, optimizer, target_mean, target_std)
    protected_metadata = dict(metadata)
    protected_metadata.pop("state_payload_sha256", None)
    protected_metadata.pop("metadata_payload_sha256", None)
    protected_metadata["state_payload_sha256"] = array_manifest_sha256(arrays)
    protected_metadata["metadata_payload_sha256"] = smoke.canonical_sha256(
        protected_metadata
    )
    arrays["metadata_json"] = np.asarray(
        json.dumps(
            protected_metadata,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return arrays


def save_snapshot(
    path: Path,
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    metadata: Mapping[str, Any],
    target_mean: np.ndarray | None,
    target_std: np.ndarray | None,
) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite committed snapshot: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending.npz")
    if temporary.exists():
        raise FileExistsError(f"stale pending snapshot exists: {temporary}")
    arrays = _state_arrays(parameters, optimizer, metadata, target_mean, target_std)
    with temporary.open("xb") as stream:
        np.savez_compressed(stream, **arrays)
        stream.flush()
        os.fsync(stream.fileno())
    with np.load(temporary, allow_pickle=False) as archive:
        readback = {name: archive[name].copy() for name in archive.files}
    if set(readback) != set(arrays) or not all(
        np.array_equal(readback[name], arrays[name]) for name in arrays
    ):
        raise ValueError("snapshot readback is not bit-exact")
    temporary.replace(path)
    return {
        "path": str(path),
        "sha256": smoke.sha256(path),
        "bytes": path.stat().st_size,
        "array_count": len(arrays),
        "bit_exact_readback": True,
    }


def replace_latest_snapshot(source: Path, latest: Path) -> None:
    pointer = latest.with_name(latest.name + ".pending")
    if pointer.exists():
        raise FileExistsError(f"stale latest-snapshot pointer exists: {pointer}")
    pointer.write_bytes(source.read_bytes())
    if smoke.sha256(pointer) != smoke.sha256(source):
        raise ValueError("latest-snapshot pointer copy changed bytes")
    pointer.replace(latest)


def ensure_snapshot_receipt(path: Path) -> dict[str, Any]:
    snapshot = load_snapshot(path)
    validate_resume(snapshot)
    receipt = {
        "schema_version": "winner_v12.full_calibrator_snapshot_receipt.v1",
        "path": str(path),
        "sha256": smoke.sha256(path),
        "bytes": path.stat().st_size,
        "stage": snapshot["metadata"]["stage"],
        "completed_updates": snapshot["metadata"]["completed_updates"],
        "optimizer_count": int(np.asarray(snapshot["optimizer"]["count"])),
        "state_payload_sha256": snapshot["metadata"]["state_payload_sha256"],
        "metadata_payload_sha256": snapshot["metadata"]["metadata_payload_sha256"],
    }
    receipt_path = path.with_suffix(".receipt.json")
    if receipt_path.exists():
        if json.loads(receipt_path.read_text(encoding="utf-8")) != receipt:
            raise ValueError(f"snapshot receipt changed: {receipt_path}")
    else:
        write_json_exclusive(receipt_path, receipt)
    return receipt


def newest_committed_snapshot(work_root: Path) -> Path:
    candidates: list[tuple[int, Path]] = []
    for path in sorted((work_root / "snapshots").iterdir()):
        if not path.is_file() or COMMITTED_SNAPSHOT_RE.fullmatch(path.name) is None:
            continue
        snapshot = load_snapshot(path)
        validate_resume(snapshot)
        validate_stage2_lineage(snapshot, work_root)
        ensure_snapshot_receipt(path)
        metadata = snapshot["metadata"]
        stage = metadata["stage"]
        completed = int(metadata["completed_updates"])
        order = completed if stage == "stage1" else STAGE1_UPDATES + 1 + completed
        candidates.append((order, path))
    if not candidates:
        raise FileNotFoundError("no committed per-update snapshot exists")
    candidates.sort(key=lambda item: (item[0], item[1].name))
    if len(candidates) > 1 and candidates[-1][0] == candidates[-2][0]:
        raise ValueError("multiple committed snapshots claim the newest update")
    return candidates[-1][1]


def load_snapshot(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as archive:
        if len(archive.files) != len(set(archive.files)):
            raise ValueError("snapshot archive contains duplicate members")
        arrays = {name: archive[name].copy() for name in archive.files}
    if "metadata_json" not in arrays:
        raise ValueError("snapshot metadata member is absent")
    metadata_array = np.asarray(arrays.pop("metadata_json"))
    if metadata_array.shape != () or metadata_array.dtype.kind != "U":
        raise ValueError("snapshot metadata member layout changed")
    metadata = json.loads(str(metadata_array.item()))
    if not isinstance(metadata, dict):
        raise ValueError("snapshot metadata is not an object")
    stage = metadata.get("stage")
    if stage not in {"stage1", "stage2"}:
        raise ValueError("snapshot stage is invalid")
    parameter_keys = set(training.initialize_training_parameters(seed=PARAMETER_SEED))
    optimizer_keys = (
        set(training.ENCODER_AUXILIARY_KEYS)
        if stage == "stage1"
        else set(training.DEPLOYABLE_ACTION_KEYS + training.TRAINING_ONLY_STAGE2_KEYS)
    )
    expected_members = {
        "target_mean",
        "target_std",
        "optimizer.count",
        *(f"parameter.{key}" for key in parameter_keys),
        *(f"optimizer.m.{key}" for key in optimizer_keys),
        *(f"optimizer.v.{key}" for key in optimizer_keys),
    }
    if set(arrays) != expected_members:
        raise ValueError("snapshot archive member schema changed")
    parameters = {
        name.removeprefix("parameter."): value
        for name, value in arrays.items()
        if name.startswith("parameter.")
    }
    optimizer = {
        "count": arrays["optimizer.count"],
        "m": {
            name.removeprefix("optimizer.m."): value
            for name, value in arrays.items()
            if name.startswith("optimizer.m.")
        },
        "v": {
            name.removeprefix("optimizer.v."): value
            for name, value in arrays.items()
            if name.startswith("optimizer.v.")
        },
    }
    return {
        "parameters": parameters,
        "optimizer": optimizer,
        "metadata": metadata,
        "target_mean": arrays["target_mean"],
        "target_std": arrays["target_std"],
    }


def snapshot_metadata(
    *,
    stage: str,
    completed_updates: int,
    metrics: list[dict[str, Any]],
    sampled_count: int,
    valid_count: int,
    frozen_stage1_tree_sha256: str | None,
) -> dict[str, Any]:
    scheduled_tick_slots = completed_updates * SCHEDULED_TICK_SLOTS_PER_UPDATE
    return {
        "schema_version": "winner_v12.full_calibrator_snapshot.v1",
        "logical_run_id": "winner-v12-full-calibrator-seed-120120",
        "stage": stage,
        "completed_updates": completed_updates,
        "root_seed": ROOT_SEED,
        "parameter_seed": PARAMETER_SEED,
        "preregistration_lf_sha256": smoke.lf_sha256(PREREGISTRATION),
        "cpu_contract_lf_sha256": smoke.lf_sha256(CPU_CONTRACT),
        "cpu_contract_result_sha256": smoke.sha256(CPU_RESULT),
        "runner_lf_sha256": smoke.lf_sha256(Path(__file__)),
        "metrics": metrics,
        "stage_scheduled_tick_slots": scheduled_tick_slots,
        "total_scheduled_tick_slots": (
            scheduled_tick_slots
            if stage == "stage1"
            else STAGE1_UPDATES * SCHEDULED_TICK_SLOTS_PER_UPDATE + scheduled_tick_slots
        ),
        "cumulative_sampled_count": sampled_count,
        "cumulative_valid_transition_count": valid_count,
        "frozen_stage1_tree_sha256": frozen_stage1_tree_sha256,
    }


def validate_resume(snapshot: Mapping[str, Any]) -> None:
    if set(snapshot) != {
        "parameters",
        "optimizer",
        "metadata",
        "target_mean",
        "target_std",
    }:
        raise ValueError("snapshot decoded-state schema changed")
    metadata = snapshot["metadata"]
    if not isinstance(metadata, Mapping) or set(metadata) != SNAPSHOT_METADATA_KEYS:
        raise ValueError("snapshot metadata schema changed")
    for key in (
        "completed_updates",
        "root_seed",
        "parameter_seed",
        "stage_scheduled_tick_slots",
        "total_scheduled_tick_slots",
        "cumulative_sampled_count",
        "cumulative_valid_transition_count",
    ):
        if type(metadata[key]) is not int:
            raise ValueError(f"snapshot metadata integer type changed: {key}")
    expected_state_hash = array_manifest_sha256(
        _numeric_state_arrays(
            snapshot["parameters"],
            snapshot["optimizer"],
            snapshot["target_mean"],
            snapshot["target_std"],
        )
    )
    if metadata.get("state_payload_sha256") != expected_state_hash:
        raise ValueError("snapshot numeric-state payload hash changed")
    metadata_for_hash = dict(metadata)
    observed_metadata_hash = metadata_for_hash.pop("metadata_payload_sha256", None)
    if observed_metadata_hash != smoke.canonical_sha256(metadata_for_hash):
        raise ValueError("snapshot metadata payload hash changed")
    if metadata.get("schema_version") != "winner_v12.full_calibrator_snapshot.v1":
        raise ValueError("snapshot schema changed")
    if metadata.get("logical_run_id") != "winner-v12-full-calibrator-seed-120120":
        raise ValueError("snapshot logical run changed")
    if (
        metadata.get("root_seed") != ROOT_SEED
        or metadata.get("parameter_seed") != PARAMETER_SEED
    ):
        raise ValueError("snapshot seed changed")
    if metadata.get("preregistration_lf_sha256") != smoke.lf_sha256(PREREGISTRATION):
        raise ValueError("snapshot preregistration changed")
    if metadata.get("cpu_contract_lf_sha256") != smoke.lf_sha256(CPU_CONTRACT):
        raise ValueError("snapshot CPU contract changed")
    if metadata.get("cpu_contract_result_sha256") != smoke.sha256(CPU_RESULT):
        raise ValueError("snapshot CPU contract result changed")
    if metadata.get("runner_lf_sha256") != smoke.lf_sha256(Path(__file__)):
        raise ValueError("snapshot runner source changed")
    stage = metadata.get("stage")
    count = int(metadata.get("completed_updates", -1))
    if stage == "stage1" and not (0 <= count <= STAGE1_UPDATES):
        raise ValueError("snapshot Stage-1 counter is invalid")
    if stage == "stage2" and not (0 <= count <= STAGE2_UPDATES):
        raise ValueError("snapshot Stage-2 counter is invalid")
    if stage not in {"stage1", "stage2"}:
        raise ValueError("snapshot stage is invalid")
    scheduled = count * SCHEDULED_TICK_SLOTS_PER_UPDATE
    if metadata.get("stage_scheduled_tick_slots") != scheduled:
        raise ValueError("snapshot stage scheduled-slot count changed")
    expected_total = (
        scheduled
        if stage == "stage1"
        else STAGE1_UPDATES * SCHEDULED_TICK_SLOTS_PER_UPDATE + scheduled
    )
    if metadata.get("total_scheduled_tick_slots") != expected_total:
        raise ValueError("snapshot total scheduled-slot count changed")
    initial_parameters = training.initialize_training_parameters(seed=PARAMETER_SEED)
    expected_keys = set(initial_parameters)
    if set(snapshot["parameters"]) != expected_keys:
        raise ValueError("snapshot parameter schema changed")
    for key, value in snapshot["parameters"].items():
        expected = np.asarray(initial_parameters[key])
        observed = np.asarray(value)
        if observed.shape != expected.shape or observed.dtype != expected.dtype:
            raise ValueError(f"snapshot parameter layout changed: {key}")
    optimizer_keys = (
        set(training.ENCODER_AUXILIARY_KEYS)
        if stage == "stage1"
        else set(training.DEPLOYABLE_ACTION_KEYS + training.TRAINING_ONLY_STAGE2_KEYS)
    )
    optimizer = snapshot["optimizer"]
    if not isinstance(optimizer, Mapping) or set(optimizer) != {"count", "m", "v"}:
        raise ValueError("snapshot optimizer container schema changed")
    if set(optimizer["m"]) != optimizer_keys or set(optimizer["v"]) != optimizer_keys:
        raise ValueError("snapshot optimizer schema changed")
    if int(np.asarray(optimizer["count"])) != count:
        raise ValueError("snapshot optimizer count changed")
    if np.asarray(optimizer["count"]).shape != () or np.asarray(
        optimizer["count"]
    ).dtype != np.dtype("int32"):
        raise ValueError("snapshot optimizer counter layout changed")
    for moment in ("m", "v"):
        for key, value in optimizer[moment].items():
            expected = np.asarray(snapshot["parameters"][key])
            observed = np.asarray(value)
            if observed.shape != expected.shape or observed.dtype != expected.dtype:
                raise ValueError(f"snapshot optimizer layout changed: {moment}.{key}")
    if not training.finite_tree(
        {
            "parameters": snapshot["parameters"],
            "optimizer": optimizer,
            "target_mean": snapshot["target_mean"],
            "target_std": snapshot["target_std"],
        }
    ):
        raise FloatingPointError("snapshot contains nonfinite state")
    target_mean = snapshot["target_mean"]
    target_std = snapshot["target_std"]
    if target_mean is None or target_std is None:
        raise ValueError("snapshot frozen normalization is absent")
    expected_target_shape = (int(training.AUXILIARY_INDICES.size),)
    if (
        target_mean.shape != expected_target_shape
        or target_std.shape != expected_target_shape
    ):
        raise ValueError("snapshot frozen normalization shape changed")
    if target_mean.dtype != np.dtype("float32") or target_std.dtype != np.dtype(
        "float32"
    ):
        raise ValueError("snapshot frozen normalization dtype changed")
    if np.any(target_std < np.float32(1.0e-6)):
        raise ValueError("snapshot frozen normalization floor changed")
    target_mean_sha256 = smoke.array_sha256(target_mean)
    target_std_sha256 = smoke.array_sha256(target_std)
    observed_stage1_hash = smoke.tree_sha256(
        training.stage1_parameters(snapshot["parameters"])
    )
    frozen_stage1_hash = metadata.get("frozen_stage1_tree_sha256")
    if stage == "stage2" and frozen_stage1_hash != observed_stage1_hash:
        raise ValueError("snapshot frozen Stage-1 tree changed")
    if stage == "stage1" and frozen_stage1_hash is not None:
        raise ValueError("Stage-1 snapshot claims a frozen Stage-1 tree")
    if stage == "stage1" and any(
        not np.array_equal(
            np.asarray(snapshot["parameters"][key]), np.asarray(initial_parameters[key])
        )
        for key in training.DEPLOYABLE_ACTION_KEYS + training.TRAINING_ONLY_STAGE2_KEYS
    ):
        raise ValueError("Stage-1 snapshot changed frozen Stage-2 leaves")
    metrics = metadata.get("metrics")
    expected_metric_count = count if stage == "stage1" else STAGE1_UPDATES + count
    if not isinstance(metrics, list) or len(metrics) != expected_metric_count:
        raise ValueError("snapshot metric-history length changed")
    for row in metrics:
        if not isinstance(row, Mapping) or row.get("stage") not in {"stage1", "stage2"}:
            raise ValueError("snapshot metric row is malformed")
        expected_row_keys = (
            STAGE1_METRIC_KEYS if row["stage"] == "stage1" else STAGE2_METRIC_KEYS
        )
        if set(row) != expected_row_keys:
            raise ValueError("snapshot metric-row schema changed")
    expected_pairs = (
        [
            *(("stage1", update) for update in range(1, STAGE1_UPDATES + 1)),
            *(("stage2", update) for update in range(1, count + 1)),
        ]
        if stage == "stage2"
        else [("stage1", update) for update in range(1, count + 1)]
    )
    observed_pairs = [(row.get("stage"), row.get("update")) for row in metrics]
    if observed_pairs != expected_pairs:
        raise ValueError("snapshot metric-history order changed")
    metric_sampled = sum(int(row["sampled_count"]) for row in metrics)
    metric_valid = sum(int(row["valid_transition_count"]) for row in metrics)
    if metadata.get("cumulative_sampled_count") != metric_sampled:
        raise ValueError("snapshot cumulative sample count changed")
    if metadata.get("cumulative_valid_transition_count") != metric_valid:
        raise ValueError("snapshot cumulative valid-transition count changed")
    if not (0 < metric_valid <= metric_sampled <= expected_total):
        raise ValueError("snapshot cumulative sample accounting is invalid")
    for row in metrics:
        if type(row["update"]) is not int:
            raise ValueError("snapshot metric update type changed")
        if (
            type(row["sampled_count"]) is not int
            or type(row["valid_transition_count"]) is not int
        ):
            raise ValueError("snapshot metric sample-count type changed")
        if type(row["completed_episodes"]) is not int:
            raise ValueError("snapshot completed-episode type changed")
        if not np.isfinite(float(row["loss"])):
            raise FloatingPointError("snapshot metric loss is nonfinite")
        sampled = int(row["sampled_count"])
        valid = int(row["valid_transition_count"])
        if not (0 < valid <= sampled <= SCHEDULED_TICK_SLOTS_PER_UPDATE):
            raise ValueError("snapshot per-update sample accounting is invalid")
        if not (0 <= int(row["completed_episodes"]) <= 80):
            raise ValueError("snapshot completed-episode count is invalid")
        if SHA256_RE.fullmatch(str(row["episode_receipts_sha256"])) is None:
            raise ValueError("snapshot episode-receipt hash is absent")
        if row["stage"] == "stage1" and (
            row.get("frozen_target_mean_sha256") != target_mean_sha256
            or row.get("frozen_target_std_sha256") != target_std_sha256
        ):
            raise ValueError("snapshot Stage-1 normalization lineage changed")
        if row["stage"] == "stage2":
            if any(not np.isfinite(float(row[key])) for key in STAGE2_LOSS_METRIC_KEYS):
                raise FloatingPointError("snapshot Stage-2 metric is nonfinite")
            boundary = row["action_boundary"]
            if (
                not isinstance(boundary, Mapping)
                or set(boundary) != ACTION_BOUNDARY_KEYS
            ):
                raise ValueError("snapshot Stage-2 action-boundary schema changed")
            if type(boundary["attempted_samples"]) is not int:
                raise ValueError("snapshot Stage-2 action-boundary count type changed")
            if (
                type(boundary["realized_equals_numpy_bit_exact"]) is not bool
                or type(boundary["numpy_equals_jax_bit_exact"]) is not bool
            ):
                raise ValueError(
                    "snapshot Stage-2 action-boundary boolean type changed"
                )
            if not np.isfinite(
                float(boundary["maximum_realized_numpy_error"])
            ) or not np.isfinite(float(boundary["maximum_numpy_jax_error"])):
                raise FloatingPointError(
                    "snapshot Stage-2 action-boundary error is nonfinite"
                )
            if (
                boundary.get("attempted_samples") != sampled
                or boundary.get("realized_equals_numpy_bit_exact") is not True
                or boundary.get("numpy_equals_jax_bit_exact") is not True
                or boundary.get("maximum_realized_numpy_error") != 0.0
                or boundary.get("maximum_numpy_jax_error") != 0.0
            ):
                raise ValueError("snapshot Stage-2 action-boundary evidence changed")
            if any(
                SHA256_RE.fullmatch(str(boundary[key])) is None
                for key in (
                    "raw_sha256",
                    "previous_action_sha256",
                    "realized_action_sha256",
                    "numpy_expected_sha256",
                    "jax_expected_sha256",
                )
            ):
                raise ValueError("snapshot Stage-2 action-boundary hash changed")
    for key in (
        "preregistration_lf_sha256",
        "cpu_contract_lf_sha256",
        "cpu_contract_result_sha256",
        "runner_lf_sha256",
        "state_payload_sha256",
        "metadata_payload_sha256",
    ):
        if SHA256_RE.fullmatch(str(metadata[key])) is None:
            raise ValueError(f"snapshot metadata hash is malformed: {key}")


def validate_stage2_lineage(snapshot: Mapping[str, Any], work_root: Path) -> None:
    if snapshot["metadata"]["stage"] != "stage2":
        return
    stage1_path = work_root / "snapshots" / "snapshot_stage1_update_100.npz"
    if not stage1_path.is_file():
        raise FileNotFoundError("Stage-2 snapshot lacks Stage-1 final lineage")
    stage1_snapshot = load_snapshot(stage1_path)
    validate_resume(stage1_snapshot)
    expected_hash = smoke.tree_sha256(
        training.stage1_parameters(stage1_snapshot["parameters"])
    )
    if snapshot["metadata"]["frozen_stage1_tree_sha256"] != expected_hash:
        raise ValueError("Stage-2 encoder differs from independent Stage-1 final state")
    if not np.array_equal(snapshot["target_mean"], stage1_snapshot["target_mean"]):
        raise ValueError("Stage-2 target mean differs from Stage-1 final state")
    if not np.array_equal(snapshot["target_std"], stage1_snapshot["target_std"]):
        raise ValueError("Stage-2 target std differs from Stage-1 final state")


def persist_update(
    work_root: Path,
    *,
    stage: str,
    completed_updates: int,
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    metrics: list[dict[str, Any]],
    sampled_count: int,
    valid_count: int,
    target_mean: np.ndarray | None,
    target_std: np.ndarray | None,
    frozen_stage1_tree_sha256: str | None,
) -> dict[str, Any]:
    name = f"snapshot_{stage}_update_{completed_updates:03d}.npz"
    path = work_root / "snapshots" / name
    receipt = save_snapshot(
        path,
        parameters,
        optimizer,
        snapshot_metadata(
            stage=stage,
            completed_updates=completed_updates,
            metrics=metrics,
            sampled_count=sampled_count,
            valid_count=valid_count,
            frozen_stage1_tree_sha256=frozen_stage1_tree_sha256,
        ),
        target_mean,
        target_std,
    )
    committed = load_snapshot(path)
    validate_resume(committed)
    validate_stage2_lineage(committed, work_root)
    if ensure_snapshot_receipt(path)["sha256"] != receipt["sha256"]:
        raise ValueError("committed snapshot receipt hash mismatch")
    replace_latest_snapshot(path, work_root / SNAPSHOT_NAME)
    return receipt


def write_json_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(path.name + ".pending")
    if temporary.exists():
        raise FileExistsError(temporary)
    with temporary.open("x", encoding="utf-8") as stream:
        stream.write(
            json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n"
        )
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def pending_final_target(path: Path) -> Path | None:
    name = path.name
    if name.endswith(".pending.npz"):
        return path.with_name(name.removesuffix(".pending.npz"))
    if name.endswith(".pending.onnx"):
        return path.with_name(name.removesuffix(".pending.onnx"))
    if name.endswith(".pending"):
        return path.with_name(name.removesuffix(".pending"))
    return None


def quarantine_uncommitted_pending(work_root: Path) -> dict[str, Any] | None:
    work_root = work_root.resolve()
    quarantine_root = work_root / "recovery_quarantine"
    candidates = []
    for path in sorted(work_root.rglob("*")):
        if quarantine_root in path.parents:
            continue
        target = pending_final_target(path)
        if target is not None:
            candidates.append((path, target))
    if not candidates:
        return None
    quarantine_root.mkdir(parents=True, exist_ok=True)
    entries = []
    for path, target in candidates:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"pending recovery encountered a non-regular file: {path}")
        if os.path.commonpath((str(work_root), str(path.resolve()))) != str(work_root):
            raise ValueError("pending recovery path escaped the work root")
        relative = path.relative_to(work_root)
        digest = smoke.sha256(path)
        safe_name = "__".join(relative.parts).replace(".pending", "_pending_")
        destination = quarantine_root / f"{safe_name}.{digest[:16]}.uncommitted"
        suffix = 1
        while destination.exists():
            destination = quarantine_root / (
                f"{safe_name}.{digest[:16]}.{suffix}.uncommitted"
            )
            suffix += 1
        entry = {
            "original_path": str(path),
            "final_target": str(target),
            "final_target_exists": target.exists(),
            "sha256": digest,
            "bytes": path.stat().st_size,
            "quarantined_path": str(destination),
        }
        path.replace(destination)
        if smoke.sha256(destination) != digest:
            raise ValueError("quarantined pending artifact changed bytes")
        entries.append(entry)
    receipt = {
        "schema_version": "winner_v12.full_calibrator_recovery_event.v1",
        "policy": "pending artifacts are never committed and are quarantined before replay from the newest committed snapshot",
        "entries": entries,
    }
    receipt_path = work_root / f"recovery_event_{time.time_ns()}.json"
    write_json_exclusive(receipt_path, receipt)
    return receipt


def recovery_event_receipts(work_root: Path) -> list[dict[str, Any]]:
    receipts = []
    for path in sorted(work_root.glob("recovery_event_*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if (
            value.get("schema_version")
            != "winner_v12.full_calibrator_recovery_event.v1"
        ):
            raise ValueError("recovery-event schema changed")
        receipts.append(
            {
                "path": str(path),
                "sha256": smoke.sha256(path),
                "bytes": path.stat().st_size,
                "event": value,
            }
        )
    return receipts


def tree_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def state_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        tree_equal(left["parameters"], right["parameters"])
        and tree_equal(left["optimizer"]["m"], right["optimizer"]["m"])
        and tree_equal(left["optimizer"]["v"], right["optimizer"]["v"])
        and np.array_equal(left["optimizer"]["count"], right["optimizer"]["count"])
        and left["metadata"] == right["metadata"]
        and np.array_equal(left["target_mean"], right["target_mean"])
        and np.array_equal(left["target_std"], right["target_std"])
    )


def archive_array_count(path: Path) -> int:
    with np.load(path, allow_pickle=False) as archive:
        return len(archive.files)


def ensure_stage1_final_checkpoint(work_root: Path) -> dict[str, Any]:
    snapshot_path = work_root / "snapshots" / "snapshot_stage1_update_100.npz"
    snapshot = load_snapshot(snapshot_path)
    validate_resume(snapshot)
    validate_stage2_lineage(snapshot, work_root)
    if (
        snapshot["metadata"]["stage"] != "stage1"
        or int(snapshot["metadata"]["completed_updates"]) != STAGE1_UPDATES
    ):
        raise ValueError("Stage-1 final source snapshot counter changed")
    checkpoint_path = work_root / "winner_v12_calibrator_stage1_final.npz"
    if checkpoint_path.exists():
        checkpoint_state = load_snapshot(checkpoint_path)
        if not state_equal(checkpoint_state, snapshot):
            raise ValueError("Stage-1 final checkpoint state changed")
        checkpoint = {
            "path": str(checkpoint_path),
            "sha256": smoke.sha256(checkpoint_path),
            "bytes": checkpoint_path.stat().st_size,
            "array_count": archive_array_count(checkpoint_path),
            "bit_exact_readback": True,
        }
    else:
        checkpoint = save_snapshot(
            checkpoint_path,
            snapshot["parameters"],
            snapshot["optimizer"],
            snapshot["metadata"],
            snapshot["target_mean"],
            snapshot["target_std"],
        )
    receipt = {
        "label": "stage1_final",
        "update": STAGE1_UPDATES,
        "source_snapshot": {
            "path": str(snapshot_path),
            "sha256": smoke.sha256(snapshot_path),
        },
        "checkpoint": checkpoint,
    }
    receipt_path = work_root / "winner_v12_calibrator_stage1_final_receipt.json"
    if receipt_path.exists():
        if json.loads(receipt_path.read_text(encoding="utf-8")) != receipt:
            raise ValueError("Stage-1 final receipt changed")
    else:
        write_json_exclusive(receipt_path, receipt)
    return receipt


def ensure_persistent_artifact(
    work_root: Path, label: str, update: int
) -> dict[str, Any]:
    snapshot_path = work_root / "snapshots" / f"snapshot_stage2_update_{update:03d}.npz"
    snapshot = load_snapshot(snapshot_path)
    validate_resume(snapshot)
    validate_stage2_lineage(snapshot, work_root)
    if (
        snapshot["metadata"]["stage"] != "stage2"
        or int(snapshot["metadata"]["completed_updates"]) != update
    ):
        raise ValueError(f"persistent {label} source snapshot counter changed")
    parameters = snapshot["parameters"]
    optimizer = snapshot["optimizer"]
    checkpoint_path = work_root / f"winner_v12_calibrator_{label}.npz"
    if checkpoint_path.exists():
        checkpoint_state = load_snapshot(checkpoint_path)
        if not state_equal(checkpoint_state, snapshot):
            raise ValueError(f"persistent {label} checkpoint state changed")
        checkpoint = {
            "path": str(checkpoint_path),
            "sha256": smoke.sha256(checkpoint_path),
            "bytes": checkpoint_path.stat().st_size,
            "array_count": archive_array_count(checkpoint_path),
            "bit_exact_readback": True,
        }
    else:
        checkpoint = save_snapshot(
            checkpoint_path,
            parameters,
            optimizer,
            snapshot["metadata"],
            snapshot["target_mean"],
            snapshot["target_std"],
        )
    graph_path = work_root / f"winner_v12_calibrator_{label}.onnx"
    if not graph_path.exists():
        pending_graph = graph_path.with_name(graph_path.name + ".pending.onnx")
        if pending_graph.exists():
            raise FileExistsError(pending_graph)
        smoke.networks.export_calibrator_onnx(
            training.deployable_parameters(parameters), pending_graph
        )
        pending_graph.replace(graph_path)
    flat = np.arange(EPISODE_TICKS * training.OBS_SIZE, dtype=np.int64)
    observations = (
        ((flat + update * 17) % 257).astype(np.float32) - np.float32(128.0)
    ).reshape(EPISODE_TICKS, training.OBS_SIZE) / np.float32(128.0)
    if np.count_nonzero(observations) < observations.size - EPISODE_TICKS:
        raise AssertionError("persistent ONNX observation bank lost nonzero coverage")
    graph = smoke.onnx_contract(
        graph_path,
        training.deployable_parameters(parameters),
        observations,
    )
    if not all(
        graph[key]
        for key in (
            "abi_exact",
            "all_initializers_finite",
            "all_chain_outputs_finite",
            "training_only_tensors_absent",
            "jax_onnx_at_most_1e_7",
            "previous_action_out_equals_action_bit_exact",
        )
    ):
        raise ValueError(f"persistent {label} ONNX contract failed")
    receipt = {
        "label": label,
        "update": update,
        "source_snapshot": {
            "path": str(snapshot_path),
            "sha256": smoke.sha256(snapshot_path),
        },
        "checkpoint": checkpoint,
        "graph": graph,
        "onnx_observation_bank": {
            "construction": "((arange(250*115) + update*17) % 257 - 128) / 128 as float32",
            "shape": list(observations.shape),
            "sha256": smoke.array_sha256(observations),
            "all_finite": bool(np.all(np.isfinite(observations))),
            "nonzero_values": int(np.count_nonzero(observations)),
        },
    }
    receipt_path = work_root / f"winner_v12_calibrator_{label}_receipt.json"
    if receipt_path.exists():
        observed = json.loads(receipt_path.read_text(encoding="utf-8"))
        if observed != receipt:
            raise ValueError(f"persistent {label} receipt changed")
    else:
        write_json_exclusive(receipt_path, receipt)
    return receipt


def build_snapshot_manifest(work_root: Path) -> list[dict[str, Any]]:
    expected_names = {
        *(f"snapshot_stage1_update_{update:03d}.npz" for update in range(1, 101)),
        *(f"snapshot_stage2_update_{update:03d}.npz" for update in range(0, 101)),
    }
    observed_paths = sorted(
        path
        for path in (work_root / "snapshots").iterdir()
        if path.is_file() and COMMITTED_SNAPSHOT_RE.fullmatch(path.name) is not None
    )
    if {path.name for path in observed_paths} != expected_names:
        raise ValueError("immutable snapshot set is incomplete or contains extras")
    manifest = []
    for path in observed_paths:
        snapshot = load_snapshot(path)
        validate_resume(snapshot)
        validate_stage2_lineage(snapshot, work_root)
        manifest.append(ensure_snapshot_receipt(path))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--resume-snapshot", type=Path)
    parser.add_argument("--training-authorized", action="store_true")
    parser.add_argument("--offline-cpu-only", action="store_true")
    args = parser.parse_args()
    if not args.training_authorized or not args.offline_cpu_only:
        raise PermissionError(
            "full training requires --training-authorized --offline-cpu-only"
        )
    preregistration = load_preregistration()
    authority = validate_training_authority()
    cpu_result = authority["cpu_result"]
    claim = authority["claim"]
    if args.resume_snapshot is None:
        claim_receipt_payload(claim, args.work_root)
        if args.work_root.exists():
            if not args.work_root.is_dir():
                raise FileExistsError(
                    "authorized training work root is not a directory"
                )
            quarantine_uncommitted_pending(args.work_root)
            committed = (
                [
                    path
                    for path in (args.work_root / "snapshots").glob("*")
                    if path.is_file()
                    and COMMITTED_SNAPSHOT_RE.fullmatch(path.name) is not None
                ]
                if (args.work_root / "snapshots").is_dir()
                else []
            )
            if committed:
                raise ValueError("an existing committed run requires --resume-snapshot")
            allowed_names = {
                "snapshots",
                "recovery_quarantine",
                "winner_v12_full_calibrator_training_claim_receipt.json",
            }
            unexpected = [
                path.name
                for path in args.work_root.iterdir()
                if path.name not in allowed_names
                and not re.fullmatch(r"recovery_event_\d+\.json", path.name)
            ]
            if unexpected:
                raise ValueError(
                    f"pre-update authorized work root contains unexpected entries: {sorted(unexpected)}"
                )
            receipt_path = (
                args.work_root
                / "winner_v12_full_calibrator_training_claim_receipt.json"
            )
            consume_or_validate_claim(
                claim, args.work_root, fresh=not receipt_path.exists()
            )
        else:
            args.work_root.mkdir(parents=True)
            consume_or_validate_claim(claim, args.work_root, fresh=True)
    else:
        if not args.work_root.is_dir():
            raise FileNotFoundError("resume work root is absent")
        quarantine_uncommitted_pending(args.work_root)
        consume_or_validate_claim(claim, args.work_root, fresh=False)
        newest_resume_snapshot = newest_committed_snapshot(args.work_root)
        if args.resume_snapshot.resolve() != newest_resume_snapshot.resolve():
            raise ValueError("resume must use the newest committed per-update snapshot")
        replace_latest_snapshot(newest_resume_snapshot, args.work_root / SNAPSHOT_NAME)
    result_path = args.work_root / RESULT_NAME
    if result_path.exists():
        raise FileExistsError("full calibrator result already exists")

    smoke_contract = json.loads(smoke.DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    smoke.validate_contract(smoke_contract)
    expected_versions = dict(preregistration["implementation_contract_environment"])
    if expected_versions.pop("platform") != "CPU only":
        raise ValueError("implementation platform changed")
    software = smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )
    if not software["exact"]:
        raise ValueError("full training software versions changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("canonical P30 fit hash changed")
    if (
        smoke.git_output(args.playground_root, "rev-parse", "HEAD")
        != smoke.CONTROL_COMMIT
    ):
        raise ValueError("Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("training scene hash changed")

    import jax
    import jax.numpy as jnp
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("full calibrator training requires CPU-only JAX")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = training_population(preregistration, domain)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    start = time.monotonic()

    if args.resume_snapshot is None:
        parameters = training.initialize_training_parameters(seed=PARAMETER_SEED)
        if (
            smoke.tree_sha256(parameters)
            != preregistration["parameter_initialization"]["tree_sha256"]
        ):
            raise ValueError("initial parameter tree hash changed")
        stage = "stage1"
        completed = 0
        optimizer = training.adam_initialize(training.stage1_parameters(parameters))
        target_mean = None
        target_std = None
        metrics: list[dict[str, Any]] = []
        sampled_count = 0
        valid_count = 0
    else:
        restored = load_snapshot(args.resume_snapshot)
        validate_resume(restored)
        parameters = restored["parameters"]
        optimizer = restored["optimizer"]
        metadata = restored["metadata"]
        stage = metadata["stage"]
        completed = int(metadata["completed_updates"])
        target_mean = restored["target_mean"]
        target_std = restored["target_std"]
        metrics = list(metadata["metrics"])
        sampled_count = int(metadata["cumulative_sampled_count"])
        valid_count = int(metadata["cumulative_valid_transition_count"])

    initial = training.initialize_training_parameters(seed=PARAMETER_SEED)
    initial_stage2 = {
        key: np.asarray(initial[key]).copy()
        for key in training.DEPLOYABLE_ACTION_KEYS + training.TRAINING_ONLY_STAGE2_KEYS
    }
    stage1_loss_grad = jax.value_and_grad(training.stage1_loss)

    if stage == "stage1":
        for update_index in range(completed, STAGE1_UPDATES):
            batch_np, episodes, evidence = stage1_rollout(
                mujoco,
                scene,
                population,
                design,
                observer_type,
                args.canonical_fit,
                update_index,
            )
            normalization = evidence.pop("normalization")
            if not training.finite_tree({"batch": batch_np}):
                raise FloatingPointError(f"nonfinite Stage-1 rollout {update_index}")
            normalization_mean, normalization_std = validate_stage1_normalization(
                normalization, batch_np
            )
            if not evidence.get("realized_action_chain_exact"):
                raise ValueError("Stage-1 realized-action chain changed")
            if not evidence.get("fixed_p30_observer_slot_exact"):
                raise ValueError("Stage-1 fixed-P30 observation slot changed")
            episode_receipts_sha256 = validate_episode_receipts(
                episodes,
                population,
                stage=1,
                update_index=update_index,
            )
            if update_index == 0:
                target_mean = normalization_mean
                target_std = normalization_std
            if target_mean is None or target_std is None:
                raise AssertionError("Stage-1 normalization is absent")
            batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
            stage1_parameters = training.stage1_parameters(parameters)
            loss, gradients = stage1_loss_grad(
                stage1_parameters,
                batch,
                jnp.asarray(target_mean),
                jnp.asarray(target_std),
            )
            stage1_parameters, optimizer = training.adam_step(
                stage1_parameters,
                gradients,
                optimizer,
                learning_rate=training.STAGE1_LEARNING_RATE,
                beta1=training.ADAM_BETA1,
                beta2=training.ADAM_BETA2,
                epsilon=training.ADAM_EPSILON,
            )
            parameters = training.merge_stage1(parameters, stage1_parameters)
            if not training.finite_tree(
                {
                    "loss": loss,
                    "gradients": gradients,
                    "parameters": parameters,
                    "optimizer": optimizer,
                }
            ):
                raise FloatingPointError(f"nonfinite Stage-1 update {update_index}")
            if any(
                not np.array_equal(np.asarray(parameters[key]), initial_stage2[key])
                for key in initial_stage2
            ):
                raise ValueError("Stage-1 changed the frozen Stage-2 leaves")
            valid = int(np.sum(batch_np["valid_mask"]))
            if valid <= 0:
                raise ValueError("Stage-1 update has no valid transitions")
            sampled = sum(
                int(row["episode"]["valid_ticks"])
                + (1 if row["terminal"] is not None else 0)
                for row in episodes
            )
            if sampled < valid or sampled > SCHEDULED_TICK_SLOTS_PER_UPDATE:
                raise ValueError("Stage-1 sample accounting is invalid")
            sampled_count += sampled
            valid_count += valid
            metrics.append(
                {
                    "stage": "stage1",
                    "update": update_index + 1,
                    "loss": float(loss),
                    "sampled_count": sampled,
                    "valid_transition_count": valid,
                    "episode_receipts_sha256": episode_receipts_sha256,
                    "frozen_target_mean_sha256": smoke.array_sha256(target_mean),
                    "frozen_target_std_sha256": smoke.array_sha256(target_std),
                    "completed_episodes": sum(
                        row["episode"]["valid_ticks"] == EPISODE_TICKS
                        for row in episodes
                    ),
                }
            )
            persist_update(
                args.work_root,
                stage="stage1",
                completed_updates=update_index + 1,
                parameters=parameters,
                optimizer=optimizer,
                metrics=metrics,
                sampled_count=sampled_count,
                valid_count=valid_count,
                target_mean=target_mean,
                target_std=target_std,
                frozen_stage1_tree_sha256=None,
            )
        stage = "stage2"
        completed = 0
        if any(
            not np.array_equal(np.asarray(parameters[key]), initial_stage2[key])
            for key in initial_stage2
        ):
            raise ValueError("Stage-1 handoff changed initial Stage-2 leaves")
        stage1_final_receipt = ensure_stage1_final_checkpoint(args.work_root)
        frozen_stage1_hash = smoke.tree_sha256(training.stage1_parameters(parameters))
        stage2_parameters = training.stage2_parameters(parameters)
        optimizer = training.adam_initialize(stage2_parameters)
        persist_update(
            args.work_root,
            stage="stage2",
            completed_updates=0,
            parameters=parameters,
            optimizer=optimizer,
            metrics=metrics,
            sampled_count=sampled_count,
            valid_count=valid_count,
            target_mean=target_mean,
            target_std=target_std,
            frozen_stage1_tree_sha256=frozen_stage1_hash,
        )

    frozen_stage1_hash = smoke.tree_sha256(training.stage1_parameters(parameters))
    if stage != "stage2":
        raise AssertionError("training stage transition failed")
    stage1_final_receipt = ensure_stage1_final_checkpoint(args.work_root)

    def objective(stage2_parameters: Mapping[str, Any], batch: Mapping[str, Any]):
        return training.stage2_ppo_loss(
            stage2_parameters,
            batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    objective_grad = jax.value_and_grad(objective, has_aux=True)
    persistent_receipts = [
        ensure_persistent_artifact(args.work_root, label, update)
        for update, label in PERSISTENT.items()
        if completed >= update
    ]
    for update_index in range(completed, STAGE2_UPDATES):
        batch_np, episodes, _observations = stage2_rollout(
            mujoco,
            scene,
            population,
            design,
            observer_type,
            args.canonical_fit,
            parameters,
            update_index,
        )
        episode_receipts_sha256 = validate_episode_receipts(
            episodes,
            population,
            stage=2,
            update_index=update_index,
        )
        if not training.finite_tree(
            {"batch": batch_np, "onnx_observation_bank": _observations}
        ):
            raise FloatingPointError(f"nonfinite Stage-2 rollout {update_index}")
        validate_stage2_masks(batch_np, episodes)
        action_boundary = stage2_action_boundary_evidence(batch_np)
        if (
            not action_boundary["realized_equals_numpy_bit_exact"]
            or not action_boundary["numpy_equals_jax_bit_exact"]
        ):
            raise ValueError("Stage-2 raw-to-bounded action contract changed")
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
        stage2_parameters = training.stage2_parameters(parameters)
        (loss, loss_metrics), gradients = objective_grad(stage2_parameters, batch)
        stage2_parameters, optimizer = training.adam_step(
            stage2_parameters,
            gradients,
            optimizer,
            learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1,
            beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        stage2_parameters = training.clamp_stage2_parameters(stage2_parameters)
        validate_log_std(stage2_parameters)
        parameters = training.merge_stage2(parameters, stage2_parameters)
        if (
            smoke.tree_sha256(training.stage1_parameters(parameters))
            != frozen_stage1_hash
        ):
            raise ValueError("Stage-2 changed frozen Stage-1 leaves")
        if not training.finite_tree(
            {
                "loss": loss,
                "metrics": loss_metrics,
                "gradients": gradients,
                "parameters": parameters,
                "optimizer": optimizer,
            }
        ):
            raise FloatingPointError(f"nonfinite Stage-2 update {update_index}")
        sampled = int(np.sum(batch_np["valid_mask"]))
        valid = int(np.sum(batch_np["valid_transition_mask"]))
        if sampled < valid or valid <= 0:
            raise ValueError("Stage-2 sample accounting is invalid")
        sampled_count += sampled
        valid_count += valid
        metrics.append(
            {
                "stage": "stage2",
                "update": update_index + 1,
                "loss": float(loss),
                "sampled_count": sampled,
                "valid_transition_count": valid,
                "episode_receipts_sha256": episode_receipts_sha256,
                "action_boundary": action_boundary,
                "completed_episodes": sum(
                    row["episode"]["valid_ticks"] == EPISODE_TICKS for row in episodes
                ),
                **{key: float(value) for key, value in loss_metrics.items()},
            }
        )
        persist_update(
            args.work_root,
            stage="stage2",
            completed_updates=update_index + 1,
            parameters=parameters,
            optimizer=optimizer,
            metrics=metrics,
            sampled_count=sampled_count,
            valid_count=valid_count,
            target_mean=target_mean,
            target_std=target_std,
            frozen_stage1_tree_sha256=frozen_stage1_hash,
        )
        if update_index + 1 in PERSISTENT:
            label = PERSISTENT[update_index + 1]
            persistent_receipts.append(
                ensure_persistent_artifact(args.work_root, label, update_index + 1)
            )

    if [row["label"] for row in persistent_receipts] != ["half", "final"]:
        raise ValueError("persistent checkpoint set is incomplete")
    snapshot_manifest = build_snapshot_manifest(args.work_root)
    newest_snapshot = newest_committed_snapshot(args.work_root)
    expected_final_snapshot = (
        args.work_root / "snapshots" / "snapshot_stage2_update_100.npz"
    )
    if newest_snapshot.resolve() != expected_final_snapshot.resolve():
        raise ValueError("final immutable snapshot is not the newest committed state")
    latest_snapshot = args.work_root / SNAPSHOT_NAME
    replace_latest_snapshot(newest_snapshot, latest_snapshot)
    if smoke.sha256(latest_snapshot) != smoke.sha256(expected_final_snapshot):
        raise ValueError("latest-snapshot pointer differs from final committed state")
    artifact_manifest = {
        "authorization_claim_receipt": {
            "path": str(
                args.work_root
                / "winner_v12_full_calibrator_training_claim_receipt.json"
            ),
            "sha256": smoke.sha256(
                args.work_root
                / "winner_v12_full_calibrator_training_claim_receipt.json"
            ),
        },
        "stage1_final": stage1_final_receipt,
        "persistent": persistent_receipts,
        "snapshots": snapshot_manifest,
        "latest_snapshot": {
            "path": str(latest_snapshot),
            "sha256": smoke.sha256(latest_snapshot),
            "bytes": latest_snapshot.stat().st_size,
        },
        "recovery_events": recovery_event_receipts(args.work_root),
    }
    result = {
        "schema_version": "winner_v12.full_calibrator_training_result.v1",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT",
        "decision": "AUTHORIZE_FROZEN_124_CELL_CALIBRATOR_GATE_ONLY",
        "logical_run_id": "winner-v12-full-calibrator-seed-120120",
        "environment": {
            "software_versions": software,
            "jax_devices": [str(x) for x in jax.devices()],
        },
        "authority_source": {
            "cpu_result_sha256": smoke.sha256(CPU_RESULT),
            "cpu_result_status": cpu_result["status"],
            "launch_contract_lf_sha256": smoke.lf_sha256(LAUNCH_CONTRACT),
            "claim_lf_sha256": smoke.lf_sha256(
                ROOT / claim["repository_relative_claim_path"]
            ),
        },
        "execution": {
            "stage1_optimizer_updates": STAGE1_UPDATES,
            "stage2_optimizer_updates": STAGE2_UPDATES,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "population": {
            "episodes_per_update": len(population),
            "configuration_ids": preregistration["population"][
                "training_configuration_ids"
            ],
            "hidden_plants": smoke.PLANTS,
            "cumulative_sampled_count": sampled_count,
            "cumulative_valid_transition_count": valid_count,
        },
        "parameter_tree_sha256": smoke.tree_sha256(parameters),
        "stage1_tree_sha256": frozen_stage1_hash,
        "stage1_final_artifact": stage1_final_receipt,
        "metrics": metrics,
        "persistent_artifacts": persistent_receipts,
        "artifact_manifest": artifact_manifest,
        "artifact_manifest_sha256": smoke.canonical_sha256(artifact_manifest),
        "elapsed_seconds_this_process": time.monotonic() - start,
        "training_reward_selection_weight": "NONE",
        "checks": {
            "exact_100_stage1_updates": len(
                [row for row in metrics if row["stage"] == "stage1"]
            )
            == STAGE1_UPDATES,
            "exact_100_stage2_updates": len(
                [row for row in metrics if row["stage"] == "stage2"]
            )
            == STAGE2_UPDATES,
            "exact_201_immutable_snapshots": len(snapshot_manifest) == 201,
            "stage1_final_checkpoint_present": bool(stage1_final_receipt),
            "half_and_final_checkpoint_graphs_present": len(persistent_receipts) == 2,
            "latest_pointer_matches_final": True,
            "formal_support_cells_zero": True,
            "locomotion_training_steps_zero": True,
            "robot_or_rdk_access_zero": True,
        },
        "failed_checks": [],
        "authority": {
            "formal_support_gate_executed": False,
            "locomotion_training_or_behavior_executed": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the separately frozen 124-cell calibrator support/context gate",
        },
    }
    if not all(result["checks"].values()):
        raise ValueError("final full-training artifact checks failed")
    write_json_exclusive(result_path, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "result_sha256": smoke.sha256(result_path),
                "elapsed_seconds_this_process": result["elapsed_seconds_this_process"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
