#!/usr/bin/env python3
"""Run the V137 recurrent sequence-distillation CPU contract."""

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
from validate_winner_v112_recovered_training import (  # noqa: E402
    tree_deltas,
)
import winner_v137_sequence_teacher_distillation as distill  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v137_sequence_teacher_cpu_preregistration.json"
)
RESULT = ANALYSIS / "winner_v137_sequence_teacher_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V137_SEQUENCE_TEACHER_CPU_RESULT_20260725.md"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V136_RESULT = ANALYSIS / "winner_v136_warm_start_startup_result.json"


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


def sequence_metrics(
    *,
    source_action: np.ndarray,
    candidate_action: np.ndarray,
    target_action: np.ndarray,
    corrected: np.ndarray,
) -> dict:
    baseline = float(
        np.mean(
            np.square(
                source_action[corrected] - target_action[corrected]
            )
        )
    )
    corrected_mse = float(
        np.mean(
            np.square(
                candidate_action[corrected] - target_action[corrected]
            )
        )
    )
    preservation_mse = float(
        np.mean(
            np.square(
                candidate_action[~corrected] - source_action[~corrected]
            )
        )
    )
    return {
        "corrected_rows": int(np.sum(corrected)),
        "preservation_rows": int(np.sum(~corrected)),
        "baseline_corrected_mse": baseline,
        "corrected_mse": corrected_mse,
        "corrected_ratio_to_source": corrected_mse / baseline,
        "preservation_mse": preservation_mse,
        "preservation_ratio_to_corrected_baseline": (
            preservation_mse / baseline
        ),
        "candidate_vs_source_linf": float(
            np.max(np.abs(candidate_action - source_action))
        ),
        "candidate_vs_teacher_linf": float(
            np.max(np.abs(candidate_action - target_action))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--v121-final-deployed", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V137: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    teacher_root = args.teacher_run_root.resolve()
    frozen_deployed = args.v121_final_deployed.resolve()
    work = args.work_root.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "v121_transform": file_sha256(V121_TRANSFORM),
        "v131_behavior_result": file_sha256(V131_RESULT),
        "v136_warm_start_result": file_sha256(V136_RESULT),
        "training_module": file_sha256(
            TRAINING / "winner_v137_sequence_teacher_distillation.py"
        ),
        "runner": file_sha256(Path(__file__).resolve()),
        "network_source": file_sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
        "v121_final_deployed": file_sha256(frozen_deployed),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V137 CPU preregistration changed")

    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        export_reference_residual_recurrent_adapter_onnx,
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = distill.load_teacher_sequences(teacher_root)
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
    startup_obs = jnp.asarray(
        dataset["obs"][:, : distill.STARTUP_TICKS]
    )
    startup_target = jnp.asarray(
        dataset["target_action"][:, : distill.STARTUP_TICKS]
    )
    startup_weights = jnp.asarray(dataset["startup_weights"])

    def objective(policy):
        return distill.startup_loss_components(
            network,
            normalizer,
            policy,
            startup_obs,
            startup_target,
            startup_weights,
            transform,
        )

    value_and_grad = jax.jit(jax.value_and_grad(objective, has_aux=True))
    evaluate = jax.jit(objective)
    full_sequence = jax.jit(
        lambda policy: distill.sequence_outputs(
            network,
            normalizer,
            policy,
            jnp.asarray(dataset["obs"]),
            transform,
        )
    )
    source_startup_action, _ = distill.sequence_outputs(
        network,
        normalizer,
        source_policy,
        startup_obs,
        transform,
    )
    policy = source_policy
    update_rows = []
    gradient_rows = []
    for update_index in range(1, 3):
        (loss, components), raw_grads = value_and_grad(policy)
        grads = distill.freeze_nonrecurrent_adapter_gradients(raw_grads)
        norm = float(distill.gradient_norm(grads))
        slope = norm * norm
        initial_step = 1.0 / max(1.0, norm)
        accepted = None
        for backtrack in range(distill.BACKTRACK_LIMIT + 1):
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
            raise RuntimeError("V137 deterministic line search failed")
        (
            policy,
            step,
            backtrack,
            candidate_loss,
            candidate_components,
        ) = accepted
        gradient_rows.append(leaf_norms(grads))
        update_rows.append(
            {
                "update": update_index,
                "loss_before": float(loss),
                "action_loss_before": float(components[0]),
                "hidden_energy_before": float(components[1]),
                "loss_after": float(candidate_loss),
                "action_loss_after": float(candidate_components[0]),
                "hidden_energy_after": float(candidate_components[1]),
                "gradient_norm": norm,
                "initial_step": initial_step,
                "accepted_step": step,
                "backtracks": backtrack,
            }
        )
    candidate_startup_action, _ = distill.sequence_outputs(
        network,
        normalizer,
        policy,
        startup_obs,
        transform,
    )
    source_full_action, _ = full_sequence(source_policy)
    candidate_full_action, _ = full_sequence(policy)
    source_startup_np = np.asarray(source_startup_action)
    candidate_startup_np = np.asarray(candidate_startup_action)
    source_full_np = np.asarray(source_full_action)
    candidate_full_np = np.asarray(candidate_full_action)
    startup_metrics = sequence_metrics(
        source_action=source_startup_np,
        candidate_action=candidate_startup_np,
        target_action=dataset["target_action"][:, : distill.STARTUP_TICKS],
        corrected=dataset["corrected"][:, : distill.STARTUP_TICKS],
    )
    full_metrics = sequence_metrics(
        source_action=source_full_np,
        candidate_action=candidate_full_np,
        target_action=dataset["target_action"],
        corrected=dataset["corrected"],
    )
    x0_indices = [
        index
        for index, row in enumerate(dataset["manifest"])
        if "_x0.000_" in row["name"]
    ]
    updated_tree = [normalizer, policy, source_tree[2]]
    structure, deltas = tree_deltas(source_tree, updated_tree)
    changed = {name for name, value in deltas.items() if value > 0.0}
    expected_changed = {
        "1/params/adapter_hidden_bias",
        "1/params/adapter_hidden_projection/kernel",
        "1/params/adapter_location/bias",
        "1/params/adapter_location/kernel",
        "1/params/adapter_obs_projection/kernel",
    }

    work.mkdir(parents=True)
    exports = {}
    for value, params in ((0, source_tree), (2, updated_tree)):
        raw_path = work / f"winner_v137_raw_{value}.onnx"
        deployed_path = work / f"winner_v137_deployed_{value}.onnx"
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
    last_gradient_norms = gradient_rows[-1]
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "dataset_exact_8x600": (
            dataset["obs"].shape == (8, 600, 115)
            and int(np.sum(dataset["corrected"])) == 71
        ),
        "startup_exact_8x32_with_15_corrections": (
            startup_obs.shape == (8, 32, 115)
            and int(
                np.sum(dataset["corrected"][:, : distill.STARTUP_TICKS])
            )
            == 15
        ),
        "startup_class_weight_derived": math.isclose(
            dataset["startup_correction_weight"],
            241 / 15,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "both_line_search_updates_accepted": len(update_rows) == 2,
        "startup_loss_strictly_decreases": (
            update_rows[-1]["loss_after"] < update_rows[0]["loss_before"]
        ),
        "startup_corrected_error_reduced_five_percent": (
            startup_metrics["corrected_ratio_to_source"] <= 0.95
        ),
        "full_corrected_error_reduced_five_percent": (
            full_metrics["corrected_ratio_to_source"] <= 0.95
        ),
        "full_preservation_leakage_within_one_percent": (
            full_metrics["preservation_ratio_to_corrected_baseline"]
            <= 0.01
        ),
        "x0_actions_remain_exact_zero": (
            len(x0_indices) == 2
            and np.count_nonzero(candidate_full_np[x0_indices]) == 0
        ),
        "checkpoint_structure_exact": structure,
        "only_five_recurrent_adapter_leaves_changed": (
            changed == expected_changed
        ),
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
        "formal_training_zero": True,
        "behavior_cells_zero": True,
        "hosted_compute_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v137.sequence_teacher_cpu_result.v1",
        "status": (
            "PASS_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V137_SEQUENCE_TEACHER_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "dataset": {
            "traces": 8,
            "ticks_per_trace": 600,
            "startup_ticks": 32,
            "full_corrected_rows": 71,
            "startup_corrected_rows": 15,
            "startup_correction_weight": dataset[
                "startup_correction_weight"
            ],
            "trace_manifest": dataset["manifest"],
        },
        "smoke": {
            "updates": update_rows,
            "startup_metrics": startup_metrics,
            "full_metrics": full_metrics,
            "changed_leaves": sorted(changed),
            "last_gradient_norms": last_gradient_norms,
        },
        "exports": {str(key): value for key, value in exports.items()},
        "step_zero_v121_final_max_abs_error": step_zero_error,
        "decision": (
            "EARN_ONE_V138_SEQUENCE_TEACHER_FORMAL_PREREGISTRATION"
            if not failed
            else "CLOSE_SEQUENCE_TEACHER_DISTILLATION"
        ),
        "authority": {
            "formal_cpu_preregistration": not failed,
            "formal_training": False,
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
        "# Winner V137 sequence-teacher CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Startup corrected ratio: "
        f"`{startup_metrics['corrected_ratio_to_source']}`\n"
        f"- Full preservation ratio: "
        f"`{full_metrics['preservation_ratio_to_corrected_baseline']}`\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Two CPU updates only; no formal training, behavior, Colab, or "
        "hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(RESULT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
