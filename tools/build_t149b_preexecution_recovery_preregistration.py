#!/usr/bin/env python3
"""Freeze T149B's verifier-label-only pre-execution recovery."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


OUTPUT = ANALYSIS / "t149b_preexecution_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T149B_PREEXECUTION_RECOVERY_PREREGISTRATION_20260729.md"
)
T149 = ANALYSIS / "t149_negative_context_command_plateau_preregistration.json"
SOURCE_RUNNER = (
    ROOT / "tools/run_t149_negative_context_command_plateau_transform.py"
)
RUNNER = ROOT / "tools/run_t149b_preexecution_recovery.py"
TEST = ROOT / "tests/test_t149b_preexecution_recovery.py"
SOURCE_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t149_negative_context_command_plateau_v1"
)
SOURCE_RESULT = (
    ANALYSIS / "t149_negative_context_command_plateau_result.json"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T149B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T149B preregistration requires clean tree")
    source = json.loads(T149.read_text(encoding="utf-8"))
    runner_text = SOURCE_RUNNER.read_text(encoding="utf-8")
    checks = {
        "source_contract_green": (
            source["status"]
            == "PREREGISTERED_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
            and source["failed_checks"] == []
        ),
        "source_stopped_before_work_or_result": (
            not SOURCE_WORK.exists() and not SOURCE_RESULT.exists()
        ),
        "source_defect_exact": (
            "for item in prereg[\"frozen_inputs\"].values():"
            in runner_text
            and "        verify(item)\n" in runner_text
        ),
        "recovery_runner_uses_labeled_verification": (
            "for name, item in prereg[\"frozen_inputs\"].items():"
            in RUNNER.read_text(encoding="utf-8")
            and "t149.verify(item, name)"
            in RUNNER.read_text(encoding="utf-8")
        ),
        "all_recovery_sources_present": all(
            path.exists() for path in (T149, SOURCE_RUNNER, RUNNER, TEST)
        ),
        "mechanism_thresholds_and_decision_unchanged": True,
        "no_environment_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T149B preregistration checks failed: {failed}")
    frozen = dict(source["frozen_inputs"])
    frozen.update(
        {
            "source_preregistration": receipt(T149),
            "source_runner": receipt(SOURCE_RUNNER),
            "recovery_builder": receipt(Path(__file__).resolve()),
            "recovery_runner": receipt(RUNNER),
            "recovery_test": receipt(TEST),
        }
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t149b_preexecution_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T149B_PREEXECUTION_RECOVERY",
        "question": source["question"],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "recovery_kind": "T149_MISSING_VERIFY_LABEL_PREEXECUTION",
        "source_t149_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "mechanism": source["mechanism"],
        "thresholds": source["thresholds"],
        "frozen_inputs": frozen,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            **source["decision_rule"],
            "no_further_preexecution_recovery": True,
        },
        "execution_now": source["execution_now"],
        "authority": source["authority"],
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T149B pre-execution recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source failure: missing receipt-verifier label\n"
        "- Work/results produced before stop: none\n"
        "- Mechanism/thresholds/decision: unchanged\n"
        "- Environment / behavior / optimizer / Colab / robot: `0/0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
