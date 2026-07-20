#!/usr/bin/env python3
"""Run the separately frozen winner-v6b zero-PPO CPU software contract."""

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
import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v6b_zero_ppo_cpu_contract_preregistration.json"
NETWORK_SOURCE = ROOT / "patches/winner_v6_dynamic_calibration_networks.py"
BASE_CHECKER = ROOT / "tools/check_winner_v6_zero_ppo_cpu_contract.py"
IMPORTER = ROOT / "tools/import_winner_v6b_zero_ppo_cpu_contract.py"
RUNTIME_RECEIPT = ANALYSIS / "winner_v6_bound_semantics_review_receipt.json"
FAILED_RESULT = ANALYSIS / "winner_v6_zero_ppo_cpu_contract_result.json"
ATTRIBUTION = ANALYSIS / "winner_v6_zero_ppo_contract_hold_attribution.json"
sys.path.insert(0, str(ROOT / "tools"))

import check_winner_v6_zero_ppo_cpu_contract as base  # noqa: E402


networks = base.networks


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_physical_chain(
    protected_path: Path,
    expanded_path: Path,
    seed: int,
    ticks: int = 32,
) -> dict[str, Any]:
    """Check the protected full-action contract on one consistent state chain."""

    protected_session = ort.InferenceSession(
        str(protected_path), providers=["CPUExecutionProvider"]
    )
    expanded_session = ort.InferenceSession(
        str(expanded_path), providers=["CPUExecutionProvider"]
    )
    model = onnx.load(protected_path)
    initializers = networks.onnx_initializers(model)
    home = np.asarray(initializers["guard_home"], dtype=np.float32)
    maximum_delta = np.asarray(
        initializers["max_action_delta"], dtype=np.float32
    )
    observations = base.locomotion_observations(seed, ticks)
    previous = np.zeros((1, networks.ACTION_SIZE), dtype=np.float32)
    hidden = np.zeros((1, networks.HIDDEN_SIZE), dtype=np.float32)
    context = np.linspace(-0.75, 0.75, networks.HIDDEN_SIZE, dtype=np.float32)[
        None, :
    ]
    action_history = [previous.copy(), previous.copy(), previous.copy()]
    bit_exact = True
    bounds_hold = True
    finite = True
    maximum_excess = 0.0
    for obs in observations:
        # A valid zero-tracking synthetic chain: the measured joint position,
        # applied-target observer, and action histories all derive from the prior
        # confirmed graph output rather than independent random tensors.
        obs[:, 13:27] = previous * np.float32(networks.ACTION_SCALE_RAD)
        obs[:, 27:41] = 0.0
        obs[:, 41:55] = action_history[0]
        obs[:, 55:69] = action_history[1]
        obs[:, 69:83] = action_history[2]
        obs[:, 83:97] = home + previous * np.float32(networks.ACTION_SCALE_RAD)
        protected_action, protected_state = protected_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        expanded_action, expanded_state, hidden_out = expanded_session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": obs,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        delta = np.abs(expanded_action - previous)
        excess = np.maximum(delta - maximum_delta, 0.0)
        maximum_excess = max(maximum_excess, float(np.max(excess)))
        bit_exact &= bool(
            np.array_equal(protected_action, expanded_action)
            and np.array_equal(protected_state, expanded_state)
        )
        bounds_hold &= bool(
            np.max(np.abs(expanded_action)) <= 1.0
            and np.all(excess <= 1.0e-7)
        )
        finite &= bool(
            np.isfinite(expanded_action).all()
            and np.isfinite(expanded_state).all()
            and np.isfinite(hidden_out).all()
        )
        action_history = [
            expanded_state.copy(), action_history[0], action_history[1]
        ]
        previous = expanded_state
        hidden = hidden_out
    return {
        "ticks": ticks,
        "seed": seed,
        "joint_state_source": "prior confirmed output * 0.25 rad",
        "applied_target_source": "guard_home + prior confirmed output * 0.25 rad",
        "action_history_chained": True,
        "protected_and_expanded_bit_exact": bit_exact,
        "absolute_and_delta_bounds_hold": bounds_hold,
        "maximum_delta_excess": maximum_excess,
        "all_finite": finite,
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
    observed_hashes = {
        "network_source": sha256(NETWORK_SOURCE),
        "base_checker": sha256(BASE_CHECKER),
        "v6b_checker": sha256(Path(__file__)),
        "importer": sha256(IMPORTER),
        "runtime_review_receipt": sha256(RUNTIME_RECEIPT),
        "failed_v6_result": sha256(FAILED_RESULT),
        "hold_attribution": sha256(ATTRIBUTION),
        "protected_half": sha256(
            ROOT / preregistration["protected_checkpoints"]["half"]["path"]
        ),
        "protected_final": sha256(
            ROOT / preregistration["protected_checkpoints"]["final"]["path"]
        ),
    }
    if observed_hashes != preregistration["input_hashes"]:
        raise ValueError("winner-v6b frozen input hash mismatch")

    calibrator_parameters = networks.initialize_calibrator_parameters()
    locomotion_parameters = networks.initialize_locomotion_adapter_parameters()
    calibrator_path = work_root / "winner_v6b_calibrator_step_zero.onnx"
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
    physical_chains = []
    for index, label in enumerate(("half", "final")):
        protected_path = ROOT / preregistration["protected_checkpoints"][label]["path"]
        expanded_path = work_root / f"winner_v6b_locomotion_{label}_step_zero.onnx"
        networks.export_locomotion_onnx(
            protected_path, locomotion_parameters, expanded_path
        )
        expansions.append(
            base.check_protected_expansion(
                protected_path,
                expanded_path,
                locomotion_parameters,
                context,
                handoff_previous,
                60740 + index * 10,
            )
        )
        physical_chains.append(
            check_physical_chain(
                protected_path, expanded_path, 60742 + index * 10
            )
        )

    stressed_calibrator, stressed_locomotion = base.stress_parameters(
        calibrator_parameters, locomotion_parameters
    )
    stress_calibrator_path = work_root / "winner_v6b_calibrator_bound_stress.onnx"
    stress_locomotion_path = work_root / "winner_v6b_locomotion_bound_stress.onnx"
    networks.export_calibrator_onnx(stressed_calibrator, stress_calibrator_path)
    networks.export_locomotion_onnx(
        ROOT / preregistration["protected_checkpoints"]["half"]["path"],
        stressed_locomotion,
        stress_locomotion_path,
        adapter_enabled=True,
    )
    stress_bounds = base.check_stress_bounds(
        stress_calibrator_path, stress_locomotion_path
    )

    action_head_zero = bool(
        np.count_nonzero(np.asarray(calibrator_parameters["action_weight"])) == 0
        and np.count_nonzero(np.asarray(calibrator_parameters["action_bias"])) == 0
    )
    context_heads_zero = bool(
        np.count_nonzero(
            np.asarray(locomotion_parameters["context_hidden_weight"])
        )
        == 0
        and np.count_nonzero(
            np.asarray(locomotion_parameters["hidden_action_weight"])
        )
        == 0
        and np.count_nonzero(
            np.asarray(locomotion_parameters["context_action_weight"])
        )
        == 0
        and np.count_nonzero(np.asarray(locomotion_parameters["action_bias"])) == 0
    )
    tolerance = float(preregistration["numeric_tolerance"])
    devices = [str(device) for device in jax.devices()]
    graph_inputs = {
        value["name"]
        for value in base.abi(calibrator_path)["inputs"]
        + expansions[0]["abi"]["inputs"]
    }
    checks = {
        "frozen_input_hashes_exact": observed_hashes
        == preregistration["input_hashes"],
        "failed_v6_result_remains_held": json.loads(
            FAILED_RESULT.read_text(encoding="utf-8")
        )["status"]
        == "HOLD_WINNER_V6_ZERO_PPO_CPU_SOFTWARE_CONTRACT",
        "jax_cpu_only": bool(devices)
        and all(device.platform == "cpu" for device in jax.devices()),
        "onnxruntime_cpu_only": calibrator_session.get_providers()
        == ["CPUExecutionProvider"],
        "calibrator_abi_exact": base.abi(calibrator_path)
        == preregistration["expected_abi"]["calibrator"],
        "locomotion_abis_exact": all(
            row["abi"] == preregistration["expected_abi"]["locomotion"]
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
        "default_off_arbitrary_input_identity_bit_exact": all(
            row["protected_actions_bit_exact"]
            and row["protected_previous_action_state_bit_exact"]
            and row["context_branch_exact_zero_default_off"]
            for row in expansions
        ),
        "enabled_adapter_arbitrary_input_bounds_hold": (
            stress_bounds["calibrator_bounds_hold"]
            and stress_bounds["locomotion_bounds_hold"]
        ),
        "protected_physical_chains_hold_full_action_contract": all(
            row["protected_and_expanded_bit_exact"]
            and row["absolute_and_delta_bounds_hold"]
            and row["all_finite"]
            for row in physical_chains
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
        "PASS_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT"
        if not failed
        else "HOLD_WINNER_V6B_ZERO_PPO_CPU_SOFTWARE_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v6b.zero_ppo_cpu_software_contract_result.v1",
        "status": status,
        "decision": (
            "AUTHORIZE_SEPARATE_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "STOP_WINNER_V6_DYNAMIC_CALIBRATION_PATH"
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
        "default_off_expansions": expansions,
        "protected_physical_chains": physical_chains,
        "enabled_stress_bounds": stress_bounds,
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
            "This is a software contract only; no behavior or support outcome was evaluated.",
            "The failed winner-v6 formal result remains held and is not reclassified.",
            "Temporary ONNX outputs are not deployable policies.",
        ],
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
