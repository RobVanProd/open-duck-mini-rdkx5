#!/usr/bin/env python3
"""Resume T145's exact cache after its parent process was interrupted."""

from __future__ import annotations

import json
from pathlib import Path

import run_t145_conditional_path_negative_endpoint as t145
from run_t136_static_calibration_router_transform import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RECOVERY = ANALYSIS / "t145b_parent_interruption_recovery_preregistration.json"
RESULT = ANALYSIS / "t145b_parent_interruption_recovery_result.json"
MARKDOWN = ANALYSIS / "T145B_PARENT_INTERRUPTION_RECOVERY_RESULT_20260729.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t145_conditional_path_negative_endpoint_v1"
)


def main() -> int:
    prereg = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (
        prereg.get("recovery_kind")
        != "T145_PARENT_INTERRUPTED_AFTER_TWO_BLOCKS"
    ):
        raise RuntimeError("T145B recovery identity changed")
    t145.PREREG = RECOVERY
    t145.RESULT = RESULT
    t145.MARKDOWN = MARKDOWN
    t145.CACHE = CACHE
    t145.ALLOW_EXISTING_CACHE = True
    code = t145.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["schema_version"] = (
        "open_duck.t145b_parent_interruption_recovery_result.v1"
    )
    value["status"] = (
        "PASS_T145B_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
        if passed
        else "HOLD_T145B_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["recovery_kind"] = prereg["recovery_kind"]
    value["source_t145_contract_sha256"] = prereg[
        "source_t145_contract_sha256"
    ]
    value["execution"]["source_completed_behavior_cells"] = 8
    value["execution"]["recovery_new_behavior_cells"] = 8
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
        "# T145B parent-interruption recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{value['condition']['green_cells']}/16`\n"
        "- Preserved / newly evaluated cells: `8/8`\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"result_sha256={value['result_sha256']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
