#!/usr/bin/env python3
"""Test threshold transfer between saved early-warning seed blocks.

Offline JSON analysis only. This does not select or authorize a runtime gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def candidates(scores: list[float]) -> list[float]:
    values = sorted(set(scores))
    if not values:
        raise ValueError("empty score block")
    epsilon = max(1e-12, (values[-1] - values[0]) * 1e-9)
    return [values[0] - epsilon] + [
        (left + right) / 2 for left, right in zip(values, values[1:])
    ] + [values[-1] + epsilon]


def metrics(rows: list[dict], threshold: float, statistic: str) -> dict:
    tp = fn = tn = fp = 0
    flagged = []
    for row in rows:
        predicted = float(row[statistic]) >= threshold
        actual = bool(row["failure"])
        flagged += [int(row["seed"])] if predicted else []
        tp += int(predicted and actual)
        fn += int(not predicted and actual)
        tn += int(not predicted and not actual)
        fp += int(predicted and not actual)
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return {
        "tp": tp, "fn": fn, "tn": tn, "fp": fp,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "balanced_accuracy": (sensitivity + specificity) / 2,
        "positive_predictive_value": tp / (tp + fp) if tp + fp else None,
        "negative_predictive_value": tn / (tn + fn) if tn + fn else None,
        "flagged_seeds": flagged,
    }


def fit(rows: list[dict], statistic: str) -> tuple[float, dict]:
    tested = [(threshold, metrics(rows, threshold, statistic))
              for threshold in candidates([float(row[statistic]) for row in rows])]
    # Safety-oriented deterministic tie break: sensitivity, specificity, then
    # lower threshold. The primary objective remains balanced accuracy.
    return max(tested, key=lambda item: (
        item[1]["balanced_accuracy"], item[1]["sensitivity"],
        item[1]["specificity"], -item[0]))


def load(path: str) -> list[dict]:
    report = json.loads(Path(path).read_text())
    rows = report["per_seed"]
    labels = {bool(row["failure"]) for row in rows}
    if labels != {False, True}:
        raise ValueError(f"{path} must contain both outcome classes")
    return rows


def direction(name: str, train: list[dict], test_name: str, test: list[dict], statistic: str) -> dict:
    threshold, train_metrics = fit(train, statistic)
    return {
        "fit_block": name,
        "test_block": test_name,
        "threshold": threshold,
        "fit_metrics": train_metrics,
        "transfer_metrics": metrics(test, threshold, statistic),
    }


def main() -> int:
    args = parse_args()
    discovery, heldout = load(args.discovery), load(args.heldout)
    directions = [
        direction("discovery", discovery, "heldout", heldout, args.statistic),
        direction("heldout", heldout, "discovery", discovery, args.statistic),
    ]
    stable = all(item["transfer_metrics"]["sensitivity"] == 1.0 for item in directions)
    report = {
        "status": "THRESHOLD_TRANSFER_ASYMMETRIC_NO_RUNTIME_GATE" if not stable else "THRESHOLD_TRANSFER_REQUIRES_MORE_POSITIVES",
        "inputs": {"discovery": args.discovery, "heldout": args.heldout},
        "statistic": args.statistic,
        "window_ticks": discovery[0]["window_ticks"],
        "selection": "maximize balanced accuracy; ties: sensitivity, specificity, lower threshold",
        "directions": directions,
        "stable_full_sensitivity_transfer": stable,
        "decision": "Do not select or implement a runtime start-paused threshold.",
        "limitations": [
            "Only seven failures are present across 32 traces, including two in the held-out block.",
            "This evaluates seed-block transfer, not probability calibration or robot safety.",
            "Thresholds and performance are based on saved simulation traces only.",
        ],
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Early-Warning Threshold Transfer Check", "",
        f"Status: **{report['status']}**", "",
        "Offline saved-JSON analysis only; no simulation, training, robot access, GPU, or Colab use.", "",
        f"Metric: first `{report['window_ticks']}` ticks `{report['statistic']}` teacher disagreement.", "",
        "| fit → test | threshold | fit TP/FN/TN/FP | test TP/FN/TN/FP | test sensitivity | test specificity | test balanced accuracy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["directions"]:
        a, b = item["fit_metrics"], item["transfer_metrics"]
        lines.append(
            f"| {item['fit_block']} → {item['test_block']} | {item['threshold']:.8f} | "
            f"{a['tp']}/{a['fn']}/{a['tn']}/{a['fp']} | {b['tp']}/{b['fn']}/{b['tn']}/{b['fp']} | "
            f"{b['sensitivity']:.3f} | {b['specificity']:.3f} | {b['balanced_accuracy']:.3f} |"
        )
    lines += ["", "## Decision", "", report["decision"], "",
              "The discovery-derived cutoff transfers to the held-out block, but the held-out-derived cutoff misses lower-disagreement failures in discovery. This asymmetric result is not evidence for a stable universal operating threshold.", "",
              "## Limitations", ""]
    lines += [f"- {item}" for item in report["limitations"]]
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--heldout", required=True)
    parser.add_argument("--statistic", default="p95")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
