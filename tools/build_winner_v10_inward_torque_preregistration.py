#!/usr/bin/env python3
"""Freeze the zero-behavior winner-v10 torque-representation contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "winner_v10_inward_torque_contract_preregistration.json"
RUNNER = ROOT / "tools" / "run_winner_v10_inward_torque_contract.py"
IMPORTER = ROOT / "tools" / "import_winner_v10_inward_torque_contract.py"
ATTRIBUTION = ANALYSIS / "winner_v9_numeric_torque_hold_attribution.json"
V9_RESULT = ANALYSIS / "winner_v9_nominal_behavior_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-half", type=Path, required=True)
    parser.add_argument("--source-final", type=Path, required=True)
    parser.add_argument("--source-model-xml", type=Path, required=True)
    parser.add_argument("--source-scene-xml", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError("winner-v10 preregistration already exists")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        attribution["status"]
        != "PASS_WINNER_V9_HOLD_ATTRIBUTED_TO_FLOAT32_TORQUE_BOUNDARY"
    ):
        raise ValueError("winner-v9 numeric torque attribution is not passed")
    numeric = attribution["numeric_evidence"]
    exact_limit = float(numeric["frozen_decimal_torque_gate_nm"])
    inward = float(
        np.nextafter(np.float32(exact_limit), np.float32(-np.inf))
    )
    inward_decimal = f"{inward:.8f}"
    if float(np.float32(float(inward_decimal))) != inward:
        raise ValueError("winner-v10 XML decimal does not round-trip to inward float32")
    sources = {
        "source_half": args.source_half.resolve(),
        "source_final": args.source_final.resolve(),
        "source_model_xml": args.source_model_xml.resolve(),
        "source_scene_xml": args.source_scene_xml.resolve(),
    }
    payload = {
        "schema_version": "open_duck_mini.winner_v10_inward_torque_contract_preregistration.v1",
        "status": "FROZEN_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT_NOT_RUN",
        "causal_hypothesis": "Changing only the STS3215 XML torque limit from the nearest float32 above the frozen decimal boundary to the next representable value inward removes the winner-v9 numeric hold while leaving both stateful policies byte-identical.",
        "input_hashes": {
            "runner": sha256(RUNNER),
            "importer": sha256(IMPORTER),
            "builder": sha256(Path(__file__)),
            "numeric_attribution": sha256(ATTRIBUTION),
            "winner_v9_result": sha256(V9_RESULT),
            **{name: sha256(path) for name, path in sources.items()},
        },
        "frozen_sources": {
            name: {"filename": path.name, "sha256": sha256(path)}
            for name, path in sources.items()
        },
        "expected_abi": {
            "inputs": [
                {"name": "obs", "dtype": "float", "shape": [1, 115]},
                {
                    "name": "previous_action",
                    "dtype": "float",
                    "shape": [1, 14],
                },
            ],
            "outputs": [
                {
                    "name": "continuous_actions",
                    "dtype": "float",
                    "shape": [1, 14],
                },
                {
                    "name": "previous_action_out",
                    "dtype": "float",
                    "shape": [1, 14],
                },
            ],
        },
        "transform": {
            "frozen_decimal_torque_gate_nm": exact_limit,
            "nearest_float32_torque_nm": float(np.float32(exact_limit)),
            "inward_float32_torque_nm": inward,
            "inward_xml_decimal": inward_decimal,
            "source_force_range_xml": f'forcerange="-{exact_limit:.8f} {exact_limit:.8f}"',
            "output_force_range_xml": f'forcerange="-{inward_decimal} {inward_decimal}"',
            "equation": "nextafter(float32(frozen_decimal_torque_gate_nm), -infinity)",
            "policy_graph_change": False,
            "tolerance_current_rate_or_duration_gate_change": False,
        },
        "pass_rule": [
            "all frozen input hashes and both 115+14 stateful ABIs match",
            "both winner-v10 policy outputs are byte-identical copies of winner-v9",
            "256 arbitrary CPU inferences per checkpoint are finite, state-exact, and obey the stored measured action delta",
            "exactly one XML force-range token changes and all 14 actuators inherit it",
            "the positive XML torque parses to the one-step-inward float32 value below the unchanged frozen decimal gate",
            "scene bytes remain exact; no behavior, training, simulator rollout, GPU, runtime, or robot work occurs",
        ],
        "no_retry_or_tuning": "A failure closes this exact winner-v10 representation route. Do not change the source graphs, inward equation, XML decimal, ABI, population, tolerance, or gate.",
        "pass_authorizes_only": "write a separately frozen complete 16-cell winner-v10 nominal behavior/current/torque preregistration",
        "authority": {
            "one_zero_behavior_cpu_contract": True,
            "behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"PREREGISTRATION={OUTPUT}")
    print(f"PREREGISTRATION_SHA256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
