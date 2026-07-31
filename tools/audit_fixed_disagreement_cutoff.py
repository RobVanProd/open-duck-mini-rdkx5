#!/usr/bin/env python3
"""Audit one preregistered cutoff against saved early-warning scores."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [center - margin, center + margin]


def main() -> int:
    args = parse_args()
    source = json.loads(Path(args.input_json).read_text())
    rows = source["per_seed"]
    tp = fn = tn = fp = 0
    per_seed = []
    for row in rows:
        predicted = float(row[args.statistic]) >= args.cutoff
        actual = bool(row["failure"])
        tp += int(predicted and actual)
        fn += int(not predicted and actual)
        tn += int(not predicted and not actual)
        fp += int(predicted and not actual)
        per_seed.append({"seed": row["seed"], "failure": actual, "score": row[args.statistic], "flagged": predicted})
    sensitivity, specificity = tp / (tp + fn), tn / (tn + fp)
    enough = tp + fn >= args.minimum_failures
    report = {
        "status": "FIXED_CUTOFF_AUDIT_COMPLETE" if enough else "FIXED_CUTOFF_AUDIT_INCONCLUSIVE_TOO_FEW_FAILURES",
        "input_json": args.input_json,
        "statistic": args.statistic,
        "window_ticks": rows[0]["window_ticks"],
        "cutoff": args.cutoff,
        "minimum_failures": args.minimum_failures,
        "failures": tp + fn,
        "duration_complete": tn + fp,
        "confusion": {"tp": tp, "fn": fn, "tn": tn, "fp": fp},
        "sensitivity": sensitivity,
        "sensitivity_wilson_95": wilson(tp, tp + fn),
        "specificity": specificity,
        "specificity_wilson_95": wilson(tn, tn + fp),
        "balanced_accuracy": (sensitivity + specificity) / 2,
        "per_seed": per_seed,
        "cutoff_refit": False,
        "runtime_gate_authorized": False,
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict) -> None:
    c = report["confusion"]
    sl, sh = report["sensitivity_wilson_95"]
    pl, ph = report["specificity_wilson_95"]
    lines = [
        "# Fixed Disagreement Cutoff Audit", "", f"Status: **{report['status']}**", "",
        "Offline saved-score analysis only. The cutoff was not refit.", "",
        f"- cutoff: `{report['cutoff']:.8f}` on first `{report['window_ticks']}` ticks `{report['statistic']}`",
        f"- TP/FN/TN/FP: `{c['tp']}/{c['fn']}/{c['tn']}/{c['fp']}`",
        f"- sensitivity: `{report['sensitivity']:.3f}` (Wilson 95% `{sl:.3f}`-`{sh:.3f}`)",
        f"- specificity: `{report['specificity']:.3f}` (Wilson 95% `{pl:.3f}`-`{ph:.3f}`)",
        f"- balanced accuracy: `{report['balanced_accuracy']:.3f}`", "",
        "This audit does not authorize a runtime or robot gate.",
    ]
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--statistic", default="p95")
    parser.add_argument("--cutoff", type=float, required=True)
    parser.add_argument("--minimum-failures", type=int, default=5)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
