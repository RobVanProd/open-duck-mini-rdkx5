#!/usr/bin/env python3
"""Rerun T146 using pre-action handoff fields."""

from __future__ import annotations

import json
from pathlib import Path

import run_t146_upper_command_attribution as t146
from run_t136_static_calibration_router_transform import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RECOVERY = ANALYSIS / "t146b_pre_action_field_recovery_preregistration.json"
RESULT = ANALYSIS / "t146b_pre_action_field_recovery_result.json"
MARKDOWN = ANALYSIS / "T146B_PRE_ACTION_FIELD_RECOVERY_RESULT_20260729.md"


def main() -> int:
    prereg = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (
        prereg.get("recovery_kind")
        != "T146_POST_ACTION_FIELDS_USED_FOR_HANDOFF"
    ):
        raise RuntimeError("T146B recovery identity changed")
    t146.PREREG = RECOVERY
    t146.RESULT = RESULT
    t146.MARKDOWN = MARKDOWN
    code = t146.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = value["status"] == "PASS_T146_UPPER_COMMAND_ATTRIBUTION"
    value["schema_version"] = (
        "open_duck.t146b_pre_action_field_recovery_result.v1"
    )
    value["status"] = (
        "PASS_T146B_UPPER_COMMAND_ATTRIBUTION"
        if passed
        else "HOLD_T146B_UPPER_COMMAND_ATTRIBUTION"
    )
    value["recovery_kind"] = prereg["recovery_kind"]
    value["source_t146_contract_sha256"] = prereg[
        "source_t146_contract_sha256"
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
        "# T146B pre-action field recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        "- Existing trace rows reused; new behavior / training: `0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"result_sha256={value['result_sha256']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
