#!/usr/bin/env python3
"""Run the preregistered V145 on-policy DAgger CPU contract."""

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
import jax
import jax.numpy as jnp
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from build_winner_v113_postexport_policies import sha256  # noqa: E402
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
    directory_sha256,
    inference_error,
    restore_like,
)
from run_winner_v134_full_actor_teacher_cpu_contract import (  # noqa: E402
    action_metrics,
    leaf_norms,
)
from validate_winner_v112_recovered_training import tree_deltas  # noqa: E402
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v145_on_policy_dagger_cpu_preregistration.json"
RESULT = ANALYSIS / "winner_v145_on_policy_dagger_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V145_ON_POLICY_DAGGER_CPU_RESULT_20260725.md"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate_policy(
    network,
    normalizer,
    policy,
    data: dict,
    transform: dict,
) -> tuple[np.ndarray, np.ndarray]:
    action, hidden = dagger.deployed_actions(
        network,
        normalizer,
        policy,
        jnp.asarray(data["obs"]),
        jnp.asarray(data["previous_action"]),
        jnp.asarray(data["h_in"]),
        transform,
    )
    return np.asarray(action), np.asarray(hidden)


def run_two_updates(
    *,
    network,
    normalizer,
    initial_policy,
    batch: dict,
    transform: dict,
) -> tuple[object, list[dict], list[dict[str, float]], tuple]:
    def objective(policy):
        return dagger.loss_components(
            network, normalizer, policy, batch, transform
        )

    value_and_grad = jax.jit(jax.value_and_grad(objective, has_aux=True))
    evaluate = jax.jit(objective)
    policy = initial_policy
    updates = []
    gradient_rows = []
    for update_index in range(1, 3):
        (loss, components), raw_grads = value_and_grad(policy)
        grads = dagger.freeze_scale_gradients(raw_grads)
        norm = float(dagger.gradient_norm(grads))
        slope = norm * norm
        initial_step = 1.0 / max(1.0, norm)
        accepted = None
        for backtrack in range(dagger.STD_BACKTRACK_LIMIT + 1):
            step = initial_step * (0.5**backtrack)
            candidate = dagger.apply_gradient(policy, grads, step)
            candidate_loss, candidate_components = evaluate(candidate)
            if float(candidate_loss) <= (
                float(loss) - dagger.ARMIJO_FRACTION * step * slope
            ):
                accepted = (
                    candidate,
                    step,
                    backtrack,
                    candidate_loss,
                    candidate_components,
                )
                break
        if accepted is None:
            raise RuntimeError("V145 deterministic line search failed")
        (
            policy,
            step,
            backtrack,
            candidate_loss,
            candidate_components,
        ) = accepted
        gradient_rows.append(leaf_norms(grads))
        updates.append(
            {
                "update": update_index,
                "loss_before": float(loss),
                "action_loss_before": float(components[0]),
                "hidden_loss_before": float(components[1]),
                "loss_after": float(candidate_loss),
                "action_loss_after": float(candidate_components[0]),
                "hidden_loss_after": float(candidate_components[1]),
                "gradient_norm": norm,
                "initial_step": initial_step,
                "accepted_step": step,
                "backtracks": backtrack,
            }
        )
    return policy, updates, gradient_rows, evaluate(policy)


