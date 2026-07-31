#!/usr/bin/env python3
"""Run T227D's metadata-corrected recovered CPU validation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))

import run_t227c_recovered_cpu_validation as base  # noqa: E402


PREREG = (
    ANALYSIS / "t227d_recovered_cpu_validation_preregistration.json"
)
RESULT = ANALYSIS / "t227d_recovered_cpu_validation_result.json"
MARKDOWN = (
    ANALYSIS / "T227D_RECOVERED_CPU_VALIDATION_RESULT_20260730.md"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T227D_RECOVERED_CPU_VALIDATION"
        or value.get("failed_checks")
        or base.engine.t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T227D preregistration identity changed")
    for name, item in value["sources"].items():
        base.engine.t20.verify_receipt(item, f"sources.{name}")
    for name, item in value["assets"].items():
        base.engine.t20.verify_receipt(item, f"assets.{name}")
    for name, item in value["frozen_artifacts"].items():
        base.engine.t20.verify_receipt(
            item, f"frozen_artifacts.{name}"
        )
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): base.engine.t20.sha256(
            path
        )
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or base.engine.t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T227D playground changed")


def main() -> int:
    base.PREREG = PREREG
    base.RESULT = RESULT
    base.MARKDOWN = MARKDOWN
    base.validate_prereg = validate_prereg
    return_code = base.main()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value.pop("result_sha256", None)
    passed = return_code == 0 and not value["failed_checks"]
    value["schema_version"] = (
        "open_duck.t227d_recovered_cpu_validation_result.v1"
    )
    value["status"] = (
        "PASS_T227D_RECOVERED_CPU_VALIDATION"
        if passed
        else "HOLD_T227D_RECOVERED_CPU_VALIDATION"
    )
    value["metadata_correction"] = {
        "classification": (
            "MISSING_CARRIED_FORWARD_RUNNER_READBACK"
        ),
        "scientific_mechanism_changed": False,
        "evidence_artifacts_changed": False,
        "prior_optimizer_steps": 0,
        "prior_onnx_inferences": 0,
    }
    value["result_sha256"] = base.engine.t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T227D recovered CPU validation result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{value['failed_checks']}`\n"
        "- Recovery: exact T227B artifacts, no training rerun\n"
        "- Metadata fix: carried-forward frozen runner readback only\n"
        "- New optimizer / simulator / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={value['failed_checks']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
