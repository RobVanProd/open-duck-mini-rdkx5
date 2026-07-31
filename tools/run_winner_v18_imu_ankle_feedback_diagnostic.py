#!/usr/bin/env python3
"""Run the preregistered Winner-v18 one-sided IMU ankle-feedback diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v14_support_action_diagnostic as v14
import run_winner_v16_support_action_direction_diagnostic as base
import run_winner_v16_support_action_direction_diagnostic_v2 as v2
import winner_v18_imu_ankle_feedback as feedback


PREREGISTRATION = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_preregistration.json"
HOLD_ATTRIBUTION = (
    ANALYSIS / "winner_v17_support_action_combination_hold_attribution.json"
)
FAILURE_IDS = base.FAILURE_IDS
INTERVENTIONS = tuple(
    {"id": mode, "mode": mode}
    for mode in (
        "BASELINE",
        "CONSTANT_ANKLE_POS",
        "TILT_BACKWARD",
        "TILT_OPPOSITE",
        "RATE_BACKWARD",
        "RATE_OPPOSITE",
        "TILT_RATE_BACKWARD",
    )
)


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v18.imu_ankle_feedback_diagnostic_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_CPU_ONLY_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "diagnostic_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v18 preregistration changed")
    if value.get("frozen_screen") != {
        "checkpoint_labels": ["half", "final"],
        "failure_configuration_ids": list(FAILURE_IDS),
        "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "interventions": list(INTERVENTIONS),
        "maximum_target_offset_rad": 0.03,
        "maximum_normalized_offset": 0.12,
        "tilt_boundary_rad": 0.35,
        "rate_reference_rad_s": 1.75,
        "gyro_pitch_rate_observation_index": 1,
        "accelerometer_observation_slice": [3, 6],
        "duration_ticks": 250,
        "cells_per_checkpoint_intervention": 12,
        "total_cells": 168,
        "optimizer_updates": 0,
    }:
        raise ValueError("Winner-v18 frozen screen changed")
    if value.get("baseline_reproduction") != {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": v2.DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }:
        raise ValueError("Winner-v18 baseline reproduction contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v18 sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v18 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v18 source manifest changed")


class FeedbackSession:
    """Wrap one source graph with a deployable-observation feedback transform."""

    def __init__(
        self,
        session: Any,
        direction: Any,
        networks: Any,
        intervention: Mapping[str, Any],
    ) -> None:
        del direction
        self.session = session
        self.maximum_delta = np.asarray(
            networks.INTERNAL_ACTION_DELTA, dtype=np.float32
        )
        self.intervention = dict(intervention)
        self.source_actions: list[np.ndarray] = []
        self.realized_actions: list[np.ndarray] = []
        self.activations: list[np.float32] = []
        self.pitch_proxies: list[np.float32] = []
        self.pitch_rates: list[np.float32] = []
        self.source_previous_action_out_exact = True
        self.intervention_formula_bit_exact = True

    def run(
        self, names: list[str], inputs: Mapping[str, np.ndarray]
    ) -> list[np.ndarray]:
        outputs = self.session.run(names, inputs)
        source = np.asarray(outputs[0][0], dtype=np.float32)
        source_previous = np.asarray(outputs[1][0], dtype=np.float32)
        previous = np.asarray(inputs["previous_action"][0], dtype=np.float32)
        observation = np.asarray(inputs["obs"][0], dtype=np.float32)
        realized, amount, pitch_proxy, pitch_rate = feedback.intervene(
            source,
            previous,
            self.maximum_delta,
            observation,
            self.intervention["mode"],
        )
        expected = feedback.intervene(
            source,
            previous,
            self.maximum_delta,
            observation,
            self.intervention["mode"],
        )[0]
        self.source_previous_action_out_exact &= np.array_equal(
            source, source_previous
        )
        self.intervention_formula_bit_exact &= np.array_equal(realized, expected)
        self.source_actions.append(source.copy())
        self.realized_actions.append(realized.copy())
        self.activations.append(amount)
        self.pitch_proxies.append(pitch_proxy)
        self.pitch_rates.append(pitch_rate)
        return [realized[None, :], realized[None, :], outputs[2]]

    def evidence(self, array_sha256: Any) -> dict[str, Any]:
        source = np.asarray(self.source_actions, dtype=np.float32)
        realized = np.asarray(self.realized_actions, dtype=np.float32)
        activation = np.asarray(self.activations, dtype=np.float32)
        pitch_proxy = np.asarray(self.pitch_proxies, dtype=np.float32)
        pitch_rate = np.asarray(self.pitch_rates, dtype=np.float32)
        delta = realized - source
        return {
            "call_count": int(source.shape[0]),
            "source_previous_action_out_exact": bool(
                self.source_previous_action_out_exact
            ),
            "intervention_formula_bit_exact": bool(
                self.intervention_formula_bit_exact
            ),
            "source_action_sha256": array_sha256(source),
            "realized_action_sha256": array_sha256(realized),
            "maximum_abs_action_delta_from_source": float(np.max(np.abs(delta))),
            "mean_squared_action_delta_from_source": float(np.mean(np.square(delta))),
            "activation_minimum": float(np.min(activation)),
            "activation_mean": float(np.mean(activation)),
            "activation_maximum": float(np.max(activation)),
            "pitch_proxy_rad_range": [
                float(np.min(pitch_proxy)),
                float(np.max(pitch_proxy)),
            ],
            "pitch_rate_rad_s_range": [
                float(np.min(pitch_rate)),
                float(np.max(pitch_rate)),
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", type=Path, required=True)
    known, _ = parser.parse_known_args()

    base.PREREGISTRATION = PREREGISTRATION
    base.validate_preregistration = validate_preregistration
    base.INTERVENTIONS = INTERVENTIONS
    base.InterventionSession = FeedbackSession
    v14.scale_one_matches_formal = v2.baseline_matches_formal
    return_code = base.main()

    result = json.loads(known.output.read_text(encoding="utf-8"))
    result["schema_version"] = "winner_v18.imu_ankle_feedback_diagnostic_result.v1"
    if result["status"] == "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC":
        result["status"] = "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    elif result["status"] == "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC":
        result["status"] = "INVALID_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    else:
        raise ValueError("Winner-v18 base result status changed")
    selected = result["selected_direction"]
    result["decision"] = (
        "AUTHORIZE_SELECTED_IMU_ANKLE_FEEDBACK_CPU_CONTRACT_PREREGISTRATION_ONLY"
        if not result["failed_validity_checks"] and selected is not None
        else (
            "NO_ONE_SIDED_IMU_ANKLE_FEEDBACK_PASSES_STOP_WITH_ATTRIBUTION"
            if not result["failed_validity_checks"]
            else "DO_NOT_INTERPRET_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        )
    )
    result["baseline_reproduction"] = {
        "derived_float_fields": ["terminal", "episode"],
        "finite_absolute_tolerance": v2.DERIVED_FLOAT_ABS_TOLERANCE,
        "all_other_compared_fields": "exact",
        "observation_action_prediction_hidden_trace_hashes": "exact",
    }
    for checkpoint in result["checkpoint_results"]:
        for row in checkpoint["intervention_results"]:
            evidence = [cell["intervention_evidence"] for cell in row["cells"]]
            row["activation_minimum"] = min(
                item["activation_minimum"] for item in evidence
            )
            row["activation_mean"] = float(
                np.mean([item["activation_mean"] for item in evidence])
            )
            row["activation_maximum"] = max(
                item["activation_maximum"] for item in evidence
            )
    for name, summary in result["intervention_summary"].items():
        rows = [
            next(
                row
                for row in checkpoint["intervention_results"]
                if row["intervention"]["id"] == name
            )
            for checkpoint in result["checkpoint_results"]
        ]
        summary["activation_minimum"] = min(row["activation_minimum"] for row in rows)
        summary["activation_mean"] = float(
            np.mean([row["activation_mean"] for row in rows])
        )
        summary["activation_maximum"] = max(row["activation_maximum"] for row in rows)
    result["authority"] = {
        "robot_clearance": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "a separate CPU-only selected-feedback contract preregistration"
        ),
    }
    result["sources"]["base_runner_lf_sha256"] = result["sources"].pop(
        "runner_lf_sha256"
    )
    result["sources"]["runner_lf_sha256"] = lf_sha256(Path(__file__))
    result["sources"]["hold_attribution_lf_sha256"] = lf_sha256(
        HOLD_ATTRIBUTION
    )
    known.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"DECISION={result['decision']}")
    print(f"SELECTED={selected}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
