#!/usr/bin/env python3
"""Run T77's preregistered endpoint-bank joint-adapter CPU contract."""

from __future__ import annotations

import json
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
import numpy as np
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402
import run_t66_endpoint_core_cpu_contract as t66  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t77_endpoint_joint_adapter_cpu_preregistration.json"
RESULT = ANALYSIS / "t77_endpoint_joint_adapter_cpu_result.json"
MARKDOWN = ANALYSIS / "T77_ENDPOINT_JOINT_ADAPTER_CPU_RESULT_20260728.md"
WORK = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t77_endpoint_joint_adapter_cpu_v1"
)
OUTPUT = WORK / "smoke"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
        or value.get("failed_checks") != []
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T77 preregistration identity changed")
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
        raise RuntimeError("T77 composed source inventory changed")


def training_command(
    *,
    python: Path,
    output: Path,
    reference: Path,
    restore: Path,
) -> list[str]:
    command = t66.training_command(
        python=python,
        output=output,
        reference=reference,
        restore=restore,
    )
    flag = "--winner_t66_endpoint_core_continuation"
    command[command.index(flag)] = (
        "--winner_t77_endpoint_joint_adapter_continuation"
    )
    return command


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def finite_tree(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def graph_contract(path: Path) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(path),
        providers=["CPUExecutionProvider"],
    )
    io = t20.graph_io(path)
    rng = np.random.default_rng(20260728)
    outputs = session.run(
        None,
        {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": rng.uniform(
                -1, 1, size=(1, 14)
            ).astype(np.float32),
            "h_in": rng.normal(size=(1, 64)).astype(np.float32),
        },
    )
    return {
        "receipt": t20.receipt(path),
        "io": io,
        "providers": session.get_providers(),
        "outputs_finite": all(np.isfinite(value).all() for value in outputs),
        "output_shapes": [list(value.shape) for value in outputs],
    }


def main() -> int:
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T77 result: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T77 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("formal T77 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    playground = Path(prereg["playground"]["path"])
    source_path = Path(prereg["assets"]["source_checkpoint"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    expected_raw = Path(prereg["assets"]["expected_step_zero_raw"]["path"])
    WORK.mkdir(parents=True)
    command = training_command(
        python=Path(sys.executable),
        output=OUTPUT,
        reference=reference,
        restore=source_path,
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
    log = WORK / "training.log"
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T77 CPU training failed rc={completed.returncode}\n"
            f"{completed.stdout[-16000:]}"
        )

    checkpoints = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in OUTPUT.iterdir()
        if path.is_dir()
    }
    graphs = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in OUTPUT.glob("*.onnx")
    }
    if sorted(checkpoints) != [0, 1024] or sorted(graphs) != [0, 1024]:
        raise RuntimeError(
            f"T77 export steps changed: {sorted(checkpoints)}, {sorted(graphs)}"
        )

    checkpointer = ocp.PyTreeCheckpointer()
    source = checkpointer.restore(str(source_path))
    initial = restore_tree(checkpoints[0], source)
    final = restore_tree(checkpoints[1024], source)
    restore_structure, restore_deltas = tree_errors(source, initial)
    update_structure, update_deltas = tree_errors(initial, final)
    policy_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("1/params/")
    }
    joint_adapter_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if any(
            group in name
            for group in prereg["mechanism"]["trainable_actor_groups"]
        )
    }
    frozen_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if name not in joint_adapter_deltas
    }
    critic_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("2/params/")
    }
    normalizer_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("0/")
    }
    graph_zero = graph_contract(graphs[0])
    graph_final = graph_contract(graphs[1024])
    expected_step_zero_hash = t20.sha256(expected_raw)
    runner_readback = (
        "T77_ENDPOINT_JOINT_ADAPTER_CONTINUATION="
        "strata=8,broad=1,isolated=7,"
        "actor_updates=recurrent_core_plus_output_head"
    )
    checks = {
        "command_exact_flags": (
            "--winner_t37_freeze_observation_normalizer" in command
            and "--winner_t77_endpoint_joint_adapter_continuation" in command
            and "--winner_t66_endpoint_core_continuation" not in command
            and command[command.index("--ppo_num_envs") + 1] == "8"
            and command[command.index("--ppo_batch_size") + 1] == "8"
        ),
        "runner_endpoint_readback_exact": runner_readback in completed.stdout,
        "source_restore_structure_exact": restore_structure,
        "source_restore_bit_exact": max(
            restore_deltas.values(), default=0.0
        ) == 0.0,
        "update_structure_exact": update_structure,
        "step_zero_raw_onnx_byte_exact": (
            graph_zero["receipt"]["sha256"] == expected_step_zero_hash
        ),
        "all_four_joint_adapter_groups_present": (
            all(
                any(group in name for name in joint_adapter_deltas)
                for group in prereg["mechanism"]["trainable_actor_groups"]
            )
        ),
        "every_joint_adapter_leaf_updated": (
            bool(joint_adapter_deltas)
            and all(delta > 0.0 for delta in joint_adapter_deltas.values())
        ),
        "every_base_actor_leaf_bit_exact": (
            bool(frozen_deltas)
            and all(delta == 0.0 for delta in frozen_deltas.values())
        ),
        "normalizer_bit_exact": (
            bool(normalizer_deltas)
            and all(delta == 0.0 for delta in normalizer_deltas.values())
        ),
        "every_critic_leaf_updated": (
            bool(critic_deltas)
            and all(delta > 0.0 for delta in critic_deltas.values())
        ),
        "trees_finite": finite_tree(initial) and finite_tree(final),
        "step_zero_graph_contract": (
            graph_zero["providers"][0] == "CPUExecutionProvider"
            and graph_zero["outputs_finite"]
            and graph_zero["output_shapes"] == [[1, 14], [1, 14], [1, 64]]
        ),
        "step_1024_graph_contract": (
            graph_final["providers"][0] == "CPUExecutionProvider"
            and graph_final["outputs_finite"]
            and graph_final["output_shapes"] == [[1, 14], [1, 14], [1, 64]]
        ),
        "no_behavior_hosted_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t77_endpoint_joint_adapter_cpu_result.v1"
        ),
        "status": (
            "PASS_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
            if passed
            else "HOLD_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "log": t20.receipt(log),
            "initial_checkpoint": t20.directory_receipt(checkpoints[0]),
            "final_checkpoint": t20.directory_receipt(checkpoints[1024]),
            "graphs": {
                "0": graph_zero,
                "1024": graph_final,
            },
        },
        "tree_contract": {
            "source": t20.directory_receipt(source_path),
            "source_restore_maximum_abs_error": max(
                restore_deltas.values(), default=0.0
            ),
            "joint_adapter_actor_leaf_deltas": joint_adapter_deltas,
            "frozen_base_actor_leaf_deltas": frozen_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "critic_leaf_deltas": critic_deltas,
        },
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 1024,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = t20.canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T77 endpoint joint-adapter CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Joint-adapter actor leaves: "
                    f"`{len(joint_adapter_deltas)}`"
                ),
                f"- Frozen base actor leaves: `{len(frozen_deltas)}`",
                f"- Critic leaves: `{len(critic_deltas)}`",
                "- CPU steps / behavior / hosted / robot: `1024/0/0/0`",
                "",
                "A pass earns only a separate hosted-run preregistration.",
                "",
            ]
        ),
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
