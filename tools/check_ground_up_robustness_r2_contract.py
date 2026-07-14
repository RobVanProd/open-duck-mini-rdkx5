#!/usr/bin/env python3
"""Contract-check isolated R2 dynamics overrides before behavior."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

from closed_loop_sim_eval import (
    ClosedLoopConfig,
    apply_eval_dynamics_override,
    run_closed_loop_sim,
)


MODEL_FIELDS = (
    "geom_friction", "dof_frictionloss", "dof_armature", "body_ipos",
    "body_mass", "qpos0", "actuator_gainprm", "actuator_biasprm",
)
ALLOWED_FIELDS = {
    "floor_friction": {"geom_friction"},
    "joint_frictionloss_scale": {"dof_frictionloss"},
    "armature_scale": {"dof_armature"},
    "torso_com_offset_m": {"body_ipos"},
    "all_link_mass_scale": {"body_mass"},
    "torso_mass_add_kg": {"body_mass"},
    "joint_qpos0_offset_rad": {"qpos0"},
    "kp_scale": {"actuator_gainprm", "actuator_biasprm"},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextlib.contextmanager
def cwd(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def strip_wall_clock(value):
    if isinstance(value, dict):
        return {key: strip_wall_clock(item) for key, item in value.items() if key != "wall_clock_s"}
    if isinstance(value, list):
        return [strip_wall_clock(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--default-off-reference", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    playground = args.playground_root.resolve()
    sys.path.insert(0, str(playground))
    import jax
    import jax.numpy as jp
    with cwd(playground):
        from playground.open_duck_mini_v2 import joystick
        env = joystick.Joystick(
            task="flat_terrain_backlash",
            config=joystick.default_config(),
            config_overrides={
                "push_config.enable": False,
                "noise_config.level": 0.0,
                "noise_config.action_min_delay": 0,
                "noise_config.action_max_delay": 1,
                "noise_config.imu_min_delay": 0,
                "noise_config.imu_max_delay": 1,
            },
        )
    baseline = env.mjx_model
    baseline_fields = {name: np.asarray(getattr(baseline, name)) for name in MODEL_FIELDS}
    condition_rows = []
    for condition in prereg["conditions_in_strict_order"]:
        updated, report = apply_eval_dynamics_override(baseline, condition["override"], jp)
        output_fields = {name: np.asarray(getattr(updated, name)) for name in MODEL_FIELDS}
        changed = {name for name in MODEL_FIELDS if not np.array_equal(baseline_fields[name], output_fields[name])}
        key = next(iter(condition["override"]))
        expected = ALLOWED_FIELDS[key]
        # A multiplier endpoint of exactly 1.0 is a deliberate no-op boundary.
        permitted_changed_set = changed <= expected and (changed == expected or not changed)
        readback_finite = all(
            np.all(np.isfinite(np.asarray(item, dtype=float)))
            for name, item in report["readback"].items()
            if name not in {"changed_indices", "affected_dof_ids", "affected_joint_qpos_addrs"}
        )
        condition_rows.append({
            "id": condition["id"],
            "override": condition["override"],
            "report": report,
            "changed_model_fields": sorted(changed),
            "allowed_model_fields": sorted(expected),
            "only_intended_fields_changed": permitted_changed_set,
            "readback_finite": bool(readback_finite),
        })

    default_model, default_report = apply_eval_dynamics_override(baseline, None, jp)
    default_model_exact = all(
        np.array_equal(baseline_fields[name], np.asarray(getattr(default_model, name)))
        for name in MODEL_FIELDS
    )
    policy = Path(prereg["policies"][1]["path"])
    fit = json.loads(args.fit.read_text())
    common = dict(
        policy_path=policy,
        fit=fit,
        playground_root=playground,
        command_x=0.08,
        bridge_mode="fitted",
        expected_observation_dim=115,
        expected_action_dim=14,
        task="flat_terrain_backlash",
        seed=prereg["seeds"][0],
        eval_role="candidate",
        reset_mode="home-support",
        reference_feature_table_path=args.reference_feature_table.resolve(),
        reference_start_phase=0,
        policy_state_input_names=("previous_action",),
        policy_state_output_names=("previous_action_out",),
        policy_applied_target_observation=True,
    )
    default_result = run_closed_loop_sim(ClosedLoopConfig(duration_s=12.0, **common))
    reference_payload = json.loads(args.default_off_reference.read_text())
    reference_run = next(run for run in reference_payload["runs"] if float(run["command_x"]) == 0.08)
    default_off_exact = (
        default_result["status"] == reference_run["status"]
        and default_result["candidate_gate"] == reference_run["candidate_gate"]
        and strip_wall_clock(default_result["modes"]["fitted"])
        == strip_wall_clock(reference_run["modes"]["fitted"])
        and default_result["insertion_point"]["dynamics_override"]["enabled"] is False
    )
    qpos_override = {"joint_qpos0_offset_rad": 0.03}
    qpos_result = run_closed_loop_sim(
        ClosedLoopConfig(duration_s=0.04, eval_dynamics_override=qpos_override, **common)
    )
    qpos_report = qpos_result.get("insertion_point", {}).get("dynamics_override", {})
    home_before = np.asarray((qpos_report.get("readback") or {}).get("home_init_before", []), dtype=float)
    home_after = np.asarray((qpos_report.get("readback") or {}).get("home_init_after", []), dtype=float)
    qpos_home_propagated = (
        qpos_result.get("status") not in {"HOLD_SIM_RUNTIME_ERROR", "HOLD_ENV_NOT_READY"}
        and qpos_report.get("key") == "joint_qpos0_offset_rad"
        and home_before.size == 14
        and np.allclose(home_after - home_before, 0.03, rtol=0.0, atol=1e-8)
    )
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CONTRACT_REQUIRED_CPU_ONLY",
        "exact_20_conditions_320_max_cells": len(condition_rows) == 20 and prereg["matrix"]["maximum_cells"] == 320,
        "all_policy_hashes_exact": all(sha256(Path(item["path"])) == item["sha256"] for item in prereg["policies"]),
        "all_conditions_one_axis_only": all(len(item["override"]) == 1 for item in condition_rows),
        "all_only_intended_model_fields_changed": all(item["only_intended_fields_changed"] for item in condition_rows),
        "all_readbacks_finite": all(item["readback_finite"] for item in condition_rows),
        "default_off_model_exact": default_model_exact and default_report["enabled"] is False,
        "default_off_600_tick_behavior_exact": default_off_exact,
        "joint_offset_reaches_home_support_reset": bool(qpos_home_propagated),
        "cpu_only": jax.default_backend() == "cpu" and os.environ["CUDA_VISIBLE_DEVICES"] == "" and os.environ["JAX_PLATFORMS"] == "cpu",
    }
    failed = [key for key, value in checks.items() if not value]
    status = "PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT" if not failed else "FAIL_ROBUSTNESS_R2_EVALUATOR_CONTRACT"
    payload = {
        "schema_version": "ground_up_robustness_r2_evaluator_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "conditions": condition_rows,
        "default_off_reference": {"path": str(args.default_off_reference.resolve()), "sha256": sha256(args.default_off_reference)},
        "default_off_result_status": default_result.get("status"),
        "qpos_smoke_status": qpos_result.get("status"),
        "qpos_smoke_readback": qpos_report,
        "tool_hashes": {
            "closed_loop_sim_eval": sha256(Path(__file__).with_name("closed_loop_sim_eval.py")),
            "evaluate_ground_up_policy": sha256(Path(__file__).with_name("evaluate_ground_up_policy.py")),
        },
        "authority": {"run_r2_sequential_cpu_behavior": not failed, "run_r3_or_later": False, "training": False, "colab": False, "local_gpu": False, "rdk_or_robot": False},
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Robustness R2 Evaluator Contract", "", f"status: `{status}`", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in checks.items())
    lines.extend(["", "Passing authorizes only the preregistered sequential R2 CPU behavior matrix, stopping at the first failed condition.", "No R3+, training, Colab, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed, "conditions": len(condition_rows)}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
