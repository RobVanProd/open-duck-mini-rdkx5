#!/usr/bin/env python3
"""Run the preregistered V143 torque-only actor CPU contract."""

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
import winner_v143_torque_only_actor_distillation as distill  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v143_torque_only_actor_cpu_preregistration.json"
RESULT = ANALYSIS / "winner_v143_torque_only_actor_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V143_TORQUE_ONLY_ACTOR_CPU_RESULT_20260725.md"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V142_ATTRIBUTION = (
    ANALYSIS / "winner_v142_transferred_load_attribution.json"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate_actions(
    network,
    normalizer,
    policy,
    dataset: dict,
    transform: dict,
) -> tuple[np.ndarray, np.ndarray]:
    action, hidden = distill.deployed_actions(
        network,
        normalizer,
        policy,
        jnp.asarray(dataset["obs"]),
        jnp.asarray(dataset["previous_action"]),
        jnp.asarray(dataset["h_in"]),
        transform,
    )
    return np.asarray(action), np.asarray(hidden)


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
            raise FileExistsError(f"refusing to overwrite V143: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    oracle_root = args.oracle_run_root.resolve()
    frozen_deployed = args.v121_final_deployed.resolve()
    work = args.work_root.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "v131_behavior_result": file_sha256(V131_RESULT),
        "v142_attribution": file_sha256(V142_ATTRIBUTION),
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v134_training_module": file_sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "training_module": file_sha256(
            TRAINING / "winner_v143_torque_only_actor_distillation.py"
        ),
        "runner": file_sha256(Path(__file__).resolve()),
        "network_source": file_sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": file_sha256(frozen_deployed),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V143 CPU preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = distill.load_teacher_dataset(oracle_root)
    indices = distill.smoke_indices(dataset)
    smoke_np = {
        key: np.asarray(dataset[key][indices])
        for key in (
            "obs",
            "previous_action",
            "h_in",
            "base_action",
            "target_action",
            "target_h_out",
            "weights",
            "corrected",
        )
    }
    smoke = {
        key: jnp.asarray(value)
        for key, value in smoke_np.items()
        if key not in {"base_action", "corrected"}
    }
    template = ocp.PyTreeCheckpointer().restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = running_statistics.RunningStatisticsState(
        **source_tree[0]
    )
    source_tree = [normalizer, source_tree[1], source_tree[2]]
    initial_policy = source_tree[1]
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

    def objective(policy):
        return distill.loss_components(
            network, normalizer, policy, smoke, transform
        )

    value_and_grad = jax.jit(jax.value_and_grad(objective, has_aux=True))
    evaluate = jax.jit(objective)
    initial_action, initial_hidden = evaluate_actions(
        network, normalizer, initial_policy, dataset, transform
    )
    policy = initial_policy
    update_rows = []
    gradient_norm_rows = []
    for update_index in range(1, 3):
        (loss, components), raw_grads = value_and_grad(policy)
        grads = distill.freeze_scale_gradients(raw_grads)
        norm = float(distill.gradient_norm(grads))
        slope = norm * norm
        initial_step = 1.0 / max(1.0, norm)
        accepted = None
        for backtrack in range(distill.STD_BACKTRACK_LIMIT + 1):
            step = initial_step * (0.5**backtrack)
            candidate = distill.apply_gradient(policy, grads, step)
            candidate_loss, candidate_components = evaluate(candidate)
            if float(candidate_loss) <= (
                float(loss) - distill.ARMIJO_FRACTION * step * slope
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
            raise RuntimeError("V143 deterministic line search failed")
        (
            policy,
            step,
            backtrack,
            candidate_loss,
            candidate_components,
        ) = accepted
        gradient_norm_rows.append(leaf_norms(grads))
        update_rows.append(
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

    final_loss, final_components = evaluate(policy)
    final_action, final_hidden = evaluate_actions(
        network, normalizer, policy, dataset, transform
    )
    smoke_final_action, smoke_final_hidden = evaluate_actions(
        network,
        normalizer,
        policy,
        {key: np.asarray(dataset[key][indices]) for key in dataset if key in {
            "obs", "previous_action", "h_in"
        }},
        transform,
    )
    full_metrics = action_metrics(
        final_action,
        dataset["target_action"],
        dataset["base_action"],
        dataset["corrected"],
    )
    smoke_metrics = action_metrics(
        smoke_final_action,
        smoke_np["target_action"],
        smoke_np["base_action"],
        smoke_np["corrected"],
    )
    updated_tree = [normalizer, policy, source_tree[2]]
    structure, deltas = tree_deltas(source_tree, updated_tree)
    changed = {name for name, value in deltas.items() if value > 0.0}
    scale_paths = {
        "1/params/scale_logits/bias",
        "1/params/scale_logits/kernel",
    }
    actor_paths = {
        name for name in deltas if name.startswith("1/params/")
    }
    expected_changed = actor_paths - scale_paths
    last_gradient_norms = gradient_norm_rows[-1]

    work.mkdir(parents=True)
    exports = {}
    for value, params in ((0, source_tree), (2, updated_tree)):
        raw_path = work / f"winner_v143_raw_{value}.onnx"
        deployed_path = work / f"winner_v143_deployed_{value}.onnx"
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
    initial_hidden_error = float(
        np.max(np.abs(initial_hidden - dataset["target_h_out"]))
    )
    final_hidden_mse = float(
        np.mean(np.square(final_hidden - dataset["target_h_out"]))
    )
    smoke_hidden_mse = float(
        np.mean(
            np.square(
                smoke_final_hidden - smoke_np["target_h_out"]
            )
        )
    )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "dataset_exact_4800_with_17_torque_corrections": (
            dataset["obs"].shape == (4_800, 115)
            and int(np.sum(dataset["corrected"])) == 17
            and int(np.sum(dataset["torque_projected"])) == 17
            and int(np.sum(dataset["supreme_only_reset_to_source"])) == 54
        ),
        "all_non_torque_targets_are_source_exact": bool(
            np.array_equal(
                dataset["target_action"][~dataset["corrected"]],
                dataset["base_action"][~dataset["corrected"]],
            )
        ),
        "correction_weight_class_balance_derived": math.isclose(
            dataset["correction_weight"],
            4_783 / 17,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "smoke_batch_exact_17_plus_239": (
            len(indices) == 256
            and int(np.sum(smoke_np["corrected"])) == 17
        ),
        "initial_actions_match_recorded_base": (
            float(np.max(np.abs(initial_action - dataset["base_action"])))
            <= 1.0e-6
        ),
        "initial_hidden_matches_teacher": initial_hidden_error <= 1.0e-6,
        "both_line_search_updates_accepted": len(update_rows) == 2,
        "total_loss_decreases": (
            float(final_loss) < update_rows[0]["loss_before"]
        ),
        "action_loss_decreases": (
            float(final_components[0])
            < update_rows[0]["action_loss_before"]
        ),
        "smoke_corrected_error_reduced_at_least_five_percent": (
            smoke_metrics["corrected_ratio_to_zero_predictor"] <= 0.95
        ),
        "smoke_preservation_leakage_within_one_percent": (
            smoke_metrics["preservation_ratio_to_corrected_baseline"]
            <= 0.01
        ),
        "full_corrected_error_reduced_at_least_five_percent": (
            full_metrics["corrected_ratio_to_zero_predictor"] <= 0.95
        ),
        "full_preservation_leakage_within_one_percent": (
            full_metrics["preservation_ratio_to_corrected_baseline"]
            <= 0.01
        ),
        "hidden_error_bounded": (
            smoke_hidden_mse
            <= smoke_metrics["baseline_corrected_mse"] * 0.01
            and final_hidden_mse
            <= full_metrics["baseline_corrected_mse"] * 0.01
        ),
        "checkpoint_structure_exact": structure,
        "all_non_scale_actor_leaves_changed": changed == expected_changed,
        "scale_logits_frozen": not bool(changed & scale_paths),
        "last_gradients_finite": all(
            math.isfinite(value) for value in last_gradient_norms.values()
        ),
        "step_zero_matches_v121_final_deployment": step_zero_error <= 1.0e-7,
        "both_export_abis_exact": all(
            row["deployed"]["graph_io"] == expected_io
            for row in exports.values()
        ),
        "both_export_inference_contracts_pass": all(
            row["deployed"]["inference"]["pass"]
            for row in exports.values()
        ),
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v143.torque_only_actor_cpu_result.v1",
        "status": (
            "PASS_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V143_TORQUE_ONLY_ACTOR_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "rows": 4_800,
            "torque_corrected_rows": 17,
            "supreme_only_rows_reset_to_source": 54,
            "preservation_rows": 4_783,
            "correction_weight": dataset["correction_weight"],
            "trace_manifest": dataset["manifest"],
        },
        "smoke": {
            "rows": 256,
            "updates": update_rows,
            "metrics": smoke_metrics,
            "final_total_loss": float(final_loss),
            "final_action_loss": float(final_components[0]),
            "final_hidden_loss": float(final_components[1]),
            "hidden_mse": smoke_hidden_mse,
            "changed_leaves": sorted(changed),
            "expected_changed_leaves": sorted(expected_changed),
            "last_gradient_norms": last_gradient_norms,
        },
        "full_dataset": {
            "metrics": full_metrics,
            "hidden_mse": final_hidden_mse,
        },
        "exports": {str(key): value for key, value in exports.items()},
        "step_zero_v121_final_max_abs_error": step_zero_error,
        "decision": (
            "EARN_ONE_V144_TORQUE_ONLY_ACTOR_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_TORQUE_ONLY_ACTOR_DISTILLATION"
        ),
        "authority": {
            "behavior_preregistration": not failed,
            "behavior_evaluation": False,
            "formal_distillation_training": False,
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
        "# Winner V143 torque-only actor CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Teacher changes only 17 torque-projected rows; all other "
        "4,783 rows target the frozen source action.\n"
        f"- Full corrected ratio: "
        f"`{full_metrics['corrected_ratio_to_zero_predictor']}`\n"
        f"- Full preservation ratio: "
        f"`{full_metrics['preservation_ratio_to_corrected_baseline']}`\n"
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
