#!/usr/bin/env python3
"""Preregister the Winner-v91 full universal-target feasibility gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v91_universal_target_full_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V91_UNIVERSAL_TARGET_FULL_GATE_PREREGISTRATION_20260722.md"
V90_RESULT = ANALYSIS / "winner_v90_universal_target_intersection_result.json"
V90_RESULT_SHA256 = "4c97d2ac41ca5d6000359217d25c8e8d17702fb4f329f70015bd5b1b1128f775"
COORDINATES = (0.5, 0.25, 0.25)
ACTION = (0.0, 0.0, -0.5, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.25, 0.25)


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
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v91 contract: {path}")
    source = json.loads(V90_RESULT.read_text(encoding="utf-8"))
    selected = source.get("selected_universal_target", {})
    if (
        sha256(V90_RESULT) != V90_RESULT_SHA256
        or source.get("classification") != "UNIVERSAL_STATIC_TARGETS_EXIST_IN_CAPTURED_GRID"
        or source.get("intersection_count") != 25
        or selected.get("candidate_index") != 536
        or selected.get("coordinates") != list(COORDINATES)
        or selected.get("support_pass_count") != 30
        or source.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v91 source selection changed")
    source_paths = {
        "builder": Path("tools/build_winner_v91_universal_target_full_gate_preregistration.py"),
        "runner": Path("tools/run_winner_v91_universal_target_full_gate.py"),
        "tests": Path("tests/test_winner_v91_universal_target_full_gate.py"),
        "v90_result": V90_RESULT.relative_to(ROOT),
        "v85_builder": Path("tools/build_winner_v85_integrated_support_gate_preregistration.py"),
        "base_gate": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "intervention": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
        "target_expansion": Path("patches/winner_v43_static_target_teacher.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v91.universal_target_full_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_124_CELL_UNIVERSAL_TARGET_GATE_ONLY",
        "frozen_target": {
            "v90_result_sha256": V90_RESULT_SHA256,
            "candidate_index": 536,
            "mirrored_coordinates": list(COORDINATES),
            "expanded_raw_action": list(ACTION),
            "expanded_raw_action_sha256": array_sha256(np.asarray(ACTION, dtype=np.float32)),
            "application": (
                "full 14-D replacement before the unchanged graph-authoritative "
                "absolute/rate boundary at every tick"
            ),
        },
        "gate": {
            "instrumentation_source": "exact Winner-v84 half checkpoint at count 705",
            "duration_ticks": 250,
            "core_model_configurations": 56,
            "sensor_transport_conditions": 6,
            "actuator_plants": 2,
            "core_model_plant_cells": 112,
            "sensor_transport_plant_cells": 12,
            "formal_cells": 124,
            "thresholds": "unchanged reviewed Winner-v12 physical support thresholds",
            "pass_rule": (
                "all 124 cells pass support, every requested action equals the exact "
                "bounded universal-target chain, previous_action chaining is exact, "
                "and JAX/ONNX hidden error is at most 1e-7"
            ),
            "predictor_or_context_selection": False,
        },
        "execution_now": {
            "formal_support_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "formal_cpu_gate_authorized": True,
            "result_authorizes": (
                "one separately preregistered universal-target policy mechanism CPU "
                "contract only if all 124 cells pass"
            ),
            "training_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v91 universal-target full-gate preregistration",
                "",
                "- Candidate / coordinates: `536 / [0.5, 0.25, 0.25]`",
                "- Population: `112` core-model + `12` sensor/transport cells",
                "- Duration: `250` ticks per cell",
                "- Action: full replacement through unchanged graph boundary",
                "- Pass: all `124 / 124` physical support cells",
                "- Optimizer updates / policy artifacts / robot access: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
