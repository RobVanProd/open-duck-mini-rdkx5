#!/usr/bin/env python3
"""Rebind T182 to its exact single-command formal worker."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
WORKER = ROOT / "tools" / "evaluate_t182_shared_failure_single_cell.py"
RUNNER = ROOT / "tools" / "run_t182_shared_failure_single_cell.py"
TEST = ROOT / "tests" / "test_t182b_single_command_worker.py"
T182_PREREG = ANALYSIS / "t182_shared_failure_single_cell_preregistration.json"
RECOVERY = ANALYSIS / "t182_worker_command_contract_recovery_20260730.json"
OUTPUT = (
    ANALYSIS / "t182b_shared_failure_single_cell_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T182B_SHARED_FAILURE_SINGLE_CELL_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    receipt,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T182B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T182B preregistration requires a clean worktree")
    prior = _load_json(T182_PREREG)
    recovery = _load_json(RECOVERY)
    if (
        prior.get("preregistered_contract_sha256")
        != "95c704ebea493bcc72171db72fd5fee88786fdde44219bba2cb0d6cedbd511d2"
        or recovery.get("result_sha256")
        != "01b8e7efe60d9075fd032605bc6e31a73f73e9b1e58ea910fb288162f66b3557"
    ):
        raise RuntimeError("T182B recovery identity differs")
    repository_inputs = dict(prior["repository_inputs"])
    repository_inputs["worker"] = receipt(WORKER)
    frozen_paths = {
        "builder": BUILDER,
        "single_command_worker": WORKER,
        "runner": RUNNER,
        "test": TEST,
        "invalid_t182_preregistration": T182_PREREG,
        "worker_contract_recovery": RECOVERY,
    }
    value = {
        key: item
        for key, item in prior.items()
        if key
        not in {
            "schema_version",
            "repository_commit",
            "repository_inputs",
            "frozen_inputs",
            "preregistered_contract_sha256",
        }
    }
    value.update(
        {
            "schema_version": (
                "open_duck.t182b_shared_failure_single_cell_"
                "preregistration.v1"
            ),
            # Retained for the frozen T182 runner; recovery identity is explicit.
            "status": "PREREGISTERED_T182_SHARED_FAILURE_SINGLE_CELL",
            "repository_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "repository_inputs": repository_inputs,
            "recovery": {
                "status": (
                    "PREREGISTERED_T182B_SINGLE_COMMAND_WORKER_RECOVERY"
                ),
                "recovery_sha256": recovery["result_sha256"],
                "allowed_formal_commands": [0.077],
                "all_other_t182_fields_exact": True,
            },
            "frozen_inputs": {
                name: receipt(path) for name, path in frozen_paths.items()
            },
        }
    )
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T182B shared-failure single-cell preregistration\n\n"
        "- Status: `PREREGISTERED_T182B_SINGLE_COMMAND_WORKER_RECOVERY`\n"
        "- Only correction: formal command tuple `(.077,)`\n"
        "- Policy, fit, positive-Z condition, seed, duration, calibration, "
        "handoff, behavior, and protection: unchanged\n"
        "- Fresh cache required; one behavior cell; no retry\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["recovery"]["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
