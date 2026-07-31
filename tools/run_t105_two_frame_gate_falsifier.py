#!/usr/bin/env python3
"""Run T105's frozen ABI-preserving two-frame hidden-gate falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t105_two_frame_gate_preregistration.json"
OUTPUT = ANALYSIS / "t105_two_frame_gate_result.json"
MARKDOWN = ANALYSIS / "T105_TWO_FRAME_GATE_RESULT_20260728.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T105 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "PREREGISTERED_T105_TWO_FRAME_GATE_FALSIFIER"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T105 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    verify_receipt(value["gate_asset"], "gate_asset")
    for index, item in enumerate(value["traces"]):
        verify_receipt(item["trace"], f"trace:{index}")
    return value


def score(
    hidden: np.ndarray,
    mean: np.ndarray,
    scale: np.ndarray,
    coefficient: np.ndarray,
    intercept: float,
) -> float:
    return float(((hidden - mean) / scale) @ coefficient + intercept)


def transitions(values: list[bool]) -> int:
    return sum(left != right for left, right in zip(values, values[1:]))


def pair_key(item: Mapping[str, Any]) -> str:
    return "|".join(
        (
            item["checkpoint_id"],
            item["fit_id"],
            f"{float(item['command_x_m_s']):.3f}",
        )
    )


def read_trace(
    item: dict[str, Any],
    model: dict[str, np.ndarray | float],
    warmup: int,
) -> dict[str, Any]:
    current_scores: list[float] = []
    two_frame_scores: list[float] = []
    recurrent_errors: list[float] = []
    prior_h_out: np.ndarray | None = None
    with Path(item["trace"]["path"]).open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            h_in = np.asarray(
                row["policy_state_input"]["h_in"], np.float64
            )[0]
            h_out = np.asarray(
                row["policy_state_output"]["h_out"], np.float64
            )[0]
            if prior_h_out is not None:
                recurrent_errors.append(
                    float(np.max(np.abs(h_in - prior_h_out)))
                )
            current = score(h_out, **model)
            previous = score(h_in, **model)
            current_scores.append(current)
            two_frame_scores.append(0.5 * (current + previous))
            prior_h_out = h_out
    return {
        **item,
        "pair_key": pair_key(item),
        "label": 1 if item["population"] == "com_x_negative" else -1,
        "current_scores": current_scores[warmup:],
        "two_frame_scores": two_frame_scores[warmup:],
        "maximum_h_in_previous_h_out_error": max(
            recurrent_errors, default=0.0
        ),
    }


def threshold_interval(
    nominal: Iterable[float],
    endpoint: Iterable[float],
    maximum_error_fraction: float,
) -> dict[str, Any]:
    nominal_array = np.sort(np.asarray(list(nominal), np.float64))
    endpoint_array = np.sort(np.asarray(list(endpoint), np.float64))
    nominal_allowance = int(
        np.floor(maximum_error_fraction * nominal_array.size)
    )
    endpoint_allowance = int(
        np.floor(maximum_error_fraction * endpoint_array.size)
    )
    nominal_index = nominal_array.size - nominal_allowance - 1
    lower = float(
        np.nextafter(nominal_array[nominal_index], np.inf)
    )
    upper = float(endpoint_array[endpoint_allowance])
    feasible = bool(lower <= upper)
    selected = float((lower + upper) / 2.0) if feasible else None
    return {
        "nominal_rows": int(nominal_array.size),
        "endpoint_rows": int(endpoint_array.size),
        "nominal_false_active_allowance": nominal_allowance,
        "endpoint_false_inactive_allowance": endpoint_allowance,
        "lower_exclusive_nominal_bound": lower,
        "upper_inclusive_endpoint_bound": upper,
        "feasible": feasible,
        "selected_midpoint": selected,
    }


def classification(
    rows: list[dict[str, Any]],
    score_key: str,
    threshold: float,
) -> dict[str, Any]:
    nominal_predictions: list[bool] = []
    endpoint_predictions: list[bool] = []
    per_trace: list[dict[str, Any]] = []
    for item in rows:
        predictions = [
            value >= threshold for value in item[score_key]
        ]
        if item["label"] == 1:
            endpoint_predictions.extend(predictions)
        else:
            nominal_predictions.extend(predictions)
        per_trace.append(
            {
                "pair_key": item["pair_key"],
                "population": item["population"],
                "checkpoint_id": item["checkpoint_id"],
                "fit_id": item["fit_id"],
                "command_x_m_s": item["command_x_m_s"],
                "cell_green": item["cell_green"],
                "rows": len(predictions),
                "gate_active_fraction": float(np.mean(predictions)),
                "transitions": transitions(predictions),
            }
        )
    return {
        "nominal_false_active_fraction": (
            float(np.mean(nominal_predictions))
            if nominal_predictions
            else 0.0
        ),
        "endpoint_false_inactive_fraction": (
            float(np.mean(np.logical_not(endpoint_predictions)))
            if endpoint_predictions
            else 0.0
        ),
        "maximum_failing_endpoint_transitions": max(
            (
                item["transitions"]
                for item in per_trace
                if item["population"] == "com_x_negative"
                and not item["cell_green"]
            ),
            default=0,
        ),
        "traces": per_trace,
    }


def flatten(
    rows: Iterable[dict[str, Any]], population: str, score_key: str
) -> list[float]:
    return [
        value
        for item in rows
        if item["population"] == population
        for value in item[score_key]
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T105 result: {path}")
    prereg = load_preregistration()
    gate = json.loads(
        Path(prereg["gate_asset"]["path"]).read_text(encoding="utf-8")
    )
    model: dict[str, np.ndarray | float] = {
        "mean": np.asarray(gate["model"]["mean"], np.float64),
        "scale": np.asarray(gate["model"]["scale"], np.float64),
        "coefficient": np.asarray(
            gate["model"]["coefficient"], np.float64
        ),
        "intercept": float(gate["model"]["intercept"]),
    }
    warmup = int(prereg["population"]["warmup_ticks"])
    rows = [
        read_trace(item, model, warmup) for item in prereg["traces"]
    ]
    maximum_error = float(
        prereg["thresholds"]["maximum_expected_class_error_fraction"]
    )
    full_interval = threshold_interval(
        flatten(rows, "nominal", "two_frame_scores"),
        flatten(rows, "com_x_negative", "two_frame_scores"),
        maximum_error,
    )
    full_metrics = (
        classification(
            rows,
            "two_frame_scores",
            float(full_interval["selected_midpoint"]),
        )
        if full_interval["feasible"]
        else None
    )
    baseline = classification(rows, "current_scores", 0.0)
    folds: list[dict[str, Any]] = []
    heldout_nominal: list[bool] = []
    heldout_endpoint: list[bool] = []
    heldout_trace_metrics: list[dict[str, Any]] = []
    for heldout_key in sorted({item["pair_key"] for item in rows}):
        train = [item for item in rows if item["pair_key"] != heldout_key]
        test = [item for item in rows if item["pair_key"] == heldout_key]
        interval = threshold_interval(
            flatten(train, "nominal", "two_frame_scores"),
            flatten(train, "com_x_negative", "two_frame_scores"),
            maximum_error,
        )
        fold: dict[str, Any] = {
            "heldout_pair": heldout_key,
            "training_threshold_interval": interval,
        }
        if interval["feasible"]:
            threshold = float(interval["selected_midpoint"])
            metrics = classification(test, "two_frame_scores", threshold)
            fold["heldout_metrics"] = metrics
            for item in test:
                predictions = [
                    value >= threshold
                    for value in item["two_frame_scores"]
                ]
                if item["population"] == "nominal":
                    heldout_nominal.extend(predictions)
                else:
                    heldout_endpoint.extend(predictions)
            heldout_trace_metrics.extend(metrics["traces"])
        else:
            fold["heldout_metrics"] = None
        folds.append(fold)
    all_folds_feasible = all(
        fold["training_threshold_interval"]["feasible"]
        for fold in folds
    )
    cross_validation = {
        "folds": folds,
        "all_folds_feasible": all_folds_feasible,
        "nominal_false_active_fraction": (
            float(np.mean(heldout_nominal))
            if heldout_nominal
            else 1.0
        ),
        "endpoint_false_inactive_fraction": (
            float(np.mean(np.logical_not(heldout_endpoint)))
            if heldout_endpoint
            else 1.0
        ),
        "maximum_failing_endpoint_transitions": max(
            (
                item["transitions"]
                for item in heldout_trace_metrics
                if item["population"] == "com_x_negative"
                and not item["cell_green"]
            ),
            default=0,
        ),
    }
    recurrent_error = max(
        item["maximum_h_in_previous_h_out_error"] for item in rows
    )
    pass_candidate = bool(
        full_interval["feasible"]
        and all_folds_feasible
        and cross_validation["nominal_false_active_fraction"]
        <= maximum_error
        and cross_validation["endpoint_false_inactive_fraction"]
        <= maximum_error
        and cross_validation["maximum_failing_endpoint_transitions"]
        <= prereg["thresholds"][
            "maximum_post_warmup_transitions_per_failing_trace"
        ]
        and recurrent_error
        <= prereg["thresholds"][
            "maximum_h_in_previous_h_out_error"
        ]
    )
    checks = {
        "exactly_twenty_four_traces": len(rows) == 24,
        "exactly_twelve_folds": len(folds) == 12,
        "h_in_is_exact_prior_h_out": (
            recurrent_error
            <= prereg["thresholds"][
                "maximum_h_in_previous_h_out_error"
            ]
        ),
        "all_metrics_finite": all(
            np.isfinite(value)
            for value in (
                baseline["nominal_false_active_fraction"],
                baseline["endpoint_false_inactive_fraction"],
                cross_validation["nominal_false_active_fraction"],
                cross_validation["endpoint_false_inactive_fraction"],
                recurrent_error,
            )
        ),
        "no_graph_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    status_pass = bool(not failed and pass_candidate)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t105_two_frame_gate_result.v1",
        "status": (
            "PASS_T105_TWO_FRAME_GATE_FALSIFIER"
            if status_pass
            else (
                "CLOSE_T105_TWO_FRAME_GATE_FALSIFIER"
                if not failed
                else "HOLD_T105_TWO_FRAME_GATE_FALSIFIER"
            )
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if status_pass
            else (
                prereg["decision_rule"]["fail_decision"]
                if not failed
                else "HOLD_WITHOUT_SUCCESSOR"
            )
        ),
        "candidate_pass": pass_candidate,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "maximum_h_in_previous_h_out_error": recurrent_error,
        "baseline_current_score_zero_threshold": baseline,
        "two_frame_full_population": {
            "threshold_interval": full_interval,
            "metrics": full_metrics,
        },
        "two_frame_grouped_cross_validation": cross_validation,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows": sum(
                len(item["two_frame_scores"]) for item in rows
            ),
            "simulator_steps": 0,
            "graph_transforms": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "interpretation": {
            "hosted_run_earned": False,
            "behavior_rerun_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "t106_graph_transform_preregistration": status_pass,
            "behavior": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    cv = cross_validation
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T105 two-frame gate result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                (
                    "- Full-population threshold feasible: "
                    f"`{full_interval['feasible']}`"
                ),
                (
                    "- All 12 training folds feasible: "
                    f"`{all_folds_feasible}`"
                ),
                (
                    "- Held-out nominal false-active / endpoint "
                    "false-inactive: "
                    f"`{cv['nominal_false_active_fraction']:.6f} / "
                    f"{cv['endpoint_false_inactive_fraction']:.6f}`"
                ),
                (
                    "- Maximum failing-trace transitions: "
                    f"`{cv['maximum_failing_endpoint_transitions']}`"
                ),
                "- Graph / behavior / training / Colab / robot: `0 / 0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"candidate_pass={pass_candidate}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
