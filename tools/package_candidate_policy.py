#!/usr/bin/env python3
"""Create a candidate ONNX metadata packet.

This is an offline packaging gate. It does not train, deploy, SSH, or run robot
tests. The tool records whether a candidate has enough metadata and sim evidence
to be reviewed before suspended robot validation.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "policy/BEST_WALK_ONNX_2.onnx"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
EXPECTED_INPUT_DIM = 101
EXPECTED_OUTPUT_DIM = 14
REQUIRED_EVIDENCE = {
    "candidate_gate_x0",
    "candidate_gate_x008",
    "contract_audit",
    "training_manifest",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception:
        return None
    return result.stdout.strip()


def git_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "status": "MISSING"}
    return {
        "path": str(path),
        "commit": run_git(["rev-parse", "HEAD"], path),
        "branch": run_git(["branch", "--show-current"], path),
        "status_short": run_git(["status", "--short"], path),
    }


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def as_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(value).expanduser().resolve()


def load_json(path: Path | None) -> Any:
    if path is None or not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def shape_to_list(shape: Any) -> list[Any]:
    return [int(dim) if isinstance(dim, int) else str(dim) for dim in shape]


@contextmanager
def suppress_native_stderr():
    """Temporarily silence native-library writes to stderr."""

    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)
    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stderr_fd)
            yield
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(saved_fd)


def onnx_contract(path: Path) -> dict[str, Any]:
    try:
        import onnxruntime as ort  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "HOLD_ONNXRUNTIME_MISSING",
            "error": f"{type(exc).__name__}: {exc}",
        }

    try:
        with suppress_native_stderr():
            session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        inputs = [
            {
                "name": item.name,
                "shape": shape_to_list(item.shape),
                "dtype": item.type,
            }
            for item in session.get_inputs()
        ]
        outputs = [
            {
                "name": item.name,
                "shape": shape_to_list(item.shape),
                "dtype": item.type,
            }
            for item in session.get_outputs()
        ]
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "HOLD_ONNX_INSPECTION_FAILED",
            "error": f"{type(exc).__name__}: {exc}",
        }

    input_shape = inputs[0]["shape"] if inputs else []
    output_shape = outputs[0]["shape"] if outputs else []
    input_dim = input_shape[-1] if input_shape else None
    output_dim = output_shape[-1] if output_shape else None
    status = (
        "PASS_POLICY_CONTRACT"
        if input_dim == EXPECTED_INPUT_DIM and output_dim == EXPECTED_OUTPUT_DIM
        else "HOLD_POLICY_CONTRACT"
    )
    return {
        "status": status,
        "inputs": inputs,
        "outputs": outputs,
        "input_dim": input_dim,
        "output_dim": output_dim,
    }


def file_evidence(path: Path | None, label: str) -> dict[str, Any]:
    if path is None:
        return {"label": label, "status": "MISSING", "path": None}
    if not path.exists():
        return {"label": label, "status": "MISSING", "path": str(path)}
    return {
        "label": label,
        "status": "PRESENT",
        "path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def extract_gate_status(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "MISSING", "path": None}
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    if path.suffix.lower() == ".json":
        data = load_json(path)
        if isinstance(data, dict):
            closed_loop = data.get("closed_loop_sim") or data
            candidate_gate = closed_loop.get("candidate_gate") or {}
            return {
                "status": "PASS_PARSED_GATE_STATUS",
                "path": str(path),
                "overall_status": data.get("overall_status") or closed_loop.get("status"),
                "candidate_gate_status": candidate_gate.get("status"),
                "eval_role": data.get("eval_role") or closed_loop.get("eval_role"),
            }
    text = path.read_text(errors="replace")
    overall = None
    gate = None
    eval_role = None
    match = re.search(r"^overall_status:\s*`([^`]+)`", text, flags=re.MULTILINE)
    if match:
        overall = match.group(1)
    match = re.search(r"^eval_role:\s*`([^`]+)`", text, flags=re.MULTILINE)
    if match:
        eval_role = match.group(1)
    gate_section = text.split("### Candidate Gate", 1)
    if len(gate_section) == 2:
        match = re.search(r"^status:\s*`([^`]+)`", gate_section[1], flags=re.MULTILINE)
        if match:
            gate = match.group(1)
    return {
        "status": "PASS_PARSED_GATE_STATUS",
        "path": str(path),
        "overall_status": overall,
        "candidate_gate_status": gate,
        "eval_role": eval_role,
    }


def decide_status(payload: dict[str, Any], allow_missing_evidence: bool) -> str:
    if payload["candidate"]["sha256"] == payload["baseline"]["sha256"]:
        return "HOLD_BASELINE_OVERWRITE_RISK"
    if payload["contract"]["status"] != "PASS_POLICY_CONTRACT":
        return payload["contract"]["status"]
    missing = [
        key
        for key in payload["required_evidence"]
        if payload["evidence"].get(key, {}).get("status") != "PRESENT"
    ]
    if missing and not allow_missing_evidence:
        return "HOLD_MISSING_SIM_GATE_EVIDENCE"
    for gate_name in ["candidate_gate_x0", "candidate_gate_x008", "actuator_bridge_eval"]:
        gate = payload.get("sim_gate", {}).get(gate_name, {})
        for status in [gate.get("candidate_gate_status"), gate.get("overall_status")]:
            if isinstance(status, str) and status.startswith("HOLD"):
                return status
    if payload.get("non_deployable_reason"):
        return "INFO_NON_DEPLOYABLE_ARTIFACT"
    return "READY_FOR_SIM_GATE_REVIEW"


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Candidate Policy Package",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "## Candidate",
        "",
        f"- name: `{payload['candidate']['name']}`",
        f"- path: `{payload['candidate']['path']}`",
        f"- sha256: `{payload['candidate']['sha256']}`",
        f"- size_bytes: `{payload['candidate']['size_bytes']}`",
        "",
        "## Contract",
        "",
        f"- status: `{payload['contract']['status']}`",
        f"- expected input dim: `{EXPECTED_INPUT_DIM}`",
        f"- actual input dim: `{payload['contract'].get('input_dim')}`",
        f"- expected output dim: `{EXPECTED_OUTPUT_DIM}`",
        f"- actual output dim: `{payload['contract'].get('output_dim')}`",
        "",
        "| kind | name | shape | dtype |",
        "|---|---|---|---|",
    ]
    for item in payload["contract"].get("inputs", []):
        lines.append(
            f"| input | `{item['name']}` | `{item['shape']}` | `{item['dtype']}` |"
        )
    for item in payload["contract"].get("outputs", []):
        lines.append(
            f"| output | `{item['name']}` | `{item['shape']}` | `{item['dtype']}` |"
        )

    if payload.get("non_deployable_reason"):
        lines.extend(
            [
                "",
                "## Non-Deployable Notice",
                "",
                payload["non_deployable_reason"],
            ]
        )

    lines.extend(
        [
            "",
            "## Source Revisions",
            "",
            "| repo | branch | commit | dirty status |",
            "|---|---|---|---|",
        ]
    )
    for name, info in payload["sources"].items():
        dirty = "clean" if not info.get("status_short") else "dirty"
        lines.append(
            f"| `{name}` | `{info.get('branch')}` | `{info.get('commit')}` | `{dirty}` |"
        )

    lines.extend(
        [
            "",
            "## Evidence",
            "",
            "| evidence | required | status | path |",
            "|---|---|---|---|",
        ]
    )
    required = set(payload.get("required_evidence") or [])
    for key, item in payload["evidence"].items():
        lines.append(
            f"| `{item['label']}` | `{key in required}` | `{item['status']}` | `{item['path']}` |"
        )

    parsed_gates = [
        (key, gate)
        for key, gate in (payload.get("sim_gate") or {}).items()
        if isinstance(gate, dict) and gate.get("status") == "PASS_PARSED_GATE_STATUS"
    ]
    if parsed_gates:
        lines.extend(
            [
                "",
                "## Sim Gate Status",
                "",
                "| gate | eval_role | overall_status | candidate_gate_status |",
                "|---|---|---|---|",
            ]
        )
        for key, sim_gate in parsed_gates:
            lines.append(
                f"| `{key}` | `{sim_gate.get('eval_role')}` | "
                f"`{sim_gate.get('overall_status')}` | "
                f"`{sim_gate.get('candidate_gate_status')}` |"
            )

    training_manifest = payload.get("training_manifest")
    if training_manifest:
        lines.extend(["", "## Training Manifest", ""])
        if isinstance(training_manifest, dict):
            lines.append(f"- status: `{training_manifest.get('status')}`")
            lines.append(f"- platform: `{training_manifest.get('platform')}`")
            lines.append(
                f"- actuator_bridge_enabled: `{training_manifest.get('actuator_bridge_enabled')}`"
            )
            lines.append(
                f"- target_rate_scale: `{training_manifest.get('target_rate_scale')}`"
            )
            lines.append(
                f"- actuator_tracking_scale: `{training_manifest.get('actuator_tracking_scale')}`"
            )
            command = training_manifest.get("command_shell")
            if command:
                lines.extend(["", "```bash", command, "```"])
        else:
            lines.append("Training manifest could not be parsed as a JSON object.")

    lines.extend(
        [
            "",
            "## Robot Gate",
            "",
            "This package does not approve robot testing. Robot-side suspended",
            "validation still requires reviewed sim gates, Rob physically present,",
            "and explicit approval for the specific test.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create metadata for a candidate Open Duck ONNX policy."
    )
    parser.add_argument("onnx_path")
    parser.add_argument("--candidate-name")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--training-manifest")
    parser.add_argument("--contract-audit")
    parser.add_argument("--target-velocity-summary")
    parser.add_argument(
        "--actuator-bridge-eval",
        help=(
            "Legacy alias for the x=0.08 actuator bridge candidate gate. "
            "Use --candidate-gate-x0 and --candidate-gate-x008 for new packages."
        ),
    )
    parser.add_argument("--candidate-gate-x0")
    parser.add_argument("--candidate-gate-x008")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    parser.add_argument(
        "--allow-missing-evidence",
        action="store_true",
        help="Mark package reviewable even if optional sim-gate evidence is missing.",
    )
    parser.add_argument(
        "--non-deployable-reason",
        help="Record why this artifact must not be used on the robot.",
    )
    args = parser.parse_args()

    onnx_path = Path(args.onnx_path).expanduser().resolve()
    if not onnx_path.exists():
        print(f"Missing ONNX file: {onnx_path}", file=sys.stderr)
        return 2

    baseline_path = Path(args.baseline).expanduser().resolve()
    baseline_sha = sha256_file(baseline_path) if baseline_path.exists() else None
    manifest_path = as_path(args.training_manifest)
    legacy_actuator_bridge_eval_path = as_path(args.actuator_bridge_eval)
    candidate_gate_x0_path = as_path(args.candidate_gate_x0)
    candidate_gate_x008_path = as_path(args.candidate_gate_x008) or legacy_actuator_bridge_eval_path

    payload: dict[str, Any] = {
        "generated_at": timestamp(),
        "candidate": {
            "name": args.candidate_name or onnx_path.stem,
            "path": str(onnx_path),
            "sha256": sha256_file(onnx_path),
            "size_bytes": onnx_path.stat().st_size,
        },
        "baseline": {
            "path": str(baseline_path),
            "sha256": baseline_sha,
        },
        "contract": onnx_contract(onnx_path),
        "sources": {
            "rdk_repo": git_info(ROOT),
            "playground_repo": git_info(Path(args.playground_path).expanduser().resolve()),
        },
        "evidence": {
            "contract_audit": file_evidence(as_path(args.contract_audit), "contract_audit"),
            "target_velocity_summary": file_evidence(
                as_path(args.target_velocity_summary), "target_velocity_summary"
            ),
            "candidate_gate_x0": file_evidence(
                candidate_gate_x0_path, "candidate_gate_x0"
            ),
            "candidate_gate_x008": file_evidence(
                candidate_gate_x008_path, "candidate_gate_x008"
            ),
            "actuator_bridge_eval": file_evidence(
                legacy_actuator_bridge_eval_path, "actuator_bridge_eval_legacy"
            ),
            "training_manifest": file_evidence(manifest_path, "training_manifest"),
        },
        "sim_gate": {
            "candidate_gate_x0": extract_gate_status(candidate_gate_x0_path),
            "candidate_gate_x008": extract_gate_status(candidate_gate_x008_path),
            "actuator_bridge_eval": extract_gate_status(legacy_actuator_bridge_eval_path),
        },
        "required_evidence": sorted(REQUIRED_EVIDENCE),
        "training_manifest": load_json(manifest_path),
        "non_deployable_reason": args.non_deployable_reason,
    }
    payload["status"] = decide_status(payload, args.allow_missing_evidence)

    text = markdown(payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(text)
    else:
        print(text)

    hold = payload["status"].startswith("HOLD")
    return 1 if hold else 0


if __name__ == "__main__":
    raise SystemExit(main())
