#!/usr/bin/env python3
"""Run the frozen Winner-v55 reset-label and delayed-handoff audit on CPU."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

PREREGISTRATION = ANALYSIS / "winner_v55_reset_label_handoff_preregistration.json"
V54_RESULT = ANALYSIS / "winner_v54_residual_teacher_causal_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"\0")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(b"\0")
    digest.update(array.tobytes())
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    expected_execution = {
        "reset_rows": 0,
        "diagnostic_cells": 0,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    if (
        value.get("schema_version")
        != "winner_v55.reset_label_handoff_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_RESET_AND_108_CELL_CPU_DIAGNOSTIC_ONLY"
        or value.get("handoff_audit", {}).get("handoff_ticks")
        != [0, 1, 2, 4, 8, 12, 16, 20, 250]
        or value.get("handoff_audit", {}).get("cells") != 108
        or value.get("reset_collision_audit", {}).get("rows") != 30
        or value.get("execution_now") != expected_execution
    ):
        raise ValueError("Winner-v55 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v55 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v55 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v55 source manifest changed")


class DelayedTeacherSession:
    """Use graph actions before one fixed tick and bounded teacher actions after."""

    def __init__(
        self,
        session: Any,
        *,
        raw_teacher: np.ndarray,
        handoff_tick: int,
        bounded_action: Callable[[np.ndarray, np.ndarray], np.ndarray],
    ) -> None:
        teacher = np.asarray(raw_teacher, dtype=np.float32)
        if teacher.shape != (14,) or not np.all(np.isfinite(teacher)):
            raise ValueError("Winner-v55 teacher target is invalid")
        if handoff_tick not in (0, 1, 2, 4, 8, 12, 16, 20, 250):
            raise ValueError("Winner-v55 handoff tick is not preregistered")
        self.session = session
        self.raw_teacher = teacher.copy()
        self.handoff_tick = handoff_tick
        self.bounded_action = bounded_action
        self.tick = 0

    def run(
        self, output_names: Sequence[str], inputs: Mapping[str, np.ndarray]
    ) -> list[np.ndarray]:
        outputs = self.session.run(output_names, dict(inputs))
        if self.tick < self.handoff_tick:
            result = [np.asarray(value, dtype=np.float32) for value in outputs]
        else:
            previous = np.asarray(inputs["previous_action"], dtype=np.float32)
            if previous.shape != (1, 14):
                raise ValueError("Winner-v55 previous-action ABI changed")
            applied = self.bounded_action(self.raw_teacher, previous[0])[None, :]
            result = [
                applied,
                applied.copy(),
                np.asarray(outputs[2], dtype=np.float32),
            ]
        self.tick += 1
        return result


def select_classification(
    *, reset_conflict: bool, pass_counts: Mapping[int, int]
) -> tuple[str, str, int | None]:
    if pass_counts.get(0) != 12:
        return (
            "TEACHER_ENDPOINT_INSUFFICIENT",
            "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
            None,
        )
    if not reset_conflict:
        return (
            "NO_RESET_LABEL_CONFLICT",
            "CLOSE_RESET_CONFLICT_HYPOTHESIS_WITHOUT_TRAINING",
            None,
        )
    feasible = [tick for tick in (1, 2, 4, 8, 12, 16, 20) if pass_counts.get(tick) == 12]
    if feasible:
        return (
            "RESET_LABEL_CONFLICT_WITH_DELAYED_HANDOFF_FEASIBLE",
            "AUTHORIZE_DELAYED_TEACHER_MECHANISM_CPU_CONTRACT_PREREGISTRATION_ONLY",
            max(feasible),
        )
    return (
        "RESET_LABEL_CONFLICT_IMMEDIATE_TEACHER_ONLY",
        "AUTHORIZE_UNIVERSAL_ACTIVE_PREFIX_FEASIBILITY_PREREGISTRATION_ONLY",
        None,
    )


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--handoff-diagnostic-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.handoff_diagnostic_authorized:
        raise PermissionError(
            "Winner-v55 requires --offline-cpu-only --handoff-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v55 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v55 summary: {markdown}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48
    import run_winner_v54_residual_teacher_causal as v54
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v55 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    if sha256(V54_RESULT) != preregistration["frozen_source"]["v54_result_sha256"]:
        raise ValueError("Winner-v55 V54 source changed")
    if sha256(V42_RESULT) != preregistration["frozen_source"]["v42_result_sha256"]:
        raise ValueError("Winner-v55 V42 source changed")
    v54_result = json.loads(V54_RESULT.read_text(encoding="utf-8"))
    if v54_result.get("status") != "PASS_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC":
        raise ValueError("Winner-v55 V54 status changed")

    smoke, gate, v53 = v54.configure_v53_modules()
    full_preregistration = json.loads(
        FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8")
    )
    calibrator_design = gate.load_calibrator_design(full_preregistration)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    teacher_table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    source = preregistration["frozen_source"]
    teacher_ids = source["teacher_configuration_ids"]
    failure_ids = source["failure_configuration_ids"]
    if set(teacher_ids) - set(by_id) or set(teacher_ids) != set(teacher_table):
        raise ValueError("Winner-v55 teacher population changed")

    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v55 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v55 canonical fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)

    checkpoint_path, graph_path = v53.checkpoint_paths(args.training_work_root, "final")
    snapshot = v53.load_snapshot_for_reviewed_gate(checkpoint_path)
    v53.validate_snapshot_for_reviewed_gate(snapshot)
    if snapshot["metadata"]["completed_updates"] != 453:
        raise ValueError("Winner-v55 checkpoint boundary changed")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)

    reset_rows = []
    zero_previous = np.zeros((14,), dtype=np.float32)
    zero_hidden = np.zeros((64,), dtype=np.float32)
    for configuration_id in teacher_ids:
        for plant in source["plants"]:
            episode = smoke.Episode(
                mujoco,
                scene,
                by_id[configuration_id],
                plant,
                calibrator_design,
                observer_type,
                args.canonical_fit,
            )
            observation = gate.ObservationTransport(None, None).observe(
                episode.observation()
            )
            outputs = session.run(
                ["calibration_actions", "previous_action_out", "h_out"],
                {
                    "obs": observation[None, :],
                    "previous_action": zero_previous[None, :],
                    "h_in": zero_hidden[None, :],
                },
            )
            graph_action = np.asarray(outputs[0][0], dtype=np.float32)
            raw_teacher = np.asarray(teacher_table[configuration_id], dtype=np.float32)
            bounded_teacher = smoke.bounded_action_numpy(raw_teacher, zero_previous)
            reset_input = np.concatenate([observation, zero_previous, zero_hidden])
            reset_rows.append(
                {
                    "configuration_id": configuration_id,
                    "plant": plant,
                    "initial_contacts": list(episode.initial_contacts),
                    "reset_input_sha256": array_sha256(reset_input),
                    "observation_sha256": array_sha256(observation),
                    "graph_action_sha256": array_sha256(graph_action),
                    "bounded_teacher_action_sha256": array_sha256(bounded_teacher),
                    "bounded_teacher_pitch": bounded_teacher[
                        source["pitch_indices"]
                    ].astype(float).tolist(),
                }
            )
    input_groups: dict[str, set[str]] = {}
    for row in reset_rows:
        input_groups.setdefault(row["reset_input_sha256"], set()).add(
            row["bounded_teacher_action_sha256"]
        )
    conflict_groups = [
        {"reset_input_sha256": key, "bounded_teacher_label_count": len(labels)}
        for key, labels in sorted(input_groups.items())
        if len(labels) > 1
    ]
    reset_conflict = bool(conflict_groups)

    v54_cells = {
        (row["configuration_id"], row["plant"]): row
        for row in v54_result["checkpoint"]["cells"]
    }
    handoff_rows = []
    endpoint_exact = {0: [], 250: []}
    for handoff_tick in preregistration["handoff_audit"]["handoff_ticks"]:
        for configuration_id in failure_ids:
            raw_teacher = np.asarray(teacher_table[configuration_id], dtype=np.float32)
            for plant in source["plants"]:
                wrapper = DelayedTeacherSession(
                    session,
                    raw_teacher=raw_teacher,
                    handoff_tick=handoff_tick,
                    bounded_action=smoke.bounded_action_numpy,
                )
                cell = gate.run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=by_id[configuration_id],
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=wrapper,
                    parameters=snapshot["parameters"],
                    target_mean=target_mean,
                    target_std=target_std,
                )
                compact = v48.compact_cell(cell)
                row = {
                    "handoff_tick": handoff_tick,
                    "configuration_id": configuration_id,
                    "plant": plant,
                    **compact,
                }
                handoff_rows.append(row)
                if handoff_tick in endpoint_exact:
                    arm = "full_teacher" if handoff_tick == 0 else "graph"
                    endpoint_exact[handoff_tick].append(
                        compact == v54_cells[(configuration_id, plant)]["arms"][arm]
                    )
    pass_counts = {
        tick: sum(
            bool(row["support_pass"])
            for row in handoff_rows
            if row["handoff_tick"] == tick
        )
        for tick in preregistration["handoff_audit"]["handoff_ticks"]
    }
    classification, decision, selected_handoff = select_classification(
        reset_conflict=reset_conflict,
        pass_counts=pass_counts,
    )
    checks = {
        "exact_30_reset_rows": len(reset_rows) == 30,
        "exact_108_handoff_cells": len(handoff_rows) == 108,
        "tick_0_endpoint_bit_exact_to_v54": len(endpoint_exact[0]) == 12
        and all(endpoint_exact[0]),
        "tick_250_endpoint_bit_exact_to_v54": len(endpoint_exact[250]) == 12
        and all(endpoint_exact[250]),
        "all_previous_action_chains_exact": all(
            row["previous_action_chain_exact"] for row in handoff_rows
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            row["maximum_jax_onnx_hidden_error"] <= 1.0e-7
            for row in handoff_rows
        ),
        "all_values_finite": finite_tree(reset_rows) and finite_tree(handoff_rows),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "winner_v55.reset_label_handoff_result.v1",
        "status": (
            "PASS_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC"
            if not failed_checks
            else "HOLD_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC"
        ),
        "classification": classification,
        "decision": decision if not failed_checks else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v54_result_sha256": sha256(V54_RESULT),
            "v42_result_sha256": sha256(V42_RESULT),
            "checkpoint_sha256": sha256(checkpoint_path),
            "onnx_sha256": sha256(graph_path),
        },
        "reset_audit": {
            "rows": reset_rows,
            "unique_reset_input_count": len(input_groups),
            "unique_bounded_teacher_action_count": len(
                {row["bounded_teacher_action_sha256"] for row in reset_rows}
            ),
            "unique_graph_action_count": len(
                {row["graph_action_sha256"] for row in reset_rows}
            ),
            "conflict_groups": conflict_groups,
            "reset_label_conflict": reset_conflict,
        },
        "handoff_audit": {
            "pass_counts": {str(key): value for key, value in pass_counts.items()},
            "selected_positive_handoff_tick": selected_handoff,
            "cells": handoff_rows,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "reset_rows": len(reset_rows),
            "diagnostic_cells": len(handoff_rows),
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": (
                "one separate prospective CPU mechanism preregistration only"
                if not failed_checks
                else "nothing"
            ),
        },
    }
    if not finite_tree(result):
        raise FloatingPointError("Winner-v55 result contains nonfinite values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v55 reset-label and handoff result",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- Reset input / teacher labels / graph actions: `{len(input_groups)} / {result['reset_audit']['unique_bounded_teacher_action_count']} / {result['reset_audit']['unique_graph_action_count']}`",
                f"- Handoff support passes: `{json.dumps(result['handoff_audit']['pass_counts'], sort_keys=True)}`",
                f"- Selected positive handoff: `{selected_handoff}`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
