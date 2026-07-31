from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT_JSON = ANALYSIS / "winner_v4_response_pretraining_contract.json"
OUTPUT_MD = ANALYSIS / "WINNER_V4_RESPONSE_PRETRAINING_CONTRACT_20260720.md"

INTERFACE_PATH = "outputs/analysis/winner_v4_response_interface_preregistration.json"
INTERFACE_SHA256 = "562ea92c4ba9eb026263740a07fe349ed79e051f0a162e8dd476812f089b6adc"
RUNTIME_REPOSITORY = "https://github.com/RobVanProd/open-duck-mini-rdkx5-native-runtime.git"
RUNTIME_REVIEW_COMMIT = "fc4eb2651113ef2bfc8839ec2289725cea8c3a51"
RUNTIME_REVIEW_PATH = "artifacts/gates/phase_0_audit/winner_v4_response_review/result.json"
RUNTIME_REVIEW_SHA256 = "e860ac7c93565ef6bba9bc08435565faa75cca0768dc7392f6415b66629f55f8"
RUNTIME_COLLECTOR_SHA256 = "d581e26b520e429e9efeddabe2f51a8f533b8b4851101a4abdc4da8b75f079a9"
RUNTIME_PROFILE_SHA256 = "ea3262eac9a5a9f1d30ab8253ea758961a4525e65fab23c4e79c24f17b4bfc72"
RUNTIME_FLATTENER_SHA256 = "9648d8927415ee23caf714e8d8767bd8e0b305d2ec4f2f0c11dbf0ddc635070d"
PLAYGROUND_REPOSITORY = "https://github.com/apirrone/Open_Duck_Playground.git"
PLAYGROUND_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
P30_PATH = "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
P30_SHA256 = "908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b"
P31_PATH = "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json"
P31_SHA256 = "a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276"
JOB_PATH = "tools/run_winner_v4_response_identifiability_cpu.py"

SUPPORT_MODE_ID = "feet_supported_flat_floor_free_body_passive_fall_catch_v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_contract() -> dict[str, object]:
    return {
        "schema_version": "open_duck_mini.winner_v4_response_pretraining_contract.v1",
        "status": "PREREGISTERED_CPU_FALSIFICATION_NOT_RUN",
        "decision": "AUTHORIZE_ONE_ZERO_PPO_CPU_RESPONSE_IDENTIFIABILITY_RUN",
        "hypothesis": (
            "The runtime-exact 73-value automatic response context remains observable after "
            "physical sensor quantization and distinguishes the frozen -0.05 m and +0.05 m "
            "torso-X endpoints while the robot is feet-supported and otherwise unconstrained."
        ),
        "sources": {
            "interface": {"path": INTERFACE_PATH, "sha256": INTERFACE_SHA256},
            "runtime_review": {
                "repository": RUNTIME_REPOSITORY,
                "commit": RUNTIME_REVIEW_COMMIT,
                "path": RUNTIME_REVIEW_PATH,
                "sha256": RUNTIME_REVIEW_SHA256,
            },
            "runtime_code": {
                "configuration_collector_sha256": RUNTIME_COLLECTOR_SHA256,
                "configuration_profile_sha256": RUNTIME_PROFILE_SHA256,
                "response_context_review_sha256": RUNTIME_FLATTENER_SHA256,
            },
            "playground": {
                "repository": PLAYGROUND_REPOSITORY,
                "commit": PLAYGROUND_COMMIT,
                "scene": "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml",
            },
            "actuator_fits": [
                {"id": "p30_all_joint", "path": P30_PATH, "sha256": P30_SHA256},
                {
                    "id": "p31_34_pitch_with_p30_nonpitch",
                    "path": P31_PATH,
                    "sha256": P31_SHA256,
                },
            ],
            "job": {"path": JOB_PATH, "sha256": sha256_path(ROOT / JOB_PATH)},
        },
        "support_mode": {
            "id": SUPPORT_MODE_ID,
            "manual_measurement_required": False,
            "physical_boundary": [
                "a rigid, level, stationary surface supports both feet",
                "both frozen binary foot contacts remain true during the complete accepted home-settle and excitation population",
                "the floating body is not suspended, clamped, or intentionally loaded at the torso, head, limbs, or external stand",
                "a passive fall catch may surround the robot but must remain mechanically clear throughout accepted evidence",
                "loss of either foot contact or contact with the passive catch aborts and discards the calibration",
            ],
            "simulator_realization": {
                "scene": "flat_terrain_backlash",
                "floating_base": True,
                "gravity_enabled": True,
                "external_forces": False,
                "equality_or_support_constraints": False,
                "torso_support_contact": False,
                "floor_contact_is_physical": True,
                "home_keyframe": "home",
                "home_settle_ticks": 250,
                "control_period_s": 0.02,
                "physics_substeps_per_control_tick": 10,
                "accepted_contact_state": [1, 1],
            },
            "rejected_modes": [
                "free_hanging_or_suspended",
                "torso_supported_or_clamped",
                "feet_unloaded",
                "single_foot_supported",
                "passive_catch_touching_or_load_bearing",
            ],
            "future_runtime_requirement": (
                "Before physical policy conditioning, runtime must hash-bind this exact support-mode "
                "identifier to the raw calibration evidence and reject every other mode."
            ),
        },
        "experiment": {
            "backend": "MuJoCo 3.9.0 CPU double precision",
            "training_steps": 0,
            "formal_behavior_cells": 0,
            "torso_body": "trunk_assembly",
            "torso_x_offsets_m": [-0.05, 0.05],
            "actuator_fit_count": 2,
            "repeats_per_endpoint_and_fit": 2,
            "excitation": {
                "frequency_hz": 50,
                "joint_order": "runtime frozen logical order",
                "stage_ticks": 201,
                "tick_count": 2814,
                "target_rad": "home + 0.015*sin(2*pi*t/40) + 0.005*sin(2*pi*t/20)",
                "one_joint_at_a_time": True,
            },
            "actuator_transition": {
                "delay_tau_velocity_limit": "selected measured fit",
                "home_relative_gain_ratio": True,
                "target_quantization": "STS3215 4096-count floor conversion before bridge",
            },
            "sensor_quantization": {
                "present_position_rad": "nearest STS3215 4096-count position",
                "present_current_a": 0.0065,
                "gyro_rad_s": "pi/(180*16)",
                "acceleration_m_s2": 0.01,
            },
            "profile_extraction": "runtime open_duck_x5.automatic_configuration_profile.v4 builder",
            "context_flattening": "runtime-reviewed exact 73-field order, float32",
        },
        "pass_requirements": [
            "all frozen source hashes and versions match",
            "model actuator order and home control equal the frozen 14-joint runtime values exactly",
            "both foot contacts remain true for every accepted settle and excitation tick",
            "all eight runtime-profile extractions complete with 73 finite float32 values",
            "same fit, endpoint, and seed repeat produces a bit-exact 73-vector",
            "for each actuator fit, the quantized -0.05 m and +0.05 m endpoint contexts are not bit-identical",
            "the two policy and runtime field-order lists are exactly equal",
        ],
        "persistence_and_stop_rules": {
            "pass_requires_both_fits": True,
            "retry_allowed": False,
            "if_endpoint_collapses": "close response73 before PPO",
            "if_support_mode_fails": "hold and redesign the automatic response procedure before PPO",
            "if_any_source_or_contract_check_fails": "invalidate the run without training",
            "true_mass_com_inertia_or_component_identity_rescue_forbidden": True,
        },
        "next_if_pass": (
            "Freeze and run a separate zero-PPO policy implementation contract for the response branch, "
            "default-off protected-actor identity, ONNX ABI, rejection behavior, and normalization."
        ),
        "authority": {
            "one_cpu_falsification_run": True,
            "hosted_cpu_allowed_if_local_cpu_unavailable": True,
            "gpu_or_igpu": False,
            "ppo_or_training": False,
            "policy_architecture_implementation": False,
            "runtime_implementation": False,
            "rdkx5_or_robot": False,
            "serial_gpio_i2c": False,
            "torque_or_motion": False,
            "gate5_or_deployment": False,
            "robot_clearance": False,
        },
    }


