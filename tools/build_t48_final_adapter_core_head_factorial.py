#!/usr/bin/env python3
"""Build and freeze T48's final-adapter core/head causal factorial."""

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
T47 = ANALYSIS / "t47_t46_condition4_failure_attribution.json"
T46_PREREG = (
    ANALYSIS
    / "t46_uniform_final_base_r2_remainder_preregistration.json"
)
T45_PREREG = (
    ANALYSIS
    / "t45_uniform_final_base_qualification_preregistration.json"
)
RUNNER = ROOT / "tools" / "run_t48_final_adapter_core_head_factorial.py"
WORKER = ROOT / "tools" / "evaluate_t48_x0077_causal_cell.py"
OUTPUT = (
    ANALYSIS
    / "t48_final_adapter_core_head_factorial_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_PREREGISTRATION_20260728.md"
)
ASSET_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t48_final_adapter_core_head_factorial_v1"
)
VARIANTS = (
    ("FINAL_WITH_HALF_CORE", ("core",)),
    ("FINAL_WITH_HALF_HEAD", ("head",)),
    ("FINAL_WITH_HALF_CORE_HEAD", ("core", "head")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def tensor_sha256(value: onnx.TensorProto) -> str:
    return hashlib.sha256(value.SerializeToString()).hexdigest()


def graph_signature(model: onnx.ModelProto) -> list[tuple[Any, ...]]:
    return [
        (
            node.op_type,
            node.domain,
            tuple(node.input),
            tuple(node.output),
        )
        for node in model.graph.node
    ]


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
    final: onnx.ModelProto,
    half: onnx.ModelProto,
    groups: dict[str, list[str]],
    variant_id: str,
    half_groups: tuple[str, ...],
) -> dict[str, Any]:
    selected = {
        name for group in half_groups for name in groups[group]
    }
    final_by_name = {
        item.name: item for item in final.graph.initializer
    }
    half_by_name = {
        item.name: item for item in half.graph.initializer
    }
    model = copy.deepcopy(final)
    for item in model.graph.initializer:
        if item.name in selected:
            item.CopyFrom(half_by_name[item.name])
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
        for name in final_by_name
        if tensor_sha256(observed_by_name[name])
        != tensor_sha256(final_by_name[name])
    )
    expected_changed = sorted(
        name
        for name in selected
        if tensor_sha256(half_by_name[name])
        != tensor_sha256(final_by_name[name])
    )
    contract = {
        "selected_initializers_exact_half": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(half_by_name[name])
            for name in selected
        ),
        "unselected_initializers_exact_final": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(final_by_name[name])
            for name in final_by_name
            if name not in selected
        ),
        "changed_initializers_exact": changed_names == expected_changed,
        "graph_topology_exact_final": (
            graph_signature(observed) == graph_signature(final)
        ),
        "onnx_checker": True,
    }
    inference = validate_policy(policy_path)
    return {
        "variant_id": variant_id,
        "half_groups": list(half_groups),
        "half_group_count": len(half_groups),
        "selected_initializers": sorted(selected),
        "changed_initializers": changed_names,
        "policy": {
            **receipt(policy_path),
            "checkpoint_id": f"T48_{variant_id}",
        },
        "contract": contract,
        "inference_contract": inference,
        "semantically_equals_half_endpoint": all(
            tensor_sha256(observed_by_name[name])
            == tensor_sha256(half_by_name[name])
            for name in half_by_name
        ),
        "pass": all(contract.values()) and inference["pass"],
    }


