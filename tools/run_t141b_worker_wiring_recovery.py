#!/usr/bin/env python3
"""Recover T141 after its pre-behavior worker-wiring failure."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import run_t141_expert_bank_negative_endpoint as t141
from run_t136_static_calibration_router_transform import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RECOVERY = ANALYSIS / "t141b_worker_wiring_recovery_preregistration.json"
RESULT = ANALYSIS / "t141b_worker_wiring_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T141B_WORKER_WIRING_RECOVERY_RESULT_20260729.md"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t141b_expert_bank_negative_endpoint_v1"
)


def main() -> int:
    prereg = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (
        prereg.get("recovery_kind")
        != "T141_PRE_BEHAVIOR_REPOSITORY_INPUT_WIRING"
    ):
        raise RuntimeError("T141B recovery identity changed")
    for label, item in prereg["repository_inputs"].items():
        t141.verify(item)
    t141.PREREG = RECOVERY
    t141.RESULT = RESULT
    t141.MARKDOWN = MARKDOWN
    t141.CACHE = CACHE
    code = t141.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["schema_version"] = (
        "open_duck.t141b_worker_wiring_recovery_result.v1"
    )
    value["status"] = (
        "PASS_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
        if passed
        else "HOLD_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["recovery_kind"] = prereg["recovery_kind"]
    value["source_t141_contract_sha256"] = prereg[
        "source_t141_contract_sha256"
    ]
    value["result_sha256"] = ""
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
        "# T141B worker-wiring recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{value['condition']['green_cells']}/16`\n"
        "- Original T141 behavior cells: `0`; recovery cells: `16`\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"result_sha256={value['result_sha256']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
