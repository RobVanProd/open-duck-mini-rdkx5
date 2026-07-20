#!/usr/bin/env python3
"""Run the zero-behavior winner-v9 stored-bound contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
import onnxruntime as ort

from run_winner_v8_physical_envelope_contract import (
    abi,
    chain,
    initializers,
    replace_initializer,
    stress,
    transform_xml,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "winner_v9_stored_bound_contract_preregistration.json"
MARGIN = np.float32(4.0) * np.finfo(np.float32).eps


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def transform_graph(
    source: onnx.ModelProto,
    stored_delta: np.ndarray,
    internal_delta: np.ndarray,
) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    replace_initializer(model, "max_action_delta", stored_delta)
    replace_initializer(model, "v7_safe_max_action_delta", internal_delta)
    model.graph.name = "winner_v9_inward_stored_physical_boundary"
    model.producer_name = "open-duck-winner-v9"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    return model


def graph_change(
    source: onnx.ModelProto,
    output: onnx.ModelProto,
    stored_delta: np.ndarray,
    internal_delta: np.ndarray,
) -> dict[str, object]:
    source_inits = initializers(source)
    output_inits = initializers(output)
    changed = sorted(
        name
        for name, value in source_inits.items()
        if not np.array_equal(value, output_inits[name])
    )
    return {
        "changed_initializers": changed,
        "nodes_exact": [node.SerializeToString() for node in source.graph.node]
        == [node.SerializeToString() for node in output.graph.node],
        "unchanged_initializers_exact": all(
            np.array_equal(value, output_inits[name])
            for name, value in source_inits.items()
            if name not in changed
        ),
        "abi_exact": abi(source) == abi(output),
        "stored_delta_exact": np.array_equal(
            output_inits["max_action_delta"], stored_delta
        ),
        "internal_delta_exact": np.array_equal(
            output_inits["v7_safe_max_action_delta"], internal_delta
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-half", type=Path, required=True)
    parser.add_argument("--source-final", type=Path, required=True)
    parser.add_argument("--model-xml", type=Path, required=True)
    parser.add_argument("--scene-xml", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("winner-v9 output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    frozen = prereg["frozen_inputs"]
    observed = {
        "runner_sha256": sha256(Path(__file__)),
        "helper_sha256": sha256(
            ROOT / "tools/run_winner_v8_physical_envelope_contract.py"
        ),
        "source_half_sha256": sha256(args.source_half),
        "source_final_sha256": sha256(args.source_final),
        "model_xml_sha256": sha256(args.model_xml),
        "scene_xml_sha256": sha256(args.scene_xml),
        "numeric_attribution_sha256": sha256(
            ROOT / frozen["numeric_attribution"]["path"]
        ),
    }
    expected = {
        "runner_sha256": frozen["runner_sha256"],
        "helper_sha256": frozen["helper_sha256"],
        "source_half_sha256": frozen["source_half"]["sha256"],
        "source_final_sha256": frozen["source_final"]["sha256"],
        "model_xml_sha256": frozen["model_xml_sha256"],
        "scene_xml_sha256": frozen["scene_xml_sha256"],
        "numeric_attribution_sha256": frozen["numeric_attribution"]["sha256"],
    }
    if observed != expected:
        raise ValueError("winner-v9 frozen input mismatch")

    rates = np.asarray(
        prereg["transform"]["full_measured_rate_limits_rad_s"], dtype=np.float32
    )
    nominal_delta = rates * np.float32(0.02 / 0.25)
    stored_delta = np.nextafter(nominal_delta, np.float32(-np.inf))
    internal_delta = np.nextafter(
        stored_delta - MARGIN, np.float32(-np.inf)
    )
    policies = []
    for index, (label, source_path) in enumerate(
        (("half", args.source_half), ("final", args.source_final))
    ):
        source_model = onnx.load(source_path)
        transformed = transform_graph(
            source_model,
            stored_delta.reshape(1, 14),
            internal_delta.reshape(1, 14),
        )
        output_path = work_root / f"winner_v9_{label}_stored_bound.onnx"
        onnx.save(transformed, output_path)
        session = ort.InferenceSession(
            str(output_path), providers=["CPUExecutionProvider"]
        )
        output_inits = initializers(transformed)
        policies.append(
            {
                "label": label,
                "source_path": str(source_path),
                "source_sha256": sha256(source_path),
                "output_path": str(output_path),
                "output_sha256": sha256(output_path),
                "output_bytes": output_path.stat().st_size,
                "abi": abi(transformed),
                "graph_change": graph_change(
                    source_model,
                    transformed,
                    stored_delta.reshape(1, 14),
                    internal_delta.reshape(1, 14),
                ),
                "stress": stress(
                    session, stored_delta.reshape(1, 14), 90770 + index, 4096
                ),
                "x0_chain": chain(
                    session,
                    output_inits,
                    stored_delta.reshape(1, 14),
                    90780 + index,
                    0.0,
                    256,
                ),
                "moving_chain": chain(
                    session,
                    output_inits,
                    stored_delta.reshape(1, 14),
                    90740 + index,
                    0.077,
                    256,
                ),
            }
        )
    xml = transform_xml(
        args.model_xml,
        args.scene_xml,
        work_root / "xmls",
        float(prereg["transform"]["physical_force_limit_nm"]),
    )
    checks = {
        "frozen_inputs_exact": observed == expected,
        "both_abis_exact": all(
            row["abi"] == prereg["expected_abi"] for row in policies
        ),
        "only_two_analytically_rounded_initializers_changed": all(
            row["graph_change"]["changed_initializers"]
            == ["max_action_delta", "v7_safe_max_action_delta"]
            and row["graph_change"]["nodes_exact"]
            and row["graph_change"]["unchanged_initializers_exact"]
            and row["graph_change"]["abi_exact"]
            and row["graph_change"]["stored_delta_exact"]
            and row["graph_change"]["internal_delta_exact"]
            for row in policies
        ),
        "all_8192_stress_cases_obey_stored_bound": all(
            row["stress"]["strictly_bounded"]
            and row["stress"]["state_equals_action_bit_exact"]
            for row in policies
        ),
        "both_256_tick_x0_chains_exact_zero": all(
            row["x0_chain"]["zero_action_and_state_exact"]
            and row["x0_chain"]["strictly_bounded"]
            for row in policies
        ),
        "both_256_tick_moving_chains_obey_stored_bound": all(
            row["moving_chain"]["strictly_bounded"]
            and row["moving_chain"]["all_finite"]
            for row in policies
        ),
        "xml_physical_force_contract_exact": xml[
            "only_active_range_text_changed"
        ]
        and xml["output_scene_sha256"] == xml["source_scene_sha256"]
        and xml["actuator_count"] == 14
        and xml["all_actuators_inherit_sts3215"]
        and xml["force_range_nm"]
        == [
            -float(prereg["transform"]["physical_force_limit_nm"]),
            float(prereg["transform"]["physical_force_limit_nm"]),
        ],
        "cpu_only_no_behavior_or_training": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_WINNER_V9_STORED_BOUND_CONTRACT"
        if not failed
        else "HOLD_WINNER_V9_STORED_BOUND_CONTRACT"
    )
    payload = {
        "schema_version": "open_duck_mini.winner_v9_stored_bound_contract_result.v1",
        "status": status,
        "decision": "AUTHORIZE_SEPARATE_WINNER_V9_NOMINAL_PREREGISTRATION_ONLY"
        if not failed
        else "CLOSE_WINNER_V9_STORED_BOUND_ROUTE",
        "preregistration_sha256": sha256(PREREG),
        "checks": checks,
        "failed_checks": failed,
        "observed_input_hashes": observed,
        "rate_limits_rad_s": rates.tolist(),
        "nominal_delta": nominal_delta.tolist(),
        "stored_delta": stored_delta.tolist(),
        "internal_delta": internal_delta.tolist(),
        "policies": policies,
        "xml": xml,
        "authority": {
            "behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
