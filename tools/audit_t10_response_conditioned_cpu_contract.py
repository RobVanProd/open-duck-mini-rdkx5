#!/usr/bin/env python3
"""Independently audit the T10 response-conditioned V121 CPU contract."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
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


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t10_response_conditioned_continuation_cpu_preregistration.json"
)
RESULT = (
    ANALYSIS / "t10_response_conditioned_continuation_cpu_result.json"
)
AUDIT = (
    ANALYSIS
    / "t10_response_conditioned_continuation_cpu_independent_audit.json"
)
MARKDOWN = (
    ANALYSIS
    / "T10_RESPONSE_CONDITIONED_CONTINUATION_CPU_INDEPENDENT_AUDIT_"
    "20260726.md"
)
EXPECTED_INPUTS = {
    "obs": [1, 115],
    "previous_action": [1, 14],
    "h_in": [1, 64],
    "calibration_context": [1, 64],
}
EXPECTED_OUTPUTS = {
    "continuous_actions": [1, 14],
    "previous_action_out": [1, 14],
    "h_out": [1, 64],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def append_if(issues: list[str], condition: bool, label: str) -> None:
    if not condition:
        issues.append(label)


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(entry, "key", getattr(entry, "idx", entry)))
        for entry in path
    )


def tree_deltas(left: Any, right: Any) -> tuple[bool, dict[str, float]]:
    left_rows, left_structure = jax.tree_util.tree_flatten_with_path(left)
    right_rows, right_structure = jax.tree_util.tree_flatten_with_path(
        right
    )
    if left_structure != right_structure:
        return False, {}
    result = {}
    for (left_path, before), (right_path, after) in zip(
        left_rows,
        right_rows,
        strict=True,
    ):
        if left_path != right_path:
            return False, {}
        result[path_name(left_path)] = float(
            np.max(
                np.abs(
                    np.asarray(after, dtype=float)
                    - np.asarray(before, dtype=float)
                )
            )
        )
    return True, result


def describe_onnx(path: Path) -> dict[str, dict[str, list[int]]]:
    import onnx

    model = onnx.load(path)

    def values(items) -> dict[str, list[int]]:
        return {
            item.name: [
                dim.dim_value for dim in item.type.tensor_type.shape.dim
            ]
            for item in items
        }

    return {
        "inputs": values(model.graph.input),
        "outputs": values(model.graph.output),
    }


def audit_graph(
    path: Path,
    *,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    import onnx
    import onnxruntime as ort

    model = onnx.load(path)
    values = {
        item.name: np.asarray(onnx.numpy_helper.to_array(item))
        for item in model.graph.initializer
    }
    producer = {
        output: (node.op_type, tuple(node.input))
        for node in model.graph.node
        for output in node.output
    }
    hierarchy = {
        "context_hidden": producer.get("context_hidden_projected")
        == (
            "MatMul",
            ("calibration_context", "context_hidden_weight"),
        ),
        "context_action": producer.get("context_location")
        == (
            "MatMul",
            ("calibration_context", "context_action_weight"),
        ),
        "guard": producer.get("guard_actual_target")
        == ("Add", ("guard_home", "guard_joint_offsets")),
        "first_deadband": producer.get("v121_preprojection_action")
        == (
            "Where",
            (
                "deadband_is_zero_command",
                "deadband_zero_action",
                "deadband_source_actions",
            ),
        ),
        "final_rate": producer.get("v121_final_rate_action")
        == (
            "Min",
            ("v121_final_above_lower", "v121_final_rate_upper"),
        ),
        "restored_deadband": producer.get("continuous_actions")
        == (
            "Where",
            (
                "deadband_is_zero_command",
                "deadband_zero_action",
                "v121_final_rate_action",
            ),
        ),
        "state_feedback": producer.get("previous_action_out")
        == ("Identity", ("continuous_actions",)),
    }
    session = ort.InferenceSession(
        str(path),
        providers=["CPUExecutionProvider"],
    )
    rng = np.random.Generator(np.random.PCG64(seed))
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    max_rate_excess = 0.0
    max_previous_error = 0.0
    max_context_action_delta = 0.0
    max_context_hidden_delta = 0.0
    x0_exact = True
    finite = True
    for index in range(cases):
        observation = rng.normal(
            0.0,
            0.2,
            size=(1, 115),
        ).astype(np.float32)
        observation[:, 101:115] = rng.uniform(
            -0.8,
            0.8,
            size=(1, 14),
        ).astype(np.float32)
        observation[:, 13:27] = rng.uniform(
            -0.1,
            0.1,
            size=(1, 14),
        ).astype(np.float32)
        is_zero = index % 5 == 0
        observation[:, 6] = np.float32(0.0 if is_zero else 0.077)
        context = rng.normal(
            0.0,
            0.7,
            size=(1, 64),
        ).astype(np.float32)
        action, previous_out, hidden_out = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": context,
            },
        )
        zero_action, zero_hidden = session.run(
            ["continuous_actions", "h_out"],
            {
                "obs": observation,
                "previous_action": previous,
                "h_in": hidden,
                "calibration_context": np.zeros(
                    (1, 64),
                    dtype=np.float32,
                ),
            },
        )
        finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(previous_out).all()
            and np.isfinite(hidden_out).all()
        )
        x0_exact &= not is_zero or np.count_nonzero(action) == 0
        if not is_zero:
            max_rate_excess = max(
                max_rate_excess,
                float(
                    np.max(
                        np.maximum(
                            np.abs(action - previous)
                            - values["max_action_delta"],
                            0.0,
                        )
                    )
                ),
            )
        max_previous_error = max(
            max_previous_error,
            float(np.max(np.abs(previous_out - action))),
        )
        max_context_action_delta = max(
            max_context_action_delta,
            float(np.max(np.abs(action - zero_action))),
        )
        max_context_hidden_delta = max(
            max_context_hidden_delta,
            float(np.max(np.abs(hidden_out - zero_hidden))),
        )
        previous = previous_out
        hidden = hidden_out
    return {
        "abi": describe_onnx(path),
        "providers": session.get_providers(),
        "hierarchy": hierarchy,
        "all_hierarchy_checks": all(hierarchy.values()),
        "initializers_finite": all(
            np.isfinite(value).all() for value in values.values()
        ),
        "all_outputs_finite": finite,
        "x0_exact_zero": bool(x0_exact),
        "max_rate_excess": max_rate_excess,
        "max_previous_error": max_previous_error,
        "max_context_action_delta": max_context_action_delta,
        "max_context_hidden_delta": max_context_hidden_delta,
    }


def main() -> int:
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T10 independent audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    issues: list[str] = []

    prereg_basis = {
        key: prereg[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "assets",
            "software_contract",
            "cpu_smoke",
            "decision_rule",
            "authority",
            "execution_now",
            "preexecution_amendment",
        )
    }
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    append_if(
        issues,
        canonical_sha256(prereg_basis)
        == prereg["preregistered_contract_sha256"],
        "preregistration_canonical",
    )
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result_canonical",
    )
    for name, item in prereg["sources"].items():
        path = Path(item["path"])
        append_if(
            issues,
            path.is_file()
            and path.stat().st_size == item["bytes"]
            and sha256(path) == item["sha256"],
            f"source:{name}",
        )
    for name, item in prereg["assets"].items():
        path = Path(item["path"])
        if name == "expanded_checkpoint":
            condition = (
                path.is_dir() and directory_sha256(path) == item["sha256"]
            )
        else:
            condition = (
                path.is_file()
                and path.stat().st_size == item["bytes"]
                and sha256(path) == item["sha256"]
            )
        append_if(issues, condition, f"asset:{name}")

    training = result["training"]
    expanded = Path(prereg["assets"]["expanded_checkpoint"]["path"])
    initial_checkpoint = Path(training["initial_checkpoint"]["path"])
    final_checkpoint = Path(training["final_checkpoint"]["path"])
    initial_graph = Path(training["initial_onnx"]["path"])
    final_graph = Path(training["final_onnx"]["path"])
    append_if(
        issues,
        directory_sha256(initial_checkpoint)
        == training["initial_checkpoint"]["sha256"],
        "initial_checkpoint_receipt",
    )
    append_if(
        issues,
        directory_sha256(final_checkpoint)
        == training["final_checkpoint"]["sha256"],
        "final_checkpoint_receipt",
    )
    append_if(
        issues,
        sha256(initial_graph) == training["initial_onnx"]["sha256"],
        "initial_onnx_receipt",
    )
    append_if(
        issues,
        sha256(final_graph) == training["final_onnx"]["sha256"],
        "final_onnx_receipt",
    )

    checkpointer = ocp.PyTreeCheckpointer()
    expanded_tree = checkpointer.restore(str(expanded))
    initial_tree = checkpointer.restore(
        str(initial_checkpoint),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    final_tree = checkpointer.restore(
        str(final_checkpoint),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    initial_structure, initial_deltas = tree_deltas(
        expanded_tree,
        initial_tree,
    )
    trained_structure, trained_deltas = tree_deltas(
        initial_tree,
        final_tree,
    )
    policy_deltas = {
        key: value
        for key, value in trained_deltas.items()
        if key.startswith("1/params/")
    }
    context_deltas = {
        key: value
        for key, value in policy_deltas.items()
        if "/context_hidden_projection/" in key
        or "/context_location/" in key
    }
    append_if(
        issues,
        initial_structure
        and max(initial_deltas.values(), default=float("inf")) == 0.0,
        "expanded_restore_exact",
    )
    append_if(issues, trained_structure, "trained_structure")
    append_if(
        issues,
        bool(policy_deltas) and all(value > 0.0 for value in policy_deltas.values()),
        "all_policy_leaves_update",
    )
    append_if(
        issues,
        len(context_deltas) == 2
        and all(value > 0.0 for value in context_deltas.values()),
        "both_context_families_update",
    )
    append_if(
        issues,
        all(
            np.isfinite(np.asarray(leaf)).all()
            for leaf in jax.tree_util.tree_leaves(final_tree)
        ),
        "trained_tree_finite",
    )

    initial = audit_graph(initial_graph, seed=1010210, cases=128)
    trained = audit_graph(final_graph, seed=1010211, cases=128)
    for label, contract in (("initial", initial), ("trained", trained)):
        append_if(
            issues,
            contract["abi"]
            == {"inputs": EXPECTED_INPUTS, "outputs": EXPECTED_OUTPUTS},
            f"{label}_abi",
        )
        append_if(
            issues,
            contract["providers"] == ["CPUExecutionProvider"],
            f"{label}_cpu_provider",
        )
        append_if(
            issues,
            contract["all_hierarchy_checks"],
            f"{label}_hierarchy",
        )
        append_if(
            issues,
            contract["initializers_finite"]
            and contract["all_outputs_finite"],
            f"{label}_finite",
        )
        append_if(
            issues,
            contract["x0_exact_zero"],
            f"{label}_x0",
        )
        append_if(
            issues,
            contract["max_rate_excess"] <= 1.0e-7
            and contract["max_previous_error"] == 0.0,
            f"{label}_state_rate",
        )
    append_if(
        issues,
        trained["max_context_hidden_delta"] > 1.0e-8,
        "trained_context_hidden_effect",
    )
    append_if(
        issues,
        trained["max_context_action_delta"] > 1.0e-8,
        "trained_context_action_effect",
    )

    reset = result["reset_contract"]
    x0 = reset["x0"]
    moving = reset["moving"]
    append_if(
        issues,
        x0["bypassed"]
        and x0["calibration_ticks"] == 0
        and x0["context_linf"] == 0.0
        and x0["hidden_linf"] == 0.0
        and x0["previous_action_linf"] == 0.0
        and x0["phase"] == [1.0, 0.0]
        and x0["applied_target_observation_matches_bridge"],
        "x0_reset_receipt",
    )
    append_if(
        issues,
        not moving["bypassed"]
        and moving["calibration_ticks"] == 250
        and moving["context_linf"] > 0.0
        and moving["context_finite"]
        and moving["previous_action_linf"] > 0.0
        and moving["previous_action_matches_realized"]
        and moving["phase"] == [1.0, 0.0]
        and moving["applied_target_observation_matches_bridge"],
        "moving_reset_receipt",
    )
    append_if(
        issues,
        result["execution"]
        == {
            "optimizer_steps": 1024,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_boundary",
    )
    recomputed_pass = not issues
    expected_status = (
        "PASS_T10_RESPONSE_CONDITIONED_CPU_CONTRACT"
        if recomputed_pass
        else "HOLD_T10_RESPONSE_CONDITIONED_CPU_CONTRACT"
    )
    append_if(
        issues,
        result["status"] == expected_status,
        "result_status",
    )
    recomputed_pass = not issues
    status = (
        "PASS_T10_RESPONSE_CONDITIONED_CPU_INDEPENDENT_AUDIT"
        if recomputed_pass
        else "HOLD_T10_RESPONSE_CONDITIONED_CPU_INDEPENDENT_AUDIT"
    )
    decision = (
        "EARN_ONE_RESPONSE_CONDITIONED_HOSTED_CONTINUATION_PREREGISTRATION"
        if recomputed_pass
        else "HOLD_RESPONSE_CONDITIONED_HOSTED_CONTINUATION"
    )
    basis = {
        "schema_version": "open_duck.t10_response_cpu_audit.v1",
        "status": status,
        "decision": decision,
        "issues": issues,
        "result_file_sha256": sha256(RESULT),
        "result_canonical_sha256": result["result_sha256"],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checkpoint_recomputation": {
            "initial_structure_exact": initial_structure,
            "initial_max_abs_error": max(
                initial_deltas.values(),
                default=float("inf"),
            ),
            "trained_structure_exact": trained_structure,
            "policy_leaf_count": len(policy_deltas),
            "context_leaf_deltas": context_deltas,
        },
        "graph_recomputation": {
            "initial": initial,
            "trained": trained,
        },
        "execution": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "audit_sha256": canonical_sha256(basis),
    }
    AUDIT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T10 independent CPU-contract audit\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        f"- Issues: `{issues}`\n"
        f"- Recomputed context action delta: "
        f"`{trained['max_context_action_delta']:.9g}`\n"
        f"- Recomputed context hidden delta: "
        f"`{trained['max_context_hidden_delta']:.9g}`\n"
        "- Additional optimizer steps: `0`\n"
        "- Behavior cells: `0`\n"
        "- Robot/RDK-X5 access: `0`\n"
        f"- Canonical audit SHA-256: `{value['audit_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"issues={issues}")
    print(f"audit_sha256={value['audit_sha256']}")
    print(f"file_sha256={sha256(AUDIT)}")
    return 0 if recomputed_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
