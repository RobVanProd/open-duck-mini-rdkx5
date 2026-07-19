#!/usr/bin/env python3
"""Review the runtime winner-v2 asset lock against current policy evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT.parent / "open-duck-mini-rdkx5-native-runtime"
DEFAULT_LOCK = (
    RUNTIME
    / "artifacts/gates/phase_5_policy/winner_v2_offline_asset_lock_20260719.json"
)
DEFAULT_JSON = ROOT / "outputs/analysis/winner_v2_offline_asset_lock_review.json"
DEFAULT_MD = ROOT / "outputs/analysis/WINNER_V2_OFFLINE_ASSET_LOCK_REVIEW_20260719.md"
PASS_TOKEN = "PASS_FROZEN_OFFLINE_ASSET_LOCK_POLICY_REVIEW"
HOLD_TOKEN = "HOLD_STALE_OFFLINE_ASSET_LOCK"
EXPECTED_AUTHORITY = {
    "cpu_only": True,
    "gate5": False,
    "rdkx5_access": False,
    "robot_clearance": False,
    "robot_or_motor_access": False,
    "runtime_deployment": False,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def file_checks(root: Path, records: dict[str, str], prefix: str) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for relative, expected in sorted(records.items()):
        path = root / relative
        checks[f"{prefix}:{relative}"] = path.is_file() and sha256_file(path) == expected
    return checks


def review(lock_path: Path) -> dict[str, Any]:
    lock_bytes = lock_path.read_bytes()
    lock = json.loads(lock_bytes)
    checks: dict[str, bool] = {
        "schema_exact": lock.get("schema_version")
        == "open_duck_x5.winner_v2_offline_asset_lock.v1",
        "status_is_offline_identity_pass": lock.get("status")
        == "PASS_FROZEN_OFFLINE_ASSET_IDENTITIES_BLOCKED_FOR_COM_X5_AND_GATE5",
        "frozen_flag_true": lock.get("frozen_offline_asset_identities") is True,
        "authority_exact_and_offline": lock.get("authority") == EXPECTED_AUTHORITY,
        "four_blockers_preserved": len(lock.get("blockers", [])) == 4,
    }

    runtime_assets = lock.get("runtime_assets", {})
    runtime_files = runtime_assets.get("files", {})
    if isinstance(runtime_files, dict):
        checks.update(file_checks(RUNTIME, runtime_files, "runtime"))
    else:
        checks["runtime_files_object"] = False

    runtime_commit = str(runtime_assets.get("identity_commit", ""))
    commit_exists = git(
        RUNTIME, "cat-file", "-e", f"{runtime_commit}^{{commit}}", check=False
    ).returncode == 0
    checks["runtime_identity_commit_exists"] = commit_exists
    checks["runtime_identity_commit_is_ancestor"] = commit_exists and git(
        RUNTIME, "merge-base", "--is-ancestor", runtime_commit, "HEAD", check=False
    ).returncode == 0

    policy_assets = lock.get("policy_assets", {})
    package_root = ROOT / str(policy_assets.get("package_root", ""))
    policy_files = policy_assets.get("files", {})
    if isinstance(policy_files, dict):
        checks.update(file_checks(package_root, policy_files, "policy_package"))
    else:
        checks["policy_files_object"] = False
    manifest_path = package_root / "manifest.json"
    checks["policy_manifest_exact"] = (
        manifest_path.is_file()
        and sha256_file(manifest_path)
        == policy_assets.get("corrected_handoff_manifest_sha256")
    )

    evidence = lock.get("evidence_assets", {})
    runtime_evidence = {
        name: record
        for name, record in evidence.items()
        if name.startswith("runtime_") and isinstance(record, dict)
    }
    for name, record in sorted(runtime_evidence.items()):
        path = RUNTIME / str(record.get("path", ""))
        checks[f"{name}_hash_exact"] = (
            path.is_file() and sha256_file(path) == record.get("sha256")
        )

    acceptance = evidence.get("policy_recursive_closure_result", {})
    acceptance_path = ROOT / str(acceptance.get("path", ""))
    acceptance_bytes = acceptance_path.read_bytes() if acceptance_path.is_file() else b""
    acceptance_commit = str(acceptance.get("commit", ""))
    checks["current_policy_acceptance_hash_exact"] = (
        bool(acceptance_bytes)
        and sha256_bytes(acceptance_bytes) == acceptance.get("sha256")
    )
    acceptance_commit_exists = git(
        ROOT, "cat-file", "-e", f"{acceptance_commit}^{{commit}}", check=False
    ).returncode == 0
    checks["policy_acceptance_commit_exists"] = acceptance_commit_exists
    checks["policy_acceptance_commit_is_ancestor"] = acceptance_commit_exists and git(
        ROOT, "merge-base", "--is-ancestor", acceptance_commit, "HEAD", check=False
    ).returncode == 0
    committed_acceptance = b""
    if acceptance_commit_exists and acceptance.get("path"):
        shown = git(
            ROOT,
            "show",
            f"{acceptance_commit}:{acceptance['path']}",
            check=False,
        )
        committed_acceptance = shown.stdout if shown.returncode == 0 else b""
    checks["committed_policy_acceptance_hash_exact"] = (
        bool(committed_acceptance)
        and sha256_bytes(committed_acceptance) == acceptance.get("sha256")
    )
    current_acceptance = json.loads(acceptance_bytes) if acceptance_bytes else {}
    checks["current_policy_decision_pass"] = (
        current_acceptance.get("decision")
        == "PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE"
    )
    checks["current_policy_authority_robot_false"] = (
        current_acceptance.get("authority", {}).get("robot_clearance") is False
    )

    reduced_record = evidence.get("runtime_reduced_recursive_result", {})
    reduced_path = RUNTIME / str(reduced_record.get("path", ""))
    reduced = json.loads(reduced_path.read_text(encoding="utf-8")) if reduced_path.is_file() else {}
    reduced_cells = reduced.get("cells", [])
    checks["reduced_four_cells"] = isinstance(reduced_cells, list) and len(reduced_cells) == 4
    checks["reduced_observation_values_exact_zero"] = bool(reduced_cells) and all(
        float(cell["semantic_max_abs_error"]["observation"]) == 0.0
        for cell in reduced_cells
    )
    checks["reduced_observation_gate_exact_zero"] = bool(reduced_cells) and all(
        cell.get("semantic_gates", {}).get(
            "teacher_forced_observation_exact_zero"
        )
        is True
        and "teacher_forced_observation_at_most_1e_6"
        not in cell.get("semantic_gates", {})
        for cell in reduced_cells
    )

    issues = sorted(name for name, passed in checks.items() if not passed)
    decision = PASS_TOKEN if not issues else HOLD_TOKEN
    return {
        "schema_version": "winner_v2.offline_asset_lock_policy_review.v1",
        "status": decision,
        "decision": decision,
        "asset_lock_path": str(lock_path.relative_to(RUNTIME)),
        "asset_lock_sha256": sha256_bytes(lock_bytes),
        "runtime_head": git(RUNTIME, "rev-parse", "HEAD").stdout.decode().strip(),
        "policy_head": git(ROOT, "rev-parse", "HEAD").stdout.decode().strip(),
        "checks": checks,
        "issues": issues,
        "current_policy_acceptance_sha256": (
            sha256_bytes(acceptance_bytes) if acceptance_bytes else None
        ),
        "locked_policy_acceptance_sha256": acceptance.get("sha256"),
        "locked_policy_acceptance_commit": acceptance.get("commit"),
        "authority": {
            "robot_clearance": False,
            "gate5": False,
            "runtime_deployment": False,
            "rdkx5_access": False,
            "robot_or_motor_access": False,
            "gpu_or_igpu": False,
        },
    }


def render_markdown(result: dict[str, Any]) -> str:
    issues = result["issues"]
    issue_lines = "\n".join(f"- `{issue}`" for issue in issues) or "- none"
    return f"""# Winner-v2 Offline Asset-Lock Policy Review — 2026-07-19

Decision: `{result['decision']}`

The runtime asset lock is checked against the current policy result, corrected
handoff package, runtime sources, formal evidence and frozen offline authority.
It is not accepted unless every identity matches and the reduced artifact uses
the preregistered exact-zero teacher-forced observation gate.

## Current issues

{issue_lines}

Locked policy result: `{result['locked_policy_acceptance_commit']}` /
`{result['locked_policy_acceptance_sha256']}`.

Current policy result SHA-256:
`{result['current_policy_acceptance_sha256']}`.

The present hold does not change the accepted recursive CPU outcome. It blocks
freezing a stale deployment asset set. No formal outcome rerun, threshold
change, robot, RDK-X5, motor, torque, deployment, GPU or iGPU action is
authorized by this review. Robot clearance remains `NO`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    result = review(args.asset_lock.resolve())
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.markdown.write_text(render_markdown(result), encoding="utf-8")
    print(result["decision"])
    for issue in result["issues"]:
        print(f"ISSUE={issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
