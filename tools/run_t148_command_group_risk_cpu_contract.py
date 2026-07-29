#!/usr/bin/env python3
"""Run T148's integrated command-group-risk CPU contract."""

from __future__ import annotations

import argparse
import json
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

import numpy as np
from tensorboardX.proto.event_pb2 import Event


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
import run_t109_always_on_expert_transform as t109  # noqa: E402
import run_t112_always_on_trainthrough_cpu_contract as t112  # noqa: E402
import run_t128_negative_only_expert_cpu_contract as t128  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t148_command_group_risk_cpu_preregistration.json"
RESULT = ANALYSIS / "t148_command_group_risk_cpu_result.json"
MARKDOWN = ANALYSIS / "T148_COMMAND_GROUP_RISK_CPU_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t148_command_group_risk_cpu_v1"
)
CPU_SOURCE = WORK / "t100c_half_cpu_remap"
OUTPUT = WORK / "smoke"
INSPECTION = WORK / "inspection"
EXPECTED = WORK / "t100c_half_expected_always_on.onnx"
EXTRA_HEAD = "negative_adapter_location"
READBACK = (
    "T147_COMMAND_GROUP_RISK="
    "anchors=.074,.077,.080,boundaries=.0755,.0785,"
    "actor_loss=max_group_clipped_surrogate,"
    "advantage=global,critic=unchanged,entropy=unchanged,"
    "optimizer=unchanged,abi=unchanged"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T148 preregistration identity changed")
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
        raise RuntimeError("T148 composed source inventory changed")


def read_tensorboard_scalars(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Read TensorBoardX scalar summaries without adding a dependency."""
    values: dict[str, list[dict[str, Any]]] = {}
    with path.open("rb") as stream:
        while True:
            header = stream.read(8)
            if not header:
                break
            if len(header) != 8:
                raise RuntimeError("truncated TensorBoard record header")
            length = struct.unpack("<Q", header)[0]
            if len(stream.read(4)) != 4:
                raise RuntimeError("truncated TensorBoard header CRC")
            payload = stream.read(length)
            if len(payload) != length or len(stream.read(4)) != 4:
                raise RuntimeError("truncated TensorBoard record")
            event = Event()
            event.ParseFromString(payload)
            if not event.HasField("summary"):
                continue
            for item in event.summary.value:
                if item.HasField("simple_value"):
                    values.setdefault(item.tag, []).append(
                        {
                            "step": int(event.step),
                            "value": float(item.simple_value),
                        }
                    )
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.cpu_contract_authorized:
        raise PermissionError("T148 requires --cpu-contract-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T148: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T148 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T148 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    playground = Path(prereg["playground"]["path"])
    source_path = Path(prereg["assets"]["source_checkpoint"]["path"])
    source_graph = Path(prereg["assets"]["source_raw_onnx"]["path"])
    topology = Path(prereg["assets"]["cpu_topology_template"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    gate_asset = Path(
        prereg["assets"]["hidden_gate_static_asset"]["path"]
    )

    t112.CPU_SOURCE = CPU_SOURCE
    t112.INSPECTION = INSPECTION
    source, remap = t112.cpu_remap(source_path, topology)
    transform = t109.transform(source_graph, EXPECTED)
    model_contract = t128.mechanism_contract(playground, 8)
    command = t98.training_command(
        python=Path(sys.executable),
        playground=playground,
        output=OUTPUT,
        reference=reference,
        restore=CPU_SOURCE,
        gate_asset=gate_asset,
    )
    command.append("--winner_t147_command_group_risk")
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
            f"T148 CPU training failed rc={completed.returncode}\n"
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
        raise RuntimeError("T148 export steps changed")
    event_files = list(OUTPUT.glob("events.out.tfevents*"))
    if len(event_files) != 1:
        raise RuntimeError(
            f"T148 expected one TensorBoard event file: {event_files}"
        )
    scalars = read_tensorboard_scalars(event_files[0])

    initial = t98.restore_tree(checkpoints[0], source)
    final = t98.restore_tree(checkpoints[1024], source)
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
    critic_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("2/params/")
    }
    cases = t98.trace_cases(
        {
            "assets": {
                "t97_preregistration": prereg["assets"][
                    "trace_population"
                ]
            }
        }
    )
    step_zero_trace = t112.trace_equivalence(EXPECTED, graphs[0], cases)
    step_zero_chain = t98.compare_random_chain(EXPECTED, graphs[0])
    postupdate = t112.update_binding(graphs[0], graphs[1024], cases)
    random_binding = t112.random_update_binding(graphs[0], graphs[1024])
    graph_contracts = {
        str(step): {
            "receipt": t20.receipt(graph),
            "io": t98.graph_io(graph),
            "chain": t98.graph_chain(graph),
        }
        for step, graph in sorted(graphs.items())
    }
    group_tags = {
        anchor: f"training/command_group_{anchor}_loss"
        for anchor in ("074", "077", "080")
    }
    count_tags = {
        anchor: f"training/command_group_{anchor}_count"
        for anchor in ("074", "077", "080")
    }
    group_metrics = {
        "losses": {
            anchor: scalars.get(tag, [])
            for anchor, tag in group_tags.items()
        },
        "counts": {
            anchor: scalars.get(tag, [])
            for anchor, tag in count_tags.items()
        },
        "selected": scalars.get(
            "training/command_group_selected", []
        ),
        "all_present": scalars.get(
            "training/command_groups_all_present", []
        ),
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
    thresholds = prereg["thresholds"]

    def one_finite_positive(
        entries: list[dict[str, Any]],
    ) -> bool:
        return (
            len(entries) == 1
            and entries[0]["step"] == 1024
            and np.isfinite(entries[0]["value"])
            and entries[0]["value"] > 0.0
        )

    checks = {
        "command_exact": (
            command.count("--winner_t147_command_group_risk") == 1
            and command[command.index("--ppo_num_envs") + 1] == "8"
            and command[command.index("--ppo_batch_size") + 1] == "8"
            and command[
                command.index("--ground_up_command_support_min_x") + 1
            ]
            == "0.074"
            and command[
                command.index("--ground_up_command_support_max_x") + 1
            ]
            == "0.080"
        ),
        "runner_readback_exact": completed.stdout.count(READBACK) == 1,
        "all_group_losses_recorded_finite": all(
            len(entries) == 1
            and entries[0]["step"] == 1024
            and np.isfinite(entries[0]["value"])
            for entries in group_metrics["losses"].values()
        ),
        "all_group_counts_recorded_positive": all(
            one_finite_positive(entries)
            for entries in group_metrics["counts"].values()
        ),
        "all_groups_present_in_real_update": (
            len(group_metrics["all_present"]) == 1
            and group_metrics["all_present"][0]["step"] == 1024
            and group_metrics["all_present"][0]["value"] == 1.0
        ),
        "selected_group_metric_valid": (
            len(group_metrics["selected"]) == 1
            and group_metrics["selected"][0]["step"] == 1024
            and 0.0 <= group_metrics["selected"][0]["value"] <= 2.0
        ),
        "exact_negative_model_contract": (
            model_contract["population"] == 8
            and model_contract["offsets_bit_exact"]
            and model_contract["model_fields_exact"]
            and model_contract["torso_body_id"] == 2
        ),
        "source_cpu_remap_exact": (
            remap["structure_exact"]
            and remap["maximum_abs_error"] == 0.0
            and remap["tree_finite"]
        ),
        "exact_always_on_transform": (
            transform["node_count_exact"]
            and transform["abi_exact"]
            and transform["initializers_exact"]
            and transform["replacement_exact"]
            and transform["negative_gate_consumer_count"] == 0
        ),
        "step_zero_tree_exact": (
            restore_structure
            and max(restore_deltas.values(), default=0.0) == 0.0
        ),
        "update_structure_exact": update_structure,
        "only_negative_expert_actor_changed": (
            bool(expert_deltas)
            and all(value > 0.0 for value in expert_deltas.values())
            and bool(protected_deltas)
            and all(value == 0.0 for value in protected_deltas.values())
        ),
        "normalizer_bit_exact": (
            bool(normalizer_deltas)
            and all(value == 0.0 for value in normalizer_deltas.values())
        ),
        "every_critic_leaf_changed": (
            bool(critic_deltas)
            and all(value > 0.0 for value in critic_deltas.values())
        ),
        "trees_finite": t112.finite_tree(initial)
        and t112.finite_tree(final),
        "step_zero_trace_exact": (
            step_zero_trace["rows"]
            == thresholds["step_zero_trace_bit_exact_rows"]
            and step_zero_trace["bit_exact_rows"]
            == step_zero_trace["rows"]
            and step_zero_trace["maximum_abs_error"] == 0.0
            and step_zero_trace["always_on_identity_rows"]
            == step_zero_trace["rows"]
        ),
        "step_zero_random_chain_exact": (
            step_zero_chain["steps"]
            == thresholds["step_zero_random_chain_bit_exact_steps"]
            and step_zero_chain["bit_exact_steps"]
            == step_zero_chain["steps"]
            and step_zero_chain["maximum_abs_error"] == 0.0
        ),
        "postupdate_trace_action_binding": (
            postupdate["raw_changed_fraction"]
            >= thresholds["minimum_trace_raw_action_changed_fraction"]
            and postupdate["final_changed_fraction"]
            >= thresholds["minimum_trace_final_action_changed_fraction"]
            and postupdate["always_on_identity_rows"]
            == postupdate["rows"]
            and postupdate["maximum_hidden_delta"] == 0.0
        ),
        "postupdate_random_action_binding": (
            random_binding["changed_steps"] > 0
            and random_binding["maximum_raw_action_delta"]
            >= thresholds["minimum_random_raw_action_delta"]
        ),
        "graph_abi_and_cpu_chain_exact": all(
            item["io"]["inputs"] == expected_io["inputs"]
            and item["io"]["outputs"] == expected_io["outputs"]
            and item["io"]["providers"][0] == "CPUExecutionProvider"
            and item["chain"]["finite"]
            and item["chain"]["steps"] == 256
            for item in graph_contracts.values()
        ),
        "no_behavior_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t148_command_group_risk_cpu_result.v1"
        ),
        "status": (
            "PASS_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
            if passed
            else "HOLD_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
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
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "model_contract": model_contract,
        "source_remap": remap,
        "always_on_transform": transform,
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "readback": READBACK,
            "group_metrics": group_metrics,
            "log": t20.receipt(log),
            "event_file": t20.receipt(event_files[0]),
            "initial_checkpoint": t20.directory_receipt(checkpoints[0]),
            "final_checkpoint": t20.directory_receipt(checkpoints[1024]),
            "graphs": graph_contracts,
        },
        "tree_contract": {
            "negative_expert_actor_leaf_deltas": expert_deltas,
            "protected_mature_actor_leaf_deltas": protected_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "critic_leaf_deltas": critic_deltas,
        },
        "causal_contract": {
            "step_zero_trace": step_zero_trace,
            "step_zero_random_chain": step_zero_chain,
            "postupdate_trace": postupdate,
            "postupdate_random": random_binding,
        },
        "checks": checks,
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
    value["result_sha256"] = t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T148 integrated command-group risk CPU result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Real grouped-risk update metrics: "
        f"`{group_metrics}`\n"
        "- CPU steps / behavior / hosted / robot: `1024/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n\n"
        "A pass earns only a separate hosted-run preregistration.\n",
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
