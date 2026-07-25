#!/usr/bin/env python3
"""Preregister V155's velocity-gated phase/contact residual."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/build_winner_v155_velocity_gated_phase_residual.py"
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
V134_LOADER = (
    ROOT / "training/winner_v134_full_actor_teacher_distillation.py"
)
V145_LOADER = ROOT / "training/winner_v145_on_policy_dagger.py"
OUTPUT = (
    ANALYSIS
    / "winner_v155_velocity_gated_phase_residual_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL_PREREGISTRATION_20260725.md"
)
RIGHT_ANKLE_VELOCITY_OBS = 40


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def active_ticks(
    rows: list[dict],
    *,
    phase: np.ndarray,
    contact: np.ndarray,
    radius_squared: float,
) -> list[int]:
    obs = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
    phase_distance = np.sum(
        np.square(obs[:, 99:101] - phase[None, :]), axis=1
    )
    active = (
        (phase_distance <= radius_squared)
        & np.all(obs[:, 97:99] == contact[None, :], axis=1)
    )
    return np.flatnonzero(active).tolist()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-raw", type=Path, required=True)
    parser.add_argument("--source-deployed", type=Path, required=True)
    parser.add_argument("--first-shadow-trace", type=Path, required=True)
    parser.add_argument("--second-shadow-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V155: {path}")
    source_raw = args.source_raw.resolve()
    source_deployed = args.source_deployed.resolve()
    first_trace = args.first_shadow_trace.resolve()
    second_trace = args.second_shadow_trace.resolve()
    inputs = {
        "runner": RUNNER,
        "v121_transform": V121_TRANSFORM,
        "v140_result": V140_RESULT,
        "v144_correction": V144_CORRECTION,
        "v150_correction": V150_CORRECTION,
        "v151_result": V151_RESULT,
        "v152_alignment": V152_ALIGNMENT,
        "v153_result": V153_RESULT,
        "v154_result": V154_RESULT,
        "v134_loader": V134_LOADER,
        "v145_loader": V145_LOADER,
        "source_raw": source_raw,
        "source_deployed": source_deployed,
        "first_shadow_trace": first_trace,
        "second_shadow_trace": second_trace,
    }
    input_hashes = {name: sha256(path) for name, path in inputs.items()}
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v150 = json.loads(V150_CORRECTION.read_text(encoding="utf-8"))
    v151 = json.loads(V151_RESULT.read_text(encoding="utf-8"))
    v152 = json.loads(V152_ALIGNMENT.read_text(encoding="utf-8"))
    v153 = json.loads(V153_RESULT.read_text(encoding="utf-8"))
    v154 = json.loads(V154_RESULT.read_text(encoding="utf-8"))
    first_rows = load_rows(first_trace)
    second_rows = load_rows(second_trace)
    phase = np.asarray(v153["gate"]["phase"], dtype=np.float64)
    contact = np.asarray(v153["gate"]["contact"], dtype=np.float64)
    radius_squared = float(v153["gate"]["radius_squared"])
    first_active = active_ticks(
        first_rows,
        phase=phase,
        contact=contact,
        radius_squared=radius_squared,
    )
    second_active = active_ticks(
        second_rows,
        phase=phase,
        contact=contact,
        radius_squared=radius_squared,
    )
    first_tick = int(v144["causal_result"]["peak_event"]["source_tick"])
    second_tick = int(v150["causal_result"]["event"]["source_tick"])
    positive_keys = {
        ("first", first_tick),
        ("second", first_tick),
        ("second", second_tick),
    }
    positive_values = []
    negative_values = []
    population = []
    for trace_name, rows, ticks in (
        ("first", first_rows, first_active),
        ("second", second_rows, second_active),
    ):
        for tick in ticks:
            value = float(rows[tick]["obs_state"][RIGHT_ANKLE_VELOCITY_OBS])
            positive = (trace_name, tick) in positive_keys
            population.append(
                {
                    "trace": trace_name,
                    "tick": tick,
                    "value": value,
                    "positive": positive,
                }
            )
            (positive_values if positive else negative_values).append(value)
    positive_min = min(positive_values)
    negative_max = max(negative_values)
    threshold = (positive_min + negative_max) / 2.0
    correction = float(v153["correction"]["value"])
    checks = {
        "all_inputs_exist_and_hash": len(input_hashes) == len(inputs),
        "v140_source_green": (
            v140.get("status")
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "finite_local_family_closed": (
            v151.get("decision") == "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
        ),
        "phase_contact_alignment_green": (
            v152.get("status") == "PASS_WINNER_V152_PHASE_CONTACT_ALIGNMENT"
        ),
        "phase_only_mechanism_closed": (
            v154.get("decision") == "CLOSE_PHASE_CONTACT_RESIDUAL"
        ),
        "two_shadow_labels_exact": (
            first_tick == 394
            and second_tick == 583
            and v144["causal_result"]["peak_event"]["joint"] == 13
            and v150["causal_result"]["event"]["joint"] == 13
        ),
        "phase_population_exact": (
            first_active == list(range(43, 584, 27))
            and second_active == list(range(43, 584, 27))
        ),
        "right_ankle_velocity_strictly_separates": (
            len(positive_values) == 3
            and len(negative_values) == 39
            and negative_max < positive_min
        ),
        "midpoint_threshold_has_no_search": (
            negative_max < threshold < positive_min
        ),
        "same_frozen_correction": (
            correction
            == max(
                float(
                    v144["causal_result"]["peak_event"][
                        "source_action_delta"
                    ]
                ),
                float(v150["causal_result"]["event"]["source_action_delta"]),
            )
        ),
        "training_behavior_and_robot_not_authorized": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v155.velocity_gated_phase_residual_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
            if not failed
            else "HOLD_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source": "V140 selected raw actor; no V148/V151 centers",
            "phase": phase.tolist(),
            "contact": contact.tolist(),
            "phase_radius_squared": radius_squared,
            "state_feature": {
                "name": "right ankle observed joint velocity",
                "obs_index": RIGHT_ANKLE_VELOCITY_OBS,
                "reason": (
                    "the same joint's measured velocity is the direct "
                    "frozen-observation state variable; no scan over the "
                    "115 observation fields"
                ),
            },
            "positive_population": (
                "the original tick-394 precursor, its inherited "
                "intervention state on the displaced trace, and the "
                "displaced tick-583 precursor"
            ),
            "negative_population": (
                "all other matching phase/contact rows in both frozen "
                "600-tick traces"
            ),
            "threshold_rule": (
                "midpoint between maximum negative and minimum positive"
            ),
            "threshold": threshold,
            "correction_joint": 13,
            "correction": correction,
            "postprocess": (
                "frozen G3 guard, x=0 deadband, and final rate projection"
            ),
            "optimizer_or_training": False,
            "forward_predictor": False,
        },
        "separation": {
            "positive_values": positive_values,
            "negative_max": negative_max,
            "positive_min": positive_min,
            "margin": positive_min - negative_max,
            "population": population,
        },
        "pass_rule": {
            "classification": "all 3 positives and all 39 negatives exact",
            "scope": (
                "only right ankle changes inside phase/contact/velocity gate"
            ),
            "causal_targets": (
                "both known precursor actions receive the frozen correction"
            ),
            "x0": "exact zero",
            "state": "final action feedback exact; h_out exact",
            "deployment": "existing deployment graph contract green",
        },
        "stop_rule": (
            "any graph-contract or subsequent one-cell behavior failure "
            "closes this state-triggered residual; do not alter the "
            "feature, threshold rule, phase, contact, radius, correction, "
            "or tolerance"
        ),
        "authority": {
            "cpu_graph_contract": not failed,
            "behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V155 velocity-gated phase residual preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Safe maximum: `{negative_max}`.\n"
        f"- Dangerous minimum: `{positive_min}`.\n"
        f"- Frozen midpoint: `{threshold}`.\n"
        "- CPU graph contract only; no behavior, training, Colab, or "
        "hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"threshold={threshold}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
