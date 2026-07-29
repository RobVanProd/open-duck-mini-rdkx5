#!/usr/bin/env python3
"""Attribute T113's failure using only frozen trace/result artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t118_routing_failure_attribution_preregistration.json"
RESULT = ANALYSIS / "t118_routing_failure_attribution_result.json"
MARKDOWN = ANALYSIS / "T118_ROUTING_FAILURE_ATTRIBUTION_RESULT_20260729.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify(value: Mapping[str, Any]) -> Path:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T118 input: {path}")
    return path


def load_prereg() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value["status"] != "PREREGISTERED_T118_ROUTING_FAILURE_ATTRIBUTION"
        or value["failed_checks"]
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T118 preregistration changed")
    for item in value["frozen_inputs"].values():
        verify(item)
    return value


def source(prereg: Mapping[str, Any], name: str) -> dict[str, Any]:
    path = verify(prereg["frozen_inputs"][name])
    return json.loads(path.read_text(encoding="utf-8"))


def trace_rows(receipt: Mapping[str, Any]) -> list[dict[str, Any]]:
    path = verify(receipt)
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T118 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T118 execution requires clean worktree")
    prereg = load_prereg()
    started = time.time()
    t103 = source(prereg, "hard_gate")
    t104 = source(prereg, "gate_dynamics")
    t108 = source(prereg, "soft_gate")
    t111 = source(prereg, "always_on")
    t117 = source(prereg, "trainthrough")
    t55 = source(prereg, "single_support_cpu")
    t59 = source(prereg, "single_support_nominal")
    t65 = source(prereg, "single_support_family")

    crossings = []
    failed_moving_cells = 0
    clean_nonstability_contract = True
    threshold = float(
        prereg["analysis_contract"]["pitch_boundary_abs_rad"]
    )
    for block in t117["blocks"]:
        for cell in block["result"]["cells"]:
            if float(cell["command_x_m_s"]) == 0.0 or cell["cell_green"]:
                continue
            failed_moving_cells += 1
            behavior = cell["behavior"]
            protection = cell["protection"]
            clean_nonstability_contract &= bool(
                behavior["replacement_quality_checks"]["tracking"]
                and behavior["replacement_quality_checks"]["p95_rate"]
                and behavior["replacement_quality_checks"]["instant_rate"]
                and behavior["replacement_quality_checks"]["zero_saturation"]
                and protection["duration_protection_pass"]
            )
            rows = trace_rows(
                {
                    "path": protection["path"],
                    "bytes": Path(protection["path"]).stat().st_size,
                    "sha256": protection["sha256"],
                }
            )
            hit = next(
                row
                for row in rows
                if abs(float(row["body_pitch_rad"])) > threshold
            )
            phase = math.atan2(
                float(hit["obs_state"][100]),
                float(hit["obs_state"][99]),
            ) % (2.0 * math.pi)
            crossings.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": cell["command_x_m_s"],
                    "tick": int(hit["tick"]),
                    "pitch_rad": float(hit["body_pitch_rad"]),
                    "pitch_rate_rad_s": float(
                        hit["body_pitch_rate_rad_s"]
                    ),
                    "local_vx_m_s": float(hit["local_linvel_m_s"][0]),
                    "contacts": [int(x) for x in hit["foot_contacts"]],
                    "phase_rad": phase,
                    "phase_quadrant": min(
                        3, int(phase / (0.5 * math.pi))
                    ),
                }
            )
    support_counts: dict[str, int] = {}
    for item in crossings:
        key = "".join(str(x) for x in item["contacts"])
        support_counts[key] = support_counts.get(key, 0) + 1
    quadrants = sorted({item["phase_quadrant"] for item in crossings})
    all_backward_pitch = all(item["pitch_rad"] < -threshold for item in crossings)
    all_backward_motion = all(item["local_vx_m_s"] < 0.0 for item in crossings)

    routing = {
        "hard_gate": int(t103["condition"]["green_cells"]),
        "soft_gate": int(t108["condition"]["green_cells"]),
        "always_on": int(t111["condition"]["green_cells"]),
        "always_on_trainthrough": int(t117["condition"]["green_cells"]),
    }
    expected_routing = prereg["analysis_contract"][
        "routing_comparison_green_cells"
    ]
    fixed_gate = t104["decision_inputs"]
    support_rule = prereg["analysis_contract"][
        "simple_support_phase_mask_rejected_if"
    ]
    simple_mask_rejected = bool(
        support_counts.get("10", 0)
        >= support_rule["left_single_support_crossings_at_least"]
        and support_counts.get("01", 0)
        >= support_rule["right_single_support_crossings_at_least"]
        and len(quadrants)
        >= support_rule["occupied_phase_quadrants_at_least"]
    )
    single_support_family_closed = bool(
        t55["status"] == "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
        and t59["status"] == "HOLD_T59_T56_NOMINAL_MATRIX"
        and t65["status"] == "HOLD_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
        and t65["decision"] == "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
    )
    checks = {
        "exact_eleven_failed_moving_cells": failed_moving_cells == 11,
        "crossing_for_every_failed_moving_cell": (
            len(crossings) == failed_moving_cells
        ),
        "all_crossings_backward_pitch": all_backward_pitch,
        "all_crossings_backward_motion": all_backward_motion,
        "tracking_rate_saturation_and_duration_protection_clean": (
            clean_nonstability_contract
        ),
        "both_single_support_sides_represented": (
            support_counts.get("10", 0) >= 2
            and support_counts.get("01", 0) >= 2
        ),
        "phase_crossings_span_at_least_three_quadrants": len(quadrants) >= 3,
        "simple_support_phase_mask_rejected": simple_mask_rejected,
        "routing_counts_exact": routing == expected_routing,
        "hard_gate_best_existing_route": (
            routing["hard_gate"] > max(
                routing["soft_gate"],
                routing["always_on"],
                routing["always_on_trainthrough"],
            )
        ),
        "always_on_trainthrough_did_not_improve_constant_route": (
            routing["always_on_trainthrough"] <= routing["always_on"]
        ),
        "fixed_gate_negative_false_inactive_positive": (
            fixed_gate["negative_com_false_inactive_fraction_post_warmup"] > 0.0
        ),
        "fixed_gate_nominal_false_active_positive": (
            fixed_gate["nominal_false_active_fraction_post_warmup"] > 0.0
        ),
        "fixed_gate_transitions_material": (
            t104["aggregates"]["com_x_negative_moving"][
                "maximum_gate_transitions_post_warmup"
            ]
            >= 20
        ),
        "single_support_family_closed": single_support_family_closed,
        "analysis_only": True,
        "no_simulator_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t118_routing_failure_attribution_result.v1"
        ),
        "status": (
            "PASS_T118_ROUTING_FAILURE_ATTRIBUTION"
            if passed
            else "HOLD_T118_ROUTING_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["hold_decision"]
        ),
        "classification": (
            "FIXED_ROUTER_UNTRAINED_FOR_CLOSED_LOOP"
            if passed
            else "ROUTING_CAUSE_NOT_ISOLATED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "failure_anatomy": {
            "failed_moving_cells": failed_moving_cells,
            "crossings": crossings,
            "support_counts": support_counts,
            "occupied_phase_quadrants": quadrants,
            "all_backward_pitch": all_backward_pitch,
            "all_backward_motion": all_backward_motion,
            "nonstability_contract_clean": clean_nonstability_contract,
        },
        "routing_comparison_green_cells": routing,
        "fixed_gate_dynamics": {
            "negative_false_inactive_fraction_post_warmup": fixed_gate[
                "negative_com_false_inactive_fraction_post_warmup"
            ],
            "nominal_false_active_fraction_post_warmup": fixed_gate[
                "nominal_false_active_fraction_post_warmup"
            ],
            "maximum_negative_transitions_post_warmup": t104[
                "aggregates"
            ]["com_x_negative_moving"][
                "maximum_gate_transitions_post_warmup"
            ],
        },
        "balance_first": {
            "cpu_contract_passed": (
                t55["status"] == "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            ),
            "hosted_nominal_persistence_failed": (
                t59["status"] == "HOLD_T59_T56_NOMINAL_MATRIX"
            ),
            "midpoint_family_closed": single_support_family_closed,
        },
        "causal_conclusion": (
            "T113's eleven moving failures are backward-pitch collapses "
            "with clean tracking/rate/saturation/protection checks, but "
            "their first boundary crossings span both feet and the gait "
            "cycle. A one-foot or fixed phase mask is therefore not the "
            "missing mechanism. The fixed hard router remains the best "
            "existing route, yet it is dynamically inconsistent; soft "
            "post-hoc, always-on, and always-on train-through all worsen "
            "it. The untested distinct mechanism is to train the soft "
            "state-dependent router and its expert jointly through the "
            "closed loop."
        ),
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows_read": sum(
                int(item["tick"]) + 1 for item in crossings
            ),
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "t119_cpu_preregistration": passed,
            "training": False,
            "colab": False,
            "behavior_rerun": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T118 routing failure attribution result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Failed moving cells analyzed: `{failed_moving_cells}`\n"
        f"- Support crossings (left/right/both/none): "
        f"`{support_counts.get('10', 0)}/{support_counts.get('01', 0)}/"
        f"{support_counts.get('11', 0)}/{support_counts.get('00', 0)}`\n"
        f"- Occupied phase quadrants: `{quadrants}`\n"
        f"- Routing green cells (hard/soft/always/train-through): "
        f"`{routing['hard_gate']}/{routing['soft_gate']}/"
        f"{routing['always_on']}/{routing['always_on_trainthrough']}`\n"
        "- Simulator / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
