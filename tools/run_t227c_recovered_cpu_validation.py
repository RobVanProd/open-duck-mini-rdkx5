#!/usr/bin/env python3
"""Validate T227B's completed CPU smoke without rerunning it."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t209_dual_roll_cost_cpu_contract as engine  # noqa: E402
import run_t215b_axis_complete_tilt_cpu_contract as t215b  # noqa: E402
import run_t227_command_atom_cpu_contract as t227  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = (
    ANALYSIS / "t227c_recovered_cpu_validation_preregistration.json"
)
RESULT = ANALYSIS / "t227c_recovered_cpu_validation_result.json"
MARKDOWN = (
    ANALYSIS / "T227C_RECOVERED_CPU_VALIDATION_RESULT_20260730.md"
)
EXTRA_HEAD = "negative_adapter_location"


def restore_like(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T227C_RECOVERED_CPU_VALIDATION"
        or value.get("failed_checks")
        or engine.t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T227C preregistration identity changed")
    for group in ("sources", "assets", "frozen_artifacts"):
        for name, item in value[group].items():
            engine.t20.verify_receipt(item, f"{group}.{name}")
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): engine.t20.sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or engine.t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T227C playground changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recovered-cpu-validation-authorized",
        action="store_true",
    )
    args = parser.parse_args()
    if not args.recovered_cpu_validation_authorized:
        raise PermissionError(
            "T227C requires --recovered-cpu-validation-authorized"
        )
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T227C: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T227C execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    work = Path(prereg["frozen_artifacts"]["work"]["path"])
    smoke = work / "smoke"
    source_path = Path(
        prereg["assets"]["source_checkpoint"]["path"]
    )
    source_graph = Path(
        prereg["assets"]["source_raw_onnx"]["path"]
    )
    cpu_source_path = Path(
        prereg["frozen_artifacts"]["cpu_source_remap"]["path"]
    )
    reference = Path(
        prereg["assets"]["reference_features"]["path"]
    )
    gate_asset = Path(
        prereg["assets"]["hidden_gate_static_asset"]["path"]
    )
    playground = Path(prereg["playground"]["path"])

    policy = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in smoke.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    }
    cost = {
        int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
        for path in smoke.glob("*_v127_cost_value")
    }
    graphs = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in smoke.glob("*.onnx")
    }
    aux_paths = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in smoke.glob("*_v127_aux.json")
    }
    expected_steps = [0, 1024]
    artifact_sets_exact = (
        sorted(policy)
        == sorted(cost)
        == sorted(graphs)
        == sorted(aux_paths)
        == expected_steps
    )

    cpu_source = ocp.PyTreeCheckpointer().restore(str(cpu_source_path))
    source = restore_like(source_path, cpu_source)
    remap_structure, remap_deltas = tree_errors(source, cpu_source)
    initial = engine.t98.restore_tree(policy[0], source)
    final = engine.t98.restore_tree(policy[1024], source)
    restore_structure, restore_deltas = tree_errors(source, initial)
    update_structure, update_deltas = tree_errors(initial, final)
    policy_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("1/params/")
    }
    expert_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if EXTRA_HEAD in name
    }
    protected_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if name not in expert_deltas
    }
    normalizer_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("0/")
    }
    reward_critic_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("2/params/")
    }
    initial_cost = ocp.PyTreeCheckpointer().restore(str(cost[0]))
    final_cost = restore_like(cost[1024], initial_cost)
    cost_structure, cost_deltas = tree_errors(initial_cost, final_cost)
    aux = {
        str(step): json.loads(path.read_text(encoding="utf-8"))
        for step, path in sorted(aux_paths.items())
    }
    events_path = next(smoke.glob("events.out.tfevents*"))
    events = engine.t55.all_scalar_events(events_path)
    graph_contracts = {
        str(step): {
            "receipt": engine.t20.receipt(path),
            "io": engine.t98.graph_io(path),
            "chain": engine.t98.graph_chain(path),
        }
        for step, path in sorted(graphs.items())
    }
    expected_io = {
        "inputs": {
            "h_in": [1, 64],
            "obs": [1, 115],
            "previous_action": [1, 14],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "h_out": [1, 64],
            "previous_action_out": [1, 14],
        },
    }
    base_default = json.loads(
        (work / "base_default_off.json").read_text(encoding="utf-8")
    )
    composed_default = json.loads(
        (work / "composed_default_off.json").read_text(
            encoding="utf-8"
        )
    )
    environment = json.loads(
        (work / "enabled_contract.json").read_text(encoding="utf-8")
    )
    command = t227.training_command(
        playground=playground,
        output=smoke,
        restore=cpu_source_path,
        reference=reference,
        gate_asset=gate_asset,
    )
    training_log = (work / "training.log").read_text(encoding="utf-8")
    contract = prereg["derived_training_contract"]
    initial_aux_expected = {
        "eta": 0.0,
        "initial_cost": 0.0,
        "initialized": False,
        "lambda": 0.0,
        "quarter_iterations": contract["quarter_iterations"],
        "step": 0,
        "total_training_iterations": contract[
            "total_training_iterations"
        ],
    }
    final_aux = aux["1024"]
    if final_aux["initialized"]:
        eta_expected = 1.0 / (
            float(final_aux["quarter_iterations"])
            * float(final_aux["initial_cost"])
        )
    else:
        eta_expected = 0.0
    artifact_files = [
        path
        for path in work.rglob("*")
        if path.is_file()
    ]
    artifact_span_seconds = (
        max(path.stat().st_mtime for path in artifact_files)
        - min(path.stat().st_mtime for path in artifact_files)
    )

    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "all_export_sets_exact": artifact_sets_exact,
        "default_off_trajectory_bit_exact": (
            base_default["trajectory_digests"]
            == composed_default["trajectory_digests"]
        ),
        "environment_lattice_all_green": (
            environment["status"]
            == "PASS_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
            and environment["failed_checks"] == []
            and all(environment["checks"].values())
        ),
        "source_cpu_remap_exact": (
            remap_structure
            and max(remap_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_tree_exact": (
            restore_structure
            and max(restore_deltas.values(), default=0.0) == 0.0
        ),
        "update_structure_exact": update_structure,
        "only_t216_negative_adapter_head_changes": (
            len(expert_deltas) == 2
            and all(value > 0.0 for value in expert_deltas.values())
            and bool(protected_deltas)
            and all(value == 0.0 for value in protected_deltas.values())
        ),
        "normalizer_bit_exact": (
            bool(normalizer_deltas)
            and all(value == 0.0 for value in normalizer_deltas.values())
        ),
        "every_reward_critic_leaf_changes": (
            bool(reward_critic_deltas)
            and all(value > 0.0 for value in reward_critic_deltas.values())
        ),
        "cost_critic_structure_exact": cost_structure,
        "every_cost_critic_leaf_changes": (
            bool(cost_deltas)
            and all(value > 0.0 for value in cost_deltas.values())
        ),
        "all_checkpoint_trees_finite": all(
            all(
                bool(np.all(np.isfinite(np.asarray(leaf))))
                for leaf in jax.tree_util.tree_leaves(tree)
            )
            for tree in (initial, final, initial_cost, final_cost)
        ),
        "initial_dual_state_exact": aux["0"] == initial_aux_expected,
        "final_dual_state_obeys_derived_branch": (
            (
                final_aux["initialized"] is False
                and float(final_aux["initial_cost"]) == 0.0
                and float(final_aux["eta"]) == 0.0
                and float(final_aux["lambda"]) == 0.0
            )
            or (
                final_aux["initialized"] is True
                and float(final_aux["initial_cost"]) > 0.0
                and math.isclose(
                    float(final_aux["eta"]),
                    eta_expected,
                    rel_tol=1.0e-6,
                    abs_tol=1.0e-9,
                )
                and math.isfinite(float(final_aux["lambda"]))
                and float(final_aux["lambda"]) > 0.0
            )
        ),
        "step_zero_raw_onnx_byte_exact": (
            engine.t20.sha256(source_graph)
            == engine.t20.sha256(graphs[0])
        ),
        "graph_abi_and_cpu_chain_exact": all(
            item["io"]["inputs"] == expected_io["inputs"]
            and item["io"]["outputs"] == expected_io["outputs"]
            and item["io"]["providers"][0] == "CPUExecutionProvider"
            and item["chain"]["finite"]
            and item["chain"]["steps"] == 256
            for item in graph_contracts.values()
        ),
        "runner_readbacks_exact": (
            prereg["expected_runner_readback"] in training_log
            and "T215B_AXIS_COMPLETE_TILT_COST=" in training_log
            and "Observation size: 115" in training_log
        ),
        "exact_command_scope": (
            command.count("--winner_t227_command_atom_bank") == 1
            and command[command.index("--ppo_num_envs") + 1] == "32"
            and command[command.index("--ppo_batch_size") + 1] == "32"
        ),
        "tilt_cost_and_dual_metrics_finite": all(
            t215b.finite_metric(events, tag)
            for tag in (
                "eval/episode_cost/t209_predicted_roll_risk",
                "training/winner_v127_batch_episode_cost",
                "training/winner_v127_dual_eta",
                "training/winner_v127_dual_lambda_after_update",
            )
        ),
        "legacy_reward_penalties_disabled": (
            command[
                command.index(
                    "--ground_up_peak_torque_exceedance_scale"
                )
                + 1
            ]
            == "0"
            and command[
                command.index(
                    "--ground_up_linear_peak_torque_exceedance_scale"
                )
                + 1
            ]
            == "0"
            and "--winner_t202_predicted_roll_risk" not in command
            and "--winner_t209_dual_roll_cost" not in command
        ),
        "artifact_span_at_most_1800_seconds": (
            artifact_span_seconds <= 1800.0
        ),
        "no_rerun_optimizer_simulator_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t227c_recovered_cpu_validation_result.v1"
        ),
        "status": (
            "PASS_T227C_RECOVERED_CPU_VALIDATION"
            if passed
            else "HOLD_T227C_RECOVERED_CPU_VALIDATION"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "mechanism": prereg["mechanism"],
        "recovery": {
            "classification": (
                "REPORT_ONLY_ENVIRONMENT_COUNTER_ALIAS"
            ),
            "training_rerun": False,
            "source_work": engine.t20.directory_receipt(work),
            "artifact_span_seconds": artifact_span_seconds,
            "environment_contract_transitions": environment[
                "simulator_prefix_transitions"
            ],
        },
        "training": {
            "command": command,
            "policy_checkpoints": {
                str(step): engine.t20.directory_receipt(path)
                for step, path in sorted(policy.items())
            },
            "cost_checkpoints": {
                str(step): engine.t20.directory_receipt(path)
                for step, path in sorted(cost.items())
            },
            "graphs": graph_contracts,
            "aux": aux,
            "event_file": engine.t20.receipt(events_path),
        },
        "tree_contract": {
            "source_remap_max_abs": max(
                remap_deltas.values(), default=0.0
            ),
            "step_zero_max_abs": max(
                restore_deltas.values(), default=0.0
            ),
            "trainable_head_leaf_deltas": expert_deltas,
            "protected_actor_leaf_deltas": protected_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "reward_critic_leaf_deltas": reward_critic_deltas,
            "cost_critic_leaf_deltas": cost_deltas,
        },
        "execution": {
            "saved_artifact_reads": len(artifact_files),
            "onnx_chain_inferences": 512,
            "optimizer_steps": 0,
            "simulator_transitions": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": engine.t20.canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T227C recovered CPU validation result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Recovery: existing T227B artifacts only; no training rerun\n"
        "- New optimizer / simulator / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
