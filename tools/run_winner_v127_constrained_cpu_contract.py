#!/usr/bin/env python3
"""Run the preregistered V127 constrained-PPO CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_winner_v113_postexport_policies import sha256  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    sha256_directory,
    tree_errors,
)
from run_winner_v119_transition_cpu_smoke import (  # noqa: E402
    deployed_onnx_contract,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
MARKDOWN = ANALYSIS / "WINNER_V127_CONSTRAINED_CPU_RESULT_20260724.md"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
V119_PREREG = ANALYSIS / "winner_v119_transition_cpu_preregistration.json"
VELOCITY_LIMITS = (
    "1.0,.75,1.4736209064722061,1.4300791546702385,"
    "1.3976470567286015,.5,.5,.5,.5,.5,.75,1.25,1.0,"
    "1.2215287424623966"
)


def input_sha256_directory(path: Path) -> str:
    """Hash a source directory exactly as the preregistration builder does."""
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def deployment_inference_error(candidate: Path, frozen: Path) -> float:
    candidate_session = ort.InferenceSession(
        candidate.read_bytes(), providers=["CPUExecutionProvider"]
    )
    frozen_session = ort.InferenceSession(
        frozen.read_bytes(), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260724)
    maximum = 0.0
    for _ in range(32):
        feeds = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": rng.uniform(-0.5, 0.5, (1, 14)).astype(
                np.float32
            ),
            "h_in": rng.normal(size=(1, 64)).astype(np.float32),
        }
        candidate_outputs = candidate_session.run(None, feeds)
        frozen_outputs = frozen_session.run(None, feeds)
        for left, right in zip(candidate_outputs, frozen_outputs, strict=True):
            maximum = max(
                maximum,
                float(np.max(np.abs(np.asarray(left) - np.asarray(right)))),
            )
    return maximum


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(template)
    return checkpointer.restore(
        str(path), item=template, restore_args=restore_args
    )


def command(
    playground: Path,
    source: Path,
    output: Path,
) -> list[str]:
    return [
        sys.executable,
        "playground/open_duck_mini_v2/runner.py",
        "--task",
        "flat_terrain_backlash",
        "--env",
        "joystick",
        "--output_dir",
        str(output),
        "--num_timesteps",
        "1024",
        "--ppo_seed",
        "100",
        "--ppo_num_envs",
        "4",
        "--ppo_num_evals",
        "2",
        "--ppo_episode_length",
        "64",
        "--ppo_unroll_length",
        "8",
        "--ppo_batch_size",
        "4",
        "--ppo_num_minibatches",
        "1",
        "--ppo_num_updates_per_batch",
        "2",
        "--ppo_learning_rate",
        "0.0003",
        "--ppo_discounting",
        "0.97",
        "--ppo_entropy_cost",
        "0.005",
        "--policy_architecture",
        "reference_residual_recurrent_adapter",
        "--recurrent_hidden_size",
        "64",
        "--imitation_scale",
        "1.0",
        "--reference_feature_table_path",
        str(REFERENCE),
        "--nominal_reference_bootstrap",
        "--ground_up_hard_vector_command_support",
        "--ground_up_command_support_min_x",
        "0.074",
        "--ground_up_command_support_max_x",
        "0.080",
        "--ground_up_action_velocity_limits_rad_s",
        VELOCITY_LIMITS,
        "--ground_up_measured_actuator_bridge",
        "--ground_up_actuator_bridge_delay_ticks",
        "3,3,3,3,3,3,2,3,3,3,2,3,2,3",
        "--ground_up_actuator_bridge_tau_s",
        ".015,.015,.005,.010,.010,.120,.120,.120,.120,.020,"
        ".035,.010,.030,.005",
        "--ground_up_applied_target_observation",
        "--ground_up_tracking_tail_exceedance_scale",
        "-6572.254964031055",
        "--ground_up_tracking_tail_threshold_rad",
        "0.20",
        "--ground_up_peak_torque_exceedance_scale",
        "0",
        "--ground_up_linear_peak_torque_exceedance_scale",
        "0",
        "--reference_start_phase",
        "0",
        "--ground_up_signed_progress_objective",
        "--winner_v3_variable_configuration",
        "--winner_v3_deviation_scale",
        "1.0",
        "--winner_v119_train_transition_match",
        "--winner_v127_constrained_cost",
        "--critic_observation",
        "privileged_state",
        "--restore_checkpoint_path",
        str(source),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--v121-half", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--reuse-completed-smoke", action="store_true")
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    frozen_v121 = args.v121_half.resolve()
    work = args.work_root.resolve()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V127 CPU evidence")
    if work.exists() != args.reuse_completed_smoke:
        raise FileExistsError(
            "work root must be absent for a new run and present only for "
            "an explicitly preregistered recovery"
        )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
        or prereg.get("failed_checks") != []
        or prereg.get("authority", {}).get("cpu_contract_authorized")
        is not True
    ):
        raise ValueError("V127 CPU contract is not preregistered")
    expected_hashes = prereg["input_hashes"]
    observed_hashes = {
        "oracle_result": sha256(
            ANALYSIS / "winner_v126_all_tick_supreme_clip_behavior_result.json"
        ),
        "retro_audit": sha256(
            ANALYSIS / "winner_v126_v115_linear_price_clipping_audit.json"
        ),
        "train": sha256(
            ROOT / "training/winner_v127_constrained_ppo_train.py"
        ),
        "losses": sha256(
            ROOT / "training/winner_v127_constrained_ppo_losses.py"
        ),
        "patch": sha256(
            ROOT / "patches/winner_v127_constrained_cost_channel.patch"
        ),
        "composer": sha256(
            ROOT / "tools/compose_winner_v127_constrained_playground.py"
        ),
        "runner": sha256(Path(__file__).resolve()),
        "builder": sha256(
            ROOT / "tools/build_winner_v127_constrained_cpu_preregistration.py"
        ),
        "composed_manifest": sha256(
            playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
        ),
        "source_checkpoint_directory": input_sha256_directory(source),
    }
    if observed_hashes != expected_hashes:
        raise ValueError(
            f"V127 inputs changed: {observed_hashes} != {expected_hashes}"
        )
    recovery = prereg.get("recovery")
    if args.reuse_completed_smoke:
        log = work / "training.log"
        output = work / "smoke"
        if (
            not isinstance(recovery, dict)
            or recovery.get("authorized") is not True
            or recovery.get("training_log_sha256") != sha256(log)
            or recovery.get("smoke_directory_sha256")
            != input_sha256_directory(output)
        ):
            raise ValueError("V127 completed-smoke recovery is not frozen")

    sys.path.insert(0, str(playground))
    from playground.open_duck_mini_v2.joystick import (  # noqa: E402
        default_config,
        winner_v127_dense_torque_exceedance_cost,
    )
    from playground.common.winner_v127_constrained_ppo_train import (  # noqa: E402
        winner_v127_dual_update,
    )

    config = default_config()
    forces = np.asarray(
        [0.0, 1.91229675, -2.0, 2.5] + [0.25] * 10,
        dtype=np.float32,
    )
    observed_cost = float(
        winner_v127_dense_torque_exceedance_cost(
            jax.numpy.asarray(forces), 1.91229675
        )
    )
    analytic_cost = float(
        np.maximum(np.abs(forces) - np.float32(1.91229675), 0).sum()
    )
    k = 32
    quarter = math.ceil(k / 4)
    j_c0 = 2.5
    dual, eta, initial_cost, initialized = (
        jax.numpy.asarray(0.0),
        jax.numpy.asarray(0.0),
        jax.numpy.asarray(0.0),
        jax.numpy.asarray(False),
    )
    dual, eta, initial_cost, initialized = winner_v127_dual_update(
        dual,
        eta,
        initial_cost,
        initialized,
        jax.numpy.asarray(0.0),
        quarter,
    )
    zero_state = (
        float(dual),
        float(eta),
        float(initial_cost),
        bool(initialized),
    )
    persistent: list[float] = []
    for _ in range(quarter):
        dual, eta, initial_cost, initialized = winner_v127_dual_update(
            dual,
            eta,
            initial_cost,
            initialized,
            jax.numpy.asarray(j_c0),
            quarter,
        )
        persistent.append(float(dual))
    synthetic_eta = float(eta)
    synthetic_initial_cost = float(initial_cost)
    synthetic_initialized = bool(initialized)

    output = work / "smoke"
    log = work / "training.log"
    run_command = command(playground, source, output)
    if args.reuse_completed_smoke:
        elapsed = float(recovery["elapsed_upper_bound_seconds"])
    else:
        work.mkdir(parents=True)
        output.mkdir()
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(playground)
        started = time.monotonic()
        completed = subprocess.run(
            run_command,
            cwd=playground,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=1800,
            check=False,
        )
        elapsed = time.monotonic() - started
        log.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            raise RuntimeError(
                f"V127 CPU runner failed rc={completed.returncode}; "
                f"tail={completed.stdout[-5000:]}"
            )

    policy_checkpoints = sorted(
        path
        for path in output.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    )
    cost_checkpoints = sorted(output.glob("*_v127_cost_value"))
    raw_graphs = sorted(output.glob("*.onnx"))
    aux_paths = sorted(output.glob("*_v127_aux.json"))
    policy_by_step = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in policy_checkpoints
    }
    cost_by_step = {
        int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
        for path in cost_checkpoints
    }
    raw_by_step = {
        int(path.stem.rsplit("_", 1)[1]): path for path in raw_graphs
    }
    aux_by_step = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in aux_paths
    }
    expected_steps = [0, 1024]
    if (
        sorted(policy_by_step) != expected_steps
        or sorted(cost_by_step) != expected_steps
        or sorted(raw_by_step) != expected_steps
        or sorted(aux_by_step) != expected_steps
    ):
        raise ValueError("V127 export steps are incomplete")

    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(cpu_template))
    source_tree = restore_like(source, template)
    initial_tree = restore_like(policy_by_step[0], source_tree)
    final_tree = restore_like(policy_by_step[1024], source_tree)
    source_structure, source_deltas = tree_errors(source_tree, initial_tree)
    trained_structure, trained_deltas = tree_errors(initial_tree, final_tree)
    policy_deltas = {
        name: value
        for name, value in trained_deltas.items()
        if name.startswith("1/params/")
    }
    initial_cost_tree = checkpointer.restore(str(cost_by_step[0]))
    final_cost_tree = restore_like(cost_by_step[1024], initial_cost_tree)
    cost_structure, cost_deltas = tree_errors(
        initial_cost_tree, final_cost_tree
    )
    aux_initial = json.loads(aux_by_step[0].read_text(encoding="utf-8"))
    aux_final = json.loads(aux_by_step[1024].read_text(encoding="utf-8"))

    v119_prereg = json.loads(V119_PREREG.read_text(encoding="utf-8"))
    deployed = {}
    for step, raw_path in raw_by_step.items():
        deployed_path = work / f"v127_deployed_{step}.onnx"
        deployed[step] = deployed_onnx_contract(
            raw_path, deployed_path, prereg=v119_prereg
        )
        deployed[step]["path"] = str(deployed_path)
        deployed[step]["step"] = step
    step0_error = deployment_inference_error(
        Path(deployed[0]["path"]), frozen_v121
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
    final_eta_expected = (
        1.0
        / (
            float(aux_final["quarter_iterations"])
            * float(aux_final["initial_cost"])
        )
        if aux_final["initialized"]
        else 0.0
    )
    all_policy_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_tree)
    )
    all_cost_finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final_cost_tree)
    )
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "default_off_config_exact_false": (
            config.winner_v127_constrained_cost is False
        ),
        "dense_cost_matches_source_law": abs(observed_cost - analytic_cost)
        <= 1.0e-7,
        "synthetic_zero_cost_leaves_dual_uninitialized": zero_state
        == (0.0, 0.0, 0.0, False),
        "synthetic_first_positive_cost_initializes_derived_eta": (
            synthetic_initialized
            and synthetic_initial_cost == j_c0
            and math.isclose(
                synthetic_eta,
                1.0 / (quarter * j_c0),
                rel_tol=1.0e-6,
                abs_tol=1.0e-9,
            )
        ),
        "synthetic_persistent_cost_lambda_monotone": all(
            right >= left
            for left, right in zip(
                persistent[:-1], persistent[1:], strict=True
            )
        ),
        "synthetic_persistent_cost_reaches_one_by_quarter": abs(
            persistent[-1] - 1.0
        )
        <= 1.0e-12,
        "source_checkpoint_has_only_three_deployable_trees": len(source_tree)
        == 3,
        "source_restore_structure_exact": source_structure,
        "source_restore_parameters_bit_exact": max(
            source_deltas.values(), default=0.0
        )
        == 0.0,
        "trained_policy_structure_exact": trained_structure,
        "every_policy_leaf_updated": bool(policy_deltas)
        and all(value > 0.0 for value in policy_deltas.values()),
        "trained_policy_tree_finite": bool(all_policy_finite),
        "cost_critic_structure_exact": cost_structure,
        "every_cost_critic_leaf_updated": bool(cost_deltas)
        and all(value > 0.0 for value in cost_deltas.values()),
        "trained_cost_critic_tree_finite": bool(all_cost_finite),
        "initial_dual_state_exact": aux_initial
        == {
            "eta": 0.0,
            "initial_cost": 0.0,
            "initialized": False,
            "lambda": 0.0,
            "quarter_iterations": 8,
            "step": 0,
            "total_training_iterations": 32,
        },
        "smoke_dual_state_obeys_zero_or_initialized_branch": (
            (
                aux_final["initialized"] is False
                and float(aux_final["initial_cost"]) == 0.0
                and float(aux_final["eta"]) == 0.0
                and float(aux_final["lambda"]) == 0.0
            )
            or (
                aux_final["initialized"] is True
                and math.isfinite(float(aux_final["initial_cost"]))
                and float(aux_final["initial_cost"]) > 0.0
                and math.isclose(
                    float(aux_final["eta"]),
                    final_eta_expected,
                    rel_tol=1.0e-6,
                    abs_tol=1.0e-9,
                )
                and math.isfinite(float(aux_final["lambda"]))
                and float(aux_final["lambda"]) > 0.0
            )
        ),
        "both_deployed_onnx_abis_exact": all(
            row["graph_io"] == expected_io for row in deployed.values()
        ),
        "both_deployed_onnx_contracts_pass": all(
            row["inference"]["pass"] for row in deployed.values()
        ),
        "both_deployed_initializers_finite": all(
            row["initializers_finite"] for row in deployed.values()
        ),
        "step0_deployed_inference_matches_v121_half": step0_error
        <= 1.0e-7,
        "wall_seconds_at_most_1800": elapsed <= 1800,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v127.constrained_cpu_result.v1",
        "status": (
            "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "training": {
            "command": run_command,
            "elapsed_seconds": elapsed,
            "completed_smoke_reused": args.reuse_completed_smoke,
            "policy_checkpoint_sha256": {
                str(step): sha256_directory(path)
                for step, path in policy_by_step.items()
            },
            "cost_checkpoint_sha256": {
                str(step): sha256_directory(path)
                for step, path in cost_by_step.items()
            },
            "raw_onnx_sha256": {
                str(step): sha256(path) for step, path in raw_by_step.items()
            },
            "aux": {"0": aux_initial, "1024": aux_final},
            "policy_leaf_max_abs_delta": policy_deltas,
            "cost_leaf_max_abs_delta": cost_deltas,
        },
        "cost_law": {
            "forces_nm": forces.tolist(),
            "observed": observed_cost,
            "analytic": analytic_cost,
            "max_abs_error": abs(observed_cost - analytic_cost),
        },
        "deployment": {
            "step0_v121_half_max_abs_error": step0_error,
            "graphs": deployed,
        },
        "decision": (
            "EARN_ONE_V127_HOSTED_PREREGISTRATION"
            if not failed
            else "NO_HOSTED_RUN"
        ),
        "authority": {
            "hosted_preregistration_authorized": not failed,
            "hosted_run_authorized": False,
            "robot_or_rdk": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127 constrained CPU contract\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- First batch cost: `{aux_final['initial_cost']}`\n"
        f"- Derived eta: `{aux_final['eta']}`\n"
        f"- Final lambda: `{aux_final['lambda']}`\n"
        f"- V121-half step-0 inference error: `{step0_error}`\n"
        f"- Decision: `{payload['decision']}`\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "output": str(RESULT),
                "sha256": sha256(RESULT),
            }
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
