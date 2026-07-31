#!/usr/bin/env python3
"""Run the zero-update Winner-v49 full-action teacher ABI CPU proof."""

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

import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


CONTRACT = ANALYSIS / "winner_v49_full_action_teacher_abi_cpu_contract.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
ENVIRONMENTS = 30
TICKS = 250
SELECTED_ELEMENTS = ENVIRONMENTS * TICKS * len(v49.ACTION_INDICES)


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
        != "winner_v49.full_action_teacher_abi_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_FULL_ACTION_TEACHER_CPU_PROOF_ONLY"
        or value.get("teacher_abi", {}).get("supervised_action_indices")
        != list(v49.ACTION_INDICES)
        or value.get("teacher_abi", {}).get("supervised_elements")
        != SELECTED_ELEMENTS
        or value.get("teacher_abi", {}).get("full_action_teacher_scale")
        != float(v49.FULL_ACTION_TEACHER_SCALE)
        or value.get("execution_now")
        != {
            "synthetic_teacher_rows": 0,
            "optimizer_updates": 0,
            "simulator_behavior_ticks": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v49 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v49 source manifest is absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v49 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v49 source-manifest digest changed")


def sequential_previous_actions(
    identifiers: list[str], table: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray]:
    previous = np.zeros((len(identifiers), TICKS, 14), dtype=np.float32)
    bounded = np.zeros_like(previous)
    current = np.zeros((len(identifiers), 14), dtype=np.float32)
    raw = np.stack([table[name] for name in identifiers]).astype(np.float32)
    delta = np.asarray(
        v49.v43.training.networks.INTERNAL_ACTION_DELTA, dtype=np.float32
    )
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
            "Winner-v49 requires --offline-cpu-only --teacher-abi-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v49 result: {args.output}")

    import jax
    import jax.numpy as jnp

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v49 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    table = v49.v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    identifiers = [name for name in v49.v43.CONFIGURATION_IDS for _ in range(2)]
    previous_np, expected_bounded = sequential_previous_actions(identifiers, table)
    valid = np.ones((ENVIRONMENTS, TICKS), dtype=np.float32)
    raw, bounded, mask = v49.build_teacher_batch(
        identifiers, previous_np, valid, table
    )
    old_raw, old_bounded, old_mask = v49.v43.build_teacher_batch(
        identifiers, previous_np, valid, table
    )
    raw_np = np.asarray(raw, dtype=np.float32)
    bounded_np = np.asarray(bounded, dtype=np.float32)
    mask_np = np.asarray(mask, dtype=np.float32)
    candidate = jnp.full(
        (ENVIRONMENTS, TICKS, 14), jnp.float32(0.125), dtype=jnp.float32
    )

    def teacher_objective(actions: Any, previous_actions: Any) -> Any:
        loss, _ = v49.full_action_teacher_loss(
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
        return v49.combine_objective(
            baseline_objective(actions), current_teacher, enabled=False
        )

    baseline_loss, baseline_grad = jax.value_and_grad(baseline_objective)(candidate)
    disabled_loss, disabled_grad = jax.value_and_grad(disabled_objective)(candidate)

    pitch_only_candidate = jnp.asarray(bounded_np)
    pitch_only_candidate = pitch_only_candidate.at[..., np.asarray(v49.PITCH_ACTION_INDICES)].set(
        jnp.float32(0.0)
    )

    def old_scaled_pitch(actions: Any) -> Any:
        loss, _ = v49.v43.static_target_teacher_loss(
            actions, identifiers, jnp.asarray(previous_np), valid, table
        )
        return jnp.asarray(v49.OLD_PITCH_TEACHER_SCALE) * loss

    def new_scaled_full(actions: Any) -> Any:
        loss = teacher_objective(actions, jnp.asarray(previous_np))
        return jnp.asarray(v49.FULL_ACTION_TEACHER_SCALE) * loss

    old_pitch_grad = jax.grad(old_scaled_pitch)(pitch_only_candidate)
    new_full_grad = jax.grad(new_scaled_full)(pitch_only_candidate)
    pitch = np.asarray(v49.PITCH_ACTION_INDICES, dtype=np.int64)
    nonpitch = np.asarray(v49.NONPITCH_ACTION_INDICES, dtype=np.int64)
    teacher_grad_np = np.asarray(teacher_action_grad, dtype=np.float32)
    baseline_grad_np = np.asarray(baseline_grad, dtype=np.float32)
    disabled_grad_np = np.asarray(disabled_grad, dtype=np.float32)
    old_pitch_grad_np = np.asarray(old_pitch_grad, dtype=np.float32)
    new_full_grad_np = np.asarray(new_full_grad, dtype=np.float32)
    pitch_gradient_error = float(
        np.max(np.abs(old_pitch_grad_np[..., pitch] - new_full_grad_np[..., pitch]))
    )
    checks = {
        "cpu_only_environment_exact": True,
        "exact_15_configuration_table_bound": tuple(table) == v49.v43.CONFIGURATION_IDS,
        "exact_30_two_plant_teacher_rows": len(identifiers) == ENVIRONMENTS,
        "exact_250_tick_teacher_horizon": raw_np.shape == (ENVIRONMENTS, TICKS, 14),
        "exact_105000_valid_action_elements": int(np.sum(mask_np)) == SELECTED_ELEMENTS,
        "all_14_action_elements_selected": bool(np.all(mask_np == 1.0)),
        "raw_targets_bit_exact_to_winner_v43": np.array_equal(raw_np, np.asarray(old_raw)),
        "bounded_targets_bit_exact_to_winner_v43": np.array_equal(
            bounded_np, np.asarray(old_bounded)
        ),
        "inherited_inward_boundary_bit_exact": np.array_equal(
            bounded_np, expected_bounded
        ),
        "old_pitch_mask_is_strict_subset": int(np.sum(np.asarray(old_mask)))
        == ENVIRONMENTS * TICKS * 6,
        "full_scale_per_element_weight_bit_exact": v49.per_element_scale_is_preserved(),
        "teacher_loss_finite_nonzero": math.isfinite(float(teacher_loss))
        and float(teacher_loss) > 0.0,
        "teacher_gradient_nonzero_on_all_14_indices": all(
            np.any(teacher_grad_np[..., index] != 0.0)
            for index in v49.ACTION_INDICES
        ),
        "teacher_target_and_previous_action_paths_stopped": bool(
            np.all(np.asarray(teacher_previous_grad) == 0.0)
        ),
        "pitch_scaled_gradient_preserved_at_most_1e_10": (
            pitch_gradient_error <= 1.0e-10
        ),
        "pitch_only_candidate_has_zero_new_nonpitch_gradient": bool(
            np.all(new_full_grad_np[..., nonpitch] == 0.0)
        ),
        "default_off_loss_bit_exact": np.array_equal(
            np.asarray(disabled_loss), np.asarray(baseline_loss)
        ),
        "default_off_gradient_bit_exact": np.array_equal(
            disabled_grad_np, baseline_grad_np
        ),
        "all_arrays_losses_gradients_finite": all(
            np.all(np.isfinite(value))
            for value in (
                raw_np,
                bounded_np,
                mask_np,
                teacher_grad_np,
                np.asarray(teacher_previous_grad),
                baseline_grad_np,
                disabled_grad_np,
                old_pitch_grad_np,
                new_full_grad_np,
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
        "schema_version": "winner_v49.full_action_teacher_abi_cpu_result.v1",
        "status": (
            "PASS_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT"
            if passed
            else "HOLD_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_FULL_ACTION_TEACHER_SOURCE_GRADIENT_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_ATTACH_FULL_ACTION_TEACHER_TO_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "teacher_evidence": {
            "environment_rows": ENVIRONMENTS,
            "duration_ticks": TICKS,
            "supervised_action_indices": list(v49.ACTION_INDICES),
            "selected_elements": int(np.sum(mask_np)),
            "teacher_loss": float(teacher_loss),
            "baseline_loss": float(baseline_loss),
            "old_pitch_teacher_scale": float(v49.OLD_PITCH_TEACHER_SCALE),
            "full_action_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "per_element_scale": float(
                v49.FULL_ACTION_TEACHER_SCALE / np.float32(14)
            ),
            "maximum_pitch_scaled_gradient_error": pitch_gradient_error,
            "raw_targets_sha256": array_sha256(raw_np),
            "bounded_targets_sha256": array_sha256(bounded_np),
            "teacher_mask_sha256": array_sha256(mask_np),
            "teacher_action_gradient_sha256": array_sha256(teacher_grad_np),
        },
        "execution": {
            "synthetic_teacher_rows": ENVIRONMENTS * TICKS,
            "optimizer_updates": 0,
            "simulator_behavior_ticks": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "training_authorized": False,
            "one_update_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered source-gradient CPU contract",
        },
    }
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
