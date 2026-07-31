#!/usr/bin/env python3
"""Attribute T145C failures using frozen traces only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable, Mapping

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t146_upper_command_attribution_preregistration.json"
RESULT = ANALYSIS / "t146_upper_command_attribution_result.json"
MARKDOWN = ANALYSIS / "T146_UPPER_COMMAND_ATTRIBUTION_RESULT_20260729.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_trace(item: Mapping[str, Any], name: str) -> Path:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != item["bytes"]
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"changed T146 trace {name}: {path}")
    return path


def rows(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def exact_vector(value: Any) -> bytes:
    return np.asarray(value, dtype=np.float64).tobytes()


def handoff_signature(row: Mapping[str, Any]) -> dict[str, Any]:
    state = row["policy_state_input"]
    observation = np.asarray(row["obs_state"], dtype=np.float64)
    physical_observation = np.concatenate(
        [observation[:6], observation[13:101]]
    )
    return {
        "actual_position_pre_rad": exact_vector(
            row["actual_position_pre_rad"]
        ),
        "physical_observation_excluding_command_and_reference": (
            physical_observation.tobytes()
        ),
        "previous_action": exact_vector(state["previous_action"]),
        "h_in": exact_vector(state["h_in"]),
        "calibration_context_sha256": row[
            "policy_calibration_context_sha256"
        ],
    }


def parse_training_metrics(log: str) -> list[dict[str, float | int]]:
    pattern = re.compile(
        r"STEP:\s*(\d+)\s+reward:\s*([-+0-9.eE]+)"
        r"\s+reward_std:\s*([-+0-9.eE]+)"
    )
    return [
        {
            "step": int(step),
            "reward_mean": float(mean),
            "reward_std": float(std),
            "std_to_abs_mean": float(std) / max(abs(float(mean)), 1e-12),
        }
        for step, mean, std in pattern.findall(log)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T146 requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T146: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T146 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T146_UPPER_COMMAND_ATTRIBUTION"
        or prereg["failed_checks"]
        or canonical_sha256(basis) != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T146 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    t145c = json.loads(
        Path(prereg["frozen_inputs"]["t145c_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    trace_map = {}
    total_rows = 0
    for name, item in prereg["traces"].items():
        path = verify_trace(item, name)
        values = list(rows(path))
        if not values:
            raise RuntimeError(f"empty T146 trace: {path}")
        total_rows += len(values)
        trace_map[str(path)] = {
            "first": values[0],
            "last": values[-1],
            "rows": len(values),
        }

    cells = []
    signatures: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for block in t145c["blocks"]:
        group = (block["checkpoint_id"], block["fit_id"])
        signatures[group] = []
        for cell in block["result"]["cells"]:
            path = cell["protection"]["path"]
            trace = trace_map[path]
            command = float(cell["command_x_m_s"])
            behavior = cell["behavior"]
            signature = handoff_signature(trace["first"])
            signatures[group].append(
                {"command_x_m_s": command, "signature": signature}
            )
            cells.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": command,
                    "cell_green": bool(cell["cell_green"]),
                    "trace_rows": trace["rows"],
                    "last_tick": int(trace["last"]["tick"]),
                    "termination_reason": behavior["termination_reason"],
                    "total_contact_transitions": int(
                        behavior["left_contact_transitions"]
                        + behavior["right_contact_transitions"]
                    ),
                    "mean_local_vx_m_s": behavior["mean_local_vx_m_s"],
                    "tracking_p95_rad": behavior["pitch_tracking_p95_rad"],
                    "action_saturation_pct": behavior[
                        "action_saturation_pct"
                    ],
                    "instant_rate_excess_rad_s": behavior[
                        "instant_rate_excess_rad_s"
                    ],
                }
            )
    handoff_fields = [
        "actual_position_pre_rad",
        "physical_observation_excluding_command_and_reference",
        "previous_action",
        "h_in",
        "calibration_context_sha256",
    ]
    handoff_checks = {}
    for group, items in signatures.items():
        reference = items[0]["signature"]
        handoff_checks[f"{group[0]}:{group[1]}"] = {
            field: all(
                item["signature"][field] == reference[field]
                for item in items[1:]
            )
            for field in handoff_fields
        }
    failing = [cell for cell in cells if not cell["cell_green"]]
    high = [
        cell for cell in cells if cell["command_x_m_s"] in {0.077, 0.08}
    ]
    low = [
        cell for cell in cells if cell["command_x_m_s"] in {0.0, 0.074}
    ]
    thresholds = prereg["thresholds"]
    training_log = Path(
        prereg["frozen_inputs"]["t129_training_log"]["path"]
    ).read_text(encoding="utf-8", errors="replace")
    metrics = parse_training_metrics(training_log)
    checks = {
        "all_command_handoffs_bit_exact_within_checkpoint_fit": all(
            all(fields.values()) for fields in handoff_checks.values()
        ),
        "only_upper_commands_fail": (
            len(failing) == 8
            and all(cell["command_x_m_s"] in {0.077, 0.08} for cell in failing)
        ),
        "x0_and_x074_all_pass": len(low) == 8 and all(
            cell["cell_green"] for cell in low
        ),
        "all_upper_commands_fail": len(high) == 8 and all(
            not cell["cell_green"] for cell in high
        ),
        "all_failures_after_sustained_walking": all(
            cell["last_tick"]
            >= thresholds["minimum_failure_tick_for_sustained_classification"]
            and cell["total_contact_transitions"]
            >= thresholds["minimum_total_contact_transitions"]
            for cell in failing
        ),
        "failure_not_saturation_or_rate_excess": all(
            cell["action_saturation_pct"] == 0.0
            and cell["instant_rate_excess_rad_s"] == 0.0
            for cell in failing
        ),
        "training_metrics_cover_zero_half_final": (
            [item["step"] for item in metrics] == [0, 1003520, 2007040]
        ),
        "hosted_reward_dispersion_exceeds_mean_at_both_exports": all(
            item["reward_std"] > abs(item["reward_mean"])
            for item in metrics
            if item["step"] > 0
        ),
        "new_behavior_optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    sustained = not failed_checks
    handoff = (
        not checks["all_command_handoffs_bit_exact_within_checkpoint_fit"]
        or not checks["all_failures_after_sustained_walking"]
    )
    if sustained:
        classification = "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
        decision = prereg["decision_rule"]["sustained_command_decision"]
    elif handoff:
        classification = "HANDOFF_CAUSALITY_REMAINS_PLAUSIBLE"
        decision = prereg["decision_rule"]["handoff_decision"]
    else:
        classification = "INCONCLUSIVE"
        decision = prereg["decision_rule"]["inconclusive_decision"]
    value: dict[str, Any] = {
        "schema_version": "open_duck.t146_upper_command_attribution_result.v1",
        "status": (
            "PASS_T146_UPPER_COMMAND_ATTRIBUTION"
            if sustained
            else "HOLD_T146_UPPER_COMMAND_ATTRIBUTION"
        ),
        "classification": classification,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "handoff_checks": handoff_checks,
        "cells": cells,
        "failure_summary": {
            "failing_cells": len(failing),
            "minimum_last_tick": min(cell["last_tick"] for cell in failing),
            "maximum_last_tick": max(cell["last_tick"] for cell in failing),
            "minimum_contact_transitions": min(
                cell["total_contact_transitions"] for cell in failing
            ),
            "maximum_contact_transitions": max(
                cell["total_contact_transitions"] for cell in failing
            ),
        },
        "hosted_training_metrics": metrics,
        "checks": checks,
        "failed_checks": failed_checks,
        "execution": {
            "trace_rows_read": total_rows,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "command_group_risk_cpu_contract_preregistration": sustained,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T146 upper-command attribution result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{classification}`\n"
        f"- Decision: `{decision}`\n"
        f"- Failing cells: `{len(failing)}/16`, all at x=.077/.08\n"
        f"- Failure tick range: `{value['failure_summary']['minimum_last_tick']}"
        f"–{value['failure_summary']['maximum_last_tick']}`\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={classification}")
    print(f"decision={decision}")
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if sustained else 1


if __name__ == "__main__":
    raise SystemExit(main())
