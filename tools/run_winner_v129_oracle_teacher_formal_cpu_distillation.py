#!/usr/bin/env python3
"""Run the single preregistered V129 formal CPU distillation."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

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
import optax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
    directory_sha256,
    inference_error,
    restore_like,
    sha256,
)
from validate_winner_v112_recovered_training import (  # noqa: E402
    tree_deltas,
    tree_finite,
)
import winner_v129_oracle_teacher_distillation as distill  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v129_oracle_teacher_formal_cpu_preregistration.json"
)
CPU_RESULT = ANALYSIS / "winner_v129_oracle_teacher_cpu_result.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
RESULT = ANALYSIS / "winner_v129_oracle_teacher_formal_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_RESULT_20260724.md"
)
EXPORT_UPDATES = (0, 19, 38)


def evaluate(
    network: Any,
    normalizer: Any,
    fixed_policy: Any,
    head: dict[str, jax.Array],
    dataset: dict[str, Any],
    transform: dict[str, Any],
) -> dict[str, float]:
    batch = {
        key: jnp.asarray(dataset[key])
        for key in (
            "obs",
            "previous_action",
            "h_in",
            "target_action",
            "target_h_out",
            "weights",
        )
    }
    total, (action_loss, hidden_loss) = distill.loss_components(
        network,
        normalizer,
        fixed_policy,
        head,
        batch,
        transform,
    )
    policy = distill.policy_with_head(fixed_policy, head)
    action, h_out = distill.deployed_actions(
        network,
        normalizer,
        policy,
        batch["obs"],
        batch["previous_action"],
        batch["h_in"],
        transform,
    )
    action_error = np.asarray(action) - dataset["target_action"]
    row_mse = np.mean(np.square(action_error), axis=-1)
    corrected = dataset["corrected"]
    hidden_error = np.asarray(h_out) - dataset["target_h_out"]
    return {
        "objective": float(total),
        "weighted_action_mse": float(action_loss),
        "hidden_mse": float(hidden_loss),
        "corrected_action_mse": float(np.mean(row_mse[corrected])),
        "preservation_action_mse": float(np.mean(row_mse[~corrected])),
        "action_linf": float(np.max(np.abs(action_error))),
        "hidden_linf": float(np.max(np.abs(hidden_error))),
    }


def save_checkpoint(path: Path, tree: Any) -> str:
    checkpointer = ocp.PyTreeCheckpointer()
    checkpointer.save(
        str(path),
        tree,
        save_args=orbax_utils.save_args_from_target(tree),
    )
    return directory_sha256(path)


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
            raise FileExistsError(f"refusing to overwrite formal V129: {path}")

    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    oracle_root = args.oracle_run_root.resolve()
    frozen_deployed = args.v121_final_deployed.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    observed_hashes = {
        "cpu_result": sha256(CPU_RESULT),
        "training_module": sha256(
            TRAINING / "winner_v129_oracle_teacher_distillation.py"
        ),
        "formal_runner": sha256(Path(__file__).resolve()),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": sha256(frozen_deployed),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V129_FORMAL_CPU_DISTILLATION"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or cpu_result.get("decision")
        != "EARN_ONE_V129_FORMAL_CPU_DISTILLATION_PREREGISTRATION"
    ):
        raise ValueError("formal V129 preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = distill.load_teacher_dataset(oracle_root)
    batches = distill.padded_epoch_batches(dataset)
    if len(batches) != 19:
        raise ValueError("formal V129 requires exactly 19 updates per epoch")

    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = running_statistics.RunningStatisticsState(**source_tree[0])
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
    optimizer_state = optimizer.init(initial_head)

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
        )

    work.mkdir(parents=True)
    head = initial_head
    snapshots = {0: initial_head}
    update_rows = []
    update_index = 0
    for epoch in range(1, 3):
        for batch_np in batches:
            update_index += 1
            batch = {
                key: jnp.asarray(value)
                for key, value in batch_np.items()
            }
            head, optimizer_state, loss, components = update(
                head, optimizer_state, batch
            )
            update_rows.append(
                {
                    "update": update_index,
                    "epoch": epoch,
                    "loss": float(loss),
                    "action_loss": float(components[0]),
                    "hidden_loss": float(components[1]),
                }
            )
        snapshots[update_index] = head
    if tuple(sorted(snapshots)) != EXPORT_UPDATES:
        raise ValueError("formal V129 export updates changed")

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
    exports = {}
    metrics = {}
    changed_leaves = {}
    checkpoint_hashes = {}
    expected_changed = {
        "1/params/adapter_location/bias",
        "1/params/adapter_location/kernel",
    }
    for value in EXPORT_UPDATES:
        snapshot_head = snapshots[value]
        policy = distill.policy_with_head(fixed_policy, snapshot_head)
        tree = [normalizer, policy, source_tree[2]]
        checkpoint_path = work / f"checkpoint_{value}"
        checkpoint_hashes[value] = save_checkpoint(checkpoint_path, tree)
        structure, deltas = tree_deltas(source_tree, tree)
        if not structure:
            raise ValueError("formal V129 checkpoint structure changed")
        changed_leaves[value] = sorted(
            name for name, delta in deltas.items() if delta > 0.0
        )
        raw_path = work / f"winner_v129_raw_{value}.onnx"
        deployed_path = work / f"winner_v129_deployed_{value}.onnx"
        export_reference_residual_recurrent_adapter_onnx(
            tree,
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
        metrics[value] = evaluate(
            network,
            normalizer,
            fixed_policy,
            snapshot_head,
            dataset,
            transform,
        )

    step_zero_error = inference_error(
        Path(exports[0]["deployed"]["path"]), frozen_deployed
    )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "dataset_exact": (
            dataset["obs"].shape == (4_800, 115)
            and int(np.sum(dataset["corrected"])) == 14
            and dataset["updates_per_epoch"] == 19
        ),
        "exactly_38_updates": update_index == 38,
        "export_updates_exact": tuple(sorted(exports)) == EXPORT_UPDATES,
        "step_zero_matches_v121_final": step_zero_error <= 1.0e-7,
        "half_objective_below_step_zero": (
            metrics[19]["objective"] < metrics[0]["objective"]
        ),
        "final_objective_below_step_zero": (
            metrics[38]["objective"] < metrics[0]["objective"]
        ),
        "half_corrected_loss_below_step_zero": (
            metrics[19]["corrected_action_mse"]
            < metrics[0]["corrected_action_mse"]
        ),
        "final_corrected_loss_below_step_zero": (
            metrics[38]["corrected_action_mse"]
            < metrics[0]["corrected_action_mse"]
        ),
        "only_adapter_head_changed_half": (
            set(changed_leaves[19]) == expected_changed
        ),
        "only_adapter_head_changed_final": (
            set(changed_leaves[38]) == expected_changed
        ),
        "step_zero_unchanged": changed_leaves[0] == [],
        "all_checkpoint_trees_finite": all(
            tree_finite(
                [
                    normalizer,
                    distill.policy_with_head(fixed_policy, snapshots[value]),
                    source_tree[2],
                ]
            )
            for value in EXPORT_UPDATES
        ),
        "all_export_abis_exact": all(
            row["deployed"]["graph_io"] == expected_io
            for row in exports.values()
        ),
        "all_export_inference_contracts_pass": all(
            row["deployed"]["inference"]["pass"]
            for row in exports.values()
        ),
        "all_metrics_finite": all(
            math.isfinite(metric)
            for row in metrics.values()
            for metric in row.values()
        ),
        "no_hosted_compute": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v129.oracle_teacher_formal_cpu_result.v1",
        "status": (
            "PASS_WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_DISTILLATION"
            if not failed
            else "HOLD_WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_DISTILLATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "rows": 4_800,
            "corrected_rows": 14,
            "preservation_rows": 4_786,
            "correction_weight": dataset["correction_weight"],
            "batch_size": distill.BATCH_SIZE,
            "updates_per_epoch": dataset["updates_per_epoch"],
            "epochs": 2,
            "trace_manifest": dataset["manifest"],
        },
        "training": {
            "optimizer": "Adam",
            "learning_rate": 0.0003,
            "updates": update_index,
            "rows": update_rows,
            "metrics": {
                str(value): metrics[value] for value in EXPORT_UPDATES
            },
            "changed_leaves": {
                str(value): changed_leaves[value]
                for value in EXPORT_UPDATES
            },
        },
        "checkpoints": {
            str(value): {
                "path": str(work / f"checkpoint_{value}"),
                "directory_sha256": checkpoint_hashes[value],
            }
            for value in EXPORT_UPDATES
        },
        "exports": {
            str(value): exports[value] for value in EXPORT_UPDATES
        },
        "step_zero_v121_final_max_abs_error": step_zero_error,
        "decision": (
            "EARN_ONE_V129_NOMINAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_V129_DISTILLATION_WITHOUT_BEHAVIOR"
        ),
        "authority": {
            "nominal_behavior_preregistration": not failed,
            "nominal_behavior_evaluation": False,
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
        "# Winner V129 formal CPU distillation\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Updates: `{update_index}` (half 19, final 38).\n"
        f"- Objective 0/19/38: `{metrics[0]['objective']}` / "
        f"`{metrics[19]['objective']}` / `{metrics[38]['objective']}`.\n"
        f"- Decision: `{payload['decision']}`\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
