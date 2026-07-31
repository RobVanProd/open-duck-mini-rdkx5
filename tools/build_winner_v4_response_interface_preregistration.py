from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT_JSON = ANALYSIS / "winner_v4_response_interface_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V4_RESPONSE_INTERFACE_PREREGISTRATION_20260720.md"

CURRENT_CONTRACT_PATH = (
    "outputs/analysis/winner_v3_current_gate_application_contract.json"
)
CURRENT_CONTRACT_SHA256 = "17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb"

RUNTIME_REPOSITORY = "https://github.com/RobVanProd/open-duck-mini-rdkx5-native-runtime.git"
RUNTIME_REVIEW_BASE_COMMIT = "e9c3c12191953180bfccdacec0e1e30ba91f94f9"
RUNTIME_PROFILE_SCHEMA = "open_duck_x5.automatic_configuration_profile.v4"
RUNTIME_PROFILE_SOURCE_SHA256 = "ea3262eac9a5a9f1d30ab8253ea758961a4525e65fab23c4e79c24f17b4bfc72"
RUNTIME_SUPPORT_SOURCE_SHA256 = "f1d05e2fb1e82d242b29fef6e4796f01d81bd686c7a61666bad6590e0b870cd5"
RUNTIME_SUPPORT_DOC_SHA256 = "090770dfc9c062a9df5e5cad3ab55efbe6e4fa2a9633464238351b3d56290438"

