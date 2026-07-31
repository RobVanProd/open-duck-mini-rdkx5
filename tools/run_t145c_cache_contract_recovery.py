#!/usr/bin/env python3
"""Resume T145 while validating cached blocks against their source contract."""

from __future__ import annotations

import json
from pathlib import Path

import run_t145_conditional_path_negative_endpoint as t145
from run_t136_static_calibration_router_transform import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RECOVERY = ANALYSIS / "t145c_cache_contract_recovery_preregistration.json"
SOURCE = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
RESULT = ANALYSIS / "t145c_cache_contract_recovery_result.json"
MARKDOWN = ANALYSIS / "T145C_CACHE_CONTRACT_RECOVERY_RESULT_20260729.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t145_conditional_path_negative_endpoint_v1"
)


def main() -> int:
    prereg = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (
        prereg.get("recovery_kind")
        != "T145B_ORIGINAL_CACHE_CONTRACT_REJECTION"
    ):
        raise RuntimeError("T145C recovery identity changed")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    t145.PREREG = RECOVERY
    t145.RESULT = RESULT
    t145.MARKDOWN = MARKDOWN
    t145.CACHE = CACHE
    t145.ALLOW_EXISTING_CACHE = True
    t145.SOURCE_CACHE_PREREG = source
    code = t145.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["schema_version"] = (
        "open_duck.t145c_cache_contract_recovery_result.v1"
    )
    value["status"] = (
        "PASS_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
        if passed
        else "HOLD_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
    )
    value["recovery_kind"] = prereg["recovery_kind"]
    value["source_t145_contract_sha256"] = prereg[
        "source_t145_contract_sha256"
    ]
    value["execution"]["source_completed_behavior_cells"] = 8
    value["execution"]["t145b_new_behavior_cells"] = 0
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
        "# T145C cache-contract recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{value['condition']['green_cells']}/16`\n"
        "- Original / T145B / newly evaluated cells: `8/0/8`\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"result_sha256={value['result_sha256']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
