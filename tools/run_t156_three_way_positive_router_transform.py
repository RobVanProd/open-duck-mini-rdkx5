#!/usr/bin/env python3
"""Recover +COM contexts and build the frozen three-way expert router."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort
from onnx import helper, numpy_helper

from run_t135_calibration_context_router_screen import (
    build_diagnostic_policy,
    classifier,
    context_sha256,
)
from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    abi,
    canonical_sha256,
    receipt,
    verify,
)


PREREG = ANALYSIS / "t156_three_way_positive_router_preregistration.json"
RESULT = ANALYSIS / "t156_three_way_positive_router_result.json"
MARKDOWN = (
    ANALYSIS / "T156_THREE_WAY_POSITIVE_ROUTER_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t156_three_way_positive_router_v1"
)
STEPS = ("1003520", "2007040")
POSITIVE_OVERRIDE = {"torso_com_offset_m": [0.05, 0.0, 0.0]}


def initializer_map(
    model: onnx.ModelProto,
) -> dict[str, onnx.TensorProto]:
    return {item.name: item for item in model.graph.initializer}


def load_context(trace: Path) -> tuple[np.ndarray, str]:
    first = json.loads(trace.read_text(encoding="utf-8").splitlines()[0])
    context = np.asarray(
        first["policy_state_output"]["h_out"], dtype=np.float32
    ).reshape(1, 64)
    trace_hash = first["policy_calibration_context_sha256"]
    if context_sha256(context) != trace_hash:
        raise RuntimeError(f"T156 context/trace hash mismatch: {trace}")
    return context.reshape(-1), trace_hash


def recover_positive_context(
    prereg: dict[str, Any],
    policy: Path,
    fit: dict[str, Any],
) -> dict[str, Any]:
    fit_id = fit["fit_id"]
    root = WORK / "positive_contexts" / fit_id
    trace_dir = root / "traces"
    evaluation = root / "evaluation.json"
    stdout = root / "stdout.log"
    root.mkdir(parents=True)
    command = [
        sys.executable,
        prereg["frozen_inputs"]["evaluator"]["path"],
        "--policy",
        str(policy),
        "--policy-sha256",
        receipt(policy)["sha256"],
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        fit["path"],
        "--reference-feature-table",
        prereg["reference_feature_table"]["path"],
        "--calibrator",
        prereg["calibrator"]["path"],
        "--calibrator-sha256",
        prereg["calibrator"]["sha256"],
        "--override-json",
        json.dumps(POSITIVE_OVERRIDE, separators=(",", ":")),
        "--commands",
        str(prereg["calibration"]["command_x_m_s"]),
        "--seed",
        str(prereg["calibration"]["seed"]),
        "--duration-s",
        "0.02",
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    stdout.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T156 calibration worker failed: {fit_id}; log={stdout}"
        )
    payload = json.loads(evaluation.read_text(encoding="utf-8"))
    trace = Path(payload["runs"][0]["trace_jsonl"])
    context, trace_hash = load_context(trace)
    expected = prereg["expected_positive_context_hashes"][fit_id]
    return {
        "fit_id": fit_id,
        "population": "com_x_positive",
        "context": context.astype(float).tolist(),
        "context_sha256": trace_hash,
        "expected_context_sha256": expected,
        "context_hash_exact": trace_hash == expected,
        "trace": receipt(trace),
        "evaluation": receipt(evaluation),
        "stdout": receipt(stdout),
        "calibration_ticks": 250,
        "behavior_ticks": 1,
    }


def positive_classifier(
    prior_contexts: list[dict[str, Any]],
    positive_contexts: list[dict[str, Any]],
) -> tuple[np.ndarray, float, dict[str, Any]]:
    nonpositive = [
        np.asarray(row["context"], dtype=np.float32)
        for row in prior_contexts
    ]
    positive = [
        np.asarray(row["context"], dtype=np.float32)
        for row in positive_contexts
    ]
    coefficient, intercept, full = classifier(nonpositive, positive)
    fit_ids = sorted({row["fit_id"] for row in positive_contexts})
    leave_one_fit_out = []
    for held in fit_ids:
        train_nonpositive = [
            np.asarray(row["context"], dtype=np.float32)
            for row in prior_contexts
            if row["fit_id"] != held
        ]
        train_positive = [
            np.asarray(row["context"], dtype=np.float32)
            for row in positive_contexts
            if row["fit_id"] != held
        ]
        fold_coefficient, fold_intercept, _ = classifier(
            train_nonpositive,
            train_positive,
        )
        held_rows = [
            *[
                row
                for row in prior_contexts
                if row["fit_id"] == held
            ],
            *[
                row
                for row in positive_contexts
                if row["fit_id"] == held
            ],
        ]
        scores = []
        for row in held_rows:
            score = float(
                np.asarray(row["context"], dtype=np.float32)
                @ fold_coefficient
                + fold_intercept
            )
            expected_positive = row["population"] == "com_x_positive"
            scores.append(
                {
                    "population": row["population"],
                    "score": score,
                    "expected_positive": expected_positive,
                    "label_exact": (
                        score > 0.0
                        if expected_positive
                        else score < 0.0
                    ),
                }
            )
        leave_one_fit_out.append(
            {
                "train_fit": next(
                    fit_id for fit_id in fit_ids if fit_id != held
                ),
                "held_fit": held,
                "scores": scores,
                "labels_exact": all(
                    item["label_exact"] for item in scores
                ),
            }
        )
    return coefficient, intercept, {
        "nonpositive_scores": full["nominal_scores"],
        "positive_scores": full["negative_scores"],
        "positive_min_minus_nonpositive_max": full[
            "negative_min_minus_nominal_max"
        ],
        "all_labels_exact": full["all_labels_exact"],
        "leave_one_fit_out": leave_one_fit_out,
        "leave_one_fit_out_exact": all(
            row["labels_exact"] for row in leave_one_fit_out
        ),
    }


def positive_reference(
    source: Path,
    positive_source: Path,
    destination: Path,
) -> dict[str, Any]:
    model = onnx.load(source)
    positive = onnx.load(positive_source)
    model_initializers = initializer_map(model)
    positive_initializers = initializer_map(positive)
    replacements = {}
    for name in ("negative_adapter_weight", "negative_adapter_bias"):
        old = model_initializers[name]
        new = positive_initializers[name]
        if numpy_helper.to_array(old).shape != numpy_helper.to_array(new).shape:
            raise RuntimeError(f"T156 positive tensor shape changed: {name}")
        index = next(
            i
            for i, item in enumerate(model.graph.initializer)
            if item.name == name
        )
        replacements[name] = {
            "source": receipt(positive_source),
            "old_sha256": canonical_sha256(
                numpy_helper.to_array(old).astype(float).tolist()
            ),
            "new_sha256": canonical_sha256(
                numpy_helper.to_array(new).astype(float).tolist()
            ),
        }
        del model.graph.initializer[index]
        model.graph.initializer.insert(index, copy.deepcopy(new))
    candidates = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.name == "t143_select_forward_path"
        and node.op_type == "Where"
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(candidates) != 1:
        raise RuntimeError("T156 T143 selected-path node changed")
    index, old = candidates[0]
    replacement = helper.make_node(
        "Identity",
        ["negative_condition_adapter_location"],
        ["conditional_adapter_location"],
        name="t156_positive_always_on_reference",
    )
    del model.graph.node[index]
    model.graph.node.insert(index, replacement)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)
    return {
        "source": receipt(source),
        "positive_source": receipt(positive_source),
        "reference": receipt(destination),
        "router_replacement_index": index,
        "source_where_inputs": list(old.input),
        "identity_exact": (
            list(replacement.input)
            == ["negative_condition_adapter_location"]
            and list(replacement.output)
            == ["conditional_adapter_location"]
        ),
        "positive_tensors_replaced": replacements,
    }


def transform(
    source: Path,
    positive_source: Path,
    destination: Path,
    coefficient: np.ndarray,
    intercept: float,
) -> dict[str, Any]:
    model = onnx.load(source)
    before = copy.deepcopy(model)
    positive = onnx.load(positive_source)
    positive_initializers = initializer_map(positive)
    old_initializers = {
        item.name: item.SerializeToString()
        for item in model.graph.initializer
    }
    candidates = [
        (index, node)
        for index, node in enumerate(model.graph.node)
        if node.name == "t143_select_forward_path"
        and node.op_type == "Where"
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(candidates) != 1:
        raise RuntimeError("T156 source select node changed")
    select_index, select_node = candidates[0]
    select_node.output[0] = "t156_nominal_negative_adapter_location"
    additions = {
        "positive_adapter_weight": numpy_helper.to_array(
            positive_initializers["negative_adapter_weight"]
        ),
        "positive_adapter_bias": numpy_helper.to_array(
            positive_initializers["negative_adapter_bias"]
        ),
        "positive_router_coefficient": coefficient.reshape(64, 1),
        "positive_router_intercept": np.asarray(
            [intercept], dtype=np.float32
        ),
        "positive_router_zero": np.asarray([0.0], dtype=np.float32),
    }
    for name, value in additions.items():
        model.graph.initializer.append(
            numpy_helper.from_array(np.asarray(value, dtype=np.float32), name)
        )
    inserted = [
        helper.make_node(
            "Gemm",
            ["h_out", "positive_adapter_weight", "positive_adapter_bias"],
            ["t156_positive_adapter_location"],
            name="t156_positive_expert",
        ),
        helper.make_node(
            "MatMul",
            ["calibration_context", "positive_router_coefficient"],
            ["t156_positive_router_linear"],
            name="t156_positive_router_matmul",
        ),
        helper.make_node(
            "Add",
            ["t156_positive_router_linear", "positive_router_intercept"],
            ["t156_positive_router_score"],
            name="t156_positive_router_add",
        ),
        helper.make_node(
            "GreaterOrEqual",
            ["t156_positive_router_score", "positive_router_zero"],
            ["t156_positive_condition"],
            name="t156_positive_router_gate",
        ),
        helper.make_node(
            "Where",
            [
                "t156_positive_condition",
                "t156_positive_adapter_location",
                "t156_nominal_negative_adapter_location",
            ],
            ["conditional_adapter_location"],
            name="t156_select_three_way_path",
        ),
    ]
    for offset, node in enumerate(inserted, start=1):
        model.graph.node.insert(select_index + offset, node)
    onnx.checker.check_model(model)
    destination.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, destination)

    after = onnx.load(destination)
    old_nodes = list(before.graph.node)
    new_nodes = list(after.graph.node)
    new_initializers = {
        item.name: item.SerializeToString()
        for item in after.graph.initializer
    }
    expected_select = copy.deepcopy(old_nodes[select_index])
    expected_select.output[0] = "t156_nominal_negative_adapter_location"
    source_nodes_exact = True
    old_index = 0
    for new_index, node in enumerate(new_nodes):
        if select_index + 1 <= new_index <= select_index + 5:
            continue
        expected = (
            expected_select
            if old_index == select_index
            else old_nodes[old_index]
        )
        source_nodes_exact &= (
            node.SerializeToString() == expected.SerializeToString()
        )
        old_index += 1
    return {
        "source": receipt(source),
        "positive_source": receipt(positive_source),
        "transformed": receipt(destination),
        "five_nodes_inserted": len(new_nodes) == len(old_nodes) + 5,
        "source_select_output_rewire_exact": (
            expected_select.output[0]
            == "t156_nominal_negative_adapter_location"
        ),
        "all_source_nodes_otherwise_byte_exact": source_nodes_exact,
        "existing_initializers_byte_exact": all(
            new_initializers.get(name) == value
            for name, value in old_initializers.items()
        ),
        "five_initializers_added": (
            set(new_initializers) - set(old_initializers) == set(additions)
        ),
        "positive_tensors_exact": all(
            np.array_equal(
                numpy_helper.to_array(
                    initializer_map(after)[target]
                ),
                numpy_helper.to_array(
                    positive_initializers[source_name]
                ),
            )
            for target, source_name in (
                ("positive_adapter_weight", "negative_adapter_weight"),
                ("positive_adapter_bias", "negative_adapter_bias"),
            )
        ),
        "abi_exact": abi(before) == abi(after),
    }


def equivalence_contract(
    source: Path,
    positive_reference_path: Path,
    transformed: Path,
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    positive_session = ort.InferenceSession(
        str(positive_reference_path),
        providers=["CPUExecutionProvider"],
    )
    transformed_session = ort.InferenceSession(
        str(transformed), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260729)
    rows = []
    for context_row in contexts:
        positive_condition = (
            context_row["population"] == "com_x_positive"
        )
        selected = positive_session if positive_condition else source_session
        exact = True
        finite = True
        feedback = True
        samples = 0
        for command_x in (0.0, 0.074, 0.077, 0.08):
            for _ in range(16):
                feed = {
                    "obs": rng.normal(size=(1, 115)).astype(np.float32),
                    "previous_action": rng.uniform(
                        -0.98, 0.98, size=(1, 14)
                    ).astype(np.float32),
                    "h_in": rng.normal(size=(1, 64)).astype(np.float32),
                    "calibration_context": np.asarray(
                        context_row["context"], dtype=np.float32
                    ).reshape(1, 64),
                }
                feed["obs"][:, 6] = np.float32(command_x)
                expected = selected.run(None, feed)
                actual = transformed_session.run(None, feed)
                exact &= all(
                    np.array_equal(left, right)
                    for left, right in zip(expected, actual, strict=True)
                )
                finite &= all(
                    bool(np.all(np.isfinite(value))) for value in actual
                )
                feedback &= np.array_equal(actual[0], actual[1])
                samples += 1
        rows.append(
            {
                "fit_id": context_row["fit_id"],
                "population": context_row["population"],
                "selected_source": (
                    "T154_positive_expert_always_on"
                    if positive_condition
                    else "T143C_nominal_negative_router"
                ),
                "samples": samples,
                "all_outputs_bit_exact": exact,
                "all_outputs_finite": finite,
                "action_feedback_bit_exact": feedback,
            }
        )
    return {
        "rows": rows,
        "all_selected_source_outputs_bit_exact": all(
            row["all_outputs_bit_exact"] for row in rows
        ),
        "all_outputs_finite": all(
            row["all_outputs_finite"] for row in rows
        ),
        "all_action_feedback_bit_exact": all(
            row["action_feedback_bit_exact"] for row in rows
        ),
        "samples": sum(row["samples"] for row in rows),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in (
                source_session,
                positive_session,
                transformed_session,
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T156 requires --execute")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T156: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T156 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T156 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for fit in prereg["fits"]:
        verify(fit, f"fit:{fit['fit_id']}")
    for group in ("source_graphs", "positive_graphs"):
        for step, item in prereg[group].items():
            verify(item, f"{group}:{step}")

    WORK.mkdir(parents=True)
    diagnostic_policy = WORK / "calibration_context_diagnostic.onnx"
    build_diagnostic_policy(diagnostic_policy)
    started = time.time()
    positive_contexts = [
        recover_positive_context(prereg, diagnostic_policy, fit)
        for fit in prereg["fits"]
    ]
    t135b = json.loads(
        Path(prereg["frozen_inputs"]["t135b_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    prior_contexts = t135b["runs"]
    coefficient, intercept, classifier_result = positive_classifier(
        prior_contexts,
        positive_contexts,
    )
    contexts = [*prior_contexts, *positive_contexts]
    graphs = {}
    references = {}
    contracts = {}
    for step in STEPS:
        source = Path(prereg["source_graphs"][step]["path"])
        positive = Path(prereg["positive_graphs"][step]["path"])
        reference_path = (
            WORK / step / "positive_always_on_reference.onnx"
        )
        transformed_path = (
            WORK / step / "three_way_positive_router.onnx"
        )
        references[step] = positive_reference(
            source,
            positive,
            reference_path,
        )
        graphs[step] = transform(
            source,
            positive,
            transformed_path,
            coefficient,
            intercept,
        )
        contracts[step] = equivalence_contract(
            source,
            reference_path,
            transformed_path,
            contexts,
        )
    asset = {
        "schema_version": "open_duck.t156_positive_router.v1",
        "feature": "calibration_context[1,64]",
        "positive_if": (
            "MatMul(context, coefficient) + intercept >= 0"
        ),
        "coefficient": coefficient.astype(float).tolist(),
        "intercept": intercept,
        "source_context_hashes": {
            row_fit: {
                row["population"]: row["context_sha256"]
                for row in contexts
                if row["fit_id"] == row_fit
            }
            for row_fit in sorted({row["fit_id"] for row in contexts})
        },
    }
    asset["asset_sha256"] = canonical_sha256(asset)
    asset_path = WORK / "positive_context_router_asset.json"
    asset_path.write_text(
        json.dumps(asset, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    checks = {
        "two_positive_contexts_hash_exact": (
            len(positive_contexts) == 2
            and all(
                row["context_hash_exact"]
                and len(row["context"]) == 64
                and row["calibration_ticks"] == 250
                for row in positive_contexts
            )
        ),
        "full_positive_classifier_exact": (
            classifier_result["all_labels_exact"]
            and classifier_result[
                "positive_min_minus_nonpositive_max"
            ]
            > 0.0
        ),
        "leave_one_fit_out_classifier_exact": classifier_result[
            "leave_one_fit_out_exact"
        ],
        "all_graph_transforms_exact": all(
            all(
                row[name]
                for name in (
                    "five_nodes_inserted",
                    "source_select_output_rewire_exact",
                    "all_source_nodes_otherwise_byte_exact",
                    "existing_initializers_byte_exact",
                    "five_initializers_added",
                    "positive_tensors_exact",
                    "abi_exact",
                )
            )
            for row in graphs.values()
        ),
        "all_positive_references_exact": all(
            row["identity_exact"] for row in references.values()
        ),
        "all_selected_source_outputs_bit_exact": all(
            row["all_selected_source_outputs_bit_exact"]
            for row in contracts.values()
        ),
        "all_feedback_finite_cpu": all(
            row["all_outputs_finite"]
            and row["all_action_feedback_bit_exact"]
            and row["cpu_only"]
            for row in contracts.values()
        ),
        "both_checkpoints_transformed": set(graphs) == set(STEPS),
        "formal_behavior_cells_zero": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t156_three_way_positive_router_result.v1"
        ),
        "status": (
            "PASS_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
            if passed
            else "HOLD_T156_THREE_WAY_POSITIVE_ROUTER_TRANSFORM"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "positive_contexts": positive_contexts,
        "classifier": {
            **classifier_result,
            "asset": receipt(asset_path),
            "asset_sha256": asset["asset_sha256"],
        },
        "graphs": graphs,
        "positive_references": references,
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "calibration_prefixes": 2,
            "calibration_ticks": 500,
            "diagnostic_behavior_ticks": 2,
            "graphs_transformed": len(graphs),
            "cpu_equivalence_samples": sum(
                row["samples"] for row in contracts.values()
            ),
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T156 three-way positive router transform\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Nominal/negative: exact T143C selected output\n"
        "- Positive COM: exact T154 positive expert through the same "
        "deployment chain\n"
        "- Formal behavior / optimizer / Colab / robot: `0/0/0/0`\n",
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
