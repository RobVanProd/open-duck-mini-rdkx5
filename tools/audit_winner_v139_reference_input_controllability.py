#!/usr/bin/env python3
"""Audit whether the frozen actor can express each oracle correction via reference input."""

from __future__ import annotations

import argparse
import hashlib
import json
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

from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    directory_sha256,
    restore_like,
)
import winner_v134_full_actor_teacher_distillation as teacher  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v139_reference_input_controllability_preregistration.json"
)
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V131_RESULT = ANALYSIS / "winner_v131_two_fit_oracle_behavior_result.json"
V138_RESULT = ANALYSIS / "winner_v138_phase20_start_result_v2.json"
OUTPUT = ANALYSIS / "winner_v139_reference_input_controllability_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY_RESULT_20260725.md"
)
REFERENCE_SLICE = slice(101, 115)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V139: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    teacher_root = args.teacher_run_root.resolve()
    network_source = (
        playground
        / "playground/common/reference_residual_recurrent_adapter_ppo_networks.py"
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_transform": sha256(V121_TRANSFORM),
        "v131_behavior_result": sha256(V131_RESULT),
        "v138_phase20_result": sha256(V138_RESULT),
        "teacher_loader": sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "network_source": sha256(network_source),
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V139 preregistration changed")
    sys.path.insert(0, str(playground))
    from playground.common.reference_residual_recurrent_adapter_ppo_networks import (  # noqa: E402
        make_reference_residual_recurrent_adapter_ppo_networks,
    )

    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    dataset = teacher.load_teacher_dataset(teacher_root)
    selected = np.flatnonzero(dataset["torque_projected"])
    if len(selected) != 17:
        raise ValueError("V139 requires exactly 17 torque-projected rows")
    template = ocp.PyTreeCheckpointer().restore(str(cpu_template))
    source_tree = restore_like(source, template)
    normalizer = running_statistics.RunningStatisticsState(**source_tree[0])
    policy = source_tree[1]
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
    obs = jnp.asarray(dataset["obs"][selected])
    previous = jnp.asarray(dataset["previous_action"][selected])
    hidden = jnp.asarray(dataset["h_in"][selected])
    target = np.asarray(dataset["target_action"][selected])
    recorded_base = np.asarray(dataset["base_action"][selected])

    def action_for_reference(reference, fixed_obs, prior, h_in):
        changed_obs = fixed_obs.at[REFERENCE_SLICE].set(reference)
        action, _ = teacher.deployed_actions(
            network,
            normalizer,
            policy,
            changed_obs[None],
            prior[None],
            h_in[None],
            transform,
        )
        return action[0]

    action_batch = jax.jit(
        jax.vmap(action_for_reference, in_axes=(0, 0, 0, 0))
    )
    jacobian_batch = jax.jit(
        jax.vmap(
            jax.jacrev(action_for_reference, argnums=0),
            in_axes=(0, 0, 0, 0),
        )
    )
    reference = obs[:, REFERENCE_SLICE]
    source_action = np.asarray(
        action_batch(reference, obs, previous, hidden)
    )
    jacobian = np.asarray(
        jacobian_batch(reference, obs, previous, hidden)
    )
    candidate_reference = []
    linear_predictions = []
    rows = []
    for local_index, dataset_index in enumerate(selected):
        matrix = jacobian[local_index].astype(np.float64)
        desired = (
            target[local_index] - source_action[local_index]
        ).astype(np.float64)
        delta, _, rank, singular = np.linalg.lstsq(
            matrix, desired, rcond=None
        )
        candidate_ref = (
            np.asarray(reference[local_index], dtype=np.float64) + delta
        )
        linear = source_action[local_index] + matrix @ delta
        candidate_reference.append(candidate_ref)
        linear_predictions.append(linear)
        rows.append(
            {
                "key": dataset["keys"][int(dataset_index)],
                "command_x_m_s": float(
                    dataset["obs"][dataset_index, 6]
                ),
                "phase": np.asarray(
                    dataset["obs"][dataset_index, 99:101],
                    dtype=np.float64,
                ).tolist(),
                "source_error_mse": float(
                    np.mean(np.square(source_action[local_index] - target[local_index]))
                ),
                "linear_error_mse": float(
                    np.mean(np.square(linear - target[local_index]))
                ),
                "reference_delta_linf": float(np.max(np.abs(delta))),
                "candidate_reference_linf": float(
                    np.max(np.abs(candidate_ref))
                ),
                "jacobian_rank": int(rank),
                "jacobian_min_singular": float(
                    np.min(singular) if singular.size else 0.0
                ),
            }
        )
    candidate_reference_array = jnp.asarray(
        np.stack(candidate_reference).astype(np.float32)
    )
    candidate_action = np.asarray(
        action_batch(candidate_reference_array, obs, previous, hidden)
    )
    source_mse = float(np.mean(np.square(source_action - target)))
    linear_mse = float(
        np.mean(np.square(np.stack(linear_predictions) - target))
    )
    nonlinear_mse = float(np.mean(np.square(candidate_action - target)))
    for index, row in enumerate(rows):
        row["nonlinear_error_mse"] = float(
            np.mean(np.square(candidate_action[index] - target[index]))
        )
        row["nonlinear_ratio_to_source"] = (
            row["nonlinear_error_mse"] / row["source_error_mse"]
        )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "exact_17_torque_projected_rows": len(rows) == 17,
        "source_actions_reproduce_recorded_base": (
            float(np.max(np.abs(source_action - recorded_base))) <= 1.0e-6
        ),
        "all_jacobians_and_solutions_finite": bool(
            np.all(np.isfinite(jacobian))
            and np.all(np.isfinite(candidate_reference_array))
            and np.all(np.isfinite(candidate_action))
        ),
        "linear_minimum_norm_fit_ratio_at_most_point25": (
            linear_mse / source_mse <= 0.25
        ),
        "nonlinear_fit_ratio_at_most_point25": (
            nonlinear_mse / source_mse <= 0.25
        ),
        "every_event_nonlinearly_improves": all(
            row["nonlinear_ratio_to_source"] < 1.0 for row in rows
        ),
        "all_candidate_reference_values_within_unit_box": all(
            row["candidate_reference_linf"] <= 1.0 for row in rows
        ),
        "no_behavior_training_or_hosted_compute": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v139.reference_input_controllability.v1",
        "status": (
            "PASS_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
            if not failed
            else "HOLD_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "method": {
            "population": "17 V131 torque-projected final-checkpoint rows",
            "variables": "obs[101:115] reference input only",
            "actor_policy_and_state": "frozen V121 final, recorded previous_action and h_in",
            "solver": (
                "one local Jacobian per row; NumPy minimum-L2 least-squares "
                "reference delta; one nonlinear actor readback"
            ),
            "bounds": "candidate reference must remain in [-1,1]",
            "selection_or_parameter_search": False,
        },
        "summary": {
            "rows": len(rows),
            "source_mse": source_mse,
            "linear_mse": linear_mse,
            "linear_ratio_to_source": linear_mse / source_mse,
            "nonlinear_mse": nonlinear_mse,
            "nonlinear_ratio_to_source": nonlinear_mse / source_mse,
            "reference_delta_linf_max": max(
                row["reference_delta_linf"] for row in rows
            ),
            "candidate_reference_linf_max": max(
                row["candidate_reference_linf"] for row in rows
            ),
            "minimum_jacobian_rank": min(
                row["jacobian_rank"] for row in rows
            ),
            "worst_event_nonlinear_ratio": max(
                row["nonlinear_ratio_to_source"] for row in rows
            ),
        },
        "rows": rows,
        "decision": (
            "EARN_ONE_V140_SHARED_REFERENCE_SYNTHESIS_PREREGISTRATION"
            if not failed
            else "CLOSE_REFERENCE_INPUT_REDIRECTION"
        ),
        "authority": {
            "shared_reference_synthesis_preregistration": not failed,
            "reference_artifact_change": False,
            "behavior_evaluation": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V139 reference-input controllability\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Nonlinear correction ratio: "
        f"`{payload['summary']['nonlinear_ratio_to_source']:.6f}`.\n"
        f"- Worst per-event ratio: "
        f"`{payload['summary']['worst_event_nonlinear_ratio']:.6f}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Per-event upper bound only; no shared reference, behavior, "
        "training, Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
