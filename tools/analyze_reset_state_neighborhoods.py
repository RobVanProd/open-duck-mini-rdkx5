#!/usr/bin/env python3
"""Measure whether initial policy observations organize closed-loop outcomes.

Offline analysis only: reads saved seed-sweep JSON and full-observation traces.
It does not simulate, train, deploy, access a robot, or use a GPU.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    result = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        end = start
        while end + 1 < values.size and values[order[end + 1]] == values[order[start]]:
            end += 1
        result[order[start : end + 1]] = (start + end) / 2.0
        start = end + 1
    return result


def correlation(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    return {
        "pearson": float(np.corrcoef(a, b)[0, 1]),
        "spearman": float(np.corrcoef(rank(a), rank(b))[0, 1]),
    }


def load_initial_observation(path: Path) -> np.ndarray:
    first = json.loads(path.read_text().splitlines()[0])
    observation = np.asarray(first.get("obs_state"), dtype=np.float64)
    if observation.shape != (101,):
        raise ValueError(f"expected obs_state[101] in {path}, got {observation.shape}")
    return observation


def outcome_class(result: dict[str, Any]) -> str:
    summary = result["summary"]
    if summary.get("termination_reason") != "duration_complete":
        return "fall_or_termination"
    status = str(result.get("status") or "")
    if "LOW_FORWARD_PROGRESS" in status:
        return "low_forward_progress"
    if "TRACKING" in status:
        return "tracking_hold"
    if "PASS" in status:
        return "pass"
    return "other"


def main() -> int:
    args = parse_args()
    norm = np.load(Path(args.normalization_npz), allow_pickle=False)["norm"]
    mean, std = np.asarray(norm[0], dtype=float), np.asarray(norm[1], dtype=float)
    std = np.maximum(std, 1.0e-6)
    rows = []
    for sweep_path_text in args.sweeps:
        sweep_path = Path(sweep_path_text)
        sweep = json.loads(sweep_path.read_text())
        for result in sweep.get("results", []):
            trace_path = Path(result["output_dir"]) / "trace.jsonl"
            observation = load_initial_observation(trace_path)
            rows.append(
                {
                    "seed": int(result["seed"]),
                    "sweep": str(sweep_path),
                    "trace": str(trace_path),
                    "status": result.get("status"),
                    "outcome_class": outcome_class(result),
                    "termination_reason": result["summary"].get("termination_reason"),
                    "samples": result["summary"].get("samples"),
                    "mean_vx_m_s": float(result["summary"]["mean_local_vx_m_s"]),
                    "initial_observation": observation,
                    "normalized_observation": (observation - mean) / std,
                }
            )
    rows.sort(key=lambda item: item["seed"])
    seeds = [item["seed"] for item in rows]
    if len(seeds) != len(set(seeds)):
        raise ValueError(f"duplicate seeds across sweeps: {seeds}")
    observations = np.asarray([item["normalized_observation"] for item in rows])
    velocities = np.asarray([item["mean_vx_m_s"] for item in rows])
    distances = np.sqrt(
        np.mean((observations[:, None, :] - observations[None, :, :]) ** 2, axis=2)
    )
    np.fill_diagonal(distances, np.inf)

    neighbor_rows = []
    predictions = {1: [], 3: []}
    for index, item in enumerate(rows):
        order = np.argsort(distances[index])
        neighbors = []
        for neighbor_index in order[: args.neighbors_to_report]:
            neighbor = rows[int(neighbor_index)]
            neighbors.append(
                {
                    "seed": neighbor["seed"],
                    "distance": float(distances[index, neighbor_index]),
                    "mean_vx_m_s": neighbor["mean_vx_m_s"],
                    "outcome_class": neighbor["outcome_class"],
                }
            )
        for k in predictions:
            predictions[k].append(float(np.mean(velocities[order[:k]])))
        neighbor_rows.append(
            {
                "seed": item["seed"],
                "mean_vx_m_s": item["mean_vx_m_s"],
                "outcome_class": item["outcome_class"],
                "neighbors": neighbors,
            }
        )

    prediction_metrics = {}
    baseline_prediction = np.full_like(velocities, np.mean(velocities))
    for k, predicted in predictions.items():
        predicted_array = np.asarray(predicted)
        prediction_metrics[f"knn_{k}"] = {
            "rmse_m_s": float(np.sqrt(np.mean((predicted_array - velocities) ** 2))),
            "correlation": correlation(velocities, predicted_array),
        }
    prediction_metrics["global_mean"] = {
        "rmse_m_s": float(np.sqrt(np.mean((baseline_prediction - velocities) ** 2)))
    }
    complete_mask = np.asarray(
        [item["termination_reason"] == "duration_complete" for item in rows], dtype=bool
    )
    complete_predicted = np.asarray(predictions[1])[complete_mask]
    complete_velocities = velocities[complete_mask]
    prediction_metrics["knn_1_duration_complete_only"] = {
        "samples": int(np.sum(complete_mask)),
        "rmse_m_s": float(
            np.sqrt(np.mean((complete_predicted - complete_velocities) ** 2))
        ),
        "correlation": correlation(complete_velocities, complete_predicted),
    }

    target = next((item for item in neighbor_rows if item["seed"] == args.target_seed), None)
    report = {
        "status": "PASS_RESET_STATE_NEIGHBORHOOD_ANALYSIS_READY",
        "sweeps": args.sweeps,
        "normalization_npz": args.normalization_npz,
        "samples": len(rows),
        "seed_range": [min(seeds), max(seeds)],
        "outcome_counts": {
            name: sum(item["outcome_class"] == name for item in rows)
            for name in sorted({item["outcome_class"] for item in rows})
        },
        "duration_complete": sum(
            item["termination_reason"] == "duration_complete" for item in rows
        ),
        "falls_or_terminations": sum(
            item["termination_reason"] != "duration_complete" for item in rows
        ),
        "velocity": {
            "mean_m_s": float(np.mean(velocities)),
            "p50_m_s": float(np.percentile(velocities, 50)),
            "min_m_s": float(np.min(velocities)),
            "max_m_s": float(np.max(velocities)),
        },
        "prediction_metrics": prediction_metrics,
        "target_seed": target,
        "nearest_neighbors": neighbor_rows,
        "limitations": [
            "Nearest-neighbor association is not a causal recovery policy.",
            "One-second mean velocity from terminated traces is truncated by the fall.",
            "The teacher normalization weights observation dimensions according to its dataset, not an independently validated reset-state metric.",
            "Twenty-four resets remain too few to define a deployment or training router.",
        ],
        "offline_only": True,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    velocity = report["velocity"]
    lines = [
        "# Reset-State Neighborhood Analysis",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline saved-trace analysis only. No simulation, training, robot access,",
        "deployment, GPU, or Colab allocation was performed by this analysis.",
        "",
        "## Dataset",
        "",
        f"- resets: `{report['samples']}` (seeds {report['seed_range'][0]}-{report['seed_range'][1]})",
        f"- duration complete: `{report['duration_complete']}`",
        f"- falls/terminations: `{report['falls_or_terminations']}`",
        f"- outcome counts: `{report['outcome_counts']}`",
        f"- mean/median vx: `{velocity['mean_m_s']:.5f}` / `{velocity['p50_m_s']:.5f}` m/s",
        f"- min/max vx: `{velocity['min_m_s']:.5f}` / `{velocity['max_m_s']:.5f}` m/s",
        "",
        "## Leave-One-Out Neighborhood Prediction",
        "",
        "| predictor | RMSE (m/s) | Pearson | Spearman |",
        "|---|---:|---:|---:|",
    ]
    for key in (
        "global_mean",
        "knn_1",
        "knn_1_duration_complete_only",
        "knn_3",
    ):
        item = report["prediction_metrics"][key]
        corr = item.get("correlation") or {}
        lines.append(
            f"| `{key}` | {item['rmse_m_s']:.5f} | "
            f"{corr.get('pearson', float('nan')):.3f} | "
            f"{corr.get('spearman', float('nan')):.3f} |"
        )
    target = report.get("target_seed")
    if target:
        lines += [
            "",
            f"## Target Seed {target['seed']} Neighborhood",
            "",
            f"Target outcome: `{target['outcome_class']}`, vx `{target['mean_vx_m_s']:.5f}` m/s",
            "",
            "| neighbor | distance | vx (m/s) | outcome |",
            "|---:|---:|---:|---|",
        ]
        for item in target["neighbors"]:
            lines.append(
                f"| {item['seed']} | {item['distance']:.4f} | "
                f"{item['mean_vx_m_s']:.5f} | `{item['outcome_class']}` |"
            )
    lines += [
        "",
        "## Closest Pair per Seed",
        "",
        "| seed | vx | outcome | nearest seed | distance | nearest vx | nearest outcome |",
        "|---:|---:|---|---:|---:|---:|---|",
    ]
    for item in report["nearest_neighbors"]:
        neighbor = item["neighbors"][0]
        lines.append(
            f"| {item['seed']} | {item['mean_vx_m_s']:.5f} | `{item['outcome_class']}` | "
            f"{neighbor['seed']} | {neighbor['distance']:.4f} | "
            f"{neighbor['mean_vx_m_s']:.5f} | `{neighbor['outcome_class']}` |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "Nearby reset observations sometimes share sharply similar outcomes,",
        "including the seed-6/15 low-progress neighborhood and seed-9/12 fall",
        "neighborhood. The reset state is therefore behaviorally relevant. It is",
        "not sufficient as a universal classifier: falls occupy multiple",
        "neighborhoods and some close states have different gate outcomes.",
        "",
        "The evidence supports reset-state robustness as the next problem, not a",
        "global phase teacher or a deployment router. Temporal recovery trajectories",
        "for each recurrent failure neighborhood are required before another",
        "intervention can be specified.",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweeps", nargs="+", required=True)
    parser.add_argument("--normalization-npz", required=True)
    parser.add_argument("--target-seed", type=int, default=6)
    parser.add_argument("--neighbors-to-report", type=int, default=5)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
