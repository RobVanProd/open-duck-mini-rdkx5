#!/usr/bin/env python3
"""Independently audit the T12 response-prefix negative-COM screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from run_t6_corrected_robustness_screen import (
    behavior_row,
    classify_behavior,
    trace_summary,
)
from run_t8_state_coherent_handoff import (
    read_trace,
    state_handoff_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t12_response_prefix_com_preregistration.json"
RESULT = ANALYSIS / "t12_response_prefix_com_result.json"
AUDIT = ANALYSIS / "t12_response_prefix_com_independent_audit.json"
MARKDOWN = (
    ANALYSIS / "T12_RESPONSE_PREFIX_COM_INDEPENDENT_AUDIT_20260726.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def valid_receipt(item: dict[str, Any]) -> bool:
    path = Path(item["path"])
    return bool(
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256(path) == item["sha256"]
    )


def exact_readback(report: dict[str, Any] | None) -> bool:
    report = report or {}
    readback = report.get("readback") or {}
    before = readback.get("before")
    after = readback.get("after")
    return bool(
        report.get("enabled") is True
        and report.get("key") == "torso_com_offset_m"
        and report.get("value") == [-0.05, 0.0, 0.0]
        and readback.get("body_id") == 2
        and readback.get("body_name") == "trunk_assembly"
        and isinstance(before, list)
        and isinstance(after, list)
        and len(before) == 3
        and len(after) == 3
        and abs(float(after[0]) - float(before[0]) + 0.05) <= 1e-12
        and float(after[1]) == float(before[1])
        and float(after[2]) == float(before[2])
    )


def append_if(issues: list[str], condition: bool, name: str) -> None:
    if not condition:
        issues.append(name)


def main() -> int:
    if AUDIT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T12 audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg_basis = {
        key: prereg[key]
        for key in (
            "schema_version",
            "status",
            "question",
            "causal_basis",
            "sources",
            "playground",
            "candidate",
            "matrix",
            "handoff_contract",
            "behavior_contract",
            "protection_contract",
            "decision_rule",
            "authority",
            "execution_now",
        )
    }
    result_basis = {
        key: value
        for key, value in result.items()
        if key != "result_sha256"
    }
    issues: list[str] = []
    append_if(
        issues,
        canonical_sha256(prereg_basis)
        == prereg["preregistered_contract_sha256"],
        "preregistration_canonical",
    )
    append_if(
        issues,
        canonical_sha256(result_basis) == result["result_sha256"],
        "result_canonical",
    )
    for name, item in prereg["sources"].items():
        append_if(issues, valid_receipt(item), f"source:{name}")
    recomputed_blocks = []
    for block in result["blocks"]:
        raw = block["raw"]
        append_if(
            issues,
            valid_receipt(raw["evaluation"]),
            f"{block['checkpoint_id']}:{block['fit_id']}:evaluation",
        )
        append_if(
            issues,
            valid_receipt(raw["stdout"]),
            f"{block['checkpoint_id']}:{block['fit_id']}:stdout",
        )
        evaluation = json.loads(
            Path(raw["evaluation"]["path"]).read_text(encoding="utf-8")
        )
        traces = {
            Path(item["path"]).name: item for item in raw["traces"]
        }
        cells = []
        for run in evaluation["runs"]:
            item = traces[Path(run["trace_jsonl"]).name]
            append_if(
                issues,
                valid_receipt(item),
                (
                    f"{block['checkpoint_id']}:{block['fit_id']}:"
                    f"x{float(run['command_x']):.3f}:trace"
                ),
            )
            path = Path(item["path"])
            records = read_trace(path)
            behavior = classify_behavior(
                behavior_row(run), prereg["behavior_contract"]
            )
            protection = trace_summary(
                path, prereg["protection_contract"]
            )
            handoff = state_handoff_summary(run, records)
            trace_valid = bool(
                protection["ticks_contiguous_from_zero"]
                and protection["rows"] == behavior["samples"]
                and sha256(path) == item["sha256"]
            )
            readback = exact_readback(run.get("dynamics_override"))
            green = bool(
                trace_valid
                and behavior["core_pass"]
                and behavior["replacement_quality_pass"]
                and protection["duration_protection_pass"]
                and protection[
                    "maximum_full_measured_vector_excess_rad_s"
                ]
                == 0.0
                and handoff["all_checks_pass"]
                and readback
            )
            cells.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(run["command_x"]),
                    "behavior": behavior,
                    "protection": protection,
                    "handoff": handoff,
                    "trace": item,
                    "trace_valid": trace_valid,
                    "com_readback_exact": readback,
                    "cell_green": green,
                }
            )
        recomputed = {
            "checkpoint_id": block["checkpoint_id"],
            "fit_id": block["fit_id"],
            "cells": cells,
        }
        recomputed_blocks.append(recomputed)
        append_if(
            issues,
            cells == block["cells"],
            f"{block['checkpoint_id']}:{block['fit_id']}:cells_exact",
        )
    cells = [
        cell for block in recomputed_blocks for cell in block["cells"]
    ]
    append_if(issues, len(cells) == 12, "matrix_exact")
    append_if(
        issues,
        sum(int(cell["cell_green"]) for cell in cells)
        == result["summary"]["green_cells"],
        "green_count",
    )
    append_if(
        issues,
        all(cell["handoff"]["all_checks_pass"] for cell in cells),
        "handoff_chains",
    )
    append_if(
        issues,
        all(cell["com_readback_exact"] for cell in cells),
        "com_readbacks",
    )
    expected_pass = all(cell["cell_green"] for cell in cells)
    append_if(
        issues,
        (result["status"] == "PASS_T12_RESPONSE_PREFIX_COM_SCREEN")
        == expected_pass,
        "status_classification",
    )
    passed = not issues
    basis = {
        "schema_version": "open_duck.t12_response_prefix_com_audit.v1",
        "status": (
            "PASS_T12_RESPONSE_PREFIX_COM_INDEPENDENT_AUDIT"
            if passed
            else "HOLD_T12_RESPONSE_PREFIX_COM_INDEPENDENT_AUDIT"
        ),
        "decision": (
            result["decision"]
            if passed
            else "HOLD_T12_EVIDENCE_INCONSISTENT"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "result_sha256": result["result_sha256"],
        "recomputed_green_cells": sum(
            int(cell["cell_green"]) for cell in cells
        ),
        "recomputed_total_cells": len(cells),
        "issues": issues,
        "execution": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "audit_sha256": canonical_sha256(basis)}
    AUDIT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T12 response-prefix negative-COM independent audit\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Recomputed green cells: "
        f"`{value['recomputed_green_cells']}/12`\n"
        f"- Issues: `{issues}`\n"
        "- Optimizer/behavior/hosted/robot execution: `0/0/0/0`\n"
        f"- Canonical SHA-256: `{value['audit_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(
        f"green_cells={value['recomputed_green_cells']}/"
        f"{value['recomputed_total_cells']}"
    )
    print(f"issues={issues}")
    print(f"audit_sha256={value['audit_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
