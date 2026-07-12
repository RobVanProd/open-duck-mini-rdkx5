import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "runtime/scripts/fixed_target_gain_ab.py"
)
spec = importlib.util.spec_from_file_location("fixed_target_gain_ab", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FakeHWI:
    joints = {
        "left_hip_yaw": 20,
        "left_hip_roll": 21,
        "left_hip_pitch": 22,
        "left_knee": 23,
        "left_ankle": 24,
        "neck_pitch": 30,
        "head_pitch": 31,
        "head_yaw": 32,
        "head_roll": 33,
        "right_hip_yaw": 10,
        "right_hip_roll": 11,
        "right_hip_pitch": 12,
        "right_knee": 13,
        "right_ankle": 14,
    }


class FixedTargetGainContractTest(unittest.TestCase):
    def test_only_preregistered_gains_change(self):
        normal = module.runtime_gains(FakeHWI(), {})
        trial = module.runtime_gains(
            FakeHWI(), {"left_hip_pitch": 31.0, "left_knee": 34.0}
        )

        self.assertEqual(normal, [30, 30, 30, 30, 30, 8, 8, 8, 8, 30, 30, 30, 30, 30])
        changed = [(index, before, after) for index, (before, after) in enumerate(zip(normal, trial)) if before != after]
        self.assertEqual(changed, [(2, 30.0, 31.0), (3, 30.0, 34.0)])


if __name__ == "__main__":
    unittest.main()
