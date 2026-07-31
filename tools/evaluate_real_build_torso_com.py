#!/usr/bin/env python3
"""Validate measured torso inputs and apply the frozen real-build COM rule."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs/analysis/real_build_torso_com_measurement_template.json"
DEFAULT_BREAK_RESULT = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
SIM_TORSO_X_M = -0.04832589998841286
EXPECTED_COMPONENT_IDS = (
    "printed_torso_and_fasteners",
    "rdk_x5_board",
    "rdk_x5_thermal_and_mount",
    "rdk_x5_cables_and_adapters",
    "battery_cells_pack",
    "battery_bms_charger_wiring",
    "servo_bus_imu_power_hardware",
    "build_specific_covers_or_ballast",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _missing_or_invalid(measurement: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if measurement.get("schema_version") != "real_build_torso_com_measurement.v2":
        issues.append("schema_version")

    components = measurement.get("components")
    if not isinstance(components, list):
        return issues + ["components"]
    ids = [item.get("id") for item in components if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append("components.ids_or_order")

    numeric_fields = ("mass_kg", "mass_uncertainty_kg", "x_m", "x_uncertainty_m")
    for index, component in enumerate(components):
        prefix = f"components[{index}]"
        if not isinstance(component, dict):
            issues.append(prefix)
            continue
        for field in numeric_fields:
            if not _finite_number(component.get(field)):
                issues.append(f"{prefix}.{field}")
        source = component.get("source")
        if not isinstance(source, str) or not source.strip():
            issues.append(f"{prefix}.source")
        if all(_finite_number(component.get(field)) for field in numeric_fields):
            mass = float(component["mass_kg"])
            dm = float(component["mass_uncertainty_kg"])
            dx = float(component["x_uncertainty_m"])
            if mass < 0.0:
                issues.append(f"{prefix}.mass_kg_nonnegative")
            if dm < 0.0 or dm > mass:
                issues.append(f"{prefix}.mass_uncertainty_bounds")
            if dx < 0.0:
                issues.append(f"{prefix}.x_uncertainty_m_nonnegative")

    coordinate = measurement.get("coordinate_contract")
    if not isinstance(coordinate, dict):
        return issues + ["coordinate_contract"]
    for field in ("datum_description", "positive_x_description", "transform_evidence"):
        value = coordinate.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"coordinate_contract.{field}")
    for field in ("datum_origin_x_in_trunk_assembly_m", "datum_origin_x_uncertainty_m"):
        if not _finite_number(coordinate.get(field)):
            issues.append(f"coordinate_contract.{field}")
    if coordinate.get("axis_sign_to_trunk_assembly_x") not in (-1, 1):
        issues.append("coordinate_contract.axis_sign_to_trunk_assembly_x")
    if coordinate.get("unit") != "m":
        issues.append("coordinate_contract.unit")
    if _finite_number(coordinate.get("datum_origin_x_uncertainty_m")) and float(
        coordinate["datum_origin_x_uncertainty_m"]
    ) < 0.0:
        issues.append("coordinate_contract.datum_origin_x_uncertainty_m_nonnegative")

    if not issues:
        minimum_total_mass = sum(
            float(item["mass_kg"]) - float(item["mass_uncertainty_kg"])
            for item in components
        )
        if minimum_total_mass <= 0.0:
            issues.append("components.minimum_total_mass_positive")
    return sorted(set(issues))


def _weighted_extreme(mass_bounds: list[tuple[float, float]], x_values: list[float], want_min: bool) -> float:
    candidates: list[float] = []
    for choices in itertools.product((0, 1), repeat=len(mass_bounds)):
        masses = [bounds[choice] for bounds, choice in zip(mass_bounds, choices)]
        total = sum(masses)
        if total > 0.0:
            candidates.append(sum(mass * x for mass, x in zip(masses, x_values)) / total)
    if not candidates:
        raise ValueError("mass uncertainty box contains no positive-total-mass vertex")
    return min(candidates) if want_min else max(candidates)


def _load_break_contract(path: Path) -> dict[str, float]:
    result = json.loads(path.read_text())
    if result.get("status") != "PASS_COM_BREAK_RADIUS_BRACKETED" or result.get("failed_checks") != []:
        raise ValueError("break-radius result is not a valid passing artifact")
    bounds = result.get("bounds", {})
    negative = bounds.get("negative", {})
    positive = bounds.get("positive", {})
    negative_inner = float(negative["certified_inner_pass_m"])
    positive_inner = float(positive["certified_inner_pass_m"])
    negative_width = float(negative["bracket_width_m"])
    positive_width = float(positive["bracket_width_m"])
    if not math.isclose(negative_width, 0.00078125, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("unexpected negative break-radius resolution")
    if not math.isclose(positive_width, 0.00078125, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("unexpected positive break-radius resolution")
    return {
        "negative_inner_m": negative_inner,
        "positive_inner_m": positive_inner,
        "margin_m": 0.00078125,
        "allowed_error_lower_m": negative_inner + 0.00078125,
        "allowed_error_upper_m": positive_inner - 0.00078125,
    }


def evaluate(measurement: dict[str, Any], input_path: Path, break_path: Path) -> dict[str, Any]:
    break_contract = _load_break_contract(break_path)
    issues = _missing_or_invalid(measurement)
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
        "schema_version": "real_build_torso_com_result.v1",
    }
    if issues:
        return {
            **base,
            "decision": "MEASURE_BUILD_SPECIFIC_MASS_AND_X_PLACEMENT",
            "missing_or_invalid_fields": issues,
            "numerical_estimate_reported": False,
            "status": "HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE",
        }

    components = measurement["components"]
    coordinate = measurement["coordinate_contract"]
    sign = int(coordinate["axis_sign_to_trunk_assembly_x"])
    datum = float(coordinate["datum_origin_x_in_trunk_assembly_m"])
    datum_uncertainty = float(coordinate["datum_origin_x_uncertainty_m"])
    mass_bounds: list[tuple[float, float]] = []
    relative_lows: list[float] = []
    relative_highs: list[float] = []
    nominal_mass = 0.0
    nominal_moment = 0.0
    for component in components:
        mass = float(component["mass_kg"])
        dm = float(component["mass_uncertainty_kg"])
        x = float(component["x_m"])
        dx = float(component["x_uncertainty_m"])
        transformed = sorted((sign * (x - dx), sign * (x + dx)))
        mass_bounds.append((mass - dm, mass + dm))
        relative_lows.append(transformed[0])
        relative_highs.append(transformed[1])
        nominal_mass += mass
        nominal_moment += mass * (datum + sign * x)

    real_lower = datum - datum_uncertainty + _weighted_extreme(mass_bounds, relative_lows, True)
    real_upper = datum + datum_uncertainty + _weighted_extreme(mass_bounds, relative_highs, False)
    real_nominal = nominal_moment / nominal_mass
    error_lower = real_lower - SIM_TORSO_X_M
    error_upper = real_upper - SIM_TORSO_X_M
    inside = (
        error_lower >= break_contract["allowed_error_lower_m"]
        and error_upper <= break_contract["allowed_error_upper_m"]
    )
    return {
        **base,
        "comparison": {
            "complete_interval_inside_with_margin": inside,
            "error_interval_m": [error_lower, error_upper],
            "negative_clearance_m": error_lower - break_contract["allowed_error_lower_m"],
            "positive_clearance_m": break_contract["allowed_error_upper_m"] - error_upper,
            "sim_torso_ipos_x_m": SIM_TORSO_X_M,
        },
        "decision": (
            "PASS_REAL_BUILD_COM_INSIDE_CERTIFIED_RADIUS"
            if inside
            else "HOLD_REAL_BUILD_COM_OUTSIDE_CERTIFIED_RADIUS"
        ),
        "estimate": {
            "real_torso_com_interval_x_m": [real_lower, real_upper],
            "real_torso_com_nominal_x_m": real_nominal,
            "total_nominal_mass_kg": nominal_mass,
        },
        "missing_or_invalid_fields": [],
        "numerical_estimate_reported": True,
        "status": (
            "PASS_REAL_BUILD_COM_INSIDE_CERTIFIED_RADIUS"
            if inside
            else "HOLD_REAL_BUILD_COM_OUTSIDE_CERTIFIED_RADIUS"
        ),
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
