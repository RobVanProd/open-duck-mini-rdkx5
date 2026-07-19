#!/usr/bin/env python3
"""Evaluate a direct two-support measurement of the as-built torso X COM."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_template.json"
DEFAULT_BREAK_RESULT = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
SIM_TORSO_X_M = -0.04832589998841286
HIP_AXIS_DATUM_X_M = -0.019
MIN_SUPPORT_INTERVAL_SEPARATION_M = 0.060
FORMAL_TRIAL_IDS = ("trial_1", "trial_2", "trial_3")
EXPECTED_PROVENANCE = {
    "break_radius_result_sha256": "6b84b34e7280b0f0d92109a70444d18af7b0196cd3555530b8f42e70dea54e32",
    "open_duck_mini_commit": "b23317a485b3cec7d8417f352478778b3475173c",
    "sim_xml_sha256": "968b18de4e3f55b31252155f52779fa490989f5da92bc9b308e0bb4e81d6bb5c",
    "urdf_sha256": "a42c5ff3213b4662d81708807d698ab63d4e7432a54b4112728969d45928b54b",
}
EXPECTED_DATUM_DESCRIPTION = "midpoint of the left and right hip-yaw rotation axes"
EXPECTED_POSITIVE_X = "robot forward/toe direction at deterministic home"
SPECIMEN_PREDICATES = (
    "all_torso_fixed_deployment_components_installed",
    "articulated_children_excluded_at_left_right_hip_yaw_and_neck_pitch",
    "no_external_load_paths",
    "powered_off_and_electrically_disconnected",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load_break_contract(path: Path) -> dict[str, float]:
    if sha256_file(path) != EXPECTED_PROVENANCE["break_radius_result_sha256"]:
        raise ValueError("break-radius result SHA-256 differs from preregistration")
    result = json.loads(path.read_text())
    if result.get("status") != "PASS_COM_BREAK_RADIUS_BRACKETED" or result.get("failed_checks") != []:
        raise ValueError("break-radius result is not a valid passing artifact")
    negative = result["bounds"]["negative"]
    positive = result["bounds"]["positive"]
    margin = 0.00078125
    if not math.isclose(float(negative["bracket_width_m"]), margin, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("unexpected negative break-radius resolution")
    if not math.isclose(float(positive["bracket_width_m"]), margin, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("unexpected positive break-radius resolution")
    return {
        "allowed_error_lower_m": float(negative["certified_inner_pass_m"]) + margin,
        "allowed_error_upper_m": float(positive["certified_inner_pass_m"]) - margin,
        "margin_m": margin,
    }


def _missing_fields(measurement: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if measurement.get("schema_version") != "real_build_torso_com_direct_reaction_measurement.v1":
        missing.append("schema_version")

    provenance = measurement.get("provenance")
    if not isinstance(provenance, dict):
        missing.append("provenance")
    else:
        for field in EXPECTED_PROVENANCE:
            if not _nonempty_string(provenance.get(field)):
                missing.append(f"provenance.{field}")

    specimen = measurement.get("specimen_contract")
    if not isinstance(specimen, dict):
        missing.append("specimen_contract")
    else:
        for field in SPECIMEN_PREDICATES:
            if not isinstance(specimen.get(field), bool):
                missing.append(f"specimen_contract.{field}")
        for field in (
            "specimen_description",
            "deployment_configuration_evidence",
            "isolated_specimen_evidence",
            "inventory_attestation",
        ):
            if not _nonempty_string(specimen.get(field)):
                missing.append(f"specimen_contract.{field}")

    coordinate = measurement.get("coordinate_contract")
    if not isinstance(coordinate, dict):
        missing.append("coordinate_contract")
    else:
        for field in ("datum_description", "positive_x_description", "physical_datum_evidence"):
            if not _nonempty_string(coordinate.get(field)):
                missing.append(f"coordinate_contract.{field}")
        for field in ("datum_origin_x_in_trunk_assembly_m", "datum_origin_x_uncertainty_m"):
            if not _finite_number(coordinate.get(field)):
                missing.append(f"coordinate_contract.{field}")
        if coordinate.get("axis_sign_to_trunk_assembly_x") not in (-1, 1):
            missing.append("coordinate_contract.axis_sign_to_trunk_assembly_x")

    apparatus = measurement.get("apparatus")
    if not isinstance(apparatus, dict):
        missing.append("apparatus")
    else:
        for field in (
            "support_a_x_relative_to_datum_m",
            "support_a_uncertainty_m",
            "support_b_x_relative_to_datum_m",
            "support_b_uncertainty_m",
            "scale_a_uncertainty_kg",
            "scale_b_uncertainty_kg",
            "independent_total_mass_kg",
            "independent_total_mass_uncertainty_kg",
        ):
            if not _finite_number(apparatus.get(field)):
                missing.append(f"apparatus.{field}")
        for field in (
            "support_position_evidence",
            "scale_calibration_evidence",
            "independent_total_mass_evidence",
        ):
            if not _nonempty_string(apparatus.get(field)):
                missing.append(f"apparatus.{field}")

    trials = measurement.get("trials")
    if not isinstance(trials, list) or len(trials) != len(FORMAL_TRIAL_IDS):
        missing.append("trials")
    else:
        for index, trial in enumerate(trials):
            prefix = f"trials[{index}]"
            if not isinstance(trial, dict):
                missing.append(prefix)
                continue
            if trial.get("id") != FORMAL_TRIAL_IDS[index]:
                missing.append(f"{prefix}.id")
            for field in ("reaction_a_kg", "reaction_b_kg"):
                if not _finite_number(trial.get(field)):
                    missing.append(f"{prefix}.{field}")
            if not _nonempty_string(trial.get("evidence")):
                missing.append(f"{prefix}.evidence")
    return sorted(set(missing))


def _provenance_or_boundary_issues(measurement: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    provenance = measurement["provenance"]
    for field, expected in EXPECTED_PROVENANCE.items():
        if provenance.get(field) != expected:
            issues.append(f"provenance.{field}_exact")

    coordinate = measurement["coordinate_contract"]
    if coordinate["datum_description"] != EXPECTED_DATUM_DESCRIPTION:
        issues.append("coordinate_contract.datum_description_exact")
    if not math.isclose(
        float(coordinate["datum_origin_x_in_trunk_assembly_m"]),
        HIP_AXIS_DATUM_X_M,
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        issues.append("coordinate_contract.datum_origin_exact")
    if coordinate["axis_sign_to_trunk_assembly_x"] != 1:
        issues.append("coordinate_contract.axis_sign_exact")
    if coordinate["positive_x_description"] != EXPECTED_POSITIVE_X:
        issues.append("coordinate_contract.positive_x_description_exact")

    specimen = measurement["specimen_contract"]
    for field in SPECIMEN_PREDICATES:
        if specimen[field] is not True:
            issues.append(f"specimen_contract.{field}_true")
    return sorted(issues)


def _measurement_issues(measurement: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    coordinate = measurement["coordinate_contract"]
    datum_uncertainty = float(coordinate["datum_origin_x_uncertainty_m"])
    if datum_uncertainty < 0.0:
        issues.append("coordinate_contract.datum_origin_x_uncertainty_m_nonnegative")

    apparatus = measurement["apparatus"]
    xa = float(apparatus["support_a_x_relative_to_datum_m"])
    dxa = float(apparatus["support_a_uncertainty_m"])
    xb = float(apparatus["support_b_x_relative_to_datum_m"])
    dxb = float(apparatus["support_b_uncertainty_m"])
    dma = float(apparatus["scale_a_uncertainty_kg"])
    dmb = float(apparatus["scale_b_uncertainty_kg"])
    total_mass = float(apparatus["independent_total_mass_kg"])
    total_dm = float(apparatus["independent_total_mass_uncertainty_kg"])
    for field, value in (
        ("support_a_uncertainty_m", dxa),
        ("support_b_uncertainty_m", dxb),
        ("scale_a_uncertainty_kg", dma),
        ("scale_b_uncertainty_kg", dmb),
        ("independent_total_mass_uncertainty_kg", total_dm),
    ):
        if value < 0.0:
            issues.append(f"apparatus.{field}_nonnegative")
    if total_mass <= 0.0 or total_dm >= total_mass:
        issues.append("apparatus.independent_total_mass_positive_interval")
    if (xb - dxb) - (xa + dxa) < MIN_SUPPORT_INTERVAL_SEPARATION_M:
        issues.append("apparatus.minimum_support_interval_separation")

    if not issues:
        total_interval = (total_mass - total_dm, total_mass + total_dm)
        for index, trial in enumerate(measurement["trials"]):
            ra = float(trial["reaction_a_kg"])
            rb = float(trial["reaction_b_kg"])
            if ra - dma <= 0.0:
                issues.append(f"trials[{index}].reaction_a_positive_interval")
            if rb - dmb <= 0.0:
                issues.append(f"trials[{index}].reaction_b_positive_interval")
            reaction_sum = (ra - dma + rb - dmb, ra + dma + rb + dmb)
            if reaction_sum[1] < total_interval[0] or total_interval[1] < reaction_sum[0]:
                issues.append(f"trials[{index}].reaction_sum_total_mass_overlap")
    return sorted(issues)


def _trial_interval(
    xa: float,
    dxa: float,
    xb: float,
    dxb: float,
    ra: float,
    dma: float,
    rb: float,
    dmb: float,
    datum: float,
    datum_uncertainty: float,
) -> tuple[float, float, float]:
    candidates: list[float] = []
    for xa_v, xb_v, ra_v, rb_v in itertools.product(
        (xa - dxa, xa + dxa),
        (xb - dxb, xb + dxb),
        (ra - dma, ra + dma),
        (rb - dmb, rb + dmb),
    ):
        total = ra_v + rb_v
        if total <= 0.0:
            raise ValueError("reaction uncertainty box contains nonpositive total load")
        candidates.append((ra_v * xa_v + rb_v * xb_v) / total)
    nominal_rel = (ra * xa + rb * xb) / (ra + rb)
    return (
        datum - datum_uncertainty + min(candidates),
        datum + datum_uncertainty + max(candidates),
        datum + nominal_rel,
    )


def evaluate(measurement: dict[str, Any], input_path: Path, break_path: Path) -> dict[str, Any]:
    break_contract = _load_break_contract(break_path)
    base: dict[str, Any] = {
        "authority": {
            "gate5_deployment_robot_rdk": False,
            "model_correction": False,
            "training_gpu_igpu_hosted": False,
        },
        "break_radius_contract": {
            **break_contract,
            "path": str(break_path),
            "sha256": sha256_file(break_path),
        },
        "input": {"path": str(input_path), "sha256": sha256_file(input_path)},
        "schema_version": "real_build_torso_com_direct_reaction_result.v1",
    }

    missing = _missing_fields(measurement)
    if missing:
        return {
            **base,
            "decision": "HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE",
            "issues": missing,
            "numerical_estimate_reported": False,
            "status": "HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE",
        }

    boundary_issues = _provenance_or_boundary_issues(measurement)
    if boundary_issues:
        return {
            **base,
            "decision": "INVALID_DIRECT_REACTION_SPECIMEN_BOUNDARY",
            "issues": boundary_issues,
            "numerical_estimate_reported": False,
            "status": "INVALID_DIRECT_REACTION_SPECIMEN_BOUNDARY",
        }

    measurement_issues = _measurement_issues(measurement)
    if measurement_issues:
        return {
            **base,
            "decision": "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY",
            "issues": measurement_issues,
            "numerical_estimate_reported": False,
            "status": "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY",
        }

    coordinate = measurement["coordinate_contract"]
    apparatus = measurement["apparatus"]
    xa = float(apparatus["support_a_x_relative_to_datum_m"])
    dxa = float(apparatus["support_a_uncertainty_m"])
    xb = float(apparatus["support_b_x_relative_to_datum_m"])
    dxb = float(apparatus["support_b_uncertainty_m"])
    dma = float(apparatus["scale_a_uncertainty_kg"])
    dmb = float(apparatus["scale_b_uncertainty_kg"])
    datum = float(coordinate["datum_origin_x_in_trunk_assembly_m"])
    datum_uncertainty = float(coordinate["datum_origin_x_uncertainty_m"])

    trial_rows: list[dict[str, Any]] = []
    for trial in measurement["trials"]:
        ra = float(trial["reaction_a_kg"])
        rb = float(trial["reaction_b_kg"])
        low, high, nominal = _trial_interval(
            xa, dxa, xb, dxb, ra, dma, rb, dmb, datum, datum_uncertainty
        )
        trial_rows.append(
            {
                "id": trial["id"],
                "real_torso_com_interval_x_m": [low, high],
                "real_torso_com_nominal_x_m": nominal,
                "reaction_sum_kg": ra + rb,
            }
        )

    intersection = [
        max(row["real_torso_com_interval_x_m"][0] for row in trial_rows),
        min(row["real_torso_com_interval_x_m"][1] for row in trial_rows),
    ]
    if intersection[0] > intersection[1]:
        return {
            **base,
            "decision": "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY",
            "issues": ["trials.real_torso_com_intervals_nonempty_intersection"],
            "numerical_estimate_reported": False,
            "status": "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY",
        }

    real_interval = [
        min(row["real_torso_com_interval_x_m"][0] for row in trial_rows),
        max(row["real_torso_com_interval_x_m"][1] for row in trial_rows),
    ]
    real_nominal = sum(row["real_torso_com_nominal_x_m"] for row in trial_rows) / len(trial_rows)
    error_interval = [real_interval[0] - SIM_TORSO_X_M, real_interval[1] - SIM_TORSO_X_M]
    inside = (
        error_interval[0] >= break_contract["allowed_error_lower_m"]
        and error_interval[1] <= break_contract["allowed_error_upper_m"]
    )
    status = (
        "PASS_REAL_BUILD_DIRECT_COM_INSIDE_CERTIFIED_RADIUS"
        if inside
        else "HOLD_REAL_BUILD_DIRECT_COM_OUTSIDE_CERTIFIED_RADIUS"
    )
    return {
        **base,
        "comparison": {
            "complete_interval_inside_with_margin": inside,
            "error_interval_m": error_interval,
            "negative_clearance_m": error_interval[0] - break_contract["allowed_error_lower_m"],
            "positive_clearance_m": break_contract["allowed_error_upper_m"] - error_interval[1],
            "sim_torso_ipos_x_m": SIM_TORSO_X_M,
        },
        "decision": status,
        "estimate": {
            "real_torso_com_interval_x_m": real_interval,
            "real_torso_com_nominal_x_m": real_nominal,
            "trial_interval_intersection_x_m": intersection,
            "trial_results": trial_rows,
        },
        "issues": [],
        "numerical_estimate_reported": True,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--break-result", type=Path, default=DEFAULT_BREAK_RESULT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    measurement = json.loads(args.input.read_text())
    result = evaluate(measurement, args.input.resolve(), args.break_result.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
