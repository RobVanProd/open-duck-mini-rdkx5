#!/usr/bin/env python3
"""Audit whether the two right-ankle events share a phase/contact mechanism."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
V151_RESULT = ANALYSIS / "winner_v151_bounded_two_center_result.json"
OUTPUT = ANALYSIS / "winner_v152_phase_contact_alignment.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V152_PHASE_CONTACT_ALIGNMENT_20260725.md"
)
EXPECTED = {
    "v144_correction": (
        "4d955dacf6d30a0953c306ab6e7d9a1d87fea872a8b646aebd48c9e528c0dd0c"
    ),
    "v150_correction": (
        "032641cb262a8138d8cf1b395d61d2b71cca560590652ae0b92090c945531e00"
    ),
    "v151_result": (
        "fbc794b6d12bbe8f60087f8d417a201ccf5b259f5f2514c730ba4af2ef4a90f2"
    ),
    "first_trace": (
        "eb432bdb64c251dcbb466bd795db381891837086dae9dcc7a2564a7f2a2930b5"
    ),
    "second_trace": (
        "a816549061de726762ff01602a3366f78a919e9800132f8faca622836e39b731"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-trace", type=Path, required=True)
    parser.add_argument("--second-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V152: {path}")
    first_trace = args.first_trace.resolve()
    second_trace = args.second_trace.resolve()
    first = load_trace(first_trace)
    second = load_trace(second_trace)
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v150 = json.loads(V150_CORRECTION.read_text(encoding="utf-8"))
    v151 = json.loads(V151_RESULT.read_text(encoding="utf-8"))
    first_event = v144["causal_result"]["peak_event"]
    second_event = v150["causal_result"]["event"]
    first_tick = int(first_event["source_tick"])
    second_tick = int(second_event["source_tick"])
    phase = np.asarray(first[first_tick]["obs_state"][99:101], dtype=np.float32)

    def matching(rows: list[dict]) -> list[int]:
        return [
            int(row["tick"])
            for row in rows
            if np.array_equal(
                np.asarray(row["obs_state"][99:101], dtype=np.float32),
                phase,
            )
        ]

    first_ticks = matching(first)
    second_ticks = matching(second)
    first_contact_ticks = [
        tick
        for tick in first_ticks
        if first[tick]["foot_contacts"] == [0, 1]
    ]
    second_contact_ticks = [
        tick
        for tick in second_ticks
        if second[tick]["foot_contacts"] == [0, 1]
    ]
    first_delta = float(first_event["source_action_delta"])
    second_delta = float(second_event["source_action_delta"])
    correction = max(first_delta, second_delta)
    checks = {
        "all_input_hashes_exact": {
            "v144_correction": sha256(V144_CORRECTION),
            "v150_correction": sha256(V150_CORRECTION),
            "v151_result": sha256(V151_RESULT),
            "first_trace": sha256(first_trace),
            "second_trace": sha256(second_trace),
        }
        == EXPECTED,
        "finite_local_family_is_closed": (
            v151.get("decision") == "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
        ),
        "both_events_are_right_ankle": (
            first_event["joint"] == second_event["joint"] == 13
        ),
        "precursor_phase_bit_exact": np.array_equal(
            np.asarray(
                second[second_tick]["obs_state"][99:101],
                dtype=np.float32,
            ),
            phase,
        ),
        "precursor_contact_bit_exact_right_support": (
            first[first_tick]["foot_contacts"]
            == second[second_tick]["foot_contacts"]
            == [0, 1]
        ),
        "phase_recurrence_exact_27_ticks": (
            len(first_ticks) == len(second_ticks) == 22
            and set(np.diff(first_ticks).tolist()) == {27}
            and set(np.diff(second_ticks).tolist()) == {27}
        ),
        "contact_gate_removes_startup_double_support": (
            len(first_contact_ticks) == len(second_contact_ticks) == 21
            and first_ticks[0] == second_ticks[0] == 16
            and first[16]["foot_contacts"] == [1, 1]
            and 16 not in first_contact_ticks
            and 16 not in second_contact_ticks
        ),
        "event_separation_is_seven_periods": (
            second_tick - first_tick == 189
            and (second_tick - first_tick) // 27 == 7
        ),
        "oracle_labels_same_sign_nonzero": (
            first_delta > 0.0 and second_delta > 0.0
        ),
        "correction_rule_is_max_without_search": (
            correction == first_delta and first_delta >= second_delta
        ),
        "no_simulation_training_or_policy_change": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v152.phase_contact_alignment.v1",
        "status": (
            "PASS_WINNER_V152_PHASE_CONTACT_ALIGNMENT"
            if not failed
            else "HOLD_WINNER_V152_PHASE_CONTACT_ALIGNMENT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "v144_correction": sha256(V144_CORRECTION),
            "v150_correction": sha256(V150_CORRECTION),
            "v151_result": sha256(V151_RESULT),
            "first_trace": sha256(first_trace),
            "second_trace": sha256(second_trace),
        },
        "events": {
            "first": first_event,
            "second": second_event,
            "source_tick_separation": second_tick - first_tick,
            "gait_periods_apart": (second_tick - first_tick) // 27,
        },
        "phase_contact": {
            "phase": phase.tolist(),
            "contacts": [0, 1],
            "phase_recurrence_ticks_first": first_ticks,
            "phase_recurrence_ticks_second": second_ticks,
            "phase_contact_ticks_first": first_contact_ticks,
            "phase_contact_ticks_second": second_contact_ticks,
            "period_ticks": 27,
        },
        "selected_mechanism": {
            "class": (
                "phase-and-contact-synchronous right-ankle feedforward "
                "residual"
            ),
            "source": "V140 raw actor; no V148/V151 state-local centers",
            "phase": phase.tolist(),
            "contacts": [0, 1],
            "correction": correction,
            "correction_rule": (
                "maximum of the two same-sign exact-oracle labels"
            ),
            "radius_rule": (
                "half the Euclidean distance to the nearest distinct frozen "
                "phase sample"
            ),
            "why_distinct": (
                "the trigger is the deterministic periodic gait phase and "
                "support side, not proximity to either high-dimensional "
                "event state"
            ),
        },
        "decision": (
            "EARN_V153_PHASE_CONTACT_RESIDUAL_PREREGISTRATION"
            if not failed
            else "CLOSE_PHASE_CONTACT_RESIDUAL"
        ),
        "authority": {
            "v153_preregistration": not failed,
            "policy_change": False,
            "behavior": False,
            "training": False,
            "hosted_training": False,
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
        "# Winner V152 phase/contact alignment\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Both precursor phases: `{phase.tolist()}` with contacts `[0, 1]`.\n"
        "- The events are 189 ticks, or seven exact 27-tick gait periods, "
        "apart.\n"
        f"- Derived correction: `{correction}` action units.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- Read-only audit; no simulation, policy change, training, "
        "Colab, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
