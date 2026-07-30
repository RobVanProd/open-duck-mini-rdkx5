#!/usr/bin/env python3
"""Run T227B's activation-order-corrected T227 CPU contract."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))

import run_t227_command_atom_cpu_contract as base  # noqa: E402


PREREG = (
    ANALYSIS / "t227b_command_atom_cpu_retry_preregistration.json"
)
RESULT = ANALYSIS / "t227b_command_atom_cpu_result.json"
MARKDOWN = ANALYSIS / "T227B_COMMAND_ATOM_CPU_RESULT_20260730.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t227b_command_atom_cpu_contract_v3"
)
_BASE_TRANSFORM = base.transform_result


def validate_prereg(value: dict[str, Any]) -> None:
    basis = dict(value)
    basis.pop("preregistered_contract_sha256", None)
    if (
        value.get("status")
        != "PREREGISTERED_T227B_COMMAND_ATOM_CPU_RETRY"
        or value.get("failed_checks")
        or base.engine.t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T227B preregistration identity changed")
    for name, item in value["sources"].items():
        base.engine.t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        base.engine.t20.verify_receipt(item, name)
    for name, item in value["abort_evidence"].items():
        base.engine.t20.verify_receipt(item, name)
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
        raise RuntimeError("T227B composed playground changed")


def transform_result(return_code: int) -> int:
    interim_code = _BASE_TRANSFORM(return_code)
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    value.pop("result_sha256", None)
    passed = interim_code == 0 and not value["failed_checks"]
    value["schema_version"] = (
        "open_duck.t227b_command_atom_cpu_result.v1"
    )
    value["status"] = (
        "PASS_T227B_COMMAND_ATOM_CPU_CONTRACT"
        if passed
        else "HOLD_T227B_COMMAND_ATOM_CPU_CONTRACT"
    )
    value["retry_provenance"] = {
        "classification": (
            "COMMAND_ATOMS_ENABLED_DURING_UNVECTORIZED_ABI_PROBE"
        ),
        "scientific_mechanism_changed": False,
        "prior_environment_contract_green": True,
        "prior_optimizer_steps": 0,
        "prior_formal_behavior_cells": 0,
        "prior_hosted_compute_units": 0,
    }
    value["result_sha256"] = base.engine.t20.canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    final_aux = value["training"]["aux"]["1024"]
    MARKDOWN.write_text(
        "# T227B command-atom CPU result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{value['failed_checks']}`\n"
        "- Cartesian reset: 32/32 configuration-command pairs\n"
        "- Activation: after unvectorized 115-D ABI discovery\n"
        f"- Final dual lambda / eta: "
        f"`{final_aux['lambda']}` / `{final_aux['eta']}`\n"
        "- Optimizer / formal behavior / hosted / robot: "
        "`1024 / 0 / 0 / 0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={value['failed_checks']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


def main() -> int:
    base.PREREG = PREREG
    base.RESULT = RESULT
    base.MARKDOWN = MARKDOWN
    base.WORK = WORK
    base.validate_prereg = validate_prereg
    base.transform_result = transform_result
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
