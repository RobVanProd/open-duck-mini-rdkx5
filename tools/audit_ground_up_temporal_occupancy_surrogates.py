#!/usr/bin/env python3
"""Run the preregistered smooth temporal-occupancy surrogate diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


INDICES = np.asarray([2, 3, 4, 11, 12, 13])
THRESHOLD = 0.20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sigmoid(value: np.ndarray) -> np.ndarray:
    out = np.empty_like(value)
    positive = value >= 0
    out[positive] = 1.0 / (1.0 + np.exp(-value[positive]))
    exp_value = np.exp(value[~positive])
    out[~positive] = exp_value / (1.0 + exp_value)
    return out


def summarize(path: Path, candidates: list[dict]) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=np.float64)
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=np.float64)
    error = np.abs(sent[:, INDICES] - actual[:, INDICES])
    excess = np.maximum(error - THRESHOLD, 0.0)
    p95 = np.percentile(error, 95, axis=0)
    occupancy = np.mean(error > THRESHOLD, axis=0)
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": len(rows),
        "group": path.parent.name,
        "command_x": float(rows[0]["command"][0]),
        "seed": int(rows[0]["seed"]),
        "exact_max_joint_occupancy": float(np.max(occupancy)),
        "exact_max_joint_exceedance_ticks": int(np.max(np.sum(error > THRESHOLD, axis=0))),
        "max_joint_p95_rad": float(np.max(p95)),
        "six_joint_squared_hinge_mean": float(np.mean(np.square(excess))),
        "six_joint_linear_hinge_mean": float(np.mean(excess)),
        "surrogates": {
            item["name"]: float(
                np.mean(sigmoid((error - THRESHOLD) / item["temperature_rad"]))
            )
            for item in candidates
        },
    }


def discordances(rows: list[dict], score_key, target_key: str) -> list[dict]:
    found = []
    for left, right in itertools.permutations(rows, 2):
        left_target = left[target_key]
        right_target = right[target_key]
        if left_target == right_target:
            continue
        if score_key(left) < score_key(right) and left_target > right_target:
            found.append(
                {
                    "lower_scored": left["path"],
                    "higher_scored": right["path"],
                    "lower_score_target": left_target,
                    "higher_score_target": right_target,
                }
            )
    return found


def correlation(rows: list[dict], score_key, target_key: str) -> float:
    score = np.asarray([score_key(row) for row in rows], dtype=np.float64)
    target = np.asarray([row[target_key] for row in rows], dtype=np.float64)
    return float(np.corrcoef(score, target)[0, 1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    candidates = prereg["candidates"]
    hash_checks = {}
    for name, item in (
        ("temporal_occupancy_audit", prereg["inputs"]["temporal_occupancy_audit"]),
        ("tracking_tail_result", prereg["inputs"]["tracking_tail_result"]),
        ("pitch_rate_result", prereg["inputs"]["pitch_rate_result"]),
    ):
        path = Path(item["path"])
        hash_checks[name] = path.is_file() and sha256(path) == item["sha256"]

    traces = []
    for directory in sorted(path for path in args.trace_root.iterdir() if path.is_dir()):
        traces.extend(summarize(path, candidates) for path in sorted(directory.glob("*.jsonl")))
    unique = [row for row in traces if row["seed"] == prereg["inputs"]["unique_ranking_seed"]]

    pairs = {}
    for row in traces:
        pairs.setdefault((row["group"], row["command_x"]), []).append(row)
    reproduction_fields = [
        "exact_max_joint_occupancy",
        "max_joint_p95_rad",
        "six_joint_squared_hinge_mean",
        "six_joint_linear_hinge_mean",
    ]
    reproduction_deltas = []
    for key, rows in sorted(pairs.items()):
        if len(rows) != 2:
            reproduction_deltas.append({"key": key, "missing_pair": True})
            continue
        left, right = sorted(rows, key=lambda row: row["seed"])
        fields = {
            name: abs(left[name] - right[name]) for name in reproduction_fields
        }
        fields.update(
            {
                f"surrogate_{candidate['name']}": abs(
                    left["surrogates"][candidate["name"]]
                    - right["surrogates"][candidate["name"]]
                )
                for candidate in candidates
            }
        )
        reproduction_deltas.append(
            {"group": key[0], "command_x": key[1], "deltas": fields}
        )
    max_reproduction_delta = max(
        (
            value
            for item in reproduction_deltas
            for value in item.get("deltas", {}).values()
        ),
        default=float("inf"),
    )

    score_functions = {
        "six_joint_squared_hinge_mean": lambda row: row["six_joint_squared_hinge_mean"],
        "six_joint_linear_hinge_mean": lambda row: row["six_joint_linear_hinge_mean"],
    }
    score_functions.update(
        {
            candidate["name"]: lambda row, name=candidate["name"]: row["surrogates"][name]
            for candidate in candidates
        }
    )
    scores = {}
    for name, fn in score_functions.items():
        primary = discordances(unique, fn, "exact_max_joint_occupancy")
        secondary = discordances(unique, fn, "max_joint_p95_rad")
        scores[name] = {
            "primary_occupancy_discordant_pairs": len(primary),
            "secondary_p95_discordant_pairs": len(secondary),
            "exact_occupancy_correlation": correlation(
                unique, fn, "exact_max_joint_occupancy"
            ),
            "p95_correlation": correlation(unique, fn, "max_joint_p95_rad"),
            "primary_discordances": primary,
            "secondary_discordances": secondary,
        }

    squared = scores["six_joint_squared_hinge_mean"]
    linear = scores["six_joint_linear_hinge_mean"]
    advancing = []
    for candidate in candidates:
        name = candidate["name"]
        item = scores[name]
        item["beats_both_baselines_primary"] = item[
            "primary_occupancy_discordant_pairs"
        ] < min(
            squared["primary_occupancy_discordant_pairs"],
            linear["primary_occupancy_discordant_pairs"],
        )
        item["beats_both_baselines_secondary"] = item[
            "secondary_p95_discordant_pairs"
        ] < min(
            squared["secondary_p95_discordant_pairs"],
            linear["secondary_p95_discordant_pairs"],
        )
        item["advance"] = (
            item["beats_both_baselines_primary"]
            and item["beats_both_baselines_secondary"]
        )
        if item["advance"]:
            advancing.append(candidate)

    checks = {
        "preregistration_status_valid": prereg["status"]
        == "PREREGISTERED_CPU_DIAGNOSTIC_ONLY",
        "all_input_hashes_match": all(hash_checks.values()),
        "all_36_traces_present": len(traces) == prereg["inputs"]["expected_trace_count"],
        "all_traces_have_600_rows": all(row["rows"] == 600 for row in traces),
        "all_18_unique_rows_present": len(unique)
        == prereg["inputs"]["expected_unique_policy_command_rows"],
        "seed_100_101_diagnostics_reproduce_exactly": max_reproduction_delta == 0.0,
        "all_scores_finite": all(
            np.isfinite(item[key])
            for item in scores.values()
            for key in ("exact_occupancy_correlation", "p95_correlation")
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        status = "FAIL_TEMPORAL_OCCUPANCY_SURROGATE_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
        selected = None
    elif advancing:
        selected = sorted(
            advancing,
            key=lambda candidate: (
                scores[candidate["name"]]["primary_occupancy_discordant_pairs"],
                scores[candidate["name"]]["secondary_p95_discordant_pairs"],
                -abs(scores[candidate["name"]]["exact_occupancy_correlation"]),
                -candidate["temperature_rad"],
            ),
        )[0]
        status = "PASS_TEMPORAL_OCCUPANCY_SURROGATE_WITH_WINNER"
        decision = f"AUTHORIZE_IMPLEMENTATION_CONTRACT_{selected['name']}"
    else:
        status = "PASS_TEMPORAL_OCCUPANCY_SURROGATE_NO_WINNER"
        decision = "CLOSE_SMOOTH_OCCUPANCY_SURROGATE_FAMILY"
        selected = None

    payload = {
        "schema_version": "ground_up_temporal_occupancy_surrogate_screen_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "input_hash_checks": hash_checks,
        "preregistration": {
            "path": str(args.preregistration.resolve()),
            "sha256": sha256(args.preregistration),
        },
        "trace_count": len(traces),
        "unique_ranking_rows": len(unique),
        "max_seed_reproduction_delta": max_reproduction_delta,
        "scores": scores,
        "selected": selected,
        "rows": traces,
        "authority": {
            "implementation_contract": selected is not None,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Temporal-Occupancy Surrogate Screen Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "| diagnostic | occupancy discordance | p95 discordance | occupancy correlation | advances |",
        "|---|---:|---:|---:|---|",
    ]
    for name in score_functions:
        item = scores[name]
        lines.append(
            f"| `{name}` | {item['primary_occupancy_discordant_pairs']} | "
            f"{item['secondary_p95_discordant_pairs']} | "
            f"{item['exact_occupancy_correlation']:.9f} | "
            f"`{item.get('advance', False)}` |"
        )
    lines.extend(
        [
            "",
            f"seed-100/101 maximum diagnostic delta: `{max_reproduction_delta}`",
            f"selected candidate: `{selected['name'] if selected else None}`",
            "",
            (
                "A selected surrogate authorizes only an implementation and CPU contract. "
                "It does not authorize training, Colab, x=0, RDK-X5, or robot access."
                if selected
                else "No smooth occupancy surrogate met the frozen dual-ranking rule; the family is closed without training."
            ),
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "selected": selected}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
