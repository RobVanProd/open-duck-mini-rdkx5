#!/usr/bin/env python3
"""Validate the preregistered reset-COM estimator-input CPU package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax
import numpy as np


REPO = Path(__file__).resolve().parents[1]
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_INPUT_ARM_PREREGISTRATION_20260715.md"
PATCH = REPO / "patches/ground_up_reset_com_estimator_input.patch"
EXPANDER = REPO / "tools/expand_ground_up_reset_com_estimator_checkpoint.py"
FEASIBILITY = REPO / "outputs/analysis/ground_up_torso_com_reset_estimator_feasibility_result.json"
FEATURE_TABLE = REPO / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
REFERENCE_ACTOR = REPO / "patches/reference_residual_hard_vector_ppo_networks.py"
EXPECTED_HASHES = {
    "prereg": "775fc0815a6b86ceea792fbbb7a10805145b0a54b6263b38f440e6dec2837ab8",
    "patch": "2758898a09ef487d5a6949b9aaafda3db9f00c10976136bd6f5c3e9e7a75a4e8",
    "expander": "7158f8aa7e67040b842307f8ab76313a80918b1c741a73b92f5921d7555a6a34",
    "feasibility": "1fbae0325295cb5efd03d6140816f69fb73e590b72e34f1848ed93ebb24de951",
    "feature_table": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "reference_actor": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
}
EXPECTED_COMPOSED_HASHES = {
    "joystick": "4ddcfbda6f06f9d04acf4ee82deb364993da750adfb8487d032c16be38db3186",
    "runner": "e5ed1bac7ed181f02014487827f05f35fd421ff97ae50614de1b2ce8089f87a2",
}
ANCHORS = {
    -0.05: np.asarray([-13.04679012298584, 0.7727481126785278, 28.672449111938477]),
    0.0: np.asarray([-11.879271507263184, 0.8971166610717773, 29.650177001953125]),
    0.05: np.asarray([-10.715840339660645, 1.0117170810699463, 30.856430053710938]),
}
ANCHOR_TOLERANCE = 1e-3
LATCH_TOLERANCE = 1e-6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_estimate(sensor: np.ndarray) -> float:
    negative, nominal, positive = ANCHORS[-0.05], ANCHORS[0.0], ANCHORS[0.05]
    un = negative - nominal
    up = positive - nominal
    delta = sensor - nominal
    tn = float(np.clip(np.dot(delta, un) / np.dot(un, un), 0.0, 1.0))
    tp = float(np.clip(np.dot(delta, up) / np.dot(up, up), 0.0, 1.0))
    rn = float(np.linalg.norm(sensor - (nominal + tn * un)))
    rp = float(np.linalg.norm(sensor - (nominal + tp * up)))
    estimate = -0.05 * tn if rn <= rp else 0.05 * tp
    return float(np.clip(estimate / 0.05, -1.0, 1.0))


def configured_environment(joystick: Any, enabled: bool) -> Any:
    config = joystick.default_config()
    config.nominal_reference_bootstrap = True
    config.noise_config.level = 0.0
    config.noise_config.action_min_delay = 0
    config.noise_config.action_max_delay = 1
    config.noise_config.imu_min_delay = 0
    config.noise_config.imu_max_delay = 1
    config.push_config.enable = False
    config.reference_feature_table_path = str(FEATURE_TABLE)
    config.ground_up_reset_com_estimator_input = enabled
    return joystick.Joystick(task="flat_terrain_backlash", config=config)


def reset_cells(joystick: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    env = configured_environment(joystick, True)
    nominal = env.mjx_model
    base_ipos = np.asarray(nominal.body_ipos)
    cells = []
    for offset in (-0.05, 0.0, 0.05):
        model = nominal.replace(body_ipos=nominal.body_ipos.at[2, 0].add(offset))
        env._mjx_model = model
        state = jax.jit(env.reset)(jax.random.PRNGKey(0))
        latch = float(np.asarray(state.info["ground_up_reset_com_estimate_latched"]))
        sensor = np.asarray(env.get_accelerometer(state.data), dtype=float)
        expected_latch = independent_estimate(sensor)
        delta = np.asarray(model.body_ipos) - base_ipos
        cells.append(
            {
                "offset_m": offset,
                "sensor_m_s2": sensor.tolist(),
                "anchor_max_abs_error_m_s2": float(np.max(np.abs(sensor - ANCHORS[offset]))),
                "latched_normalized_estimate": latch,
                "independent_expected_latch": expected_latch,
                "latch_abs_error": abs(latch - expected_latch),
                "state_shape": list(state.obs["state"].shape),
                "privileged_state_shape": list(state.obs["privileged_state"].shape),
                "state_index_101": float(np.asarray(state.obs["state"])[101]),
                "privileged_index_101": float(np.asarray(state.obs["privileged_state"])[101]),
                "reference_action_final_14": np.asarray(state.obs["state"])[-14:].tolist(),
                "body2_x_only_mutation": bool(
                    np.count_nonzero(delta) == (0 if offset == 0.0 else 1)
                    and np.asarray(model.body_ipos)[2, 0]
                    == np.asarray(base_ipos[2, 0] + np.asarray(offset, dtype=base_ipos.dtype), dtype=base_ipos.dtype)
                ),
            }
        )
    disabled_env = configured_environment(joystick, False)
    disabled_state = jax.jit(disabled_env.reset)(jax.random.PRNGKey(0))
    disabled = {
        "state_shape": list(disabled_state.obs["state"].shape),
        "privileged_state_shape": list(disabled_state.obs["privileged_state"].shape),
        "latch_key_absent": "ground_up_reset_com_estimate_latched" not in disabled_state.info,
    }
    return cells, disabled


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--composed-root", type=Path, required=True)
    parser.add_argument("--expansion-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    composed = args.composed_root.resolve()
    expansion_path = args.expansion_result.resolve()
    output = args.output.resolve()
    paths = {
        "prereg": PREREG,
        "patch": PATCH,
        "expander": EXPANDER,
        "feasibility": FEASIBILITY,
        "feature_table": FEATURE_TABLE,
        "reference_actor": REFERENCE_ACTOR,
    }
    actual_hashes = {name: sha256(path) for name, path in paths.items()}
    composed_paths = {
        "joystick": composed / "playground/open_duck_mini_v2/joystick.py",
        "runner": composed / "playground/open_duck_mini_v2/runner.py",
    }
    composed_hashes = {name: sha256(path) for name, path in composed_paths.items()}
    joystick_source = composed_paths["joystick"].read_text()
    runner_source = composed_paths["runner"].read_text()
    step_source = joystick_source.split("    def step(", 1)[1]
    feasibility = json.loads(FEASIBILITY.read_text())
    expansion = json.loads(expansion_path.read_text())

    sys.path.insert(0, str(composed))
    previous_cwd = Path.cwd()
    os.chdir(composed)
    try:
        from playground.open_duck_mini_v2 import joystick

        cells, disabled = reset_cells(joystick)
    finally:
        os.chdir(previous_cwd)

    checks = {
        "frozen_input_hashes_exact": actual_hashes == EXPECTED_HASHES,
        "fresh_composed_sources_exact": composed_hashes == EXPECTED_COMPOSED_HASHES,
        "upstream_feasibility_decision_exact": feasibility.get("decision")
        == "SUPPORT_RESET_LATCHED_PIECEWISE_LINEAR_COM_ESTIMATOR_ARM",
        "checkpoint_expansion_passed_and_hash_locked": expansion.get("status")
        == "PASS_RESET_COM_ESTIMATOR_CHECKPOINT_EXPANSION"
        and expansion.get("tool_sha256") == EXPECTED_HASHES["expander"]
        and not expansion.get("failed_checks"),
        "cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu"
        and jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "feature_default_off_in_config_and_cli": "ground_up_reset_com_estimator_input=False"
        in joystick_source
        and 'parser.add_argument("--ground_up_reset_com_estimator_input", action="store_true")'
        in runner_source,
        "single_reset_latch_write_and_no_step_write": joystick_source.count(
            'info["ground_up_reset_com_estimate_latched"] ='
        )
        == 1
        and 'info["ground_up_reset_com_estimate_latched"] =' not in step_source,
        "frozen_estimator_constants_and_rules_present": all(
            fragment in joystick_source
            for fragment in (
                "-13.04679012298584",
                "-11.879271507263184",
                "-10.715840339660645",
                "negative_residual <= positive_residual",
                "estimate_m / 0.05, -1.0, 1.0",
            )
        ),
        "three_reset_anchor_sensors_match": all(
            cell["anchor_max_abs_error_m_s2"] <= ANCHOR_TOLERANCE for cell in cells
        ),
        "three_reset_latches_match_independent_estimator": all(
            cell["latch_abs_error"] <= LATCH_TOLERANCE for cell in cells
        ),
        "enabled_observation_shapes_and_index_exact": all(
            cell["state_shape"] == [116]
            and cell["privileged_state_shape"] == [227]
            and abs(cell["state_index_101"] - cell["latched_normalized_estimate"])
            <= LATCH_TOLERANCE
            and abs(cell["privileged_index_101"] - cell["latched_normalized_estimate"])
            <= LATCH_TOLERANCE
            and len(cell["reference_action_final_14"]) == 14
            for cell in cells
        ),
        "three_models_mutate_body2_x_only": all(cell["body2_x_only_mutation"] for cell in cells),
        "latches_finite_bounded_and_strictly_ordered": all(
            np.isfinite(cell["latched_normalized_estimate"])
            and -1.0 <= cell["latched_normalized_estimate"] <= 1.0
            for cell in cells
        )
        and all(
            left["latched_normalized_estimate"] < right["latched_normalized_estimate"]
            for left, right in zip(cells, cells[1:])
        ),
        "default_off_observation_contract_preserved": disabled
        == {"state_shape": [115], "privileged_state_shape": [226], "latch_key_absent": True},
        "zero_training_or_dynamic_behavior": expansion["execution"]["training_steps"] == 0
        and expansion["execution"]["dynamic_behavior_cells"] == 0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_RESET_COM_ESTIMATOR_INPUT_CPU_PACKAGE_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_INPUT_CPU_PACKAGE_CONTRACT"
    payload = {
        "schema_version": "ground_up_reset_com_estimator_input_package_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": actual_hashes,
        "composed_source_hashes": composed_hashes,
        "expansion_result": {
            "path": str(expansion_path),
            "sha256": sha256(expansion_path),
            "status": expansion.get("status"),
            "expanded": expansion.get("expanded"),
            "output_equivalence": expansion.get("output_equivalence"),
        },
        "reset_cells": cells,
        "default_off_reset": disabled,
        "execution": {
            "devices": [str(device) for device in jax.devices()],
            "reset_cells": 3,
            "dynamic_steps": 0,
            "actor_calls_outside_checkpoint_equivalence": 0,
            "training_steps": 0,
            "colab": False,
            "local_gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "separate_hosted_training_preregistration_if_pass": True,
            "training_now": False,
            "colab_now": False,
            "behavior_evaluation_now": False,
            "robot_or_rdk": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
