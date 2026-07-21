#!/usr/bin/env python3
"""Freeze the prospective Winner-v12 calibrator CPU-smoke implementation."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json"
MARKDOWN = (
    ROOT / "outputs/analysis/WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT_20260720.md"
)
CALIBRATOR_PREREG = (
    ROOT / "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
)
DOMAIN_PREREG = (
    ROOT
    / "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
)
TRAINING = ROOT / "patches/winner_v12_calibrator_training.py"
RUNNER = ROOT / "tools/run_winner_v12_calibrator_cpu_smoke.py"
WORKFLOW = ROOT / ".github/workflows/winner-v12-calibrator-cpu-smoke.yml"

SOURCE_PATHS = {
    "workflow": (".github/workflows/winner-v12-calibrator-cpu-smoke.yml", "lf"),
    "builder": ("tools/build_winner_v12_calibrator_cpu_smoke_contract.py", "lf"),
    "runner": ("tools/run_winner_v12_calibrator_cpu_smoke.py", "lf"),
    "importer": ("tools/import_winner_v12_calibrator_cpu_smoke.py", "lf"),
    "tests": ("tests/test_winner_v12_calibrator_cpu_smoke_contract.py", "lf"),
    "training_primitives": ("patches/winner_v12_calibrator_training.py", "lf"),
    "decomposed_network": (
        "patches/winner_v12_decomposed_backend_networks.py",
        "lf",
    ),
    "winner_v11_network": (
        "patches/winner_v11_dynamic_calibration_networks.py",
        "lf",
    ),
    "winner_v6_network": (
        "patches/winner_v6_dynamic_calibration_networks.py",
        "lf",
    ),
    "calibrator_preregistration": (
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json",
        "lf",
    ),
    "mechanics_preregistration": (
        "outputs/analysis/winner_v12_zero_ppo_decomposed_backend_preregistration.json",
        "lf",
    ),
    "mechanics_result": (
        "outputs/analysis/winner_v12_zero_ppo_decomposed_backend_result.json",
        "lf",
    ),
    "domain_preregistration": (
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json",
        "lf",
    ),
    "current_gate": (
        "outputs/analysis/winner_v3_current_gate_application_contract.json",
        "lf",
    ),
    "p30_fit": (
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
        "lf",
    ),
    "p31_34_fit": (
        "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
        "lf",
    ),
    "runtime_observer": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py",
        "lf",
    ),
    "runtime_observer_contract": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer_contract.json",
        "lf",
    ),
    "runtime_observer_cross_fit": (
        "outputs/analysis/winner_v2_observer_cross_fit_result.json",
        "lf",
    ),
    "runtime_observation_map": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observation_map.json",
        "lf",
    ),
    "reference_table": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/reference/ground_up_projected_reference_feature_table.npz",
        "raw",
    ),
    "winner_v10_representation": (
        "outputs/analysis/winner_v10_inward_torque_contract_result.json",
        "lf",
    ),
    "winner_v10_nominal": (
        "outputs/analysis/winner_v10_nominal_behavior_result.json",
        "lf",
    ),
    "playground_composer": ("tools/compose_winner_v7_playground.py", "lf"),
    "actuator_bridge": ("tools/actuator_bridge_model.py", "lf"),
    "corrected_support_harness": (
        "tools/run_winner_v5_automatic_support_recovery_cpu.py",
        "lf",
    ),
}

EXPECTED_IDS = [
    "MASS_LOW",
    "MASS_HIGH",
    "COM_X_NEG",
    "COM_X_POS",
    "COM_Y_NEG",
    "COM_Y_POS",
    "COM_Z_NEG",
    "COM_Z_POS",
    "INERTIA_X_LOW",
    "INERTIA_X_HIGH",
    "INERTIA_Y_LOW",
    "INERTIA_Y_HIGH",
    "INERTIA_Z_LOW",
    "INERTIA_Z_HIGH",
    "COM_CORNER_00",
    "COM_CORNER_01",
]
PLANTS = [
    "P30_ALL_JOINT" if index % 2 == 0 else "P31_34_PITCH_WITH_P30_NONPITCH"
    for index in range(16)
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def function_arguments(path: Path, name: str) -> list[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return [argument.arg for argument in node.args.args]
    raise ValueError(f"missing function: {name}")


def source_manifest() -> dict[str, dict[str, str]]:
    manifest = {}
    for name, (relative, mode) in SOURCE_PATHS.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest[name] = {
            "path": relative,
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
    return manifest


def main() -> int:
    preregistration = json.loads(CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN_PREREG.read_text(encoding="utf-8"))
    population = domain["evaluation_matrix"]["fixed_anchors"][:16]
    population_ids = [row["id"] for row in population]
    training_source = TRAINING.read_text(encoding="utf-8")
    runner_source = RUNNER.read_text(encoding="utf-8")
    workflow_source = WORKFLOW.read_text(encoding="utf-8")
    forbidden_arguments = {
        "configuration",
        "mass",
        "com",
        "inertia",
        "plant",
        "fit",
        "body",
        "randomizer",
    }
    routing_functions = (
        "response_step",
        "stage1_predictions",
        "stage1_loss",
        "stage2_mean_value",
        "sample_stage2_action",
        "stage2_ppo_loss",
    )
    routing_arguments = {
        name: function_arguments(TRAINING, name) for name in routing_functions
    }
    checks = {
        "corrected_v2_preregistration_exact": preregistration.get("schema_version")
        == "winner_v12.calibrator_training_preregistration.v2"
        and preregistration.get("status") == "PREREGISTERED_IMPLEMENTATION_NOT_RUN"
        and preregistration.get("decision")
        == "AUTHORIZE_WINNER_V12_CALIBRATOR_IMPLEMENTATION_AND_CPU_SMOKE_CONTRACT_ONLY",
        "zero_optimizer_steps_before_contract": preregistration["authority"][
            "optimizer_steps_now"
        ]
        == 0,
        "mechanics_result_passed": preregistration["why_this_follows_evidence"][
            "winner_v12_mechanics_pass"
        ]
        == "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS",
        "fixed_p30_observer_required": preregistration["calibration_episode"][
            "applied_target_observation"
        ]
        == (
            "exact fixed runtime P30 observer for every episode, including when "
            "the hidden physical plant is P31/34"
        ),
        "population_exact": population_ids == EXPECTED_IDS,
        "population_has_com_x_neg": "COM_X_NEG" in population_ids,
        "population_has_no_heldout": not any(
            identifier.startswith("HELDOUT") for identifier in population_ids
        ),
        "plants_balanced": PLANTS.count("P30_ALL_JOINT") == 8
        and PLANTS.count("P31_34_PITCH_WITH_P30_NONPITCH") == 8,
        "network_routing_has_no_privileged_arguments": all(
            not (set(arguments) & forbidden_arguments)
            for arguments in routing_arguments.values()
        ),
        "deployable_mapping_excludes_training_heads": (
            "DEPLOYABLE_CALIBRATOR_KEYS = ENCODER_AUXILIARY_KEYS + DEPLOYABLE_ACTION_KEYS"
            in training_source
            and "return _select(parameters, DEPLOYABLE_CALIBRATOR_KEYS)"
            in training_source
        ),
        "stage1_fixed_p30_observer_literal": (
            "self.observer = observer_type(canonical_fit, HOME_RAD)" in runner_source
            and "next_observation[83:97], episode.observer.value.astype(np.float32)"
            in runner_source
        ),
        "hidden_plant_separate_from_observer_literal": (
            "self.bridge = ActuatorBridgeModel(" in runner_source
            and "applied_target = self.bridge.step(sent_target, CONTROL_DT_S)"
            in runner_source
            and "observed_target = self.observer.step(sent_target, CONTROL_DT_S)"
            in runner_source
        ),
        "phase_and_reference_frozen_literal": (
            "np.asarray([1.0, 0.0]" in runner_source and "np.zeros(14" in runner_source
        ),
        "one_update_per_stage_literal": (
            '"optimizer_updates": {"stage1": 1, "stage2": 1}' in runner_source
            and '"retry_count": 0' in runner_source
        ),
        "terminal_action_retention_literal": (
            "sample_mask[environment, tick] = 1.0" in runner_source
            and "done[environment, tick] = 1.0" in runner_source
            and '"stage2_terminal_actions_retained_with_done"' in runner_source
        ),
        "support_boundaries_have_nextafter_canaries": (
            "def support_boundary_canary()" in runner_source
            and "np.nextafter(MINIMUM_BASE_Z_M, -math.inf)" in runner_source
            and "np.nextafter(TORQUE_LIMIT_NM, math.inf)" in runner_source
            and "np.nextafter(CURRENT_LIMIT_A, math.inf)" in runner_source
        ),
        "nonfinite_evidence_fails_closed": (
            "nonfinite MuJoCo transition state" in runner_source
            and "nonfinite JAX or ONNX chain output" in runner_source
            and "allow_nan=False" in runner_source
            and '"onnx_chain_outputs_finite"' in runner_source
        ),
        "playground_assets_fail_closed": (
            "def validate_playground_tree(" in runner_source
            and "PLAYGROUND_RECEIPT_LF_SHA256" in runner_source
            and '"status", "--porcelain=v1"' in runner_source
            and "observed_paths != expected_paths" in runner_source
            and "composed Playground file drift" in runner_source
        ),
        "software_versions_fail_closed": (
            "def validate_software_versions(" in runner_source
            and '"software_versions_exact"' in runner_source
            and '"canonical_lf_sha256"' in runner_source
        ),
        "manual_single_run_workflow_frozen": (
            "workflow_dispatch:" in workflow_source
            and "push:" not in workflow_source
            and 'python-version: "3.12.13"' in workflow_source
            and "fetch-depth: 0" in workflow_source
            and "matrix:" not in workflow_source
            and "run_winner_v12_calibrator_cpu_smoke.py" in workflow_source
        ),
        "protected_policies_not_inferred": (
            "InferenceSession(str(args.policy_half)" not in runner_source
            and "InferenceSession(str(args.policy_final)" not in runner_source
        ),
        "no_unbounded_retry_loop": "while True" not in runner_source,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Winner-v12 smoke contract checks failed: {failed}")
    payload = {
        "schema_version": "winner_v12.calibrator_cpu_smoke_contract.v1",
        "status": "PASS_WINNER_V12_CALIBRATOR_CPU_SMOKE_CONTRACT",
        "decision": "AUTHORIZE_ONE_WINNER_V12_CPU_SMOKE_ONLY",
        "causal_scope": (
            "implementation plumbing only: prove one two-stage update can consume "
            "deployable response evidence, preserve stage isolation, save/restore, "
            "and export the reviewed graph without privileged state"
        ),
        "smoke_population": {
            "root_seed": 120120,
            "environment_count": 16,
            "ticks_per_environment": 250,
            "observation_states_per_full_episode": 251,
            "configuration_source": (
                "first 16 fixed anchors in the frozen winner-v3 evaluation matrix; "
                "not discovery-selected and not heldout"
            ),
            "configuration_ids": population_ids,
            "configuration_hashes": [canonical_sha256(row) for row in population],
            "population_sha256": canonical_sha256(population),
            "plant_assignments": PLANTS,
            "prng_derivation": (
                "NumPy SeedSequence([120120, stage_id, environment_index]) -> PCG64; "
                "stage_id 1 for ternary exploration and 2 for Gaussian exploration"
            ),
        },
        "simulator": {
            "backend": "classic MuJoCo CPU double-precision physics",
            "playground_commit": "b9be205ac64488c23504ca42e5ec790337adeec3",
            "composition_receipt_canonical_lf_sha256": "628c35fab95e41a2fa82ae2255e0109502d72632c7ad408bf7e1294f5eb1c196",
            "composition": "hash-checked Winner-v7 115-D source tree with reviewed Winner-v10 XML copied into the existing asset directory",
            "asset_integrity": (
                "the canonical composition receipt identity and every changed-file "
                "raw hash are pinned; git status must "
                "contain exactly those files plus the two reviewed XMLs and receipt, "
                "so mesh and other compiled assets remain clean at the pinned commit"
            ),
            "model_path": "playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml",
            "model_sha256": "660fa8e4ac0d977806e881d008090e7153cd0608dbee05b88f957a91bde6f655",
            "scene_path": "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
            "scene_sha256": "65324e27a3a84e2e42d1073bfc636f9cdbf6bef7b1f20c1b5a886b8fd58fcc71",
            "home_reset": (
                "correct-order mj_setConst on default MjData, then exact home keyframe "
                "qpos, zero qvel, home ctrl, mj_forward"
            ),
            "control_dt_s": 0.02,
            "physics_substeps_per_tick": 10,
            "command": [0.0] * 7,
            "phase": [1.0, 0.0],
            "phase_advances": False,
            "projected_reference": [0.0] * 14,
            "reset_support": (
                "flat rigid floor, both feet loaded, no torso/limb/head support or "
                "external force"
            ),
        },
        "observation_and_transition": {
            "observation_dim": 115,
            "action_dim": 14,
            "auxiliary_indices": list(range(0, 6))
            + list(range(13, 41))
            + list(range(83, 99)),
            "obs_83_97": (
                "fixed runtime P30 observer under both hidden physical plants; a "
                "canonical LF copy of the frozen fit is used only to satisfy the "
                "runtime observer's raw hash check"
            ),
            "hidden_physical_plant": (
                "alternating P30 and P31/34; affects bridge-driven physics/sensors "
                "only and never selects the observation observer"
            ),
            "history_at_tick_t": (
                "previous_action input is a_(t-1); obs[41:55], [55:69], [69:83] "
                "are a_(t-2), a_(t-3), a_(t-4)"
            ),
            "valid_commit": (
                "current action, history, fixed observer output, and recurrent h_out "
                "commit only after a valid physics transition; invalid and padded "
                "ticks are masked"
            ),
            "terminal_action_training_sample": (
                "the action that creates an invalid transition is retained as an "
                "attempted PPO sample with reward 0 and done=1; its invalid next "
                "state is not committed and never enters Stage-1 targets"
            ),
            "stage1_target": "next valid obs_(t+1) at the 50 frozen indices",
            "heldout_in_training_or_normalization": False,
        },
        "hyperparameters": {
            "stage1": {
                "learning_rate": 1.0e-4,
                "adam_beta1": 0.9,
                "adam_beta2": 0.999,
                "adam_epsilon": 1.0e-8,
                "weight_decay": 0.0,
                "bptt_ticks": 250,
                "optimizer_updates": 1,
                "ternary_probabilities": {
                    "-1": 1.0 / 3.0,
                    "0": 1.0 / 3.0,
                    "1": 1.0 / 3.0,
                },
            },
            "target_normalization": (
                "all valid Stage-1 smoke targets only; NumPy float64 population "
                "mean/std ddof=0; std=max(std,1e-6); cast mean/std to float32"
            ),
            "stage2": {
                "learning_rate": 1.0e-4,
                "adam_beta1": 0.9,
                "adam_beta2": 0.999,
                "adam_epsilon": 1.0e-8,
                "weight_decay": 0.0,
                "gamma": 1.0,
                "gae_lambda": 0.95,
                "clip_epsilon": 0.2,
                "value_coefficient": 0.5,
                "entropy_coefficient": 0.001,
                "ppo_epochs": 1,
                "minibatches": 1,
                "optimizer_updates": 1,
                "advantage_normalization": (
                    "all valid smoke transitions; float64 population mean/std; "
                    "std floor 1e-6; cast float32"
                ),
                "timeout_bootstrap": 0.0,
                "log_std_clamp": [-5.0, 1.0],
            },
            "gradient_clipping": None,
        },
        "support_logic": {
            "per_valid_tick_reward": 1.0,
            "invalid_transition_reward": 0.0,
            "invalid_transition_action_in_ppo_batch": True,
            "invalid_next_state_in_auxiliary_batch": False,
            "terminal_bonus": 250.0,
            "terminal_bonus_condition": (
                "all 250 transitions valid and max unbiased gyro-XY norm over final "
                "50 ticks <=0.05 rad/s"
            ),
            "minimum_base_z_m": 0.1,
            "maximum_abs_roll_pitch_rad": 0.35,
            "both_contacts_required": True,
            "per_joint_peak_torque_nm_max": 1.91229675,
            "per_joint_peak_current_a_max": 2.5,
            "current_nm_per_a": 0.784532,
            "strict_overcurrent_threshold_a": 2.0,
            "strict_overcurrent_trip_ticks": 100,
            "maximum_allowed_consecutive_overcurrent_ticks": 99,
        },
        "required_positive_proofs": [
            "exact source/domain/XML/policy hashes and CPU-only execution",
            "exact composition receipt and no unexpected dirty or untracked Playground asset",
            "exact 16-row population, 250 transitions, 251-state timing, and balanced hidden plants",
            "fixed-P30 obs[83:97] under both physically distinct P30/P31-34 plants",
            "bit-exact NumPy/JAX graph action boundary and realized-action history chain",
            "Stage 1 updates only encoder/auxiliary leaves and has nonzero previous-action and auxiliary-action gradients",
            "Stage 2 updates every action/log_std/value leaf while encoder/auxiliary leaves stay bit-exact",
            "validity, termination, current streak, and terminal gyro bonus match the frozen definitions",
            "the failure-causing action is retained with reward zero/done and threshold boundaries pass deterministic nextafter canaries",
            "independent XML force-range readback stays within 1.91229675 N.m",
            "all parameters, gradients, losses, observations, actions, and metrics are finite",
            "all train state saves/restores bit-exact",
            "protected policies and the untrained locomotion adapter are bit-exact and unused",
            "exported calibrator has exact three-input/three-output ABI, no training-only tensors, and 250-tick JAX/ONNX error <=1e-7",
        ],
        "protected_policies": {
            "half": "cf001269908d86e47eaa145ffda1d87e946a314ecf51056dc086c4cf10164ab6",
            "final": "d52b63241340d9d56671b95c58bb0fc72af0998fd47d4684719f6cd44f244a10",
        },
        "software_versions": {
            "python": "3.12.13",
            "jax": "0.7.2",
            "jaxlib": "0.7.2",
            "mujoco": "3.9.0",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
            "numpy": "2.0.2",
        },
        "checks": checks,
        "sources": source_manifest(),
        "authority": {
            "formal_support_cells": 0,
            "full_calibrator_training": False,
            "hosted_gpu_or_igpu": False,
            "locomotion_training_or_behavior_evaluation": False,
            "optimizer_updates_authorized": {"stage1": 1, "stage2": 1},
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "robot_clearance": False,
        },
        "pass_authorizes_only": (
            "one no-retry CPU smoke producing an auditable result; a pass permits only "
            "a separate prospective full-calibrator training preregistration"
        ),
        "post_smoke_stop": True,
        "flat_transport_kernel": {
            "implemented": False,
            "reason": (
                "the R64 calibrator has not yet shown a long-range transport failure; "
                "K_n,L remains a preregisterable future falsification, not an "
                "unmeasured architecture substitution"
            ),
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Winner-v12 calibrator CPU-smoke contract",
        "",
        f"- Status: `{payload['status']}`",
        f"- Decision: `{payload['decision']}`",
        "- Execution: one CPU-only 16-environment × 250-tick smoke",
        "- Optimizer: exactly one Stage-1 update and one Stage-2 update",
        "- Formal support cells: `0`",
        "- Robot clearance: `false`",
        "",
        "The smoke validates training plumbing, stage isolation, automatic response",
        "routing, save/restore, and the deployable ONNX boundary. It does not select",
        "a policy or measure supported-configuration behavior.",
        "",
        "The observation observer is always the runtime P30 observer. Alternating",
        "P30/P31-34 selections are hidden physical plants only; they cannot alter",
        "obs[83:97] directly or enter the actor, critic, or auxiliary target as labels.",
        "",
        "A pass stops for review and permits only a separate prospective full-training",
        "preregistration. It grants no hosted compute, X5, Gate 5, or robot authority.",
        "",
    ]
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT),
                "output_sha256": sha256(OUTPUT),
                "population_sha256": payload["smoke_population"]["population_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
