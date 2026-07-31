#!/usr/bin/env python3
"""Attribute the physical and reporting causes in the Winner-v13 gate HOLD."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FORMAL_RESULT = ANALYSIS / "winner_v13_support_controller_gate_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
OUTPUT = ANALYSIS / "winner_v13_support_controller_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V13_SUPPORT_CONTROLLER_HOLD_ATTRIBUTION_20260721.md"
EXPECTED_RESULT_SHA256 = (
    "350bd845a27bf0257e2569f5bc1027a76f8e0fcb551cffff745cb43068f9ad2a"
)
EXPECTED_FAILURE_COUNTS = {"half": 15, "final": 11}
EXPECTED_FAILED_CONFIGURATION_IDS = [
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "COM_X_NEG",
    "DISCOVERY_03",
    "HELDOUT_04",
    "HELDOUT_09",
]
SOURCES = {
    "builder": Path(
        "tools/build_winner_v13_support_controller_hold_attribution.py"
    ),
    "formal_gate_result": Path(
        "outputs/analysis/winner_v13_support_controller_gate_result.json"
    ),
    "formal_gate_importer": Path(
        "tools/import_winner_v13_support_controller_gate_result.py"
    ),
    "winner_v13_gate_runner": Path(
        "tools/run_winner_v13_support_controller_gate.py"
    ),
    "reviewed_base_gate_runner": Path(
        "tools/run_winner_v12_calibrator_support_gate.py"
    ),
    "support_training_runner": Path(
        "tools/run_winner_v13_support_controller_training.py"
    ),
    "normalized_stage1_result": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"
    ),
    "normalized_training_primitives": Path(
        "patches/winner_v13_normalized_calibrator_training.py"
    ),
    "legacy_training_primitives": Path(
        "patches/winner_v12_calibrator_training.py"
    ),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _assignment_expression(path: Path, function: str, variable: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    target_function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == function
        ),
        None,
    )
    if target_function is None:
        raise ValueError(f"missing {function} in {path}")
    for node in target_function.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == variable
            for target in node.targets
        ):
            return ast.dump(node.value, include_attributes=False)
    raise ValueError(f"missing {function}.{variable} in {path}")


def validate_reporting_path() -> dict[str, Any]:
    gate_source = (ROOT / SOURCES["winner_v13_gate_runner"]).read_text(
        encoding="utf-8"
    )
    training_source = (ROOT / SOURCES["support_training_runner"]).read_text(
        encoding="utf-8"
    )
    base_source = (ROOT / SOURCES["reviewed_base_gate_runner"]).read_text(
        encoding="utf-8"
    )
    normalized_source = (ROOT / SOURCES["normalized_training_primitives"]).read_text(
        encoding="utf-8"
    )
    required = {
        "gate_imports_legacy_coordinate_helper": (
            "import winner_v12_calibrator_training as training_module"
            in gate_source
            and "training = training_module" in gate_source
        ),
        "support_training_imports_legacy_helper": (
            "import winner_v12_calibrator_training as training" in training_source
        ),
        "legacy_gate_treats_prediction_as_raw": (
            "np.square((prediction_np - target) / target_std)" in base_source
        ),
        "stage1_predicts_normalized_coordinates": (
            'target = normalized_target(batch["targets"], target_mean, target_std)'
            in normalized_source
            and "jnp.square(prediction - target)" in normalized_source
        ),
        "gate_action_is_onnx_output_not_predictor_output": (
            'outputs = session.run(' in base_source
            and "action = np.asarray(outputs[0][0]" in base_source
            and "jax_h, prediction = training.response_step(" in base_source
        ),
    }
    if not all(required.values()):
        raise ValueError(f"Winner-v13 reporting-path evidence changed: {required}")
    legacy = ROOT / SOURCES["legacy_training_primitives"]
    normalized = ROOT / SOURCES["normalized_training_primitives"]
    hidden_pre_identical = _assignment_expression(
        legacy, "response_step", "hidden_pre"
    ) == _assignment_expression(normalized, "response_step", "hidden_pre")
    h_out_identical = _assignment_expression(
        legacy, "response_step", "h_out"
    ) == _assignment_expression(normalized, "response_step", "h_out")
    if not hidden_pre_identical or not h_out_identical:
        raise ValueError("Winner-v13 hidden-state path no longer matches v12")
    return {
        **required,
        "legacy_and_normalized_hidden_pre_ast_identical": hidden_pre_identical,
        "legacy_and_normalized_h_out_ast_identical": h_out_identical,
    }


def configuration_index(domain: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    matrix = domain["evaluation_matrix"]
    rows = (
        matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
    )
    index = {row["id"]: row for row in rows}
    if len(index) != len(rows):
        raise ValueError("configuration identifiers are not unique")
    return index


def summarize_checkpoint(
    checkpoint: Mapping[str, Any], configurations: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    cells = (
        checkpoint["core_model_plant_cells"]
        + checkpoint["sensor_transport_plant_cells"]
    )
    failures = [cell for cell in cells if cell["support_pass"] is False]
    label = checkpoint["label"]
    if len(cells) != 124 or len(failures) != EXPECTED_FAILURE_COUNTS[label]:
        raise ValueError(f"Winner-v13 {label} support population changed")
    if any(cell["condition"] is not None for cell in failures):
        raise ValueError(f"Winner-v13 {label} now has sensor/transport failures")
    failed_ids = sorted({cell["configuration_id"] for cell in failures})
    if label == "half" and failed_ids != EXPECTED_FAILED_CONFIGURATION_IDS:
        raise ValueError("Winner-v13 half failure configuration set changed")
    if not set(failed_ids).issubset(EXPECTED_FAILED_CONFIGURATION_IDS):
        raise ValueError(f"Winner-v13 {label} has an unexpected failure configuration")
    x_offsets = {
        cell["configuration_id"]: float(
            configurations[cell["configuration_id"]]["torso_com_offset_m"][0]
        )
        for cell in failures
    }
    if not all(value < 0.0 for value in x_offsets.values()):
        raise ValueError(f"Winner-v13 {label} failure outside negative-X domain")
    failed_terminal_checks = Counter(
        name
        for cell in failures
        for name, passed in cell["terminal"]["checks"].items()
        if not passed
    )
    if failed_terminal_checks != {"roll_pitch": len(failures)}:
        raise ValueError(f"Winner-v13 {label} terminal mechanism changed")
    context = checkpoint["heldout_context_separation"]
    repeats = checkpoint["heldout_repeatability"]
    if (
        len(context) != 16
        or not all(row["separation_above_1e_7"] for row in context)
        or len(repeats) != 32
        or not all(row["bit_exact"] for row in repeats)
    ):
        raise ValueError(f"Winner-v13 {label} context evidence changed")
    return {
        "failure_count": len(failures),
        "failure_configuration_ids": failed_ids,
        "failure_configuration_x_offsets_m": dict(sorted(x_offsets.items())),
        "sensor_transport_failure_count": 0,
        "failed_terminal_checks": dict(failed_terminal_checks),
        "terminal_tick_min": min(cell["terminal"]["tick"] for cell in failures),
        "terminal_tick_max": max(cell["terminal"]["tick"] for cell in failures),
        "terminal_pitch_rad_min": min(
            cell["terminal"]["pitch_rad"] for cell in failures
        ),
        "terminal_pitch_rad_max": max(
            cell["terminal"]["pitch_rad"] for cell in failures
        ),
        "all_16_contexts_separate": True,
        "minimum_context_linf_separation": min(
            row["final_h_out_linf_separation"] for row in context
        ),
        "all_32_repeats_bit_exact": True,
        "legacy_reported_prediction_metrics": checkpoint["heldout_prediction"],
    }


def validate_formal_result(value: Mapping[str, Any]) -> None:
    if (
        sha256(FORMAL_RESULT) != EXPECTED_RESULT_SHA256
        or value.get("schema_version")
        != "winner_v13.support_controller_gate_result.v1"
        or value.get("status") != "HOLD_WINNER_V13_SUPPORT_CONTROLLER_GATE"
        or value.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or value.get("failed_checks") != ["all_248_main_cells_pass"]
        or value.get("execution")
        != {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or [row["label"] for row in value.get("checkpoint_results", [])]
        != ["half", "final"]
    ):
        raise ValueError("formal Winner-v13 gate evidence changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite HOLD attribution: {path}")

    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    validate_formal_result(formal)
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or stage1.get("normalization", {}).get("contact_mean") != [1.0, 1.0]
        or stage1.get("normalization", {}).get("contact_std")
        != [9.999999974752427e-07, 9.999999974752427e-07]
    ):
        raise ValueError("Winner-v13 normalized Stage-1 evidence changed")
    configurations = configuration_index(
        json.loads(DOMAIN.read_text(encoding="utf-8"))
    )
    checkpoints = {
        row["label"]: summarize_checkpoint(row, configurations)
        for row in formal["checkpoint_results"]
    }
    reporting_checks = validate_reporting_path()
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v13.support_controller_hold_attribution.v1",
        "status": "PASS_WINNER_V13_SUPPORT_CONTROLLER_HOLD_ATTRIBUTION",
        "decision": "KEEP_GATE_HOLD_CORRECT_REPORTING_BEFORE_CAUSAL_REPAIR",
        "formal_result": {
            "path": str(FORMAL_RESULT.relative_to(ROOT)).replace("\\", "/"),
            "sha256": EXPECTED_RESULT_SHA256,
            "status": formal["status"],
            "decision": formal["decision"],
        },
        "physical_failure": {
            "classification": "NEGATIVE_X_EARLY_PITCH_INSTABILITY",
            "checkpoint_results": checkpoints,
            "all_failures_have_negative_torso_com_x": True,
            "all_failures_are_roll_pitch_only": True,
            "sensor_transport_failures": 0,
            "formal_hold_remains_outcome_determining": True,
        },
        "reporting_defect": {
            "classification": "NORMALIZED_PREDICTION_MISREAD_AS_RAW_RESPONSE",
            "checks": reporting_checks,
            "legacy_formula": "square((prediction_normalized - target_raw) / target_std)",
            "correct_formula": (
                "square(prediction_normalized - "
                "((target_raw - target_mean) / target_std))"
            ),
            "constant_contact_amplification": {
                "target_raw": [1.0, 1.0],
                "target_mean": [1.0, 1.0],
                "target_std": stage1["normalization"]["contact_std"],
                "correct_normalized_target": [0.0, 0.0],
                "legacy_zero_prediction_squared_error_per_contact": 1.0e12,
                "correct_zero_prediction_squared_error_per_contact": 0.0,
            },
            "outcome_effect": "REPORTING_ONLY_ACTION_AND_PHYSICS_UNCHANGED",
            "formal_predictor_comparison_must_be_recomputed": True,
        },
        "evidence_selected_next_step": {
            "flat_transport_kernel_selected": False,
            "reason_flat_transport_not_selected": (
                "All 16 heldout contexts remain separated at both checkpoints and "
                "physical failures occur by ticks 28-68; no long-range context "
                "collapse is observed."
            ),
            "authorized": (
                "preregister one CPU-only graph-owned calibration-action amplitude "
                "diagnostic using corrected normalized predictor scoring"
            ),
            "not_authorized": [
                "response-conditioned locomotion training",
                "checkpoint selection",
                "runtime deployment",
                "Gate 5",
                "robot or RDK-X5 access",
            ],
        },
        "execution": {
            "new_optimizer_updates": 0,
            "new_behavior_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v13 support-controller HOLD attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Half/final physical failures: `15 / 11`",
                "- Sensor/transport failures: `0`",
                "- New training / behavior / robot access: `0 / 0 / 0`",
                "",
                "The gate remains a real HOLD. Every physical failure is an early",
                "negative-torso-X pitch-limit exit; both checkpoints still preserve all",
                "16 context separations and all 32 heldout repeats exactly.",
                "",
                "Separately, the gate imported the legacy raw-response scoring helper",
                "for a Stage-1 head trained in normalized coordinates. That produces the",
                "~4e10 predictor aggregate, especially from the two constant contact",
                "dimensions. It is reporting-only: ONNX supplies the action, the recurrent",
                "hidden-state equation is identical, and predictor output never enters the",
                "physics path. A versioned scorer must correct this before the next causal",
                "diagnostic; the frozen gate result itself is not rewritten.",
                "",
                "The flat-transport kernel is not selected because context separation",
                "passes and the failures happen by ticks 28-68, not after long-horizon",
                "information decay.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
