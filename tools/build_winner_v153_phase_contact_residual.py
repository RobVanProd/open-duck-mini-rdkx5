#!/usr/bin/env python3
"""Build and contract V153's phase/contact-synchronous residual graph."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRAINING = ROOT / "training"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TRAINING))

from audit_winner_v140_preservation_projected_actor import (  # noqa: E402
    make_dynamic_batch,
)
from build_winner_v148_single_center_residual import (  # noqa: E402
    infer,
    rename_tensor,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v153_phase_contact_residual_preregistration.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
V151_RESULT = ANALYSIS / "winner_v151_bounded_two_center_result.json"
V152_ALIGNMENT = ANALYSIS / "winner_v152_phase_contact_alignment.json"
OUTPUT = ANALYSIS / "winner_v153_phase_contact_residual_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V153_PHASE_CONTACT_RESIDUAL_RESULT_20260725.md"
)
RIGHT_ANKLE = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def append_phase_contact_residual(
    source: onnx.ModelProto,
    *,
    phase: np.ndarray,
    contact: np.ndarray,
    radius_squared: float,
    correction: np.ndarray,
) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_tensor(model, "continuous_actions", "v153_base_actions")
    rename_tensor(
        model, "previous_action_out", "v153_base_previous_action_out"
    )
    values = {
        "v153_phase_indices": np.asarray([99, 100], dtype=np.int64),
        "v153_contact_indices": np.asarray([97, 98], dtype=np.int64),
        "v153_phase": phase[None, :].astype(np.float32),
        "v153_contact": contact[None, :].astype(np.float32),
        "v153_phase_radius_squared": np.asarray(
            [radius_squared], dtype=np.float32
        ),
        "v153_contact_radius_squared": np.asarray([0.0], dtype=np.float32),
        "v153_correction": correction[None, :].astype(np.float32),
    }
    model.graph.initializer.extend(
        numpy_helper.from_array(value, name=name)
        for name, value in values.items()
    )
    model.graph.node.extend(
        [
            helper.make_node(
                "Gather",
                ["obs", "v153_phase_indices"],
                ["v153_observed_phase"],
                axis=1,
                name="v153_gather_phase",
            ),
            helper.make_node(
                "Sub",
                ["v153_observed_phase", "v153_phase"],
                ["v153_phase_delta"],
                name="v153_phase_delta_node",
            ),
            helper.make_node(
                "Mul",
                ["v153_phase_delta", "v153_phase_delta"],
                ["v153_phase_squared_delta"],
                name="v153_phase_square",
            ),
            helper.make_node(
                "ReduceSum",
                ["v153_phase_squared_delta"],
                ["v153_phase_distance_squared"],
                axes=[1],
                keepdims=1,
                name="v153_phase_distance",
            ),
            helper.make_node(
                "LessOrEqual",
                [
                    "v153_phase_distance_squared",
                    "v153_phase_radius_squared",
                ],
                ["v153_phase_inside"],
                name="v153_phase_compare",
            ),
            helper.make_node(
                "Gather",
                ["obs", "v153_contact_indices"],
                ["v153_observed_contact"],
                axis=1,
                name="v153_gather_contact",
            ),
            helper.make_node(
                "Sub",
                ["v153_observed_contact", "v153_contact"],
                ["v153_contact_delta"],
                name="v153_contact_delta_node",
            ),
            helper.make_node(
                "Mul",
                ["v153_contact_delta", "v153_contact_delta"],
                ["v153_contact_squared_delta"],
                name="v153_contact_square",
            ),
            helper.make_node(
                "ReduceSum",
                ["v153_contact_squared_delta"],
                ["v153_contact_distance_squared"],
                axes=[1],
                keepdims=1,
                name="v153_contact_distance",
            ),
            helper.make_node(
                "LessOrEqual",
                [
                    "v153_contact_distance_squared",
                    "v153_contact_radius_squared",
                ],
                ["v153_contact_exact"],
                name="v153_contact_compare",
            ),
            helper.make_node(
                "And",
                ["v153_phase_inside", "v153_contact_exact"],
                ["v153_inside"],
                name="v153_phase_contact_and",
            ),
            helper.make_node(
                "Cast",
                ["v153_inside"],
                ["v153_gate"],
                to=onnx.TensorProto.FLOAT,
                name="v153_gate_cast",
            ),
            helper.make_node(
                "Mul",
                ["v153_gate", "v153_correction"],
                ["v153_gated_correction"],
                name="v153_gate_correction",
            ),
            helper.make_node(
                "Add",
                ["v153_base_actions", "v153_gated_correction"],
                ["continuous_actions"],
                name="v153_apply_correction",
            ),
            helper.make_node(
                "Identity",
                ["continuous_actions"],
                ["previous_action_out"],
                name="v153_realized_feedback",
            ),
        ]
    )
    for output in model.graph.output:
        if output.name == "v153_base_actions":
            output.name = "continuous_actions"
        elif output.name == "v153_base_previous_action_out":
            output.name = "previous_action_out"
    onnx.checker.check_model(model)
    return model


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--source-deployed", type=Path, required=True)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    parser.add_argument("--first-shadow-trace", type=Path, required=True)
    parser.add_argument("--second-shadow-trace", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN, args.work_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V153: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    teacher_root = args.teacher_run_root.resolve()
    first_shadow_trace = args.first_shadow_trace.resolve()
    second_shadow_trace = args.second_shadow_trace.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_transform": sha256(V121_TRANSFORM),
        "v140_result": sha256(V140_RESULT),
        "v144_correction": sha256(V144_CORRECTION),
        "v150_correction": sha256(V150_CORRECTION),
        "v151_result": sha256(V151_RESULT),
        "v152_alignment": sha256(V152_ALIGNMENT),
        "v134_loader": sha256(
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "v145_loader": sha256(
            TRAINING / "winner_v145_on_policy_dagger.py"
        ),
        "source_raw": sha256(source_raw),
        "source_deployed": sha256(source_deployed),
        "first_shadow_trace": sha256(first_shadow_trace),
        "second_shadow_trace": sha256(second_shadow_trace),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V153_PHASE_CONTACT_RESIDUAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V153 preregistration changed")
    alignment = json.loads(V152_ALIGNMENT.read_text(encoding="utf-8"))
    first_label = json.loads(
        V144_CORRECTION.read_text(encoding="utf-8")
    )["causal_result"]["peak_event"]
    second_label = json.loads(
        V150_CORRECTION.read_text(encoding="utf-8")
    )["causal_result"]["event"]
    teacher = v134.load_teacher_dataset(teacher_root)
    first_shadow = dagger.load_shadow_dataset(first_shadow_trace)
    second_shadow = dagger.load_shadow_dataset(second_shadow_trace)
    data = {
        "obs": np.concatenate(
            [teacher["obs"], first_shadow["obs"], second_shadow["obs"]],
            axis=0,
        ),
        "previous_action": np.concatenate(
            [
                teacher["previous_action"],
                first_shadow["previous_action"],
                second_shadow["previous_action"],
            ],
            axis=0,
        ),
        "h_in": np.concatenate(
            [teacher["h_in"], first_shadow["h_in"], second_shadow["h_in"]],
            axis=0,
        ),
    }
    phase = np.asarray(
        alignment["selected_mechanism"]["phase"], dtype=np.float64
    )
    contact = np.asarray(
        alignment["selected_mechanism"]["contacts"], dtype=np.float64
    )
    phases = data["obs"][:, 99:101].astype(np.float64)
    phase_distance = np.sum(np.square(phases - phase[None, :]), axis=1)
    distinct = phase_distance[phase_distance > 0.0]
    nearest_distinct_squared = float(np.min(distinct))
    radius_squared = nearest_distinct_squared * 0.25
    phase_gate = phase_distance <= radius_squared
    contact_gate = np.all(data["obs"][:, 97:99] == contact, axis=1)
    gate = phase_gate & contact_gate
    correction = np.zeros(14, dtype=np.float32)
    correction[RIGHT_ANKLE] = np.float32(
        alignment["selected_mechanism"]["correction"]
    )
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    work.mkdir(parents=True)
    local_raw = work / "winner_v153_phase_contact_raw.onnx"
    local_deployed = work / "winner_v153_phase_contact_deployed.onnx"
    model = append_phase_contact_residual(
        onnx.load(source_raw),
        phase=phase,
        contact=contact,
        radius_squared=radius_squared,
        correction=correction,
    )
    onnx.save(model, local_raw)
    contract = deploy_graph(local_raw, local_deployed, transform)
    source_dynamic = work / "winner_v153_source_dynamic.onnx"
    local_dynamic = work / "winner_v153_local_dynamic.onnx"
    onnx.save(make_dynamic_batch(onnx.load(source_deployed)), source_dynamic)
    onnx.save(make_dynamic_batch(onnx.load(local_deployed)), local_dynamic)
    source_action, source_previous, source_hidden = infer(
        source_dynamic, data
    )
    local_action, local_previous, local_hidden = infer(local_dynamic, data)
    delta = local_action - source_action
    changed_elements = np.argwhere(np.abs(delta) > 1.0e-7)
    changed_rows = np.unique(changed_elements[:, 0])
    changed_joints = np.unique(changed_elements[:, 1])
    first_index = 4_800 + int(first_label["source_tick"])
    second_index = 4_800 + 600 + int(second_label["source_tick"])
    first_delta = float(delta[first_index, RIGHT_ANKLE])
    second_delta = float(delta[second_index, RIGHT_ANKLE])
    first_target = float(first_label["final_action"][RIGHT_ANKLE])
    second_target = float(second_label["final_action"][RIGHT_ANKLE])
    x0 = np.abs(data["obs"][:, 6]) <= 0.01
    checks = {
        "dataset_exact_6000": data["obs"].shape == (6_000, 115),
        "phase_radius_derived_from_nearest_distinct_sample": (
            nearest_distinct_squared > 0.0
            and radius_squared == nearest_distinct_squared * 0.25
        ),
        "both_causal_precursors_inside_phase_contact_gate": (
            bool(gate[first_index]) and bool(gate[second_index])
        ),
        "gate_has_periodic_support": int(np.sum(gate)) > 2,
        "changes_only_inside_phase_contact_gate": bool(
            np.all(gate[changed_rows])
        ),
        "changes_only_right_ankle": changed_joints.tolist() == [RIGHT_ANKLE],
        "first_center_receives_frozen_max_correction": (
            abs(first_delta - float(correction[RIGHT_ANKLE])) <= 5.0e-7
            and abs(
                float(local_action[first_index, RIGHT_ANKLE]) - first_target
            )
            <= 5.0e-7
        ),
        "second_center_receives_same_conservative_correction": (
            abs(second_delta - float(correction[RIGHT_ANKLE])) <= 5.0e-7
            and float(local_action[second_index, RIGHT_ANKLE])
            >= second_target - 5.0e-7
        ),
        "x0_deadband_remains_exact": bool(
            np.count_nonzero(local_action[x0]) == 0
        ),
        "realized_previous_action_exact": bool(
            np.array_equal(local_action, local_previous)
        ),
        "hidden_output_bit_exact": bool(
            np.array_equal(source_hidden, local_hidden)
        ),
        "source_previous_action_contract_preserved": bool(
            np.array_equal(source_action, source_previous)
        ),
        "deployment_contract_green": contract["inference"]["pass"],
        "no_state_local_center_initializers": not any(
            initializer.name.startswith(("v148_", "v151_"))
            for initializer in model.graph.initializer
        ),
        "no_training_behavior_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v153.phase_contact_residual_result.v1",
        "status": (
            "PASS_WINNER_V153_PHASE_CONTACT_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V153_PHASE_CONTACT_RESIDUAL"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "gate": {
            "phase": phase.tolist(),
            "contact": contact.tolist(),
            "nearest_distinct_phase_distance_squared": (
                nearest_distinct_squared
            ),
            "radius_squared": radius_squared,
            "aggregate_gate_rows": np.flatnonzero(gate).tolist(),
            "aggregate_gate_count": int(np.sum(gate)),
            "changed_rows": changed_rows.tolist(),
            "changed_elements": changed_elements.tolist(),
        },
        "correction": {
            "joint": RIGHT_ANKLE,
            "value": float(correction[RIGHT_ANKLE]),
            "first_center_delta": first_delta,
            "second_center_delta": second_delta,
            "first_target_error": abs(
                float(local_action[first_index, RIGHT_ANKLE]) - first_target
            ),
            "second_target_overshoot": (
                float(local_action[second_index, RIGHT_ANKLE])
                - second_target
            ),
        },
        "artifact": {
            "raw": {"path": str(local_raw), "sha256": sha256(local_raw)},
            "deployed": contract,
            "work_root": str(work),
        },
        "decision": (
            "EARN_ONE_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_PHASE_CONTACT_RESIDUAL"
        ),
        "authority": {
            "v154_behavior_preregistration": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V153 phase/contact residual\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Phase/contact gate rows: `{int(np.sum(gate))}` of 6,000.\n"
        f"- Right-ankle correction: `{correction[RIGHT_ANKLE]}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU graph contract only; no behavior, training, Colab, or "
        "hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