def render_markdown(contract: dict[str, object], json_sha256: str) -> str:
    support = contract["support_mode"]
    lines = [
        "# Winner-v4 Response Pretraining Contract — 2026-07-20",
        "",
        f"status: `{contract['status']}`",
        "",
        f"decision: `{contract['decision']}`",
        "",
        f"JSON SHA-256: `{json_sha256}`",
        "",
        "## What this resolves",
        "",
        str(contract["hypothesis"]),
        "",
        "The runtime accepted the exact 73-field ABI but held training on two points: signed-X",
        "identifiability and an underspecified calibration support boundary. This contract freezes",
        "both before running any PPO step.",
        "",
        "## Frozen support mode",
        "",
        f"ID: `{support['id']}`",
        "",
    ]
    lines.extend(f"- {item}" for item in support["physical_boundary"])
    lines.extend(
        [
            "",
            "This requires no scale, caliper, entered COM, component inventory, or other manual",
            "per-build measurement. The simulator uses the same flat-floor, free-body boundary:",
            "gravity and physical foot contact are active, and there is no torso support, equality",
            "constraint, or external force.",
            "",
            "## Frozen CPU falsification",
            "",
            "For torso X = `-0.05 m` and `+0.05 m`, under both measured actuator fits, run the",
            "runtime's exact 2,814-tick one-joint-at-a-time excitation after a 250-tick home",
            "settle. Quantize targets, positions, current, gyro, and acceleration to the physical",
            "interfaces before calling the runtime profile-v4 extractor. Repeat every cell twice.",
            "",
            "Pass requires bit-exact repeats and a non-identical signed endpoint context under",
            "each actuator fit. Either signed pair collapsing closes response73 before training.",
            "",
            "## Authority",
            "",
            "This authorizes one CPU-only, zero-PPO falsification run, locally or on hosted CPU.",
            "It authorizes no policy implementation, training, GPU/iGPU, runtime implementation,",
            "robot/X5 access, serial/GPIO/I2C, torque, motion, Gate 5, deployment, or clearance.",
            "A pass authorizes only a separate policy implementation contract.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args(argv)
    contract = build_contract()
    payload = (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode()
    digest = sha256_bytes(payload)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(payload)
    args.output_md.write_text(render_markdown(contract, digest), encoding="utf-8")
    print(f"status={contract['status']} json_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
