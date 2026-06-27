#!/usr/bin/env python3
"""Audit whether configured reward terms appear in candidate eval artifacts.

This is an offline evidence tool. It does not train, SSH, deploy, or touch the
robot. It is intended to catch cases where a staged recipe configures nonzero
reward scales but the recovered closed-loop eval artifacts do not expose the
corresponding reward/cost metrics.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and not (
        math.isnan(float(value)) or math.isinf(float(value))
    )


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def load_reward_overrides(path: Path, phase_name: str | None) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    selected: Any = payload
    if isinstance(payload, dict) and isinstance(payload.get("phases"), list):
        phases = payload["phases"]
        if phase_name:
            matches = [phase for phase in phases if phase.get("name") == phase_name]
            if not matches:
                raise SystemExit(f"phase {phase_name!r} not found in {path}")
            selected = matches[0]
        elif phases:
            selected = phases[0]
    if isinstance(selected, dict) and isinstance(
        selected.get("training_recipe_overrides"), dict
    ):
        selected = selected["training_recipe_overrides"]
    if not isinstance(selected, dict):
        raise SystemExit(f"reward overrides did not contain an object: {path}")
    return selected


def configured_terms(overrides: dict[str, Any]) -> dict[str, float]:
    terms: dict[str, float] = {}
    for key, value in overrides.items():
        if not key.endswith("_scale") or not finite(value):
            continue
        scale = float(value)
        if scale == 0.0:
            continue
        terms[key[: -len("_scale")]] = scale
    return terms


def iter_eval_jsons(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("closed_loop_actuator_bridge_eval.json"))


def mode_reward_terms(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    closed = payload.get("closed_loop_sim") or {}
    modes = closed.get("modes") or {}
    output: dict[str, dict[str, Any]] = {}
    if isinstance(modes, dict):
        for mode_name, mode_payload in modes.items():
            if isinstance(mode_payload, dict):
                output[str(mode_name)] = mode_payload.get("reward_terms") or {}
    return output


def term_status(term: str, scale: float, observed: list[dict[str, Any]]) -> dict[str, Any]:
    metric_name = f"reward/{term}" if scale > 0 else f"cost/{term}"
    opposite_name = f"cost/{term}" if scale > 0 else f"reward/{term}"
    values: list[float] = []
    seen_metric = 0
    seen_opposite = 0
    for reward_terms in observed:
        if metric_name in reward_terms:
            seen_metric += 1
            stats = reward_terms.get(metric_name) or {}
            if isinstance(stats, dict):
                for key in ("mean", "p95", "max", "min"):
                    value = stats.get(key)
                    if finite(value):
                        values.append(float(value))
        if opposite_name in reward_terms:
            seen_opposite += 1
    max_abs = max((abs(value) for value in values), default=None)
    if seen_metric == 0 and seen_opposite == 0:
        status = "MISSING"
    elif max_abs is not None and max_abs == 0.0:
        status = "OBSERVED_ZERO"
    else:
        status = "OBSERVED_NONZERO"
    return {
        "term": term,
        "scale": scale,
        "expected_metric": metric_name,
        "opposite_metric_seen_count": seen_opposite,
        "observed_count": seen_metric,
        "status": status,
        "max_abs_stat": max_abs,
    }


def audit(args: argparse.Namespace) -> dict[str, Any]:
    overrides = load_reward_overrides(args.reward_overrides_json, args.reward_overrides_phase)
    terms = configured_terms(overrides)
    eval_paths = iter_eval_jsons(args.eval_path)
    if not eval_paths:
        raise SystemExit(f"no closed_loop_actuator_bridge_eval.json files under {args.eval_path}")

    observed_by_mode: list[dict[str, Any]] = []
    eval_summaries: list[dict[str, Any]] = []
    for path in eval_paths:
        payload = json.loads(path.read_text())
        modes = mode_reward_terms(payload)
        for mode_name, reward_terms in modes.items():
            observed_by_mode.append(reward_terms)
            eval_summaries.append(
                {
                    "path": str(path),
                    "mode": mode_name,
                    "overall_status": payload.get("overall_status"),
                    "reward_term_count": len(reward_terms),
                }
            )

    term_rows = [
        term_status(term, scale, observed_by_mode)
        for term, scale in sorted(terms.items())
    ]
    missing = [row["term"] for row in term_rows if row["status"] == "MISSING"]
    observed_zero = [
        row["term"] for row in term_rows if row["status"] == "OBSERVED_ZERO"
    ]
    if missing:
        status = "HOLD_REWARD_TERMS_MISSING"
    elif observed_zero:
        status = "WARN_REWARD_TERMS_ZERO"
    else:
        status = "PASS_REWARD_TERMS_OBSERVED"
    return {
        "status": status,
        "reward_overrides_json": str(args.reward_overrides_json),
        "reward_overrides_phase": args.reward_overrides_phase,
        "eval_path": str(args.eval_path),
        "eval_files": eval_summaries,
        "configured_nonzero_terms": terms,
        "term_audit": term_rows,
        "missing_terms": missing,
        "observed_zero_terms": observed_zero,
        "robot_tests_run": False,
        "ssh_run": False,
        "deploy_run": False,
        "runtime_behavior_changed": False,
    }


def write_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Reward Term Activation Audit",
        "",
        f"status: `{report['status']}`",
        "",
        "## Inputs",
        "",
        f"- reward overrides: `{report['reward_overrides_json']}`",
        f"- phase: `{report.get('reward_overrides_phase') or 'first/default'}`",
        f"- eval path: `{report['eval_path']}`",
        f"- eval files: `{len(report['eval_files'])}`",
        "",
        "## Term Audit",
        "",
        "| term | scale | expected metric | observed files | max abs stat | status |",
        "|---|---:|---|---:|---:|---|",
    ]
    for row in report["term_audit"]:
        lines.append(
            "| {term} | {scale} | `{metric}` | {count} | {max_abs} | `{status}` |".format(
                term=row["term"],
                scale=fmt(row["scale"]),
                metric=row["expected_metric"],
                count=row["observed_count"],
                max_abs=fmt(row["max_abs_stat"]),
                status=row["status"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if report["missing_terms"]:
        lines.append(
            "Configured nonzero reward scales were missing from the recovered eval "
            "reward-term summaries. Treat the gate as behaviorally valid, but do "
            "not claim those terms were observed during eval without a trace that "
            "contains them."
        )
        lines.append("")
        lines.append("Missing terms:")
        lines.append("")
        for term in report["missing_terms"]:
            lines.append(f"- `{term}`")
    elif report["observed_zero_terms"]:
        lines.append(
            "All configured nonzero reward terms were present, but at least one "
            "remained zero in the recovered summaries."
        )
    else:
        lines.append("All configured nonzero reward terms were observed.")
    lines.extend(
        [
            "",
            "No robot tests, SSH, deployment, runtime behavior changes, or training "
            "were performed by this audit.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reward-overrides-json", type=Path, required=True)
    parser.add_argument("--reward-overrides-phase")
    parser.add_argument(
        "--eval-path",
        type=Path,
        required=True,
        help="A closed_loop_actuator_bridge_eval.json file or directory containing them.",
    )
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    report = audit(args)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        write_md(args.output_md, report)
    if not args.output_json and not args.output_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
