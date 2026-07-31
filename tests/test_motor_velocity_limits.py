import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "runtime/scripts/motor_velocity_limits.py"
SPEC = importlib.util.spec_from_file_location("motor_velocity_limits", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MotorVelocityLimitsTest(unittest.TestCase):
    def test_default_is_off(self):
        self.assertIsNone(MODULE.parse_motor_velocity_limits(None))

    def test_exact_vector_is_preserved(self):
        text = "5.24,5.24,1.5,1.5,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.0,1.25"
        self.assertEqual(MODULE.parse_motor_velocity_limits(text)[2:5], [1.5, 1.5, 1.75])
        self.assertEqual(MODULE.parse_motor_velocity_limits(text)[11:14], [1.25, 1.0, 1.25])

    def test_invalid_vectors_fail_closed(self):
        for value in ("1,2", [1.0] * 13 + [0.0], [1.0] * 13 + [float("nan")]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.parse_motor_velocity_limits(value)


if __name__ == "__main__":
    unittest.main()
