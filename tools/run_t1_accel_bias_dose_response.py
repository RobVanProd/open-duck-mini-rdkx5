#!/usr/bin/env python3
"""Run and aggregate the preregistered T1 accelerometer-bias matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import mean
from typing import Any

from closed_loop_sim_eval_t1_accel_bias import (
    ClosedLoopConfig,
    run_closed_loop_sim,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t1_accel_bias_v3_preregistration.json"
CONTRACT = ANALYSIS / "t1_accel_bias_v2_contract_result.json"
OUTPUT = ANALYSIS / "t1_accel_bias_v3_dose_response_result.json"
MARKDOWN = ANALYSIS / "T1_ACCEL_BIAS_V3_DOSE_RESPONSE_RESULT_20260725.md"
CURRENT_TO_TORQUE = 0.784532


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def encode_nonfinite(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: encode_nonfinite(item) for key, item in value.items()}
    if isinstance(value, list):
        return [encode_nonfinite(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return "NaN"
        return "Infinity" if value > 0.0 else "-Infinity"
    return value


def token(value: float) -> str:
    return f"{value:+.3f}".replace("+", "p").replace("-", "m").replace(".", "p")


def verify_inputs(prereg: dict[str, Any]) -> None:
    if prereg.get("status") != "PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE":
        raise RuntimeError(f"invalid T1 preregistration: {prereg.get('status')}")
    for name, expected in prereg["input_sha256"].items():
        path = Path(prereg["input_paths"][name])
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"T1 input changed or missing: {name}: {path}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("status") != "PASS_T1_ACCEL_BIAS_CONTRACT":
        raise RuntimeError(f"T1 evaluator contract is not green: {contract}")
    accepted = prereg["execution_contract"]["accepted_pre_matrix_contract"]
    if sha256(CONTRACT) != accepted["sha256"]:
        raise RuntimeError("accepted T1 evaluator contract result hash changed")
    if (
        contract.get("preregistered_contract_sha256")
        != accepted["preregistered_contract_sha256"]
    ):
        raise RuntimeError("accepted T1 evaluator contract has wrong preregistration")


def cell_contract(
    prereg: dict[str, Any], cell: dict[str, Any]
) -> dict[str, Any]:
    return {
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "input_sha256": prereg["input_sha256"],
        "playground_commit": prereg["playground"]["commit"],
        "frozen_configuration": prereg["frozen_configuration"],
        "cell": cell,
    }


def extract_metrics(result: dict[str, Any]) -> dict[str, Any]:
    mode = (result.get("modes") or {}).get("vanilla") or {}
    forward = mode.get("forward_motion") or {}
    pitch = mode.get("body_pitch_rad") or {}
    pitch_chain_velocity = (
        (mode.get("pitch_chain_summary") or {})
        .get("sent_target_velocity_p95_rad_s", {})
        .get("max")
    )
    current_peaks = [
        (joint.get("current_a") or {}).get("max")
        for joint in (mode.get("joints") or {}).values()
    ]
    current_peaks = [float(value) for value in current_peaks if finite(value)]
    pitch_min = pitch.get("min")
    pitch_max = pitch.get("max")
    pitch_abs_max = (
        max(abs(float(pitch_min)), abs(float(pitch_max)))
        if finite(pitch_min) and finite(pitch_max)
        else None
    )
    termination = mode.get("termination_reason")
    return {
        "samples": mode.get("samples"),
        "termination_reason": termination,
        "fall": termination != "duration_complete",
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "command_tracking_ratio": forward.get("command_tracking_ratio"),
        "body_pitch_mean_rad": pitch.get("mean"),
        "body_pitch_max_rad": pitch_max,
        "body_pitch_abs_max_rad": pitch_abs_max,
        "pitch_chain_target_velocity_p95_max_rad_s": pitch_chain_velocity,
        "actuator_force_peak_nm": (
            max(current_peaks) * CURRENT_TO_TORQUE if current_peaks else None
        ),
    }


def run_or_load_cell(
    prereg: dict[str, Any],
    cell: dict[str, Any],
    cache_root: Path,
    policy: Path,
    fit: dict[str, Any],
    playground: Path,
) -> tuple[dict[str, Any], bool]:
    contract = cell_contract(prereg, cell)
    contract_hash = canonical_sha256(contract)
    raw_path = cache_root / (
        f"bias_{token(float(cell['bias_m_s2']))}"
        f"_x_{token(float(cell['command_x_m_s']))}"
        f"_seed_{int(cell['seed'])}.json"
    )
    if raw_path.is_file():
        cached = json.loads(raw_path.read_text(encoding="utf-8"))
        if cached.get("cell_contract_sha256") == contract_hash:
            return cached, True
    result = run_closed_loop_sim(
        ClosedLoopConfig(
            policy_path=policy,
            fit=fit,
            playground_root=playground,
            command_x=float(cell["command_x_m_s"]),
            duration_s=float(
                prereg["frozen_configuration"]["duration_s"]
            ),
            bridge_mode="vanilla",
            expected_observation_dim=101,
            expected_action_dim=14,
            task="flat_terrain_backlash",
            seed=int(cell["seed"]),
            eval_role="reproduction",
            observation_accel_x_bias_m_s2=float(cell["bias_m_s2"]),
        )
    )
    payload = {
        "cell_contract_sha256": contract_hash,
        "cell_contract": contract,
        "metrics": extract_metrics(result),
        "closed_loop_result": encode_nonfinite(result),
    }
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = raw_path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, allow_nan=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, raw_path)
    return payload, False


def aggregate_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metric_names = [
        "mean_local_vx_m_s",
        "command_tracking_ratio",
        "body_pitch_mean_rad",
        "body_pitch_max_rad",
        "body_pitch_abs_max_rad",
        "pitch_chain_target_velocity_p95_max_rad_s",
        "actuator_force_peak_nm",
    ]
    output = {
        "cell_count": len(rows),
        "duration_complete_count": sum(
            row["metrics"]["termination_reason"] == "duration_complete"
            for row in rows
        ),
        "fall_count": sum(bool(row["metrics"]["fall"]) for row in rows),
    }
    for name in metric_names:
        values = [
            float(row["metrics"][name])
            for row in rows
            if finite(row["metrics"].get(name))
        ]
        output[name] = mean(values) if len(values) == len(rows) else None
    return output


def relative_change(candidate: float, baseline: float) -> float:
    if baseline == 0.0:
        return 0.0 if candidate == 0.0 else math.inf
    return abs(candidate - baseline) / abs(baseline)


def decide(
    prereg: dict[str, Any], groups: list[dict[str, Any]]
) -> dict[str, Any]:
    by_key = {
        (float(group["bias_m_s2"]), float(group["command_x_m_s"])): group
        for group in groups
    }
    baseline = by_key[(0.0, 0.08)]["aggregate"]
    biased = by_key[(1.6, 0.08)]["aggregate"]
    vx_degradation = (
        (baseline["mean_local_vx_m_s"] - biased["mean_local_vx_m_s"])
        / abs(baseline["mean_local_vx_m_s"])
    )
    fall_increase = biased["fall_count"] - baseline["fall_count"]
    forward_pitch_shift = (
        biased["body_pitch_mean_rad"] - baseline["body_pitch_mean_rad"]
    )
    thresholds = prereg["decision_rule"]["first_order_support_if_any"]
    triggers = {
        "mean_local_vx_relative_degradation": {
            "value": vx_degradation,
            "threshold": thresholds[
                "mean_local_vx_relative_degradation_gte"
            ],
            "triggered": (
                vx_degradation
                >= thresholds["mean_local_vx_relative_degradation_gte"]
            ),
        },
        "fall_count_increase": {
            "value": fall_increase,
            "threshold": thresholds["fall_count_increase_gte"],
            "triggered": fall_increase >= thresholds["fall_count_increase_gte"],
        },
        "mean_body_pitch_forward_shift_rad": {
            "value": forward_pitch_shift,
            "threshold": thresholds[
                "mean_body_pitch_forward_shift_rad_gte"
            ],
            "triggered": (
                forward_pitch_shift
                >= thresholds["mean_body_pitch_forward_shift_rad_gte"]
            ),
        },
    }
    close_metrics = prereg["decision_rule"]["close_metrics"]
    close_comparisons = []
    close_ok = True
    for command in prereg["frozen_configuration"]["commands_x_m_s"]:
        baseline_group = by_key[(0.0, float(command))]["aggregate"]
        for bias in prereg["frozen_configuration"]["biases_m_s2"]:
            candidate = by_key[(float(bias), float(command))]["aggregate"]
            if candidate["fall_count"] > baseline_group["fall_count"]:
                close_ok = False
            if float(command) == 0.0:
                continue
            for metric in close_metrics:
                change = relative_change(
                    float(candidate[metric]), float(baseline_group[metric])
                )
                passed = change < 0.10
                close_ok = close_ok and passed
                close_comparisons.append(
                    {
                        "bias_m_s2": float(bias),
                        "command_x_m_s": float(command),
                        "metric": metric,
                        "relative_change": change,
                        "passed_lt_0p10": passed,
                    }
                )
    first_order = any(item["triggered"] for item in triggers.values())
    if first_order:
        status = "SUPPORT_T1_ACCEL_BIAS_FIRST_ORDER_CAUSE"
    elif close_ok:
        status = "CLOSE_T1_ACCEL_BIAS_CAUSE"
    else:
        status = "INCONCLUSIVE_T1_T2_RAW_TELEMETRY_REQUIRED"
    failed_close = [
        row
        for row in close_comparisons
        if not row["passed_lt_0p10"]
    ]
    return {
        "status": status,
        "primary_x008": {
            "baseline_bias_0": baseline,
            "test_bias_p1p6": biased,
            "triggers": triggers,
        },
        "close_rule": {
            "passed": close_ok,
            "failed_comparison_count": len(failed_close),
            "worst_relative_changes": sorted(
                close_comparisons,
                key=lambda row: row["relative_change"],
                reverse=True,
            )[:25],
        },
    }


def write_markdown(payload: dict[str, Any]) -> None:
    decision = payload["decision"]
    primary = decision["primary_x008"]
    lines = [
        "# T1 accelerometer-bias dose response",
        "",
        f"- Status: `{decision['status']}`",
        f"- Cells: `{payload['completed_cells']}/{payload['expected_cells']}`",
        f"- Cache hits: `{payload['cache_hits']}`",
        f"- Result SHA-256: `{payload['result_sha256']}`",
        "",
        "## Primary x=0.08 decision",
        "",
        "| trigger | value | threshold | fired |",
        "|---|---:|---:|---|",
    ]
    for name, item in primary["triggers"].items():
        lines.append(
            f"| {name} | {item['value']:.9f} | {item['threshold']:.9f} | "
            f"`{item['triggered']}` |"
        )
    lines.extend(
        [
            "",
            "## Aggregate matrix",
            "",
            "| bias m/s2 | command m/s | falls | mean vx | track ratio | "
            "pitch mean | pitch abs max | target vel p95 max | force peak |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for group in payload["groups"]:
        item = group["aggregate"]
        lines.append(
            f"| {group['bias_m_s2']:.1f} | {group['command_x_m_s']:.3f} | "
            f"{item['fall_count']} | {item['mean_local_vx_m_s']:.6f} | "
            f"{item['command_tracking_ratio'] if item['command_tracking_ratio'] is not None else 'NA'} | "
            f"{item['body_pitch_mean_rad']:.6f} | "
            f"{item['body_pitch_abs_max_rad']:.6f} | "
            f"{item['pitch_chain_target_velocity_p95_max_rad_s']:.6f} | "
            f"{item['actuator_force_peak_nm']:.6f} |"
        )
    lines.extend(
        [
            "",
            "This is an offline CPU falsification result. It does not modify "
            "or deploy a policy and carries zero direct deployment authority.",
        ]
    )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy\t1_accel_bias_v1_cells"
        ),
    )
    parser.add_argument(
        "--compile-cache-root",
        type=Path,
        default=Path(
            r"D:\CodexArtifacts\open-duck-policy\jax_compilation_cache"
        ),
    )
    parser.add_argument(
        "--max-new-cells",
        type=int,
        default=None,
        help=(
            "Stop after this many uncached cells. A partial matrix has no "
            "decision and is intended only for resumable execution."
        ),
    )
    args = parser.parse_args()
    compile_cache_root = args.compile_cache_root.resolve()
    compile_cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault(
        "JAX_COMPILATION_CACHE_DIR", str(compile_cache_root)
    )
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_inputs(prereg)
    policy = Path(prereg["input_paths"]["policy"])
    fit = json.loads(
        Path(prereg["input_paths"]["fit"]).read_text(encoding="utf-8")
    )
    playground = Path(prereg["playground"]["path"])
    cache_root = args.cache_root.resolve()
    rows = []
    cache_hits = 0
    new_cells = 0
    for index, cell in enumerate(prereg["matrix"], start=1):
        if args.max_new_cells is not None and new_cells >= args.max_new_cells:
            break
        payload, cached = run_or_load_cell(
            prereg, cell, cache_root, policy, fit, playground
        )
        cache_hits += int(cached)
        new_cells += int(not cached)
        rows.append({"cell": cell, "metrics": payload["metrics"]})
        print(
            f"[{index}/{len(prereg['matrix'])}] "
            f"bias={cell['bias_m_s2']:+.1f} x={cell['command_x_m_s']:.3f} "
            f"seed={cell['seed']} {'cache' if cached else 'run'} "
            f"term={payload['metrics']['termination_reason']}",
            flush=True,
        )

    complete = len(rows) == len(prereg["matrix"])
    groups = []
    if complete:
        for bias in prereg["frozen_configuration"]["biases_m_s2"]:
            for command in prereg["frozen_configuration"]["commands_x_m_s"]:
                selected = [
                    row
                    for row in rows
                    if float(row["cell"]["bias_m_s2"]) == float(bias)
                    and float(row["cell"]["command_x_m_s"]) == float(command)
                ]
                groups.append(
                    {
                        "bias_m_s2": float(bias),
                        "command_x_m_s": float(command),
                        "aggregate": aggregate_group(selected),
                    }
                )
        decision = decide(prereg, groups)
    else:
        decision = {
            "status": "PARTIAL_T1_MATRIX_NO_DECISION",
            "reason": "result requires all preregistered cells",
        }
    payload = {
        "schema_version": "open_duck.t1_accel_bias_dose_response_result.v3",
        "status": decision["status"],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "matrix_sha256": prereg["matrix_sha256"],
        "expected_cells": len(prereg["matrix"]),
        "completed_cells": len(rows),
        "cache_hits": cache_hits,
        "new_cells": new_cells,
        "cache_root": str(cache_root),
        "jax_compilation_cache_root": str(compile_cache_root),
        "groups": groups,
        "decision": decision,
        "authority": prereg["authority"],
    }
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if complete:
        write_markdown(payload)
    print(decision["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
