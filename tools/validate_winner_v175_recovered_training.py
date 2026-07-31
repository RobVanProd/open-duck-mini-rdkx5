#!/usr/bin/env python3
"""Validate recovered V175 outputs on an explicit CPU topology."""

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

from flax.training import orbax_utils
import jax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from validate_winner_v112_recovered_training import (  # noqa: E402
    event_scalars,
    onnx_contract,
    sha256,
    step,
    tree_deltas,
    tree_finite,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v175_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v175_hosted_package_contract.json"
TRANSPORT_CONTRACT = (
    ANALYSIS / "winner_v175_upload_transport_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "winner_v175_colab_launch_contract.json"
OUTPUT = ANALYSIS / "winner_v175_recovered_training_validation.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V175_RECOVERED_TRAINING_VALIDATION_20260725.md"
)
EXPECTED = {
    "preregistration": (
        "a6f2bd5377a2e9dd5659755a203c8900b548797ad8ca7b1455428dda41a226bc"
    ),
    "package_contract": (
        "755362bcc66dfa532bd2bebbb55d71ea85cb5ba6d07dd43b6249a814ff0db6f5"
    ),
    "transport_contract": (
        "bbfd3a9a52328d3b889bbe0b6d890a0044ff70409032de68a38b3382213eb932"
    ),
    "launch_contract": (
        "723b8d754db6b1dc2d0ee128ab4554c8b38de1eb25275447c98ff1159f000fcb"
    ),
    "hosted_result": (
        "dc8bbbca1f9f746c4ca185cacaea94898abf5400e3a9b75f49c2a1a72b0f8e66"
    ),
    "launch_receipt": (
        "87669274fb5be56f5d8b7419281759d1bce9ff32550b9a487b37f581103f13f6"
    ),
    "recovery_archive": (
        "663e0a96d8b82837f87741971b2377e933714385eda7f44fe6a928ebb05a5260"
    ),
    "source_checkpoint": (
        "29b6d1d707784cc49050ab4b5513c06b020ebf7cf02dba3bee304a74477348f8"
    ),
    "policy_cpu_template": (
        "b4c9d6510da13763b77fc47f69797398e645f938091c37e8c3b4cd862fff3038"
    ),
    "cost_cpu_template": (
        "cb44184d21ca2f1147912dbb96d575fc68a7b5fa62362ae2003cfbe8b8a44478"
    ),
}
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
EXPECTED_UPDATE_COUNTS = {0: 0.0, 1_003_520: 784.0, 2_007_040: 1_568.0}


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def restore_like(path: Path, template):
    checkpointer = ocp.PyTreeCheckpointer()
    restore_args = orbax_utils.restore_args_from_target(template)
    return checkpointer.restore(
        str(path), item=template, restore_args=restore_args
    )


def cost_step(path: Path) -> int:
    return int(path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--policy-cpu-template", type=Path, required=True)
    parser.add_argument("--cost-cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")

    recovery = args.recovery_root.resolve()
    training = (
        args.extracted_root.resolve()
        / "winner_v175_tangent_continuation/training"
    )
    source = args.source_checkpoint.resolve()
    policy_template_path = args.policy_cpu_template.resolve()
    cost_template_path = args.cost_cpu_template.resolve()
    paths = {
        "hosted_result": recovery / "winner_v175_result.json",
        "launch_receipt": recovery / "winner_v175_launch_receipt.json",
        "recovery_archive": recovery / "winner_v175_artifacts.tar.gz",
    }
    input_hashes = {
        "preregistration": sha256(PREREGISTRATION),
        "package_contract": sha256(PACKAGE_CONTRACT),
        "transport_contract": sha256(TRANSPORT_CONTRACT),
        "launch_contract": sha256(LAUNCH_CONTRACT),
        **{name: sha256(path) for name, path in paths.items()},
        "source_checkpoint": directory_sha256(source),
        "policy_cpu_template": directory_sha256(policy_template_path),
        "cost_cpu_template": directory_sha256(cost_template_path),
    }
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    transport = json.loads(
        TRANSPORT_CONTRACT.read_text(encoding="utf-8")
    )
    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(
        paths["launch_receipt"].read_text(encoding="utf-8")
    )

    policy_paths = sorted(
        (
            path
            for path in training.iterdir()
            if path.is_dir() and "_v127_cost_value" not in path.name
        ),
        key=step,
    )
    cost_paths = sorted(
        training.glob("*_v127_cost_value"), key=cost_step
    )
    graph_paths = sorted(training.glob("*.onnx"), key=step)
    aux_paths = sorted(training.glob("*_v127_aux.json"))
    policy_by_step = {step(path): path for path in policy_paths}
    cost_by_step = {cost_step(path): path for path in cost_paths}
    graph_by_step = {step(path): path for path in graph_paths}
    aux_by_step = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in aux_paths
    }
    policy_hashes = {
        value: directory_sha256(path)
        for value, path in policy_by_step.items()
    }
    cost_hashes = {
        value: directory_sha256(path)
        for value, path in cost_by_step.items()
    }
    graph_rows = {
        value: onnx_contract(path)
        for value, path in graph_by_step.items()
    }
    aux = {
        value: json.loads(path.read_text(encoding="utf-8"))
        for value, path in aux_by_step.items()
    }

    checkpointer = ocp.PyTreeCheckpointer()
    policy_template = checkpointer.restore(str(policy_template_path))
    source_tree = restore_like(source, policy_template)
    policy_trees = {
        value: restore_like(path, source_tree)
        for value, path in policy_by_step.items()
    }
    initial_structure, initial_deltas = tree_deltas(
        source_tree, policy_trees[0]
    )
    trained_policy = []
    for value in EXPECTED_STEPS[1:]:
        structure, deltas = tree_deltas(policy_trees[0], policy_trees[value])
        policy_deltas = {
            name: delta
            for name, delta in deltas.items()
            if name.startswith("1/params/")
        }
        trained_policy.append(
            {
                "step": value,
                "structure_exact": structure,
                "tree_finite": tree_finite(policy_trees[value]),
                "policy_leaf_deltas": policy_deltas,
                "every_policy_leaf_updated": bool(policy_deltas)
                and all(delta > 0.0 for delta in policy_deltas.values()),
            }
        )

    cost_template = checkpointer.restore(str(cost_template_path))
    cost_trees = {
        value: restore_like(path, cost_template)
        for value, path in cost_by_step.items()
    }
    trained_cost = []
    for value in EXPECTED_STEPS[1:]:
        structure, deltas = tree_deltas(cost_trees[0], cost_trees[value])
        trained_cost.append(
            {
                "step": value,
                "structure_exact": structure,
                "tree_finite": tree_finite(cost_trees[value]),
                "leaf_deltas": deltas,
                "every_leaf_updated": bool(deltas)
                and all(delta > 0.0 for delta in deltas.values()),
            }
        )

    event_path = next(training.glob("events.out.tfevents*"))
    scalars = event_scalars(event_path)
    metric_tags = (
        "eval/avg_episode_length",
        "eval/episode_cost/winner_v127_dense_torque_exceedance",
        "eval/episode_reward",
        "training/cost_v_loss",
        "training/dense_cost_mean",
        "training/dual_lambda",
        "training/policy_loss",
        "training/total_loss",
        "training/v_loss",
        "training/winner_v173_cost_first_branch",
        "training/winner_v173_reward_only_branch",
        "training/winner_v173_tangent_branch",
    )
    metric_evidence = {tag: scalars.get(tag, []) for tag in metric_tags}
    metric_steps_exact = all(
        [row["step"] for row in metric_evidence[tag]] == EXPECTED_STEPS
        for tag in metric_tags[:3]
    ) and all(
        [row["step"] for row in metric_evidence[tag]]
        == EXPECTED_STEPS[1:]
        for tag in metric_tags[3:]
    )
    metrics_finite = all(
        math.isfinite(float(row["value"]))
        for rows in metric_evidence.values()
        for row in rows
    )
    hosted_policy = {
        int(value): hash_value
        for value, hash_value in hosted["policy_checkpoint_sha256"].items()
    }
    hosted_cost = {
        int(value): hash_value
        for value, hash_value in hosted["cost_checkpoint_sha256"].items()
    }
    hosted_graphs = {
        int(value): row["sha256"]
        for value, row in hosted["graphs"].items()
    }
    hosted_aux = {
        int(value): row
        for value, row in hosted["optimizer_state"].items()
    }
    update_counts = {
        value: (
            float(aux[value]["v173_reward_only_updates"])
            + float(aux[value]["v173_cost_first_updates"])
            + float(aux[value]["v173_tangent_updates"])
        )
        for value in EXPECTED_STEPS
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "all_frozen_launch_contracts_green": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V175_HOSTED_CONTINUATION"
            and package.get("status") == "PASS_WINNER_V175_HOSTED_PACKAGE"
            and transport.get("status")
            == "PASS_WINNER_V175_UPLOAD_TRANSPORT"
            and launch.get("status")
            == "PASS_WINNER_V175_COLAB_LAUNCH_CONTRACT"
            and all(
                item.get("failed_checks") == []
                for item in (prereg, package, transport, launch)
            )
        ),
        "hosted_artifact_passed": (
            hosted.get("status")
            == "PASS_WINNER_V175_HOSTED_CONTINUATION_ARTIFACT"
            and hosted.get("failed_checks") == []
            and all(hosted.get("checks", {}).values())
        ),
        "launch_receipt_complete_no_retry": (
            receipt.get("status") == "COMPLETED_WINNER_V175_COLAB_LAUNCH"
            and receipt.get("returncode") == 0
            and receipt.get("retry") is False
            and receipt.get("resume") is False
            and receipt.get("robot_or_rdk_access") is False
        ),
        "result_hash_matches_receipt": (
            receipt.get("output_json_sha256")
            == input_hashes["hosted_result"]
        ),
        "archive_hash_matches_result_and_receipt": (
            hosted.get("archive", {}).get("sha256")
            == input_hashes["recovery_archive"]
            and receipt.get("output_archive_sha256")
            == input_hashes["recovery_archive"]
        ),
        "all_exact_export_sets_present": (
            sorted(policy_by_step)
            == sorted(cost_by_step)
            == sorted(graph_by_step)
            == sorted(aux_by_step)
            == EXPECTED_STEPS
        ),
        "policy_hashes_match_hosted_result": policy_hashes == hosted_policy,
        "cost_hashes_match_hosted_result": cost_hashes == hosted_cost,
        "onnx_hashes_match_hosted_result": (
            {
                value: row["sha256"]
                for value, row in graph_rows.items()
            }
            == hosted_graphs
        ),
        "optimizer_states_match_hosted_result": aux == hosted_aux,
        "step_zero_source_restore_structure_exact": initial_structure,
        "step_zero_source_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "all_policy_trees_finite": tree_finite(policy_trees[0])
        and all(row["tree_finite"] for row in trained_policy),
        "all_policy_structures_exact": all(
            row["structure_exact"] for row in trained_policy
        ),
        "every_policy_leaf_updated_at_both_checkpoints": all(
            row["every_policy_leaf_updated"] for row in trained_policy
        ),
        "all_cost_trees_finite": tree_finite(cost_trees[0])
        and all(row["tree_finite"] for row in trained_cost),
        "all_cost_structures_exact": all(
            row["structure_exact"] for row in trained_cost
        ),
        "every_cost_leaf_updated_at_both_checkpoints": all(
            row["every_leaf_updated"] for row in trained_cost
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in graph_rows.values()
        ),
        "dual_disabled_and_pinned_zero": all(
            float(row["lambda"]) == 0.0
            and float(row["eta"]) == 0.0
            and float(row["initial_cost"]) == 0.0
            and row["initialized"] is False
            for row in aux.values()
        ),
        "actor_update_counts_exact": update_counts
        == EXPECTED_UPDATE_COUNTS,
        "cost_seen_and_no_zero_directions": all(
            aux[value]["v173_cost_seen"] is True
            and float(aux[value]["v173_zero_direction_updates"]) == 0.0
            for value in EXPECTED_STEPS[1:]
        ),
        "hosted_branch_accounting_is_cost_first_only": all(
            float(aux[value]["v173_cost_first_updates"])
            == EXPECTED_UPDATE_COUNTS[value]
            and float(aux[value]["v173_reward_only_updates"]) == 0.0
            and float(aux[value]["v173_tangent_updates"]) == 0.0
            for value in EXPECTED_STEPS[1:]
        ),
        "constrained_direction_invariants_hold": all(
            float(aux[value]["v173_min_tangent_retention"]) >= 1.0 / 32.0
            and float(
                aux[value]["v173_max_constrained_derivative_excess"]
            )
            <= 64.0 * 1.1920928955078125e-7
            for value in EXPECTED_STEPS[1:]
        ),
        "training_metrics_have_exact_export_steps": metric_steps_exact,
        "training_metrics_all_finite": metrics_finite,
        "cpu_only_validation": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "formal_behavior_evaluation_was_not_run_hosted": (
            hosted.get("authority", {}).get("behavior_evaluation") is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v175.recovered_training_validation.v1",
        "status": (
            "PASS_WINNER_V175_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_WINNER_V175_RECOVERED_TRAINING_VALIDATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "policy_checkpoints": [
            {"step": value, "directory_sha256": policy_hashes[value]}
            for value in EXPECTED_STEPS
        ],
        "cost_checkpoints": [
            {"step": value, "directory_sha256": cost_hashes[value]}
            for value in EXPECTED_STEPS
        ],
        "onnx": [graph_rows[value] for value in EXPECTED_STEPS],
        "optimizer_state": {
            str(value): aux[value] for value in EXPECTED_STEPS
        },
        "trained_policy": trained_policy,
        "trained_cost": trained_cost,
        "training_metric_evidence": metric_evidence,
        "behavior_neutral_observation": {
            "all_hosted_actor_updates_used_cost_first_branch": True,
            "selection_weight": 0,
            "requires_frozen_nominal_behavior_gate": True,
        },
        "authority": {
            "nominal_behavior_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 recovered training validation\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Source restore: CPU topology, bit-exact step zero.\n"
        "- Actor branches: all hosted updates were cost-first; this has zero "
        "behavior-selection weight.\n"
        "- Authority: preregister the both-checkpoint nominal behavior gate "
        "only.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
