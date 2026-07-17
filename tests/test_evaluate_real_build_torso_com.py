import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_real_build_torso_com", ROOT / "tools/evaluate_real_build_torso_com.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
BREAK_PATH = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"


def complete_measurement(x_body_m: float) -> dict:
    components = []
    for component_id in MODULE.EXPECTED_COMPONENT_IDS:
        components.append(
            {
                "id": component_id,
                "mass_kg": 0.1,
                "mass_uncertainty_kg": 0.0,
                "x_m": x_body_m,
                "x_uncertainty_m": 0.0,
                "source": "synthetic unit-test fixture",
            }
        )
    return {
        "components": components,
        "coordinate_contract": {
            "datum_description": "synthetic trunk origin",
            "datum_origin_x_in_trunk_assembly_m": 0.0,
            "datum_origin_x_uncertainty_m": 0.0,
            "positive_x_description": "synthetic +X",
            "axis_sign_to_trunk_assembly_x": 1,
            "transform_evidence": "synthetic identity transform",
            "unit": "m",
        },
        "schema_version": "real_build_torso_com_measurement.v2",
    }


class RealBuildComEvaluationTest(unittest.TestCase):
    def evaluate(self, data: dict) -> dict:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(data, handle)
            path = Path(handle.name)
        try:
            return MODULE.evaluate(data, path, BREAK_PATH)
        finally:
            path.unlink()

    def test_null_template_holds_without_numeric_estimate(self):
        path = ROOT / "outputs/analysis/real_build_torso_com_measurement_template.json"
        data = json.loads(path.read_text())
        result = MODULE.evaluate(data, path, BREAK_PATH)
        self.assertEqual(result["status"], "HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE")
        self.assertFalse(result["numerical_estimate_reported"])
        self.assertNotIn("estimate", result)

    def test_nominal_sim_match_passes(self):
        result = self.evaluate(complete_measurement(MODULE.SIM_TORSO_X_M))
        self.assertEqual(result["status"], "PASS_REAL_BUILD_COM_INSIDE_CERTIFIED_RADIUS")
        self.assertEqual(result["decision"], "PASS_REAL_BUILD_COM_INSIDE_CERTIFIED_RADIUS")
        self.assertEqual(result["comparison"]["error_interval_m"], [0.0, 0.0])

    def test_positive_outside_holds(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M + 0.005)
        result = self.evaluate(data)
        self.assertEqual(result["status"], "HOLD_REAL_BUILD_COM_OUTSIDE_CERTIFIED_RADIUS")
        self.assertLess(result["comparison"]["positive_clearance_m"], 0.0)

    def test_numeric_transform_is_required(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M)
        data["coordinate_contract"]["axis_sign_to_trunk_assembly_x"] = None
        result = self.evaluate(data)
        self.assertEqual(result["status"], "HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE")
        self.assertIn("coordinate_contract.axis_sign_to_trunk_assembly_x", result["missing_or_invalid_fields"])

    def test_mass_and_position_box_extrema_are_enclosed(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M)
        data["components"][0].update(
            mass_kg=0.2,
            mass_uncertainty_kg=0.01,
            x_m=MODULE.SIM_TORSO_X_M - 0.002,
            x_uncertainty_m=0.0005,
        )
        data["components"][1].update(
            mass_kg=0.05,
            mass_uncertainty_kg=0.005,
            x_m=MODULE.SIM_TORSO_X_M + 0.002,
            x_uncertainty_m=0.00025,
        )
        result = self.evaluate(data)
        lower, upper = result["estimate"]["real_torso_com_interval_x_m"]
        nominal = result["estimate"]["real_torso_com_nominal_x_m"]
        self.assertLessEqual(lower, nominal)
        self.assertLessEqual(nominal, upper)


if __name__ == "__main__":
    unittest.main()