def main() -> int:
    if ASSET_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite T48 assets: {ASSET_ROOT}")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T48 prereg: {path}")
    t47 = json.loads(T47.read_text(encoding="utf-8"))
    t46 = json.loads(T46_PREREG.read_text(encoding="utf-8"))
    t45 = json.loads(T45_PREREG.read_text(encoding="utf-8"))
    half_path = Path(t45["policies"][0]["path"])
    final_path = Path(t45["policies"][1]["path"])
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    if graph_signature(half) != graph_signature(final):
        raise ValueError("T48 endpoint graph topology differs")
    groups = {
        "core": t47["endpoint_attribution"]["recurrent_core"],
        "head": t47["endpoint_attribution"]["output_head"],
    }
    ASSET_ROOT.mkdir(parents=True)
    variants = [
        build_variant(
            final,
            half,
            groups,
            variant_id,
            half_groups,
        )
        for variant_id, half_groups in VARIANTS
    ]
    condition = next(
        item
        for item in t46["conditions"]
        if item["id"] == "JOINT_FRICTIONLOSS_HI"
    )
    fit = next(item for item in t46["fits"] if item["fit_id"] == "p30")
    worker_text = WORKER.read_text(encoding="utf-8")
    checks = {
        "t47_green_and_earned_factorial": (
            t47["status"]
            == "PASS_T47_T46_CONDITION4_FAILURE_ATTRIBUTION"
            and t47["decision"]
            == "EARN_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_PREREGISTRATION"
        ),
        "exact_failed_cell_frozen": (
            t47["failure"]["condition_id"] == "JOINT_FRICTIONLOSS_HI"
            and t47["failure"]["checkpoint_id"]
            == "T45_UNIFORM_FINAL_BASE_FINAL"
            and t47["failure"]["fit_id"] == "p30"
            and t47["failure"]["command_x_m_s"] == 0.077
        ),
        "worker_exact_x0p077": (
            "worker.FORMAL_COMMANDS = (0.077,)" in worker_text
        ),
        "exact_three_variants": (
            len(variants) == 3
            and [item["variant_id"] for item in variants]
            == [item[0] for item in VARIANTS]
        ),
        "all_variant_contracts_green": all(
            item["pass"] for item in variants
        ),
        "single_group_variants_preserve_distinct_endpoint": all(
            not item["semantically_equals_half_endpoint"]
            for item in variants
            if item["half_group_count"] == 1
        ),
        "combined_variant_duplicates_half_endpoint": next(
            item
            for item in variants
            if item["variant_id"] == "FINAL_WITH_HALF_CORE_HEAD"
        )["semantically_equals_half_endpoint"],
        "condition_and_fit_exact": (
            condition["override"] == {"joint_frictionloss_scale": 1.1}
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
            "open_duck.t48_final_adapter_core_head_factorial_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL"
            if not failed
            else "HOLD_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_PREREGISTRATION"
        ),
        "question": (
            "Is replacing the final adapter's recurrent core, output head, "
            "or only both with half-checkpoint values sufficient to repair "
            "T46's sole condition-4 failure?"
        ),
        "groups": groups,
        "variants": variants,
        "execution_order": [item[0] for item in VARIANTS],
        "cell": {
            "condition": condition,
            "fit_id": "p30",
            "command_x_m_s": 0.077,
            "seed": t46["seed"],
            "duration_s": 12.0,
        },
        "fit": fit,
        "calibrator": t46["calibrator"],
        "reference_feature_table": t46["reference_feature_table"],
        "playground": t46["playground"],
        "support_handoff": t46["support_handoff"],
        "behavior_contract": t46["behavior_contract"],
        "protection_contract": t46["protection_contract"],
        "decision_rule": {
            "run_all_three": True,
            "no_early_stop": True,
            "one_group_pass": (
                "A passing one-subblock variant identifies a sufficient "
                "adapter cause and earns only a separate uniform-transform "
                "qualification."
            ),
            "both_one_group_pass": (
                "Select recurrent core by frozen execution-order precedence."
            ),
            "only_combined_pass": (
                "Close post-hoc adapter replacement because the combined "
                "variant duplicates the half endpoint."
            ),
            "no_variant_pass": (
                "Close adapter subblock substitution and require a "
                "different persistence mechanism."
            ),
            "diagnostic_precedence": [
                "one changed subblock",
                "core before head",
            ],
            "no_policy_promotion": True,
            "no_checkpoint_selection": True,
            "no_training_or_retry": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "frozen_inputs": {
            "t47_attribution": receipt(T47),
            "t46_preregistration": receipt(T46_PREREG),
            "t45_preregistration": receipt(T45_PREREG),
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
                "# T48 final-adapter core/head factorial",
                "",
                f"- Status: `{value['status']}`",
                "- Cell: condition 4 / final / P30 / x=.077",
                "- Variants: half core, half head, half core+head",
                "- Run all three; no early stop",
                "- Combined-only pass cannot promote because it duplicates "
                "the half endpoint",
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
