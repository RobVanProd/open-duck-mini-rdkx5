import argparse
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


PATH = Path(__file__).resolve().parents[1] / "tools" / "train_phase_modulated_bc_student.py"
sys.path.insert(0, str(PATH.parent))
SPEC = importlib.util.spec_from_file_location("phase_student", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PhaseRateObjectiveTest(unittest.TestCase):
    def test_parse_phase_rate_spec_is_bilateral_and_exact(self):
        mask = MODULE.parse_phase_rate_spec("2=1|2,3=0|1,11=5|6,12=4|5", 14)
        self.assertEqual(mask.sum(), 8)
        self.assertEqual(mask[1, 2], mask[2, 2])
        self.assertEqual(mask[0, 3], mask[1, 3])
        self.assertEqual(mask[5, 11], mask[6, 11])
        self.assertEqual(mask[4, 12], mask[5, 12])

    def test_phase_pair_mask_uses_newer_sample_phase(self):
        obs = np.zeros((3, 101), dtype=np.float32)
        obs[1, 99:101] = [1.0, 0.0]  # bin 0
        obs[2, 99:101] = [0.0, 1.0]  # bin 2
        pairs = np.array([[0, 1], [1, 2]], dtype=np.int64)
        mask = MODULE.phase_rate_pair_mask(obs, pairs, "3=0,2=2")
        self.assertEqual(mask[0, 3], 1)
        self.assertEqual(mask[0].sum(), 1)
        self.assertEqual(mask[1, 2], 1)
        self.assertEqual(mask[1].sum(), 1)

    def test_invalid_phase_rate_spec_fails_closed(self):
        for spec in ("3", "14=0", "3=8"):
            with self.subTest(spec=spec), self.assertRaises((argparse.ArgumentTypeError, ValueError)):
                MODULE.parse_phase_rate_spec(spec, 14)

    def test_per_joint_rate_limits_are_exact_and_fail_closed(self):
        values = MODULE.parse_rate_limits("1,2,3", 3, 9.0)
        np.testing.assert_array_equal(values, [1, 2, 3])
        np.testing.assert_array_equal(MODULE.parse_rate_limits("", 3, 9.0), [9, 9, 9])
        for text in ("1,2", "1,0,3", "1,nan,3"):
            with self.subTest(text=text), self.assertRaises(argparse.ArgumentTypeError):
                MODULE.parse_rate_limits(text, 3, 9.0)


if __name__ == "__main__":
    unittest.main()
