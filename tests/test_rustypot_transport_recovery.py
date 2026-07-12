import importlib.util
import sys
import types
import unittest
import weakref
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py"
)


class FakeIO:
    def __init__(self, generation, fail_first=False):
        self.generation = generation
        self.fail_first = fail_first
        self.calls = 0

    def read_present_position(self, ids):
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise OSError("Checksum error")
        return [float(servo_id) for servo_id in ids]

    def read_present_velocity(self, ids):
        return [float(servo_id) for servo_id in ids]


class FakeRustypot(types.ModuleType):
    def __init__(self):
        super().__init__("rustypot")
        self.opens = []

    def feetech(self, port, baudrate):
        if self.opens and self.opens[-1][2]() is not None:
            raise OSError("Device or resource busy")
        generation = len(self.opens) + 1
        io = FakeIO(generation, fail_first=(generation == 1))
        self.opens.append((port, baudrate, weakref.ref(io)))
        return io


def load_hwi(fake_rustypot):
    fake_config_module = types.ModuleType("mini_bdx_runtime.duck_config")
    fake_config_module.DuckConfig = object
    package = types.ModuleType("mini_bdx_runtime")
    package.__path__ = []

    saved = {
        name: sys.modules.get(name)
        for name in ("rustypot", "mini_bdx_runtime", "mini_bdx_runtime.duck_config")
    }
    sys.modules["rustypot"] = fake_rustypot
    sys.modules["mini_bdx_runtime"] = package
    sys.modules["mini_bdx_runtime.duck_config"] = fake_config_module
    try:
        spec = importlib.util.spec_from_file_location("hwi_under_test", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.HWI
    finally:
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


class Config:
    joints_offset = {
        "left_hip_yaw": 0,
        "left_hip_roll": 0,
        "left_hip_pitch": 0,
        "left_knee": 0,
        "left_ankle": 0,
        "neck_pitch": 0,
        "head_pitch": 0,
        "head_yaw": 0,
        "head_roll": 0,
        "right_hip_yaw": 0,
        "right_hip_roll": 0,
        "right_hip_pitch": 0,
        "right_knee": 0,
        "right_ankle": 0,
    }


class TransportRecoveryTest(unittest.TestCase):
    def test_checksum_retry_reopens_transport_with_same_contract(self):
        fake = FakeRustypot()
        HWI = load_hwi(fake)
        hwi = HWI(Config(), "/dev/fake-servo")

        values = hwi._retry("read_present_position", [12, 13, 14])

        self.assertEqual(values, [12.0, 13.0, 14.0])
        self.assertEqual(hwi.read_error_count, 1)
        self.assertEqual(hwi.transport_reset_count, 1)
        self.assertEqual(
            [(port, baudrate) for port, baudrate, _ in fake.opens],
            [("/dev/fake-servo", 1_000_000), ("/dev/fake-servo", 1_000_000)],
        )

    def test_success_path_does_not_reopen_transport(self):
        fake = FakeRustypot()
        HWI = load_hwi(fake)
        hwi = HWI(Config(), "/dev/fake-servo")
        fake.opens[0][2]().fail_first = False

        values = hwi._retry("read_present_position", [13])

        self.assertEqual(values, [13.0])
        self.assertEqual(hwi.transport_reset_count, 0)
        self.assertEqual(len(fake.opens), 1)

    def test_id13_is_read_last_but_values_return_in_canonical_joint_order(self):
        fake = FakeRustypot()
        HWI = load_hwi(fake)
        hwi = HWI(Config(), "/dev/fake-servo")
        fake.opens[0][2]().fail_first = False

        positions = hwi._read_all_in_joint_order("read_present_position")
        velocities = hwi._read_all_in_joint_order("read_present_velocity")
        canonical_ids = list(hwi.joints.values())

        self.assertEqual(hwi.read_ids[-1], 13)
        self.assertEqual(positions, [float(value) for value in canonical_ids])
        self.assertEqual(velocities, [float(value) for value in canonical_ids])


if __name__ == "__main__":
    unittest.main()
