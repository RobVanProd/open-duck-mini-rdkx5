#!/usr/bin/env python3
"""Run V167's fixed reference-amplitude shadow-direction screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS
    / "winner_v167_reference_amplitude_direction_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v167_reference_amplitude_direction_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION_RESULT_20260725.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rows(path: Path) -> dict[int, dict[str, object]]:
    rows = {}
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            rows[int(row["tick"])] = row
    return rows


def feed_from_row(row: dict[str, object]) -> dict[str, np.ndarray]:
    state = row["policy_state_input"]
    return {
        "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
        "h_in": np.asarray(state["h_in"], dtype=np.float32),
        "previous_action": np.asarray(
            state["previous_action"], dtype=np.float32
        ),
    }


def output_map(
    session: ort.InferenceSession, feed: dict[str, np.ndarray]
) -> dict[str, np.ndarray]:
    names = [item.name for item in session.get_outputs()]
    values = session.run(names, feed)
    return dict(zip(names, values, strict=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V167: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    paths = {name: Path(path) for name, path in prereg["paths"].items()}
    observed_hashes = {name: sha256(path) for name, path in paths.items()}
    trace_hashes_exact = all(
        sha256(Path(source["trace"]["path"]))
        == source["trace"]["sha256"]
        for source in prereg["screen"]["sources"]
    )
    if (
        prereg["status"]
        != "PREREGISTERED_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
        or prereg["failed_checks"] != []
        or observed_hashes != prereg["input_hashes"]
        or not trace_hashes_exact
    ):
        raise ValueError("V167 preregistration or inputs changed")

    session = ort.InferenceSession(
        str(paths["selected_policy"]),
        providers=["CPUExecutionProvider"],
    )
    scale = float(prereg["mechanism"]["scale"])
    event_rows = []
    original_linf = 0.0
    unity_bit_exact = True
    for source_index, source in enumerate(prereg["screen"]["sources"]):
        rows = load_rows(Path(source["trace"]["path"]))
        for event in source["events"]:
            tick = int(event["source_tick"])
            joint = int(event["joint"])
            row = rows[tick]
            feed = feed_from_row(row)
            original = output_map(session, feed)["continuous_actions"][0]
            recorded = np.asarray(
                row["policy_graph_authoritative_output"], dtype=np.float32
            )
            original_linf = max(
                original_linf,
                float(np.max(np.abs(original - recorded))),
            )
            unity_feed = {name: value.copy() for name, value in feed.items()}
            unity_feed["obs"][:, 101:115] *= np.float32(1.0)
            unity = output_map(session, unity_feed)["continuous_actions"][0]
            unity_bit_exact = unity_bit_exact and bool(
                np.array_equal(unity, original)
            )
            scaled_feed = {name: value.copy() for name, value in feed.items()}
            scaled_feed["obs"][:, 101:115] *= np.float32(scale)
            scaled = output_map(session, scaled_feed)["continuous_actions"][0]

            oracle = row["exact_torque_oracle"]
            base_action = float(oracle["base_action"][joint])
            oracle_action = float(oracle["final_action"][joint])
            oracle_delta = oracle_action - base_action
            scaled_action = float(scaled[joint])
            scaled_delta = scaled_action - base_action
            source_error = abs(oracle_action - base_action)
            scaled_error = abs(oracle_action - scaled_action)
            event_rows.append(
                {
                    "source_index": source_index,
                    "plant": source["identity"]["plant"],
                    "command_x_m_s": source["identity"]["command_x_m_s"],
                    "source_tick": tick,
                    "violation_tick": event["violation_tick"],
                    "joint": joint,
                    "base_action": base_action,
                    "oracle_action": oracle_action,
                    "oracle_delta": oracle_delta,
                    "scaled_action": scaled_action,
                    "scaled_delta": scaled_delta,
                    "source_error": source_error,
                    "scaled_error": scaled_error,
                    "same_nonzero_direction": (
                        scaled_delta != 0.0
                        and oracle_delta != 0.0
                        and scaled_delta * oracle_delta > 0.0
                    ),
                    "strict_error_reduction": scaled_error < source_error,
                }
            )

    checks = {
        "cpu_provider_exact": session.get_providers()
        == ["CPUExecutionProvider"],
        "event_count_exact_12": len(event_rows) == 12,
        "original_graph_reproduction_linf_at_most_1e6": (
            original_linf <= 1.0e-6
        ),
        "unity_reference_scale_bit_exact": unity_bit_exact,
        "all_oracle_deltas_nonzero": all(
            row["oracle_delta"] != 0.0 for row in event_rows
        ),
        "all_scaled_deltas_nonzero": all(
            row["scaled_delta"] != 0.0 for row in event_rows
        ),
        "all_scaled_deltas_same_sign_as_oracle": all(
            row["same_nonzero_direction"] for row in event_rows
        ),
        "all_scaled_actions_strictly_reduce_oracle_action_error": all(
            row["strict_error_reduction"] for row in event_rows
        ),
        "no_simulation_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    aligned = sum(row["same_nonzero_direction"] for row in event_rows)
    improved = sum(row["strict_error_reduction"] for row in event_rows)
    payload = {
        "schema_version": "winner_v167.reference_amplitude_direction_result.v1",
        "status": (
            "PASS_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
            if passed
            else "HOLD_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            **observed_hashes,
            "preregistration": sha256(PREREG),
        },
        "mechanism": prereg["mechanism"],
        "summary": {
            "events": len(event_rows),
            "same_nonzero_direction": aligned,
            "strict_error_reduction": improved,
            "original_graph_reproduction_linf": original_linf,
            "unity_reference_scale_bit_exact": unity_bit_exact,
            "maximum_scaled_action_change": max(
                abs(row["scaled_delta"]) for row in event_rows
            ),
        },
        "events": event_rows,
        "decision": (
            "EARN_ONE_REFERENCE_AMPLITUDE_WORST_CELL_PREREGISTRATION"
            if passed
            else "CLOSE_UNIFORM_REFERENCE_AMPLITUDE_CONTRACTION_NO_RETRY"
        ),
        "authority": {
            "behavior_preregistration": passed,
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
        "# Winner V167 reference-amplitude direction result\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Fixed scale: `{scale:.16f}`.\n"
        f"- Oracle-direction alignment: `{aligned}/{len(event_rows)}`; "
        f"strict action-error reduction: `{improved}/{len(event_rows)}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- CPU shadow inference only; no simulator, training, production "
        "contract change, Gate 5, or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
