#!/usr/bin/env python3
"""Run T209's default-off, enabled, and 1,024-step CPU contract."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
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

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
import run_t112_always_on_trainthrough_cpu_contract as t112  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t209_dual_roll_cost_cpu_preregistration.json"
RESULT = ANALYSIS / "t209_dual_roll_cost_cpu_result.json"
MARKDOWN = ANALYSIS / "T209_DUAL_ROLL_COST_CPU_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t209_dual_roll_cost_cpu_contract_v1"
)
EXTRA_HEAD = "negative_adapter_location"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T209_DUAL_ROLL_COST_CPU_CONTRACT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T209 preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        t20.verify_receipt(item, name)
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): t20.sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T209 composed playground changed")


def cpu_environment(playground: Path) -> dict[str, str]:
    value = t55.cpu_environment(playground)
    value["PYTHONPATH"] = str(playground)
    return value


def run_worker(
    *,
    mode: str,
    playground: Path,
    reference: Path,
    source_onnx: Path,
    output: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(TOOLS / "run_t209_environment_contract_worker.py"),
        "--mode",
        mode,
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--output",
        str(output),
    ]
    if mode == "enabled":
        command.extend(
            [
                "--source-onnx",
                str(source_onnx),
                "--ticks",
                "108",
                "--seed",
                "209",
            ]
        )
    completed = subprocess.run(
        command,
        cwd=playground,
        env=cpu_environment(playground),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    output.with_suffix(".log").write_text(
        completed.stdout, encoding="utf-8", newline="\n"
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T209 {mode} worker failed\n{completed.stdout[-20000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def training_command(
    *,
    playground: Path,
    output: Path,
    restore: Path,
    reference: Path,
    gate_asset: Path,
) -> list[str]:
    command = t98.training_command(
        python=Path(sys.executable),
        playground=playground,
        output=output,
        reference=reference,
        restore=restore,
        gate_asset=gate_asset,
    )
    anchor = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[anchor:anchor] = [
        "--winner_v127_constrained_cost",
        "--winner_t209_dual_roll_cost",
    ]
    for flag in (
        "--ground_up_peak_torque_exceedance_scale",
        "--ground_up_linear_peak_torque_exceedance_scale",
    ):
        command[command.index(flag) + 1] = "0"
    return command


def finite_metric(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> bool:
    values = events.get(tag, [])
    return bool(values) and all(
        math.isfinite(float(row["value"])) for row in values
    )


def restore_like(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.cpu_contract_authorized:
        raise PermissionError("T209 requires --cpu-contract-authorized")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T209: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T209 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)

    work = WORK
    output = work / "smoke"
    cpu_source = work / "t203_half_cpu_remap"
    work.mkdir(parents=True)
    output.mkdir()
    playground = Path(prereg["playground"]["path"])
    base_playground = Path(prereg["playground"]["base_path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    source_path = Path(prereg["assets"]["source_checkpoint"]["path"])
    source_graph = Path(prereg["assets"]["source_raw_onnx"]["path"])
    topology = Path(prereg["assets"]["cpu_topology_template"]["path"])
    gate_asset = Path(
        prereg["assets"]["hidden_gate_static_asset"]["path"]
    )

    base_default = run_worker(
        mode="default_off",
        playground=base_playground,
        reference=reference,
        source_onnx=source_graph,
        output=work / "base_default_off.json",
    )
    composed_default = run_worker(
        mode="default_off",
        playground=playground,
        reference=reference,
        source_onnx=source_graph,
        output=work / "composed_default_off.json",
    )
    enabled = run_worker(
        mode="enabled",
        playground=playground,
        reference=reference,
        source_onnx=source_graph,
        output=work / "enabled_contract.json",
    )

    sys.path.insert(0, str(playground))
    from playground.common.winner_v127_constrained_ppo_train import (  # noqa: E402
        winner_v127_dual_update,
    )

    total_iterations = 16
    quarter_iterations = 4
    dual = jax.numpy.asarray(0.0)
    eta = jax.numpy.asarray(0.0)
    initial_cost = jax.numpy.asarray(0.0)
    initialized = jax.numpy.asarray(False)
    dual, eta, initial_cost, initialized = winner_v127_dual_update(
        dual,
        eta,
        initial_cost,
        initialized,
        jax.numpy.asarray(0.0),
        quarter_iterations,
    )
    synthetic_zero = {
        "lambda": float(dual),
        "eta": float(eta),
        "initial_cost": float(initial_cost),
        "initialized": bool(initialized),
    }
    persistent = []
    for _ in range(quarter_iterations):
        dual, eta, initial_cost, initialized = winner_v127_dual_update(
            dual,
            eta,
            initial_cost,
            initialized,
            jax.numpy.asarray(2.5),
            quarter_iterations,
        )
        persistent.append(float(dual))
    synthetic_positive = {
        "lambda": float(dual),
        "eta": float(eta),
        "initial_cost": float(initial_cost),
        "initialized": bool(initialized),
        "trajectory": persistent,
    }

    t112.CPU_SOURCE = cpu_source
    source, remap = t112.cpu_remap(source_path, topology)
    command = training_command(
        playground=playground,
        output=output,
        restore=cpu_source,
        reference=reference,
        gate_asset=gate_asset,
    )
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=cpu_environment(playground),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    elapsed = time.monotonic() - started
    log = work / "training.log"
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T209 CPU training failed rc={completed.returncode}\n"
            f"{completed.stdout[-20000:]}"
        )

    policy_checkpoints = [
        path
        for path in output.iterdir()
        if path.is_dir() and "_v127_cost_value" not in path.name
    ]
    cost_checkpoints = list(output.glob("*_v127_cost_value"))
    graphs = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in output.glob("*.onnx")
    }
    policy = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in policy_checkpoints
    }
    cost = {
        int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]): path
        for path in cost_checkpoints
    }
    aux_paths = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in output.glob("*_v127_aux.json")
    }
    expected_steps = [0, 1024]
    if not (
        sorted(policy) == expected_steps
        and sorted(cost) == expected_steps
        and sorted(graphs) == expected_steps
        and sorted(aux_paths) == expected_steps
    ):
        raise RuntimeError("T209 export sets changed")

    initial = t98.restore_tree(policy[0], source)
    final = t98.restore_tree(policy[1024], source)
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

    events = t55.all_scalar_events(
        next(output.glob("events.out.tfevents*"))
    )
    graph_contracts = {
        str(step): {
            "receipt": t20.receipt(path),
            "io": t98.graph_io(path),
            "chain": t98.graph_chain(path),
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
    final_aux = aux["1024"]
    final_eta_expected = (
        1.0
        / (
            float(final_aux["quarter_iterations"])
            * float(final_aux["initial_cost"])
        )
        if final_aux["initialized"]
        else 0.0
    )
    initial_aux_expected = {
        "eta": 0.0,
        "initial_cost": 0.0,
        "initialized": False,
        "lambda": 0.0,
        "quarter_iterations": quarter_iterations,
        "step": 0,
        "total_training_iterations": total_iterations,
    }
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "default_off_trajectory_bit_exact": (
            base_default["trajectory_digests"]
            == composed_default["trajectory_digests"]
        ),
        "default_off_observation_abi_and_finiteness_exact": (
            base_default["observation_shape"]
            == composed_default["observation_shape"]
            == [115]
            and base_default["finite"]
            and composed_default["finite"]
        ),
        "enabled_environment_contract_green": (
            enabled["failed_checks"] == []
            and all(enabled["checks"].values())
        ),
        "synthetic_zero_cost_leaves_dual_uninitialized": (
            synthetic_zero
            == {
                "lambda": 0.0,
                "eta": 0.0,
                "initial_cost": 0.0,
                "initialized": False,
            }
        ),
        "synthetic_first_positive_cost_initializes_derived_eta": (
            synthetic_positive["initialized"]
            and synthetic_positive["initial_cost"] == 2.5
            and math.isclose(
                synthetic_positive["eta"],
                1.0 / (quarter_iterations * 2.5),
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
        "synthetic_persistent_cost_reaches_one_by_quarter": math.isclose(
            persistent[-1], 1.0, rel_tol=1.0e-6, abs_tol=1.0e-7
        ),
        "source_cpu_remap_exact": (
            remap["structure_exact"]
            and remap["maximum_abs_error"] == 0.0
            and remap["tree_finite"]
        ),
        "step_zero_tree_exact": (
            restore_structure
            and max(restore_deltas.values(), default=0.0) == 0.0
        ),
        "update_structure_exact": update_structure,
        "only_t203_negative_adapter_head_changes": (
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
        "all_checkpoint_trees_finite": (
            t112.finite_tree(initial)
            and t112.finite_tree(final)
            and t112.finite_tree(initial_cost)
            and t112.finite_tree(final_cost)
        ),
        "initial_dual_state_exact": aux["0"] == initial_aux_expected,
        "smoke_dual_state_obeys_zero_or_initialized_branch": (
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
                    final_eta_expected,
                    rel_tol=1.0e-6,
                    abs_tol=1.0e-9,
                )
                and math.isfinite(float(final_aux["lambda"]))
                and float(final_aux["lambda"]) > 0.0
            )
        ),
        "step_zero_raw_onnx_byte_exact": (
            t20.sha256(source_graph) == t20.sha256(graphs[0])
        ),
        "graph_abi_and_cpu_chain_exact": all(
            item["io"]["inputs"] == expected_io["inputs"]
            and item["io"]["outputs"] == expected_io["outputs"]
            and item["io"]["providers"][0] == "CPUExecutionProvider"
            and item["chain"]["finite"]
            and item["chain"]["steps"] == 256
            for item in graph_contracts.values()
        ),
        "runner_readback_exact": (
            prereg["expected_runner_readback"] in completed.stdout
        ),
        "roll_cost_and_dual_metrics_finite": all(
            finite_metric(events, tag)
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
        ),
        "no_formal_behavior_hosted_or_hardware": True,
        "wall_seconds_at_most_1800": elapsed <= 1800,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t209_dual_roll_cost_cpu_result.v1",
        "status": (
            "PASS_T209_DUAL_ROLL_COST_CPU_CONTRACT"
            if passed
            else "HOLD_T209_DUAL_ROLL_COST_CPU_CONTRACT"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "environment_contract": enabled,
        "default_off": {
            "base": base_default,
            "composed": composed_default,
        },
        "dual_unit_contract": {
            "zero": synthetic_zero,
            "positive": synthetic_positive,
        },
        "source_remap": remap,
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "log": t20.receipt(log),
            "policy_checkpoints": {
                str(step): t20.directory_receipt(path)
                for step, path in sorted(policy.items())
            },
            "cost_checkpoints": {
                str(step): t20.directory_receipt(path)
                for step, path in sorted(cost.items())
            },
            "graphs": graph_contracts,
            "aux": aux,
            "event_file": t20.receipt(
                next(output.glob("events.out.tfevents*"))
            ),
        },
        "tree_contract": {
            "trainable_head_leaf_deltas": expert_deltas,
            "protected_actor_leaf_deltas": protected_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "reward_critic_leaf_deltas": reward_critic_deltas,
            "cost_critic_leaf_deltas": cost_deltas,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 1024,
            "environment_contract_transitions": enabled[
                "simulator_transitions"
            ],
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = t20.canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T209 dual roll-cost CPU result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- Final dual lambda / eta: "
        f"`{final_aux['lambda']}` / `{final_aux['eta']}`\n"
        "- Optimizer / formal behavior / hosted / robot: "
        "`1024 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
