#!/usr/bin/env python3
"""Run the frozen zero-update Winner-v56 first-tick gradient proof on CPU."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

CONTRACT = ANALYSIS / "winner_v56_first_tick_teacher_gradient_contract.json"
V52_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v56.first_tick_teacher_gradient_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_FIRST_TICK_GRADIENT_PROOF_ONLY"
        or value.get("objective", {}).get("total_rows") != 44
        or value.get("objective", {}).get("selected_elements") != 616
        or value.get("objective", {}).get("scale") != 136.35153198242188
        or value.get("execution_now", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v56 contract identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v56 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v56 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v56 source manifest changed")


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--gradient-proof-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.gradient_proof_authorized:
        raise PermissionError(
            "Winner-v56 requires --offline-cpu-only --gradient-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v56 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v56 summary: {markdown}")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnxruntime as ort
    import run_winner_v54_residual_teacher_causal as v54
    import winner_v43_static_target_teacher as v43
    import winner_v56_first_tick_teacher_mapping as v56

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v56 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v52 = json.loads(V52_RESULT.read_text(encoding="utf-8"))
    if sha256(V52_RESULT) != contract["source_checkpoint"]["v52_result_sha256"]:
        raise ValueError("Winner-v56 V52 source changed")
    smoke, gate, v53 = v54.configure_v53_modules()
    calibrator_design = gate.load_calibrator_design(
        json.loads(FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8"))
    )
    matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    objective = contract["objective"]
    if set(objective["configuration_ids"]) - set(by_id):
        raise ValueError("Winner-v56 training configurations changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v56 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v56 canonical fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    checkpoint_path, graph_path = v53.checkpoint_paths(args.training_work_root, "final")
    if (
        sha256(checkpoint_path) != contract["source_checkpoint"]["snapshot_sha256"]
        or sha256(graph_path) != contract["source_checkpoint"]["onnx_sha256"]
    ):
        raise ValueError("Winner-v56 final artifacts changed")
    snapshot = v53.load_snapshot_for_reviewed_gate(checkpoint_path)
    v53.validate_snapshot_for_reviewed_gate(snapshot)

    observations = []
    targets = []
    variants = []
    identifiers = []
    for configuration_id in objective["configuration_ids"]:
        raw_teacher = np.asarray(table[configuration_id], dtype=np.float32)
        target = smoke.bounded_action_numpy(
            raw_teacher, np.zeros((14,), dtype=np.float32)
        )
        for plant in objective["plants"]:
            episode = smoke.Episode(
                mujoco,
                scene,
                by_id[configuration_id],
                plant,
                calibrator_design,
                observer_type,
                args.canonical_fit,
            )
            raw = gate.ObservationTransport(None, None).observe(episode.observation())
            quantized = gate.native_quantize_observation(raw)
            for variant, observation in enumerate((raw, quantized)):
                observations.append(observation)
                targets.append(target)
                variants.append(variant)
                identifiers.append(
                    {
                        "configuration_id": configuration_id,
                        "plant": plant,
                        "variant": "raw" if variant == 0 else "native_quantized",
                    }
                )
    batch_np = {
        "observations": np.asarray(observations, dtype=np.float32),
        "targets": np.asarray(targets, dtype=np.float32),
        "variant": np.asarray(variants, dtype=np.int32),
    }
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    parameters = {key: jnp.asarray(value) for key, value in snapshot["parameters"].items()}

    def objective_fn(values: Mapping[str, Any]):
        return v56.first_tick_teacher_loss(values, batch)

    (loss, metrics), gradients = jax.value_and_grad(
        objective_fn, has_aux=True
    )(parameters)
    scaled_gradients = jax.tree_util.tree_map(
        lambda value: jnp.asarray(v56.RESET_TEACHER_SCALE) * value, gradients
    )
    gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in sorted(scaled_gradients.items())
    }
    nonzero = sorted(key for key, value in gradient_max.items() if value > 0.0)
    zero = sorted(key for key, value in gradient_max.items() if value == 0.0)
    jax_actions = np.asarray(
        v56.first_tick_actions(parameters, batch["observations"]), dtype=np.float32
    )
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    onnx_actions = []
    for observation in batch_np["observations"]:
        onnx_actions.append(
            session.run(
                ["calibration_actions"],
                {
                    "obs": observation[None, :],
                    "previous_action": np.zeros((1, 14), dtype=np.float32),
                    "h_in": np.zeros((1, 64), dtype=np.float32),
                },
            )[0][0]
        )
    onnx_actions_np = np.asarray(onnx_actions, dtype=np.float32)
    maximum_jax_onnx = float(np.max(np.abs(jax_actions - onnx_actions_np)))
    baseline = jnp.asarray(np.float32(7.125))
    disabled = v56.combine_objective(baseline, loss, enabled=False)
    disabled_gradients = jax.grad(
        lambda values: v56.combine_objective(
            jnp.asarray(np.float32(7.125)),
            v56.first_tick_teacher_loss(values, batch)[0],
            enabled=False,
        )
    )(parameters)
    disabled_zero = all(
        np.array_equal(np.asarray(value), np.zeros_like(np.asarray(value)))
        for value in disabled_gradients.values()
    )
    expected_nonzero = sorted(contract["gradient_contract"]["expected_nonzero_leaves"])
    expected_zero = sorted(contract["gradient_contract"]["expected_zero_leaves"])
    heldout = set(objective["heldout_configuration_ids_forbidden"])
    checks = {
        "source_snapshot_and_onnx_exact": True,
        "exact_44_rows_616_elements": batch_np["observations"].shape == (44, 115)
        and batch_np["targets"].shape == (44, 14)
        and int(np.asarray(metrics["selected_elements"])) == 616,
        "heldout_labels_absent": not any(
            row["configuration_id"] in heldout for row in identifiers
        ),
        "raw_and_quantized_inputs_distinct_per_configuration": all(
            not np.array_equal(batch_np["observations"][index], batch_np["observations"][index + 1])
            for index in range(0, 44, 2)
        ),
        "jax_onnx_actions_at_most_1e_7": maximum_jax_onnx <= 1.0e-7,
        "targets_obey_graph_boundary": all(
            np.array_equal(
                target,
                smoke.bounded_action_numpy(target, np.zeros((14,), dtype=np.float32)),
            )
            for target in batch_np["targets"]
        ),
        "gradient_leaf_locality_exact": nonzero == expected_nonzero and zero == expected_zero,
        "scaled_loss_and_gradients_finite_nonzero": math.isfinite(float(loss))
        and float(loss) > 0.0
        and finite_tree(scaled_gradients)
        and any(value > 0.0 for value in gradient_max.values()),
        "default_off_exact": np.array_equal(np.asarray(disabled), np.asarray(baseline))
        and disabled_zero,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "winner_v56.first_tick_teacher_gradient_result.v1",
        "status": (
            "PASS_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT"
            if not failed_checks
            else "HOLD_WINNER_V56_FIRST_TICK_TEACHER_GRADIENT_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_ONE_FIRST_TICK_TEACHER_ADAM_UPDATE_PREREGISTRATION_ONLY"
            if not failed_checks
            else "DO_NOT_RUN_FIRST_TICK_TEACHER_UPDATE"
        ),
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "snapshot_sha256": sha256(checkpoint_path),
            "onnx_sha256": sha256(graph_path),
        },
        "objective": {
            "identifiers": identifiers,
            "rows": 44,
            "selected_elements": 616,
            "scale": float(v56.RESET_TEACHER_SCALE),
            "loss": float(loss),
            "scaled_loss": float(np.float32(v56.RESET_TEACHER_SCALE) * np.float32(loss)),
            "metrics": {key: float(np.asarray(value)) for key, value in metrics.items()},
            "maximum_jax_onnx_action_error": maximum_jax_onnx,
            "scaled_gradient_max_abs": gradient_max,
            "nonzero_gradient_leaves": nonzero,
            "zero_gradient_leaves": zero,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "reset_rows": 44,
            "simulator_steps": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "exports": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": "one separate CPU Adam-update proof preregistration only",
        },
    }
    if not finite_tree(result):
        raise FloatingPointError("Winner-v56 result contains nonfinite values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v56 first-tick teacher gradient result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Loss / scaled loss: `{float(loss)} / {result['objective']['scaled_loss']}`",
                f"- Pitch / non-pitch RMS: `{float(metrics['pitch_rms'])} / {float(metrics['nonpitch_rms'])}`",
                f"- JAX/ONNX maximum action error: `{maximum_jax_onnx}`",
                f"- Nonzero gradient leaves: `{json.dumps(nonzero)}`",
                "- Simulator steps / optimizer / export / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
