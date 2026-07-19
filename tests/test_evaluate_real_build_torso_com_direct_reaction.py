import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_real_build_torso_com_direct_reaction",
    ROOT / "tools/evaluate_real_build_torso_com_direct_reaction.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
BREAK_PATH = ROOT / "outputs/analysis/composite_winner_torso_com_break_radius_result.json"
TEMPLATE_PATH = ROOT / "outputs/analysis/real_build_torso_com_direct_reaction_template.json"


def complete_measurement(x_body_m: float, uncertainty: float = 0.0) -> dict:
    data = json.loads(TEMPLATE_PATH.read_text())
    data["specimen_contract"] = {
        "all_torso_fixed_deployment_components_installed": True,
        "articulated_children_excluded_at_left_right_hip_yaw_and_neck_pitch": True,
        "deployment_configuration_evidence": "synthetic deployment photograph",
        "inventory_attestation": "synthetic complete torso inventory",
        "isolated_specimen_evidence": "synthetic isolation photograph",
        "no_external_load_paths": True,
        "powered_off_and_electrically_disconnected": True,
        "specimen_description": "synthetic complete isolated torso",
    }
    data["coordinate_contract"]["datum_origin_x_uncertainty_m"] = uncertainty
    data["coordinate_contract"]["physical_datum_evidence"] = "synthetic hip-axis datum evidence"
    xa = -0.060
    xb = 0.020
    total_mass = 0.700
    relative_com = x_body_m - MODULE.HIP_AXIS_DATUM_X_M
    rb = total_mass * (relative_com - xa) / (xb - xa)
    ra = total_mass - rb
    data["apparatus"] = {
        "independent_total_mass_evidence": "synthetic independent weighing",
        "independent_total_mass_kg": total_mass,
        "independent_total_mass_uncertainty_kg": uncertainty,
        "scale_a_uncertainty_kg": uncertainty,
        "scale_b_uncertainty_kg": uncertainty,
        "scale_calibration_evidence": "synthetic calibrated scales",
        "support_a_uncertainty_m": uncertainty,
        "support_a_x_relative_to_datum_m": xa,
        "support_b_uncertainty_m": uncertainty,
        "support_b_x_relative_to_datum_m": xb,
        "support_position_evidence": "synthetic support positions",
    }
    for trial in data["trials"]:
        trial["reaction_a_kg"] = ra
        trial["reaction_b_kg"] = rb
        trial["evidence"] = f"synthetic {trial['id']} reading"
    return data


class DirectReactionEvaluationTest(unittest.TestCase):
    def evaluate(self, data: dict) -> dict:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(data, handle)
            path = Path(handle.name)
        try:
            return MODULE.evaluate(data, path, BREAK_PATH)
        finally:
            path.unlink()

    def test_null_template_holds_without_numeric_estimate(self):
        data = json.loads(TEMPLATE_PATH.read_text())
        result = MODULE.evaluate(data, TEMPLATE_PATH, BREAK_PATH)
        self.assertEqual(result["status"], "HOLD_REAL_BUILD_DIRECT_COM_INPUTS_INCOMPLETE")
        self.assertFalse(result["numerical_estimate_reported"])
        self.assertNotIn("estimate", result)

    def test_exact_simulator_match_passes(self):
        result = self.evaluate(complete_measurement(MODULE.SIM_TORSO_X_M))
        self.assertEqual(result["status"], "PASS_REAL_BUILD_DIRECT_COM_INSIDE_CERTIFIED_RADIUS")
        self.assertEqual(result["comparison"]["error_interval_m"], [0.0, 0.0])

    def test_positive_outside_holds(self):
        result = self.evaluate(complete_measurement(MODULE.SIM_TORSO_X_M + 0.005))
        self.assertEqual(result["status"], "HOLD_REAL_BUILD_DIRECT_COM_OUTSIDE_CERTIFIED_RADIUS")
        self.assertLess(result["comparison"]["positive_clearance_m"], 0.0)

    def test_false_specimen_predicate_is_invalid_boundary(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M)
        data["specimen_contract"]["no_external_load_paths"] = False
        result = self.evaluate(data)
        self.assertEqual(result["status"], "INVALID_DIRECT_REACTION_SPECIMEN_BOUNDARY")
        self.assertFalse(result["numerical_estimate_reported"])

    def test_reaction_total_mass_mismatch_is_invalid(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M)
        data["apparatus"]["independent_total_mass_kg"] = 0.800
        result = self.evaluate(data)
        self.assertEqual(result["status"], "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY")
        self.assertIn("trials[0].reaction_sum_total_mass_overlap", result["issues"])

    def test_nonoverlapping_trial_com_intervals_are_invalid(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M, uncertainty=0.0001)
        data["trials"][2]["reaction_a_kg"] -= 0.030
        data["trials"][2]["reaction_b_kg"] += 0.030
        result = self.evaluate(data)
        self.assertEqual(result["status"], "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY")
        self.assertEqual(result["issues"], ["trials.real_torso_com_intervals_nonempty_intersection"])

    def test_short_support_interval_is_invalid(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M)
        data["apparatus"]["support_b_x_relative_to_datum_m"] = -0.001
        result = self.evaluate(data)
        self.assertEqual(result["status"], "INVALID_DIRECT_REACTION_MEASUREMENT_CONSISTENCY")
        self.assertIn("apparatus.minimum_support_interval_separation", result["issues"])

    def test_uncertainty_vertices_enclose_nominal(self):
        data = complete_measurement(MODULE.SIM_TORSO_X_M, uncertainty=0.0001)
        result = self.evaluate(data)
        lower, upper = result["estimate"]["real_torso_com_interval_x_m"]
        nominal = result["estimate"]["real_torso_com_nominal_x_m"]
        self.assertLess(lower, nominal)
        self.assertLess(nominal, upper)


if __name__ == "__main__":
    unittest.main()
