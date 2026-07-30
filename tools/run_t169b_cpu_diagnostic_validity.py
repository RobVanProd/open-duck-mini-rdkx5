#!/usr/bin/env python3
"""Audit T169's endpoint representation and saturated random population."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t169b_cpu_diagnostic_validity_preregistration.json"
RESULT = ANALYSIS / "t169b_cpu_diagnostic_validity_result.json"
MARKDOWN = (
    ANALYSIS / "T169B_CPU_DIAGNOSTIC_VALIDITY_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t169b_cpu_diagnostic_validity_v1"
)
OUTPUTS = {
    "hidden_gate_score": [1, 1],
    "negative_adapter_location": [1, 14],
    "conditional_adapter_location": [1, 14],
    "anchored_location": [1, 14],
    "raw_continuous_actions": [1, 14],
}


def instrument(source: Path, destination: Path) -> Path:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    graph_values = {
        value
        for node in model.graph.node
        for value in [*node.input, *node.output]
    }
    for name, shape in OUTPUTS.items():
        if name not in graph_values:
            raise RuntimeError(f"T169B missing graph value: {name}")
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name, TensorProto.FLOAT, shape
                )
            )
    onnx.checker.check_model(model)
    onnx.save(model, destination)
    return destination


def random_audit(
    initial: Path,
    final: Path,
    *,
    seed: int,
    rows: int,
) -> dict[str, Any]:
    left = ort.InferenceSession(
        str(instrument(initial, WORK / "initial_instrumented.onnx")),
        providers=["CPUExecutionProvider"],
    )
    right = ort.InferenceSession(
        str(instrument(final, WORK / "final_instrumented.onnx")),
        providers=["CPUExecutionProvider"],
    )
    names = list(OUTPUTS)
    rng = np.random.default_rng(seed)
    gate_active_rows = 0
    head_changed_rows = 0
    conditional_changed_rows = 0
    anchored_changed_rows = 0
    raw_changed_rows = 0
    anchored_changed_elements = 0
    changed_elements_raw_exact_saturation = 0
    maximum = {
        "head_delta": 0.0,
        "conditional_delta": 0.0,
        "anchored_delta": 0.0,
        "raw_delta": 0.0,
        "abs_anchored_location": 0.0,
    }
    for _ in range(rows):
        feed = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": rng.uniform(
                -0.5, 0.5, size=(1, 14)
            ).astype(np.float32),
            "h_in": rng.normal(size=(1, 64)).astype(np.float32),
        }
        before = dict(zip(names, left.run(names, feed), strict=True))
        after = dict(zip(names, right.run(names, feed), strict=True))
        gate_active_rows += int(
            float(before["hidden_gate_score"][0, 0]) >= 0.0
        )
        changes = {}
        for label, name in (
            ("head", "negative_adapter_location"),
            ("conditional", "conditional_adapter_location"),
            ("anchored", "anchored_location"),
            ("raw", "raw_continuous_actions"),
        ):
            delta = np.abs(
                before[name].astype(np.float64)
                - after[name].astype(np.float64)
            )
            changes[label] = delta
            maximum[f"{label}_delta"] = max(
                maximum[f"{label}_delta"], float(np.max(delta))
            )
        head_changed_rows += int(np.any(changes["head"] > 0.0))
        conditional_changed_rows += int(
            np.any(changes["conditional"] > 0.0)
        )
        anchored_changed_rows += int(
            np.any(changes["anchored"] > 0.0)
        )
        raw_changed_rows += int(np.any(changes["raw"] > 0.0))
        mask = changes["anchored"] > 0.0
        anchored_changed_elements += int(np.count_nonzero(mask))
        changed_elements_raw_exact_saturation += int(
            np.count_nonzero(
                mask
                & (np.abs(before["raw_continuous_actions"]) == 1.0)
                & (
                    before["raw_continuous_actions"]
                    == after["raw_continuous_actions"]
                )
            )
        )
        if np.any(mask):
            maximum["abs_anchored_location"] = max(
                maximum["abs_anchored_location"],
                float(np.max(np.abs(before["anchored_location"][mask]))),
            )
    return {
        "rows": rows,
        "seed": seed,
        "gate_active_rows": gate_active_rows,
        "head_changed_rows": head_changed_rows,
        "conditional_changed_rows": conditional_changed_rows,
        "anchored_changed_rows": anchored_changed_rows,
        "raw_changed_rows": raw_changed_rows,
        "anchored_changed_elements": anchored_changed_elements,
        "changed_elements_raw_exact_saturation": (
            changed_elements_raw_exact_saturation
        ),
        "maximum": maximum,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T169B requires --read-only-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T169B: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to overwrite T169B work: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T169B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T169B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    t169_prereg = json.loads(
        Path(
            prereg["frozen_inputs"]["t169_preregistration"]["path"]
        ).read_text(encoding="utf-8")
    )
    t169 = json.loads(
        Path(prereg["frozen_inputs"]["t169_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    expected = np.asarray(
        t169_prereg["mechanism"]["endpoint_offsets_m"],
        dtype=np.float32,
    )
    actual = np.asarray(
        t169["endpoint_contract"]["offsets_m"],
        dtype=np.float32,
    )
    endpoint = {
        "shape_exact": expected.shape == actual.shape == (8, 3),
        "float32_bit_exact": np.array_equal(expected, actual),
        "maximum_abs_error": float(
            np.max(
                np.abs(
                    expected.astype(np.float64)
                    - actual.astype(np.float64)
                )
            )
        ),
        "expected": expected.astype(float).tolist(),
        "actual": actual.astype(float).tolist(),
    }
    WORK.mkdir(parents=True)
    population = prereg["audit"]["random_population"]
    random = random_audit(
        Path(prereg["frozen_inputs"]["step0_graph"]["path"]),
        Path(prereg["frozen_inputs"]["step1024_graph"]["path"]),
        seed=int(population["seed"]),
        rows=int(population["rows"]),
    )
    protected = t169["causal_contract"]["postupdate_trace"]
    remaining_checks = {
        name: passed
        for name, passed in t169["checks"].items()
        if name
        not in {
            "eight_stratum_model_contract_exact",
            "postupdate_random_action_binding",
        }
    }
    checks = {
        "all_remaining_t169_checks_green": all(
            remaining_checks.values()
        ),
        "endpoint_float32_representation_is_bit_exact": (
            endpoint["shape_exact"]
            and endpoint["float32_bit_exact"]
            and endpoint["maximum_abs_error"] == 0.0
        ),
        "random_population_reaches_updated_head": (
            random["head_changed_rows"] == random["rows"]
            and random["maximum"]["head_delta"] > 0.0
        ),
        "dynamic_gate_activates_and_binds_intermediate_update": (
            random["gate_active_rows"] > 0
            and random["conditional_changed_rows"]
            == random["gate_active_rows"]
            and random["anchored_changed_rows"]
            == random["gate_active_rows"]
            and random["maximum"]["conditional_delta"] > 0.0
            and random["maximum"]["anchored_delta"] > 0.0
        ),
        "all_masked_random_action_changes_are_exact_tanh_saturation": (
            random["anchored_changed_elements"] > 0
            and random["raw_changed_rows"] == 0
            and random["changed_elements_raw_exact_saturation"]
            == random["anchored_changed_elements"]
        ),
        "protected_in_distribution_trace_binds_final_action": (
            protected["rows"] == 72
            and protected["final_changed_fraction"] >= 0.05
            and protected["maximum_final_action_delta"] > 0.0
            and protected["maximum_hidden_delta"] == 0.0
        ),
        "read_only_no_optimizer_simulator_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t169b_cpu_diagnostic_validity_result.v1"
        ),
        "status": (
            "PASS_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
            if passed
            else "HOLD_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "endpoint_representation": endpoint,
        "random_population": random,
        "protected_trace_binding": protected,
        "remaining_t169_checks": remaining_checks,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "stored_onnx_inference_rows": random["rows"],
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
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
        "# T169B CPU diagnostic-validity result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Endpoint float32 equality: "
        f"`{endpoint['float32_bit_exact']}`\n"
        "- Random gate/head/conditional/anchored/raw changed rows: "
        f"`{random['gate_active_rows']}/{random['head_changed_rows']}/"
        f"{random['conditional_changed_rows']}/"
        f"{random['anchored_changed_rows']}/"
        f"{random['raw_changed_rows']}`\n"
        "- Changed anchored elements at exact tanh saturation: "
        f"`{random['changed_elements_raw_exact_saturation']}/"
        f"{random['anchored_changed_elements']}`\n"
        "- Optimizer / simulator / behavior / hosted / robot: "
        "`0 / 0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(value["decision"])
    print(f"failed_checks={failed}")
    print(json.dumps(random, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
