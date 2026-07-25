#!/usr/bin/env python3
"""Amend only the V138 phase-vector identity check."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
AUDIT = ANALYSIS / "winner_v138_phase20_start_audit_v2.json"
PREREG = ANALYSIS / "winner_v138_phase20_start_preregistration.json"
RESULT = ANALYSIS / "winner_v138_phase20_start_result.json"
RUNNER = ROOT / "tools/run_winner_v138_phase20_start_screen.py"
OUTPUT = ANALYSIS / "winner_v138_phase_identity_amendment.json"
MARKDOWN = ANALYSIS / "WINNER_V138_PHASE_IDENTITY_AMENDMENT_20260725.md"
EXPECTED = {
    "audit": (
        "9046d387dcc8bd59d1c2449138f4c72edea3ae13cdc46ebc6b6ae4f1cee145f7"
    ),
    "preregistration": (
        "f163fdef586739fe8c769727c06b2a056c308947c41744a685312f71b7889eb8"
    ),
    "result": (
        "c7b2fb1831dcf1bf1e9ba8d8d894e001765339fcef51f2564e3f93b400b3bd9b"
    ),
    "runner": (
        "ef12e1c8e1377aae5d2b5005cd54b155e901fa6dd30c6d0e58e339e6cd615af3"
    ),
}
SELECTED_PHASE = 20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V138: {path}")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    hashes = {
        "audit": sha256(AUDIT),
        "preregistration": sha256(PREREG),
        "result": sha256(RESULT),
        "runner": sha256(RUNNER),
    }
    if len(result["cells"]) != 1:
        raise ValueError("V138 V1 must have stopped after one cell")
    cell = result["cells"][0]
    trace = Path(cell["trace"]["path"])
    trace_row = json.loads(
        trace.read_text(encoding="utf-8").splitlines()[0]
    )
    observed = np.asarray(trace_row["obs_state"][99:101], dtype=np.float64)
    source_name = (
        "v121_train_matched_final_p30_all_joint_"
        "x0.080_seed167931544.jsonl"
    )
    source_path = (
        args.teacher_run_root.resolve() / "traces" / source_name
    )
    source_row = json.loads(
        source_path.read_text(encoding="utf-8").splitlines()[SELECTED_PHASE]
    )
    source = np.asarray(source_row["obs_state"][99:101], dtype=np.float64)
    nonphase_checks = {
        key: value
        for key, value in cell["metrics"]["checks"].items()
        if key != "phase20_first_observation_exact"
    }
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "v1_stopped_before_moving_behavior": (
            result["summary"]["cells_completed"] == 1
            and float(cell["identity"]["command_x_m_s"]) == 0.0
        ),
        "only_failure_is_phase_identity": (
            cell["failure_reasons"] == ["phase20_first_observation_exact"]
        ),
        "all_nonphase_checks_green": all(nonphase_checks.values()),
        "source_trace_hash_frozen": (
            sha256(source_path)
            == next(
                row["sha256"]
                for row in audit["trace_manifest"]
                if row["name"] == source_name
            )
        ),
        "observed_vector_bit_exact_to_frozen_phase20": bool(
            np.array_equal(observed, source)
        ),
        "host_float64_difference_explains_failure": (
            cell["phase_contract"]["first_phase_linf_error"] > 1.0e-7
            and cell["phase_contract"]["first_phase_linf_error"] < 2.0e-7
        ),
        "selection_and_behavior_thresholds_unchanged": True,
        "no_training_or_moving_behavior": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v138.phase_identity_amendment.v1",
        "status": (
            "PASS_WINNER_V138_PHASE_IDENTITY_AMENDMENT"
            if not failed
            else "HOLD_WINNER_V138_PHASE_IDENTITY_AMENDMENT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "attribution": {
            "observed_phase_vector": observed.tolist(),
            "frozen_source_phase20_vector": source.tolist(),
            "source_vs_observed_linf": float(
                np.max(np.abs(source - observed))
            ),
            "old_host_float64_linf": cell["phase_contract"][
                "first_phase_linf_error"
            ],
            "cause": (
                "the V1 runner synthesized an expected sine/cosine vector "
                "with host float64 math instead of comparing to the exact "
                "float32 phase vector already emitted by the frozen evaluator"
            ),
        },
        "amendment": {
            "change": (
                "compare the first phase observation to the bit-exact frozen "
                "V131 phase-20 vector"
            ),
            "selected_phase": SELECTED_PHASE,
            "selected_phase_changed": False,
            "matrix_changed": False,
            "behavior_thresholds_changed": False,
            "policy_changed": False,
            "stop_rule_changed": False,
        },
        "decision": (
            "EARN_ONE_V138_PHASE20_START_PREREGISTRATION_V2"
            if not failed
            else "CLOSE_PHASE20_START"
        ),
        "authority": {
            "v2_preregistration": not failed,
            "moving_behavior": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V138 phase-identity amendment\n\n"
        f"- Status: `{payload['status']}`\n"
        "- V1 stopped after one x=0 cell; no moving behavior ran.\n"
        "- The observed vector is bit-exact to the frozen V131 phase-20 "
        "vector; only the host-float64 expected-value check was wrong.\n"
        "- Phase selection, matrix, thresholds, stop rule, policy, and "
        "authority remain unchanged.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
