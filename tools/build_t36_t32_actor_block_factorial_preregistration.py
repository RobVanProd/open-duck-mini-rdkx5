#!/usr/bin/env python3
"""Build and freeze T36's finite T32 actor-block factorial screen."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T28_TRANSFORM = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
T33_RESULT = ANALYSIS / "t33_t32_postexport_result.json"
T34_PREREG = ANALYSIS / "t34_t32_nominal_matrix_preregistration.json"
T34_RESULT = ANALYSIS / "t34_t32_nominal_matrix_result.json"
T35_RESULT = ANALYSIS / "t35_t32_margin_causality_result.json"
RUNNER = ROOT / "tools" / "run_t36_t32_actor_block_factorial.py"
WORKER = ROOT / "tools" / "evaluate_t30_t28_margin_causal_cell.py"
OUTPUT = (
    ANALYSIS / "t36_t32_actor_block_factorial_preregistration.json"
)
OUTPUT_MD = (
    ANALYSIS
    / "T36_T32_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION_20260727.md"
)
ASSET_ROOT = (
    Path(r"D:\CodexArtifacts\open-duck-policy")
    / "t36_t32_actor_block_factorial_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from build_t28_t23_action_margin_assets import wrap as append_margin  # noqa: E402


GROUPS = {
    "normalizer": ("obs_mean", "obs_std"),
    "base": (
        "trunk_0_weight",
        "trunk_0_bias",
        "trunk_1_weight",
        "trunk_1_bias",
        "trunk_2_weight",
        "trunk_2_bias",
        "base_residual_weight",
        "base_residual_bias",
    ),
    "adapter": (
        "adapter_weight",
        "adapter_bias",
        "adapter_obs_weight",
        "adapter_hidden_weight",
        "adapter_hidden_bias",
    ),
}
VARIANTS = (
    ("NORMALIZER_HALF", ("normalizer",)),
    ("BASE_HALF", ("base",)),
    ("ADAPTER_HALF", ("adapter",)),
    ("NORMALIZER_BASE_HALF", ("normalizer", "base")),
    ("NORMALIZER_ADAPTER_HALF", ("normalizer", "adapter")),
    ("BASE_ADAPTER_HALF", ("base", "adapter")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def tensor_sha256(value: onnx.TensorProto) -> str:
    return hashlib.sha256(value.SerializeToString()).hexdigest()


def graph_signature(model: onnx.ModelProto) -> dict[str, Any]:
    return {
        "nodes": [
            {
                "op_type": node.op_type,
                "domain": node.domain,
                "inputs": list(node.input),
                "outputs": list(node.output),
            }
            for node in model.graph.node
        ],
        "inputs": [
            (item.name, str(item.type)) for item in model.graph.input
        ],
        "outputs": [
            (item.name, str(item.type)) for item in model.graph.output
        ],
        "initializers": [
            (item.name, list(item.dims), int(item.data_type))
            for item in model.graph.initializer
        ],
    }


def validate_margin(
    pre_margin_path: Path,
    wrapped_path: Path,
    limit: np.float32,
) -> dict[str, Any]:
    before = ort.InferenceSession(
        str(pre_margin_path), providers=["CPUExecutionProvider"]
    )
    after = ort.InferenceSession(
        str(wrapped_path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260727)
    checks = {
        "action_clip_exact": True,
        "previous_action_clip_exact": True,
        "hidden_exact": True,
        "feedback_exact": True,
        "strict_margin": True,
        "finite": True,
    }
    changed_values = 0
    for command_x in (0.0, 0.074, 0.077, 0.08):
        for _ in range(16):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(command_x)
            feed = {
                "obs": obs,
                "previous_action": rng.uniform(
                    -1.0, 1.0, size=(1, 14)
                ).astype(np.float32),
                "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                "calibration_context": rng.normal(
                    size=(1, 64)
                ).astype(np.float32),
            }
            source = before.run(None, feed)
            bounded = after.run(None, feed)
            expected_action = np.clip(source[0], -limit, limit)
            expected_previous = np.clip(source[1], -limit, limit)
            checks["action_clip_exact"] &= np.array_equal(
                bounded[0], expected_action
            )
            checks["previous_action_clip_exact"] &= np.array_equal(
                bounded[1], expected_previous
            )
            checks["hidden_exact"] &= np.array_equal(
                bounded[2], source[2]
            )
            checks["feedback_exact"] &= np.array_equal(
                bounded[0], bounded[1]
            )
            checks["strict_margin"] &= bool(
                np.all(np.abs(bounded[0]) < np.float32(0.98))
                and np.all(np.abs(bounded[1]) < np.float32(0.98))
            )
            checks["finite"] &= all(
                bool(np.all(np.isfinite(item))) for item in bounded
            )
            changed_values += int(
                np.count_nonzero(bounded[0] != source[0])
            )
    return {
        "checks": checks,
        "changed_action_values": changed_values,
        "pass": all(checks.values()),
    }


def build_variant(
    half: onnx.ModelProto,
    final: onnx.ModelProto,
    variant_id: str,
    half_groups: tuple[str, ...],
    limit: np.float32,
) -> dict[str, Any]:
    selected = {
        name for group in half_groups for name in GROUPS[group]
    }
    half_by_name = {
        item.name: item for item in half.graph.initializer
    }
    final_by_name = {
        item.name: item for item in final.graph.initializer
    }
    model = copy.deepcopy(final)
    for item in model.graph.initializer:
        if item.name in selected:
            item.CopyFrom(half_by_name[item.name])
    variant_dir = ASSET_ROOT / variant_id
    variant_dir.mkdir(parents=True)
    pre_margin_path = variant_dir / "pre_margin.onnx"
    wrapped_path = variant_dir / "action_margin.onnx"
    onnx.save(model, pre_margin_path)
    onnx.save(append_margin(copy.deepcopy(model), limit), wrapped_path)

    observed = onnx.load(pre_margin_path)
    observed_by_name = {
        item.name: item for item in observed.graph.initializer
    }
    selected_exact_half = all(
        tensor_sha256(observed_by_name[name])
        == tensor_sha256(half_by_name[name])
        for name in selected
    )
    unselected_exact_final = all(
        tensor_sha256(observed_by_name[name])
        == tensor_sha256(final_by_name[name])
        for name in final_by_name
        if name not in selected
    )
    changed_names = sorted(
        name
        for name in final_by_name
        if tensor_sha256(observed_by_name[name])
        != tensor_sha256(final_by_name[name])
    )
    expected_changed_names = sorted(
        name
        for name in selected
        if tensor_sha256(half_by_name[name])
        != tensor_sha256(final_by_name[name])
    )
    contract = {
        "selected_initializers_exact_half": selected_exact_half,
        "unselected_initializers_exact_final": unselected_exact_final,
        "changed_initializers_exact": (
            changed_names == expected_changed_names
        ),
        "graph_topology_exact_final": (
            graph_signature(observed) == graph_signature(final)
        ),
        "onnx_checker_pre_margin": True,
        "onnx_checker_wrapped": True,
    }
    onnx.checker.check_model(observed)
    onnx.checker.check_model(onnx.load(wrapped_path))
    margin_contract = validate_margin(
        pre_margin_path, wrapped_path, limit
    )
    return {
        "variant_id": variant_id,
        "half_groups": list(half_groups),
        "half_group_count": len(half_groups),
        "selected_initializers": sorted(selected),
        "changed_initializers": changed_names,
        "pre_margin": receipt(pre_margin_path),
        "policy": {
            **receipt(wrapped_path),
            "checkpoint_id": f"T36_{variant_id}",
        },
        "contract": contract,
        "margin_contract": margin_contract,
        "pass": all(contract.values()) and margin_contract["pass"],
    }


def main() -> int:
    if ASSET_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite {ASSET_ROOT}")
    transform = json.loads(T28_TRANSFORM.read_text(encoding="utf-8"))
    postexport = json.loads(T33_RESULT.read_text(encoding="utf-8"))
    t34_prereg = json.loads(T34_PREREG.read_text(encoding="utf-8"))
    t34_result = json.loads(T34_RESULT.read_text(encoding="utf-8"))
    t35_result = json.loads(T35_RESULT.read_text(encoding="utf-8"))
    half_receipt = postexport["deployments"]["1003520"][
        "pre_margin_wrapped"
    ]
    final_receipt = postexport["deployments"]["2007040"][
        "pre_margin_wrapped"
    ]
    half_path = Path(half_receipt["path"])
    final_path = Path(final_receipt["path"])
    if sha256(half_path) != half_receipt["sha256"]:
        raise ValueError("changed T32 half pre-margin graph")
    if sha256(final_path) != final_receipt["sha256"]:
        raise ValueError("changed T32 final pre-margin graph")
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    if graph_signature(half) != graph_signature(final):
        raise ValueError("T32 half/final graph topology differs")
    initializer_names = {item.name for item in final.graph.initializer}
    grouped_names = {
        name for names in GROUPS.values() for name in names
    }
    unknown_changed = sorted(
        item.name
        for item in final.graph.initializer
        if tensor_sha256(item)
        != tensor_sha256(
            next(
                other
                for other in half.graph.initializer
                if other.name == item.name
            )
        )
        and item.name not in grouped_names
    )
    missing_grouped = sorted(grouped_names - initializer_names)
    ASSET_ROOT.mkdir(parents=True)
    limit = np.nextafter(np.float32(0.98), np.float32(0.0))
    variants = [
        build_variant(half, final, variant_id, groups, limit)
        for variant_id, groups in VARIANTS
    ]
    fit = next(
        item
        for item in t34_prereg["fits"]
        if item["fit_id"] == "p31_34"
    )
    checks = {
        "t34_has_exactly_one_final_p31_x0077_failure": (
            t34_result["status"] == "HOLD_T34_T32_NOMINAL_MATRIX"
            and t34_result["condition"]["green_cells"] == 15
        ),
        "t35_attributes_non_green_to_actor_state_drift": (
            t35_result["status"]
            == "PASS_T35_T32_MARGIN_NOT_SUFFICIENT_CAUSE"
            and t35_result["decision"]
            == "ATTRIBUTE_T32_CONTINUED_TRAINING_ACTOR_STATE_DRIFT"
        ),
        "factorial_has_exactly_six_nonendpoint_variants": (
            len(variants) == 6
            and {tuple(item["half_groups"]) for item in variants}
            == {
                ("normalizer",),
                ("base",),
                ("adapter",),
                ("normalizer", "base"),
                ("normalizer", "adapter"),
                ("base", "adapter"),
            }
        ),
        "all_changed_initializers_are_grouped": not unknown_changed,
        "all_grouped_initializers_exist": not missing_grouped,
        "all_variant_graph_contracts_pass": all(
            item["pass"] for item in variants
        ),
        "margin_limit_exact": float(limit)
        == float(transform["stored_float32_limit_abs"]),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t36_t32_actor_block_factorial_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T36_T32_ACTOR_BLOCK_FACTORIAL"
            if not failed_checks
            else "HOLD_T36_T32_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION"
        ),
        "question": (
            "Which final-checkpoint state block—observation normalizer, "
            "feed-forward base actor, recurrent adapter, or a coupled "
            "combination—is sufficient to reproduce T32-half behavior on "
            "T34's sole failed cell when rolled back exactly?"
        ),
        "groups": GROUPS,
        "variants": variants,
        "execution_order": [item[0] for item in VARIANTS],
        "cell": {
            "condition": t34_prereg["conditions"][0],
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "seed": t34_prereg["seed"],
            "duration_s": 12.0,
        },
        "endpoint_evidence": {
            "half": {
                "pre_margin": half_receipt,
                "wrapped": postexport["deployments"]["1003520"]["wrapped"],
                "cell_green": True,
                "source": "T34 T32_MARGIN_HALF p31_34 x=.077",
            },
            "final": {
                "pre_margin": final_receipt,
                "wrapped": postexport["deployments"]["2007040"]["wrapped"],
                "cell_green": False,
                "samples": 494,
                "source": "T34 T32_MARGIN_FINAL p31_34 x=.077",
            },
        },
        "fit": fit,
        "calibrator": t34_prereg["calibrator"],
        "reference_feature_table": t34_prereg[
            "reference_feature_table"
        ],
        "playground": t34_prereg["playground"],
        "support_handoff": t34_prereg["support_handoff"],
        "behavior_contract": t34_prereg["behavior_contract"],
        "protection_contract": t34_prereg["protection_contract"],
        "decision_rule": {
            "run_all_six": True,
            "no_early_stop": True,
            "one_group_pass": (
                "A passing one-group rollback identifies that block as a "
                "sufficient drift source and earns only a prospective "
                "freeze-during-training CPU contract."
            ),
            "only_multi_group_pass": (
                "Classify the drift as coupled. The passing variant with "
                "fewest half groups wins diagnostic precedence; ties follow "
                "the frozen execution order."
            ),
            "no_variant_pass": (
                "Close block freezing as a local repair and require a "
                "different persistence mechanism."
            ),
            "diagnostic_precedence": [
                "fewest half groups",
                "frozen execution order",
            ],
            "no_policy_promotion_or_checkpoint_selection": True,
            "no_training_or_retry": True,
        },
        "frozen_inputs": {
            "t28_transform": receipt(T28_TRANSFORM),
            "t33_postexport_result": receipt(T33_RESULT),
            "t34_preregistration": receipt(T34_PREREG),
            "t34_result": receipt(T34_RESULT),
            "t35_result": receipt(T35_RESULT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "execute_six_cpu_cells": not failed_checks,
            "mechanism_contract_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T36 T32 actor-block factorial preregistration",
                "",
                f"status: `{payload['status']}`",
                "",
                (
                    "Six non-endpoint normalizer/base/adapter rollback "
                    "combinations will run on only the failed "
                    "P31/34 x=.077 cell."
                ),
                "",
                (
                    "This is causal attribution, not checkpoint selection or "
                    "policy promotion. No training, hosted compute, Gate 5, "
                    "RDK-X5, robot, torque, or motion is authorized."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"unknown_changed_initializers={unknown_changed}")
    print(f"missing_grouped_initializers={missing_grouped}")
    print(f"variants={len(variants)}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
