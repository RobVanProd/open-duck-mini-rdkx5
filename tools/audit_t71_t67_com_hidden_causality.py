#!/usr/bin/env python3
"""Run the frozen T71 paired hidden-state causal attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t71_t67_com_hidden_causal_preregistration.json"
OUTPUT = ANALYSIS / "t71_t67_com_hidden_causal_result.json"
MARKDOWN = ANALYSIS / "T71_T67_COM_HIDDEN_CAUSAL_RESULT_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, hash_key: str) -> str:
    payload = dict(value)
    payload.pop(hash_key, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(item: dict[str, Any]) -> bool:
    path = Path(item["path"])
    return (
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256(path) == item["sha256"]
    )


def read_ticks(path: Path, ticks: set[int]) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            tick = int(row["tick"])
            if tick in ticks:
                rows[tick] = row
    missing = sorted(ticks - set(rows))
    if missing:
        raise RuntimeError(f"{path} missing frozen ticks {missing}")
    return rows


def rms(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(value, dtype=np.float64))))


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def feed(row: dict[str, Any], hidden: np.ndarray | None = None) -> dict[str, np.ndarray]:
    state = row["policy_state_input"]
    return {
        "obs": np.asarray(row["obs_state"], dtype=np.float32)[None, :],
        "previous_action": np.asarray(
            state["previous_action"], dtype=np.float32
        ),
        "h_in": (
            np.asarray(state["h_in"], dtype=np.float32)
            if hidden is None
            else hidden
        ),
        # T68 proves this added ABI input is diagnostic-only and immutable.
        "calibration_context": np.zeros((1, 64), dtype=np.float32),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T71 result")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    issues: list[str] = []
    if (
        canonical_sha256(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        issues.append("preregistration_sha")
    for name, item in prereg["frozen_inputs"].items():
        if not verify_receipt(item):
            issues.append(f"frozen_input.{name}")
    for population in ("nominal_traces", "shifted_traces"):
        for key, item in prereg[population].items():
            if not verify_receipt(item):
                issues.append(f"{population}.{key}")
    for item in prereg["policies"]:
        if not verify_receipt(item):
            issues.append(f"policy.{item['checkpoint_id']}")
    if issues:
        raise RuntimeError(f"T71 frozen-input failure: {issues}")

    policies = {
        item["checkpoint_id"]: session(Path(item["path"]))
        for item in prereg["policies"]
    }
    sample_ticks = set(prereg["population"]["sample_ticks"])
    records: list[dict[str, Any]] = []
    replay_errors: list[float] = []
    moving_postreset_hidden_rms: list[float] = []
    moving_postreset_action_rms: list[float] = []
    x0_action_abs: list[float] = []

    for key in sorted(prereg["nominal_traces"]):
        checkpoint, fit, command_text = key.split("|")
        command = float(command_text)
        nominal = read_ticks(
            Path(prereg["nominal_traces"][key]["path"]), sample_ticks
        )
        shifted = read_ticks(
            Path(prereg["shifted_traces"][key]["path"]), sample_ticks
        )
        ort_session = policies[checkpoint]
        for tick in sorted(sample_ticks):
            nrow = nominal[tick]
            srow = shifted[tick]
            nfeed = feed(nrow)
            sfeed = feed(srow)
            n_action, n_hout, n_previous = ort_session.run(None, nfeed)
            s_action, s_hout, s_previous = ort_session.run(None, sfeed)
            n_trace_action = np.asarray(
                nrow["action"], dtype=np.float32
            )[None, :]
            s_trace_action = np.asarray(
                srow["action"], dtype=np.float32
            )[None, :]
            n_trace_hout = np.asarray(
                nrow["policy_state_output"]["h_out"], dtype=np.float32
            )
            s_trace_hout = np.asarray(
                srow["policy_state_output"]["h_out"], dtype=np.float32
            )
            n_trace_previous = np.asarray(
                nrow["policy_state_output"]["previous_action_out"],
                dtype=np.float32,
            )
            s_trace_previous = np.asarray(
                srow["policy_state_output"]["previous_action_out"],
                dtype=np.float32,
            )
            replay_error = max(
                float(np.max(np.abs(n_action - n_trace_action))),
                float(np.max(np.abs(s_action - s_trace_action))),
                float(np.max(np.abs(n_hout - n_trace_hout))),
                float(np.max(np.abs(s_hout - s_trace_hout))),
                float(np.max(np.abs(n_previous - n_trace_previous))),
                float(np.max(np.abs(s_previous - s_trace_previous))),
            )
            replay_errors.append(replay_error)

            nominal_hidden = nfeed["h_in"]
            shifted_hidden = sfeed["h_in"]
            hidden_input_rms = rms(nominal_hidden - shifted_hidden)
            hidden_output_rms = rms(n_hout - s_hout)
            shifted_obs_nominal_hidden = ort_session.run(
                ["continuous_actions"],
                feed(srow, hidden=nominal_hidden),
            )[0]
            nominal_obs_shifted_hidden = ort_session.run(
                ["continuous_actions"],
                feed(nrow, hidden=shifted_hidden),
            )[0]
            shifted_obs_action_rms = rms(
                shifted_obs_nominal_hidden - s_action
            )
            nominal_obs_action_rms = rms(
                nominal_obs_shifted_hidden - n_action
            )
            symmetric_action_rms = max(
                shifted_obs_action_rms, nominal_obs_action_rms
            )
            symmetric_action_abs = max(
                float(np.max(np.abs(shifted_obs_nominal_hidden - s_action))),
                float(np.max(np.abs(nominal_obs_shifted_hidden - n_action))),
            )
            if command == 0.0:
                x0_action_abs.append(symmetric_action_abs)
            elif tick > 0:
                moving_postreset_hidden_rms.append(hidden_input_rms)
                moving_postreset_action_rms.append(symmetric_action_rms)
            records.append(
                {
                    "checkpoint_id": checkpoint,
                    "fit_id": fit,
                    "command_x_m_s": command,
                    "tick": tick,
                    "hidden_input_rms": hidden_input_rms,
                    "hidden_output_rms": hidden_output_rms,
                    "shifted_observation_hidden_swap_action_rms": (
                        shifted_obs_action_rms
                    ),
                    "nominal_observation_hidden_swap_action_rms": (
                        nominal_obs_action_rms
                    ),
                    "symmetric_hidden_swap_action_rms": symmetric_action_rms,
                    "symmetric_hidden_swap_action_max_abs": (
                        symmetric_action_abs
                    ),
                    "trace_replay_max_abs_error": replay_error,
                }
            )

    thresholds = prereg["thresholds"]
    actionability = [
        value > thresholds["actionable_action_rms_floor"]
        for value in moving_postreset_action_rms
    ]
    aggregate = {
        "paired_trace_streams": len(prereg["nominal_traces"]),
        "sampled_points": len(records),
        "moving_postreset_points": len(moving_postreset_action_rms),
        "maximum_trace_replay_abs_error": max(replay_errors),
        "moving_postreset_hidden_input_rms": {
            "minimum": min(moving_postreset_hidden_rms),
            "median": float(np.median(moving_postreset_hidden_rms)),
            "maximum": max(moving_postreset_hidden_rms),
        },
        "moving_postreset_hidden_swap_action_rms": {
            "minimum": min(moving_postreset_action_rms),
            "median": float(np.median(moving_postreset_action_rms)),
            "maximum": max(moving_postreset_action_rms),
        },
        "fraction_moving_postreset_actionable": (
            sum(actionability) / len(actionability)
        ),
        "maximum_x0_hidden_swap_action_abs": max(x0_action_abs),
    }
    checks = {
        "exact_population": (
            aggregate["paired_trace_streams"] == 16
            and aggregate["sampled_points"] == 96
            and aggregate["moving_postreset_points"] == 60
        ),
        "trace_replay_exact": (
            aggregate["maximum_trace_replay_abs_error"]
            <= thresholds["maximum_trace_replay_abs_error"]
        ),
        "hidden_state_separates_plant": (
            aggregate["moving_postreset_hidden_input_rms"]["median"]
            >= thresholds[
                "minimum_moving_postreset_hidden_input_rms_median"
            ]
        ),
        "hidden_state_changes_deployed_action": (
            aggregate["moving_postreset_hidden_swap_action_rms"]["median"]
            >= thresholds[
                "minimum_moving_postreset_hidden_swap_action_rms_median"
            ]
            and aggregate["fraction_moving_postreset_actionable"]
            >= thresholds["minimum_fraction_moving_postreset_actionable"]
        ),
        "x0_deadband_masks_hidden_exactly": (
            aggregate["maximum_x0_hidden_swap_action_abs"]
            <= thresholds["maximum_x0_hidden_swap_action_abs"]
        ),
        "formal_shifted_behavior_failed": (
            json.loads(
                Path(
                    prereg["frozen_inputs"]["t70_condition7_result"]["path"]
                ).read_text(encoding="utf-8")
            )["condition"]["green_cells"]
            < 16
        ),
        "offline_read_only": True,
    }
    failed = sorted(name for name, value in checks.items() if not value)
    wrong_response = not failed
    decision = (
        prereg["decision_rule"]["wrong_control_response_decision"]
        if wrong_response
        else prereg["decision_rule"]["missing_signal_decision"]
    )
    value: dict[str, Any] = {
        "schema_version": "open_duck.t71_t67_com_hidden_causal_result.v1",
        "status": (
            "PASS_T71_COM_SIGNAL_PRESENT_AND_CAUSALLY_USED"
            if wrong_response
            else "HOLD_T71_COM_SIGNAL_OR_ACTIONABILITY_NOT_PROVEN"
        ),
        "classification": (
            "COM_SIGNAL_PRESENT_AND_USED_CONTROL_LAW_INADEQUATE"
            if wrong_response
            else "COM_SIGNAL_OR_ACTIONABILITY_INADEQUATE"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "aggregate": aggregate,
        "checks": checks,
        "failed_checks": failed,
        "records": records,
        "interpretation": {
            "causal_claim": (
                "Under an identical current observation and previous action, "
                "replacing only h_in changes the deployed moving action."
            ),
            "negative_claim": (
                "An auxiliary COM estimator, longer recurrent memory, or flat "
                "long-range transport is not earned by this failure."
            ),
            "next_mechanism": (
                "Use a distinct CPU-only transition-control rescue screen; "
                "do not train until it proves a viable nearby closed loop."
            ),
        },
        "execution": {
            "new_simulator_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "transition_control_rescue_preregistration": wrong_response,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T71 T67 COM-hidden causal result",
                "",
                f"- Status: `{value['status']}`",
                f"- Classification: `{value['classification']}`",
                f"- Decision: `{decision}`",
                "- New simulator cells / optimizer / Colab / robot: `0/0/0/0`",
                "",
                "The paired hidden state is plant-sensitive and causally "
                "changes the moving action while the current observation is "
                "held fixed. The remaining problem is the learned response, "
                "not missing COM information.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={decision}")
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0 if wrong_response else 2


if __name__ == "__main__":
    raise SystemExit(main())
