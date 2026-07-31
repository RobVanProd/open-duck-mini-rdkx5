#!/usr/bin/env python3
"""Attribute T164's Y-negative persistence gap to one exact adapter pair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = (
    ANALYSIS / "t168_nominal_adapter_persistence_attribution_preregistration.json"
)
RESULT = ANALYSIS / "t168_nominal_adapter_persistence_attribution_result.json"
MARKDOWN = (
    ANALYSIS / "T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t168_nominal_adapter_persistence_attribution_v1"
)

GROUPS = {
    "negative_expert": [
        "negative_adapter_weight",
        "negative_adapter_bias",
    ],
    "nominal_expert": [
        "nominal_condition_negative_adapter_weight",
        "nominal_condition_negative_adapter_bias",
    ],
    "positive_expert": [
        "positive_adapter_weight",
        "positive_adapter_bias",
    ],
    "positive_endpoint": ["t162_endpoint_command"],
}
EXPECTED_COMPOSED_DIFFERENCES = sorted(
    name for names in GROUPS.values() for name in names
)
EXPECTED_RAW_DIFFERENCES = [
    "negative_adapter_bias",
    "negative_adapter_weight",
]
OUTPUT_NAMES = [
    "continuous_actions",
    "h_out",
    "previous_action_out",
]


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def replace(
    model: onnx.ModelProto,
    name: str,
    value: np.ndarray,
) -> None:
    for index, item in enumerate(model.graph.initializer):
        if item.name == name:
            model.graph.initializer[index].CopyFrom(
                numpy_helper.from_array(value, name=name)
            )
            return
    raise KeyError(name)


def graph_difference(left: Path, right: Path) -> dict[str, Any]:
    a = onnx.load(left)
    b = onnx.load(right)
    ai = arrays(a)
    bi = arrays(b)
    node_differences = [
        index
        for index, (x, y) in enumerate(
            zip(a.graph.node, b.graph.node, strict=True)
        )
        if x.SerializeToString() != y.SerializeToString()
    ]
    changed = sorted(
        name
        for name in ai
        if not np.array_equal(ai[name], bi[name])
    )
    return {
        "left_nodes": len(a.graph.node),
        "right_nodes": len(b.graph.node),
        "node_differences": node_differences,
        "nodes_byte_exact": (
            len(a.graph.node) == len(b.graph.node) and not node_differences
        ),
        "initializer_names_exact": set(ai) == set(bi),
        "changed_initializers": changed,
        "all_arrays_finite": all(
            np.all(np.isfinite(value))
            for value in [*ai.values(), *bi.values()]
        ),
    }


def build_variants(
    half_path: Path,
    final_path: Path,
) -> tuple[dict[str, Path], dict[str, Any]]:
    half = onnx.load(half_path)
    final = onnx.load(final_path)
    half_arrays = arrays(half)
    final_arrays = arrays(final)
    changed = sorted(
        name
        for name in half_arrays
        if not np.array_equal(half_arrays[name], final_arrays[name])
    )
    if changed != EXPECTED_COMPOSED_DIFFERENCES:
        raise RuntimeError(f"T168 composed graph scope changed: {changed}")
    paths = {
        "half": half_path,
        "final": final_path,
    }
    for group, names in GROUPS.items():
        model = onnx.load(half_path)
        for name in names:
            replace(model, name, final_arrays[name])
        onnx.checker.check_model(model)
        path = WORK / f"half_with_final_{group}.onnx"
        onnx.save(model, path)
        paths[group] = path
    return paths, {
        "changed_initializers": changed,
        "expected_changed_initializers": EXPECTED_COMPOSED_DIFFERENCES,
        "only_expected_groups_differ": changed
        == EXPECTED_COMPOSED_DIFFERENCES,
    }


def route_rows(
    contexts: list[dict[str, Any]],
    graph: Path,
) -> list[dict[str, Any]]:
    values = arrays(onnx.load(graph))
    negative_coefficient = values[
        "conditional_path_router_coefficient"
    ]
    negative_intercept = values["conditional_path_router_intercept"]
    positive_coefficient = values["positive_router_coefficient"]
    positive_intercept = values["positive_router_intercept"]
    output = []
    for row in contexts:
        context = np.asarray(row["context"], dtype=np.float32).reshape(1, 64)
        negative_score = float(
            (
                context @ negative_coefficient + negative_intercept
            ).reshape(-1)[0]
        )
        positive_score = float(
            (
                context @ positive_coefficient + positive_intercept
            ).reshape(-1)[0]
        )
        route = (
            "positive_expert"
            if positive_score >= 0.0
            else "negative_expert"
            if negative_score >= 0.0
            else "nominal_expert"
        )
        output.append(
            {
                "condition_id": row["condition_id"],
                "fit_id": row["fit_id"],
                "context_sha256": row["context_sha256"],
                "negative_router_score": negative_score,
                "positive_router_score": positive_score,
                "active_route": route,
            }
        )
    return output


def make_session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def exact_outputs(
    left: list[np.ndarray],
    right: list[np.ndarray],
) -> bool:
    return all(
        np.array_equal(a, b)
        for a, b in zip(left, right, strict=True)
    )


def finite_outputs(values: list[np.ndarray]) -> bool:
    return all(np.all(np.isfinite(value)) for value in values)


def replay(
    sessions: dict[str, ort.InferenceSession],
    traces: list[dict[str, Any]],
    contexts: dict[str, np.ndarray],
) -> dict[str, Any]:
    rows = 0
    all_finite = True
    nominal_matches_final = 0
    inactive_match_half = {
        name: 0
        for name in ("negative_expert", "positive_expert", "positive_endpoint")
    }
    half_final_action_different = 0
    maximum_half_final_action_delta = 0.0
    by_fit: dict[str, dict[str, Any]] = {}
    for trace in traces:
        trace_rows = [
            json.loads(line)
            for line in Path(trace["path"]).read_text(
                encoding="utf-8"
            ).splitlines()
        ]
        if len(trace_rows) != trace["rows"]:
            raise RuntimeError(f"T168 trace row count changed: {trace['path']}")
        fit_id = trace["fit_id"]
        summary = by_fit.setdefault(
            fit_id,
            {
                "rows": 0,
                "nominal_matches_final": 0,
                "inactive_match_half": {
                    name: 0 for name in inactive_match_half
                },
                "half_final_action_different": 0,
            },
        )
        for row in trace_rows:
            state = row["policy_state_input"]
            feed = {
                "obs": np.asarray(row["obs_state"], np.float32)[None, :],
                "previous_action": np.asarray(
                    state["previous_action"], np.float32
                ),
                "h_in": np.asarray(state["h_in"], np.float32),
                "calibration_context": contexts[fit_id],
            }
            output = {
                name: session.run(OUTPUT_NAMES, feed)
                for name, session in sessions.items()
            }
            rows += 1
            summary["rows"] += 1
            all_finite = all_finite and all(
                finite_outputs(value) for value in output.values()
            )
            if exact_outputs(
                output["nominal_expert"], output["final"]
            ):
                nominal_matches_final += 1
                summary["nominal_matches_final"] += 1
            for name in inactive_match_half:
                if exact_outputs(output[name], output["half"]):
                    inactive_match_half[name] += 1
                    summary["inactive_match_half"][name] += 1
            delta = float(
                np.max(
                    np.abs(
                        output["half"][0].astype(np.float64)
                        - output["final"][0].astype(np.float64)
                    )
                )
            )
            maximum_half_final_action_delta = max(
                maximum_half_final_action_delta, delta
            )
            if delta > 0.0:
                half_final_action_different += 1
                summary["half_final_action_different"] += 1
    return {
        "rows": rows,
        "all_outputs_finite": all_finite,
        "nominal_hybrid_matches_final_rows": nominal_matches_final,
        "inactive_hybrid_matches_half_rows": inactive_match_half,
        "half_final_action_different_rows": half_final_action_different,
        "maximum_half_final_action_delta": maximum_half_final_action_delta,
        "by_fit": by_fit,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T168 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T168: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to overwrite T168 work: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T168 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T168 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    for name, item in prereg["graphs"].items():
        verify(item, name)
    for index, item in enumerate(prereg["traces"]):
        verify(item, f"trace:{index}")

    t167 = json.loads(
        Path(prereg["frozen_inputs"]["t167_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    if (
        t167["status"] != "HOLD_T167_CALIBRATION_CONTEXT_SEPARABILITY"
        or t167["decision"] != "CLOSE_STATIC_CALIBRATION_ROUTING_FOR_Y_NEGATIVE"
        or t167["summary"]["prior_hash_matches"] != 18
    ):
        raise RuntimeError("T168 T167 prerequisite changed")
    half_path = Path(prereg["graphs"]["composed_half"]["path"])
    final_path = Path(prereg["graphs"]["composed_final"]["path"])
    raw_half = Path(prereg["graphs"]["raw_t100c_half"]["path"])
    raw_final = Path(prereg["graphs"]["raw_t100c_final"]["path"])
    composed_difference = graph_difference(half_path, final_path)
    raw_difference = graph_difference(raw_half, raw_final)
    composed_half = arrays(onnx.load(half_path))
    composed_final = arrays(onnx.load(final_path))
    raw_half_values = arrays(onnx.load(raw_half))
    raw_final_values = arrays(onnx.load(raw_final))
    nominal_source_binding = {
        "half_weight_exact": np.array_equal(
            composed_half["nominal_condition_negative_adapter_weight"],
            raw_half_values["negative_adapter_weight"],
        ),
        "half_bias_exact": np.array_equal(
            composed_half["nominal_condition_negative_adapter_bias"],
            raw_half_values["negative_adapter_bias"],
        ),
        "final_weight_exact": np.array_equal(
            composed_final["nominal_condition_negative_adapter_weight"],
            raw_final_values["negative_adapter_weight"],
        ),
        "final_bias_exact": np.array_equal(
            composed_final["nominal_condition_negative_adapter_bias"],
            raw_final_values["negative_adapter_bias"],
        ),
    }

    WORK.mkdir(parents=True)
    variant_paths, variant_scope = build_variants(half_path, final_path)
    contexts = [
        row
        for row in t167["cells"]
        if row["condition_id"] == "TORSO_COM_Y_NEG"
    ]
    routes = route_rows(t167["cells"], half_path)
    y_routes = [
        row
        for row in routes
        if row["condition_id"] == "TORSO_COM_Y_NEG"
    ]
    context_by_fit = {
        row["fit_id"]: np.asarray(
            row["context"], dtype=np.float32
        ).reshape(1, 64)
        for row in contexts
    }
    sessions = {
        name: make_session(path)
        for name, path in variant_paths.items()
    }
    replay_result = replay(sessions, prereg["traces"], context_by_fit)
    rows = replay_result["rows"]
    inactive = replay_result["inactive_hybrid_matches_half_rows"]
    checks = {
        "t167_closed_static_y_router_with_all_prior_hashes_exact": True,
        "composed_nodes_exact_and_only_seven_expected_constants_differ": (
            composed_difference["nodes_byte_exact"]
            and composed_difference["initializer_names_exact"]
            and composed_difference["changed_initializers"]
            == EXPECTED_COMPOSED_DIFFERENCES
            and composed_difference["all_arrays_finite"]
            and variant_scope["only_expected_groups_differ"]
        ),
        "raw_t100c_nodes_exact_and_only_nominal_adapter_pair_differs": (
            raw_difference["nodes_byte_exact"]
            and raw_difference["initializer_names_exact"]
            and raw_difference["changed_initializers"]
            == EXPECTED_RAW_DIFFERENCES
            and raw_difference["all_arrays_finite"]
        ),
        "composed_nominal_pair_is_exact_raw_t100c_pair": all(
            nominal_source_binding.values()
        ),
        "both_y_negative_contexts_take_nominal_route": (
            len(y_routes) == 2
            and all(
                row["active_route"] == "nominal_expert"
                and row["negative_router_score"] < 0.0
                and row["positive_router_score"] < 0.0
                for row in y_routes
            )
        ),
        "nominal_pair_swap_recreates_final_on_every_protected_row": (
            rows > 0
            and replay_result["nominal_hybrid_matches_final_rows"] == rows
        ),
        "inactive_group_swaps_preserve_half_on_every_protected_row": (
            rows > 0
            and all(value == rows for value in inactive.values())
        ),
        "half_final_action_difference_is_observable": (
            replay_result["half_final_action_different_rows"] > 0
            and replay_result["maximum_half_final_action_delta"] > 0.0
        ),
        "all_inference_outputs_finite": replay_result[
            "all_outputs_finite"
        ],
        "stored_inference_only_no_simulator_behavior_optimizer_colab_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t168_nominal_adapter_persistence_attribution_result.v1"
        ),
        "status": (
            "PASS_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
            if passed
            else "HOLD_T168_NOMINAL_ADAPTER_PERSISTENCE_ATTRIBUTION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "composed_graph_difference": composed_difference,
        "raw_t100c_graph_difference": raw_difference,
        "nominal_source_binding": nominal_source_binding,
        "routes": routes,
        "y_negative_routes": y_routes,
        "variant_scope": variant_scope,
        "variant_paths": {
            name: str(path) for name, path in variant_paths.items()
        },
        "stored_trace_replay": replay_result,
        "execution": {
            "stored_inference_rows": rows,
            "onnx_variants": len(variant_paths),
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority"],
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T168 nominal-adapter persistence attribution result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Y-negative routes: "
        f"`{[row['active_route'] for row in y_routes]}`\n"
        f"- Protected inference rows: `{rows}`\n"
        "- Nominal hybrid equals final: "
        f"`{replay_result['nominal_hybrid_matches_final_rows']}/{rows}`\n"
        "- Half/final differing action rows: "
        f"`{replay_result['half_final_action_different_rows']}/{rows}`\n"
        "- Simulator / behavior / optimizer / Colab / robot: "
        "`0 / 0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(value["decision"])
    print(json.dumps(replay_result, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
