#!/usr/bin/env python3
"""Invoke the frozen T177 runner one condition at a time until terminal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_t177_head_prefix_mean_full_r2.py"
RESULT = ROOT / "outputs" / "analysis" / (
    "t177_head_prefix_mean_full_r2_result.json"
)
PROGRESS = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t177_head_prefix_mean_full_r2_v1/progress.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    invocation = 0
    while not RESULT.exists():
        invocation += 1
        print(
            json.dumps(
                {
                    "event": "start_condition_invocation",
                    "invocation": invocation,
                }
            ),
            flush=True,
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--execute",
                "--maximum-new-conditions",
                "1",
            ],
            cwd=ROOT,
            check=False,
        )
        if completed.returncode != 0:
            print(
                json.dumps(
                    {
                        "event": "terminal_nonzero",
                        "returncode": completed.returncode,
                        "result_exists": RESULT.exists(),
                    }
                ),
                flush=True,
            )
            return completed.returncode
        if RESULT.exists():
            break
        progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
        print(
            json.dumps(
                {
                    "event": "condition_invocation_complete",
                    "completed_conditions": progress["completed_conditions"],
                    "expected_conditions": progress["expected_conditions"],
                    "progress_sha256": progress["progress_sha256"],
                }
            ),
            flush=True,
        )
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "event": "t177_terminal",
                "status": result["status"],
                "decision": result["decision"],
                "completed_conditions": result["summary"][
                    "completed_conditions"
                ],
                "first_failed_condition": result["summary"][
                    "first_failed_condition"
                ],
            }
        ),
        flush=True,
    )
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
