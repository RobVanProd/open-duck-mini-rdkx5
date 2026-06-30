#!/usr/bin/env python3
"""Summarize the current Phase 2 domain-randomization campaign state.

This is an offline read-only reporter. It does not train, SSH, deploy, or touch
the robot. Its job is to turn the current candidate, gate, and backend artifacts
into a compact status document so the next training action is unambiguous.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "PHASE2_CURRENT_STATUS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "phase2_current_status.json"


DEFAULT_CANDIDATE_METADATA = (
    ROOT
    / "policy"
    / "candidates"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_20260629"
    / "candidate_metadata.json"
)
DEFAULT_GATES = {
    "z002_x008_nopush": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json",
    "z002_x000_nopush": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json",
    "z002_x008_gentle_push": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json",
    "z002_x000_gentle_push": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json",
    "z005_x008_nopush": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json",
    "z005_x000_nopush": ROOT
    / "outputs"
    / "analysis"
    / "phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_nopush_15s_8seed_cpu.json",
}
DEFAULT_BACKEND_ARTIFACTS = {
    "local_rocm_hold": ROOT
    / "outputs"
    / "analysis"
    / "phase2_z005_support_local_rocm_hold.json",
    "local_rocm_command_buffer": ROOT
    / "outputs"
    / "analysis"
    / "phase2_z005_local_rocm_command_buffer_result.json",
}
DEFAULT_Z005_SEED5_DIAGNOSTIC = (
    ROOT / "outputs" / "analysis" / "phase2_z005_seed5_failure_diagnostic.json"
)
DEFAULT_SCALAR_BRANCH_RESULTS = {
    "z005_support": ROOT
    / "outputs"
    / "analysis"
    / "PHASE2_Z005_SUPPORT_A100_CACHEFIX_RESULT.md",
    "right_swing_structural": ROOT
    / "docs"
    / "PHASE2_RIGHT_SWING_STRUCTURAL_RESULT.md",
    "right_swing_phase_lift": ROOT
    / "docs"
    / "PHASE2_RIGHT_SWING_PHASE_LIFT_RESULT.md",
    "right_swing_phase_advance": ROOT
    / "docs"
    / "PHASE2_RIGHT_SWING_PHASE_ADVANCE_RESULT.md",
    "right_swing_phase_single_support": ROOT
    / "docs"
    / "PHASE2_RIGHT_SWING_PHASE_SINGLE_SUPPORT_RESULT.md",
}


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def artifact_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "status": "MISSING"}
    return {
        "path": rel(path),
        "status": "PRESENT",
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def metric(aggregate: dict[str, Any], name: str, stat: str = "max") -> Any:
    value = aggregate.get(name)
    if isinstance(value, dict):
        return value.get(stat)
    return value


def summarize_gate(label: str, path: Path) -> dict[str, Any]:
    record = artifact_record(path)
    out: dict[str, Any] = {"label": label, **record}
    data = read_json(path)
    if data is None:
        out["status"] = "MISSING_GATE"
        return out

    results = data.get("results") or []
    statuses = [row.get("status") for row in results]
    pass_count = statuses.count("PASS_CANDIDATE_SIM_GATE")
    total = len(statuses)
    hold_count = total - pass_count
    aggregate_by_policy = data.get("aggregate") or {}
    first_policy = next(iter(aggregate_by_policy.values()), {})
    config = data.get("config") or {}
    out.update(
        {
            "status": "PASS_GATE_8SEED" if total == 8 and pass_count == 8 else "HOLD_GATE",
            "task": config.get("task"),
            "command_x": config.get("command_x"),
            "terrain_hfield_z_scale": config.get("terrain_hfield_z_scale"),
            "push_enabled": bool(config.get("eval_push_enable")),
            "seeds": config.get("seeds"),
            "pass_count": pass_count,
            "hold_count": hold_count,
            "total_count": total,
            "statuses": statuses,
            "mean_track_ratio": metric(first_policy, "track_ratio", "mean"),
            "mean_local_vx_m_s": metric(first_policy, "mean_local_vx_m_s", "mean"),
            "max_tracking_p95_rad": metric(first_policy, "max_tracking_p95_rad", "max"),
            "max_pitch_vel_p95_rad_s": metric(first_policy, "max_pitch_vel_p95_rad_s", "max"),
            "max_pitch_vel_limit_excess_rad_s": metric(
                first_policy, "max_pitch_vel_limit_excess_rad_s", "max"
            ),
            "fall_count": first_policy.get("fall_count"),
            "duration_complete_count": first_policy.get("duration_complete_count"),
            "push_success_rate_mean": metric(first_policy, "push_success_rate", "mean"),
        }
    )
    failed = [row for row in results if row.get("status") != "PASS_CANDIDATE_SIM_GATE"]
    if failed:
        out["first_failure"] = {
            "seed": failed[0].get("seed"),
            "status": failed[0].get("status"),
            "summary": failed[0].get("summary", {}),
        }
    return out


def summarize_candidate(path: Path) -> dict[str, Any]:
    record = artifact_record(path)
    data = read_json(path)
    if data is None:
        return {"status": "MISSING_CANDIDATE_METADATA", **record}
    candidate = data.get("candidate") or {}
    transform = data.get("candidate_transform") or {}
    contract = data.get("contract") or {}
    return {
        "status": "PRESENT",
        "metadata": record,
        "name": candidate.get("name"),
        "path": rel(candidate.get("path")),
        "sha256": candidate.get("sha256"),
        "contract_status": contract.get("status"),
        "input_dim": contract.get("input_dim"),
        "output_dim": contract.get("output_dim"),
        "transform_kind": transform.get("kind"),
        "transform_scale": transform.get("scale"),
        "transform_verify_status": transform.get("verify_status"),
        "transform_verify_max_abs_error": transform.get("verify_max_abs_error"),
    }


def summarize_backends(paths: dict[str, Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, path in paths.items():
        record = artifact_record(path)
        data = read_json(path)
        status = data.get("status") if data else record["status"]
        out[label] = {
            **record,
            "status": status,
            "robot_touched": bool((data or {}).get("robot_touched", False)),
            "ssh_used": bool((data or {}).get("ssh_used", False)),
            "deploy_performed": bool((data or {}).get("deploy_performed", False)),
            "summary": (data or {}).get("interpretation"),
        }
    return out


def summarize_z005_seed5_diagnostic(path: Path = DEFAULT_Z005_SEED5_DIAGNOSTIC) -> dict[str, Any]:
    record = artifact_record(path)
    data = read_json(path)
    if data is None:
        return {"status": "MISSING", **record}
    return {
        **record,
        "status": data.get("status"),
        "shared_findings": (data.get("findings") or {}).get("shared", []),
        "recommendation": data.get("recommendation"),
        "robot_touched": bool(data.get("robot_touched", False)),
        "ssh_used": bool(data.get("ssh_used", False)),
        "deploy_performed": bool(data.get("deploy_performed", False)),
        "training_started": bool(data.get("training_started", False)),
    }


def summarize_scalar_branch_results(paths: dict[str, Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, path in paths.items():
        record = artifact_record(path)
        status = "MISSING"
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("status:"):
                    status = line.split("`", 2)[1] if "`" in line else line.split(":", 1)[1].strip()
                    break
        out[name] = {
            **record,
            "status": status,
            "hold": status.startswith("HOLD"),
        }
    return out


def decide(payload: dict[str, Any]) -> tuple[str, str]:
    gates = payload["gates"]
    z002_required = [
        "z002_x008_nopush",
        "z002_x000_nopush",
        "z002_x008_gentle_push",
        "z002_x000_gentle_push",
    ]
    z002_pass = all(gates.get(name, {}).get("status") == "PASS_GATE_8SEED" for name in z002_required)
    z005_required = ["z005_x008_nopush", "z005_x000_nopush"]
    z005_pass = all(gates.get(name, {}).get("status") == "PASS_GATE_8SEED" for name in z005_required)
    scalar_results = payload.get("scalar_branch_results") or {}
    scalar_branches_exhausted = bool(scalar_results) and all(
        item.get("hold") for item in scalar_results.values()
    )
    if z005_pass:
        return (
            "PASS_PHASE2_TERRAIN_Z005_READY_FOR_NEXT_STAGE",
            "z=0.005 no-push command and stillness gates pass; run the z=0.005 gentle-push gates before widening randomization.",
        )
    if z002_pass:
        if scalar_branches_exhausted:
            return (
                "HOLD_PHASE2_SCALAR_SUPPORT_BRANCH_EXHAUSTED",
                "Current packaged candidate is robust at z=0.002 including gentle push, but z=0.005 terrain is not cleared. The scalar z=0.005/support/swing reward family has held repeatedly; do not launch another scalar support reward run. Next offline work should rebuild a corrected-bridge oracle/source or move to a structural phase-aware/live-oracle student path under the canonical corrected evaluator.",
            )
        return (
            "HOLD_PHASE2_TERRAIN_Z005_NOT_CLEARED",
            "Current packaged candidate is robust at z=0.002 including gentle push, but z=0.005 terrain is not cleared. Continue Phase 2 z=0.005 support training from the corrected-bridge candidate.",
        )
    return (
        "HOLD_PHASE2_BASE_GATES_INCOMPLETE",
        "One or more z=0.002 corrected-bridge gates are missing or failing; restore the Phase 1/Stage A2 base gate evidence before widening terrain.",
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines: list[str] = [
        "# Phase 2 Current Status",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "## Candidate",
        "",
    ]
    candidate = payload["candidate"]
    lines.extend(
        [
            f"- name: `{candidate.get('name')}`",
            f"- path: `{candidate.get('path')}`",
            f"- sha256: `{candidate.get('sha256')}`",
            f"- contract: `{candidate.get('contract_status')}` obs={candidate.get('input_dim')} action={candidate.get('output_dim')}",
            f"- transform: `{candidate.get('transform_kind')}` scale={candidate.get('transform_scale')} verify={candidate.get('transform_verify_status')}",
            "",
            "## Gate Matrix",
            "",
            "| gate | status | pass/total | x | z | push | track ratio mean | vx mean | max tracking p95 | max pitch vel p95 | max vel excess |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name, gate in payload["gates"].items():
        lines.append(
            "| {name} | `{status}` | {pass_count}/{total_count} | {x} | {z} | {push} | {track} | {vx} | {tracking} | {vel} | {excess} |".format(
                name=name,
                status=gate.get("status"),
                pass_count=gate.get("pass_count", 0),
                total_count=gate.get("total_count", 0),
                x=fmt(gate.get("command_x"), 3),
                z=fmt(gate.get("terrain_hfield_z_scale"), 3),
                push="yes" if gate.get("push_enabled") else "no",
                track=fmt(gate.get("mean_track_ratio"), 3),
                vx=fmt(gate.get("mean_local_vx_m_s"), 4),
                tracking=fmt(gate.get("max_tracking_p95_rad"), 4),
                vel=fmt(gate.get("max_pitch_vel_p95_rad_s"), 4),
                excess=fmt(gate.get("max_pitch_vel_limit_excess_rad_s"), 4),
            )
        )
    lines.extend(["", "## Blocking Gate Detail", ""])
    z005_failures = [
        (name, gate.get("first_failure"))
        for name, gate in payload["gates"].items()
        if name.startswith("z005_") and gate.get("first_failure")
    ]
    if z005_failures:
        for gate_name, failure in z005_failures:
            summary = failure.get("summary", {})
            lines.extend(
                [
                    f"- gate: `{gate_name}`",
                    f"  - first failing seed: `{failure.get('seed')}`",
                    f"  - status: `{failure.get('status')}`",
                    f"  - termination: `{summary.get('termination_reason')}`",
                    f"  - track_ratio: `{fmt(summary.get('track_ratio'), 4)}`",
                    f"  - mean_local_vx_m_s: `{fmt(summary.get('mean_local_vx_m_s'), 4)}`",
                    f"  - base_height_min_m: `{fmt(summary.get('base_height_min_m'), 4)}`",
                ]
            )
        lines.append("")
    else:
        lines.append("- No z005 failure detail available.")
        lines.append("")
    lines.extend(
        [
            "## Backend",
            "",
            "| artifact | status | robot | ssh | deploy | note |",
            "|---|---|---|---|---|---|",
        ]
    )
    for name, backend in payload["backends"].items():
        lines.append(
            f"| {name} | `{backend.get('status')}` | {backend.get('robot_touched')} | {backend.get('ssh_used')} | {backend.get('deploy_performed')} | {backend.get('summary') or ''} |"
        )
    diagnostic = payload.get("z005_seed5_diagnostic") or {}
    lines.extend(
        [
            "",
            "## z=0.005 Seed-5 Diagnostic",
            "",
            f"- status: `{diagnostic.get('status')}`",
            f"- artifact: `{diagnostic.get('path')}`",
            f"- robot_touched: `{diagnostic.get('robot_touched')}`",
            f"- ssh_used: `{diagnostic.get('ssh_used')}`",
            f"- deploy_performed: `{diagnostic.get('deploy_performed')}`",
            f"- training_started: `{diagnostic.get('training_started')}`",
            "",
        ]
    )
    findings = diagnostic.get("shared_findings") or []
    if findings:
        lines.extend(f"- {finding}" for finding in findings)
    else:
        lines.append("- no diagnostic findings available")
    lines.extend(["", f"recommendation: {diagnostic.get('recommendation') or 'NA'}"])
    branch_results = payload.get("scalar_branch_results") or {}
    if branch_results:
        lines.extend(
            [
                "",
                "## Scalar Support Branch Results",
                "",
                "| branch | status | artifact |",
                "|---|---|---|",
            ]
        )
        for name, item in branch_results.items():
            lines.append(
                f"| `{name}` | `{item.get('status')}` | `{item.get('path')}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- next_status: `{payload['status']}`",
            f"- next_action: {payload['next_action']}",
            "",
            "No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-metadata", default=str(DEFAULT_CANDIDATE_METADATA))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    candidate = summarize_candidate(Path(args.candidate_metadata))
    gates = {name: summarize_gate(name, path) for name, path in DEFAULT_GATES.items()}
    payload: dict[str, Any] = {
        "generated_at": now_utc(),
        "candidate": candidate,
        "gates": gates,
        "backends": summarize_backends(DEFAULT_BACKEND_ARTIFACTS),
        "z005_seed5_diagnostic": summarize_z005_seed5_diagnostic(),
        "scalar_branch_results": summarize_scalar_branch_results(
            DEFAULT_SCALAR_BRANCH_RESULTS
        ),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
    }
    status, next_action = decide(payload)
    payload["status"] = status
    payload["next_action"] = next_action

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(status)
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
