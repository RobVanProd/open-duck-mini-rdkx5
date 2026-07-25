#!/usr/bin/env python3
"""Check zero-bias identity and exact obs[3] injection for T1."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from closed_loop_sim_eval import (
    ClosedLoopConfig as OriginalConfig,
    run_closed_loop_sim as run_original,
)
from closed_loop_sim_eval_t1_accel_bias import (
    ClosedLoopConfig as T1Config,
    run_closed_loop_sim as run_t1,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t1_accel_bias_preregistration.json"
OUTPUT = ANALYSIS / "t1_accel_bias_contract_result.json"
MARKDOWN = ANALYSIS / "T1_ACCEL_BIAS_CONTRACT_RESULT_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def strip_new_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_new_fields(item)
            for key, item in value.items()
            if key
            not in {
                "wall_clock_s",
                "observation_accel_x_bias_m_s2",
                "accel_x_pre_bias_m_s2",
                "accel_x_post_bias_m_s2",
            }
        }
    if isinstance(value, list):
        return [strip_new_fields(item) for item in value]
    return value


def verify_inputs(prereg: dict[str, Any]) -> None:
    if prereg.get("status") != "PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE":
        raise RuntimeError(f"invalid T1 preregistration: {prereg.get('status')}")
    for name, expected in prereg["input_sha256"].items():
        path = Path(prereg["input_paths"][name])
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"T1 input changed or missing: {name}: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scratch-root",
        type=Path,
        default=Path(r"D:\CodexArtifacts\open-duck-policy\t1_contract"),
    )
    args = parser.parse_args()
    scratch = args.scratch_root.resolve()
    scratch.mkdir(parents=True, exist_ok=True)

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_inputs(prereg)
    policy = Path(prereg["input_paths"]["policy"])
    fit = json.loads(
        Path(prereg["input_paths"]["fit"]).read_text(encoding="utf-8")
    )
    playground = Path(prereg["playground"]["path"])
    original_trace = scratch / "original_zero.jsonl"
    t1_zero_trace = scratch / "t1_zero.jsonl"
    t1_positive_trace = scratch / "t1_positive_1p6.jsonl"
    common = {
        "policy_path": policy,
        "fit": fit,
        "playground_root": playground,
        "command_x": 0.08,
        "duration_s": 0.10,
        "bridge_mode": "vanilla",
        "task": "flat_terrain_backlash",
        "seed": 0,
        "eval_role": "reproduction",
        "trace_full_obs": True,
    }
    original = run_original(
        OriginalConfig(trace_jsonl=original_trace, **common)
    )
    t1_zero = run_t1(
        T1Config(
            trace_jsonl=t1_zero_trace,
            observation_accel_x_bias_m_s2=0.0,
            **common,
        )
    )
    run_t1(
        T1Config(
            trace_jsonl=t1_positive_trace,
            observation_accel_x_bias_m_s2=1.6,
            **common,
        )
    )
    original_records = load_jsonl(original_trace)
    zero_records = load_jsonl(t1_zero_trace)
    positive_records = load_jsonl(t1_positive_trace)

    zero_result_equal = canonical(strip_new_fields(original)) == canonical(
        strip_new_fields(t1_zero)
    )
    zero_trace_equal = canonical(strip_new_fields(original_records)) == canonical(
        strip_new_fields(zero_records)
    )
    positive_deltas = [
        float(record["accel_x_post_bias_m_s2"])
        - float(record["accel_x_pre_bias_m_s2"])
        for record in positive_records
    ]
    expected_float32_delta = float(
        np.float32(
            np.float32(1.6)
            + np.float32(positive_records[0]["accel_x_pre_bias_m_s2"])
        )
        - np.float32(positive_records[0]["accel_x_pre_bias_m_s2"])
    )
    delta_check = all(
        math.isclose(
            float(record["accel_x_post_bias_m_s2"]),
            float(
                np.float32(
                    np.float32(record["accel_x_pre_bias_m_s2"])
                    + np.float32(1.6)
                )
            ),
            rel_tol=0.0,
            abs_tol=0.0,
        )
        for record in positive_records
    )
    feed_check = all(
        math.isclose(
            float(record["obs0_6"][3]),
            float(record["accel_x_post_bias_m_s2"]),
            rel_tol=0.0,
            abs_tol=0.0,
        )
        for record in positive_records
    )
    first_tick_other_obs_equal = (
        len(zero_records) > 0
        and len(positive_records) > 0
        and all(
            float(zero_records[0]["obs_state"][index])
            == float(positive_records[0]["obs_state"][index])
            for index in range(101)
            if index != 3
        )
    )
    checks = {
        "zero_bias_result_exact_after_allowed_field_removal": zero_result_equal,
        "zero_bias_trace_exact_after_allowed_field_removal": zero_trace_equal,
        "positive_bias_float32_delta_exact": delta_check,
        "positive_bias_onnx_feed_matches_recorded_post_value": feed_check,
        "first_tick_other_100_observation_elements_exact": (
            first_tick_other_obs_equal
        ),
        "all_runs_produced_five_ticks": (
            len(original_records) == len(zero_records) == len(positive_records) == 5
        ),
    }
    status = (
        "PASS_T1_ACCEL_BIAS_CONTRACT"
        if all(checks.values())
        else "HOLD_T1_ACCEL_BIAS_CONTRACT"
    )
    payload = {
        "schema_version": "open_duck.t1_accel_bias_contract_result.v1",
        "status": status,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "samples": {
            "original_zero": len(original_records),
            "t1_zero": len(zero_records),
            "t1_positive_1p6": len(positive_records),
        },
        "positive_bias_delta_m_s2": {
            "expected_first_tick_float32_delta": expected_float32_delta,
            "observed_min": min(positive_deltas),
            "observed_max": max(positive_deltas),
        },
        "scratch_artifacts": {
            "original_zero_trace": str(original_trace),
            "t1_zero_trace": str(t1_zero_trace),
            "t1_positive_trace": str(t1_positive_trace),
        },
        "authority": prereg["authority"],
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T1 accelerometer-bias evaluator contract\n\n"
        f"- Status: `{status}`\n"
        f"- Zero-bias result exact: `{zero_result_equal}`\n"
        f"- Zero-bias trace exact: `{zero_trace_equal}`\n"
        f"- Positive float32 injection exact: `{delta_check}`\n"
        f"- ONNX-fed obs[3] matches post-bias record: `{feed_check}`\n"
        f"- Result SHA-256: `{sha256(OUTPUT)}`\n",
        encoding="utf-8",
    )
    print(status)
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
