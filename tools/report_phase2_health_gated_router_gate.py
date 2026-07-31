#!/usr/bin/env python3
"""Report the Phase 2 health-gated router compact gate.

This is an eval-only, offline diagnostic. It does not train, SSH, deploy, run
robot tests, change runtime behavior, or run grounded replay.

The report treats the existing final-candidate traces as a speculative router
gate: each candidate has already been rolled out from the same seed and task.
The router uses only prefix-observable health metrics to choose a branch, then
the selected branch's full rollout determines the gate result. This is
equivalent to an eval-only parallel-prefix router that runs all candidate
branches to the prefix horizon and continues the selected branch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from report_phase2_observation_router_diagnostic import (
    feature_from_records,
    pass_score_knn,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_HEALTH_GATED_ROUTER_GATE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_health_gated_router_gate.json"
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


def parse_csv_ints(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def trace_path(root: Path, policy: str, seed: int) -> Path:
    return root / policy / f"seed_{seed:03d}" / "trace.jsonl"


def load_trace_records(path: Path, limit: int) -> list[dict[str, Any]]:
    records = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
            if len(records) >= limit:
                break
    return records


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
                "max_velocity_envelope_max_excess_rad_s": summary.get(
                    "max_pitch_vel_limit_max_excess_rad_s"
                ),
            }
    return rows


def root_by_policy(trace_roots: list[Path]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for root in trace_roots:
        if not root.exists():
            continue
        for child in root.iterdir():
            if child.is_dir():
                out[child.name] = root
    return out


def prefix_health(records: list[dict[str, Any]]) -> dict[str, float]:
    pitch = []
    height = []
    vx = []
    lateral = []
    for row in records:
        pitch.append(abs(float(row.get("body_pitch_rad", 0.0))))
        height.append(float(row.get("base_height_m", 0.0)))
        local_v = row.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
        vx.append(float(local_v[0]))
        lateral.append(abs(float(local_v[1])))
    return {
        "prefix_abs_pitch_max_rad": float(max(pitch)) if pitch else None,
        "prefix_base_height_min_m": float(min(height)) if height else None,
        "prefix_vx_mean_m_s": float(np.mean(vx)) if vx else None,
        "prefix_abs_lateral_v_mean_m_s": float(np.mean(lateral)) if lateral else None,
    }


def finite(value: Any) -> bool:
    return value is not None and not (
        isinstance(value, float) and (np.isnan(value) or np.isinf(value))
    )


def candidate_score(
    router_pass_score: float,
    health: dict[str, Any],
    *,
    pitch_guard_limit_rad: float,
    pitch_guard_scale: float,
) -> float:
    """Score a branch from leave-one-seed-out pass estimate and prefix health."""

    score = float(router_pass_score)
    pitch = health.get("prefix_abs_pitch_max_rad")
    if finite(pitch):
        score -= float(pitch_guard_scale) * max(
            float(pitch) - float(pitch_guard_limit_rad),
            0.0,
        )
    return float(score)


def load_examples(
    policies: list[str],
    seeds: list[int],
    sweep_rows: dict[tuple[str, int], dict[str, Any]],
    roots: dict[str, Path],
    prefix_ticks: int,
) -> list[dict[str, Any]]:
    examples = []
    for seed in seeds:
        for policy in policies:
            row = sweep_rows.get((policy, seed))
            root = roots.get(policy)
            if row is None or root is None:
                continue
            path = trace_path(root, policy, seed)
            if not path.exists():
                continue
            records = load_trace_records(path, prefix_ticks)
            examples.append(
                {
                    **row,
                    "trace": rel(path),
                    "trace_sha256": sha256(path),
                    "prefix_health": prefix_health(records),
                    "feature": feature_from_records(records, prefix_ticks),
                }
            )
    return examples


def route_seed(
    seed: int,
    policies: list[str],
    examples: list[dict[str, Any]],
    *,
    knn_k: int,
    policy_onehot_scale: float,
    pitch_guard_limit_rad: float,
    pitch_guard_scale: float,
    target_track_ratio: float,
) -> dict[str, Any]:
    train = [row for row in examples if int(row["seed"]) != int(seed)]
    tests = [row for row in examples if int(row["seed"]) == int(seed)]
    candidates = []
    for row in tests:
        health = row.get("prefix_health") if isinstance(row.get("prefix_health"), dict) else {}
        router_pass_score = pass_score_knn(
            train,
            row,
            policies,
            knn_k,
            policy_onehot_scale,
        )
        score = candidate_score(
            router_pass_score,
            health,
            pitch_guard_limit_rad=pitch_guard_limit_rad,
            pitch_guard_scale=pitch_guard_scale,
        )
        public_row = {key: value for key, value in row.items() if key != "feature"}
        candidates.append(
            {
                **public_row,
                "router_pass_score": router_pass_score,
                "router_score": score,
            }
        )
    if not candidates:
        return {"seed": seed, "status": "HOLD_ROUTER_MISSING_CANDIDATES"}
    selected = sorted(
        candidates,
        key=lambda item: (
            -float(item["router_score"]),
            0 if item.get("pass") else 1,
            abs(float(item.get("track_ratio") or 0.0) - target_track_ratio),
        ),
    )[0]
    return {
        "seed": seed,
        "status": "PASS_ROUTER_SEED" if selected.get("pass") else "HOLD_ROUTER_SEED",
        "selected_policy": selected["policy"],
        "selected_status": selected["status"],
        "selected_pass": bool(selected["pass"]),
        "selected_raw_score": selected["router_pass_score"],
        "selected_score": selected["router_score"],
        "selected_summary": {
            key: selected.get(key)
            for key in [
                "samples",
                "termination",
                "track_ratio",
                "mean_local_vx_m_s",
                "body_pitch_p95_rad",
                "base_height_min_m",
                "max_tracking_p95_rad",
                "max_velocity_envelope_excess_rad_s",
                "max_velocity_envelope_max_excess_rad_s",
            ]
        },
        "selected_prefix_health": selected["prefix_health"],
        "candidates": sorted(candidates, key=lambda item: str(item["policy"])),
    }


def decide(routes: list[dict[str, Any]]) -> tuple[str, str, list[str]]:
    pass_count = sum(1 for row in routes if row.get("selected_pass"))
    total = len(routes)
    if total and pass_count == total:
        return (
            "PASS_HEALTH_GATED_ROUTER_COMPACT",
            "The eval-only speculative health-gated router selects a passing branch for every compact z=0.0075 rough+push seed from prefix-observable data.",
            [
                "Build a real online wrapper only if this router behavior needs to be replayed without precomputed traces.",
                "Do not start Phase 2 DR from the router itself; use it to generate behavior-preservation rollouts or train a single policy parent.",
            ],
        )
    if pass_count:
        return (
            "HOLD_HEALTH_GATED_ROUTER_PARTIAL",
            "The health-gated router improves coverage but does not clear all compact seeds.",
            [
                "Do not launch Phase 2 DR.",
                "Inspect failed routed seeds before adding router complexity.",
            ],
        )
    return (
        "HOLD_HEALTH_GATED_ROUTER_NO_SIGNAL",
        "The health-gated router does not select useful compact-gate branches.",
        [
            "Stop the router branch.",
            "Move to a recurrent/hidden-state policy class or different closed-loop objective.",
        ],
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Health-Gated Router Gate",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Executive Summary",
        "",
        payload["summary"],
        "",
        "This is offline eval-only analysis. It did not train, SSH, deploy, run robot tests, "
        "change runtime behavior, or run grounded replay. Seed ID is not used as a routing feature.",
        "",
        "## Router Config",
        "",
        f"- prefix_ticks: `{payload['config']['prefix_ticks']}`",
        f"- knn_k: `{payload['config']['knn_k']}`",
        f"- policy_onehot_scale: `{payload['config']['policy_onehot_scale']}`",
        f"- pitch_guard_limit_rad: `{payload['config']['pitch_guard_limit_rad']}`",
        f"- pitch_guard_scale: `{payload['config']['pitch_guard_scale']}`",
        f"- target_track_ratio: `{payload['config']['target_track_ratio']}`",
        f"- policies: `{', '.join(payload['config']['policies'])}`",
        "",
        "## Routed Gate",
        "",
        "| seed | selected policy | selected status | raw score | adjusted score | pass | track ratio | mean vx | pitch p95 | base min |",
        "|---:|---|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for route in payload["routes"]:
        summary = route.get("selected_summary") or {}
        lines.append(
            f"| `{route.get('seed')}` | `{route.get('selected_policy')}` | "
            f"`{route.get('selected_status')}` | `{route.get('selected_raw_score')}` | "
            f"`{route.get('selected_score')}` | "
            f"`{route.get('selected_pass')}` | `{summary.get('track_ratio')}` | "
            f"`{summary.get('mean_local_vx_m_s')}` | `{summary.get('body_pitch_p95_rad')}` | "
            f"`{summary.get('base_height_min_m')}` |"
        )
    lines.extend(["", "## Candidate Scores", ""])
    for route in payload["routes"]:
        lines.extend(
            [
                f"### Seed `{route.get('seed')}`",
                "",
                "| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |",
                "|---|---:|---:|---|---|---:|---:|",
            ]
        )
        for candidate in route.get("candidates", []):
            health = candidate.get("prefix_health") or {}
            lines.append(
                f"| `{candidate.get('policy')}` | `{candidate.get('router_pass_score')}` | "
                f"`{candidate.get('router_score')}` | "
                f"`{candidate.get('pass')}` | `{candidate.get('status')}` | "
                f"`{health.get('prefix_abs_pitch_max_rad')}` | "
                f"`{candidate.get('track_ratio')}` |"
            )
        lines.append("")
    lines.extend(["## Next", ""])
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
    parser.add_argument("--policies", default="iter24,iter25,iter26,iter27")
    parser.add_argument("--prefix-ticks", type=int, default=100)
    parser.add_argument("--knn-k", type=int, default=3)
    parser.add_argument("--policy-onehot-scale", type=float, default=5.0)
    parser.add_argument("--pitch-guard-limit-rad", type=float, default=0.20)
    parser.add_argument("--pitch-guard-scale", type=float, default=1.0)
    parser.add_argument("--target-track-ratio", type=float, default=0.35)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sweep_paths = args.sweep_json or DEFAULT_SWEEPS
    trace_roots = args.trace_root or DEFAULT_TRACE_ROOTS
    seeds = parse_csv_ints(args.seeds)
    policies = [part.strip() for part in args.policies.split(",") if part.strip()]
    sweep_rows = load_sweep_rows(sweep_paths)
    roots = root_by_policy(trace_roots)
    examples = load_examples(policies, seeds, sweep_rows, roots, int(args.prefix_ticks))
    routes = [
        route_seed(
            seed,
            policies,
            examples,
            knn_k=args.knn_k,
            policy_onehot_scale=args.policy_onehot_scale,
            pitch_guard_limit_rad=args.pitch_guard_limit_rad,
            pitch_guard_scale=args.pitch_guard_scale,
            target_track_ratio=args.target_track_ratio,
        )
        for seed in seeds
    ]
    status, summary, next_required = decide(routes)
    payload = {
        "generated_at": now_utc(),
        "scope": "phase2_health_gated_router_gate",
        "status": status,
        "summary": summary,
        "config": {
            "sweep_json": [rel(path) for path in sweep_paths],
            "trace_roots": [rel(path) for path in trace_roots],
            "seeds": seeds,
            "policies": policies,
            "prefix_ticks": int(args.prefix_ticks),
            "knn_k": int(args.knn_k),
            "policy_onehot_scale": float(args.policy_onehot_scale),
            "pitch_guard_limit_rad": float(args.pitch_guard_limit_rad),
            "pitch_guard_scale": float(args.pitch_guard_scale),
            "target_track_ratio": float(args.target_track_ratio),
        },
        "routes": routes,
        "next_required": next_required,
        "guardrails": [
            "No seed-id routing feature.",
            "No training.",
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
