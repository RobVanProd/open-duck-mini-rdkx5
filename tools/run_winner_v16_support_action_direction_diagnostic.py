#!/usr/bin/env python3
"""Run the preregistered bilateral pitch-chain action-direction diagnostic."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

PREREGISTRATION = ANALYSIS / "winner_v16_support_action_direction_diagnostic_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
CHECKPOINTS = (("half", 50), ("final", 100))
FAILURE_IDS = (
    "COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG",
    "DISCOVERY_03", "HELDOUT_04", "HELDOUT_09",
)
INTERVENTIONS = (
    {"id": "BASELINE", "axis": None, "direction": 0},
    {"id": "HIP_MAG_NEG", "axis": "hip_pitch_magnitude", "direction": -1},
    {"id": "HIP_MAG_POS", "axis": "hip_pitch_magnitude", "direction": 1},
    {"id": "KNEE_NEG", "axis": "knee", "direction": -1},
    {"id": "KNEE_POS", "axis": "knee", "direction": 1},
    {"id": "ANKLE_NEG", "axis": "ankle", "direction": -1},
    {"id": "ANKLE_POS", "axis": "ankle", "direction": 1},
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v16.support_action_direction_diagnostic_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
        or value.get("decision") != "AUTHORIZE_ONE_CPU_ONLY_BILATERAL_PITCH_CHAIN_DIRECTION_DIAGNOSTIC"
        or value.get("execution_now") != {
            "optimizer_updates": 0, "diagnostic_cells": 0,
            "locomotion_steps": 0, "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v16 diagnostic preregistration changed")
    frozen = value.get("frozen_screen", {})
    if frozen != {
        "checkpoint_labels": ["half", "final"],
        "failure_configuration_ids": list(FAILURE_IDS),
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "interventions": list(INTERVENTIONS),
        "target_offset_rad": 0.03,
        "normalized_offset": 0.12,
        "duration_ticks": 250,
        "cells_per_checkpoint_intervention": 12,
        "total_cells": 168,
        "optimizer_updates": 0,
    }:
        raise ValueError("Winner-v16 diagnostic screen changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v16 diagnostic sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if set(item) != {"hash_mode", "path", "sha256"} or item["hash_mode"] != "lf" or lf_sha256(path) != item["sha256"]:
            raise ValueError(f"Winner-v16 diagnostic source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v16 diagnostic source manifest changed")


class InterventionSession:
    """Wrap one ONNX session with a bounded diagnostic-only action transform."""

    def __init__(self, session: Any, direction: Any, networks: Any, intervention: Mapping[str, Any]) -> None:
        self.session = session
        self.direction = direction
        self.maximum_delta = np.asarray(networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
        self.intervention = dict(intervention)
        self.source_actions: list[np.ndarray] = []
        self.realized_actions: list[np.ndarray] = []
        self.source_previous_action_out_exact = True
        self.intervention_formula_bit_exact = True

    def run(self, names: list[str], inputs: Mapping[str, np.ndarray]) -> list[np.ndarray]:
        outputs = self.session.run(names, inputs)
        source = np.asarray(outputs[0][0], dtype=np.float32)
        source_previous = np.asarray(outputs[1][0], dtype=np.float32)
        previous = np.asarray(inputs["previous_action"][0], dtype=np.float32)
        realized = self.direction.intervene(
            source, previous, self.maximum_delta,
            self.intervention["axis"], self.intervention["direction"],
        )
        expected = self.direction.intervene(
            source, previous, self.maximum_delta,
            self.intervention["axis"], self.intervention["direction"],
        )
        self.source_previous_action_out_exact &= np.array_equal(source, source_previous)
        self.intervention_formula_bit_exact &= np.array_equal(realized, expected)
        self.source_actions.append(source.copy())
        self.realized_actions.append(realized.copy())
        return [realized[None, :], realized[None, :], outputs[2]]

    def evidence(self, array_sha256: Any) -> dict[str, Any]:
        source = np.asarray(self.source_actions, dtype=np.float32)
        realized = np.asarray(self.realized_actions, dtype=np.float32)
        delta = realized - source
        return {
            "call_count": int(source.shape[0]),
            "source_previous_action_out_exact": bool(self.source_previous_action_out_exact),
            "intervention_formula_bit_exact": bool(self.intervention_formula_bit_exact),
            "source_action_sha256": array_sha256(source),
            "realized_action_sha256": array_sha256(realized),
            "maximum_abs_action_delta_from_source": float(np.max(np.abs(delta))),
            "mean_squared_action_delta_from_source": float(np.mean(np.square(delta))),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--direction-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.direction_diagnostic_authorized:
        raise PermissionError("direction diagnostic requires explicit CPU-only authorization flags")
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite direction diagnostic: {args.output}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_support_gate as base
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v14_support_action_diagnostic as v14
    import run_winner_v15_pitch_margin_support_gate as v15_gate
    import winner_v12_decomposed_backend_networks as networks
    import winner_v13_normalized_calibrator_training as normalized_training
    import winner_v14_support_action_diagnostic as transform
    import winner_v16_support_action_direction as direction

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise ValueError("Winner-v16 direction diagnostic requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    source = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    if (
        source.get("status") != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or source.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
    ):
        raise ValueError("Winner-v16 source evidence changed")
    v15_gate.smoke, v15_gate.training, v15_gate._TRAINING = smoke, normalized_training, source
    design = base.load_calibrator_design(preregistration)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    all_configurations = matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    index = {row["id"]: row for row in all_configurations}
    configurations = [index[name] for name in FAILURE_IDS]
    if any(float(row["torso_com_offset_m"][0]) >= 0.0 for row in configurations):
        raise ValueError("Winner-v16 screen escaped negative-X configurations")
    scene = args.playground_root / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    formal_by_label = {row["label"]: row for row in formal["checkpoint_results"]}
    checkpoint_results = []
    total_cells = 0
    baseline_matches = 0
    for label, update in CHECKPOINTS:
        snapshot_path, graph_path = v15_gate.checkpoint_paths(args.training_work_root, label)
        snapshot = full.load_snapshot(snapshot_path)
        v15_gate.validate_snapshot(snapshot)
        parameters = snapshot["parameters"]
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        source_session = ort.InferenceSession(str(graph_path), sess_options=options, providers=["CPUExecutionProvider"])
        formal_index = v14.formal_cell_index(formal_by_label[label])
        intervention_results = []
        for intervention in INTERVENTIONS:
            cells = []
            baseline_exact = True
            for configuration in configurations:
                for plant in smoke.PLANTS:
                    session = InterventionSession(source_session, direction, networks, intervention)
                    cell = v14.run_cell(
                        base=base, transform=transform, normalized_training=normalized_training,
                        networks=networks, mujoco=mujoco, scene=scene,
                        configuration=configuration, plant=plant,
                        calibrator_design=design, observer_type=observer_type,
                        canonical_fit=args.canonical_fit, session=session,
                        parameters=parameters, target_mean=target_mean,
                        target_std=target_std, scale=1.0,
                    )
                    if intervention["id"] == "BASELINE":
                        exact = v14.scale_one_matches_formal(cell, formal_index[v14.cell_key(cell)])
                        baseline_exact &= exact
                        baseline_matches += int(exact)
                    public = base.public_cell(cell)
                    public["intervention"] = dict(intervention)
                    public["intervention_evidence"] = session.evidence(base.array_sha256)
                    cells.append(public)
                    total_cells += 1
            failed = [cell for cell in cells if not cell["support_pass"]]
            intervention_results.append({
                "intervention": dict(intervention),
                "cells": cells,
                "support_pass_count": len(cells) - len(failed),
                "support_failure_count": len(failed),
                "support_failure_configuration_counts": dict(sorted(Counter(cell["configuration_id"] for cell in failed).items())),
                "failure_tick_range": None if not failed else [min(cell["terminal"]["tick"] for cell in failed), max(cell["terminal"]["tick"] for cell in failed)],
                "failure_pitch_rad_range": None if not failed else [min(cell["terminal"]["pitch_rad"] for cell in failed), max(cell["terminal"]["pitch_rad"] for cell in failed)],
                "all_action_boundaries_exact": all(cell["maximum_action_delta_excess"] <= 5.0e-7 for cell in cells),
                "all_intervention_formulas_exact": all(cell["intervention_evidence"]["intervention_formula_bit_exact"] for cell in cells),
                "all_source_previous_action_outputs_exact": all(cell["intervention_evidence"]["source_previous_action_out_exact"] for cell in cells),
                "baseline_matches_formal": baseline_exact if intervention["id"] == "BASELINE" else None,
                "maximum_abs_action_delta_from_source": max(cell["intervention_evidence"]["maximum_abs_action_delta_from_source"] for cell in cells),
                "mean_squared_action_delta_from_source": float(np.mean([cell["intervention_evidence"]["mean_squared_action_delta_from_source"] for cell in cells])),
            })
        checkpoint_results.append({
            "label": label, "update": update,
            "checkpoint_sha256": sha256(snapshot_path), "onnx_sha256": sha256(graph_path),
            "intervention_results": intervention_results,
        })
    summaries: dict[str, dict[str, Any]] = {}
    for intervention in INTERVENTIONS:
        rows = [
            next(item for item in checkpoint["intervention_results"] if item["intervention"]["id"] == intervention["id"])
            for checkpoint in checkpoint_results
        ]
        summaries[intervention["id"]] = {
            "intervention": dict(intervention),
            "half_failure_count": rows[0]["support_failure_count"],
            "final_failure_count": rows[1]["support_failure_count"],
            "passes_both_checkpoints": all(row["support_failure_count"] == 0 for row in rows),
            "maximum_abs_action_delta_from_source": max(row["maximum_abs_action_delta_from_source"] for row in rows),
            "mean_squared_action_delta_from_source": float(np.mean([row["mean_squared_action_delta_from_source"] for row in rows])),
        }
    candidates = [name for name, row in summaries.items() if name != "BASELINE" and row["passes_both_checkpoints"]]
    selected = None
    if candidates:
        order = {row["id"]: index for index, row in enumerate(INTERVENTIONS)}
        selected = min(candidates, key=lambda name: (
            summaries[name]["maximum_abs_action_delta_from_source"],
            summaries[name]["mean_squared_action_delta_from_source"], order[name],
        ))
    validity = {
        "exact_168_cells": total_cells == 168,
        "baseline_reproduces_all_24_formal_cells": baseline_matches == 24,
        "all_action_boundaries_exact": all(
            row["all_action_boundaries_exact"] for checkpoint in checkpoint_results for row in checkpoint["intervention_results"]
        ),
        "all_intervention_formulas_exact": all(
            row["all_intervention_formulas_exact"] for checkpoint in checkpoint_results for row in checkpoint["intervention_results"]
        ),
        "all_source_previous_action_outputs_exact": all(
            row["all_source_previous_action_outputs_exact"] for checkpoint in checkpoint_results for row in checkpoint["intervention_results"]
        ),
        "all_values_finite": all(
            math.isfinite(row["maximum_abs_action_delta_from_source"])
            and math.isfinite(row["mean_squared_action_delta_from_source"])
            for row in summaries.values()
        ),
        "optimizer_updates_zero": True,
        "locomotion_and_robot_access_zero": True,
    }
    failed_validity = sorted(name for name, passed in validity.items() if not passed)
    if failed_validity:
        status = "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
        decision = "DO_NOT_INTERPRET_DIRECTION_DIAGNOSTIC"
    elif selected is not None:
        status = "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
        decision = "AUTHORIZE_SELECTED_DIRECTION_CPU_CONTRACT_PREREGISTRATION_ONLY"
    else:
        status = "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
        decision = "NO_SINGLE_BILATERAL_AXIS_DIRECTION_PASSES_STOP_WITH_ATTRIBUTION"
    result = {
        "schema_version": "winner_v16.support_action_direction_diagnostic_result.v1",
        "status": status, "decision": decision,
        "validity_checks": validity, "failed_validity_checks": failed_validity,
        "checkpoint_results": checkpoint_results,
        "intervention_summary": summaries,
        "full_pass_candidates": candidates, "selected_direction": selected,
        "execution": {"optimizer_updates": 0, "diagnostic_cells": total_cells, "locomotion_steps": 0, "robot_or_rdk_access": 0},
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate CPU-only selected-direction contract preregistration",
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
            "formal_result_lf_sha256": lf_sha256(FORMAL_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(f"DECISION={decision}")
    print(f"SELECTED={selected}")
    return 0 if not failed_validity else 1


if __name__ == "__main__":
    raise SystemExit(main())
