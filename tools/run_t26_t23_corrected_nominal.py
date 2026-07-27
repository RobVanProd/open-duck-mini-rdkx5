#!/usr/bin/env python3
"""Reclassify T25B using the frozen T5 manufacturer-duration protections."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from run_t5_actuator_protection_reanalysis import (
    corrected_failure_reasons,
    duration_metrics,
    read_trace,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t26_t23_corrected_nominal_preregistration.json"
RESULT = ANALYSIS / "t26_t23_corrected_nominal_result.json"
MARKDOWN = ANALYSIS / "T26_T23_CORRECTED_NOMINAL_RESULT_20260726.md"


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_inputs(prereg: Mapping[str, Any]) -> None:
    for name, spec in prereg["repository_inputs"].items():
        path = Path(spec["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(spec["bytes"])
            or sha256(path) != spec["sha256"]
        ):
            raise ValueError(f"frozen repository input mismatch: {name}")
    manifest = prereg["external_run_manifest"]
    root = Path(manifest["root"])
    for spec in manifest["files"]:
        path = root / spec["relative_path"]
        if (
            not path.is_file()
            or path.stat().st_size != int(spec["bytes"])
            or sha256(path) != spec["sha256"]
        ):
            raise ValueError(f"frozen external input mismatch: {path}")


def audit_cell(
    cell_path: Path,
    *,
    protection: Mapping[str, Any],
    manifest_by_relative_path: Mapping[str, Mapping[str, Any]],
    root: Path,
) -> dict[str, Any]:
    cell = load_json(cell_path)
    trace_path = Path(cell["trace"]["path"])
    relative_trace = trace_path.relative_to(root).as_posix()
    trace_spec = manifest_by_relative_path[relative_trace]
    if (
        trace_spec["sha256"] != cell["trace"]["sha256"]
        or int(trace_spec["rows"]) != int(cell["trace"]["rows"])
    ):
        raise ValueError(f"cell-to-trace manifest mismatch: {cell_path}")
    _, force = read_trace(
        trace_path,
        expected_rows=int(cell["trace"]["rows"]),
    )
    duration = duration_metrics(
        force,
        motor_constant_nm_per_a=float(
            protection["motor_constant_nm_per_a"]
        ),
        overcurrent_threshold_a=float(
            protection["overcurrent_threshold_a"]
        ),
        overload_threshold_nm=float(protection["overload_threshold_nm"]),
        trip_ticks=int(protection["trip_ticks"]),
    )
    corrected_failures = corrected_failure_reasons(
        cell["failure_reasons"], duration
    )
    return {
        "identity": cell["identity"],
        "cell": {
            "path": str(cell_path),
            "sha256": sha256(cell_path),
        },
        "trace": {
            "path": str(trace_path),
            "sha256": sha256(trace_path),
            "rows": int(cell["trace"]["rows"]),
        },
        "original": {
            "pass": bool(cell["pass"]),
            "failure_reasons": list(cell["failure_reasons"]),
        },
        "corrected": {
            "pass": not corrected_failures,
            "failure_reasons": corrected_failures,
            "duration_protection": duration,
        },
        "preserved_metrics": {
            "candidate_gate_status": cell["metrics"][
                "candidate_gate_status"
            ],
            "termination_reason": cell["metrics"]["termination_reason"],
            "mean_local_vx_m_s": cell["metrics"]["mean_local_vx_m_s"],
            "worst_tracking_p95_rad": cell["metrics"][
                "worst_tracking_p95_rad"
            ],
            "worst_saturation_pct": cell["metrics"][
                "worst_saturation_pct"
            ],
            "max_conservative_rate_excess_rad_s": cell["metrics"][
                "max_conservative_rate_excess_rad_s"
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T26 result")

    prereg = load_json(PREREG)
    if (
        prereg["status"]
        != "PREREGISTERED_T26_T23_CORRECTED_NOMINAL_RECLASSIFICATION"
        or prereg["failed_checks"]
    ):
        raise ValueError("T26 preregistration is not passing")
    verify_inputs(prereg)

    manifest = prereg["external_run_manifest"]
    root = Path(manifest["root"])
    by_relative = {
        spec["relative_path"]: spec for spec in manifest["files"]
    }
    protection = prereg["frozen_reclassification"][
        "corrected_protection_contract"
    ]
    cells = []
    for spec in manifest["files"]:
        relative = spec["relative_path"]
        if relative.startswith("cells/") and relative.endswith(".json"):
            cells.append(
                audit_cell(
                    root / relative,
                    protection=protection,
                    manifest_by_relative_path=by_relative,
                    root=root,
                )
            )

    checkpoint_rows = []
    for checkpoint_id in prereg["frozen_reclassification"][
        "expected_checkpoints"
    ]:
        selected = [
            row
            for row in cells
            if row["identity"]["checkpoint_id"] == checkpoint_id
        ]
        checkpoint_rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "cells": len(selected),
                "original_passing_cells": sum(
                    row["original"]["pass"] for row in selected
                ),
                "corrected_passing_cells": sum(
                    row["corrected"]["pass"] for row in selected
                ),
                "corrected_all_eight_pass": (
                    len(selected)
                    == int(
                        prereg["frozen_reclassification"][
                            "cells_per_checkpoint"
                        ]
                    )
                    and all(row["corrected"]["pass"] for row in selected)
                ),
            }
        )

    expected_cells = int(
        prereg["frozen_reclassification"]["expected_cells"]
    )
    persistent_pass = (
        len(cells) == expected_cells
        and all(row["corrected"]["pass"] for row in cells)
        and all(row["corrected_all_eight_pass"] for row in checkpoint_rows)
    )
    result = {
        "schema_version": "open_duck.t26_t23_corrected_nominal_result.v1",
        "status": (
            "PASS_T26_T23_CORRECTED_NOMINAL_PERSISTENCE"
            if persistent_pass
            else "HOLD_T26_T23_CORRECTED_NOMINAL_PERSISTENCE"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if persistent_pass
            else prereg["decision_rule"]["fail_decision"]
        ),
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "external_manifest": manifest["manifest_sha256"],
        },
        "summary": {
            "cells": len(cells),
            "original_passing_cells": sum(
                row["original"]["pass"] for row in cells
            ),
            "corrected_passing_cells": sum(
                row["corrected"]["pass"] for row in cells
            ),
            "persistent_both_checkpoint_pass": persistent_pass,
            "worst_strict_overcurrent_run_ticks": max(
                row["corrected"]["duration_protection"][
                    "worst_strict_overcurrent_run_ticks"
                ]
                for row in cells
            ),
            "worst_strict_overload_run_ticks": max(
                row["corrected"]["duration_protection"][
                    "worst_strict_overload_run_ticks"
                ]
                for row in cells
            ),
            "worst_peak_current_a_diagnostic": max(
                row["corrected"]["duration_protection"][
                    "worst_peak_current_a"
                ]
                for row in cells
            ),
            "worst_peak_torque_nm_diagnostic": max(
                row["corrected"]["duration_protection"][
                    "worst_peak_torque_nm"
                ]
                for row in cells
            ),
            "worst_tracking_p95_rad": max(
                row["preserved_metrics"]["worst_tracking_p95_rad"]
                for row in cells
            ),
            "all_candidate_gates_green": all(
                row["preserved_metrics"]["candidate_gate_status"]
                == "PASS_CANDIDATE_SIM_GATE"
                for row in cells
            ),
            "all_duration_complete": all(
                row["preserved_metrics"]["termination_reason"]
                == "duration_complete"
                for row in cells
            ),
            "all_nonprotection_failures_absent": all(
                not row["corrected"]["failure_reasons"] for row in cells
            ),
        },
        "per_checkpoint": checkpoint_rows,
        "cells": cells,
        "authority": {
            "policy_nominally_persistent_under_corrected_gate": (
                persistent_pass
            ),
            "robustness_preregistration_authorized": persistent_pass,
            "robustness_execution_authorized": False,
            "checkpoint_selection_authorized": False,
            "training_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = result["summary"]
    MARKDOWN.write_text(
        "# T26 T23 corrected nominal result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Original / corrected cells: "
        f"`{summary['original_passing_cells']}/16` / "
        f"`{summary['corrected_passing_cells']}/16`\n"
        f"- Persistent both-checkpoint pass: "
        f"`{summary['persistent_both_checkpoint_pass']}`\n"
        f"- Worst overcurrent / overload run: "
        f"`{summary['worst_strict_overcurrent_run_ticks']}` / "
        f"`{summary['worst_strict_overload_run_ticks']}` ticks "
        "(limit: 99)\n"
        f"- Worst diagnostic peak current / torque: "
        f"`{summary['worst_peak_current_a_diagnostic']:.9f}` A / "
        f"`{summary['worst_peak_torque_nm_diagnostic']:.9f}` N.m\n"
        "- This is read-only reclassification of frozen T25B traces. It "
        "does not authorize robustness execution, checkpoint selection, "
        "Gate 5, or robot access.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(
        "corrected_cells="
        f"{summary['corrected_passing_cells']}/{summary['cells']}"
    )
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(RESULT)}")
    return 0 if persistent_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
