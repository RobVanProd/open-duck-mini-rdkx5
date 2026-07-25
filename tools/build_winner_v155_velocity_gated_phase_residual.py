#!/usr/bin/env python3
"""Build and contract V155's velocity-gated phase/contact residual."""

from __future__ import annotations

import argparse
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
)
from build_winner_v153_phase_contact_residual import (  # noqa: E402
    append_phase_contact_residual,
)
from run_winner_v129_oracle_teacher_cpu_contract import (  # noqa: E402
    deploy_graph,
)
import winner_v134_full_actor_teacher_distillation as v134  # noqa: E402
import winner_v145_on_policy_dagger as dagger  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v155_velocity_gated_phase_residual_preregistration.json"
)
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
V153_RESULT = ANALYSIS / "winner_v153_phase_contact_residual_result.json"
V154_RESULT = (
    ANALYSIS / "winner_v154_phase_contact_causal_behavior_result.json"
)
OUTPUT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
MARKDOWN = (
    ANALYSIS / "WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL_RESULT_20260725.md"
)
RIGHT_ANKLE = 13
VELOCITY_OBS = 40


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def append_velocity_gate(
    source: onnx.ModelProto,
    *,
    phase: np.ndarray,
    contact: np.ndarray,
    radius_squared: float,
    velocity_threshold: float,
    correction: np.ndarray,
) -> onnx.ModelProto:
    model = append_phase_contact_residual(
        source,
        phase=phase,
        contact=contact,
        radius_squared=radius_squared,
        correction=correction,
    )
    model.graph.initializer.extend(
        [
            numpy_helper.from_array(
                np.asarray([VELOCITY_OBS], dtype=np.int64),
                name="v155_velocity_index",
            ),
            numpy_helper.from_array(
                np.asarray([[velocity_threshold]], dtype=np.float32),
                name="v155_velocity_threshold",
            ),
        ]
    )
    cast_index = next(
        index
        for index, node in enumerate(model.graph.node)
        if node.name == "v153_gate_cast"
    )
    cast = model.graph.node[cast_index]
    if list(cast.input) != ["v153_inside"]:
        raise ValueError("unexpected V153 gate cast")
    cast.input[0] = "v155_inside"
    inserted = [
        helper.make_node(
            "Gather",
            ["obs", "v155_velocity_index"],
            ["v155_observed_velocity"],
            axis=1,
            name="v155_gather_velocity",
        ),
        helper.make_node(
            "Greater",
            ["v155_observed_velocity", "v155_velocity_threshold"],
            ["v155_velocity_above"],
            name="v155_velocity_compare",
        ),
        helper.make_node(
            "And",
            ["v153_inside", "v155_velocity_above"],
            ["v155_inside"],
            name="v155_state_gate",
        ),
    ]
    for offset, node in enumerate(inserted):
        model.graph.node.insert(cast_index + offset, node)
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
            raise FileExistsError(f"refusing to overwrite V155: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    teacher_root = args.teacher_run_root.resolve()
    first_trace = args.first_shadow_trace.resolve()
    second_trace = args.second_shadow_trace.resolve()
    work = args.work_root.resolve()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = {
        "runner": Path(__file__).resolve(),
        "v121_transform": V121_TRANSFORM,
        "v140_result": V140_RESULT,
        "v144_correction": V144_CORRECTION,
        "v150_correction": V150_CORRECTION,
        "v151_result": V151_RESULT,
        "v152_alignment": V152_ALIGNMENT,
        "v153_result": V153_RESULT,
        "v154_result": V154_RESULT,
        "v134_loader": (
            TRAINING / "winner_v134_full_actor_teacher_distillation.py"
        ),
        "v145_loader": TRAINING / "winner_v145_on_policy_dagger.py",
        "source_raw": source_raw,
        "source_deployed": source_deployed,
        "first_shadow_trace": first_trace,
        "second_shadow_trace": second_trace,
    }
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
    ):
        raise ValueError("V155 preregistration changed")
    mechanism = prereg["mechanism"]
    phase = np.asarray(mechanism["phase"], dtype=np.float64)
    contact = np.asarray(mechanism["contact"], dtype=np.float64)
    radius_squared = float(mechanism["phase_radius_squared"])
    threshold = float(mechanism["threshold"])
    correction = np.zeros(14, dtype=np.float32)
    correction[RIGHT_ANKLE] = np.float32(mechanism["correction"])
    teacher = v134.load_teacher_dataset(teacher_root)
    first = dagger.load_shadow_dataset(first_trace)
    second = dagger.load_shadow_dataset(second_trace)
    data = {
        "obs": np.concatenate(
            [teacher["obs"], first["obs"], second["obs"]], axis=0
        ),
        "previous_action": np.concatenate(
            [
                teacher["previous_action"],
                first["previous_action"],
                second["previous_action"],
            ],
            axis=0,
        ),
        "h_in": np.concatenate(
            [teacher["h_in"], first["h_in"], second["h_in"]], axis=0
        ),
    }
    phase_distance = np.sum(
        np.square(data["obs"][:, 99:101] - phase[None, :]), axis=1
    )
    phase_contact = (
        (phase_distance <= radius_squared)
        & np.all(data["obs"][:, 97:99] == contact[None, :], axis=1)
    )
    gate = phase_contact & (data["obs"][:, VELOCITY_OBS] > threshold)
    work.mkdir(parents=True)
    local_raw = work / "winner_v155_velocity_gated_phase_raw.onnx"
    local_deployed = (
        work / "winner_v155_velocity_gated_phase_deployed.onnx"
    )
    model = append_velocity_gate(
        onnx.load(source_raw),
        phase=phase,
        contact=contact,
        radius_squared=radius_squared,
        velocity_threshold=threshold,
        correction=correction,
    )
    onnx.save(model, local_raw)
    transform = json.loads(
        V121_TRANSFORM.read_text(encoding="utf-8")
    )["transform"]
    contract = deploy_graph(local_raw, local_deployed, transform)
    source_dynamic = work / "winner_v155_source_dynamic.onnx"
    local_dynamic = work / "winner_v155_local_dynamic.onnx"
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
    first_index = 4_800 + 394
    inherited_index = 4_800 + 600 + 394
    second_index = 4_800 + 600 + 583
    positive_indices = [first_index, inherited_index, second_index]
    trace_negative = [
        4_800 + i
        for i in range(600)
        if phase_contact[4_800 + i] and i != 394
    ] + [
        5_400 + i
        for i in range(600)
        if phase_contact[5_400 + i] and i not in {394, 583}
    ]
    x0 = np.abs(data["obs"][:, 6]) <= 0.01
    checks = {
        "dataset_exact_6000": data["obs"].shape == (6_000, 115),
        "all_three_positive_rows_inside_gate": bool(
            np.all(gate[positive_indices])
        ),
        "all_39_frozen_negative_rows_outside_gate": (
            len(trace_negative) == 39
            and not bool(np.any(gate[trace_negative]))
        ),
        "changes_only_inside_state_gate": bool(np.all(gate[changed_rows])),
        "changes_only_right_ankle": changed_joints.tolist() == [RIGHT_ANKLE],
        "three_causal_rows_receive_frozen_correction": bool(
            np.all(
                np.abs(delta[positive_indices, RIGHT_ANKLE] - correction[13])
                <= 5.0e-7
            )
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
        "no_training_behavior_or_hosted_compute": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v155.velocity_gated_phase_residual_result.v1"
        ),
        "status": (
            "PASS_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": observed_hashes,
        "gate": {
            "phase": phase.tolist(),
            "contact": contact.tolist(),
            "phase_radius_squared": radius_squared,
            "velocity_obs_index": VELOCITY_OBS,
            "velocity_threshold": threshold,
            "aggregate_gate_rows": np.flatnonzero(gate).tolist(),
            "aggregate_gate_count": int(np.sum(gate)),
            "changed_rows": changed_rows.tolist(),
            "changed_elements": changed_elements.tolist(),
        },
        "correction": {
            "joint": RIGHT_ANKLE,
            "value": float(correction[RIGHT_ANKLE]),
            "positive_indices": positive_indices,
            "positive_deltas": delta[
                positive_indices, RIGHT_ANKLE
            ].tolist(),
        },
        "artifact": {
            "raw": {"path": str(local_raw), "sha256": sha256(local_raw)},
            "deployed": contract,
            "work_root": str(work),
        },
        "decision": (
            "EARN_ONE_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_PREREGISTRATION"
            if not failed
            else "CLOSE_VELOCITY_GATED_PHASE_RESIDUAL"
        ),
        "authority": {
            "v156_behavior_preregistration": not failed,
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V155 velocity-gated phase residual\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Aggregate activations: `{int(np.sum(gate))}` of 6,000.\n"
        f"- Threshold: `{threshold}`.\n"
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
