#!/usr/bin/env python3
"""Freeze T2 inputs or issue an evidence-backed missing-input hold."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
FIT = ANALYSIS / "actuator_response_fit_corrected_knee.json"
OUTPUT = ANALYSIS / "t2_dc_lag_preregistration.json"
MARKDOWN = ANALYSIS / "T2_DC_LAG_PREREGISTRATION_20260725.md"
TRACE_RELATIVE = Path(
    "outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/"
    "suspended_policy_replay_x008_corrected_knee.jsonl"
)
TRACE_NAME = TRACE_RELATIVE.name
EXPECTED_FIT_SHA256 = (
    "40d2aefbdaeac986fc856aade8170f2a9d72831613a7a30873bfff0846e4f1bb"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path(r"D:\open-duck-archive-20260725"),
    )
    args = parser.parse_args()
    archive_root = args.archive_root.resolve()
    repo_trace = ROOT / TRACE_RELATIVE
    loose_matches = sorted(
        str(path)
        for path in archive_root.rglob(TRACE_NAME)
        if path.is_file()
    )
    tarballs = sorted(
        path
        for path in (archive_root / "tarball-snapshots").rglob("*")
        if path.is_file() and ".tar" in path.name
    )
    tar_inventory = []
    tar_matches = []
    for path in tarballs:
        with tarfile.open(path, "r:*") as archive:
            names = archive.getnames()
        matches = sorted(
            name for name in names if name.endswith(TRACE_NAME)
        )
        tar_inventory.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "member_count": len(names),
                "matches": matches,
            }
        )
        tar_matches.extend(f"{path}:{name}" for name in matches)
    git_history = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--format=%H",
            "--",
            TRACE_RELATIVE.as_posix(),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    fit_sha = sha256(FIT)
    fit = json.loads(FIT.read_text(encoding="utf-8"))
    joint_lags = {
        name: values["cross_correlation_lag"]["lag_ticks"]
        for name, values in fit["primary"]["joints"].items()
    }
    raw_available = bool(
        repo_trace.is_file() or loose_matches or tar_matches or git_history
    )
    status = (
        "PREREGISTERED_T2_DC_LAG_DECOMPOSITION"
        if raw_available and fit_sha == EXPECTED_FIT_SHA256
        else "HOLD_T2_REQUIRED_RAW_TELEMETRY_MISSING"
    )
    payload = {
        "schema_version": "open_duck.t2_dc_lag_preregistration.v1",
        "status": status,
        "trace": {
            "required_relative_path": TRACE_RELATIVE.as_posix(),
            "required_samples": 747,
            "startup_ticks_excluded": 50,
            "required_post_startup_samples": 696,
            "repo_path": str(repo_trace),
            "repo_path_exists": repo_trace.is_file(),
            "loose_archive_matches": loose_matches,
            "tarball_matches": tar_matches,
            "git_history_commits": git_history,
            "raw_available": raw_available,
        },
        "tarball_inventory": tar_inventory,
        "fit": {
            "path": str(FIT),
            "sha256": fit_sha,
            "expected_sha256": EXPECTED_FIT_SHA256,
            "hash_exact": fit_sha == EXPECTED_FIT_SHA256,
            "cross_correlation_lag_ticks": joint_lags,
        },
        "frozen_method": {
            "error": "sent_target(t)-actual(t)",
            "dc_term": "mean(error) over the 696 post-startup samples",
            "dc_energy_fraction": (
                "mean(error)^2 / mean(error^2); a constant has zero temporal "
                "variance, so energy—not var(constant)—is the defined measure"
            ),
            "lag_residual": (
                "sent_target shifted by the exact per-joint recorded "
                "cross-correlation lag minus actual over their common window"
            ),
            "lag_residual_energy_fraction": (
                "mean(lag_residual^2) / mean(error^2), with common-window "
                "unshifted error used as denominator"
            ),
            "pitch_chain_joints": [
                "left_hip_pitch",
                "left_knee",
                "left_ankle",
                "right_hip_pitch",
                "right_knee",
                "right_ankle",
            ],
            "home_offset_comparison": (
                "compare signed DC terms with the frozen physical-start-pose "
                "calibration offsets before attributing them to dynamics"
            ),
        },
        "decision_rule": {
            "posture_offset_dominant": (
                "DC energy fraction >=0.50 on at least 4 of 6 pitch joints"
            ),
            "bridge_lag_dominant": (
                "lag-explained fraction >=0.70 on at least 4 of 6 pitch "
                "joints, where lag-explained=1-lag_residual_energy_fraction"
            ),
            "missing_raw_trace": (
                "no decomposition result; do not infer DC from aggregate "
                "p50/p95/max or refit summaries"
            ),
        },
        "execution": {
            "authorized": raw_available,
            "performed": False,
            "result": None,
            "selection_weight": 0,
        },
        "authority": {
            "offline_read_only": True,
            "robot_or_rdk_access": False,
            "training_steps": 0,
            "hosted_compute": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T2 DC-offset versus lag preregistration\n\n"
        f"- Status: `{status}`\n"
        f"- Corrected-knee fit SHA-256: `{fit_sha}`\n"
        f"- Required raw trace present: `{raw_available}`\n"
        f"- Loose archive matches: `{len(loose_matches)}`\n"
        f"- Tarball member matches across `{len(tar_inventory)}` archives: "
        f"`{len(tar_matches)}`\n"
        f"- Git-history matches: `{len(git_history)}`\n"
        "- Aggregate fit summaries cannot recover the signed DC term, so no "
        "T2 causal decision is authorized without the 747-tick series.\n",
        encoding="utf-8",
    )
    print(status)
    print(f"raw_available={raw_available}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if raw_available else 2


if __name__ == "__main__":
    raise SystemExit(main())
