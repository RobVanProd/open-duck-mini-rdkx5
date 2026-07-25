#!/usr/bin/env python3
"""Run the preregistered V168 fit-conditioned two-policy CPU falsifier."""

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
from validate_winner_v112_recovered_training import tree_deltas  # noqa: E402
import winner_v134_full_actor_teacher_distillation as distill  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v168_fit_conditioned_policy_bank_cpu_preregistration.json"
)
RESULT = (
    ANALYSIS / "winner_v168_fit_conditioned_policy_bank_cpu_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_RESULT_20260725.md"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V130_AUDIT = ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V134_RESULT = ANALYSIS / "winner_v134_full_actor_teacher_cpu_result_v3.json"
FIT_TAGS = (
    "p30_all_joint",
    "p31_34_pitch_with_p30_nonpitch",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def path_name(path: tuple) -> str:
    parts = []
    for item in path:
        key = getattr(item, "key", None)
        index = getattr(item, "idx", None)
        parts.append(str(key if key is not None else index))
    return "/".join(parts)


def leaf_norms(tree) -> dict[str, float]:
    return {
        path_name(path): float(np.linalg.norm(np.asarray(value)))
        for path, value in jax.tree_util.tree_flatten_with_path(tree)[0]
    }


def action_metrics(
    action: np.ndarray,
    target: np.ndarray,
    base: np.ndarray,
    corrected: np.ndarray,
) -> dict:
    baseline = float(
        np.mean(np.square(target[corrected] - base[corrected]))
    )
    corrected_mse = float(
        np.mean(np.square(action[corrected] - target[corrected]))
    )
    preservation_mse = float(
        np.mean(np.square(action[~corrected] - target[~corrected]))
    )
    return {
        "baseline_corrected_mse": baseline,
        "corrected_mse": corrected_mse,
        "corrected_ratio_to_zero_predictor": corrected_mse / baseline,
        "preservation_mse": preservation_mse,
        "preservation_ratio_to_corrected_baseline": (
            preservation_mse / baseline
        ),
        "error_linf": float(np.max(np.abs(action - target))),
    }


def fit_smoke(dataset: dict, fit_tag: str) -> tuple[dict, dict, np.ndarray]:
    fit_mask = np.asarray(
        [fit_tag in key for key in dataset["keys"]], dtype=np.bool_
    )
    fit_indices = np.flatnonzero(fit_mask)
    corrected_indices = fit_indices[dataset["corrected"][fit_indices]]
    preservation_indices = fit_indices[~dataset["corrected"][fit_indices]]
    keep_preservation = 256 - len(corrected_indices)
    indices = np.concatenate(
        [corrected_indices, preservation_indices[:keep_preservation]]
    )
    corrected = np.asarray(dataset["corrected"][indices])
    correction_weight = float(
        len(preservation_indices) / len(corrected_indices)
    )
    smoke_np = {
        key: np.asarray(dataset[key][indices])
        for key in (
            "obs",
            "previous_action",
            "h_in",
            "base_action",
            "target_action",
            "target_h_out",
            "corrected",
        )
    }
    smoke_np["weights"] = np.where(
        corrected, correction_weight, 1.0
    ).astype(np.float32)
    metadata = {
        "fit_rows": int(len(fit_indices)),
        "corrected_rows": int(len(corrected_indices)),
        "preservation_rows": int(len(preservation_indices)),
        "smoke_rows": int(len(indices)),
        "smoke_corrected_rows": int(np.sum(corrected)),
        "smoke_preservation_rows": int(np.sum(~corrected)),
        "correction_weight": correction_weight,
    }
    return smoke_np, metadata, indices


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
            raise FileExistsError(f"refusing to overwrite V168: {path}")

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
    observed_hashes = {
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v130_feature_audit": file_sha256(V130_AUDIT),
        "v131_behavior_result": file_sha256(V131_RESULT),
        "v134_cpu_result": file_sha256(V134_RESULT),
        "training_module": file_sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "runner": file_sha256(Path(__file__).resolve()),
        "network_source": file_sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": file_sha256(frozen_deployed),
    }
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_FALSIFIER"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V168 CPU preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = distill.load_teacher_dataset(oracle_root)
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
    work.mkdir(parents=True)
    fit_results = {}
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
    scale_paths = {
        "1/params/scale_logits/bias",
        "1/params/scale_logits/kernel",
    }

    for fit_tag in FIT_TAGS:
        smoke_np, metadata, indices = fit_smoke(dataset, fit_tag)
        smoke = {
            key: jnp.asarray(value)
            for key, value in smoke_np.items()
            if key not in {"base_action", "corrected"}
        }

        def objective(policy):
            return distill.loss_components(
                network, normalizer, policy, smoke, transform
            )

        value_and_grad = jax.jit(
            jax.value_and_grad(objective, has_aux=True)
        )
        evaluate = jax.jit(objective)
        initial_action, initial_hidden = distill.deployed_actions(
            network,
            normalizer,
            initial_policy,
            smoke["obs"],
            smoke["previous_action"],
            smoke["h_in"],
            transform,
        )
        initial_action_np = np.asarray(initial_action)
        initial_hidden_np = np.asarray(initial_hidden)
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
                    float(loss)
                    - distill.ARMIJO_FRACTION * step * slope
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
                raise RuntimeError(
                    f"V168 deterministic line search failed for {fit_tag}"
                )
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
        final_action, final_hidden = distill.deployed_actions(
            network,
            normalizer,
            policy,
            smoke["obs"],
            smoke["previous_action"],
            smoke["h_in"],
            transform,
        )
        final_action_np = np.asarray(final_action)
        final_hidden_np = np.asarray(final_hidden)
        metrics = action_metrics(
            final_action_np,
            smoke_np["target_action"],
            smoke_np["base_action"],
            smoke_np["corrected"],
        )
        hidden_mse = float(
            np.mean(
                np.square(final_hidden_np - smoke_np["target_h_out"])
            )
        )
        updated_tree = [normalizer, policy, source_tree[2]]
        structure, deltas = tree_deltas(source_tree, updated_tree)
        changed = {name for name, value in deltas.items() if value > 0.0}
        actor_paths = {
            name for name in deltas if name.startswith("1/params/")
        }
        expected_changed = actor_paths - scale_paths
        exports = {}
        for value, params in ((0, source_tree), (2, updated_tree)):
            raw_path = work / f"winner_v168_{fit_tag}_raw_{value}.onnx"
            deployed_path = (
                work / f"winner_v168_{fit_tag}_deployed_{value}.onnx"
            )
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
            exports[str(value)] = {
                "raw_path": str(raw_path),
                "raw_sha256": sha256(raw_path),
                "deployed": deploy_graph(
                    raw_path, deployed_path, transform
                ),
            }
        step_zero_error = inference_error(
            Path(exports["0"]["deployed"]["path"]), frozen_deployed
        )
        checks = {
            "fit_partition_exact": (
                metadata["fit_rows"] == 2_400
                and metadata["smoke_rows"] == 256
                and metadata["corrected_rows"]
                == (36 if fit_tag == FIT_TAGS[0] else 35)
            ),
            "correction_weight_fit_derived": math.isclose(
                metadata["correction_weight"],
                metadata["preservation_rows"]
                / metadata["corrected_rows"],
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ),
            "initial_actions_match_recorded_base": (
                float(
                    np.max(
                        np.abs(
                            initial_action_np - smoke_np["base_action"]
                        )
                    )
                )
                <= 1.0e-6
            ),
            "initial_hidden_matches_teacher": (
                float(
                    np.max(
                        np.abs(
                            initial_hidden_np
                            - smoke_np["target_h_out"]
                        )
                    )
                )
                <= 1.0e-6
            ),
            "both_line_search_updates_accepted": len(update_rows) == 2,
            "total_loss_decreases": (
                float(final_loss) < update_rows[0]["loss_before"]
            ),
            "action_loss_decreases": (
                float(final_components[0])
                < update_rows[0]["action_loss_before"]
            ),
            "corrected_error_reduced_at_least_five_percent": (
                metrics["corrected_ratio_to_zero_predictor"] <= 0.95
            ),
            "preservation_leakage_within_one_percent": (
                metrics["preservation_ratio_to_corrected_baseline"]
                <= 0.01
            ),
            "hidden_error_bounded": (
                hidden_mse
                <= metrics["baseline_corrected_mse"] * 0.01
            ),
            "checkpoint_structure_exact": structure,
            "all_non_scale_actor_leaves_changed": (
                changed == expected_changed
            ),
            "scale_logits_frozen": not bool(changed & scale_paths),
            "last_gradients_finite": all(
                math.isfinite(value)
                for value in gradient_norm_rows[-1].values()
            ),
            "step_zero_matches_v121_final_deployment": (
                step_zero_error <= 1.0e-7
            ),
            "both_export_abis_exact": all(
                row["deployed"]["graph_io"] == expected_io
                for row in exports.values()
            ),
            "both_export_inference_contracts_pass": all(
                row["deployed"]["inference"]["pass"]
                for row in exports.values()
            ),
        }
        fit_results[fit_tag] = {
            "dataset": metadata,
            "indices_sha256": hashlib.sha256(
                np.asarray(indices, dtype=np.int64).tobytes()
            ).hexdigest(),
            "checks": checks,
            "failed_checks": sorted(
                name for name, passed in checks.items() if not passed
            ),
            "metrics": metrics,
            "hidden_mse": hidden_mse,
            "updates": update_rows,
            "changed_leaves": sorted(changed),
            "expected_changed_leaves": sorted(expected_changed),
            "last_gradient_norms": gradient_norm_rows[-1],
            "exports": exports,
            "step_zero_v121_final_max_abs_error": step_zero_error,
        }

    global_checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "dataset_exact_4800": dataset["obs"].shape == (4_800, 115),
        "fit_partitions_are_disjoint_and_complete": (
            sum(
                row["dataset"]["fit_rows"]
                for row in fit_results.values()
            )
            == 4_800
        ),
        "both_fit_contracts_pass": all(
            not row["failed_checks"] for row in fit_results.values()
        ),
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
        "runtime_dispatch_unchanged": True,
    }
    failed = sorted(
        name for name, passed in global_checks.items() if not passed
    )
    payload = {
        "schema_version": (
            "winner_v168.fit_conditioned_policy_bank_cpu_result.v1"
        ),
        "status": (
            "PASS_WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_FALSIFIER"
            if not failed
            else "HOLD_WINNER_V168_FIT_CONDITIONED_POLICY_BANK_CPU_FALSIFIER"
        ),
        "failed_checks": failed,
        "checks": global_checks,
        "input_hashes": observed_hashes,
        "fits": fit_results,
        "decision": (
            "EARN_REVIEWED_AUTOMATIC_FIT_DISPATCH_POLICY_BANK_CONTRACT_ONLY"
            if not failed
            else "CLOSE_FIT_CONDITIONED_TWO_POLICY_FULL_ACTOR_SMOKE_NO_RETRY"
        ),
        "authority": {
            "policy_bank_contract": not failed,
            "behavior_preregistration": False,
            "behavior_evaluation": False,
            "formal_training": False,
            "hosted_training": False,
            "runtime_change": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Winner V168 fit-conditioned policy-bank CPU result",
        "",
        f"- Status: `{payload['status']}`",
    ]
    for fit_tag, row in fit_results.items():
        lines.extend(
            [
                f"- `{fit_tag}` corrected ratio: "
                f"`{row['metrics']['corrected_ratio_to_zero_predictor']}`",
                f"- `{fit_tag}` preservation ratio: "
                f"`{row['metrics']['preservation_ratio_to_corrected_baseline']}`",
                f"- `{fit_tag}` failed checks: "
                f"`{row['failed_checks']}`",
            ]
        )
    lines.extend(
        [
            f"- Decision: `{payload['decision']}`",
            "- CPU falsifier only; no behavior, training, runtime, hardware, "
            "torque, or motion authority.",
            "",
        ]
    )
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
