#!/usr/bin/env python3
"""Preregister V167's gate-derived reference-amplitude direction screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V140 = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V144 = ANALYSIS / "winner_v144_shadow_oracle_result.json"
V158 = ANALYSIS / "winner_v158_x077_shadow_census_result.json"
V160 = ANALYSIS / "winner_v160_remaining_shadow_census_result.json"
V166 = ANALYSIS / "winner_v166_continuous_reference_result.json"
RUNNER = ROOT / "tools/run_winner_v167_reference_amplitude_direction.py"
OUTPUT = (
    ANALYSIS
    / "winner_v167_reference_amplitude_direction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION_PREREGISTRATION_20260725.md"
)
TORQUE_LIMIT_NM = 1.91229675


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def trace_source(
    *,
    trace_path: Path,
    identity: dict[str, object],
    events: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "identity": identity,
        "trace": {
            "path": str(trace_path.resolve()),
            "sha256": sha256(trace_path),
        },
        "events": [
            {
                "joint": int(event["joint"]),
                "source_tick": int(event["source_tick"]),
                "violation_tick": int(event["tick"]),
                "oracle_action_delta": float(event["source_action_delta"]),
            }
            for event in events
        ],
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V167: {path}")
    values = {
        "v140": json.loads(V140.read_text(encoding="utf-8")),
        "v144": json.loads(V144.read_text(encoding="utf-8")),
        "v158": json.loads(V158.read_text(encoding="utf-8")),
        "v160": json.loads(V160.read_text(encoding="utf-8")),
        "v166": json.loads(V166.read_text(encoding="utf-8")),
    }
    policy = Path(
        values["v140"]["artifacts"]["selected_deployed"]["path"]
    ).resolve()
    sources = [
        trace_source(
            trace_path=Path(values["v144"]["trace"]["path"]),
            identity=values["v144"]["identity"],
            events=values["v144"]["torque"]["event_rows"],
        ),
        trace_source(
            trace_path=Path(values["v158"]["trace"]["path"]),
            identity=values["v158"]["identity"],
            events=values["v158"]["torque"]["event_rows"],
        ),
    ]
    v160_root = Path(values["v160"]["artifacts"]["run_root"])
    trace_by_hash = {
        sha256(path): path for path in (v160_root / "traces").glob("*.jsonl")
    }
    for cell in values["v160"]["cells"]:
        trace_hash = cell["trace"]["sha256"]
        sources.append(
            trace_source(
                trace_path=trace_by_hash[trace_hash],
                identity=cell["identity"],
                events=cell["trace"]["actual_violation_events"],
            )
        )

    event_count = sum(len(source["events"]) for source in sources)
    worst_peak_nm = float(values["v160"]["aggregate"]["worst_peak_nm"])
    scale = TORQUE_LIMIT_NM / worst_peak_nm
    input_paths = {
        "runner": RUNNER,
        "selected_policy": policy,
        "v140_result": V140,
        "v144_result": V144,
        "v158_result": V158,
        "v160_result": V160,
        "v166_result": V166,
    }
    checks = {
        "v140_projection_green": (
            values["v140"]["status"]
            == "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
        ),
        "v144_valid_shadow_event": (
            len(values["v144"]["torque"]["event_rows"]) == 1
            and values["v144"]["oracle"]["peak_event"] is not None
        ),
        "v158_valid_shadow_events": (
            len(values["v158"]["torque"]["event_rows"]) == 2
            and values["v158"]["oracle"]["maximum_clip_linf"] > 0.0
        ),
        "v160_complete_shadow_census": (
            values["v160"]["status"]
            == "PASS_WINNER_V160_REMAINING_SHADOW_CENSUS"
            and values["v160"]["aggregate"]["empty_intersection_events"] == 0
        ),
        "v166_cadence_expansion_closed": (
            values["v166"]["decision"]
            == "CLOSE_CONTINUOUS_REFERENCE_CADENCE_EXPANSION_NO_RETRY"
        ),
        "selected_policy_exact": (
            sha256(policy)
            == values["v140"]["artifacts"]["selected_deployed"]["sha256"]
        ),
        "six_moving_trace_sources": len(sources) == 6,
        "twelve_actual_violation_precursors": event_count == 12,
        "scale_strictly_between_zero_and_one": 0.0 < scale < 1.0,
        "scale_derived_only_from_frozen_gate_and_worst_peak": (
            scale == TORQUE_LIMIT_NM / worst_peak_nm
        ),
        "all_trace_hashes_exact": all(
            sha256(Path(source["trace"]["path"]))
            == source["trace"]["sha256"]
            for source in sources
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v167.reference_amplitude_direction_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
            if not failed
            else "HOLD_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "paths": {name: str(path.resolve()) for name, path in input_paths.items()},
        "mechanism": {
            "class": "reviewed projected-reference geometry expansion",
            "operation": "multiply obs[101:115] by one fixed scale",
            "torque_limit_nm": TORQUE_LIMIT_NM,
            "observed_worst_v140_peak_nm": worst_peak_nm,
            "scale": scale,
            "contraction": 1.0 - scale,
            "derivation": (
                "unchanged torque limit divided by the complete V140 "
                "moving-census worst peak"
            ),
            "runtime_101_observation_contract_changed": False,
            "production_115_adapter_contract_changed": False,
        },
        "screen": {
            "cpu_only": True,
            "simulation": False,
            "training": False,
            "sources": sources,
            "event_count": event_count,
            "shadow_state": (
                "original obs, recurrent h_in, and previous_action at each "
                "actual violation's exact oracle precursor tick"
            ),
            "pass_rule": {
                "original_graph_reproduction_linf": "<=1e-6",
                "unity_reference_scale_bit_exact": True,
                "all_oracle_deltas_nonzero": True,
                "all_scaled_deltas_nonzero": True,
                "all_scaled_deltas_same_sign_as_oracle": True,
                "all_scaled_actions_strictly_reduce_oracle_action_error": True,
            },
            "stop_rule": (
                "if any pass rule fails, close uniform projected-reference "
                "amplitude contraction; do not try another scale, joint "
                "subset, command subset, or simulator cell"
            ),
            "green_followup": (
                "one separately preregistered CPU-only worst-cell behavior "
                "screen; no training or production contract change"
            ),
        },
        "authority": {
            "one_shadow_direction_screen": not failed,
            "behavior": False,
            "simulation": False,
            "training": False,
            "hosted_training": False,
            "production_contract_change": False,
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
        "# Winner V167 reference-amplitude direction preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Fixed scale: `{scale:.16f}` = `{TORQUE_LIMIT_NM}` / "
        f"`{worst_peak_nm}`.\n"
        f"- Exact actual-violation precursor events: `{event_count}` across "
        "`6` moving traces.\n"
        "- The shadow screen must move every event action in the exact "
        "oracle direction and strictly reduce every action error.\n"
        "- Failure closes uniform reference-amplitude contraction with no "
        "alternate scale or simulator run.\n"
        "- CPU inference only; no training, contract change, Gate 5, or "
        "robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"scale={scale:.17g}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
