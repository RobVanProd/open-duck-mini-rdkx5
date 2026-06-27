#!/usr/bin/env python3
"""Relabel rollout trace observations with an offline BC teacher.

This supports DAgger-style offline diagnostics: collect states visited by a
student, query a safer teacher for those states, and write ignored JSONL traces
whose `action` field is the teacher action. It does not train, deploy, SSH, or
touch the robot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from eval_reference_motion_rollout import percentile
from run_target_dataset_bc_smoke import (
    load_manifest_samples,
    make_blend_model,
    parse_csv_floats,
    predict_knn,
    predict_ridge,
    select_alpha,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "BC_TRACE_RELABEL.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "bc_trace_relabel.json"


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def predict_blend_model(
    model: dict[str, Any],
    obs: np.ndarray,
    blend_alpha_override: float | None = None,
) -> np.ndarray:
    linear_pred = predict_ridge(obs, model["weights"], model["linear_norm"])
    knn_pred = predict_knn(
        obs,
        model["train_x"],
        model["train_y"],
        model["knn_norm"],
        int(model["k"]),
    )
    alpha = float(model["blend_alpha"] if blend_alpha_override is None else blend_alpha_override)
    return np.clip(alpha * knn_pred + (1.0 - alpha) * linear_pred, -1.0, 1.0).reshape(-1)


def load_teacher(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest, samples, entries = load_manifest_samples(
        Path(args.teacher_manifest),
        include_source_regex=args.include_source_regex,
        exclude_source_regex=args.exclude_source_regex,
    )
    fit = select_alpha(samples, parse_csv_floats(args.ridge_alphas))
    if args.teacher_model_kind == "blend":
        model = make_blend_model(
            samples,
            fit,
            kind="blend",
            knn_k=args.knn_k,
            blend_alpha=args.blend_alpha,
        )
    elif args.teacher_model_kind == "source_vx_blend":
        alt_manifest, alt_samples, alt_entries = load_manifest_samples(
            Path(args.teacher_manifest),
            include_source_regex=args.alt_include_source_regex,
            exclude_source_regex=args.alt_exclude_source_regex,
        )
        if alt_manifest.get("dataset_id") != manifest.get("dataset_id"):
            raise ValueError("alternate manifest dataset id mismatch")
        alt_fit = select_alpha(alt_samples, parse_csv_floats(args.ridge_alphas))
        model = {
            "kind": "source_vx_blend",
            "primary_model": make_blend_model(
                samples,
                fit,
                kind="vx_blend",
                knn_k=args.knn_k,
                blend_alpha=args.blend_alpha,
                vx_blend_alpha=args.vx_blend_alpha,
                vx_blend_threshold_m_s=args.vx_blend_threshold_m_s,
            ),
            "alt_model": make_blend_model(
                alt_samples,
                alt_fit,
                kind="vx_blend",
                knn_k=args.knn_k,
                blend_alpha=args.blend_alpha,
                vx_blend_alpha=args.vx_blend_alpha,
                vx_blend_threshold_m_s=args.vx_blend_threshold_m_s,
            ),
            "source_vx_threshold_m_s": float(args.source_vx_threshold_m_s),
        }
        entries = entries + alt_entries
    else:
        raise ValueError(f"unsupported teacher_model_kind {args.teacher_model_kind}")
    meta = {
        "teacher_manifest": str(args.teacher_manifest),
        "teacher_dataset_id": manifest.get("dataset_id"),
        "teacher_entries": len(entries),
        "teacher_samples": int(samples.observations.shape[0]),
        "teacher_model_kind": args.teacher_model_kind,
        "knn_k": int(args.knn_k),
        "blend_alpha": float(args.blend_alpha),
        "vx_blend_alpha": float(args.vx_blend_alpha),
        "vx_blend_threshold_m_s": float(args.vx_blend_threshold_m_s),
        "source_vx_threshold_m_s": float(args.source_vx_threshold_m_s),
        "include_source_regex": args.include_source_regex,
        "exclude_source_regex": args.exclude_source_regex,
        "alt_include_source_regex": args.alt_include_source_regex,
        "alt_exclude_source_regex": args.alt_exclude_source_regex,
        "best_alpha": fit["best_alpha"],
    }
    return model, meta


def row_forward_velocity(row: dict[str, Any]) -> float:
    local_linvel = row.get("local_linvel_m_s")
    if isinstance(local_linvel, list | tuple) and local_linvel:
        try:
            return float(local_linvel[0])
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def row_lateral_velocity_abs(row: dict[str, Any]) -> float:
    local_linvel = row.get("local_linvel_m_s")
    if isinstance(local_linvel, list | tuple) and len(local_linvel) > 1:
        try:
            return abs(float(local_linvel[1]))
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def row_contact_key(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if isinstance(contacts, list | tuple) and len(contacts) == 2:
        return f"{int(contacts[0])}{int(contacts[1])}"
    return "NA"


def row_tracking_error(row: dict[str, Any]) -> float:
    sent = row.get("sent_target_rad")
    actual = row.get("actual_position_rad")
    if not (
        isinstance(sent, list | tuple)
        and isinstance(actual, list | tuple)
        and len(sent) == len(actual) == 14
    ):
        return 0.0
    err = np.abs(np.asarray(sent, dtype=float) - np.asarray(actual, dtype=float))
    finite = err[np.isfinite(err)]
    return float(np.max(finite)) if finite.size else 0.0


def gate_sample_weight(row: dict[str, Any], args: argparse.Namespace) -> tuple[float, list[str]]:
    if not args.gate_aware_sample_weights:
        return 1.0, []

    weight = float(args.gate_base_weight)
    reasons: list[str] = []
    vx = row_forward_velocity(row)
    command_x = max(abs(float(args.gate_command_x)), 1.0e-9)
    track_ratio = vx / command_x
    contacts = row_contact_key(row)

    if contacts == "11" and track_ratio < float(args.gate_min_track_ratio):
        weight = max(weight, float(args.gate_double_support_weight))
        reasons.append("double_support_low_progress")
    if track_ratio < float(args.gate_min_track_ratio):
        weight = max(weight, float(args.gate_low_progress_weight))
        reasons.append("low_progress")
    if vx < 0.0:
        weight = max(weight, float(args.gate_reverse_weight))
        reasons.append("reverse_velocity")
    if row_lateral_velocity_abs(row) > float(args.gate_high_abs_vy_m_s):
        weight = max(weight, float(args.gate_lateral_weight))
        reasons.append("high_lateral_velocity")
    if row_tracking_error(row) > float(args.gate_high_tracking_rad):
        weight = max(weight, float(args.gate_tracking_weight))
        reasons.append("high_tracking_error")

    return min(weight, float(args.gate_max_weight)), reasons


def predict_teacher_model(
    model: dict[str, Any], obs: np.ndarray, row: dict[str, Any]
) -> tuple[np.ndarray, str, float]:
    if model["kind"] == "blend":
        return predict_blend_model(model, obs), "primary", float(model["blend_alpha"])
    if model["kind"] == "source_vx_blend":
        vx = row_forward_velocity(row)
        use_alt_model = vx >= float(model["source_vx_threshold_m_s"])
        active_model = model["alt_model"] if use_alt_model else model["primary_model"]
        alpha = (
            float(active_model["vx_blend_alpha"])
            if vx >= float(active_model["vx_blend_threshold_m_s"])
            else float(active_model["blend_alpha"])
        )
        action = predict_blend_model(active_model, obs, blend_alpha_override=alpha)
        return action, "alt" if use_alt_model else "primary", alpha
    raise ValueError(f"unsupported model kind {model['kind']}")


def relabel_trace(
    path: Path,
    output_dir: Path,
    model: dict[str, Any],
    args: argparse.Namespace,
    *,
    truncate_before_done: bool = False,
) -> dict[str, Any]:
    rows = read_jsonl(path)
    samples_in = len(rows)
    done_index = None
    if truncate_before_done:
        for index, row in enumerate(rows):
            if bool(row.get("done")):
                done_index = index
                rows = rows[:index]
                break
    output_rows = []
    deltas = []
    active_models: Counter[str] = Counter()
    alpha_values = []
    sample_weights = []
    sample_weight_reasons: Counter[str] = Counter()
    skipped = 0
    for row in rows:
        obs = row.get("obs_state")
        if obs is None or len(obs) != 101:
            skipped += 1
            continue
        obs_arr = np.asarray(obs, dtype=float).reshape(1, -1)
        teacher_action, active_model, alpha = predict_teacher_model(model, obs_arr, row)
        teacher_action = teacher_action.astype(float)
        active_models[active_model] += 1
        alpha_values.append(float(alpha))
        original_action = row.get("action")
        if original_action is not None and len(original_action) == 14:
            delta = np.abs(teacher_action - np.asarray(original_action, dtype=float))
            deltas.extend(delta.reshape(-1).tolist())
        new_row = dict(row)
        new_row["original_action"] = original_action
        new_row["action"] = teacher_action.tolist()
        new_row["relabel_teacher"] = model["kind"]
        new_row["relabel_teacher_active_model"] = active_model
        new_row["relabel_teacher_blend_alpha"] = alpha
        sample_weight, reasons = gate_sample_weight(row, args)
        new_row["sample_weight"] = sample_weight
        new_row["sample_weight_reasons"] = reasons
        sample_weights.append(float(sample_weight))
        sample_weight_reasons.update(reasons or ["base"])
        new_row["mode"] = f"relabel_{model['kind']}_teacher"
        output_rows.append(new_row)
    parent_depth = max(1, int(args.output_parent_depth))
    parent_parts = list(path.parent.parts[-parent_depth:])
    output_path = output_dir.joinpath(*parent_parts, path.name)
    write_jsonl(output_path, output_rows)
    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "samples_in": samples_in,
        "samples_out": len(output_rows),
        "skipped": skipped,
        "truncate_before_done": bool(truncate_before_done),
        "first_done_index": done_index,
        "action_delta_p50": percentile(deltas, 50) if deltas else None,
        "action_delta_p95": percentile(deltas, 95) if deltas else None,
        "action_delta_max": max(deltas) if deltas else None,
        "active_model_counts": dict(sorted(active_models.items())),
        "blend_alpha_p50": percentile(alpha_values, 50) if alpha_values else None,
        "blend_alpha_p95": percentile(alpha_values, 95) if alpha_values else None,
        "sample_weight_p50": percentile(sample_weights, 50) if sample_weights else None,
        "sample_weight_p95": percentile(sample_weights, 95) if sample_weights else None,
        "sample_weight_max": max(sample_weights) if sample_weights else None,
        "sample_weight_reasons": dict(sorted(sample_weight_reasons.items())),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    def trace_label(item: dict[str, Any]) -> str:
        output_trace = Path(item["output_trace"])
        try:
            return str(output_trace.relative_to(Path(payload["output_trace_dir"])))
        except ValueError:
            source_path = Path(item["source_trace"])
            return f"{source_path.parent.name}/{source_path.name}"

    lines = [
        "# BC Trace Relabel",
        "",
        f"status: `{payload['status']}`",
        "",
        "This offline artifact relabels student-visited observations with a teacher action.",
        "Raw JSONL outputs remain ignored and are referenced only for local follow-up.",
        "",
        "## Teacher",
        "",
    ]
    for key, value in payload["teacher"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- traces: `{payload['summary']['traces']}`",
            f"- samples_out: `{payload['summary']['samples_out']}`",
            f"- truncated_traces: `{payload['summary']['truncated_traces']}`",
            "",
            "| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["traces"]:
        source_name = trace_label(item)
        lines.append(
            "| {source} | {samples} | {skipped} | {p50} | {p95} | {maxv} | {wp95} | {wmax} |".format(
                source=source_name,
                samples=item["samples_out"],
                skipped=item["skipped"],
                p50=fmt(item.get("action_delta_p50")),
                p95=fmt(item.get("action_delta_p95")),
                maxv=fmt(item.get("action_delta_max")),
                wp95=fmt(item.get("sample_weight_p95")),
                wmax=fmt(item.get("sample_weight_max")),
            )
        )
    if any(item.get("sample_weight_reasons") for item in payload["traces"]):
        lines.extend(["", "### Sample Weight Reasons", ""])
        for item in payload["traces"]:
            lines.append(f"- `{trace_label(item)}`: `{item.get('sample_weight_reasons')}`")
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Do not commit raw relabeled JSONL traces unless explicitly approved.",
            "- Use the output traces only for offline distillation experiments.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-manifest", required=True)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument(
        "--output-parent-depth",
        type=int,
        default=1,
        help=(
            "Number of source parent directories to preserve under output-trace-dir. "
            "Increase for nested traces with repeated seed/trace.jsonl leaf names."
        ),
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--teacher-model-kind", choices=["blend", "source_vx_blend"], default="blend")
    parser.add_argument("--include-source-regex", default=None)
    parser.add_argument("--exclude-source-regex", default=None)
    parser.add_argument("--alt-include-source-regex", default=None)
    parser.add_argument("--alt-exclude-source-regex", default=None)
    parser.add_argument("--knn-k", type=int, default=5)
    parser.add_argument("--blend-alpha", type=float, default=0.80)
    parser.add_argument("--vx-blend-alpha", type=float, default=1.0)
    parser.add_argument("--vx-blend-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--source-vx-threshold-m-s", type=float, default=0.02)
    parser.add_argument("--ridge-alphas", default="1e-6,1e-4,1e-2,1,100")
    parser.add_argument(
        "--gate-aware-sample-weights",
        action="store_true",
        help="Write per-row sample_weight values that emphasize low-progress gate-failure states.",
    )
    parser.add_argument("--gate-command-x", type=float, default=0.08)
    parser.add_argument("--gate-base-weight", type=float, default=1.0)
    parser.add_argument("--gate-min-track-ratio", type=float, default=0.5)
    parser.add_argument("--gate-low-progress-weight", type=float, default=3.0)
    parser.add_argument("--gate-double-support-weight", type=float, default=4.0)
    parser.add_argument("--gate-reverse-weight", type=float, default=5.0)
    parser.add_argument("--gate-lateral-weight", type=float, default=2.0)
    parser.add_argument("--gate-high-abs-vy-m-s", type=float, default=0.12)
    parser.add_argument("--gate-tracking-weight", type=float, default=2.0)
    parser.add_argument("--gate-high-tracking-rad", type=float, default=0.15)
    parser.add_argument("--gate-max-weight", type=float, default=8.0)
    parser.add_argument(
        "--truncate-before-done",
        action="store_true",
        help="Drop the first terminal done row and anything after it before relabeling.",
    )
    args = parser.parse_args()

    model, teacher_meta = load_teacher(args)
    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))
    output_dir = Path(args.output_trace_dir)
    trace_rows = [
        relabel_trace(
            path,
            output_dir,
            model,
            args,
            truncate_before_done=args.truncate_before_done,
        )
        for path in paths
    ]
    status = "PASS_BC_TRACE_RELABEL_READY" if trace_rows and all(row["samples_out"] for row in trace_rows) else "HOLD_BC_TRACE_RELABEL_EMPTY"
    payload = {
        "status": status,
        "teacher": teacher_meta,
        "trace_globs": args.trace_glob,
        "output_trace_dir": str(output_dir),
        "summary": {
            "traces": len(trace_rows),
            "samples_out": int(sum(row["samples_out"] for row in trace_rows)),
            "truncated_traces": int(
                sum(1 for row in trace_rows if row.get("first_done_index") is not None)
            ),
        },
        "traces": trace_rows,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"traces={len(trace_rows)}")
    print(f"samples_out={payload['summary']['samples_out']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
