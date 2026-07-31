#!/usr/bin/env python3
"""Build and freeze T43's forward actor-block causal factorial."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T42 = ANALYSIS / "t42_t41_condition3_failure_attribution.json"
T41_PREREG = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
T39 = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
RUNNER = ROOT / "tools" / "run_t43_forward_actor_block_factorial.py"
WORKER = ROOT / "tools" / "evaluate_t30_t28_margin_causal_cell.py"
OUTPUT = (
    ANALYSIS / "t43_forward_actor_block_factorial_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T43_FORWARD_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION_20260728.md"
)
ASSET_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t43_forward_actor_block_factorial_v1"
)
VARIANTS = (
    ("HALF_WITH_FINAL_BASE", ("base",)),
    ("HALF_WITH_FINAL_ADAPTER", ("adapter",)),
    ("HALF_WITH_FINAL_BASE_ADAPTER", ("base", "adapter")),
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


def validate_policy(path: Path) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260728)
    checks = {
        "cpu_provider": session.get_providers() == ["CPUExecutionProvider"],
        "finite": True,
        "strict_action_margin": True,
        "feedback_exact": True,
        "shapes_exact": True,
    }
    for command_x in (0.0, 0.074, 0.077, 0.08):
        for _ in range(16):
            obs = rng.normal(size=(1, 115)).astype(np.float32)
            obs[:, 6] = np.float32(command_x)
            outputs = session.run(
                None,
                {
                    "obs": obs,
                    "previous_action": rng.uniform(
                        -1.0, 1.0, size=(1, 14)
                    ).astype(np.float32),
                    "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                    "calibration_context": rng.normal(
                        size=(1, 64)
                    ).astype(np.float32),
                },
            )
            checks["finite"] &= all(
                bool(np.all(np.isfinite(item))) for item in outputs
            )
            checks["strict_action_margin"] &= bool(
                np.all(np.abs(outputs[0]) < np.float32(0.98))
                and np.all(np.abs(outputs[1]) < np.float32(0.98))
            )
            checks["feedback_exact"] &= np.array_equal(
                outputs[0], outputs[1]
            )
            checks["shapes_exact"] &= (
                outputs[0].shape == (1, 14)
                and outputs[1].shape == (1, 14)
                and outputs[2].shape == (1, 64)
            )
    return {"checks": checks, "pass": all(checks.values())}


def build_variant(
    half: onnx.ModelProto,
    final: onnx.ModelProto,
    groups: dict[str, list[str]],
    variant_id: str,
    final_groups: tuple[str, ...],
) -> dict[str, Any]:
    selected = {
        name for group in final_groups for name in groups[group]
    }
    half_by_name = {
        item.name: item for item in half.graph.initializer
    }
    final_by_name = {
        item.name: item for item in final.graph.initializer
    }
    model = copy.deepcopy(half)
    for item in model.graph.initializer:
        if item.name in selected:
            item.CopyFrom(final_by_name[item.name])
    variant_dir = ASSET_ROOT / variant_id
    variant_dir.mkdir(parents=True)
    policy_path = variant_dir / "action_margin.onnx"
    onnx.save(model, policy_path)
    observed = onnx.load(policy_path)
    onnx.checker.check_model(observed)
    observed_by_name = {
        item.name: item for item in observed.graph.initializer
    }
    changed_names = sorted(
        name
        for name in half_by_name
        if tensor_sha256(observed_by_name[name])
        != tensor_sha256(half_by_name[name])
    )
    expected_changed = sorted(
        name
        for name in selected
        if tensor_sha256(final_by_name[name])
        != tensor_sha256(half_by_name[name])
    )
    contract = {
        "selected_initializers_exact_final": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(final_by_name[name])
            for name in selected
        ),
        "unselected_initializers_exact_half": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(half_by_name[name])
            for name in half_by_name
            if name not in selected
        ),
        "changed_initializers_exact": changed_names == expected_changed,
        "graph_topology_exact_half": (
            graph_signature(observed) == graph_signature(half)
        ),
        "onnx_checker": True,
    }
    inference = validate_policy(policy_path)
    return {
        "variant_id": variant_id,
        "final_groups": list(final_groups),
        "final_group_count": len(final_groups),
        "selected_initializers": sorted(selected),
        "changed_initializers": changed_names,
        "policy": {
            **receipt(policy_path),
            "checkpoint_id": f"T43_{variant_id}",
        },
        "contract": contract,
        "inference_contract": inference,
        "semantically_equals_final_endpoint": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(final_by_name[name])
            for name in final_by_name
        ),
        "pass": all(contract.values()) and inference["pass"],
    }


def main() -> int:
    if ASSET_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite T43 assets: {ASSET_ROOT}")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T43 prereg: {path}")
    t42 = json.loads(T42.read_text(encoding="utf-8"))
    t41 = json.loads(T41_PREREG.read_text(encoding="utf-8"))
    t39 = json.loads(T39.read_text(encoding="utf-8"))
    groups = t42["endpoint_initializer_audit"]
    group_map = {
        "base": groups["base_names"],
        "adapter": groups["adapter_names"],
    }
    half_path = Path(t39["policies"][0]["path"])
    final_path = Path(t39["policies"][1]["path"])
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    if graph_signature(half) != graph_signature(final):
        raise ValueError("T43 endpoint graph topology differs")
    ASSET_ROOT.mkdir(parents=True)
    variants = [
        build_variant(
            half,
            final,
            group_map,
            variant_id,
            final_groups,
        )
        for variant_id, final_groups in VARIANTS
    ]
    condition = next(
        item
        for item in t41["conditions"]
        if item["id"] == "JOINT_FRICTIONLOSS_LO"
    )
    fit = next(item for item in t41["fits"] if item["fit_id"] == "p30")
    checks = {
        "t42_attribution_green_and_earned_factorial": (
            t42["status"]
            == "PASS_T42_T41_CONDITION3_FAILURE_ATTRIBUTION"
            and t42["decision"]
            == "EARN_T43_HALF_FORWARD_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION"
        ),
        "exact_failed_cell_frozen": (
            t42["failed_cell"]["condition_id"]
            == "JOINT_FRICTIONLOSS_LO"
            and t42["failed_cell"]["checkpoint_id"]
            == "T39_UNIFORM_NORMALIZER_HALF"
            and t42["failed_cell"]["fit_id"] == "p30"
            and t42["failed_cell"]["command_x_m_s"] == 0.08
        ),
        "exact_three_variants": (
            len(variants) == 3
            and [item["variant_id"] for item in variants]
            == [item[0] for item in VARIANTS]
        ),
        "all_variant_contracts_green": all(
            item["pass"] for item in variants
        ),
        "single_group_variants_do_not_collapse_endpoint": all(
            not item["semantically_equals_final_endpoint"]
            for item in variants
            if item["final_group_count"] == 1
        ),
        "combined_variant_collapses_to_final_endpoint": next(
            item
            for item in variants
            if item["variant_id"] == "HALF_WITH_FINAL_BASE_ADAPTER"
        )["semantically_equals_final_endpoint"],
        "condition_and_fit_exact": (
            condition["override"] == {"joint_frictionloss_scale": 0.9}
            and fit["fit_id"] == "p30"
        ),
        "runner_and_worker_present": RUNNER.is_file() and WORKER.is_file(),
        "behavior_cells_zero": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t43_forward_actor_block_factorial_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T43_FORWARD_ACTOR_BLOCK_FACTORIAL"
            if not failed
            else "HOLD_T43_FORWARD_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION"
        ),
        "question": (
            "Is final-checkpoint feed-forward base state, recurrent-adapter "
            "state, or only their combination sufficient to prevent the "
            "half checkpoint's sole T41 failure?"
        ),
        "groups": group_map,
        "variants": variants,
        "execution_order": [item[0] for item in VARIANTS],
        "cell": {
            "condition": condition,
            "fit_id": "p30",
            "command_x_m_s": 0.08,
            "seed": t41["seed"],
            "duration_s": 12.0,
        },
        "fit": fit,
        "calibrator": t41["calibrator"],
        "reference_feature_table": t41["reference_feature_table"],
        "playground": t41["playground"],
        "support_handoff": t41["support_handoff"],
        "behavior_contract": t41["behavior_contract"],
        "protection_contract": t41["protection_contract"],
        "decision_rule": {
            "run_all_three": True,
            "no_early_stop": True,
            "one_group_pass": (
                "A passing one-block variant identifies a sufficient causal "
                "drift block and earns only a separate uniform forward-block "
                "transform contract. Nominal and conditions 1-3 must be "
                "rerun before later robustness."
            ),
            "both_one_group_pass": (
                "Select base by frozen execution-order precedence."
            ),
            "only_combined_pass": (
                "Classify coupled drift and close post-hoc endpoint "
                "replacement because the combined hybrid semantically "
                "duplicates the final endpoint."
            ),
            "no_variant_pass": (
                "Close endpoint actor-block substitution and require a "
                "different persistence mechanism."
            ),
            "diagnostic_precedence": [
                "one changed block",
                "base before adapter",
            ],
            "no_policy_promotion": True,
            "no_checkpoint_selection": True,
            "no_training_or_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "frozen_inputs": {
            "t42_attribution": receipt(T42),
            "t41_preregistration": receipt(T41_PREREG),
            "t39_preregistration": receipt(T39),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
        },
        "execution_now": {
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_three_cpu_cells": not failed,
            "uniform_transform_preregistration": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T43 forward actor-block factorial preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Cell: condition 3 / half / P30 / x=.080",
                "- Variants: final base, final adapter, final base+adapter",
                "- Run all three; no early stop",
                "- Combined-only pass cannot promote because it duplicates "
                "the final endpoint",
                "- Behavior/training/Colab/Gate 5/robot authority: "
                "`3/0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"variants={len(variants)}")
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