JOINT_NAMES = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
)
JOINT_METRICS = (
    "delay_ticks",
    "gain_ratio",
    "time_constant_s",
    "tracking_p95_rad",
    "current_p95_a",
)
BODY_METRICS = (
    "pitch_rate_p95_rad_s",
    "roll_rate_p95_rad_s",
    "acceleration_norm_p95_m_s2",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def feature_order() -> list[str]:
    fields = [
        f"joint_response.{joint}.{metric}"
        for joint in JOINT_NAMES
        for metric in JOINT_METRICS
    ]
    fields.extend(f"body_response.{metric}" for metric in BODY_METRICS)
    assert len(fields) == 73
    return fields


def build_preregistration() -> dict[str, object]:
    fields = feature_order()
    return {
        "schema_version": "open_duck_mini.winner_v4_response_interface_preregistration.v1",
        "status": "PREREGISTERED_PENDING_RUNTIME_REVIEW",
        "decision": "REQUEST_RUNTIME_SCHEMA_REVIEW_NO_IMPLEMENTATION",
        "causal_hypothesis": (
            "The broad recurrent adapter failed because the deployed policy had to infer "
            "episode dynamics only implicitly after control began. Supplying a deterministic, "
            "machine-collected pre-policy response context may make the supported configuration "
            "regime observable without a manual mass, COM, dimension, or component inventory."
        ),
        "falsification": (
            "Before training, the exact runtime-equivalent simulator excitation must produce a "
            "deterministic 73-vector and the signed X endpoint pair must not collapse to an "
            "identical vector. Any schema mismatch, nondeterminism, context collapse, or "
            "default-off actor change closes this formulation before PPO."
        ),
        "sources": {
            "current_gate_application": {
                "path": CURRENT_CONTRACT_PATH,
                "sha256": CURRENT_CONTRACT_SHA256,
            },
            "runtime": {
                "repository": RUNTIME_REPOSITORY,
                "review_base_commit": RUNTIME_REVIEW_BASE_COMMIT,
                "profile_schema": RUNTIME_PROFILE_SCHEMA,
                "configuration_profile_py_sha256": RUNTIME_PROFILE_SOURCE_SHA256,
                "configuration_support_py_sha256": RUNTIME_SUPPORT_SOURCE_SHA256,
                "automatic_configuration_support_md_sha256": RUNTIME_SUPPORT_DOC_SHA256,
            },
        },
        "policy_abi": {
            "contract_id": "winner-v4-response73-r64",
            "inputs": [
                {"name": "obs", "dtype": "float32", "shape": [1, 115]},
                {"name": "previous_action", "dtype": "float32", "shape": [1, 14]},
                {"name": "h_in", "dtype": "float32", "shape": [1, 64]},
                {"name": "response_context", "dtype": "float32", "shape": [1, 73]},
            ],
            "outputs": [
                {"name": "action", "dtype": "float32", "shape": [1, 14]},
                {
                    "name": "previous_action_out",
                    "dtype": "float32",
                    "shape": [1, 14],
                },
                {"name": "h_out", "dtype": "float32", "shape": [1, 64]},
            ],
            "canonical_observation_unchanged": True,
            "observation_contract": "winner-v2-115d",
            "action_semantics_unchanged": True,
            "phase_semantics_unchanged": True,
            "response_context_is_separate_input": True,
            "response_context_is_constant_for_episode": True,
            "response_context_normalization": "inside ONNX initializers; runtime sends SI values",
        },
        "response_context": {
            "source_schema": RUNTIME_PROFILE_SCHEMA,
            "dimension": len(fields),
            "dtype": "float32",
            "flatten_order": fields,
            "manual_measurements_used": False,
            "true_configuration_parameters_present": False,
            "fields_excluded": [
                "mass",
                "center_of_mass",
                "inertia",
                "component_inventory",
                "scale_measurement",
                "caliper_measurement",
            ],
            "required_profile_state": [
                "raw trace, metadata, and duck_config hashes reproduce profile v4",
                "physical profile was collected against the exact precommitted policy envelope",
                "all timing, freshness, transaction, and telemetry-drop checks pass",
                "all 73 values lie inside the selected policy's frozen response envelope",
            ],
            "runtime_failure_behavior": (
                "missing, stale, nonfinite, unreproducible, wrong-order, or out-of-envelope "
                "context prevents policy arming"
            ),
        },
        "runtime_review_questions": [
            "Does the 73-field flatten order exactly match profile v4 production and validation?",
            "Can runtime supply response_context as a separate immutable ONNX input without changing obs[115]?",
            "Can the context be hash-bound to the raw automatic calibration evidence and selected policy envelope before arming?",
            "Does any current runtime path silently reorder, scale, default, or substitute a context value?",
            "Does the supported/benched collection posture make the profile unsuitable as a policy-conditioning input?",
            "Are additional sign-preserving response fields required before a signed-X identifiability screen?",
        ],
        "required_pretraining_cpu_contract": {
            "formal_behavior_cells": 0,
            "ppo_steps": 0,
            "runtime_policy_flatteners_bit_exact_on_fixtures": True,
            "profile_reproduction_max_abs_error": 1e-9,
            "onnx_input_names_shapes_dtypes_exact": True,
            "default_off_protected_actor_action_and_state_bit_exact": True,
            "missing_nonfinite_wrong_order_context_rejected": True,
            "signed_x_endpoint_contexts_not_bit_identical": True,
            "repeat_contexts_bit_exact_for_same_model_and_seed": True,
            "no_true_configuration_or_manual_measurement_input": True,
            "runtime_review_commit_and_artifact_required": True,
        },
        "stop_rules": [
            "do not train before runtime review and the pretraining CPU contract both pass",
            "close this 73-D formulation if signed X endpoints collapse to an identical context",
            "do not append true mass, COM, inertia, or component identity to rescue the screen",
            "do not collect physical calibration evidence before a policy passes offline and publishes its envelope",
            "do not change the completed winner-v3 result",
        ],
        "authority": {
            "runtime_review_only": True,
            "runtime_implementation": False,
            "training": False,
            "hosted_compute": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "serial_gpio_i2c": False,
            "torque_or_motion": False,
            "gate5_or_deployment": False,
        },
    }


def render_markdown(prereg: dict[str, object], json_sha256: str) -> str:
    fields = prereg["response_context"]["flatten_order"]
    lines = [
        "# Winner-v4 Automatic-Response Interface Preregistration — 2026-07-20",
        "",
        f"status: `{prereg['status']}`",
        "",
        f"decision: `{prereg['decision']}`",
        "",
        f"JSON SHA-256: `{json_sha256}`",
        "",
        "## Hypothesis",
        "",
        str(prereg["causal_hypothesis"]),
        "",
        "This is not a training preregistration. It freezes a proposed deployment ABI for",
        "runtime review and a zero-PPO CPU contract. The completed winner-v3 result is not",
        "reclassified.",
        "",
        "## Proposed ONNX ABI",
        "",
        "```text",
        "obs[1,115], previous_action[1,14], h_in[1,64], response_context[1,73]",
        "  -> action[1,14], previous_action_out[1,14], h_out[1,64]",
        "```",
        "",
        "The existing 115-D observation, final-action semantics, phase timing, and recurrent",
        "state meanings remain unchanged. `response_context` is a separate immutable per-episode",
        "input. Runtime sends physical SI values; normalization is embedded in the ONNX graph.",
        "",
        "## Exact 73-field order",
        "",
    ]
    lines.extend(f"{index}. `{field}`" for index, field in enumerate(fields))
    lines.extend(
        [
            "",
            "No mass, COM, inertia, component identity, scale reading, caliper reading, or manual",
            "per-build value is present. The context is reproduced from the runtime's immutable",
            "automatic-excitation trace, metadata, and `duck_config.json`.",
            "",
            "## Pretraining falsification",
            "",
            "Before any PPO step, policy and runtime flatteners must be bit-exact on committed",
            "fixtures; the profile must reproduce within `1e-9`; the protected actor must remain",
            "bit-exact with its new branch disabled; and repeated simulator response contexts must",
            "be deterministic. The exact signed X endpoint pair must not collapse to an identical",
            "73-vector. A collapse closes this formulation; true configuration parameters may not",
            "be appended as a rescue.",
            "",
            "## Runtime review required",
            "",
        ]
    )
    lines.extend(f"- {question}" for question in prereg["runtime_review_questions"])
    lines.extend(
        [
            "",
            "## Authority",
            "",
            "This artifact requests schema review only. It authorizes no runtime implementation,",
            "training, Colab, GPU/iGPU, X5 or robot access, serial/GPIO/I2C, torque, motion, Gate 5,",
            "deployment, or robot clearance.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args(argv)

    prereg = build_preregistration()
    json_bytes = (json.dumps(prereg, indent=2, sort_keys=True) + "\n").encode("utf-8")
    json_sha256 = sha256_bytes(json_bytes)
    markdown = render_markdown(prereg, json_sha256)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_bytes(json_bytes)
    args.output_md.write_text(markdown, encoding="utf-8")
    print(f"status={prereg['status']} json_sha256={json_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
