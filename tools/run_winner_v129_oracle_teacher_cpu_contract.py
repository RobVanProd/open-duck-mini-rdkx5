#!/usr/bin/env python3
"""Run the preregistered V129 oracle-teacher CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from brax.training.acme import running_statistics
from flax.training import orbax_utils
import jax
import jax.numpy as jnp
import numpy as np
import onnx
import onnxruntime as ort
import optax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from build_ground_up_actual_centered_guard_screen import (  # noqa: E402
    append_guard,
)
from build_ground_up_command_deadband_repair import (  # noqa: E402
    wrap as append_deadband,
)
from build_winner_v113_postexport_policies import (  # noqa: E402
    graph_io,
    sha256,
)
from build_winner_v117_postguard_rate_projection_policies import (  # noqa: E402
    append_projection,
    inference_contract,
)
from validate_winner_v112_recovered_training import (  # noqa: E402
    tree_deltas,
)
import winner_v129_oracle_teacher_distillation as distill  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v129_oracle_teacher_cpu_preregistration_v3.json"
)
RESULT = ANALYSIS / "winner_v129_oracle_teacher_cpu_result.json"
MARKDOWN = ANALYSIS / "WINNER_V129_ORACLE_TEACHER_CPU_RESULT_20260724.md"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    return checkpointer.restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def deploy_graph(
    raw_path: Path,
    output_path: Path,
    transform: dict,
) -> dict:
    source = onnx.load(raw_path)
    home = np.asarray(transform["home_target_rad"], dtype=np.float32)
    obs_indices = np.asarray(
        transform["measured_joint_offset_indices"], dtype=np.int64
    )
    pitch_indices = np.asarray(
        transform["pitch_chain_action_indices"], dtype=np.int64
    )
    delta = np.asarray(
        transform["exact_train_normalized_action_delta"],
        dtype=np.float32,
    )
    command_index = int(transform["command_x_observation_index"])
    deadband = float(transform["zero_deadband_absolute_command_x"])
    action_scale = float(transform["action_scale_rad"])
    margin = float(transform["g3_margin_rad"])
    guarded = append_guard(
        source,
        obs_indices=obs_indices,
        pitch_indices=pitch_indices,
        home=home,
        action_scale=action_scale,
        margin=margin,
    )
    deadbanded = append_deadband(
        guarded,
        command_index=command_index,
        deadband=deadband,
    )
    final = append_projection(
        deadbanded,
        selected_delta=delta,
        command_index=command_index,
        deadband=deadband,
    )
    onnx.checker.check_model(final)
    onnx.save(final, output_path)
    contract = inference_contract(
        raw_path,
        output_path,
        selected_delta=delta,
        changed_indices=pitch_indices,
        command_index=command_index,
        deadband=deadband,
        home=home,
        pitch_indices=pitch_indices,
        actual_obs_indices=obs_indices,
        action_scale=action_scale,
        guard_margin=margin,
    )
    return {
        "path": str(output_path),
        "sha256": sha256(output_path),
        "bytes": output_path.stat().st_size,
        "graph_io": graph_io(final),
        "inference": contract,
    }


def inference_error(left_path: Path, right_path: Path) -> float:
    left = ort.InferenceSession(
        left_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    right = ort.InferenceSession(
        right_path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260724)
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden_left = np.zeros((1, 64), dtype=np.float32)
    hidden_right = np.zeros((1, 64), dtype=np.float32)
    maximum = 0.0
    for _ in range(32):
        obs = rng.normal(size=(1, 115)).astype(np.float32)
        obs[:, 6] = np.float32(0.077)
        feeds_left = {
            "obs": obs,
            "previous_action": previous,
            "h_in": hidden_left,
        }
        feeds_right = {
            "obs": obs,
            "previous_action": previous,
            "h_in": hidden_right,
        }
        action_left, previous_left, hidden_left = left.run(
            None, feeds_left
        )
        action_right, previous_right, hidden_right = right.run(
            None, feeds_right
        )
        maximum = max(
            maximum,
            float(np.max(np.abs(action_left - action_right))),
            float(np.max(np.abs(previous_left - previous_right))),
            float(np.max(np.abs(hidden_left - hidden_right))),
        )
        previous = action_left
    return maximum


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--oracle-run-root", type=Path, required=True)
    parser.add_argument("--v121-final-deployed", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V129: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    oracle_root = args.oracle_run_root.resolve()
    frozen_deployed = args.v121_final_deployed.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "dataset_audit": sha256(
            ANALYSIS / "winner_v129_oracle_teacher_dataset_audit.json"
        ),
        "v128_attribution": sha256(
            ANALYSIS / "winner_v128_nominal_failure_attribution.json"
        ),
        "v121_transform": sha256(V121_TRANSFORM),
        "training_module": sha256(
            TRAINING / "winner_v129_oracle_teacher_distillation.py"
        ),
        "runner": sha256(Path(__file__).resolve()),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": sha256(frozen_deployed),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or observed_hashes != prereg.get("input_hashes")
    ):
        raise ValueError("V129 CPU preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = distill.load_teacher_dataset(oracle_root)
    corrected_indices = np.flatnonzero(dataset["corrected"])
    preservation_indices = np.flatnonzero(~dataset["corrected"])[:242]
    smoke_indices = np.concatenate(
        [corrected_indices, preservation_indices]
    )
    if smoke_indices.shape != (256,):
        raise ValueError("V129 smoke batch must be 14+242 rows")
    smoke_batch_np = {
        key: np.asarray(dataset[key][smoke_indices])
        for key in (
            "obs",
            "previous_action",
            "h_in",
            "target_action",
            "target_h_out",
            "weights",
        )
    }
    smoke_batch = {
        key: jnp.asarray(value) for key, value in smoke_batch_np.items()
    }

    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = running_statistics.RunningStatisticsState(
        **source_tree[0]
    )
    source_tree = [normalizer, source_tree[1], source_tree[2]]
    fixed_policy = source_tree[1]
    initial_head = distill.head_from_policy(fixed_policy)
    network = make_reference_residual_recurrent_adapter_ppo_networks(
        {
            "state": (115,),
            "privileged_state": (226,),
            "policy_hidden": (64,),
        },
        14,
        preprocess_observations_fn=running_statistics.normalize,
        policy_hidden_layer_sizes=(512, 256, 128),
        value_hidden_layer_sizes=(512, 256, 128),
        recurrent_hidden_size=64,
    )
    optimizer = optax.adam(0.0003)
    opt_state = optimizer.init(initial_head)

    def objective(head, batch):
        return distill.loss_components(
            network,
            normalizer,
            fixed_policy,
            head,
            batch,
            transform,
        )

    @jax.jit
    def update(head, state, batch):
        (loss, components), grads = jax.value_and_grad(
            objective, has_aux=True
        )(head, batch)
        updates, state = optimizer.update(grads, state, head)
        return (
            optax.apply_updates(head, updates),
            state,
            loss,
            components,
            grads,
        )

    initial_loss, initial_components = objective(
        initial_head, smoke_batch
    )
    head = initial_head
    step_rows = []
    final_grads = None
    for update_index in range(1, 3):
        head, opt_state, loss, components, final_grads = update(
            head, opt_state, smoke_batch
        )
        step_rows.append(
            {
                "update": update_index,
                "loss": float(loss),
                "action_loss": float(components[0]),
                "hidden_loss": float(components[1]),
            }
        )
    final_loss, final_components = objective(head, smoke_batch)
    updated_policy = distill.policy_with_head(fixed_policy, head)
    updated_tree = [normalizer, updated_policy, source_tree[2]]
    structure, deltas = tree_deltas(source_tree, updated_tree)
    changed = {name for name, value in deltas.items() if value > 0.0}
    expected_changed = {
        "1/params/adapter_location/bias",
        "1/params/adapter_location/kernel",
    }
    gradient_norms = {
        key: float(np.linalg.norm(np.asarray(value)))
        for key, value in final_grads.items()
    }

    work.mkdir(parents=True)
    exports = {}
    for value, params in ((0, source_tree), (2, updated_tree)):
        raw_path = work / f"winner_v129_raw_{value}.onnx"
        deployed_path = work / f"winner_v129_deployed_{value}.onnx"
        export_reference_residual_recurrent_adapter_onnx(
            params,
            action_size=14,
            obs_size=115,
            hidden_size=64,
            output_path=raw_path,
            hidden_layer_sizes=(512, 256, 128),
            action_velocity_limits_rad_s=transform[
                "exact_train_effective_rate_rad_s"
            ],
            control_dt=float(transform["control_dt_s"]),
            action_scale=float(transform["action_scale_rad"]),
        )
        exports[value] = {
            "raw_path": str(raw_path),
            "raw_sha256": sha256(raw_path),
            "deployed": deploy_graph(
                raw_path, deployed_path, transform
            ),
        }
    step_zero_error = inference_error(
        Path(exports[0]["deployed"]["path"]), frozen_deployed
    )
    expected_io = {
        "inputs": {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "dataset_exact_4800_rows": (
            dataset["obs"].shape == (4_800, 115)
            and int(np.sum(dataset["corrected"])) == 14
            and dataset["updates_per_epoch"] == 19
        ),
        "correction_weight_is_class_balance_derived": math.isclose(
            dataset["correction_weight"],
            4_786 / 14,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "smoke_batch_has_all_corrections_and_242_preservation_rows": (
            int(np.sum(dataset["corrected"][smoke_indices])) == 14
            and len(smoke_indices) == 256
        ),
        "initial_action_loss_nonzero": float(initial_components[0]) > 0.0,
        "initial_hidden_loss_zero_at_teacher_restore": (
            float(initial_components[1]) <= 1.0e-12
        ),
        "two_updates_reduce_total_loss": (
            float(final_loss) < float(initial_loss)
        ),
        "two_updates_reduce_action_loss": (
            float(final_components[0]) < float(initial_components[0])
        ),
        "hidden_loss_remains_zero": (
            float(final_components[1]) <= 1.0e-12
        ),
        "both_adapter_head_gradients_nonzero": all(
            value > 0.0 for value in gradient_norms.values()
        ),
        "checkpoint_structure_exact": structure,
        "only_adapter_location_head_changed": changed == expected_changed,
        "step_zero_matches_v121_final_deployment": step_zero_error <= 1.0e-7,
        "both_export_abis_exact": all(
            row["deployed"]["graph_io"] == expected_io
            for row in exports.values()
        ),
        "both_export_inference_contracts_pass": all(
            row["deployed"]["inference"]["pass"]
            for row in exports.values()
        ),
        "all_scalars_finite": all(
            math.isfinite(value)
            for value in (
                float(initial_loss),
                float(initial_components[0]),
                float(initial_components[1]),
                float(final_loss),
                float(final_components[0]),
                float(final_components[1]),
                *gradient_norms.values(),
            )
        ),
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v129.oracle_teacher_cpu_result.v1",
        "status": (
            "PASS_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "rows": 4_800,
            "corrected_rows": 14,
            "preservation_rows": 4_786,
            "correction_weight": dataset["correction_weight"],
            "updates_per_epoch": dataset["updates_per_epoch"],
            "trace_manifest": dataset["manifest"],
        },
        "smoke": {
            "updates": 2,
            "learning_rate": 0.0003,
            "initial_loss": float(initial_loss),
            "initial_action_loss": float(initial_components[0]),
            "initial_hidden_loss": float(initial_components[1]),
            "rows": step_rows,
            "final_loss": float(final_loss),
            "final_action_loss": float(final_components[0]),
            "final_hidden_loss": float(final_components[1]),
            "gradient_norms": gradient_norms,
            "changed_leaves": sorted(changed),
        },
        "exports": {str(key): value for key, value in exports.items()},
        "step_zero_v121_final_max_abs_error": step_zero_error,
        "decision": (
            "EARN_ONE_V129_FORMAL_CPU_DISTILLATION_PREREGISTRATION"
            if not failed
            else "NO_DISTILLATION_RUN"
        ),
        "authority": {
            "formal_cpu_distillation_preregistration": not failed,
            "formal_distillation_training": False,
            "hosted_training": False,
            "behavior_evaluation": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V129 oracle-teacher CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Initial/final action loss: "
        f"`{payload['smoke']['initial_action_loss']}` / "
        f"`{payload['smoke']['final_action_loss']}`\n"
        f"- Changed leaves: `{payload['smoke']['changed_leaves']}`\n"
        f"- Step-0 deployment error: `{step_zero_error}`\n"
        f"- Decision: `{payload['decision']}`\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
