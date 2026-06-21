import time

import numpy as np
import rustypot
from mini_bdx_runtime.duck_config import DuckConfig


class HWI:
    def __init__(self, duck_config: DuckConfig, usb_port: str = "/dev/ttyACM0"):

        self.duck_config = duck_config

        # Order matters here
        self.joints = {
            "left_hip_yaw": 20,
            "left_hip_roll": 21,
            "left_hip_pitch": 22,
            "left_knee": 23,
            "left_ankle": 24,
            "neck_pitch": 30,
            "head_pitch": 31,
            "head_yaw": 32,
            "head_roll": 33,
            # "left_antenna": None,
            # "right_antenna": None,
            "right_hip_yaw": 10,
            "right_hip_roll": 11,
            "right_hip_pitch": 12,
            "right_knee": 13,
            "right_ankle": 14,
        }

        self.zero_pos = {
            "left_hip_yaw": 0,
            "left_hip_roll": 0,
            "left_hip_pitch": 0,
            "left_knee": 0,
            "left_ankle": 0,
            "neck_pitch": 0,
            "head_pitch": 0,
            "head_yaw": 0,
            "head_roll": 0,
            # "left_antenna":0,
            # "right_antenna":0,
            "right_hip_yaw": 0,
            "right_hip_roll": 0,
            "right_hip_pitch": 0,
            "right_knee": 0,
            "right_ankle": 0,
        }

        self.init_pos = {
            "left_hip_yaw": 0.002,
            "left_hip_roll": 0.053,
            "left_hip_pitch": -0.63,
            "left_knee": 1.368,
            "left_ankle": -0.784,
            "neck_pitch": 0.0,
            "head_pitch": 0.0,
            "head_yaw": 0,
            "head_roll": 0,
            # "left_antenna": 0,
            # "right_antenna": 0,
            "right_hip_yaw": -0.003,
            "right_hip_roll": -0.065,
            "right_hip_pitch": 0.635,
            "right_knee": 1.379,
            "right_ankle": -0.796,
        }

        self.joints_offsets = self.duck_config.joints_offset

        # Per-joint direction sign (all +1 = stock). The left_knee motor was
        # physically re-flipped to match the right knee, so no software flip
        # is needed anymore — every joint uses the stock direction.
        self.joints_dir = {name: 1.0 for name in self.joints}

        self.kps = np.ones(len(self.joints)) * 32  # default kp
        self.kds = np.ones(len(self.joints)) * 0  # default kd
        self.low_torque_kps = np.ones(len(self.joints)) * 2

        self.io = rustypot.feetech(usb_port, 1000000)
        self.read_error_count = 0
        self.write_error_count = 0
        self.last_error = None
        self.last_error_op = None
        self.last_error_time_monotonic_s = None
        self.retry_error_counts = {}

    def _record_retry_error(self, op_name, exc):
        kind = "read" if op_name.lower().startswith(("read", "get")) else "write"
        if kind == "read":
            self.read_error_count += 1
        else:
            self.write_error_count += 1
        self.last_error_op = op_name
        self.last_error = f"{op_name}: {exc}"
        self.last_error_time_monotonic_s = time.monotonic()
        self.retry_error_counts[op_name] = self.retry_error_counts.get(op_name, 0) + 1

    def _retry(self, fn, *args, tries=8):
        """Retry a servo-bus op through intermittent checksum/serial glitches."""
        last = None
        op_name = getattr(fn, "__name__", fn.__class__.__name__)
        for _ in range(tries):
            try:
                return fn(*args)
            except Exception as e:
                self._record_retry_error(op_name, e)
                last = e
                time.sleep(0.003)
        raise last

    def set_kps(self, kps):
        self.kps = kps
        self._retry(self.io.set_kps, list(self.joints.values()), self.kps)

    def set_kds(self, kds):
        self.kds = kds
        self._retry(self.io.set_kds, list(self.joints.values()), self.kds)

    def set_kp(self, id, kp):
        self._retry(self.io.set_kps, [id], [kp])

    def turn_on(self):
        self._retry(self.io.set_kps, list(self.joints.values()), self.low_torque_kps)
        print("turn on : low KPS set")
        time.sleep(1)

        self.set_position_all(self.init_pos)
        print("turn on : init pos set")

        time.sleep(1)

        self._retry(self.io.set_kps, list(self.joints.values()), self.kps)
        print("turn on : high kps")

    def turn_off(self):
        self._retry(self.io.disable_torque, list(self.joints.values()))

    def set_position(self, joint_name, pos):
        """
        pos is in radians
        """
        id = self.joints[joint_name]
        pos = self.joints_dir[joint_name] * pos + self.joints_offsets[joint_name]
        self._retry(self.io.write_goal_position, [id], [pos])

    def set_position_all(self, joints_positions):
        """
        joints_positions is a dictionary with joint names as keys and joint positions as values
        Warning: expects radians
        """
        ids_positions = {
            self.joints[joint]: self.joints_dir[joint] * position
            + self.joints_offsets[joint]
            for joint, position in joints_positions.items()
        }

        self._retry(
            self.io.write_goal_position,
            list(self.joints.values()),
            list(ids_positions.values()),
        )

    def get_present_positions(self, ignore=[]):
        """
        Returns the present positions in radians
        """

        try:
            present_positions = self._retry(
                self.io.read_present_position, list(self.joints.values())
            )
        except Exception as e:
            print(e)
            return None

        present_positions = [
            self.joints_dir[joint] * (pos - self.joints_offsets[joint])
            for joint, pos in zip(self.joints.keys(), present_positions)
            if joint not in ignore
        ]
        return np.array(np.around(present_positions, 3))

    def get_present_velocities(self, rad_s=True, ignore=[]):
        """
        Returns the present velocities in rad/s (default) or rev/min
        """
        try:
            present_velocities = self._retry(
                self.io.read_present_velocity, list(self.joints.values())
            )
        except Exception as e:
            print(e)
            return None

        present_velocities = [
            self.joints_dir[joint] * vel
            for joint, vel in zip(self.joints.keys(), present_velocities)
            if joint not in ignore
        ]

        return np.array(np.around(present_velocities, 3))
