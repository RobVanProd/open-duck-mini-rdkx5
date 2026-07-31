#!/usr/bin/env python3
"""Run the frozen winner-v6 zero-PPO CPU software contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import jax.numpy as jnp
import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_preregistration.json"
NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
IMPORTER = ROOT / "tools/import_winner_v6_zero_ppo_cpu_contract.py"
AMENDMENT = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_preregistration_amendment.json"
sys.path.insert(0, str(NETWORK_SOURCE.parent))

import winner_v6_dynamic_calibration_networks as networks  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def abi(model_path: Path) -> dict[str, list[dict[str, Any]]]:
    model = onnx.load(model_path)

    def describe(values: Any) -> list[dict[str, Any]]:
        rows = []
        for value in values:
            tensor = value.type.tensor_type
            rows.append({
                "name": value.name,
                "dtype": (
                    "float32"
                    if tensor.elem_type == onnx.TensorProto.FLOAT
                    else onnx.TensorProto.DataType.Name(tensor.elem_type).lower()
                ),
                "shape": [dimension.dim_value for dimension in tensor.shape.dim],
            })
        return rows

    return {"inputs": describe(model.graph.input), "outputs": describe(model.graph.output)}


def maximum_error(left: Any, right: Any) -> float:
    return float(np.max(np.abs(np.asarray(left) - np.asarray(right))))


def calibration_observations(seed: int, count: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    observations = rng.normal(0.0, 0.05, (count, 1, networks.OBS_SIZE)).astype(
        np.float32
    )
    observations[:, :, 6:13] = 0.0
    observations[:, :, 97:99] = 1.0
    observations[:, :, 99:101] = np.asarray([1.0, 0.0], dtype=np.float32)
    observations[:, :, 101:115] = 0.0
    return observations


def locomotion_observations(seed: int, count: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    observations = rng.normal(0.0, 0.04, (count, 1, networks.OBS_SIZE)).astype(
        np.float32
    )
    for tick in range(count):
        phase = np.float32((2.0 * np.pi * tick) / 20.0)
        observations[tick, 0, 6:13] = 0.0
        observations[tick, 0, 6] = np.float32(0.074 + 0.003 * (tick % 3))
        observations[tick, 0, 97:99] = 1.0
        observations[tick, 0, 99:101] = [np.cos(phase), np.sin(phase)]
        observations[tick, 0, 101:115] = np.sin(
            phase + np.arange(networks.ACTION_SIZE, dtype=np.float32) * 0.17
        ) * np.float32(0.12)
    return observations


def check_step_zero(
    parameters: dict[str, jax.Array], session: ort.InferenceSession
) -> dict[str, Any]:
    fixed = calibration_observations(60720, 2)
    fixed[0] = 0.0
    fixed[0, 0, 97:99] = 1.0
    fixed[0, 0, 99] = 1.0
    random_rows = calibration_observations(60722, 64)
    observations = np.concatenate([fixed, random_rows], axis=0)
    rng = np.random.Generator(np.random.PCG64(60723))
    hidden_controls = np.concatenate([
        np.zeros((2, 1, networks.HIDDEN_SIZE), dtype=np.float32),
        rng.uniform(-0.5, 0.5, (64, 1, networks.HIDDEN_SIZE)).astype(np.float32),
    ])
    max_action_error = 0.0
    max_hidden_error = 0.0
    exact_zero = True
    hidden_finite_bounded = True
    hidden_evolved = True
    for obs, h_in in zip(observations, hidden_controls, strict=True):
        previous = np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
        expected_action, expected_previous, expected_hidden = networks.calibrator_step(
            parameters, jnp.asarray(obs), jnp.asarray(previous), jnp.asarray(h_in)
        )
        actual_action, actual_previous, actual_hidden = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": h_in},
        )
        exact_zero &= bool(
            np.array_equal(actual_action, np.zeros_like(actual_action))
            and np.array_equal(actual_previous, np.zeros_like(actual_previous))
        )
        hidden_finite_bounded &= bool(
            np.isfinite(actual_hidden).all()
            and np.max(np.abs(actual_hidden)) <= 1.0
        )
        hidden_evolved &= not np.array_equal(actual_hidden, h_in)
        max_action_error = max(
            max_action_error,
            maximum_error(expected_action, actual_action),
            maximum_error(expected_previous, actual_previous),
        )
        max_hidden_error = max(
            max_hidden_error, maximum_error(expected_hidden, actual_hidden)
        )
    return {
        "cases": int(observations.shape[0]),
        "actions_exact_zero": exact_zero,
        "hidden_finite_bounded": hidden_finite_bounded,
        "hidden_evolved_every_case": hidden_evolved,
        "max_action_error": max_action_error,
        "max_hidden_error": max_hidden_error,
    }


def check_auxiliary_trainability(parameters: dict[str, jax.Array]) -> dict[str, Any]:
    observations = jnp.asarray(calibration_observations(60724, 9))
    target_indices = jnp.asarray(networks.AUXILIARY_RESPONSE_OBS_INDICES)

    def loss_fn(candidate: dict[str, jax.Array]) -> jax.Array:
        previous = jnp.zeros((1, networks.ACTION_SIZE), dtype=jnp.float32)
        hidden = jnp.zeros((1, networks.HIDDEN_SIZE), dtype=jnp.float32)
        loss = jnp.asarray(0.0, dtype=jnp.float32)
        for tick in range(8):
            action, previous, hidden = networks.calibrator_step(
                candidate, observations[tick], previous, hidden
            )
            prediction = networks.calibrator_auxiliary_prediction(
                candidate, hidden, action
            )
            target = jnp.take(observations[tick + 1], target_indices, axis=1)
            loss = loss + jnp.mean(jnp.square(prediction - target))
        return loss / np.float32(8.0)

    gradients = jax.grad(loss_fn)(parameters)
    norms = {
        name: float(np.linalg.norm(np.asarray(value)))
        for name, value in gradients.items()
    }
    recurrent_names = (
        "obs_weight", "hidden_weight", "hidden_bias", "auxiliary_hidden_weight"
    )
    return {
        "loss": float(loss_fn(parameters)),
        "gradient_norms": norms,
        "all_gradients_finite": all(np.isfinite(value) for value in norms.values()),
        "response_encoder_receives_gradient": all(norms[name] > 0.0 for name in recurrent_names),
        "auxiliary_target_indices": networks.AUXILIARY_RESPONSE_OBS_INDICES.tolist(),
    }


def check_calibration_chain(
    parameters: dict[str, jax.Array], session: ort.InferenceSession
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    observations = calibration_observations(60725, networks.CALIBRATION_TICKS)
    previous_jax = jnp.zeros((1, networks.ACTION_SIZE), dtype=jnp.float32)
    hidden_jax = jnp.zeros((1, networks.HIDDEN_SIZE), dtype=jnp.float32)
    previous_onnx = np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
    hidden_onnx = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    max_action_error = 0.0
    max_hidden_error = 0.0
    hidden_deltas = []
    bounds_hold = True
    all_finite = True
    for obs in observations:
        expected_action, expected_previous, expected_hidden = networks.calibrator_step(
            parameters, jnp.asarray(obs), previous_jax, hidden_jax
        )
        actual_action, actual_previous, actual_hidden = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous_onnx, "h_in": hidden_onnx},
        )
        max_action_error = max(
            max_action_error,
            maximum_error(expected_action, actual_action),
            maximum_error(expected_previous, actual_previous),
        )
        max_hidden_error = max(
            max_hidden_error, maximum_error(expected_hidden, actual_hidden)
        )
        hidden_deltas.append(maximum_error(hidden_onnx, actual_hidden))
        bounds_hold &= bool(
            np.max(np.abs(actual_action)) <= 1.0
            and np.all(
                np.abs(actual_action - previous_onnx)
                <= networks.MAX_ACTION_DELTA[None, :] + 1.0e-7
            )
        )
        all_finite &= bool(
            np.isfinite(actual_action).all() and np.isfinite(actual_hidden).all()
        )
        previous_jax, hidden_jax = expected_previous, expected_hidden
        previous_onnx, hidden_onnx = actual_previous, actual_hidden
    context = networks.validate_calibration_handoff(
        hidden_onnx,
        completed_ticks=networks.CALIBRATION_TICKS,
        all_ticks_valid=True,
        support_valid=True,
    )
    return ({
        "ticks": networks.CALIBRATION_TICKS,
        "max_action_error": max_action_error,
        "max_hidden_error": max_hidden_error,
        "all_finite": all_finite,
        "action_bounds_hold": bounds_hold,
        "hidden_changed_ticks": sum(delta > 0.0 for delta in hidden_deltas),
        "context_read_only": not context.flags.writeable,
        "context_min": float(np.min(context)),
        "context_max": float(np.max(context)),
    }, context, previous_onnx.copy())


def check_fail_closed(context: np.ndarray) -> dict[str, Any]:
    invalid_cases = {
        "wrong_shape": (context[:, :63], 250, True, True),
        "wrong_dtype": (context.astype(np.float64), 250, True, True),
        "nonfinite": (np.full_like(context, np.nan), 250, True, True),
        "below_bound": (np.full_like(context, -1.01), 250, True, True),
        "above_bound": (np.full_like(context, 1.01), 250, True, True),
        "short_run": (context, 249, True, True),
        "long_run": (context, 251, True, True),
        "invalid_tick": (context, 250, False, True),
        "invalid_support": (context, 250, True, False),
    }
    rejected = []
    for name, (candidate, ticks, ticks_valid, support_valid) in invalid_cases.items():
        try:
            networks.validate_calibration_handoff(
                candidate,
                completed_ticks=ticks,
                all_ticks_valid=ticks_valid,
                support_valid=support_valid,
            )
        except ValueError:
            rejected.append(name)
    return {
        "invalid_cases": sorted(invalid_cases),
        "rejected_cases": sorted(rejected),
        "all_invalid_cases_rejected": sorted(rejected) == sorted(invalid_cases),
    }


def check_protected_expansion(
    protected_path: Path,
    expanded_path: Path,
    adapter_parameters: dict[str, jax.Array],
    context: np.ndarray,
    handoff_previous: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    base_session = ort.InferenceSession(
        str(protected_path), providers=["CPUExecutionProvider"]
    )
    expanded_session = ort.InferenceSession(
        str(expanded_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    identity_observations = locomotion_observations(seed + 1, 66)
    identity_previous = rng.uniform(-0.75, 0.75, (66, 1, networks.ACTION_SIZE)).astype(
        np.float32
    )
    identity_hidden = rng.uniform(-0.5, 0.5, (66, 1, networks.HIDDEN_SIZE)).astype(
        np.float32
    )
    identity_context = rng.uniform(-1.0, 1.0, (66, 1, networks.HIDDEN_SIZE)).astype(
        np.float32
    )
    action_bit_exact = True
    state_bit_exact = True
    context_default_off = True
    for obs, previous, hidden, random_context in zip(
        identity_observations,
        identity_previous,
        identity_hidden,
        identity_context,
        strict=True,
    ):
        base_action, base_previous = base_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        expanded_action, expanded_previous, expanded_hidden = expanded_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": random_context,
            },
        )
        zero_action, zero_previous, zero_hidden = expanded_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": np.zeros_like(random_context),
            },
        )
        action_bit_exact &= np.array_equal(base_action, expanded_action)
        state_bit_exact &= np.array_equal(base_previous, expanded_previous)
        context_default_off &= bool(
            np.array_equal(expanded_action, zero_action)
            and np.array_equal(expanded_previous, zero_previous)
            and np.array_equal(expanded_hidden, zero_hidden)
        )

    model = onnx.load(protected_path)
    protected_initializers = networks.onnx_initializers(model)
    observations = locomotion_observations(seed + 2, 32)
    previous_jax = jnp.asarray(handoff_previous)
    previous_onnx = handoff_previous.copy()
    hidden_jax = jnp.zeros((1, networks.HIDDEN_SIZE), dtype=jnp.float32)
    hidden_onnx = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    max_action_error = 0.0
    max_hidden_error = 0.0
    bounds_hold = True
    for obs in observations:
        expected_action, expected_previous, expected_hidden = networks.locomotion_step(
            protected_initializers,
            adapter_parameters,
            jnp.asarray(obs),
            previous_jax,
            hidden_jax,
            jnp.asarray(context),
        )
        actual_action, actual_previous, actual_hidden = expanded_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous_onnx,
                "h_in": hidden_onnx,
                "calibration_context": context,
            },
        )
        max_action_error = max(
            max_action_error,
            maximum_error(expected_action, actual_action),
            maximum_error(expected_previous, actual_previous),
        )
        max_hidden_error = max(
            max_hidden_error, maximum_error(expected_hidden, actual_hidden)
        )
        bounds_hold &= bool(
            np.max(np.abs(actual_action)) <= 1.0
            and np.all(
                np.abs(actual_action - previous_onnx)
                <= networks.MAX_ACTION_DELTA[None, :] + 1.0e-7
            )
        )
        previous_jax, hidden_jax = expected_previous, expected_hidden
        previous_onnx, hidden_onnx = actual_previous, actual_hidden
    return {
        "protected_path": str(protected_path.relative_to(ROOT)),
        "protected_sha256": sha256(protected_path),
        "expanded_sha256": sha256(expanded_path),
        "identity_cases": 66,
        "protected_actions_bit_exact": action_bit_exact,
        "protected_previous_action_state_bit_exact": state_bit_exact,
        "context_branch_exact_zero_default_off": context_default_off,
        "jax_onnx_chain_ticks": 32,
        "jax_onnx_max_action_error": max_action_error,
        "jax_onnx_max_hidden_error": max_hidden_error,
        "action_bounds_hold": bounds_hold,
        "abi": abi(expanded_path),
    }


def stress_parameters(
    calibrator: dict[str, jax.Array], locomotion: dict[str, jax.Array]
) -> tuple[dict[str, jax.Array], dict[str, jax.Array]]:
    rng = np.random.Generator(np.random.PCG64(60730))
    stressed_calibrator = dict(calibrator)
    stressed_calibrator["action_weight"] = jnp.asarray(
        rng.normal(0.0, 1.0, (networks.HIDDEN_SIZE, networks.ACTION_SIZE)).astype(
            np.float32
        )
    )
    stressed_calibrator["action_bias"] = jnp.asarray(
        rng.normal(0.0, 0.5, networks.ACTION_SIZE).astype(np.float32)
    )
    stressed_locomotion = dict(locomotion)
    for name in ("hidden_action_weight", "context_action_weight"):
        stressed_locomotion[name] = jnp.asarray(
            rng.normal(0.0, 1.0, (networks.HIDDEN_SIZE, networks.ACTION_SIZE)).astype(
                np.float32
            )
        )
    stressed_locomotion["context_hidden_weight"] = jnp.asarray(
        rng.normal(0.0, 0.1, (networks.HIDDEN_SIZE, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
    )
    return stressed_calibrator, stressed_locomotion


def check_stress_bounds(
    calibrator_path: Path,
    locomotion_path: Path,
    cases: int = 256,
) -> dict[str, Any]:
    calibrator_session = ort.InferenceSession(
        str(calibrator_path), providers=["CPUExecutionProvider"]
    )
    locomotion_session = ort.InferenceSession(
        str(locomotion_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.Generator(np.random.PCG64(60731))
    calibrator_holds = True
    locomotion_holds = True
    for _ in range(cases):
        obs = rng.normal(0.0, 0.25, (1, networks.OBS_SIZE)).astype(np.float32)
        obs[:, 6] = 0.077
        previous = rng.uniform(-1.0, 1.0, (1, networks.ACTION_SIZE)).astype(np.float32)
        hidden = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(np.float32)
        context = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(np.float32)
        calibration_action = calibrator_session.run(
            ["calibration_actions"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )[0]
        locomotion_action = locomotion_session.run(
            ["continuous_actions"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )[0]
        for action, destination in (
            (calibration_action, "calibrator"),
            (locomotion_action, "locomotion"),
        ):
            holds = bool(
                np.max(np.abs(action)) <= 1.0
                and np.all(
                    np.abs(action - previous)
                    <= networks.MAX_ACTION_DELTA[None, :] + 1.0e-7
                )
            )
            if destination == "calibrator":
                calibrator_holds &= holds
            else:
                locomotion_holds &= holds
    return {
        "cases_per_graph": cases,
        "calibrator_bounds_hold": calibrator_holds,
        "locomotion_bounds_hold": locomotion_holds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists():
        raise FileExistsError(f"formal work root already exists: {work_root}")
    if output.exists():
        raise FileExistsError(f"formal result already exists: {output}")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    expected_hashes = preregistration["input_hashes"]
    observed_hashes = {
        "network_source": sha256(NETWORK_SOURCE),
        "checker": sha256(Path(__file__)),
        "importer": sha256(IMPORTER),
        "pre_execution_amendment": sha256(AMENDMENT),
        "interface_preregistration": sha256(
            ANALYSIS / "winner_v6_dynamic_calibration_interface_preregistration.json"
        ),
        "runtime_review_receipt": sha256(
            ANALYSIS / "winner_v6_runtime_schema_review_receipt.json"
        ),
        "protected_half": sha256(
            ROOT / preregistration["protected_checkpoints"]["half"]["path"]
        ),
        "protected_final": sha256(
            ROOT / preregistration["protected_checkpoints"]["final"]["path"]
        ),
    }
    if observed_hashes != expected_hashes:
        raise ValueError(
            f"frozen input hash mismatch: expected={expected_hashes} observed={observed_hashes}"
        )

    calibrator_parameters = networks.initialize_calibrator_parameters()
    locomotion_parameters = networks.initialize_locomotion_adapter_parameters()
    protected_delta_vectors = []
    for label in ("half", "final"):
        protected_model = onnx.load(
            ROOT / preregistration["protected_checkpoints"][label]["path"]
        )
        protected_initializers = networks.onnx_initializers(protected_model)
        protected_delta_vectors.append(
            np.asarray(protected_initializers["max_action_delta"]).reshape(-1)
        )
    projection_matches_protected = all(
        np.array_equal(vector, networks.MAX_ACTION_DELTA)
        for vector in protected_delta_vectors
    )
    action_head_zero = bool(
        np.count_nonzero(np.asarray(calibrator_parameters["action_weight"])) == 0
        and np.count_nonzero(np.asarray(calibrator_parameters["action_bias"])) == 0
    )
    context_heads_zero = bool(
        np.count_nonzero(np.asarray(locomotion_parameters["context_hidden_weight"])) == 0
        and np.count_nonzero(np.asarray(locomotion_parameters["hidden_action_weight"])) == 0
        and np.count_nonzero(np.asarray(locomotion_parameters["context_action_weight"])) == 0
        and np.count_nonzero(np.asarray(locomotion_parameters["action_bias"])) == 0
    )

    calibrator_path = work_root / "winner_v6_calibrator_step_zero.onnx"
    networks.export_calibrator_onnx(calibrator_parameters, calibrator_path)
    calibrator_session = ort.InferenceSession(
        str(calibrator_path), providers=["CPUExecutionProvider"]
    )
    step_zero = check_step_zero(calibrator_parameters, calibrator_session)
    auxiliary = check_auxiliary_trainability(calibrator_parameters)
    calibration_chain, context, handoff_previous = check_calibration_chain(
        calibrator_parameters, calibrator_session
    )
    fail_closed = check_fail_closed(context)

    expansions = []
    for index, label in enumerate(("half", "final")):
        protected_path = ROOT / preregistration["protected_checkpoints"][label]["path"]
        expanded_path = work_root / f"winner_v6_locomotion_{label}_step_zero.onnx"
        networks.export_locomotion_onnx(
            protected_path, locomotion_parameters, expanded_path
        )
        expansions.append(
            check_protected_expansion(
                protected_path,
                expanded_path,
                locomotion_parameters,
                context,
                handoff_previous,
                60740 + index * 10,
            )
        )

    stressed_calibrator, stressed_locomotion = stress_parameters(
        calibrator_parameters, locomotion_parameters
    )
    stress_calibrator_path = work_root / "winner_v6_calibrator_bound_stress.onnx"
    stress_locomotion_path = work_root / "winner_v6_locomotion_bound_stress.onnx"
    networks.export_calibrator_onnx(stressed_calibrator, stress_calibrator_path)
    networks.export_locomotion_onnx(
        ROOT / preregistration["protected_checkpoints"]["half"]["path"],
        stressed_locomotion,
        stress_locomotion_path,
        adapter_enabled=True,
    )
    stress_bounds = check_stress_bounds(
        stress_calibrator_path, stress_locomotion_path
    )

    expected_calibrator_abi = preregistration["expected_abi"]["calibrator"]
    expected_locomotion_abi = preregistration["expected_abi"]["locomotion"]
    tolerance = float(preregistration["numeric_tolerance"])
    devices = [str(device) for device in jax.devices()]
    graph_inputs = {
        value["name"]
        for value in abi(calibrator_path)["inputs"]
        + expansions[0]["abi"]["inputs"]
    }
    checks = {
        "frozen_input_hashes_exact": observed_hashes == expected_hashes,
        "jax_cpu_only": bool(devices) and all(
            device.platform == "cpu" for device in jax.devices()
        ),
        "onnxruntime_cpu_only": calibrator_session.get_providers()
        == ["CPUExecutionProvider"],
        "calibrator_abi_exact": abi(calibrator_path) == expected_calibrator_abi,
        "locomotion_abis_exact": all(
            row["abi"] == expected_locomotion_abi for row in expansions
        ),
        "calibrator_action_head_exact_zero": action_head_zero,
        "calibrator_step_zero_actions_exact_zero": step_zero["actions_exact_zero"],
        "calibrator_hidden_finite_bounded": step_zero["hidden_finite_bounded"],
        "calibrator_hidden_evolves": step_zero["hidden_evolved_every_case"],
        "calibrator_response_encoder_trainable": auxiliary[
            "response_encoder_receives_gradient"
        ]
        and auxiliary["all_gradients_finite"],
        "calibrator_250_tick_chain_exact": (
            calibration_chain["ticks"] == 250
            and calibration_chain["hidden_changed_ticks"] == 250
            and calibration_chain["max_action_error"] <= tolerance
            and calibration_chain["max_hidden_error"] <= tolerance
        ),
        "calibration_context_immutable_finite_bounded": (
            calibration_chain["context_read_only"]
            and calibration_chain["context_min"] >= -1.0
            and calibration_chain["context_max"] <= 1.0
        ),
        "failed_calibration_never_armable": fail_closed[
            "all_invalid_cases_rejected"
        ],
        "locomotion_context_heads_exact_zero": context_heads_zero,
        "adapter_projection_matches_both_protected_checkpoints": projection_matches_protected,
        "protected_actions_and_state_bit_exact": all(
            row["protected_actions_bit_exact"]
            and row["protected_previous_action_state_bit_exact"]
            and row["context_branch_exact_zero_default_off"]
            for row in expansions
        ),
        "jax_onnx_full_handoff_chain_within_tolerance": (
            step_zero["max_action_error"] <= tolerance
            and step_zero["max_hidden_error"] <= tolerance
            and calibration_chain["max_action_error"] <= tolerance
            and calibration_chain["max_hidden_error"] <= tolerance
            and all(
                row["jax_onnx_max_action_error"] <= tolerance
                and row["jax_onnx_max_hidden_error"] <= tolerance
                for row in expansions
            )
        ),
        "graph_owned_action_bounds_hold": (
            calibration_chain["action_bounds_hold"]
            and all(row["action_bounds_hold"] for row in expansions)
            and stress_bounds["calibrator_bounds_hold"]
            and stress_bounds["locomotion_bounds_hold"]
        ),
        "no_true_configuration_graph_input": graph_inputs
        == {"obs", "previous_action", "h_in", "calibration_context"},
        "auxiliary_targets_deployable_observation_only": (
            auxiliary["auxiliary_target_indices"]
            == networks.AUXILIARY_RESPONSE_OBS_INDICES.tolist()
            and min(auxiliary["auxiliary_target_indices"]) >= 0
            and max(auxiliary["auxiliary_target_indices"]) < networks.OBS_SIZE
        ),
        "both_persistent_protected_checkpoints_checked": len(expansions) == 2,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V6_ZERO_PPO_CPU_SOFTWARE_CONTRACT"
        if not failed
        else "HOLD_WINNER_V6_ZERO_PPO_CPU_SOFTWARE_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v6.zero_ppo_cpu_software_contract_result.v1",
        "status": status,
        "decision": (
            "AUTHORIZE_SEPARATE_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "STOP_AND_REVIEW_ZERO_PPO_CONTRACT_FAILURE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed_hashes,
        "preregistration_sha256": sha256(PREREGISTRATION),
        "devices": devices,
        "versions": {
            "jax": jax.__version__,
            "onnx": onnx.__version__,
            "onnxruntime": ort.__version__,
            "numpy": np.__version__,
        },
        "step_zero": step_zero,
        "auxiliary_trainability": auxiliary,
        "calibration_chain": calibration_chain,
        "fail_closed": fail_closed,
        "protected_expansions": expansions,
        "stress_bounds": stress_bounds,
        "artifacts": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in sorted(work_root.glob("*.onnx"))
        },
        "authority": {
            "separate_calibrator_training_preregistration_design": not failed,
            "training_or_ppo": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_v2_implementation": False,
            "rdkx5_robot_torque_motion_gate5_or_deployment": False,
            "robot_clearance": False,
        },
        "limitations": [
            "This is an ABI, initialization, bound, state-chain, and numerical-equivalence contract only.",
            "No PPO update, simulator behavior outcome, support pass, gait claim, or policy selection is produced.",
            "The exported ONNX files are temporary contract artifacts and are not deployable policies.",
        ],
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
