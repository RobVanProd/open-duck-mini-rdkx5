#!/usr/bin/env python3
"""Evaluate a preregistered reset-state plus disagreement risk score."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    positive, negative = scores[labels], scores[~labels]
    return float(np.mean(
        (positive[:, None] > negative[None, :])
        + 0.5 * (positive[:, None] == negative[None, :])
    ))


def load_block(sweep_path: str, warning_path: str, mean: np.ndarray, std: np.ndarray) -> list[dict]:
    sweep = json.loads(Path(sweep_path).read_text())
    warnings = {
        int(row["seed"]): row
        for row in json.loads(Path(warning_path).read_text())["per_seed"]
    }
    rows = []
    for result in sweep["results"]:
        seed = int(result["seed"])
        trace = Path(result["output_dir"]) / "trace.jsonl"
        first = json.loads(trace.read_text().splitlines()[0])
        observation = np.asarray(first["obs_state"], dtype=float)
        if observation.shape != (101,):
            raise ValueError(f"expected obs_state[101] in {trace}, got {observation.shape}")
        warning = warnings[seed]
        failure = result["summary"].get("termination_reason") != "duration_complete"
        if failure != bool(warning["failure"]):
            raise ValueError(f"outcome mismatch for seed {seed}")
        rows.append({
            "seed": seed,
            "failure": failure,
            "observation": (observation - mean) / std,
            "disagreement": float(warning["p95"]),
        })
    if set(warnings) != {row["seed"] for row in rows}:
        raise ValueError("warning and sweep seed sets differ")
    return sorted(rows, key=lambda row: row["seed"])


def reset_risk(query: np.ndarray, reference: list[dict], exclude_seed: int | None = None) -> float:
    distances = []
    for row in reference:
        if row["seed"] == exclude_seed:
            continue
        distance = float(np.sqrt(np.mean((query - row["observation"]) ** 2)))
        distances.append((distance, row["failure"]))
    failure_distance = min(distance for distance, failure in distances if failure)
    complete_distance = min(distance for distance, failure in distances if not failure)
    return complete_distance - failure_distance


def evaluate(train_name: str, train: list[dict], test_name: str, test: list[dict]) -> dict:
    train_reset = np.asarray([
        reset_risk(row["observation"], train, row["seed"]) for row in train
    ])
    test_reset = np.asarray([reset_risk(row["observation"], train) for row in test])
    train_disagreement = np.asarray([row["disagreement"] for row in train])
    test_disagreement = np.asarray([row["disagreement"] for row in test])
    labels = np.asarray([row["failure"] for row in test], dtype=bool)

    def z(test_values: np.ndarray, train_values: np.ndarray) -> np.ndarray:
        scale = float(np.std(train_values))
        if scale == 0:
            raise ValueError("zero training standard deviation")
        return (test_values - float(np.mean(train_values))) / scale

    combined = (z(test_disagreement, train_disagreement) + z(test_reset, train_reset)) / 2
    scores = {
        "disagreement": test_disagreement,
        "reset": test_reset,
        "combined": combined,
    }
    return {
        "train_block": train_name,
        "test_block": test_name,
        "train_samples": len(train),
        "train_failures": sum(row["failure"] for row in train),
        "test_samples": len(test),
        "test_failures": int(np.sum(labels)),
        "roc_auc": {name: auc(values, labels) for name, values in scores.items()},
        "per_seed": [
            {
                "seed": row["seed"], "failure": row["failure"],
                "disagreement": float(test_disagreement[index]),
                "reset_risk": float(test_reset[index]),
                "combined_score": float(combined[index]),
            }
            for index, row in enumerate(test)
        ],
    }


def main() -> int:
    args = parse_args()
    norm = np.load(args.normalization_npz, allow_pickle=False)["norm"]
    mean, std = np.asarray(norm[0], dtype=float), np.maximum(np.asarray(norm[1], dtype=float), 1e-6)
    discovery = load_block(args.discovery_sweep, args.discovery_warning, mean, std)
    heldout = load_block(args.heldout_sweep, args.heldout_warning, mean, std)
    directions = [
        evaluate("discovery", discovery, "heldout", heldout),
        evaluate("heldout", heldout, "discovery", discovery),
    ]
    passes = all(row["roc_auc"]["combined"] > row["roc_auc"]["disagreement"] for row in directions)
    report = {
        "status": "PASS_EXPLORATORY_MULTIVARIATE_TRANSFER" if passes else "FAIL_MULTIVARIATE_TRANSFER_ROUTE_CLOSED",
        "preregistration": args.preregistration,
        "inputs": {
            "discovery_sweep": args.discovery_sweep,
            "heldout_sweep": args.heldout_sweep,
            "discovery_warning": args.discovery_warning,
            "heldout_warning": args.heldout_warning,
            "normalization_npz": args.normalization_npz,
        },
        "directions": directions,
        "pass_rule": "combined ROC AUC strictly exceeds disagreement ROC AUC in both directions",
        "passed": passes,
        "decision": (
            "Exploratory support only; collect independent failure positives before calibration."
            if passes else
            "Close this nearest-neighbor/equal-weight multivariate route; do not tune it post hoc."
        ),
        "runtime_gate_authorized": False,
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Multivariate Reset-Health Transfer Result", "",
        f"Status: **{report['status']}**", "",
        "Offline existing-trace analysis only. No simulation, training, robot access, GPU, or Colab use.", "",
        "| train → test | failures | disagreement AUC | reset AUC | combined AUC | combined improvement |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["directions"]:
        scores = row["roc_auc"]
        lines.append(
            f"| {row['train_block']} → {row['test_block']} | {row['test_failures']}/{row['test_samples']} | "
            f"{scores['disagreement']:.3f} | {scores['reset']:.3f} | {scores['combined']:.3f} | "
            f"{scores['combined'] - scores['disagreement']:+.3f} |"
        )
    lines += ["", "## Frozen pass rule", "", report["pass_rule"] + ".", "",
              "## Decision", "", report["decision"], "",
              "No threshold or runtime gate is authorized by this analysis."]
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery-sweep", required=True)
    parser.add_argument("--heldout-sweep", required=True)
    parser.add_argument("--discovery-warning", required=True)
    parser.add_argument("--heldout-warning", required=True)
    parser.add_argument("--normalization-npz", required=True)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
