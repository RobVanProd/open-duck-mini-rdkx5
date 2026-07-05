#!/usr/bin/env python3
"""Offline observation/history router diagnostic for Phase 2 policies.

This tests whether the existing Iter24-27 candidate family has a learnable
observation-conditioned routing signal. It is diagnostic only: no training for
deployment, no robot, no SSH, no grounded replay, and no runtime changes.

The diagnostic uses leave-one-seed-out evaluation. For a held seed, it scores
each candidate policy using only that policy's trace-derived observation/history
features and a nearest-neighbor pass estimator trained on the other seeds. Seed
ID is never included as a feature.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_OBSERVATION_ROUTER_DIAGNOSTIC.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_observation_router_diagnostic.json"
DEFAULT_SWEEPS = [
    ROOT / "outputs/analysis/phase2_policy_route_trace_iter24_27.json",
    ROOT / "outputs/analysis/phase2_policy_route_trace_iter25_26.json",
]
DEFAULT_TRACE_ROOTS = [
    ROOT / "outputs/analysis/phase2_policy_route_trace_iter24_27",
    ROOT / "outputs/analysis/phase2_policy_route_trace_iter25_26",
]


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_csv_ints(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def parse_csv_floats(text: str) -> list[float]:
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def trace_path(root: Path, policy: str, seed: int) -> Path:
    return root / policy / f"seed_{seed:03d}" / "trace.jsonl"


def load_trace_records(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            rows.append(json.loads(line))
            if len(rows) >= limit:
                break
    return rows


def feature_from_records(records: list[dict[str, Any]], prefix_ticks: int) -> np.ndarray:
    prefix = records[: max(1, prefix_ticks)]
    obs_rows = []
    aux_rows = []
    for row in prefix:
        obs = np.asarray(row.get("obs_state"), dtype=np.float64).reshape(-1)
        if obs.shape != (101,):
            raise ValueError("trace row missing obs_state[101]")
        obs_rows.append(obs)
        aux_rows.append(
            np.asarray(
                [
                    float(row.get("body_pitch_rad", 0.0)),
                    float(row.get("base_height_m", 0.0)),
                    *(row.get("local_linvel_m_s") or [0.0, 0.0, 0.0])[:3],
                    *(row.get("foot_contacts") or [0.0, 0.0])[:2],
                    float(row.get("push_magnitude", 0.0)),
                ],
                dtype=np.float64,
            )
        )
    obs_arr = np.asarray(obs_rows, dtype=np.float64)
    aux_arr = np.asarray(aux_rows, dtype=np.float64)
    if prefix_ticks <= 1:
        return np.concatenate([obs_arr[0], aux_arr[0]])
    return np.concatenate(
        [
            obs_arr[0],
            obs_arr[-1],
            obs_arr.mean(axis=0),
            obs_arr.std(axis=0),
            aux_arr[0],
            aux_arr[-1],
            aux_arr.mean(axis=0),
            aux_arr.std(axis=0),
        ]
    )


def health_from_records(records: list[dict[str, Any]]) -> dict[str, float]:
    pitch = []
    base_height = []
    vx = []
    lateral_v = []
    for row in records:
        pitch.append(abs(float(row.get("body_pitch_rad", 0.0))))
        base_height.append(float(row.get("base_height_m", 0.0)))
        local_v = row.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
        vx.append(float(local_v[0]))
        lateral_v.append(abs(float(local_v[1])))
    return {
        "prefix_abs_pitch_max_rad": float(max(pitch)) if pitch else 0.0,
        "prefix_base_height_min_m": float(min(base_height)) if base_height else 0.0,
        "prefix_vx_mean_m_s": float(np.mean(vx)) if vx else 0.0,
        "prefix_abs_lateral_v_mean_m_s": float(np.mean(lateral_v)) if lateral_v else 0.0,
    }


def load_sweep_rows(sweep_paths: list[Path]) -> dict[tuple[str, int], dict[str, Any]]:
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for path in sweep_paths:
        payload = load_json(path)
        for row in payload.get("results", []):
            policy = str(row.get("policy_label") or row.get("policy"))
            seed = int(row.get("seed"))
            summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
            rows[(policy, seed)] = {
                "policy": policy,
                "policy_path": row.get("policy"),
                "seed": seed,
                "status": row.get("status"),
                "pass": row.get("status") == "PASS_CANDIDATE_SIM_GATE",
                "samples": summary.get("samples"),
                "termination": summary.get("termination_reason"),
                "track_ratio": summary.get("track_ratio"),
                "mean_local_vx_m_s": summary.get("mean_local_vx_m_s"),
                "body_pitch_p95_rad": summary.get("body_pitch_p95_rad"),
                "base_height_min_m": summary.get("base_height_min_m"),
                "max_tracking_p95_rad": summary.get("max_tracking_p95_rad"),
                "max_velocity_envelope_excess_rad_s": summary.get(
                    "max_pitch_vel_limit_excess_rad_s"
                ),
            }
    return rows


def load_examples(
    trace_roots: list[Path],
    sweep_rows: dict[tuple[str, int], dict[str, Any]],
    seeds: list[int],
    prefix_ticks: int,
) -> list[dict[str, Any]]:
    examples = []
    root_by_policy: dict[str, Path] = {}
    for root in trace_roots:
        if not root.exists():
            continue
        for policy_dir in root.iterdir():
            if policy_dir.is_dir():
                root_by_policy[policy_dir.name] = root

    for (policy, seed), row in sorted(sweep_rows.items()):
        if seed not in seeds:
            continue
        root = root_by_policy.get(policy)
        if root is None:
            continue
        path = trace_path(root, policy, seed)
        if not path.exists():
            continue
        records = load_trace_records(path, prefix_ticks)
        feature = feature_from_records(records, prefix_ticks)
        health = health_from_records(records)
        examples.append(
            {
                **row,
                "trace": rel(path),
                "trace_sha256": sha256(path),
                "feature": feature,
                "prefix_health": health,
            }
        )
    return examples


def normalize(train_x: np.ndarray, test_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train_x.mean(axis=0)
    std = train_x.std(axis=0)
    std = np.where(std < 1.0e-8, 1.0, std)
    return (train_x - mean) / std, (test_x - mean) / std


def policy_one_hot(policy: str, policies: list[str]) -> np.ndarray:
    out = np.zeros((len(policies),), dtype=np.float64)
    out[policies.index(policy)] = 1.0
    return out


def pass_score_knn(
    train: list[dict[str, Any]],
    test: dict[str, Any],
    policies: list[str],
    k: int,
    policy_onehot_scale: float,
) -> float:
    train_x = np.asarray([row["feature"] for row in train], dtype=np.float64)
    test_x = np.asarray([test["feature"]], dtype=np.float64)
    train_norm, test_norm = normalize(train_x, test_x)
    if policy_onehot_scale > 0.0:
        train_policy = np.asarray(
            [policy_one_hot(str(row["policy"]), policies) * policy_onehot_scale for row in train],
            dtype=np.float64,
        )
        test_policy = policy_one_hot(str(test["policy"]), policies)[None, :] * policy_onehot_scale
        train_norm = np.concatenate([train_norm, train_policy], axis=1)
        test_norm = np.concatenate([test_norm, test_policy], axis=1)
    distances = np.linalg.norm(train_norm - test_norm[0], axis=1)
    nearest = np.argsort(distances)[: max(1, min(k, len(train)))]
    weights = 1.0 / np.maximum(distances[nearest], 1.0e-6)
    labels = np.asarray([1.0 if train[i]["pass"] else 0.0 for i in nearest], dtype=np.float64)
    return float(np.sum(labels * weights) / np.sum(weights))


def evaluate_router(
    examples: list[dict[str, Any]],
    seeds: list[int],
    k: int,
    policy_onehot_scale: float,
    pitch_guard_scale: float,
    pitch_guard_limit_rad: float,
) -> dict[str, Any]:
    policies = sorted({str(row["policy"]) for row in examples})
    routes = []
    for held_seed in seeds:
        train = [row for row in examples if int(row["seed"]) != held_seed]
        tests = [row for row in examples if int(row["seed"]) == held_seed]
        scored = []
        for row in tests:
            pass_score = pass_score_knn(train, row, policies, k, policy_onehot_scale)
            health = row.get("prefix_health") if isinstance(row.get("prefix_health"), dict) else {}
            pitch_excess = max(
                float(health.get("prefix_abs_pitch_max_rad", 0.0)) - float(pitch_guard_limit_rad),
                0.0,
            )
            scored.append(
                {
                    **row,
                    "router_pass_score": pass_score,
                    "pitch_guard_excess_rad": pitch_excess,
                    "router_adjusted_score": pass_score - float(pitch_guard_scale) * pitch_excess,
                }
            )
        if not scored:
            routes.append({"seed": held_seed, "status": "MISSING_TEST_ROWS"})
            continue
        selected = sorted(
            scored,
            key=lambda row: (
                -float(row["router_adjusted_score"]),
                0 if row["pass"] else 1,
                abs(float(row.get("track_ratio") or 0.0) - 0.35),
            ),
        )[0]
        routes.append(
            {
                "seed": held_seed,
                "selected_policy": selected["policy"],
                "selected_status": selected["status"],
                "selected_pass": bool(selected["pass"]),
                "router_pass_score": selected["router_pass_score"],
                "router_adjusted_score": selected["router_adjusted_score"],
                "pitch_guard_excess_rad": selected["pitch_guard_excess_rad"],
                "prefix_health": selected.get("prefix_health"),
                "track_ratio": selected.get("track_ratio"),
                "mean_local_vx_m_s": selected.get("mean_local_vx_m_s"),
                "max_tracking_p95_rad": selected.get("max_tracking_p95_rad"),
                "max_velocity_envelope_excess_rad_s": selected.get(
                    "max_velocity_envelope_excess_rad_s"
                ),
                "scores": [
                    {
                        "policy": row["policy"],
                        "pass": bool(row["pass"]),
                        "status": row["status"],
                        "score": row["router_pass_score"],
                        "adjusted_score": row["router_adjusted_score"],
                        "pitch_guard_excess_rad": row["pitch_guard_excess_rad"],
                        "prefix_health": row.get("prefix_health"),
                        "track_ratio": row.get("track_ratio"),
                    }
                    for row in sorted(scored, key=lambda item: str(item["policy"]))
                ],
            }
        )
    pass_count = sum(1 for row in routes if row.get("selected_pass"))
    return {
        "k": int(k),
        "policy_onehot_scale": float(policy_onehot_scale),
        "pitch_guard_scale": float(pitch_guard_scale),
        "pitch_guard_limit_rad": float(pitch_guard_limit_rad),
        "pass_count": pass_count,
        "total_count": len(seeds),
        "routes": routes,
        "passes_compact_gate": pass_count == len(seeds),
    }


def decide(evaluations: list[dict[str, Any]]) -> tuple[str, str, list[str]]:
    passing = [row for row in evaluations if row.get("passes_compact_gate")]
    best = max(evaluations, key=lambda row: row.get("pass_count", 0), default=None)
    if passing:
        return (
            "PASS_OBSERVATION_ROUTER_OFFLINE",
            "A leave-one-seed-out observation/history router can select passing candidates for all compact z=0.0075 rough+push seeds in this offline trace diagnostic. This supports building a real closed-loop router gate next.",
            [
                "Implement an eval-only router wrapper that chooses among candidate policies online without seed id.",
                "Gate the router on the canonical z=0.0075 rough+push compact screen.",
                "Only if the router gate passes, generate trainable behavior-preservation rollouts for Phase 2 DR.",
            ],
        )
    if best and best.get("pass_count", 0) >= 4:
        return (
            "HOLD_ROUTER_NEAR_MISS",
            "The offline router improves candidate selection but does not cover all compact seeds. Inspect the missed seed before building an online wrapper.",
            [
                "Do not launch DR from this router.",
                "Inspect the missed seed/policy scores and either improve router features or move to recurrent policy class.",
            ],
        )
    return (
        "HOLD_ROUTER_SIGNAL_WEAK",
        "The offline router cannot recover the oracle seed-level route from observation/history features. Skip mixture routing and move to recurrent/hidden-state or different training objective.",
        [
            "Do not spend compute on an online router wrapper.",
            "Use the router result as evidence for changing policy class or objective.",
        ],
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Observation Router Diagnostic",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Executive Summary",
        "",
        payload["summary"],
        "",
        "This is offline analysis only. It did not train, SSH, deploy, run robot tests, "
        "change runtime behavior, or run grounded replay. Seed ID is not used as a feature.",
        "",
        "## Evaluations",
        "",
        "| prefix ticks | k | policy onehot scale | pitch guard scale | pass/total | result |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for evaluation in payload["evaluations"]:
        result = "PASS" if evaluation["passes_compact_gate"] else "HOLD"
        lines.append(
            f"| `{evaluation['prefix_ticks']}` | `{evaluation['k']}` | "
            f"`{evaluation['policy_onehot_scale']}` | "
            f"`{evaluation['pitch_guard_scale']}` | "
            f"`{evaluation['pass_count']}/{evaluation['total_count']}` | `{result}` |"
        )
    lines.extend(["", "## Best Evaluation", ""])
    best = payload["best_evaluation"]
    lines.extend(
        [
            f"- prefix_ticks: `{best['prefix_ticks']}`",
            f"- k: `{best['k']}`",
            f"- policy_onehot_scale: `{best['policy_onehot_scale']}`",
            f"- pitch_guard_scale: `{best['pitch_guard_scale']}`",
            f"- pitch_guard_limit_rad: `{best['pitch_guard_limit_rad']}`",
            f"- pass_count: `{best['pass_count']}` / `{best['total_count']}`",
            "",
            "| seed | selected policy | selected status | score | adjusted score | pitch excess | track ratio | mean vx |",
            "|---:|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for route in best["routes"]:
        lines.append(
            f"| `{route.get('seed')}` | `{route.get('selected_policy')}` | "
            f"`{route.get('selected_status')}` | `{route.get('router_pass_score')}` | "
            f"`{route.get('router_adjusted_score')}` | "
            f"`{route.get('pitch_guard_excess_rad')}` | "
            f"`{route.get('track_ratio')}` | `{route.get('mean_local_vx_m_s')}` |"
        )
    missed = [route for route in best["routes"] if not route.get("selected_pass")]
    if missed:
        lines.extend(
            [
                "",
                "## Missed Seed Details",
                "",
                "These rows show why the offline router is not promotable as a deployable "
                "online wrapper yet. Scores are computed without seed ID.",
                "",
            ]
        )
        for route in missed:
            lines.extend(
                [
                    f"### Seed `{route.get('seed')}`",
                    "",
                    "| policy | score | adjusted score | pitch excess | pass | status | track ratio |",
                    "|---|---:|---:|---:|---|---|---:|",
                ]
            )
            for score in route.get("scores", []):
                lines.append(
                    f"| `{score.get('policy')}` | `{score.get('score')}` | "
                    f"`{score.get('adjusted_score')}` | "
                    f"`{score.get('pitch_guard_excess_rad')}` | "
                    f"`{score.get('pass')}` | `{score.get('status')}` | "
                    f"`{score.get('track_ratio')}` |"
                )
    lines.extend(["", "## Next", ""])
    for item in payload["next_required"]:
        lines.append(f"- {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-json", action="append", type=Path, default=None)
    parser.add_argument("--trace-root", action="append", type=Path, default=None)
    parser.add_argument("--seeds", default="0,1,2,6,7")
    parser.add_argument("--prefix-ticks", default="1,5,25,50,100,200")
    parser.add_argument("--knn-k", type=int, default=3)
    parser.add_argument("--policy-onehot-scales", default="0,1,5")
    parser.add_argument("--pitch-guard-scales", default="0,1")
    parser.add_argument("--pitch-guard-limit-rad", type=float, default=0.20)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sweep_paths = args.sweep_json or DEFAULT_SWEEPS
    trace_roots = args.trace_root or DEFAULT_TRACE_ROOTS
    seeds = parse_csv_ints(args.seeds)
    sweep_rows = load_sweep_rows(sweep_paths)

    evaluations = []
    for prefix_ticks in parse_csv_ints(args.prefix_ticks):
        examples = load_examples(trace_roots, sweep_rows, seeds, prefix_ticks)
        for policy_scale in parse_csv_floats(args.policy_onehot_scales):
            for pitch_guard_scale in parse_csv_floats(args.pitch_guard_scales):
                evaluation = evaluate_router(
                    examples,
                    seeds,
                    args.knn_k,
                    policy_scale,
                    pitch_guard_scale,
                    args.pitch_guard_limit_rad,
                )
                evaluation["prefix_ticks"] = int(prefix_ticks)
                evaluation["example_count"] = len(examples)
                evaluations.append(evaluation)

    status, summary, next_required = decide(evaluations)
    best = max(
        evaluations,
        key=lambda row: (row.get("pass_count", 0), row.get("prefix_ticks", 0), row.get("policy_onehot_scale", 0)),
    )
    payload = {
        "generated_at": now_utc(),
        "scope": "offline_phase2_observation_router_diagnostic",
        "status": status,
        "summary": summary,
        "sweep_json": [rel(path) for path in sweep_paths],
        "trace_roots": [rel(path) for path in trace_roots],
        "seeds": seeds,
        "evaluations": evaluations,
        "best_evaluation": best,
        "next_required": next_required,
        "guardrails": [
            "No seed-id feature.",
            "No robot tests.",
            "No SSH.",
            "No deploy.",
            "No grounded replay.",
            "No runtime behavior change.",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(status)
    print(rel(args.output_md))
    print(rel(args.output_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
