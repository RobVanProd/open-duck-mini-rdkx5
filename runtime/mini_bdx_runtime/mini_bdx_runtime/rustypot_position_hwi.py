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
        canonical_ids = list(self.joints.values())
        # Full-bus evidence shows ID 13's checksum is corrupted when ID 14
        # responds after it. Request ID 13 last, then restore canonical joint
        # order before exposing values to observations or telemetry.
        self.read_ids = [servo_id for servo_id in canonical_ids if servo_id != 13]
        if 13 in canonical_ids:
            self.read_ids.append(13)

        # Per-joint direction sign (all +1 = stock). The left_knee motor was
        # physically re-flipped to match the right knee, so no software flip
        # is needed anymore — every joint uses the stock direction.
        self.joints_dir = {name: 1.0 for name in self.joints}

        self.kps = np.ones(len(self.joints)) * 32  # default kp
        self.kds = np.ones(len(self.joints)) * 0  # default kd
        self.low_torque_kps = np.ones(len(self.joints)) * 2

        self.usb_port = usb_port
        self.baudrate = 1000000
        self.io = self._open_transport()
        self.read_error_count = 0
        self.write_error_count = 0
        self.transport_reset_count = 0
        self.last_error = None
        self.last_error_op = None
        self.last_error_time_monotonic_s = None
        self.retry_error_counts = {}
        self._servo_health_cursor = 0

    def _open_transport(self):
        return rustypot.feetech(self.usb_port, self.baudrate)

    def _reset_transport(self):
        """Drop a possibly desynchronized port and reopen it with identical settings."""
        self.io = None
        # A bound PyO3 method can keep the Rust IO object, and therefore the tty,
        # alive until its reference is released. Operations are passed by name,
        # so CPython reference counting releases it here without a full cyclic
        # garbage collection pause in the real-time control loop.
        self.io = self._open_transport()
        self.transport_reset_count += 1

    @staticmethod
    def _call_transport(fn, args):
        """Call in an isolated frame so a PyO3 exception cannot retain the tty."""
        try:
            return True, fn(*args), None
        except Exception as exc:
            # Return inert diagnostics, not the exception/traceback. Retaining
            # that traceback also retains `fn` and its exclusive serial handle.
            return False, None, (type(exc), str(exc))

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

    def _retry(self, op_name, *args, tries=8):
        """Retry a bus op on a fresh transport after checksum/serial corruption."""
        last = None
        for attempt in range(tries):
            fn = getattr(self.io, op_name)
            ok, result, error = self._call_transport(fn, args)
            fn = None
            if ok:
                return result

            error_type, error_text = error
            error_value = error_type(error_text)
            self._record_retry_error(op_name, error_value)
            last = error_value
            if attempt + 1 >= tries:
                break

            # Do not retry on the same receive buffer. Rustypot 0.1.0 can
            # leave bytes from a failed sync read queued, and its next send
            # asserts that the input buffer is empty. Release the bound
            # method first so its PyO3 IO/tty handle can be destroyed.
            self._reset_transport()
            time.sleep(0.003)
        raise last

    def set_kps(self, kps):
        self.kps = kps
        self._retry("set_kps", list(self.joints.values()), self.kps)

    def set_kds(self, kds):
        self.kds = kds
        self._retry("set_kds", list(self.joints.values()), self.kds)

    def set_kp(self, id, kp):
        self._retry("set_kps", [id], [kp])

    def turn_on(self):
        self._retry("set_kps", list(self.joints.values()), self.low_torque_kps)
        print("turn on : low KPS set")
        time.sleep(1)

        self.set_position_all(self.init_pos)
        print("turn on : init pos set")

        time.sleep(1)

        self._retry("set_kps", list(self.joints.values()), self.kps)
        print("turn on : high kps")

    def turn_off(self):
        self._retry("disable_torque", list(self.joints.values()))

    def set_position(self, joint_name, pos):
        """
        pos is in radians
        """
        id = self.joints[joint_name]
        pos = self.joints_dir[joint_name] * pos + self.joints_offsets[joint_name]
        self._retry("write_goal_position", [id], [pos])

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
            "write_goal_position",
            list(self.joints.values()),
            list(ids_positions.values()),
        )

    def _read_all_in_joint_order(self, operation):
        values_in_bus_order = self._retry(operation, self.read_ids)
        by_id = dict(zip(self.read_ids, values_in_bus_order))
        return [by_id[servo_id] for servo_id in self.joints.values()]

    def read_servo_health_round_robin(self):
        """Read current, voltage and temperature for one servo per call."""
        servo_id = self.read_ids[self._servo_health_cursor]
        self._servo_health_cursor = (self._servo_health_cursor + 1) % len(self.read_ids)
        joint_name = next(name for name, value in self.joints.items() if value == servo_id)
        operations = (
            ("present_current_raw", "get_present_current"),
            ("present_voltage_raw", "get_present_voltage"),
            ("present_temperature_raw", "get_present_temperature"),
        )
        result = {
            "joint_name": joint_name,
            "servo_id": servo_id,
            "joint_index": list(self.joints).index(joint_name),
            "coverage_index": self._servo_health_cursor,
            "coverage_size": len(self.read_ids),
            "errors": {},
        }
        for field, operation in operations:
            try:
                values = self._retry(operation, [servo_id])
                result[field] = None if not values else values[0]
            except Exception as exc:
                result[field] = None
                result["errors"][field] = f"{type(exc).__name__}: {exc}"
        return result

    def get_present_positions(self, ignore=[]):
        """
        Returns the present positions in radians
        """

        try:
            present_positions = self._read_all_in_joint_order("read_present_position")
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
            present_velocities = self._read_all_in_joint_order("read_present_velocity")
        except Exception as e:
            print(e)
            return None

        present_velocities = [
            self.joints_dir[joint] * vel
            for joint, vel in zip(self.joints.keys(), present_velocities)
            if joint not in ignore
        ]

        return np.array(np.around(present_velocities, 3))
