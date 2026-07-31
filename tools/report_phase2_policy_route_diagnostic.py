#!/usr/bin/env python3
"""Report whether existing Phase 2 policies are complementary across seeds.

This is an offline/read-only diagnostic. It does not train, SSH, deploy, run
robot tests, or change runtime behavior. It answers a narrow question after the
BC-only live-oracle and PPO-compatible warm-start holds:

  Is there an oracle seed-level route through existing deployable candidates
  that clears the task-matched z=0.0075 rough+push compact gate?

If yes, a validation-aware mixture/router diagnostic is evidence-aligned. If no,
the next useful branch should skip mixture routing and change policy class or
training objective directly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_POLICY_ROUTE_DIAGNOSTIC.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_policy_route_diagnostic.json"

DEFAULT_DECISIONS = [
    ROOT / "outputs/analysis/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_decision.json",
    ROOT / "outputs/analysis/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_decision.json",
    ROOT / "outputs/analysis/phase2_z0075_iter26_dual_anchor_weight2_history_context_rate150_decision.json",
    ROOT / "outputs/analysis/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_decision.json",
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


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def artifact(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def candidate_path(payload: dict[str, Any]) -> str | None:
    candidate = payload.get("candidate")
    if isinstance(candidate, dict):
        return candidate.get("path") or candidate.get("onnx")
    if isinstance(candidate, str):
        return candidate
    return None


def candidate_sha(payload: dict[str, Any]) -> str | None:
    candidate = payload.get("candidate")
    if isinstance(candidate, dict):
        return candidate.get("onnx_sha256") or candidate.get("sha256")
    return None


def seed_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    gate = payload.get("gate")
    if not isinstance(gate, dict):
        return []
    if isinstance(gate.get("x008"), dict):
        seeds = gate["x008"].get("seeds")
        if isinstance(seeds, dict):
            rows = []
            for seed_text, row in seeds.items():
                if not isinstance(row, dict):
                    continue
                item = dict(row)
                item["seed"] = int(seed_text)
                item["max_velocity_envelope_excess_rad_s"] = item.get("max_vel_excess")
                item["mean_local_vx_m_s"] = item.get("mean_local_vx")
                rows.append(item)
            return sorted(rows, key=lambda item: int(item["seed"]))
    if isinstance(gate.get("seeds"), list):
        rows = []
        for row in gate["seeds"]:
            if not isinstance(row, dict):
                continue
            item = dict(row)
            item["max_velocity_envelope_excess_rad_s"] = item.get(
                "max_velocity_envelope_excess_rad_s", item.get("max_vel_excess")
            )
            rows.append(item)
        return sorted(rows, key=lambda item: int(item.get("seed", -1)))
    return []


def summarize_decision(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    out = {"artifact": artifact(path)}
    if payload is None:
        out["status"] = "MISSING_DECISION"
        return out
    rows = seed_rows(payload)
    pass_count = sum(1 for row in rows if row.get("status") == "PASS_CANDIDATE_SIM_GATE")
    fall_count = len(rows) - pass_count
    out.update(
        {
            "status": payload.get("status"),
            "candidate": candidate_path(payload),
            "candidate_sha256": candidate_sha(payload),
            "rows": rows,
            "pass_count": pass_count,
            "total_count": len(rows),
            "fall_count": fall_count,
            "max_velocity_envelope_excess_rad_s": max(
                (row.get("max_velocity_envelope_excess_rad_s") or 0.0 for row in rows),
                default=None,
            ),
        }
    )
    return out


def score_pass(row: dict[str, Any]) -> tuple[float, float, float]:
    """Prefer lower tracking, then lower absolute vx overshoot, then lower pitch."""

    tracking = float(row.get("max_tracking_p95_rad") or 999.0)
    track_ratio = float(row.get("track_ratio") or 0.0)
    ratio_cost = abs(track_ratio - 0.35)
    pitch = float(row.get("body_pitch_p95_rad") or 999.0)
    return tracking, ratio_cost, pitch


def build_route(candidates: list[dict[str, Any]], required_seeds: list[int]) -> dict[str, Any]:
    route: dict[str, Any] = {}
    missing: list[int] = []
    for seed in required_seeds:
        passing: list[tuple[tuple[float, float, float], dict[str, Any], dict[str, Any]]] = []
        for candidate in candidates:
            for row in candidate.get("rows", []):
                if int(row.get("seed", -1)) != seed:
                    continue
                if row.get("status") != "PASS_CANDIDATE_SIM_GATE":
                    continue
                if (row.get("max_velocity_envelope_excess_rad_s") or 0.0) > 0.0:
                    continue
                passing.append((score_pass(row), candidate, row))
        if not passing:
            missing.append(seed)
            continue
        _, candidate, row = sorted(passing, key=lambda item: item[0])[0]
        route[str(seed)] = {
            "candidate": candidate.get("candidate"),
            "candidate_sha256": candidate.get("candidate_sha256"),
            "source_decision": candidate["artifact"]["path"],
            "status": row.get("status"),
            "samples": row.get("samples"),
            "termination": row.get("termination"),
            "track_ratio": row.get("track_ratio"),
            "mean_local_vx_m_s": row.get("mean_local_vx_m_s"),
            "body_pitch_p95_rad": row.get("body_pitch_p95_rad"),
            "base_height_min_m": row.get("base_height_min_m"),
            "max_tracking_p95_rad": row.get("max_tracking_p95_rad"),
            "max_velocity_envelope_excess_rad_s": row.get("max_velocity_envelope_excess_rad_s"),
        }
    return {
        "required_seeds": required_seeds,
        "covered_seeds": sorted(int(seed) for seed in route),
        "missing_seeds": missing,
        "route": route,
        "pass_count": len(route),
        "total_count": len(required_seeds),
        "oracle_covers_gate": not missing and len(route) == len(required_seeds),
    }


def decide(route: dict[str, Any]) -> tuple[str, str, list[str]]:
    if route.get("oracle_covers_gate"):
        return (
            "PASS_ORACLE_ROUTE_EXISTS",
            "Existing deployable candidates are complementary across the compact z=0.0075 rough+push seeds. A validation-aware mixture/router diagnostic is evidence-aligned, but this is not deployable or trainable evidence by itself.",
            [
                "Build an offline router/mixture diagnostic that chooses among these candidates from observation/history, not seed id.",
                "Gate the router on the same z=0.0075 rough+push compact screen before any PPO/DR launch.",
                "If the router clears the compact gate, use its rollouts to define the trainable behavior-preservation target.",
                "If no observation-based router clears the compact gate, skip mixture routing and move to recurrent/hidden-state training.",
            ],
        )
    return (
        "HOLD_NO_ORACLE_ROUTE",
        "Existing deployable candidates do not even cover the compact z=0.0075 rough+push seed set under oracle seed-level selection. Mixture routing is unlikely to be the next useful branch.",
        [
            "Skip validation-aware mixture routing for now.",
            "Move directly to a new policy class or optimization objective.",
        ],
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    route = payload["oracle_route"]
    lines = [
        "# Phase 2 Policy Route Diagnostic",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Executive Summary",
        "",
        payload["summary"],
        "",
        "This is an offline/read-only diagnostic. It did not train, SSH, deploy, run robot tests, "
        "change runtime behavior, or run grounded replay.",
        "",
        "## Candidate Pass Matrix",
        "",
        "| candidate | status | pass/total | passing seeds | max velocity excess |",
        "|---|---|---:|---|---:|",
    ]
    for candidate in payload["candidates"]:
        passing = [
            str(row.get("seed"))
            for row in candidate.get("rows", [])
            if row.get("status") == "PASS_CANDIDATE_SIM_GATE"
        ]
        lines.append(
            f"| `{candidate.get('candidate')}` | `{candidate.get('status')}` | "
            f"`{candidate.get('pass_count')}/{candidate.get('total_count')}` | "
            f"`{','.join(passing)}` | `{candidate.get('max_velocity_envelope_excess_rad_s')}` |"
        )
    lines.extend(
        [
            "",
            "## Oracle Seed-Level Route",
            "",
            f"- required seeds: `{route['required_seeds']}`",
            f"- covered seeds: `{route['covered_seeds']}`",
            f"- missing seeds: `{route['missing_seeds']}`",
            f"- oracle_covers_gate: `{route['oracle_covers_gate']}`",
            "",
            "| seed | routed candidate | samples | track ratio | mean vx | tracking p95 | velocity excess |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for seed in route["required_seeds"]:
        row = route["route"].get(str(seed))
        if row is None:
            lines.append(f"| {seed} | `MISSING` | NA | NA | NA | NA | NA |")
            continue
        lines.append(
            f"| {seed} | `{row.get('candidate')}` | `{row.get('samples')}` | "
            f"`{row.get('track_ratio')}` | `{row.get('mean_local_vx_m_s')}` | "
            f"`{row.get('max_tracking_p95_rad')}` | `{row.get('max_velocity_envelope_excess_rad_s')}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    for item in payload["next_required"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "This diagnostic does not reopen Phase 2 DR training by itself. It only says whether "
            "a router/mixture branch has an oracle upper bound worth testing.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_seed_list(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", action="append", type=Path, default=None)
    parser.add_argument("--required-seeds", default="0,1,2,6,7")
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decision_paths = args.decision or DEFAULT_DECISIONS
    candidates = [summarize_decision(path) for path in decision_paths]
    route = build_route(candidates, parse_seed_list(args.required_seeds))
    status, summary, next_required = decide(route)
    payload = {
        "generated_at": now_utc(),
        "scope": "offline_phase2_policy_route_diagnostic",
        "status": status,
        "summary": summary,
        "candidates": candidates,
        "oracle_route": route,
        "next_required": next_required,
        "guardrails": [
            "No robot tests.",
            "No SSH.",
            "No deploy.",
            "No grounded replay.",
            "No runtime behavior change.",
            "Do not use seed id as deployable routing input.",
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
