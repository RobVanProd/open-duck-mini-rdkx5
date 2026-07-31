#!/usr/bin/env python3
"""Run the frozen Winner-v11 zero-PPO CPU mechanics contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
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
PREREGISTRATION = ANALYSIS / "winner_v11_zero_ppo_cpu_mechanics_preregistration.json"
NETWORK_SOURCE = ROOT / "patches/winner_v11_dynamic_calibration_networks.py"
IMPORTER = ROOT / "tools/import_winner_v11_zero_ppo_cpu_mechanics.py"
BASE_CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
BASE_NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
HANDOFF_ROOT = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"
OBSERVER_SOURCE = HANDOFF_ROOT / "observer/winner_v2_contract.py"
P30_FIT = HANDOFF_ROOT / "observer/p30_actuator_fit.json"
REFERENCE_TABLE = HANDOFF_ROOT / "reference/ground_up_projected_reference_feature_table.npz"
POLICY_CONTRACT = HANDOFF_ROOT / "policy_contract.json"
sys.path.insert(0, str(ROOT / "patches"))
sys.path.insert(0, str(ROOT / "tools"))

import winner_v11_dynamic_calibration_networks as networks  # noqa: E402
import check_winner_v6_zero_ppo_cpu_contract as base  # noqa: E402


# Reuse only the frozen population generators and numerical checks.  Rebinding
# makes their JAX references use the Winner-v11 stored/inward boundary.
base.networks = networks

_observer_spec = importlib.util.spec_from_file_location(
    "winner_v11_frozen_observer", OBSERVER_SOURCE
)
if _observer_spec is None or _observer_spec.loader is None:
    raise ImportError("cannot load the frozen Winner-v2 observer")
observer_contract = importlib.util.module_from_spec(_observer_spec)
sys.modules[_observer_spec.name] = observer_contract
_observer_spec.loader.exec_module(observer_contract)
_policy_contract = json.loads(POLICY_CONTRACT.read_text(encoding="utf-8"))
HOME_TARGET = np.asarray(
    _policy_contract["action_contract"]["home_rad"], dtype=np.float32
)


def calibration_observations(seed: int, count: int) -> np.ndarray:
    """Build a stationary, P30-consistent zero-command calibration fixture."""

    rng = np.random.Generator(np.random.PCG64(seed))
    observations = rng.normal(0.0, 0.02, (count, 1, networks.OBS_SIZE)).astype(
        np.float32
    )
    observations[:, :, 6:13] = 0.0
    observations[:, :, 13:41] = 0.0
    observations[:, :, 41:83] = 0.0
    observations[:, :, 83:97] = HOME_TARGET[None, None, :]
    observations[:, :, 97:99] = 1.0
    observations[:, :, 99:101] = np.asarray([1.0, 0.0], dtype=np.float32)
    observations[:, :, 101:115] = 0.0
    return observations


base.calibration_observations = calibration_observations


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_p30_fit(work_directory: Path) -> Path:
    """Materialize the frozen LF bytes even from a Windows CRLF checkout."""

    path = work_directory / "p30_actuator_fit.lf.json"
    canonical_bytes = P30_FIT.read_bytes().replace(b"\r\n", b"\n")
    if path.exists() and path.read_bytes() != canonical_bytes:
        raise ValueError("existing canonical P30 fit has unexpected bytes")
    if not path.exists():
        path.write_bytes(canonical_bytes)
    return path


def initializer(model: onnx.ModelProto, name: str) -> np.ndarray:
    from onnx import numpy_helper

    for item in model.graph.initializer:
        if item.name == name:
            return np.asarray(numpy_helper.to_array(item), dtype=np.float32)
    raise ValueError(f"missing initializer: {name}")


def _past_action(
    actions: list[np.ndarray], tick: int, lag: int
) -> np.ndarray:
    index = tick - lag
    if index < 0:
        return np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
    return actions[index]


def locomotion_observation(
    rng: np.random.Generator,
    reference: Any,
    *,
    command_x: float,
    tick: int,
    applied_target: np.ndarray,
    prior_applied_target: np.ndarray,
    actions: list[np.ndarray],
) -> np.ndarray:
    """Compose one contract-faithful 115-D synthetic mechanics observation."""

    obs = rng.normal(0.0, 0.02, (1, networks.OBS_SIZE)).astype(np.float32)
    obs[:, 6:13] = 0.0
    obs[:, 6] = np.float32(command_x)
    obs[:, 13:27] = applied_target - HOME_TARGET[None, :]
    obs[:, 27:41] = (
        (applied_target - prior_applied_target)
        / np.float32(networks.CONTROL_DT_S)
        * np.float32(0.05)
    )
    obs[:, 41:55] = _past_action(actions, tick, 2)
    obs[:, 55:69] = _past_action(actions, tick, 3)
    obs[:, 69:83] = _past_action(actions, tick, 4)
    obs[:, 83:97] = applied_target
    obs[:, 97:99] = 1.0
    angle = np.float32(2.0 * np.pi * (tick % 27) / 27.0)
    obs[:, 99:101] = np.asarray([np.cos(angle), np.sin(angle)], np.float32)
    obs[:, 101:115] = reference.lookup(
        [command_x, 0.0, 0.0], tick % 27
    )[None, :]
    return obs


def check_boundary_identity(paths: dict[str, Path]) -> dict[str, Any]:
    rows = []
    for label, path in paths.items():
        model = onnx.load(path)
        stored = initializer(model, "max_action_delta").reshape(-1)
        inward = initializer(model, "v7_safe_max_action_delta").reshape(-1)
        rows.append(
            {
                "label": label,
                "stored_exact": np.array_equal(stored, networks.MAX_ACTION_DELTA),
                "inward_exact": np.array_equal(
                    inward, networks.INTERNAL_ACTION_DELTA
                ),
                "inward_strictly_inside_stored": bool(np.all(inward < stored)),
                "stored_delta": stored.tolist(),
                "inward_delta": inward.tolist(),
            }
        )
    return {
        "policies": rows,
        "both_exact": all(
            row["stored_exact"]
            and row["inward_exact"]
            and row["inward_strictly_inside_stored"]
            for row in rows
        ),
    }


def check_default_off_identity(
    protected_path: Path,
    expanded_path: Path,
    seed: int,
    cases: int = 66,
) -> dict[str, Any]:
    """Prove that the default-off graph is an exact protected-policy wrapper."""

    protected = ort.InferenceSession(
        str(protected_path), providers=["CPUExecutionProvider"]
    )
    expanded = ort.InferenceSession(
        str(expanded_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    action_bit_exact = True
    state_bit_exact = True
    context_default_off = True
    all_finite = True
    for _ in range(cases):
        obs = rng.normal(0.0, 0.2, (1, networks.OBS_SIZE)).astype(np.float32)
        previous = rng.uniform(-0.75, 0.75, (1, networks.ACTION_SIZE)).astype(
            np.float32
        )
        hidden = rng.uniform(-0.5, 0.5, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        context = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        protected_action, protected_state = protected.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        action, state, hidden_out = expanded.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        zero_action, zero_state, zero_hidden = expanded.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": np.zeros_like(context),
            },
        )
        action_bit_exact &= np.array_equal(protected_action, action)
        state_bit_exact &= np.array_equal(protected_state, state)
        context_default_off &= bool(
            np.array_equal(action, zero_action)
            and np.array_equal(state, zero_state)
            and np.array_equal(hidden_out, zero_hidden)
        )
        all_finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(state).all()
            and np.isfinite(hidden_out).all()
        )
    return {
        "protected_path": protected_path.name,
        "protected_sha256": sha256(protected_path),
        "expanded_sha256": sha256(expanded_path),
        "identity_cases": cases,
        "protected_actions_bit_exact": action_bit_exact,
        "protected_previous_action_state_bit_exact": state_bit_exact,
        "context_branch_exact_zero_default_off": context_default_off,
        "all_finite": all_finite,
        "abi": base.abi(expanded_path),
    }


def check_sequence_and_handoff(
    calibrator_session: ort.InferenceSession,
    context: np.ndarray,
    handoff_previous: np.ndarray,
    expanded_paths: dict[str, Path],
) -> dict[str, Any]:
    observations = base.calibration_observations(
        60725, networks.CALIBRATION_TICKS
    )
    previous = np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
    hidden = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    work_directory = next(iter(expanded_paths.values())).parent
    observer = observer_contract.FittedBridgeObserver(
        canonical_p30_fit(work_directory), HOME_TARGET
    )
    all_actions_zero = True
    calibration_observer_exact = True
    for obs in observations:
        calibration_observer_exact &= np.array_equal(
            obs[:, 83:97], observer.value.astype(np.float32)[None, :]
        )
        action, previous_out, hidden_out = calibrator_session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        all_actions_zero &= bool(
            np.count_nonzero(action) == 0
            and np.count_nonzero(previous_out) == 0
        )
        observer.step(
            HOME_TARGET + action[0] * np.float32(networks.ACTION_SCALE_RAD),
            networks.CONTROL_DT_S,
        )
        previous = previous_out
        hidden = hidden_out
    final_applied_target = observer.value.astype(np.float32)[None, :]
    reference = observer_contract.ProjectedReferenceTable(REFERENCE_TABLE)
    first_locomotion = locomotion_observation(
        np.random.Generator(np.random.PCG64(61725)),
        reference,
        command_x=0.077,
        tick=0,
        applied_target=final_applied_target,
        prior_applied_target=final_applied_target,
        actions=[],
    )
    initial_previous = np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
    initial_hidden = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    locomotion_hidden = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    command_exact = bool(np.count_nonzero(observations[:, :, 6:13]) == 0)
    phase_exact = bool(
        np.array_equal(
            observations[:, :, 99:101],
            np.broadcast_to(
                np.asarray([1.0, 0.0], np.float32),
                (networks.CALIBRATION_TICKS, 1, 2),
            ),
        )
    )
    context_matches_final_hidden = np.array_equal(context, hidden)
    previous_matches_final_output = np.array_equal(handoff_previous, previous)
    context_mutation_rejected = False
    try:
        context[0, 0] = np.float32(0.0)
    except ValueError:
        context_mutation_rejected = True
    graph_handoffs = []
    for label, path in expanded_paths.items():
        session = ort.InferenceSession(
            str(path), providers=["CPUExecutionProvider"]
        )
        feed = {
            "obs": first_locomotion.copy(),
            "previous_action": previous.copy(),
            "h_in": locomotion_hidden.copy(),
            "calibration_context": np.asarray(context),
        }
        action, previous_out, hidden_out = session.run(
            ["continuous_actions", "previous_action_out", "h_out"], feed
        )
        graph_handoffs.append(
            {
                "label": label,
                "previous_action_input_exact_final_calibrator_output": np.array_equal(
                    feed["previous_action"], previous
                ),
                "applied_target_slot_exact_final_calibration_fixture": np.array_equal(
                    feed["obs"][:, 83:97], final_applied_target
                ),
                "history_slots_exact_t_minus_2_3_4_reset": bool(
                    np.count_nonzero(feed["obs"][:, 41:83]) == 0
                ),
                "context_input_exact_final_calibrator_hidden": np.array_equal(
                    feed["calibration_context"], hidden
                ),
                "locomotion_hidden_input_exact_zero": bool(
                    np.count_nonzero(feed["h_in"]) == 0
                ),
                "locomotion_phase_exact_reset": np.array_equal(
                    feed["obs"][:, 99:101],
                    np.asarray([[1.0, 0.0]], dtype=np.float32),
                ),
                "projected_reference_exact_phase_zero": np.array_equal(
                    feed["obs"][:, 101:115],
                    reference.lookup([0.077, 0.0, 0.0], 0)[None, :],
                ),
                "outputs_finite": bool(
                    np.isfinite(action).all()
                    and np.isfinite(previous_out).all()
                    and np.isfinite(hidden_out).all()
                ),
            }
        )
    graph_handoffs_exact = all(
        all(value for key, value in row.items() if key != "label")
        for row in graph_handoffs
    )
    return {
        "frequency_hz": 50,
        "calibration_ticks": int(observations.shape[0]),
        "initial_previous_action_exact_zero": bool(
            np.count_nonzero(initial_previous) == 0
        ),
        "initial_hidden_exact_zero": bool(np.count_nonzero(initial_hidden) == 0),
        "command_exact_zero_all_ticks": command_exact,
        "phase_exact_one_zero_all_ticks": phase_exact,
        "phase_advanced": False,
        "calibrator_actions_exact_zero_all_ticks": all_actions_zero,
        "p30_applied_target_exact_all_calibration_ticks": calibration_observer_exact,
        "context_exact_final_h_out": context_matches_final_hidden,
        "context_immutable_and_mutation_rejected": bool(
            not context.flags.writeable and context_mutation_rejected
        ),
        "previous_action_exact_final_output": previous_matches_final_output,
        "graph_handoffs": graph_handoffs,
        "both_graph_handoffs_exact_and_finite": graph_handoffs_exact,
        "runtime_requirements_not_executed_by_policy_contract": [
            "session-local nonpersistence across process starts",
            "paused hold of the final confirmed safe physical calibration target",
            "runtime arming and torque-off behavior",
        ],
        "all_exact": bool(
            observations.shape[0] == networks.CALIBRATION_TICKS
            and command_exact
            and phase_exact
            and all_actions_zero
            and calibration_observer_exact
            and context_matches_final_hidden
            and not context.flags.writeable
            and context_mutation_rejected
            and previous_matches_final_output
            and graph_handoffs_exact
        ),
    }


def check_x0_chain(
    protected_path: Path,
    expanded_path: Path,
    adapter_parameters: dict[str, jax.Array],
    context: np.ndarray,
    handoff_previous: np.ndarray,
    seed: int,
    ticks: int = 32,
) -> dict[str, Any]:
    result = check_physical_chain(
        protected_path,
        expanded_path,
        adapter_parameters,
        context,
        handoff_previous,
        seed,
        command_x=0.0,
        ticks=ticks,
    )
    result["exact_zero_and_identity"] = bool(
        result["protected_and_expanded_bit_exact"]
        and result["actions_and_state_exact_zero"]
    )
    return result


def check_strict_stress(
    calibrator_path: Path, locomotion_path: Path, cases: int = 256
) -> dict[str, Any]:
    calibrator = ort.InferenceSession(
        str(calibrator_path), providers=["CPUExecutionProvider"]
    )
    locomotion = ort.InferenceSession(
        str(locomotion_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.Generator(np.random.PCG64(60731))
    maximum_stored_excess = {"calibrator": 0.0, "locomotion": 0.0}
    maximum_internal_excess = {"calibrator": 0.0, "locomotion": 0.0}
    strict = {"calibrator": True, "locomotion": True}
    internal_roundoff = {"calibrator": True, "locomotion": True}
    roundoff_tolerance = float(2.0 * np.finfo(np.float32).eps)
    finite = True
    state_exact = True
    for _ in range(cases):
        obs = rng.normal(0.0, 0.25, (1, networks.OBS_SIZE)).astype(np.float32)
        obs[:, 6] = np.float32(0.077)
        previous = rng.uniform(-1.0, 1.0, (1, networks.ACTION_SIZE)).astype(
            np.float32
        )
        hidden = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        context = rng.uniform(-1.0, 1.0, (1, networks.HIDDEN_SIZE)).astype(
            np.float32
        )
        cal_action, cal_state = calibrator.run(
            ["calibration_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        loc_action, loc_state = locomotion.run(
            ["continuous_actions", "previous_action_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        for label, action, state in (
            ("calibrator", cal_action, cal_state),
            ("locomotion", loc_action, loc_state),
        ):
            stored_excess = np.maximum(
                np.abs(action - previous) - networks.MAX_ACTION_DELTA[None, :],
                0.0,
            )
            internal_excess = np.maximum(
                np.abs(action - previous)
                - networks.INTERNAL_ACTION_DELTA[None, :],
                0.0,
            )
            observed_stored = float(np.max(stored_excess))
            observed_internal = float(np.max(internal_excess))
            maximum_stored_excess[label] = max(
                maximum_stored_excess[label], observed_stored
            )
            maximum_internal_excess[label] = max(
                maximum_internal_excess[label], observed_internal
            )
            strict[label] &= bool(
                observed_stored == 0.0 and np.max(np.abs(action)) <= 1.0
            )
            internal_roundoff[label] &= observed_internal <= roundoff_tolerance
            finite &= bool(np.isfinite(action).all() and np.isfinite(state).all())
            state_exact &= np.array_equal(action, state)
    return {
        "cases_per_graph": cases,
        "strict_stored_bounds": strict,
        "internal_roundoff_bounds": internal_roundoff,
        "maximum_stored_excess": maximum_stored_excess,
        "maximum_internal_excess": maximum_internal_excess,
        "internal_roundoff_tolerance": roundoff_tolerance,
        "all_finite": finite,
        "state_equals_action_bit_exact": state_exact,
    }


def check_physical_chain(
    protected_path: Path,
    expanded_path: Path,
    adapter_parameters: dict[str, jax.Array],
    context: np.ndarray,
    handoff_previous: np.ndarray,
    seed: int,
    *,
    command_x: float = 0.077,
    ticks: int = 32,
) -> dict[str, Any]:
    protected = ort.InferenceSession(
        str(protected_path), providers=["CPUExecutionProvider"]
    )
    expanded = ort.InferenceSession(
        str(expanded_path), providers=["CPUExecutionProvider"]
    )
    protected_initializers = networks.onnx_initializers(onnx.load(protected_path))
    observer = observer_contract.FittedBridgeObserver(
        canonical_p30_fit(expanded_path.parent), HOME_TARGET
    )
    reference = observer_contract.ProjectedReferenceTable(REFERENCE_TABLE)
    rng = np.random.Generator(np.random.PCG64(seed))
    previous_jax = jnp.asarray(handoff_previous)
    previous_onnx = handoff_previous.copy()
    hidden_jax = jnp.zeros((1, networks.HIDDEN_SIZE), dtype=jnp.float32)
    hidden_onnx = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    applied_target = observer.value.astype(np.float32)[None, :]
    prior_applied_target = applied_target.copy()
    actions: list[np.ndarray] = []
    bit_exact = True
    finite = True
    exact_zero = True
    recurrent_state_precondition = bool(
        np.isfinite(previous_onnx).all() and np.max(np.abs(previous_onnx)) <= 1.0
    )
    observation_contract_exact = True
    maximum_stored_excess = 0.0
    maximum_internal_excess = 0.0
    maximum_action_error = 0.0
    maximum_hidden_error = 0.0
    for tick in range(ticks):
        obs = locomotion_observation(
            rng,
            reference,
            command_x=command_x,
            tick=tick,
            applied_target=applied_target,
            prior_applied_target=prior_applied_target,
            actions=actions,
        )
        angle = np.float32(2.0 * np.pi * (tick % 27) / 27.0)
        observation_contract_exact &= bool(
            np.array_equal(obs[:, 41:55], _past_action(actions, tick, 2))
            and np.array_equal(obs[:, 55:69], _past_action(actions, tick, 3))
            and np.array_equal(obs[:, 69:83], _past_action(actions, tick, 4))
            and np.array_equal(obs[:, 83:97], applied_target)
            and np.array_equal(
                obs[:, 99:101],
                np.asarray([[np.cos(angle), np.sin(angle)]], dtype=np.float32),
            )
            and np.array_equal(
                obs[:, 101:115],
                reference.lookup([command_x, 0.0, 0.0], tick % 27)[None, :],
            )
        )
        expected_action, expected_state, expected_hidden = networks.locomotion_step(
            protected_initializers,
            adapter_parameters,
            jnp.asarray(obs),
            previous_jax,
            hidden_jax,
            jnp.asarray(context),
        )
        protected_action, protected_state = protected.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous_onnx},
        )
        action, state, hidden_out = expanded.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous_onnx,
                "h_in": hidden_onnx,
                "calibration_context": context,
            },
        )
        stored_excess = np.maximum(
            np.abs(action - previous_onnx)
            - networks.MAX_ACTION_DELTA[None, :],
            0.0,
        )
        internal_excess = np.maximum(
            np.abs(action - previous_onnx)
            - networks.INTERNAL_ACTION_DELTA[None, :],
            0.0,
        )
        maximum_stored_excess = max(
            maximum_stored_excess, float(np.max(stored_excess))
        )
        maximum_internal_excess = max(
            maximum_internal_excess, float(np.max(internal_excess))
        )
        maximum_action_error = max(
            maximum_action_error,
            base.maximum_error(expected_action, action),
            base.maximum_error(expected_state, state),
        )
        maximum_hidden_error = max(
            maximum_hidden_error, base.maximum_error(expected_hidden, hidden_out)
        )
        bit_exact &= bool(
            np.array_equal(protected_action, action)
            and np.array_equal(protected_state, state)
        )
        exact_zero &= bool(
            np.count_nonzero(action) == 0 and np.count_nonzero(state) == 0
        )
        finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(state).all()
            and np.isfinite(hidden_out).all()
        )
        recurrent_state_precondition &= bool(
            np.max(np.abs(previous_onnx)) <= 1.0
            and np.max(np.abs(state)) <= 1.0
        )
        sent_target = HOME_TARGET[None, :] + action * np.float32(
            networks.ACTION_SCALE_RAD
        )
        prior_applied_target = applied_target.copy()
        applied_target = observer.step(sent_target[0], networks.CONTROL_DT_S)[None, :].astype(
            np.float32
        )
        actions.append(state.copy())
        previous_jax, hidden_jax = expected_state, expected_hidden
        previous_onnx, hidden_onnx = state, hidden_out
    internal_tolerance = float(2.0 * np.finfo(np.float32).eps)
    return {
        "ticks": ticks,
        "seed": seed,
        "command_x": command_x,
        "protected_and_expanded_bit_exact": bit_exact,
        "actions_and_state_exact_zero": exact_zero,
        "maximum_stored_delta_excess": maximum_stored_excess,
        "maximum_internal_delta_excess": maximum_internal_excess,
        "internal_roundoff_tolerance": internal_tolerance,
        "strict_stored_bounds": maximum_stored_excess == 0.0,
        "internal_roundoff_bounds": maximum_internal_excess <= internal_tolerance,
        "jax_onnx_max_action_error": maximum_action_error,
        "jax_onnx_max_hidden_error": maximum_hidden_error,
        "all_finite": finite,
        "recurrent_state_precondition_held": recurrent_state_precondition,
        "observation_contract_exact": observation_contract_exact,
        "phase_period_ticks": 27,
        "action_history_lags": [2, 3, 4],
        "applied_target_source": "exact frozen P30 forward observer",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("Winner-v11 formal output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    source_paths = {
        "half": args.policy_half.resolve(),
        "final": args.policy_final.resolve(),
    }
    observed_policy_hashes = {label: sha256(path) for label, path in source_paths.items()}
    expected_policy_hashes = {
        label: row["sha256"]
        for label, row in prereg["protected_policies"].items()
    }
    if observed_policy_hashes != expected_policy_hashes:
        raise ValueError("Winner-v10 protected policy hash mismatch")

    observed_sources = {}
    for label, row in prereg["sources"].items():
        path = ROOT / row["path"]
        observed_sources[label] = (
            sha256(path)
            if row["hash_mode"] == "raw sha256"
            else sha256_lf(path)
        )
    expected_sources = {
        label: row["sha256"] for label, row in prereg["sources"].items()
    }
    if observed_sources != expected_sources:
        raise ValueError("Winner-v11 frozen source hash mismatch")

    protected_root = work_root / "protected"
    protected_root.mkdir()
    protected_paths = {}
    for label, source in source_paths.items():
        destination = protected_root / f"winner_v10_{label}.onnx"
        shutil.copyfile(source, destination)
        protected_paths[label] = destination

    boundary_identity = check_boundary_identity(protected_paths)
    calibrator_parameters = networks.initialize_calibrator_parameters()
    locomotion_parameters = networks.initialize_locomotion_adapter_parameters()
    calibrator_path = work_root / "winner_v11_calibrator_step_zero.onnx"
    networks.export_calibrator_onnx(calibrator_parameters, calibrator_path)
    calibrator_session = ort.InferenceSession(
        str(calibrator_path), providers=["CPUExecutionProvider"]
    )
    step_zero = base.check_step_zero(calibrator_parameters, calibrator_session)
    auxiliary = base.check_auxiliary_trainability(calibrator_parameters)
    calibration_chain, context, handoff_previous = base.check_calibration_chain(
        calibrator_parameters, calibrator_session
    )
    fail_closed = base.check_fail_closed(context)

    expansions = []
    x0_chains = []
    physical_chains = []
    expanded_paths = {}
    for index, label in enumerate(("half", "final")):
        expanded_path = work_root / f"winner_v11_locomotion_{label}_step_zero.onnx"
        networks.export_locomotion_onnx(
            protected_paths[label], locomotion_parameters, expanded_path
        )
        expanded_paths[label] = expanded_path
        expansions.append(
            check_default_off_identity(
                protected_paths[label],
                expanded_path,
                110140 + index * 10,
            )
        )
        x0_chains.append(
            check_x0_chain(
                protected_paths[label],
                expanded_path,
                locomotion_parameters,
                context,
                handoff_previous,
                110160 + index * 10,
            )
        )
        physical_chains.append(
            check_physical_chain(
                protected_paths[label],
                expanded_path,
                locomotion_parameters,
                context,
                handoff_previous,
                110180 + index * 10,
            )
        )

    sequence = check_sequence_and_handoff(
        calibrator_session, context, handoff_previous, expanded_paths
    )

    stressed_calibrator, stressed_locomotion = base.stress_parameters(
        calibrator_parameters, locomotion_parameters
    )
    stress_calibrator_path = work_root / "winner_v11_calibrator_bound_stress.onnx"
    stress_locomotion_path = work_root / "winner_v11_locomotion_bound_stress.onnx"
    networks.export_calibrator_onnx(stressed_calibrator, stress_calibrator_path)
    networks.export_locomotion_onnx(
        protected_paths["half"],
        stressed_locomotion,
        stress_locomotion_path,
        adapter_enabled=True,
    )
    strict_stress = check_strict_stress(
        stress_calibrator_path, stress_locomotion_path
    )
    strict_stress["protected_label"] = "half"
    strict_stress_rows = [strict_stress]
    stress_locomotion_final_path = (
        work_root / "winner_v11_locomotion_final_bound_stress.onnx"
    )
    networks.export_locomotion_onnx(
        protected_paths["final"],
        stressed_locomotion,
        stress_locomotion_final_path,
        adapter_enabled=True,
    )
    final_stress = check_strict_stress(
        stress_calibrator_path, stress_locomotion_final_path
    )
    final_stress["protected_label"] = "final"
    strict_stress_rows.append(final_stress)

    action_head_zero = bool(
        np.count_nonzero(np.asarray(calibrator_parameters["action_weight"])) == 0
        and np.count_nonzero(np.asarray(calibrator_parameters["action_bias"])) == 0
    )
    context_heads_zero = all(
        np.count_nonzero(np.asarray(locomotion_parameters[name])) == 0
        for name in (
            "context_hidden_weight",
            "hidden_action_weight",
            "context_action_weight",
            "action_bias",
        )
    )
    calibrator_bound_exact = np.array_equal(
        initializer(onnx.load(calibrator_path), "cal_max_action_delta").reshape(-1),
        networks.INTERNAL_ACTION_DELTA,
    )
    locomotion_bounds_exact = all(
        np.array_equal(
            initializer(onnx.load(path), "v6_max_action_delta").reshape(-1),
            networks.INTERNAL_ACTION_DELTA,
        )
        for path in expanded_paths.values()
    )
    tolerance = float(prereg["test_population"]["numeric_tolerance"])
    devices = [str(device) for device in jax.devices()]
    graph_inputs = {
        value["name"]
        for value in base.abi(calibrator_path)["inputs"]
        + expansions[0]["abi"]["inputs"]
    }
    observed_population = {
        "step_zero_cases": step_zero["cases"],
        "calibration_ticks": calibration_chain["ticks"],
        "default_off_identity_cases_per_checkpoint": expansions[0][
            "identity_cases"
        ],
        "default_off_x0_cases_per_checkpoint": x0_chains[0]["ticks"],
        "locomotion_jax_onnx_ticks_per_checkpoint": physical_chains[0]["ticks"],
        "physical_chain_ticks_per_checkpoint": physical_chains[0]["ticks"],
        "phase_period_ticks": physical_chains[0]["phase_period_ticks"],
        "action_history_lags": physical_chains[0]["action_history_lags"],
        "applied_target_source": physical_chains[0]["applied_target_source"],
        "enabled_stress_cases_per_graph": strict_stress_rows[0][
            "cases_per_graph"
        ],
        "invalid_handoff_cases": len(fail_closed["invalid_cases"]),
        "invalid_handoff_scope": "policy-side calibration context validation only",
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
        "numeric_tolerance": tolerance,
    }
    both_checkpoint_populations_exact = bool(
        len(expansions) == 2
        and all(
            row["identity_cases"]
            == observed_population["default_off_identity_cases_per_checkpoint"]
            for row in expansions
        )
        and all(
            row["ticks"]
            == observed_population["default_off_x0_cases_per_checkpoint"]
            for row in x0_chains
        )
        and all(
            row["ticks"]
            == observed_population["physical_chain_ticks_per_checkpoint"]
            and row["phase_period_ticks"]
            == observed_population["phase_period_ticks"]
            and row["action_history_lags"]
            == observed_population["action_history_lags"]
            and row["applied_target_source"]
            == observed_population["applied_target_source"]
            for row in physical_chains + x0_chains
        )
        and all(
            row["cases_per_graph"]
            == observed_population["enabled_stress_cases_per_graph"]
            for row in strict_stress_rows
        )
    )
    checks = {
        "frozen_lf_source_hashes_exact": observed_sources == expected_sources,
        "protected_winner_v10_hashes_exact": observed_policy_hashes
        == expected_policy_hashes,
        "protected_stored_and_inward_boundaries_exact": boundary_identity[
            "both_exact"
        ],
        "new_graphs_use_inward_boundary_exact": calibrator_bound_exact
        and locomotion_bounds_exact,
        "jax_cpu_only": bool(devices)
        and all(device.platform == "cpu" for device in jax.devices()),
        "onnxruntime_cpu_only": calibrator_session.get_providers()
        == ["CPUExecutionProvider"],
        "calibrator_abi_exact": base.abi(calibrator_path)
        == prereg["expected_abi"]["calibrator"],
        "locomotion_abis_exact": all(
            row["abi"] == prereg["expected_abi"]["locomotion"]
            for row in expansions
        ),
        "calibrator_action_head_exact_zero": action_head_zero,
        "calibrator_step_zero_actions_exact_zero": step_zero["actions_exact_zero"],
        "calibrator_hidden_finite_bounded_and_evolves": (
            step_zero["hidden_finite_bounded"]
            and step_zero["hidden_evolved_every_case"]
        ),
        "calibrator_response_encoder_trainable": auxiliary[
            "response_encoder_receives_gradient"
        ]
        and auxiliary["all_gradients_finite"],
        "calibrator_250_tick_chain_exact": calibration_chain["ticks"] == 250
        and calibration_chain["hidden_changed_ticks"] == 250,
        "sequence_and_handoff_exact": sequence["all_exact"],
        "calibration_context_immutable_finite_bounded": (
            calibration_chain["context_read_only"]
            and calibration_chain["context_min"] >= -1.0
            and calibration_chain["context_max"] <= 1.0
        ),
        "failed_calibration_never_armable": fail_closed[
            "all_invalid_cases_rejected"
        ],
        "locomotion_context_heads_exact_zero": context_heads_zero,
        "default_off_arbitrary_input_identity_bit_exact": all(
            row["protected_actions_bit_exact"]
            and row["protected_previous_action_state_bit_exact"]
            and row["context_branch_exact_zero_default_off"]
            for row in expansions
        ),
        "default_off_x0_exact_zero_and_identity": all(
            row["exact_zero_and_identity"]
            and row["observation_contract_exact"]
            and row["strict_stored_bounds"]
            and row["internal_roundoff_bounds"]
            for row in x0_chains
        ),
        "jax_onnx_chains_within_tolerance": (
            step_zero["max_action_error"] <= tolerance
            and step_zero["max_hidden_error"] <= tolerance
            and calibration_chain["max_action_error"] <= tolerance
            and calibration_chain["max_hidden_error"] <= tolerance
            and all(
                row["jax_onnx_max_action_error"] <= tolerance
                and row["jax_onnx_max_hidden_error"] <= tolerance
                for row in physical_chains + x0_chains
            )
        ),
        "enabled_graphs_strict_stored_bounds": all(
            all(row["strict_stored_bounds"].values())
            and all(row["internal_roundoff_bounds"].values())
            and row["all_finite"]
            and row["state_equals_action_bit_exact"]
            for row in strict_stress_rows
        ),
        "protected_physical_chains_strict_and_exact": all(
            row["protected_and_expanded_bit_exact"]
            and row["strict_stored_bounds"]
            and row["internal_roundoff_bounds"]
            and row["all_finite"]
            and row["observation_contract_exact"]
            for row in physical_chains
        ),
        "physical_chain_jax_onnx_within_tolerance": all(
            row["jax_onnx_max_action_error"] <= tolerance
            and row["jax_onnx_max_hidden_error"] <= tolerance
            for row in physical_chains + x0_chains
        ),
        "recurrent_previous_action_precondition_held": all(
            row["recurrent_state_precondition_held"]
            for row in physical_chains + x0_chains
        ),
        "frozen_test_population_exact": observed_population
        == prereg["test_population"]
        and both_checkpoint_populations_exact,
        "no_true_configuration_graph_input": graph_inputs
        == {"obs", "previous_action", "h_in", "calibration_context"},
        "auxiliary_targets_deployable_observation_only": (
            auxiliary["auxiliary_target_indices"]
            == networks.AUXILIARY_RESPONSE_OBS_INDICES.tolist()
            and max(auxiliary["auxiliary_target_indices"]) < networks.OBS_SIZE
        ),
        "both_protected_checkpoints_checked": len(expansions) == 2,
        "zero_optimizer_steps_and_behavior_cells": True,
    }
    if set(checks) != set(prereg["expected_result_checks"]):
        raise RuntimeError("checker result names differ from the frozen contract")
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V11_ZERO_PPO_CPU_MECHANICS"
        if not failed
        else "HOLD_WINNER_V11_ZERO_PPO_CPU_MECHANICS"
    )
    payload = {
        "schema_version": "winner_v11.zero_ppo_cpu_mechanics_result.v1",
        "status": status,
        "decision": (
            "AUTHORIZE_SEPARATE_WINNER_V11_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "STOP_WINNER_V11_AND_REVIEW_MECHANICS_FAILURE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "preregistration_sha256": sha256_lf(PREREGISTRATION),
        "source_hashes": observed_sources,
        "protected_policy_hashes": observed_policy_hashes,
        "devices": devices,
        "versions": {
            "jax": jax.__version__,
            "numpy": np.__version__,
            "onnx": onnx.__version__,
            "onnxruntime": ort.__version__,
        },
        "boundary_identity": boundary_identity,
        "step_zero": step_zero,
        "auxiliary_trainability": auxiliary,
        "calibration_chain": calibration_chain,
        "sequence_and_handoff": sequence,
        "fail_closed": fail_closed,
        "default_off_expansions": expansions,
        "default_off_x0_chains": x0_chains,
        "enabled_stress": strict_stress_rows,
        "protected_physical_chains": physical_chains,
        "observed_test_population": observed_population,
        "temporary_artifacts": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in sorted(work_root.glob("*.onnx"))
        },
        "execution_counts": {"optimizer_steps": 0, "formal_behavior_cells": 0},
        "authority": {
            "separate_training_preregistration_design": not failed,
            "training_or_optimizer": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_implementation": False,
            "rdkx5_robot_torque_motion_gate5_deployment": False,
            "robot_clearance": False,
        },
        "limitations": [
            "This is a CPU mechanics contract, not support or walking behavior evidence.",
            "Temporary ONNX outputs are not selected or deployable policies.",
            "Winner-v6 and Winner-v6b remain closed and are not reclassified.",
        ],
    }
    output.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
