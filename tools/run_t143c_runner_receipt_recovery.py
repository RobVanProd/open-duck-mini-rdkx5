#!/usr/bin/env python3
"""Recover T143 after T143B retained the obsolete runner receipt."""

from __future__ import annotations

import json
from pathlib import Path

import run_t143_conditional_forward_path_transform as t143
from run_t136_static_calibration_router_transform import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RECOVERY = ANALYSIS / "t143c_runner_receipt_recovery_preregistration.json"
RESULT = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T143C_RUNNER_RECEIPT_RECOVERY_RESULT_20260729.md"
)
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t143c_conditional_forward_path_v1"
)


def main() -> int:
    prereg = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if prereg.get("recovery_kind") != "T143B_OBSOLETE_PRIMARY_RUNNER_RECEIPT":
        raise RuntimeError("T143C recovery identity changed")
    t143.PREREG = RECOVERY
    t143.RESULT = RESULT
    t143.MARKDOWN = MARKDOWN
    t143.WORK = WORK
    code = t143.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
    )
    value["schema_version"] = (
        "open_duck.t143c_runner_receipt_recovery_result.v1"
    )
    value["status"] = (
        "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
        if passed
        else "HOLD_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
    )
    value["recovery_kind"] = prereg["recovery_kind"]
    value["source_t143_contract_sha256"] = prereg[
        "source_t143_contract_sha256"
    ]
    value["result_sha256"] = canonical_sha256(
        {
            key: item
            for key, item in value.items()
            if key != "result_sha256"
        }
    )
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T143C runner-receipt recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- T143/T143B transforms and behavior before recovery: `0/0`\n"
        "- Recovery behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"result_sha256={value['result_sha256']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
