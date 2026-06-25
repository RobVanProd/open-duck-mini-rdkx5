#!/usr/bin/env python3
"""Import a small CUDA/Colab artifact bundle for review.

The generated CUDA cell writes one tarball containing analysis summaries,
candidate gate reports, candidate metadata, and exported ONNX files. This tool
extracts that bundle into the repo evidence area and writes a compact manifest
so review can start from one markdown file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "outputs/analysis/cuda_imports"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sha256_sidecar(path: Path) -> str:
    text = path.read_text(errors="replace").strip()
    if not text:
        raise ValueError(f"empty SHA256 sidecar: {path}")
    token = text.split()[0].lower()
    if len(token) != 64 or any(char not in "0123456789abcdef" for char in token):
        raise ValueError(f"invalid SHA256 sidecar content in {path}: {token!r}")
    return token


def default_sha256_sidecar(bundle: Path) -> Path:
    return bundle.with_name(bundle.name + ".sha256")


def safe_member_path(member_name: str) -> Path:
    candidate = Path(member_name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe tar member path: {member_name}")
    return candidate


def extract_bundle(bundle: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "r:*") as tar:
        for member in tar.getmembers():
            safe_member_path(member.name)
        tar.extractall(output_dir)


def copy_directory(src: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / src.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def first_status_from_md(path: Path) -> str | None:
    try:
        for line in path.read_text(errors="replace").splitlines():
            stripped = line.strip()
            if "overall_status:" in stripped:
                return stripped.split("overall_status:", 1)[1].strip().strip("`")
            if "assessment_status:" in stripped:
                return stripped.split("assessment_status:", 1)[1].strip().strip("`")
            if stripped.startswith("status:"):
                return stripped.split("status:", 1)[1].strip().strip("`")
            if "candidate_gate_status:" in stripped:
                return stripped.split("candidate_gate_status:", 1)[1].strip().strip("`")
    except Exception:
        return None
    return None


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def collect_files(output_dir: Path) -> dict[str, list[Path]]:
    return {
        "markdown": sorted(output_dir.rglob("*.md")),
        "json": sorted(output_dir.rglob("*.json")),
        "onnx": sorted(output_dir.rglob("*.onnx")),
        "exit_status": sorted(output_dir.rglob("CUDA_CELL_EXIT_STATUS.txt")),
        "environment": sorted(
            list(output_dir.rglob("pip_freeze.txt"))
            + list(output_dir.rglob("nvidia_smi.txt"))
        ),
        "stdout_stderr": sorted(
            list(output_dir.rglob("stdout.txt")) + list(output_dir.rglob("stderr.txt"))
        ),
    }


def parse_exit_status(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    values: dict[str, Any] = {"path": relative(path)}
    for line in path.read_text(errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    raw_exit = values.get("exit_status")
    try:
        values["exit_status"] = int(raw_exit)
    except (TypeError, ValueError):
        values["exit_status"] = raw_exit
    return values


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def status_fields_from_json(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    fields: dict[str, Any] = {}
    for key in [
        "overall_status",
        "assessment_status",
        "status",
        "candidate_gate_status",
    ]:
        if key in payload:
            fields[key] = payload[key]

    closed_loop = payload.get("closed_loop_sim")
    if isinstance(closed_loop, dict):
        if "status" in closed_loop:
            fields.setdefault("closed_loop_status", closed_loop["status"])
        candidate_gate = closed_loop.get("candidate_gate")
        if isinstance(candidate_gate, dict) and "status" in candidate_gate:
            fields.setdefault("candidate_gate_status", candidate_gate["status"])

    sim_gate = payload.get("sim_gate")
    if isinstance(sim_gate, dict):
        actuator_eval = sim_gate.get("actuator_bridge_eval")
        if isinstance(actuator_eval, dict):
            if "candidate_gate_status" in actuator_eval:
                fields.setdefault(
                    "candidate_gate_status",
                    actuator_eval["candidate_gate_status"],
                )
            if "overall_status" in actuator_eval:
                fields.setdefault("overall_status", actuator_eval["overall_status"])

    candidate = payload.get("candidate")
    if isinstance(candidate, dict):
        fields["candidate_name"] = candidate.get("name")
        fields["candidate_sha256"] = candidate.get("sha256")

    recipe = payload.get("recipe")
    phases = payload.get("phases")
    if isinstance(recipe, str) and isinstance(phases, list):
        fields["recipe"] = recipe
        fields["phase_count"] = len(phases)
        phase_gate_statuses = []
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            gate = phase.get("phase_freeze_gate")
            if not isinstance(gate, dict):
                continue
            phase_gate_statuses.append(
                {
                    "phase": phase.get("name"),
                    "status": gate.get("status"),
                    "bridge_mode": gate.get("bridge_mode"),
                    "result_json": gate.get("result_json"),
                    "result_md": gate.get("result_md"),
                    "fall_fraction": gate.get("fall_fraction"),
                    "track_ratio_mean": gate.get("track_ratio_mean"),
                    "mean_local_vx_m_s": gate.get("mean_local_vx_m_s"),
                }
            )
        if phase_gate_statuses:
            fields["phase_gate_statuses"] = phase_gate_statuses
        if payload.get("final_candidate_onnx"):
            fields["final_candidate_onnx"] = payload.get("final_candidate_onnx")
    return fields


def primary_status(item: dict[str, Any]) -> str:
    return str(
        item.get("overall_status")
        or item.get("assessment_status")
        or item.get("candidate_gate_status")
        or item.get("status")
        or item.get("closed_loop_status")
        or "UNKNOWN"
    )


def gate_status_by_suffix(markdown_statuses: list[dict[str, Any]], suffix: str) -> str | None:
    matches = [
        item.get("status")
        for item in markdown_statuses
        if suffix in str(item.get("path", ""))
    ]
    for status in matches:
        if isinstance(status, str) and status != "UNKNOWN":
            return status
    return None


def staged_plan_summaries(json_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in json_summaries
        if isinstance(item.get("recipe"), str)
        and str(item.get("recipe", "")).startswith("movement_bootstrap")
    ]


def determine_staged_review_status(
    staged_plans: list[dict[str, Any]],
    onnx_summaries: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not staged_plans:
        return None

    # Prefer the deepest staged run evidence over static/dry-run local plans.
    plan = max(
        staged_plans,
        key=lambda item: (
            bool(item.get("phase_gate_statuses")),
            bool(item.get("final_candidate_onnx")),
            int(item.get("phase_count") or 0),
            int(item.get("size_bytes") or 0),
        ),
    )
    plan_status = str(plan.get("status") or "UNKNOWN")
    gates = plan.get("phase_gate_statuses") or []

    for gate in gates:
        status = str(gate.get("status") or "UNKNOWN")
        if status.startswith("HOLD"):
            return {
                "status": status,
                "reason": (
                    "staged curriculum phase gate held; inspect the phase gate "
                    "summary before considering any follow-on training"
                ),
                "staged_recipe": plan.get("recipe"),
                "staged_plan": plan.get("path"),
                "staged_phase_gate": gate,
            }

    if plan_status.startswith("HOLD"):
        return {
            "status": plan_status,
            "reason": "staged curriculum planner reported a hold",
            "staged_recipe": plan.get("recipe"),
            "staged_plan": plan.get("path"),
            "staged_phase_gates": gates,
        }

    if plan_status == "PASS_STAGED_CURRICULUM_RUN":
        if not gates:
            return {
                "status": "INFO_STAGED_RUN_NO_PHASE_GATE",
                "reason": (
                    "staged curriculum ran, but no phase-gate result was found "
                    "in the staged plan"
                ),
                "staged_recipe": plan.get("recipe"),
                "staged_plan": plan.get("path"),
            }
        if not onnx_summaries:
            return {
                "status": "HOLD_STAGED_NO_ONNX",
                "reason": "staged curriculum passed gates but no ONNX was found in the bundle",
                "staged_recipe": plan.get("recipe"),
                "staged_plan": plan.get("path"),
                "staged_phase_gates": gates,
            }
        return {
            "status": "READY_FOR_STAGED_GATE_REVIEW",
            "reason": (
                "staged curriculum completed and recorded passing phase gates; "
                "review the staged artifacts before any next training phase"
            ),
            "staged_recipe": plan.get("recipe"),
            "staged_plan": plan.get("path"),
            "staged_phase_gates": gates,
        }

    return {
        "status": "INFO_STAGED_PLAN_ONLY",
        "reason": "staged curriculum plan evidence found, but no run verdict is available",
        "staged_recipe": plan.get("recipe"),
        "staged_plan": plan.get("path"),
        "staged_status": plan_status,
    }


def determine_review_status(
    markdown_statuses: list[dict[str, Any]],
    json_summaries: list[dict[str, Any]],
    onnx_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    package_jsons = [
        item
        for item in json_summaries
        if item.get("candidate_name") and item.get("status")
    ]
    package_statuses = [str(item.get("status")) for item in package_jsons]

    x0_status = gate_status_by_suffix(markdown_statuses, "_candidate_gate_x0")
    x008_status = gate_status_by_suffix(markdown_statuses, "_candidate_gate_x008")

    if isinstance(x0_status, str) and x0_status.startswith("HOLD"):
        return {
            "status": x0_status,
            "reason": "candidate x=0.0 sim gate is holding",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }
    if isinstance(x008_status, str) and x008_status.startswith("HOLD"):
        return {
            "status": x008_status,
            "reason": "candidate x=0.08 sim gate is holding",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }

    for status in package_statuses:
        if status.startswith("HOLD"):
            return {
                "status": status,
                "reason": "candidate package reported a hold",
                "candidate_gate_x0": x0_status,
                "candidate_gate_x008": x008_status,
            }

    if package_jsons and not onnx_summaries:
        return {
            "status": "HOLD_NO_CANDIDATE_ONNX",
            "reason": "candidate package exists but no ONNX file was found in the bundle",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }

    if package_jsons:
        if x0_status != "PASS_CANDIDATE_SIM_GATE":
            return {
                "status": x0_status or "HOLD_MISSING_CANDIDATE_GATE_X0",
                "reason": "candidate x=0.0 sim gate is missing or not passing",
                "candidate_gate_x0": x0_status,
                "candidate_gate_x008": x008_status,
            }
        if x008_status != "PASS_CANDIDATE_SIM_GATE":
            return {
                "status": x008_status or "HOLD_MISSING_CANDIDATE_GATE_X008",
                "reason": "candidate x=0.08 sim gate is missing or not passing",
                "candidate_gate_x0": x0_status,
                "candidate_gate_x008": x008_status,
            }
        return {
            "status": "READY_FOR_SIM_GATE_REVIEW",
            "reason": "candidate package and both candidate gates are present and passing",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }

    if any(item.get("status") == "PASS_SMOKE_RUN" for item in json_summaries):
        return {
            "status": "INFO_SMOKE_ONLY",
            "reason": "bundle contains smoke evidence but no candidate package",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }

    if any(item.get("status") == "PASS_CLOSED_LOOP_REPRODUCTION" for item in json_summaries):
        return {
            "status": "INFO_BASELINE_EVAL_ONLY",
            "reason": "bundle contains baseline eval evidence but no candidate package",
            "candidate_gate_x0": x0_status,
            "candidate_gate_x008": x008_status,
        }

    staged_review = determine_staged_review_status(
        staged_plan_summaries(json_summaries),
        onnx_summaries,
    )
    if staged_review:
        staged_review.setdefault("candidate_gate_x0", x0_status)
        staged_review.setdefault("candidate_gate_x008", x008_status)
        return staged_review

    return {
        "status": "HOLD_NO_CANDIDATE_PACKAGE",
        "reason": "no candidate package metadata was found in the bundle",
        "candidate_gate_x0": x0_status,
        "candidate_gate_x008": x008_status,
    }


def build_summary(
    bundle: Path | None,
    source_dir: Path | None,
    output_dir: Path,
    expected_sha256: str | None = None,
    expected_sha256_source: str | None = None,
) -> tuple[str, dict[str, Any]]:
    files = collect_files(output_dir)
    markdown_statuses = []
    for path in files["markdown"]:
        status = first_status_from_md(path)
        markdown_statuses.append(
            {
                "path": relative(path),
                "status": status or "UNKNOWN",
                "size_bytes": path.stat().st_size,
            }
        )

    json_summaries = []
    for path in files["json"]:
        payload = read_json(path)
        item: dict[str, Any] = {
            "path": relative(path),
            "size_bytes": path.stat().st_size,
        }
        item.update(status_fields_from_json(payload))
        json_summaries.append(item)

    onnx_summaries = [
        {
            "path": relative(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in files["onnx"]
    ]

    review = determine_review_status(markdown_statuses, json_summaries, onnx_summaries)
    exit_status = parse_exit_status(files["exit_status"][0] if files["exit_status"] else None)
    if (
        exit_status is not None
        and exit_status.get("exit_status") not in (0, "0", None)
    ):
        review = {
            "status": "HOLD_CUDA_CELL_FAILED",
            "reason": (
                "CUDA cell exited nonzero; inspect partial artifacts and logs before "
                "treating any candidate result as usable"
            ),
            "previous_review": review,
            "candidate_gate_x0": review.get("candidate_gate_x0"),
            "candidate_gate_x008": review.get("candidate_gate_x008"),
        }

    payload = {
        "schema_version": "cuda_artifact_import.v1",
        "timestamp": timestamp(),
        "bundle": None
        if bundle is None
        else {
            "path": str(bundle),
            "size_bytes": bundle.stat().st_size,
            "sha256": sha256_file(bundle),
        },
        "source_dir": None if source_dir is None else str(source_dir),
        "expected_bundle_sha256": expected_sha256,
        "expected_bundle_sha256_source": expected_sha256_source,
        "output_dir": str(output_dir),
        "markdown_statuses": markdown_statuses,
        "json_summaries": json_summaries,
        "onnx_files": onnx_summaries,
        "cuda_cell_exit_status": exit_status,
        "environment_files": [relative(path) for path in files["environment"]],
        "stdout_stderr_files": [relative(path) for path in files["stdout_stderr"]],
        "staged_plans": staged_plan_summaries(json_summaries),
        "review": review,
    }

    lines = [
        "# CUDA Artifact Import Summary",
        "",
        f"- timestamp: `{payload['timestamp']}`",
        f"- output_dir: `{relative(output_dir)}`",
    ]
    if payload["bundle"]:
        lines.extend(
            [
                f"- bundle: `{payload['bundle']['path']}`",
                f"- bundle_sha256: `{payload['bundle']['sha256']}`",
            ]
        )
        if expected_sha256:
            lines.append(f"- expected_bundle_sha256: `{expected_sha256}`")
            if expected_sha256_source:
                lines.append(f"- expected_bundle_sha256_source: `{expected_sha256_source}`")
    if source_dir:
        lines.append(f"- source_dir: `{source_dir}`")
    if exit_status:
        lines.append(f"- cuda_cell_exit_status: `{exit_status.get('exit_status')}`")

    lines.extend(
        [
            "",
            "## Review Gate",
            "",
            f"- status: `{review['status']}`",
            f"- reason: {review['reason']}",
            f"- candidate_gate_x0: `{review.get('candidate_gate_x0')}`",
            f"- candidate_gate_x008: `{review.get('candidate_gate_x008')}`",
        ]
    )
    if review.get("staged_recipe") or review.get("staged_plan"):
        lines.extend(
            [
                f"- staged_recipe: `{review.get('staged_recipe')}`",
                f"- staged_plan: `{review.get('staged_plan')}`",
            ]
        )
    if review.get("staged_phase_gate"):
        gate = review["staged_phase_gate"]
        lines.extend(
            [
                f"- staged_phase: `{gate.get('phase')}`",
                f"- staged_phase_gate_status: `{gate.get('status')}`",
                f"- staged_phase_gate_bridge: `{gate.get('bridge_mode')}`",
            ]
        )

    if exit_status:
        lines.extend(["", "## CUDA Cell Metadata", ""])
        lines.append("| key | value |")
        lines.append("|---|---|")
        for key in sorted(exit_status):
            lines.append(f"| `{markdown_cell(key)}` | `{markdown_cell(exit_status[key])}` |")

    lines.extend(["", "## Environment Files", ""])
    if files["environment"]:
        for path in files["environment"]:
            lines.append(f"- `{relative(path)}`")
    else:
        lines.append("No environment snapshot files found.")

    lines.extend(["", "## Markdown Statuses", ""])
    if markdown_statuses:
        lines.append("| file | status |")
        lines.append("|---|---|")
        for item in markdown_statuses:
            lines.append(f"| `{item['path']}` | `{item['status']}` |")
    else:
        lines.append("No markdown files found.")

    lines.extend(["", "## JSON Statuses", ""])
    if json_summaries:
        lines.append("| file | status | candidate |")
        lines.append("|---|---|---|")
        for item in json_summaries:
            status = primary_status(item)
            candidate = item.get("candidate_name") or ""
            lines.append(f"| `{item['path']}` | `{status}` | `{candidate}` |")
    else:
        lines.append("No JSON files found.")

    lines.extend(["", "## Staged Plans", ""])
    staged_plans = staged_plan_summaries(json_summaries)
    if staged_plans:
        lines.append("| file | recipe | status | phase gates |")
        lines.append("|---|---|---|---|")
        for item in staged_plans:
            gates = item.get("phase_gate_statuses") or []
            gate_text = ", ".join(
                f"{gate.get('phase')}={gate.get('status')}" for gate in gates
            )
            lines.append(
                f"| `{item['path']}` | `{item.get('recipe')}` | "
                f"`{item.get('status')}` | `{markdown_cell(gate_text)}` |"
            )
    else:
        lines.append("No staged curriculum plan JSON found.")

    lines.extend(["", "## ONNX Files", ""])
    if onnx_summaries:
        lines.append("| file | size_bytes | sha256 |")
        lines.append("|---|---:|---|")
        for item in onnx_summaries:
            lines.append(
                f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` |"
            )
    else:
        lines.append("No ONNX files found.")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "This import does not approve robot testing. Review candidate sim gates",
            "and package metadata before any suspended validation is discussed.",
            "",
        ]
    )
    return "\n".join(lines), payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import a CUDA/Colab artifact bundle and summarize it."
    )
    parser.add_argument("source", help="artifact .tar.gz/.tgz file or extracted directory")
    parser.add_argument(
        "--expected-sha256",
        help=(
            "Expected SHA256 for a .tar/.tar.gz/.tgz bundle, copied from the "
            "CUDA_ARTIFACT_BUNDLE_SHA256 line printed by the generated cell."
        ),
    )
    parser.add_argument(
        "--expected-sha256-file",
        help=(
            "Path to a sidecar file containing the expected bundle SHA256. "
            "If omitted, the importer automatically uses <bundle>.sha256 when present."
        ),
    )
    parser.add_argument("--output-dir", help="destination directory")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"source not found: {source}")

    suffix = "".join(source.suffixes)
    stem = source.name
    for ext in [".tar.gz", ".tgz", ".tar"]:
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else DEFAULT_OUTPUT_ROOT / f"{timestamp()}_{stem}"
    )

    bundle: Path | None = None
    source_dir: Path | None = None
    expected_sha256: str | None = None
    expected_sha256_source: str | None = None
    if source.is_dir():
        if args.expected_sha256 or args.expected_sha256_file:
            raise SystemExit(
                "--expected-sha256 and --expected-sha256-file can only be used "
                "with a tar bundle"
            )
        source_dir = source
        copy_directory(source, output_dir)
    elif suffix.endswith(".tar.gz") or suffix.endswith(".tgz") or source.suffix == ".tar":
        bundle = source
        if args.expected_sha256:
            expected_sha256 = args.expected_sha256.lower().strip()
            expected_sha256_source = "cli"
        elif args.expected_sha256_file:
            sidecar = Path(args.expected_sha256_file).expanduser().resolve()
            if not sidecar.exists():
                raise SystemExit(f"expected SHA256 sidecar not found: {sidecar}")
            try:
                expected_sha256 = read_sha256_sidecar(sidecar)
            except ValueError as exc:
                raise SystemExit(str(exc)) from exc
            expected_sha256_source = str(sidecar)
        else:
            sidecar = default_sha256_sidecar(source)
            if sidecar.exists():
                try:
                    expected_sha256 = read_sha256_sidecar(sidecar)
                except ValueError as exc:
                    raise SystemExit(str(exc)) from exc
                expected_sha256_source = str(sidecar)
        if expected_sha256:
            actual_sha256 = sha256_file(source)
            if actual_sha256.lower() != expected_sha256:
                raise SystemExit(
                    "bundle SHA256 mismatch:\n"
                    f"  expected: {expected_sha256}\n"
                    f"  actual:   {actual_sha256}\n"
                    f"  source:   {expected_sha256_source or 'UNKNOWN'}\n"
                    "Do not review or use this CUDA artifact bundle."
                )
        extract_bundle(source, output_dir)
    else:
        raise SystemExit("source must be a .tar/.tar.gz/.tgz bundle or directory")

    summary_md, payload = build_summary(
        bundle,
        source_dir,
        output_dir,
        expected_sha256,
        expected_sha256_source,
    )
    (output_dir / "CUDA_ARTIFACT_IMPORT_SUMMARY.md").write_text(summary_md + "\n")
    (output_dir / "cuda_artifact_import_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(output_dir / "CUDA_ARTIFACT_IMPORT_SUMMARY.md")
    print(output_dir / "cuda_artifact_import_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
