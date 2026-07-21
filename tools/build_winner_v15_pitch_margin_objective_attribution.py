#!/usr/bin/env python3
"""Attribute Winner-v14 HOLD and select one bounded support-objective repair."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v14_support_action_diagnostic_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SMOKE = ROOT / "tools/run_winner_v12_calibrator_cpu_smoke.py"
OUTPUT = ANALYSIS / "winner_v15_pitch_margin_objective_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION_20260721.md"


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    if (
        result.get("status") != "PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC"
        or result.get("decision")
        != "NO_SCALE_PASSES_PREREGISTER_SUPPORT_OBJECTIVE_REPAIR"
        or result.get("passing_scales") != []
        or result.get("selected_scale") is not None
        or result.get("failed_validity_checks") != []
        or not all(result.get("validity_checks", {}).values())
    ):
        raise ValueError("Winner-v14 diagnostic does not select objective attribution")
    scale_summary = result["scale_summary"]
    if [row["scale"] for row in scale_summary] != [0.0, 0.25, 0.5, 0.75, 1.0]:
        raise ValueError("Winner-v14 diagnostic scale population changed")
    training_ids = {
        row["id"]
        for row in domain["evaluation_matrix"]["fixed_anchors"]
        + domain["evaluation_matrix"]["discovery_samples"]
    }
    failure_sets = []
    terminal_checks: Counter[str] = Counter()
    tick_min = 250
    tick_max = -1
    pitch_min = float("inf")
    pitch_max = float("-inf")
    nonzero_context_pass = True
    predictor_pass = True
    repeat_pass = True
    bound_pass = True
    for scale_row in scale_summary:
        for checkpoint in scale_row["checkpoint_results"]:
            failure_sets.append(set(checkpoint["support_failure_configuration_counts"]))
            terminal_checks.update(checkpoint["terminal_failed_check_counts"])
            tick_min = min(tick_min, checkpoint["failure_tick_range"][0])
            tick_max = max(tick_max, checkpoint["failure_tick_range"][1])
            pitch_min = min(pitch_min, checkpoint["failure_pitch_rad_range"][0])
            pitch_max = max(pitch_max, checkpoint["failure_pitch_rad_range"][1])
            checks = checkpoint["checks"]
            if scale_row["scale"] > 0.0:
                nonzero_context_pass &= checks["all_16_heldout_contexts_separate"]
            predictor_pass &= checks["corrected_prediction_beats_constant_per_plant"]
            repeat_pass &= checks["all_32_heldout_repeats_bit_exact"]
            bound_pass &= checks["all_action_deltas_within_graph_bounds"]
    persistent_failures = sorted(set.intersection(*failure_sets))
    persistent_training_failures = sorted(set(persistent_failures) & training_ids)
    if (
        persistent_failures
        != ["COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG", "DISCOVERY_03", "HELDOUT_09"]
        or persistent_training_failures
        != ["COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG", "DISCOVERY_03"]
        or set(terminal_checks) != {"roll_pitch"}
        or not all((nonzero_context_pass, predictor_pass, repeat_pass, bound_pass))
    ):
        raise ValueError("Winner-v14 failure attribution changed")
    smoke_source = SMOKE.read_text(encoding="utf-8")
    if (
        "MAXIMUM_ABS_TILT_RAD = 0.35" not in smoke_source
        or "TERMINAL_BONUS = 250.0" not in smoke_source
        or "rewards[environment, tick] = 1.0" not in smoke_source
    ):
        raise ValueError("reviewed support reward changed")
    payload: dict[str, Any] = {
        "schema_version": "winner_v15.pitch_margin_objective_attribution.v1",
        "status": "PASS_WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION",
        "decision": "PREREGISTER_ONE_SIDED_NEGATIVE_PITCH_MARGIN_CPU_CONTRACT",
        "diagnosis": {
            "all_five_scales_failed": True,
            "persistent_failure_configurations": persistent_failures,
            "persistent_failures_present_in_training_population": persistent_training_failures,
            "terminal_failed_check_counts": dict(terminal_checks),
            "failure_tick_range": [tick_min, tick_max],
            "failure_pitch_rad_range": [pitch_min, pitch_max],
            "all_nonzero_scales_preserve_heldout_context": nonzero_context_pass,
            "corrected_predictor_beats_constant_at_every_scale_checkpoint": predictor_pass,
            "all_repeats_bit_exact": repeat_pass,
            "all_action_deltas_within_graph_bounds": bound_pass,
            "causal_interpretation": (
                "The action head receives stable, distinct response context and stays "
                "within its graph bounds, yet repeatedly crosses only the negative-pitch "
                "support boundary within 28-71 ticks, including four configurations used "
                "during training. Fixed inference amplitude and information transport are "
                "not selected causes; the sparse alive/terminal support objective is."
            ),
        },
        "reviewed_source_objective": {
            "valid_transition_reward": 1.0,
            "failure_transition_reward": 0.0,
            "settled_terminal_bonus": 250.0,
            "pitch_boundary_rad": 0.35,
        },
        "selected_single_change": {
            "scope": "training reward only; observation, action, graph, plant, population, seeds, and gates unchanged",
            "valid_transition_reward": (
                "1 - square(clip(max(0, -next_pitch_rad) / 0.35, 0, 1))"
            ),
            "failure_transition_reward": 0.0,
            "settled_terminal_bonus": 250.0,
            "why_no_tunable_scale": (
                "The penalty is dimensionless, normalized by the existing frozen 0.35-rad "
                "failure boundary, and bounded in [0,1], exactly the original alive-reward range."
            ),
            "source_checkpoint": "restart from the exact passing Winner-v13 Stage-1 snapshot; do not continue failed Stage-2 weights",
        },
        "deferred_architecture": {
            "flat_long_range_kernel": "not selected",
            "reason": (
                "Every nonzero scale preserves all 16 heldout contexts and failures occur "
                "within 28-71 ticks, so evidence does not identify long-range transport."
            ),
        },
        "sources": {
            "winner_v14_import_lf_sha256": lf_sha256(RESULT),
            "configuration_domain_lf_sha256": lf_sha256(DOMAIN),
            "reviewed_smoke_lf_sha256": lf_sha256(SMOKE),
        },
        "execution_now": {
            "optimizer_updates": 0,
            "support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "support_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": "one separately frozen CPU mechanics contract",
        },
    }
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v15 pitch-margin objective attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Persistent failures: `{', '.join(persistent_failures)}`",
                f"- Failure ticks / pitch: `{tick_min}-{tick_max}` / `{pitch_min:.6f}-{pitch_max:.6f} rad`",
                "- Training / locomotion / robot access: `0 / 0 / 0`",
                "",
                "All five fixed action scales fail. Every nonzero scale retains distinct",
                "response context, corrected prediction, exact repeats, and graph bounds.",
                "The common failure is early negative pitch, including four configurations",
                "already in the training population. This selects one bounded training-only",
                "reward change: replace the flat valid-transition reward with normalized",
                "one-sided negative-pitch margin. No coefficient search is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
