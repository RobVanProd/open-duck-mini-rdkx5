#!/usr/bin/env python3
"""Run T55's materialization and two-stage CPU-only smoke contract."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
from orbax import checkpoint as ocp
from tensorboardX.proto.event_pb2 import Event


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import (  # noqa: E402
    tree_errors,
)


PREREGISTRATION = (
    ANALYSIS / "t55_dynamic_single_support_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t55_dynamic_single_support_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "T55_DYNAMIC_SINGLE_SUPPORT_CPU_RESULT_20260728.md"
)
BASE_GROUPS = ("residual_trunk", "residual_location")
STAGES = ("balance", "transfer")


def validate_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
        or value.get("failed_checks") != []
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T55 preregistration identity changed")
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
        raise RuntimeError("T55 composed source inventory changed")


def materialize_source(
    half_path: Path,
    final_path: Path,
    template_path: Path,
    output_path: Path,
) -> tuple[Any, dict[str, Any]]:
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(template_path))
    restore_args = orbax_utils.restore_args_from_target(template)
    half = checkpointer.restore(
        str(half_path),
        item=template,
        restore_args=restore_args,
    )
    final = checkpointer.restore(
        str(final_path),
        item=template,
        restore_args=restore_args,
    )
    materialized = copy.deepcopy(half)
    for group in BASE_GROUPS:
        materialized[1]["params"][group] = copy.deepcopy(
            final[1]["params"][group]
        )
    checkpointer.save(
        str(output_path),
        materialized,
        save_args=orbax_utils.save_args_from_target(materialized),
    )
    restored = checkpointer.restore(
        str(output_path),
        item=materialized,
        restore_args=orbax_utils.restore_args_from_target(materialized),
    )
    restored_structure, restored_deltas = tree_errors(
        materialized,
        restored,
    )
    half_structure, half_deltas = tree_errors(half, materialized)
    final_structure, final_deltas = tree_errors(final, materialized)
    changed_from_half = sorted(
        name for name, delta in half_deltas.items() if delta > 0.0
    )
    unchanged_from_half = sorted(
        name for name, delta in half_deltas.items() if delta == 0.0
    )
    return materialized, {
        "half": t20.directory_receipt(half_path),
        "final": t20.directory_receipt(final_path),
        "template": t20.directory_receipt(template_path),
        "materialized": t20.directory_receipt(output_path),
        "restore_structure_exact": restored_structure,
        "restore_maximum_abs_error": max(
            restored_deltas.values(),
            default=0.0,
        ),
        "half_structure_exact": half_structure,
        "final_structure_exact": final_structure,
        "changed_from_half": changed_from_half,
        "unchanged_from_half": unchanged_from_half,
        "base_leaf_deltas_from_final": {
            name: delta
            for name, delta in final_deltas.items()
            if name.startswith("1/params/residual_trunk/")
            or name.startswith("1/params/residual_location/")
        },
    }


def training_command(
    *,
    python: Path,
    output: Path,
    reference: Path,
    restore: Path,
    stage: str,
) -> list[str]:
    if stage not in STAGES:
        raise ValueError(stage)
    command = t31.training_command(
        python=python,
        output=output,
        reference=reference,
        restore=restore,
    )
    index = command.index("--critic_observation")
    command[index:index] = [f"--winner_t55_{stage}_stage"]
    return command


def cpu_environment(playground: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONPATH": str(playground),
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
            "JAX_COMPILATION_CACHE_DIR": str(
                Path(
                    "D:/CodexArtifacts/open-duck-policy/"
                    "jax_compilation_cache"
                )
            ),
        }
    )
    return environment


def run_training_stage(
    *,
    stage: str,
    playground: Path,
    output: Path,
    reference: Path,
    restore: Path,
    work: Path,
) -> dict[str, Any]:
    output.mkdir()
    command = training_command(
        python=Path(sys.executable),
        output=output,
        reference=reference,
        restore=restore,
        stage=stage,
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
    log = work / f"{stage}_training.log"
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T55 {stage} CPU runner failed rc={completed.returncode}\n"
            f"{completed.stdout[-12000:]}"
        )
    checkpoints = sorted(path for path in output.iterdir() if path.is_dir())
    graphs = sorted(output.glob("*.onnx"))
    checkpoint_by_step = {
        int(path.name.rsplit("_", 1)[1]): path for path in checkpoints
    }
    graph_by_step = {
        int(path.stem.rsplit("_", 1)[1]): path for path in graphs
    }
    if sorted(checkpoint_by_step) != [0, 1024] or sorted(graph_by_step) != [
        0,
        1024,
    ]:
        raise RuntimeError(
            f"T55 {stage} export steps changed: "
            f"{sorted(checkpoint_by_step)}, {sorted(graph_by_step)}"
        )
    return {
        "stage": stage,
        "command": command,
        "elapsed_seconds": elapsed,
        "log": t20.receipt(log),
        "checkpoint_by_step": checkpoint_by_step,
        "graph_by_step": graph_by_step,
        "event_file": next(output.glob("events.out.tfevents*")),
    }


def all_scalar_events(path: Path) -> dict[str, list[dict[str, float | int]]]:
    rows: dict[str, list[dict[str, float | int]]] = {}
    with path.open("rb") as stream:
        while True:
            length_bytes = stream.read(8)
            if not length_bytes:
                break
            if len(length_bytes) != 8:
                raise ValueError("truncated TensorBoard event length")
            length = struct.unpack("<Q", length_bytes)[0]
            stream.read(4)
            payload = stream.read(length)
            stream.read(4)
            event = Event()
            event.ParseFromString(payload)
            if not event.HasField("summary"):
                continue
            for value in event.summary.value:
                rows.setdefault(value.tag, []).append(
                    {
                        "step": int(event.step),
                        "value": float(value.simple_value),
                    }
                )
    return rows


def stage_tree_contract(
    stage: dict[str, Any],
    source_tree: Any,
) -> tuple[Any, dict[str, Any]]:
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(source_tree)
    initial = checkpointer.restore(
        str(stage["checkpoint_by_step"][0]),
        item=source_tree,
        restore_args=restore_args,
    )
    final = checkpointer.restore(
        str(stage["checkpoint_by_step"][1024]),
        item=source_tree,
        restore_args=restore_args,
    )
    restore_structure, restore_deltas = tree_errors(source_tree, initial)
    update_structure, update_deltas = tree_errors(initial, final)
    policy_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("1/params/")
    }
    critic_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("2/params/")
    }
    finite = all(
        np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(final)
    )
    return final, {
        "initial_checkpoint": t20.directory_receipt(
            stage["checkpoint_by_step"][0]
        ),
        "final_checkpoint": t20.directory_receipt(
            stage["checkpoint_by_step"][1024]
        ),
        "event_file": t20.receipt(stage["event_file"]),
        "source_restore_structure_exact": restore_structure,
        "source_restore_maximum_abs_error": max(
            restore_deltas.values(),
            default=0.0,
        ),
        "update_structure_exact": update_structure,
        "tree_finite": bool(finite),
        "policy_leaf_deltas": policy_deltas,
        "critic_leaf_deltas": critic_deltas,
        "all_policy_leaves_updated": (
            bool(policy_deltas)
            and all(delta > 0.0 for delta in policy_deltas.values())
        ),
        "all_critic_leaves_updated": (
            bool(critic_deltas)
            and all(delta > 0.0 for delta in critic_deltas.values())
        ),
        "events": all_scalar_events(stage["event_file"]),
    }


def run_default_off_worker(
    *,
    playground: Path,
    reference: Path,
    output: Path,
) -> dict[str, Any]:
    script = TOOLS / "run_t19_support_trainthrough_cpu_contract.py"
    command = [
        sys.executable,
        str(script),
        "--worker",
        "default_off",
        "--playground",
        str(playground),
        "--reference",
        str(reference),
        "--env-count",
        "1",
        "--seed",
        "100",
        "--worker-output",
        str(output),
    ]
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
    if completed.returncode != 0:
        raise RuntimeError(
            f"T55 default-off worker failed for {playground}\n"
            f"{completed.stdout[-12000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def positive_finite_metric(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> bool:
    values = events.get(tag, [])
    return bool(values) and all(
        math.isfinite(float(row["value"])) for row in values
    ) and max(float(row["value"]) for row in values) > 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T55 formal CPU contract requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T55 path: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(prereg)
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T55 execution requires a clean worktree")

    work = args.work_root.resolve()
    work.mkdir(parents=True)
    materialized_path = work / "t52_half_materialized_checkpoint"
    materialized, materialization = materialize_source(
        Path(prereg["assets"]["t32_half_checkpoint"]["path"]),
        Path(prereg["assets"]["t32_final_checkpoint"]["path"]),
        Path(prereg["assets"]["cpu_topology_template"]["path"]),
        materialized_path,
    )
    playground = Path(prereg["playground"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    balance = run_training_stage(
        stage="balance",
        playground=playground,
        output=work / "balance_smoke",
        reference=reference,
        restore=materialized_path,
        work=work,
    )
    balance_final, balance_contract = stage_tree_contract(
        balance,
        materialized,
    )
    transfer = run_training_stage(
        stage="transfer",
        playground=playground,
        output=work / "transfer_smoke",
        reference=reference,
        restore=balance["checkpoint_by_step"][1024],
        work=work,
    )
    _, transfer_contract = stage_tree_contract(
        transfer,
        balance_final,
    )
    deployments = {
        "materialized": t31.deployment_graph(
            balance["graph_by_step"][0],
            work / "deployment" / "materialized",
        ),
        "balance_1024": t31.deployment_graph(
            balance["graph_by_step"][1024],
            work / "deployment" / "balance_1024",
        ),
        "transfer_1024": t31.deployment_graph(
            transfer["graph_by_step"][1024],
            work / "deployment" / "transfer_1024",
        ),
    }
    base_default = run_default_off_worker(
        playground=Path(prereg["playground"]["base_path"]),
        reference=reference,
        output=work / "base_default_off.json",
    )
    composed_default = run_default_off_worker(
        playground=playground,
        reference=reference,
        output=work / "composed_default_off.json",
    )
    balance_events = balance_contract["events"]
    transfer_events = transfer_contract["events"]
    left_tag = "eval/episode_reward/t55_left_support_match"
    right_tag = "eval/episode_reward/t55_right_support_match"
    balance_tag = "eval/episode_reward/t55_single_support_balance"
    reward_tag = "eval/episode_reward"
    deployment_contracts_green = all(
        row["margin_contract"]["pass"]
        and row["context_parity"]["all_outputs_bit_exact"]
        and row["verification"]["previous_action_out_equals_action_bit_exact"]
        and row["verification"]["output_bounds_exact"]
        for row in deployments.values()
    )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "materialized_restore_exact": (
            materialization["restore_structure_exact"]
            and materialization["restore_maximum_abs_error"] == 0.0
        ),
        "materialized_changes_exactly_actor_base": (
            materialization["changed_from_half"]
            and all(
                name.startswith("1/params/residual_trunk/")
                or name.startswith("1/params/residual_location/")
                for name in materialization["changed_from_half"]
            )
            and all(
                delta == 0.0
                for delta in materialization[
                    "base_leaf_deltas_from_final"
                ].values()
            )
        ),
        "materialized_deployment_byte_exact_t52_half": (
            deployments["materialized"]["wrapped"]["sha256"]
            == prereg["assets"]["t52_half_policy"]["sha256"]
        ),
        "default_off_trajectory_bit_exact": (
            base_default["trajectory_digests"]
            == composed_default["trajectory_digests"]
        ),
        "default_off_shapes_and_finiteness_exact": (
            base_default["observation_shape"]
            == composed_default["observation_shape"]
            == [115]
            and base_default["finite"]
            and composed_default["finite"]
        ),
        "balance_source_restore_exact": (
            balance_contract["source_restore_structure_exact"]
            and balance_contract["source_restore_maximum_abs_error"] == 0.0
        ),
        "transfer_source_restore_exact": (
            transfer_contract["source_restore_structure_exact"]
            and transfer_contract["source_restore_maximum_abs_error"] == 0.0
        ),
        "balance_all_actor_and_critic_leaves_update": (
            balance_contract["all_policy_leaves_updated"]
            and balance_contract["all_critic_leaves_updated"]
        ),
        "transfer_all_actor_and_critic_leaves_update": (
            transfer_contract["all_policy_leaves_updated"]
            and transfer_contract["all_critic_leaves_updated"]
        ),
        "both_stage_trees_finite": (
            balance_contract["tree_finite"]
            and transfer_contract["tree_finite"]
        ),
        "balance_stage_exercises_both_support_sides": (
            positive_finite_metric(balance_events, left_tag)
            and positive_finite_metric(balance_events, right_tag)
        ),
        "transfer_stage_exercises_both_support_sides": (
            positive_finite_metric(transfer_events, left_tag)
            and positive_finite_metric(transfer_events, right_tag)
        ),
        "both_stage_balance_metrics_nonzero_and_finite": (
            positive_finite_metric(balance_events, balance_tag)
            and positive_finite_metric(transfer_events, balance_tag)
        ),
        "both_stage_reward_metrics_finite": (
            positive_finite_metric(balance_events, reward_tag)
            and positive_finite_metric(transfer_events, reward_tag)
        ),
        "commands_use_exact_mutually_exclusive_stages": (
            "--winner_t55_balance_stage" in balance["command"]
            and "--winner_t55_transfer_stage" not in balance["command"]
            and "--winner_t55_transfer_stage" in transfer["command"]
            and "--winner_t55_balance_stage" not in transfer["command"]
        ),
        "all_deployment_contracts_green": deployment_contracts_green,
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
        "robot_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t55_dynamic_single_support_cpu_result.v1"
        ),
        "status": (
            "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            if not failed
            else "HOLD_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
        ),
        "decision": (
            "EARN_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PREREGISTRATION"
            if not failed
            else "CLOSE_T55_WITHOUT_HOSTED_TRAINING"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "materialization": materialization,
        "default_off": {
            "base": base_default,
            "composed": composed_default,
        },
        "stages": {
            "balance": {
                "command": balance["command"],
                "elapsed_seconds": balance["elapsed_seconds"],
                **balance_contract,
            },
            "transfer": {
                "command": transfer["command"],
                "elapsed_seconds": transfer["elapsed_seconds"],
                **transfer_contract,
            },
        },
        "deployments": deployments,
        "execution": {
            "cpu_simulator_steps": 2048,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": not failed,
            "hosted_training": False,
            "behavior_matrix": False,
            "checkpoint_selection": False,
            "policy_deployment": False,
            "gate5": False,
            "robot_or_rdk": False,
            "torque_or_motion": False,
        },
    }
    value = {
        **result_basis,
        "result_sha256": t20.canonical_sha256(result_basis),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T55 dynamic single-support CPU result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- CPU steps / hosted / robot: `2,048 / 0 / 0`",
                "- Materialized source must be byte-exact to T52-half",
                "- Default-off T31/T55 trajectory must be bit-exact",
                "- Both curriculum stages must exercise left and right support",
                "",
                "A pass authorizes only a separate hosted preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
