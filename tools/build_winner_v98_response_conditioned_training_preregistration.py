#!/usr/bin/env python3
"""Freeze the Winner-v98 response-conditioned CPU training smoke."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v98_response_conditioned_training_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V98_RESPONSE_CONDITIONED_TRAINING_PREREGISTRATION_20260722.md"
)
POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
GOLDEN_ZERO = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.000.npz"
)
GOLDEN_MOVING = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/golden/"
    "T2_EQUAL_512000_x0.080.npz"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
V97_RESULT = ANALYSIS / "winner_v97_mechanics_numeric_correction_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CONTROL_COMMIT = "b9be205ac64488c23504ca42e5ec790337adeec3"
POLICY_SHA256 = "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
CALIBRATOR_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
SOURCE_CHECKPOINT_SHA256 = (
    "311ce59807ad872795dd95e4a30c626f11d3d80f1b3f78c5b2b997639da4d67e"
)
SOURCE_MEMBER = (
    "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190026_512000"
)
V97_RESULT_SHA256 = (
    "f163eb084f58b3e663d176d13d93b3481633bf09216d8b5dd10ddd0a27c13d58"
)
EXPECTED_REPOSITORY_HASHES = {
    "policy": POLICY_SHA256,
    "golden_x0": "aa84f0cbd4e885f9dcc36c553c43e17030f32d0304dff2a7bf06f1f41c4cbe2e",
    "golden_x008": "0cfd9e99bf499028b5b7f285fa1964f65248795592cf9d072c4bc5aa1a56fb1c",
    "reference": "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212",
    "archive": "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
    "v97_result": V97_RESULT_SHA256,
    "domain": "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v98 contract: {path}")
    playground = args.playground_root.resolve()
    source_checkpoint = args.source_checkpoint.resolve()
    calibrator = args.calibrator.resolve()
    if directory_sha256(source_checkpoint) != SOURCE_CHECKPOINT_SHA256:
        raise ValueError("Winner-v98 selected source checkpoint changed")
    if sha256(calibrator) != CALIBRATOR_SHA256:
        raise ValueError("Winner-v98 response calibrator changed")
    v97 = json.loads(V97_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V97_RESULT) != V97_RESULT_SHA256
        or v97.get("status") != "PASS_WINNER_V97_MECHANICS_NUMERIC_CORRECTION"
        or v97.get("failed_checks") != []
    ):
        raise ValueError("Winner-v98 prerequisite mechanics result changed")

    repository_paths = {
        "policy": POLICY,
        "golden_x0": GOLDEN_ZERO,
        "golden_x008": GOLDEN_MOVING,
        "reference": REFERENCE,
        "archive": ARCHIVE,
        "v97_result": V97_RESULT,
        "domain": DOMAIN,
    }
    observed_repository_hashes = {
        name: sha256(path) for name, path in repository_paths.items()
    }
    if observed_repository_hashes != EXPECTED_REPOSITORY_HASHES:
        raise ValueError(
            f"Winner-v98 repository binary changed: {observed_repository_hashes}"
        )
    repository_binaries = {
        name: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": observed_repository_hashes[name],
        }
        for name, path in repository_paths.items()
    }

    manifest_path = playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != "winner_v98.composed_playground_source.v1"
        or manifest.get("control_commit") != CONTROL_COMMIT
        or manifest.get("stop_before_winner_v98") is not False
        or set(manifest.get("copied_source_destinations", {}).values())
        < {
            "playground/common/winner_v98_response_conditioned_ppo_networks.py",
            "playground/common/winner_v98_response_calibration_wrapper.py",
            "playground/common/winner_v98_response_conditioned_export.py",
        }
    ):
        raise ValueError("Winner-v98 composed source manifest changed")
    composed_relative_paths = (
        "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json",
        "WINNER_V98_COMPOSED_SOURCE.diff",
        "playground/common/runner.py",
        "playground/common/randomize.py",
        "playground/common/winner_v3_variable_configuration.py",
        "playground/common/winner_v98_response_conditioned_ppo_networks.py",
        "playground/common/winner_v98_response_calibration_wrapper.py",
        "playground/common/winner_v98_response_conditioned_export.py",
        "playground/open_duck_mini_v2/joystick.py",
        "playground/open_duck_mini_v2/runner.py",
    )
    composed_files = {
        relative: sha256(playground / relative)
        for relative in composed_relative_paths
    }

    source_paths = {
        "builder": Path(
            "tools/build_winner_v98_response_conditioned_training_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v98_response_conditioned_cpu_contract.py"),
        "composer": Path("tools/compose_winner_v98_playground.py"),
        "network": Path("patches/winner_v98_response_conditioned_ppo_networks.py"),
        "calibration_wrapper": Path(
            "patches/winner_v98_response_calibration_wrapper.py"
        ),
        "exporter": Path("patches/winner_v98_response_conditioned_export.py"),
        "integration_patch": Path("patches/ground_up_response_conditioned_locomotion.patch"),
        "v96_network": Path("patches/winner_v96_response_conditioned_networks.py"),
        "v6_network": Path("patches/winner_v6_dynamic_calibration_networks.py"),
    }
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in source_paths.items()
    }
    software_versions = {
        name: importlib.metadata.version(name)
        for name in (
            "brax",
            "flax",
            "jax",
            "jaxlib",
            "mujoco",
            "mujoco-mjx",
            "numpy",
            "onnx",
            "onnxruntime",
            "optax",
            "orbax-checkpoint",
            "playground",
        )
    }
    value = {
        "schema_version": "winner_v98.response_conditioned_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V98_RESPONSE_CONDITIONED_CPU_SMOKE",
        "decision": "AUTHORIZE_ONE_1024_STEP_CPU_SMOKE_ONLY",
        "hypothesis": (
            "A 250-tick deployable response calibration can condition a trainable "
            "recurrent adapter around the exact selected 512K actor, while the protected "
            "actor and its normalization remain bit-exact and graph-authoritative bounds "
            "remain the final action boundary."
        ),
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "repository_binaries": repository_binaries,
        "external_binaries": {
            "source_checkpoint": {
                "external_role": f"extracted archive member {SOURCE_MEMBER}",
                "hash_mode": "recursive-posix-relative-path-and-bytes",
                "sha256": SOURCE_CHECKPOINT_SHA256,
            },
            "calibrator_onnx": {
                "external_role": "Winner-v22 final normalized response encoder",
                "sha256": CALIBRATOR_SHA256,
            },
        },
        "composed_playground_files": composed_files,
        "composed_playground_manifest_sha256": sha256(manifest_path),
        "software_versions": software_versions,
        "frozen_contract": {
            "protected_policy_sha256": POLICY_SHA256,
            "calibrator_sha256": CALIBRATOR_SHA256,
            "policy_abi": {
                "inputs": {
                    "obs": [1, 115],
                    "previous_action": [1, 14],
                    "h_in": [1, 64],
                    "calibration_context": [1, 64],
                },
                "outputs": {
                    "continuous_actions": [1, 14],
                    "previous_action_out": [1, 14],
                    "h_out": [1, 64],
                },
            },
            "calibration_ticks": 250,
            "home_return_ticks": 250,
            "locomotion_phase_reset": [1.0, 0.0],
            "adapter_seed": 60721,
            "adapter_max_normalized": 0.25,
            "protected_actor_trainable": False,
            "protected_normalizer_trainable": False,
            "calibration_prefix_in_ppo_buffer": False,
            "calibration_context_policy_inputs": [
                "deployable obs[115]",
                "previous_action[14]",
                "recurrent hidden[64]",
            ],
            "true_mass_com_inertia_labels_available_to_policy": False,
            "flat_transport_feature_enabled": False,
        },
        "cpu_smoke": {
            "timesteps": 1024,
            "seed": 100,
            "num_envs": 4,
            "num_evals": 2,
            "episode_length": 600,
            "unroll_length": 8,
            "batch_size": 4,
            "num_minibatches": 1,
            "num_updates_per_batch": 2,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "winner_v3_deviation_scale": 0.25,
            "golden_ticks": 1200,
            "jax_onnx_initial_cases": 64,
            "jax_onnx_final_cases": 256,
        },
        "thresholds": {
            "zero_update_selected_and_golden_max_abs_at_most": 1.0e-6,
            "jax_onnx_action_and_hidden_max_abs_at_most": 1.0e-6,
            "graph_rate_excess_at_most": 1.0e-6,
            "protected_parameter_update_exactly": 0.0,
            "adapter_state_context_action_update_strictly_above": 0.0,
            "wall_seconds_at_most": 3600.0,
        },
        "pass_rule": [
            "all source, binary, environment, and composed-source hashes match",
            "the selected 512K source checkpoint restores on CPU and expands without changing any protected actor or protected-normalizer leaf",
            "the step-zero graph reproduces all 1,200 frozen x=0/x=.08 golden ticks within 1e-6 and retains exact x=0 zero action",
            "reset runs exactly 250 calibration ticks plus 250 home-return ticks outside PPO transitions, resets phase to [1,0], and produces one finite immutable 64-D context",
            "one 1,024-step CPU PPO smoke keeps every protected leaf exact while adapter state, context, and action families each update",
            "step-zero and step-1,024 ONNX graphs expose the exact stateful ABI, agree with JAX within 1e-6, remain rate-bounded, and preserve exact x=0 deadband",
        ],
        "future_hosted_curriculum_not_authorized_now": {
            "sequence": [
                {"deviation_scale": 0.25, "timesteps": 245760},
                {"deviation_scale": 0.5, "timesteps": 245760},
                {
                    "deviation_scale": 1.0,
                    "timesteps": 2007040,
                    "exports": [1003520, 2007040],
                },
            ],
            "ppo": {
                "seed": 100,
                "num_envs": 256,
                "episode_length": 600,
                "unroll_length": 20,
                "batch_size": 256,
                "num_minibatches": 4,
                "num_updates_per_batch": 4,
                "learning_rate": 0.0003,
                "discounting": 0.97,
                "entropy_cost": 0.005,
            },
            "advancement": (
                "requires a separate hash-frozen package/preregistration and the unchanged "
                "full variable-configuration behavior gate; no closest checkpoint"
            ),
        },
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "formal_cpu_smoke_authorized": True,
            "result_authorizes": (
                "only preparation of a separate hosted curriculum preregistration if all "
                "checks pass"
            ),
            "hosted_or_colab_training_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v98 response-conditioned training preregistration\n\n"
        "- Source actor: exact selected T2 512K graph `99d3afce...304de`\n"
        "- Calibration: 250 response ticks + 250 home-return ticks, outside PPO\n"
        "- Trainable policy family: recurrent response adapter only\n"
        "- Protected: actor weights and source observation normalization\n"
        "- CPU smoke: one 1,024-step run; full hosted curriculum is not yet authorized\n"
        "- Flat transport: disabled\n"
        "- Robot / RDK / motion access: `0 / 0 / 0`\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
