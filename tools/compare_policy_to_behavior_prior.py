#!/usr/bin/env python3
"""Compare deployable ONNX policies against a behavior-prior MLP on a BC manifest.

This is offline analysis only. It does not train, SSH, deploy, or touch robot
runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from run_target_dataset_bc_smoke import load_manifest_samples


def percentile(values: np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def swish(x: np.ndarray) -> np.ndarray:
    return x / (1.0 + np.exp(-x))


def predict_mlp_npz(npz_path: Path, observations: np.ndarray) -> np.ndarray:
    payload = np.load(npz_path, allow_pickle=True)
    mean, std = np.asarray(payload["norm"], dtype=np.float64)
    x = (observations.astype(np.float64) - mean) / np.maximum(std, 1.0e-6)
    activation = str(np.asarray(payload["activation"]).reshape(-1)[0])
    for index in range(3):
        x = x @ np.asarray(payload[f"w{index}"], dtype=np.float64)
        x = x + np.asarray(payload[f"b{index}"], dtype=np.float64)
        if activation == "swish":
            x = swish(x)
        elif activation == "tanh":
            x = np.tanh(x)
        elif activation == "relu":
            x = np.maximum(x, 0.0)
        else:
            raise ValueError(f"unsupported activation {activation!r}")
    action = x @ np.asarray(payload["w3"], dtype=np.float64)
    action = action + np.asarray(payload["b3"], dtype=np.float64)
    output_mode = str(np.asarray(payload["output_mode"]).reshape(-1)[0])
    if output_mode in {"tanh", "ppo_tanh_loc"}:
        action = np.tanh(action)
    elif output_mode not in {"linear", "none"}:
        raise ValueError(f"unsupported output_mode {output_mode!r}")
    return np.clip(action, -1.0, 1.0)


def predict_onnx(policy: Path, observations: np.ndarray) -> np.ndarray:
    import onnxruntime as ort

    session = ort.InferenceSession(str(policy), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    outputs = []
    for row in observations.astype(np.float32):
        result = session.run([output_name], {input_name: row[None, :]})[0]
        outputs.append(np.asarray(result, dtype=np.float64).reshape(-1))
    return np.vstack(outputs)


def abs_stats(values: np.ndarray) -> dict[str, float | None]:
    arr = np.abs(np.asarray(values, dtype=float))
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return {"mean": None, "p50": None, "p95": None, "p99": None, "max": None}
    return {
        "mean": float(np.mean(finite)),
        "p50": percentile(finite, 50),
        "p95": percentile(finite, 95),
        "p99": percentile(finite, 99),
        "max": float(np.max(finite)),
    }


def summarize_policy(
    policy: Path,
    observations: np.ndarray,
    teacher_actions: np.ndarray,
    manifest_actions: np.ndarray,
) -> dict[str, Any]:
    pred = predict_onnx(policy, observations)
    teacher_delta = pred - teacher_actions
    manifest_delta = pred - manifest_actions
    action_abs = np.abs(pred)
    saturation = np.mean(action_abs >= 0.999) * 100.0
    return {
        "policy": str(policy),
        "policy_name": policy.stem,
        "samples": int(observations.shape[0]),
        "teacher_delta_abs": abs_stats(teacher_delta),
        "manifest_delta_abs": abs_stats(manifest_delta),
        "action_abs": abs_stats(pred),
        "action_saturation_pct": float(saturation),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Policy vs Behavior Prior",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline comparison only. No training, SSH, deploy, robot test, or runtime",
        "behavior change was performed.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{report['manifest']}`",
        f"- behavior prior NPZ: `{report['behavior_prior_npz']}`",
        f"- samples: `{report['samples']}`",
        "",
        "## Policy Summary",
        "",
        "| policy | teacher L1 mean | teacher L1 p95 | manifest L1 p95 | action abs p95 | saturation % |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in report["policies"]:
        teacher = item["teacher_delta_abs"]
        manifest = item["manifest_delta_abs"]
        action_abs = item["action_abs"]
        lines.append(
            f"| `{item['policy_name']}` | "
            f"{teacher['mean']:.4f} | {teacher['p95']:.4f} | "
            f"{manifest['p95']:.4f} | {action_abs['p95']:.4f} | "
            f"{item['action_saturation_pct']:.2f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    manifest, samples, _entries = load_manifest_samples(
        Path(args.manifest),
        include_source_regex=args.source_include_regex,
        exclude_source_regex=args.source_exclude_regex,
    )
    observations = samples.observations.astype(np.float64)
    manifest_actions = samples.actions.astype(np.float64)
    if args.max_samples is not None:
        observations = observations[: args.max_samples]
        manifest_actions = manifest_actions[: args.max_samples]
    teacher_actions = predict_mlp_npz(Path(args.behavior_prior_npz), observations)
    policies = [
        summarize_policy(Path(policy), observations, teacher_actions, manifest_actions)
        for policy in args.policies
    ]
    max_teacher_p95 = max(
        float(item["teacher_delta_abs"]["p95"] or 0.0) for item in policies
    )
    status = (
        "WARN_POLICY_TEACHER_DIVERGENCE"
        if max_teacher_p95 > args.teacher_delta_p95_warn
        else "PASS_POLICY_TEACHER_CLOSE"
    )
    interpretation = (
        "At least one policy has a large p95 action difference from the behavior-prior teacher on the teacher dataset. "
        "If that policy also regresses gate behavior, the PPO update is not preserving the deployable behavior prior."
        if status == "WARN_POLICY_TEACHER_DIVERGENCE"
        else "The compared policies remain close to the behavior-prior teacher on the teacher dataset; gate regression is more likely closed-loop instability than offline teacher mismatch."
    )
    report = {
        "status": status,
        "manifest": str(args.manifest),
        "manifest_status": manifest.get("status"),
        "dataset_id": manifest.get("dataset_id"),
        "behavior_prior_npz": str(args.behavior_prior_npz),
        "samples": int(observations.shape[0]),
        "thresholds": {"teacher_delta_p95_warn": float(args.teacher_delta_p95_warn)},
        "policies": policies,
        "interpretation": interpretation,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--behavior-prior-npz", required=True)
    parser.add_argument("--policies", nargs="+", required=True)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--source-include-regex", default=None)
    parser.add_argument("--source-exclude-regex", default=None)
    parser.add_argument("--teacher-delta-p95-warn", type=float, default=0.08)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/POLICY_BEHAVIOR_PRIOR_COMPARISON.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/policy_behavior_prior_comparison.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
