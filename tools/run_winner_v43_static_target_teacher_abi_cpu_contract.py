#!/usr/bin/env python3
"""Run the zero-update Winner-v43 static-target teacher ABI CPU proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))

import winner_v43_static_target_teacher as v43  # noqa: E402


CONTRACT = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_contract.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
ENVIRONMENTS = 30
TICKS = 250
SELECTED_ELEMENTS = ENVIRONMENTS * TICKS * len(v43.PITCH_ACTION_INDICES)


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v43.static_target_teacher_abi_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_STATIC_TARGET_TEACHER_ABI_CPU_PROOF_ONLY"
    ):
        raise ValueError("Winner-v43 contract identity changed")
    if value.get("teacher_abi") != {
        "configuration_ids": list(v43.CONFIGURATION_IDS),
        "configuration_occurrences": "exactly two, one per actuator plant",
        "duration_ticks": TICKS,
        "raw_target": "selected Winner-v42 three-coordinate target expanded to 14 actions",
        "bounded_target": (
            "exact Winner-v11 inward graph boundary applied relative to realized "
            "previous_action at the same tick"
        ),
        "supervised_action_indices": list(v43.PITCH_ACTION_INDICES),
        "supervised_elements": SELECTED_ELEMENTS,
        "loss": "mean squared candidate-minus-stopped-bounded-target on valid pitch elements",
        "actor_inputs": "unchanged deployable observation, previous_action, and recurrent hidden state",
        "privileged_configuration_use": "training-label lookup only",
        "deployable_graph_inputs_or_outputs_added": [],
        "nonpitch_teacher_gradient": "exact zero",
        "default_off": "baseline loss and gradients bit-exact",
    }:
        raise ValueError("Winner-v43 teacher ABI changed")
    if value.get("execution_now") != {
        "synthetic_teacher_rows": 0,
        "optimizer_updates": 0,
        "simulator_behavior_ticks": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    } or value.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "one_update_authorized": False,
        "runtime_implementation_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "one separately preregistered zero-update source-gradient CPU contract"
        ),
    }:
        raise ValueError("Winner-v43 execution authority changed")
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    if value.get("source_result") != {
        "winner_v42_result_lf_sha256": lf_sha256(V42_RESULT),
        "winner_v42_repository_attribution": v42["repository_attribution"],
    }:
        raise ValueError("Winner-v43 source result changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v43 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if item.get("hash_mode") != "lf" or lf_sha256(path) != item.get("sha256"):
            raise ValueError(f"Winner-v43 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v43 source manifest changed")


def sequential_previous_actions(
    identifiers: list[str], table: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray]:
    previous = np.zeros((len(identifiers), TICKS, 14), dtype=np.float32)
    bounded = np.zeros_like(previous)
    current = np.zeros((len(identifiers), 14), dtype=np.float32)
    raw = np.stack([table[name] for name in identifiers]).astype(np.float32)
    delta = np.asarray(v43.training.networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
    for tick in range(TICKS):
        previous[:, tick, :] = current
        lower = np.maximum(current - delta, np.float32(-1.0))
        upper = np.minimum(current + delta, np.float32(1.0))
        current = np.maximum(np.minimum(np.clip(raw, -1.0, 1.0), upper), lower)
        bounded[:, tick, :] = current
    return previous, bounded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--teacher-abi-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.teacher_abi_authorized:
        raise PermissionError(
            "Winner-v43 requires --offline-cpu-only --teacher-abi-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v43 result")

    import jax
    import jax.numpy as jnp

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise ValueError("Winner-v43 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    table = v43.load_teacher_table(v42)
    identifiers = [name for name in v43.CONFIGURATION_IDS for _ in range(2)]
    previous_np, expected_bounded = sequential_previous_actions(identifiers, table)
    valid = np.ones((ENVIRONMENTS, TICKS), dtype=np.float32)
    raw, bounded, mask = v43.build_teacher_batch(
        identifiers, previous_np, valid, table
    )
    raw_np = np.asarray(raw, dtype=np.float32)
    bounded_np = np.asarray(bounded, dtype=np.float32)
    mask_np = np.asarray(mask, dtype=np.float32)
    candidate = jnp.zeros((ENVIRONMENTS, TICKS, 14), dtype=jnp.float32)

    def teacher_objective(actions: Any, previous_actions: Any) -> Any:
        loss, _ = v43.static_target_teacher_loss(
            actions, identifiers, previous_actions, valid, table
        )
        return loss

    teacher_loss, teacher_action_grad = jax.value_and_grad(
        teacher_objective, argnums=0
    )(candidate, jnp.asarray(previous_np))
    teacher_previous_grad = jax.grad(teacher_objective, argnums=1)(
        candidate, jnp.asarray(previous_np)
    )

    def baseline_objective(actions: Any) -> Any:
        return jnp.mean(jnp.square(actions + jnp.float32(0.2)))

    def disabled_objective(actions: Any) -> Any:
        current_teacher = teacher_objective(actions, jnp.asarray(previous_np))
        return v43.combine_objective(
            baseline_objective(actions), current_teacher, jnp.float32(1.0), enabled=False
        )

    def enabled_objective(actions: Any) -> Any:
        current_teacher = teacher_objective(actions, jnp.asarray(previous_np))
        return v43.combine_objective(
            baseline_objective(actions), current_teacher, jnp.float32(1.0), enabled=True
        )

    baseline_loss, baseline_grad = jax.value_and_grad(baseline_objective)(candidate)
    disabled_loss, disabled_grad = jax.value_and_grad(disabled_objective)(candidate)
    enabled_loss, enabled_grad = jax.value_and_grad(enabled_objective)(candidate)
    teacher_grad_np = np.asarray(teacher_action_grad, dtype=np.float32)
    baseline_grad_np = np.asarray(baseline_grad, dtype=np.float32)
    disabled_grad_np = np.asarray(disabled_grad, dtype=np.float32)
    enabled_grad_np = np.asarray(enabled_grad, dtype=np.float32)
    pitch = np.asarray(v43.PITCH_ACTION_INDICES, dtype=np.int64)
    nonpitch = np.asarray(
        sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES)), dtype=np.int64
    )
    pair_targets_equal = all(
        np.array_equal(raw_np[index], raw_np[index + 1])
        for index in range(0, ENVIRONMENTS, 2)
    )
    raw_reaches_selected = all(
        np.array_equal(bounded_np[index, -1], table[configuration_id])
        for index, configuration_id in enumerate(identifiers)
    )
    teacher_pitch_nonzero = all(
        np.any(teacher_grad_np[..., action_index] != 0.0)
        for action_index in v43.PITCH_ACTION_INDICES
    )
    checks = {
        "cpu_only_environment_exact": True,
        "exact_15_configuration_table_bound": tuple(table) == v43.CONFIGURATION_IDS,
        "selected_replay_raw_target_hashes_exact": True,
        "exact_30_two_plant_teacher_rows": len(identifiers) == ENVIRONMENTS,
        "exact_250_tick_teacher_horizon": raw_np.shape == (ENVIRONMENTS, TICKS, 14),
        "exact_45000_valid_pitch_elements": int(np.sum(mask_np)) == SELECTED_ELEMENTS,
        "paired_plants_receive_identical_raw_target": pair_targets_equal,
        "nonpitch_teacher_mask_exact_zero": bool(np.all(mask_np[..., nonpitch] == 0.0)),
        "inherited_inward_boundary_bit_exact": np.array_equal(bounded_np, expected_bounded),
        "sequential_boundary_reaches_every_selected_raw_target": raw_reaches_selected,
        "teacher_loss_finite_nonzero": math.isfinite(float(teacher_loss))
        and float(teacher_loss) > 0.0,
        "teacher_gradient_nonzero_on_all_six_pitch_indices": teacher_pitch_nonzero,
        "teacher_gradient_exact_zero_on_nonpitch_indices": bool(
            np.all(teacher_grad_np[..., nonpitch] == 0.0)
        ),
        "teacher_target_and_previous_action_paths_stopped": bool(
            np.all(np.asarray(teacher_previous_grad) == 0.0)
        ),
        "default_off_loss_bit_exact": np.array_equal(
            np.asarray(disabled_loss), np.asarray(baseline_loss)
        ),
        "default_off_gradient_bit_exact": np.array_equal(disabled_grad_np, baseline_grad_np),
        "enabled_unit_scale_changes_pitch_gradients": bool(
            np.any(enabled_grad_np[..., pitch] != baseline_grad_np[..., pitch])
        ),
        "enabled_unit_scale_preserves_nonpitch_gradients_bit_exact": np.array_equal(
            enabled_grad_np[..., nonpitch], baseline_grad_np[..., nonpitch]
        ),
        "all_arrays_losses_gradients_finite": all(
            np.all(np.isfinite(value))
            for value in (
                raw_np, bounded_np, mask_np, teacher_grad_np,
                np.asarray(teacher_previous_grad), baseline_grad_np,
                disabled_grad_np, enabled_grad_np,
                np.asarray([teacher_loss, baseline_loss, disabled_loss, enabled_loss]),
            )
        ),
        "optimizer_updates_zero": True,
        "simulator_behavior_ticks_zero": True,
        "locomotion_training_steps_zero": True,
        "deployable_graph_exports_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result = {
        "schema_version": "winner_v43.static_target_teacher_abi_cpu_result.v1",
        "status": (
            "PASS_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
            if passed else "HOLD_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CPU_CONTRACT_ONLY"
            if passed else "DO_NOT_ATTACH_STATIC_TARGET_TEACHER_TO_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "teacher_evidence": {
            "configuration_ids": list(v43.CONFIGURATION_IDS),
            "environment_rows": ENVIRONMENTS,
            "duration_ticks": TICKS,
            "supervised_action_indices": list(v43.PITCH_ACTION_INDICES),
            "selected_elements": int(np.sum(mask_np)),
            "teacher_loss": float(teacher_loss),
            "baseline_loss": float(baseline_loss),
            "enabled_unit_scale_loss": float(enabled_loss),
            "maximum_raw_target_abs": float(np.max(np.abs(raw_np))),
            "maximum_bounded_target_abs": float(np.max(np.abs(bounded_np))),
            "raw_targets_sha256": array_sha256(raw_np),
            "bounded_targets_sha256": array_sha256(bounded_np),
            "teacher_mask_sha256": array_sha256(mask_np),
            "teacher_action_gradient_sha256": array_sha256(teacher_grad_np),
            "teacher_previous_action_gradient_sha256": array_sha256(
                np.asarray(teacher_previous_grad, dtype=np.float32)
            ),
        },
        "execution": {
            "synthetic_teacher_rows": ENVIRONMENTS * TICKS,
            "optimizer_updates": 0,
            "simulator_behavior_ticks": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [device.platform for device in jax.devices()],
            "numpy_version": np.__version__,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered zero-update source-gradient CPU contract"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    if failed:
        print(json.dumps(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