def subset_metrics(
    action: np.ndarray,
    dataset: dict,
    selection: np.ndarray,
) -> dict:
    return action_metrics(
        action[selection],
        dataset["target_action"][selection],
        dataset["base_action"][selection],
        dataset["corrected"][selection],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--shadow-trace", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V145: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    teacher_root = args.teacher_run_root.resolve()
    shadow_trace = args.shadow_trace.resolve()
    work = args.work_root.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    selected_deployed = Path(
        v140["artifacts"]["selected_deployed"]["path"]
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "v131_result": file_sha256(V131_RESULT),
        "v140_result": file_sha256(V140_RESULT),
        "v144_correction": file_sha256(V144_CORRECTION),
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v134_training_module": file_sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "training_module": file_sha256(
            TRAINING / "winner_v145_on_policy_dagger.py"
        ),
        "runner": file_sha256(Path(__file__).resolve()),
        "network_source": file_sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "teacher_result": file_sha256(V131_RESULT),
        "shadow_trace": file_sha256(shadow_trace),
        "v140_selected_deployed": file_sha256(selected_deployed),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V145_ON_POLICY_DAGGER_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V145 CPU preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    template = ocp.PyTreeCheckpointer().restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = running_statistics.RunningStatisticsState(
        **source_tree[0]
    )
    source_tree = [normalizer, source_tree[1], source_tree[2]]
    source_policy = source_tree[1]
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

    teacher_source = v134.load_teacher_dataset(teacher_root)
    v134_indices = v134.smoke_indices(teacher_source)
    v134_batch = {
        key: jnp.asarray(teacher_source[key][v134_indices])
        for key in (
            "obs",
            "previous_action",
            "h_in",
            "target_action",
            "target_h_out",
            "weights",
        )
    }
    v134_policy, v134_updates, _, _ = run_two_updates(
        network=network,
        normalizer=normalizer,
        initial_policy=source_policy,
        batch=v134_batch,
        transform=transform,
    )
    alpha = float(v140["summary"]["selected_alpha"])
    v140_policy = dagger.interpolate_policy(
        source_policy, v134_policy, alpha
    )
    shadow_source = dagger.load_shadow_dataset(shadow_trace)
    teacher_base_action, teacher_base_hidden = evaluate_policy(
        network, normalizer, v140_policy, teacher_source, transform
    )
    shadow_base_action, shadow_base_hidden = evaluate_policy(
        network, normalizer, v140_policy, shadow_source, transform
    )
    dataset = dagger.build_aggregated_dataset(
        teacher_root=teacher_root,
        shadow_trace=shadow_trace,
        teacher_baseline_action=teacher_base_action,
        teacher_baseline_hidden=teacher_base_hidden,
        shadow_baseline_action=shadow_base_action,
        shadow_baseline_hidden=shadow_base_hidden,
    )
    full_batch = {
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
    updated_policy, updates, gradient_rows, final_loss = run_two_updates(
        network=network,
        normalizer=normalizer,
        initial_policy=v140_policy,
        batch=full_batch,
        transform=transform,
    )
    final_action, final_hidden = evaluate_policy(
        network, normalizer, updated_policy, dataset, transform
    )
    metrics = action_metrics(
        final_action,
        dataset["target_action"],
        dataset["base_action"],
        dataset["corrected"],
    )
    teacher_selection = dataset["source"] == "teacher"
    shadow_selection = dataset["source"] == "shadow"
    teacher_metrics = subset_metrics(
        final_action, dataset, teacher_selection
    )
    shadow_metrics = subset_metrics(
        final_action, dataset, shadow_selection
    )
    initial_shadow_action_error = float(
        np.max(
            np.abs(
                shadow_base_action
                - dataset["shadow_recorded_base_action"]
            )
        )
    )
    initial_shadow_hidden_error = float(
        np.max(
            np.abs(
                shadow_base_hidden - dataset["shadow_recorded_h_out"]
            )
        )
    )
    hidden_mse = float(
        np.mean(np.square(final_hidden - dataset["target_h_out"]))
    )
    v140_tree = [normalizer, v140_policy, source_tree[2]]
    updated_tree = [normalizer, updated_policy, source_tree[2]]
    structure, deltas = tree_deltas(v140_tree, updated_tree)
    changed = {name for name, value in deltas.items() if value > 0.0}
    scale_paths = {
        "1/params/scale_logits/bias",
        "1/params/scale_logits/kernel",
    }
    actor_paths = {
        name for name in deltas if name.startswith("1/params/")
    }
    expected_changed = actor_paths - scale_paths

    work.mkdir(parents=True)
    exports = {}
    for value, params in ((0, v140_tree), (2, updated_tree)):
        raw_path = work / f"winner_v145_raw_{value}.onnx"
        deployed_path = work / f"winner_v145_deployed_{value}.onnx"
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
            "deployed": deploy_graph(raw_path, deployed_path, transform),
        }
    step_zero_error = inference_error(
        Path(exports[0]["deployed"]["path"]), selected_deployed
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
        "v134_reconstruction_two_updates_exact": (
            len(v134_updates) == 2
        ),
        "v140_jax_reconstruction_matches_selected_deployment": (
            step_zero_error <= 1.0e-7
        ),
        "dataset_exact_5400_rows": dataset["obs"].shape == (5_400, 115),
        "teacher_17_and_shadow_4_corrected_rows": (
            int(np.sum(dataset["corrected"][teacher_selection])) == 17
            and int(np.sum(dataset["corrected"][shadow_selection])) == 4
        ),
        "exact_60_joint_labels": int(np.sum(dataset["joint_mask"])) == 60,
        "correction_weight_derived": math.isclose(
            dataset["correction_weight"],
            5_379 / 21,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "nonprojected_joint_targets_preserve_v140_exact": bool(
            np.array_equal(
                dataset["target_action"][~dataset["joint_mask"]],
                dataset["base_action"][~dataset["joint_mask"]],
            )
        ),
        "shadow_trace_actions_reproduced": (
            initial_shadow_action_error <= 1.0e-6
        ),
        "shadow_trace_hidden_reproduced": (
            initial_shadow_hidden_error <= 1.0e-6
        ),
        "both_dagger_updates_accepted": len(updates) == 2,
        "loss_decreases": (
            float(final_loss[0]) < updates[0]["loss_before"]
            and float(final_loss[1][0]) < updates[0]["action_loss_before"]
        ),
        "all_correction_ratio_at_most_point95": (
            metrics["corrected_ratio_to_zero_predictor"] <= 0.95
        ),
        "all_preservation_ratio_at_most_point01": (
            metrics["preservation_ratio_to_corrected_baseline"] <= 0.01
        ),
        "teacher_correction_ratio_at_most_point95": (
            teacher_metrics["corrected_ratio_to_zero_predictor"] <= 0.95
        ),
        "teacher_preservation_ratio_at_most_point01": (
            teacher_metrics["preservation_ratio_to_corrected_baseline"]
            <= 0.01
        ),
        "shadow_correction_ratio_at_most_point95": (
            shadow_metrics["corrected_ratio_to_zero_predictor"] <= 0.95
        ),
        "shadow_preservation_ratio_at_most_point01": (
            shadow_metrics["preservation_ratio_to_corrected_baseline"]
            <= 0.01
        ),
        "hidden_error_bounded": (
            hidden_mse <= metrics["baseline_corrected_mse"] * 0.01
        ),
        "checkpoint_structure_exact": structure,
        "all_non_scale_actor_leaves_changed": changed == expected_changed,
        "scale_logits_frozen": not bool(changed & scale_paths),
        "last_gradients_finite": all(
            math.isfinite(value)
            for value in gradient_rows[-1].values()
        ),
        "both_export_abis_exact": all(
            row["deployed"]["graph_io"] == expected_io
            for row in exports.values()
        ),
        "both_export_inference_contracts_pass": all(
            row["deployed"]["inference"]["pass"]
            for row in exports.values()
        ),
        "behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v145.on_policy_dagger_cpu_result.v1",
        "status": (
            "PASS_WINNER_V145_ON_POLICY_DAGGER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V145_ON_POLICY_DAGGER_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "reconstruction": {
            "v134_updates": v134_updates,
            "v140_alpha": alpha,
            "step_zero_deployed_linf": step_zero_error,
            "shadow_action_linf": initial_shadow_action_error,
            "shadow_hidden_linf": initial_shadow_hidden_error,
        },
        "dataset": {
            "rows": 5_400,
            "teacher_rows": 4_800,
            "shadow_rows": 600,
            "teacher_corrected_rows": int(
                np.sum(dataset["corrected"][teacher_selection])
            ),
            "shadow_corrected_rows": int(
                np.sum(dataset["corrected"][shadow_selection])
            ),
            "joint_labels": int(np.sum(dataset["joint_mask"])),
            "preservation_rows": int(np.sum(~dataset["corrected"])),
            "correction_weight": dataset["correction_weight"],
            "teacher_manifest": dataset["teacher_manifest"],
            "shadow_manifest": dataset["shadow_manifest"],
        },
        "training": {
            "updates": updates,
            "metrics": metrics,
            "teacher_metrics": teacher_metrics,
            "shadow_metrics": shadow_metrics,
            "hidden_mse": hidden_mse,
            "changed_leaves": sorted(changed),
            "expected_changed_leaves": sorted(expected_changed),
            "last_gradient_norms": gradient_rows[-1],
        },
        "exports": {str(key): value for key, value in exports.items()},
        "decision": (
            "EARN_ONE_V146_ON_POLICY_DAGGER_CAUSAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_ONE_STEP_ON_POLICY_DAGGER"
        ),
        "authority": {
            "v146_behavior_preregistration": not failed,
            "behavior": False,
            "hosted_training": False,
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
        "# Winner V145 on-policy DAgger CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Dataset: 4,800 prior teacher rows + 600 V140 on-policy rows; "
        "only 60 torque-projected joint elements change target.\n"
        f"- Corrected ratio: "
        f"`{metrics['corrected_ratio_to_zero_predictor']}`\n"
        f"- Preservation ratio: "
        f"`{metrics['preservation_ratio_to_corrected_baseline']}`\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU contract only; no behavior, Colab, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
