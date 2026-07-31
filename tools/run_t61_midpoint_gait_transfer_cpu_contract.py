#!/usr/bin/env python3
"""Run T61's midpoint-to-full transfer CPU-only smoke contract."""

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

from flax.training import orbax_utils
import jax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402


PREREGISTRATION = (
    ANALYSIS
    / "t61_midpoint_gait_transfer_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t61_midpoint_gait_transfer_cpu_result.json"
MARKDOWN = (
    ANALYSIS / "T61_MIDPOINT_GAIT_TRANSFER_CPU_RESULT_20260728.md"
)
STAGES = ("midpoint", "transfer")


def validate_preregistration(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
        or value.get("failed_checks") != []
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T61 preregistration identity changed")
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
        raise RuntimeError("T61 composed source inventory changed")


def training_command(
    *,
    output: Path,
    reference: Path,
    restore: Path,
    stage: str,
) -> list[str]:
    if stage not in STAGES:
        raise ValueError(stage)
    source_stage = "transfer"
    command = t55.training_command(
        python=Path(sys.executable),
        output=output,
        reference=reference,
        restore=restore,
        stage=source_stage,
    )
    if stage == "midpoint":
        index = command.index("--winner_t55_transfer_stage")
        command[index] = "--winner_t61_midpoint_transfer_stage"
    return command


def run_stage(
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
        output=output,
        reference=reference,
        restore=restore,
        stage=stage,
    )
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=t55.cpu_environment(playground),
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
            f"T61 {stage} CPU runner failed rc={completed.returncode}\n"
            f"{completed.stdout[-12000:]}"
        )
    checkpoint_by_step = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in sorted(
            candidate for candidate in output.iterdir()
            if candidate.is_dir()
        )
    }
    graph_by_step = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in sorted(output.glob("*.onnx"))
    }
    if sorted(checkpoint_by_step) != [0, 1024] or sorted(
        graph_by_step
    ) != [0, 1024]:
        raise RuntimeError(
            f"T61 {stage} export steps changed: "
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
        raise SystemExit("T61 formal CPU contract requires --execute")
    for path in (RESULT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T61 path: {path}")
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(prereg)
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T61 execution requires a clean worktree")

    work = args.work_root.resolve()
    work.mkdir(parents=True)
    playground = Path(prereg["playground"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    source_path = Path(
        prereg["assets"]["t56_balance_final_checkpoint"]["path"]
    )
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(
        prereg["assets"]["cpu_topology_template"]["path"]
    )
    source_tree = checkpointer.restore(
        str(source_path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )

    midpoint = run_stage(
        stage="midpoint",
        playground=playground,
        output=work / "midpoint_smoke",
        reference=reference,
        restore=source_path,
        work=work,
    )
    midpoint_final, midpoint_contract = t55.stage_tree_contract(
        midpoint,
        source_tree,
    )
    transfer = run_stage(
        stage="transfer",
        playground=playground,
        output=work / "transfer_smoke",
        reference=reference,
        restore=midpoint["checkpoint_by_step"][1024],
        work=work,
    )
    _, transfer_contract = t55.stage_tree_contract(
        transfer,
        midpoint_final,
    )
    deployments = {
        "source": t31.deployment_graph(
            midpoint["graph_by_step"][0],
            work / "deployment" / "source",
        ),
        "midpoint_1024": t31.deployment_graph(
            midpoint["graph_by_step"][1024],
            work / "deployment" / "midpoint_1024",
        ),
        "transfer_1024": t31.deployment_graph(
            transfer["graph_by_step"][1024],
            work / "deployment" / "transfer_1024",
        ),
    }
    base_default = t55.run_default_off_worker(
        playground=Path(prereg["playground"]["base_path"]),
        reference=reference,
        output=work / "base_default_off.json",
    )
    composed_default = t55.run_default_off_worker(
        playground=playground,
        reference=reference,
        output=work / "composed_default_off.json",
    )
    midpoint_events = midpoint_contract["events"]
    transfer_events = transfer_contract["events"]
    left_tag = "eval/episode_reward/t55_left_support_match"
    right_tag = "eval/episode_reward/t55_right_support_match"
    support_tag = "eval/episode_reward/t55_single_support_balance"
    reward_tag = "eval/episode_reward"
    deployment_contracts_green = all(
        row["margin_contract"]["pass"]
        and row["context_parity"]["all_outputs_bit_exact"]
        and row["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and row["verification"]["output_bounds_exact"]
        for row in deployments.values()
    )
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "midpoint_source_restore_exact": (
            midpoint_contract["source_restore_structure_exact"]
            and midpoint_contract["source_restore_maximum_abs_error"] == 0.0
        ),
        "transfer_source_restore_exact": (
            transfer_contract["source_restore_structure_exact"]
            and transfer_contract["source_restore_maximum_abs_error"] == 0.0
        ),
        "midpoint_step_zero_onnx_byte_exact_source": (
            t20.sha256(midpoint["graph_by_step"][0])
            == prereg["assets"]["t56_balance_final_onnx"]["sha256"]
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
        "midpoint_all_actor_and_critic_leaves_update": (
            midpoint_contract["all_policy_leaves_updated"]
            and midpoint_contract["all_critic_leaves_updated"]
        ),
        "transfer_all_actor_and_critic_leaves_update": (
            transfer_contract["all_policy_leaves_updated"]
            and transfer_contract["all_critic_leaves_updated"]
        ),
        "both_stage_trees_finite": (
            midpoint_contract["tree_finite"]
            and transfer_contract["tree_finite"]
        ),
        "midpoint_exercises_both_support_sides": (
            positive_finite_metric(midpoint_events, left_tag)
            and positive_finite_metric(midpoint_events, right_tag)
        ),
        "transfer_exercises_both_support_sides": (
            positive_finite_metric(transfer_events, left_tag)
            and positive_finite_metric(transfer_events, right_tag)
        ),
        "both_stage_support_metrics_nonzero_and_finite": (
            positive_finite_metric(midpoint_events, support_tag)
            and positive_finite_metric(transfer_events, support_tag)
        ),
        "both_stage_reward_metrics_nonzero_and_finite": (
            positive_finite_metric(midpoint_events, reward_tag)
            and positive_finite_metric(transfer_events, reward_tag)
        ),
        "commands_use_exact_mutually_exclusive_stages": (
            "--winner_t61_midpoint_transfer_stage" in midpoint["command"]
            and "--winner_t55_transfer_stage" not in midpoint["command"]
            and "--winner_t55_balance_stage" not in midpoint["command"]
            and "--winner_t55_transfer_stage" in transfer["command"]
            and "--winner_t61_midpoint_transfer_stage"
            not in transfer["command"]
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
            "open_duck.t61_midpoint_gait_transfer_cpu_result.v1"
        ),
        "status": (
            "PASS_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
            if not failed
            else "HOLD_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
        ),
        "decision": (
            "EARN_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION"
            if not failed
            else "CLOSE_T61_WITHOUT_HOSTED_TRAINING"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "default_off": {
            "base": base_default,
            "composed": composed_default,
        },
        "stages": {
            "midpoint": {
                "command": midpoint["command"],
                "elapsed_seconds": midpoint["elapsed_seconds"],
                **midpoint_contract,
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
                "# T61 midpoint gait-transfer CPU result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Failed checks: `{failed}`",
                "- CPU steps / hosted / robot: `2,048 / 0 / 0`",
                "- Source: exact recovered T56 balance-final checkpoint",
                "- Midpoint: fixed 0.5 locomotion weight",
                "- Default-off T55/T61 trajectory must be bit-exact",
                "- Both stages must exercise left and right support",
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
