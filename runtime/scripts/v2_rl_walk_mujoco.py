import time
import pickle

import numpy as np
from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.onnx_infer import OnnxInfer

from mini_bdx_runtime.raw_imu import Imu
from mini_bdx_runtime.poly_reference_motion import PolyReferenceMotion
# 控制器在 __main__ 中根据参数动态导入
from mini_bdx_runtime.feet_contacts import FeetContacts
from mini_bdx_runtime.eyes import Eyes
from mini_bdx_runtime.sounds import Sounds
from mini_bdx_runtime.antennas import Antennas
from mini_bdx_runtime.projector import Projector
from mini_bdx_runtime.rl_utils import make_action_dict, LowPassActionFilter
from mini_bdx_runtime.duck_config import DuckConfig

import os

HOME_DIR = os.path.expanduser("~")


class RLWalk:
    def __init__(
        self,
        onnx_model_path: str,
        duck_config_path: str = f"{HOME_DIR}/duck_config.json",
        serial_port: str = "/dev/ttyACM0",
        control_freq: float = 50,
        pid=[30, 0, 0],
        action_scale=0.25,
        commands=False,
        pitch_bias=0,
        save_obs=False,
        replay_obs=None,
        cutoff_frequency=None,
        fixed_command_x=None,
        max_runtime_seconds=None,
        force_unpaused=False,
        log_telemetry: bool = False,
        telemetry_path: str | None = None,
        telemetry_read_voltage: bool = False,
        telemetry_every_n: int = 1,
    ):

        self.duck_config = DuckConfig(config_json_path=duck_config_path)

        self.commands = commands
        self.fixed_command_x = fixed_command_x
        self.max_runtime_seconds = max_runtime_seconds
        self.pitch_bias = pitch_bias
        self.cutoff_frequency = cutoff_frequency

        self.onnx_model_path = onnx_model_path
        self.policy = OnnxInfer(self.onnx_model_path, awd=True)

        self.num_dofs = 14
        self.max_motor_velocity = 5.24  # rad/s

        # Control
        self.control_freq = control_freq
        self.pid = pid

        self.save_obs = save_obs
        if self.save_obs:
            self.saved_obs = []

        self.replay_obs = replay_obs
        if self.replay_obs is not None:
            self.replay_obs = pickle.load(open(self.replay_obs, "rb"))

        self.action_filter = None
        if cutoff_frequency is not None:
            self.action_filter = LowPassActionFilter(
                self.control_freq, cutoff_frequency
            )

        self.log_telemetry = bool(log_telemetry)
        self.telemetry_path = telemetry_path
        self.telemetry_read_voltage = bool(telemetry_read_voltage)
        self.telemetry_every_n = max(1, int(telemetry_every_n or 1))
        self.telemetry_logger = None
        self.telemetry_norm = None
        self._telemetry_utc_timestamp = None
        self._telemetry_normalize_observation = None
        self._telemetry_policy_sha256 = None
        self._telemetry_policy_output_name = None
        self._telemetry_last_tick_monotonic = None
        self._telemetry_last_imu_data = None
        self._telemetry_last_dof_pos = None
        self._telemetry_last_dof_vel = None
        self._telemetry_last_feet_contacts = None

        self.hwi = HWI(self.duck_config, serial_port)

        self.start()

        self.imu = Imu(
            sampling_freq=int(self.control_freq),
            user_pitch_bias=self.pitch_bias,
            upside_down=self.duck_config.imu_upside_down,
        )

        self.feet_contacts = FeetContacts()

        # Scales
        self.action_scale = action_scale

        self.last_action = np.zeros(self.num_dofs)
        self.last_last_action = np.zeros(self.num_dofs)
        self.last_last_last_action = np.zeros(self.num_dofs)

        self.init_pos = list(self.hwi.init_pos.values())

        self.motor_targets = np.array(self.init_pos.copy())
        self.prev_motor_targets = np.array(self.init_pos.copy())

        self.last_commands = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.paused = self.duck_config.start_paused
        if force_unpaused:
            self.paused = False

        self.command_freq = 20  # hz
        if self.commands and self.fixed_command_x is None:
            # 控制器在运行时传入
            pass  # 控制器将在 run() 之前设置

        # Reference motion, but we only really need the length of one phase
        # TODO
        self.PRM = PolyReferenceMotion("./polynomial_coefficients.pkl")
        self.imitation_i = 0
        self.imitation_phase = np.array([0, 0])
        self.phase_frequency_factor = 1.0
        self.phase_frequency_factor_offset = (
            self.duck_config.phase_frequency_factor_offset
        )

        # Optional expression features
        if self.duck_config.eyes:
            self.eyes = Eyes()
        if self.duck_config.projector:
            self.projector = Projector()
        if self.duck_config.speaker:
            self.sounds = Sounds(
                volume=1.0, sound_directory="../mini_bdx_runtime/assets/"
            )
        if self.duck_config.antennas:
            self.antennas = Antennas()

        self._setup_telemetry()

    def _setup_telemetry(self):
        if not self.log_telemetry:
            return

        from mini_bdx_runtime.telemetry import (
            JsonlTelemetryLogger,
            extract_onnx_obs_normalization,
            normalize_observation,
            sha256_file,
            timestamp_slug,
            utc_timestamp,
        )

        if self.telemetry_path is None:
            self.telemetry_path = os.path.join(
                HOME_DIR, "duck_logs", f"{timestamp_slug()}_rl_walk.jsonl"
            )

        self._telemetry_utc_timestamp = utc_timestamp
        self._telemetry_normalize_observation = normalize_observation
        self._telemetry_policy_sha256 = sha256_file(self.onnx_model_path)
        self._telemetry_policy_output_name = self._policy_output_name()
        self.telemetry_norm = extract_onnx_obs_normalization(self.onnx_model_path)
        self.telemetry_logger = JsonlTelemetryLogger(self.telemetry_path)
        print("telemetry:", self.telemetry_logger.path, flush=True)

    def _policy_output_name(self):
        try:
            return self.policy.ort_session.get_outputs()[0].name
        except Exception:
            return None

    def _telemetry_voltage(self):
        # Voltage reads are intentionally opt-in and currently unavailable
        # through the local HWI wrapper without adding new bus traffic.
        if not self.telemetry_read_voltage:
            return None
        return None

    def _log_policy_tick(
        self,
        *,
        tick,
        t_mono,
        obs,
        action,
        scaled_delta,
        motor_targets_pre_rate_limit,
        motor_targets_post_rate_limit,
        motor_targets_sent,
        previous_motor_targets_for_tracking,
    ):
        if not self.log_telemetry or self.telemetry_logger is None:
            return
        if tick % self.telemetry_every_n != 0:
            return

        if self._telemetry_last_tick_monotonic is None:
            dt_s = None
        else:
            dt_s = t_mono - self._telemetry_last_tick_monotonic
        self._telemetry_last_tick_monotonic = t_mono

        mean = None if self.telemetry_norm is None else self.telemetry_norm.get("mean")
        std_recip = (
            None if self.telemetry_norm is None else self.telemetry_norm.get("std_recip")
        )
        normalized = None
        if self._telemetry_normalize_observation is not None:
            normalized = self._telemetry_normalize_observation(obs, mean, std_recip)

        joint_names = list(self.hwi.joints.keys())
        actual_pos = self._telemetry_last_dof_pos
        actual_vel = self._telemetry_last_dof_vel
        tracking_error = None
        if actual_pos is not None and previous_motor_targets_for_tracking is not None:
            tracking_error = actual_pos - previous_motor_targets_for_tracking

        imu_data = self._telemetry_last_imu_data or {}
        feet_contacts = self._telemetry_last_feet_contacts
        record = {
            "schema_version": "sim2real.telemetry.v1",
            "tick": int(tick),
            "timestamp_monotonic_s": t_mono,
            "timestamp_wall": self._telemetry_utc_timestamp(),
            "dt_s": dt_s,
            "policy": {
                "onnx_path": self.onnx_model_path,
                "onnx_sha256": self._telemetry_policy_sha256,
                "input_name": getattr(self.policy, "input_name", "obs"),
                "output_name": self._telemetry_policy_output_name,
                "observation_dim": 101,
                "action_dim": 14,
            },
            "control": {
                "control_freq_hz": self.control_freq,
                "paused": self.paused,
                "action_scale": self.action_scale,
                "max_motor_velocity_rad_s": self.max_motor_velocity,
                "cutoff_frequency_hz": self.cutoff_frequency,
                "commands": self.last_commands,
                "imitation_i": self.imitation_i,
                "imitation_phase": self.imitation_phase,
                "feet_contacts": feet_contacts,
            },
            "imu": {
                "imu_upside_down": self.duck_config.imu_upside_down,
                "raw_gyro": imu_data.get("gyro"),
                "raw_accelero": imu_data.get("accelero"),
                "policy_gyro": None if obs is None or len(obs) < 3 else obs[0:3],
                "policy_accelero": None if obs is None or len(obs) < 6 else obs[3:6],
            },
            "joints": {
                "names": joint_names,
                "servo_ids": list(self.hwi.joints.values()),
                "offsets_rad": [self.hwi.joints_offsets.get(name) for name in joint_names],
                "home_rad": self.init_pos,
                "commanded_position_rad": motor_targets_sent,
                "actual_position_rad": actual_pos,
                "actual_velocity_rad_s": actual_vel,
                "tracking_error_rad": tracking_error,
                "battery_voltage_v": self._telemetry_voltage(),
            },
            "observation": {
                "raw_vector": obs,
                "full_raw_vector": obs,
                "normalized_vector": normalized,
                "normalization_mean": mean,
                "normalization_std_recip": std_recip,
                "normalization_source": None
                if self.telemetry_norm is None
                else self.telemetry_norm.get("source"),
                "normalization_error": None
                if self.telemetry_norm is None
                else self.telemetry_norm.get("error"),
            },
            "action": {
                "onnx_action": action,
                "scaled_delta_rad": scaled_delta,
                "motor_targets_pre_rate_limit_rad": motor_targets_pre_rate_limit,
                "motor_targets_post_rate_limit_rad": motor_targets_post_rate_limit,
                "motor_targets_sent_rad": motor_targets_sent,
            },
            "bus": {
                "read_error_count": getattr(self.hwi, "read_error_count", None),
                "write_error_count": getattr(self.hwi, "write_error_count", None),
                "last_error": getattr(self.hwi, "last_error", None),
            },
        }
        self.telemetry_logger.log(record)

    def get_obs(self):

        imu_data = self.imu.get_data()

        dof_pos = self.hwi.get_present_positions(
            ignore=[
                "left_antenna",
                "right_antenna",
            ]
        )  # rad

        dof_vel = self.hwi.get_present_velocities(
            ignore=[
                "left_antenna",
                "right_antenna",
            ]
        )  # rad/s

        if dof_pos is None or dof_vel is None:
            return None

        if len(dof_pos) != self.num_dofs:
            print(f"ERROR len(dof_pos) != {self.num_dofs}")
            return None

        if len(dof_vel) != self.num_dofs:
            print(f"ERROR len(dof_vel) != {self.num_dofs}")
            return None

        cmds = self.last_commands

        feet_contacts = self.feet_contacts.get()

        if self.log_telemetry:
            self._telemetry_last_imu_data = {
                "gyro": imu_data["gyro"].copy(),
                "accelero": imu_data["accelero"].copy(),
            }
            self._telemetry_last_dof_pos = dof_pos.copy()
            self._telemetry_last_dof_vel = dof_vel.copy()
            self._telemetry_last_feet_contacts = list(feet_contacts)

        obs = np.concatenate(
            [
                imu_data["gyro"],
                imu_data["accelero"],
                cmds,
                dof_pos - self.init_pos,
                dof_vel * 0.05,
                self.last_action,
                self.last_last_action,
                self.last_last_last_action,
                self.motor_targets,
                feet_contacts,
                self.imitation_phase,
            ]
        )

        return obs

    def start(self):
        kps = [self.pid[0]] * 14
        kds = [self.pid[2]] * 14

        # lower head kps
        kps[5:9] = [8, 8, 8, 8]

        self.hwi.set_kps(kps)
        self.hwi.set_kds(kds)
        self.hwi.turn_on()

        time.sleep(2)

    def get_phase_frequency_factor(self, x_velocity):

        max_phase_frequency = 1.2
        min_phase_frequency = 1.0

        # Perform linear interpolation
        freq = min_phase_frequency + (abs(x_velocity) / 0.15) * (
            max_phase_frequency - min_phase_frequency
        )

        return freq

    def run(self):
        i = 0
        try:
            print("Starting")
            start_t = time.time()
            while True:
                if (
                    self.max_runtime_seconds is not None
                    and time.time() - start_t >= self.max_runtime_seconds
                ):
                    print("Max runtime reached")
                    break

                left_trigger = 0
                right_trigger = 0
                t = time.time()

                if self.fixed_command_x is not None:
                    self.last_commands = [
                        self.fixed_command_x,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ]
                elif self.commands:
                    self.last_commands, self.buttons, left_trigger, right_trigger = (
                        self.xbox_controller.get_last_command()
                    )
                    if self.buttons.dpad_up.triggered:
                        self.phase_frequency_factor_offset += 0.05
                        print(
                            f"Phase frequency factor offset {round(self.phase_frequency_factor_offset, 3)}"
                        )

                    if self.buttons.dpad_down.triggered:
                        self.phase_frequency_factor_offset -= 0.05
                        print(
                            f"Phase frequency factor offset {round(self.phase_frequency_factor_offset, 3)}"
                        )

                    if self.buttons.LB.is_pressed:
                        self.phase_frequency_factor = 1.3
                    else:
                        self.phase_frequency_factor = 1.0

                    if self.buttons.X.triggered:
                        if self.duck_config.projector:
                            self.projector.switch()

                    if self.buttons.B.triggered:
                        if self.duck_config.speaker:
                            self.sounds.play_random_sound()

                    if self.duck_config.antennas:
                        self.antennas.set_position_left(right_trigger)
                        self.antennas.set_position_right(left_trigger)

                    if self.buttons.A.triggered:
                        self.paused = not self.paused
                        if self.paused:
                            print("PAUSE")
                        else:
                            print("UNPAUSE")

                if self.paused:
                    time.sleep(0.1)
                    continue

                telemetry_t_mono = time.monotonic() if self.log_telemetry else None
                obs = self.get_obs()
                if obs is None:
                    continue

                self.imitation_i += 1 * (
                    self.phase_frequency_factor + self.phase_frequency_factor_offset
                )
                self.imitation_i = self.imitation_i % self.PRM.nb_steps_in_period
                self.imitation_phase = np.array(
                    [
                        np.cos(
                            self.imitation_i / self.PRM.nb_steps_in_period * 2 * np.pi
                        ),
                        np.sin(
                            self.imitation_i / self.PRM.nb_steps_in_period * 2 * np.pi
                        ),
                    ]
                )

                if self.save_obs:
                    self.saved_obs.append(obs)

                if self.replay_obs is not None:
                    if i < len(self.replay_obs):
                        obs = self.replay_obs[i]
                    else:
                        print("BREAKING ")
                        break

                action = self.policy.infer(obs)

                self.last_last_last_action = self.last_last_action.copy()
                self.last_last_action = self.last_action.copy()
                self.last_action = action.copy()

                # action = np.zeros(10)

                previous_motor_targets_for_tracking = self.motor_targets.copy()
                scaled_delta = action * self.action_scale
                motor_targets_pre_rate_limit = self.init_pos + scaled_delta
                self.motor_targets = motor_targets_pre_rate_limit

                self.motor_targets = np.clip(
                    self.motor_targets,
                    self.prev_motor_targets
                    - self.max_motor_velocity * (1 / self.control_freq),  # control dt
                    self.prev_motor_targets
                    + self.max_motor_velocity * (1 / self.control_freq),  # control dt
                )

                if self.action_filter is not None:
                    self.action_filter.push(self.motor_targets)
                    filtered_motor_targets = self.action_filter.get_filtered_action()
                    if (
                        time.time() - start_t > 1
                    ):  # give time to the filter to stabilize
                        self.motor_targets = filtered_motor_targets

                motor_targets_post_rate_limit = self.motor_targets.copy()
                self.prev_motor_targets = self.motor_targets.copy()

                head_motor_targets = self.last_commands[3:] + self.motor_targets[5:9]
                self.motor_targets[5:9] = head_motor_targets
                motor_targets_sent = self.motor_targets.copy()

                action_dict = make_action_dict(
                    self.motor_targets, list(self.hwi.joints.keys())
                )

                self.hwi.set_position_all(action_dict)

                self._log_policy_tick(
                    tick=i,
                    t_mono=telemetry_t_mono,
                    obs=obs,
                    action=action,
                    scaled_delta=scaled_delta,
                    motor_targets_pre_rate_limit=motor_targets_pre_rate_limit,
                    motor_targets_post_rate_limit=motor_targets_post_rate_limit,
                    motor_targets_sent=motor_targets_sent,
                    previous_motor_targets_for_tracking=previous_motor_targets_for_tracking,
                )

                i += 1

                took = time.time() - t
                # print("Full loop took", took, "fps : ", np.around(1 / took, 2))
                if (1 / self.control_freq - took) < 0:
                    print(
                        "Policy control budget exceeded by",
                        np.around(took - 1 / self.control_freq, 3),
                    )
                time.sleep(max(0, 1 / self.control_freq - took))

        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            self.cleanup()

        if self.save_obs:
            pickle.dump(self.saved_obs, open("robot_saved_obs.pkl", "wb"))
        print("TURNING OFF")

    def cleanup(self):
        try:
            if self.duck_config.antennas:
                self.antennas.stop()
        except Exception as exc:
            print("Antenna cleanup failed:", exc)
        try:
            if self.duck_config.eyes:
                self.eyes.stop()
        except Exception as exc:
            print("Eye cleanup failed:", exc)
        try:
            if self.duck_config.projector:
                self.projector.stop()
        except Exception as exc:
            print("Projector cleanup failed:", exc)
        try:
            self.feet_contacts.stop()
        except Exception as exc:
            print("Feet contact cleanup failed:", exc)
        try:
            self.hwi.turn_off()
        except Exception as exc:
            print("Motor turn_off cleanup failed:", exc)
        try:
            if self.telemetry_logger is not None:
                self.telemetry_logger.close()
        except Exception as exc:
            print("Telemetry cleanup failed:", exc)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx_model_path", type=str, required=True)
    parser.add_argument(
        "--duck_config_path",
        type=str,
        required=False,
        default=f"{HOME_DIR}/duck_config.json",
    )
    parser.add_argument("-a", "--action_scale", type=float, default=0.25)
    parser.add_argument("-p", type=int, default=30)
    parser.add_argument("-i", type=int, default=0)
    parser.add_argument("-d", type=int, default=0)
    parser.add_argument("-c", "--control_freq", type=int, default=50)
    parser.add_argument("--pitch_bias", type=float, default=0, help="deg")
    parser.add_argument(
        "--commands",
        action="store_true",
        default=True,
        help="external commands, keyboard or gamepad. Launch control_server.py on host computer",
    )
    parser.add_argument(
        "--save_obs",
        type=str,
        required=False,
        default=False,
        help="save the run's observations",
    )
    parser.add_argument(
        "--replay_obs",
        type=str,
        required=False,
        default=None,
        help="replay the observations from a previous run (can be from the robot or from mujoco)",
    )
    parser.add_argument("--cutoff_frequency", type=float, default=None)
    parser.add_argument("--fixed_command_x", type=float, default=None)
    parser.add_argument("--max_runtime_seconds", type=float, default=None)
    parser.add_argument("--force_unpaused", action="store_true")
    parser.add_argument("--log-telemetry", action="store_true")
    parser.add_argument("--telemetry-path", default=None)
    parser.add_argument("--telemetry-read-voltage", action="store_true")
    parser.add_argument("--telemetry-every-n", type=int, default=1)
    parser.add_argument(
        "--controller",
        type=str,
        default="f710",
        choices=["xbox", "f710"],
        help="选择手柄类型: xbox 或 f710 (默认 f710)",
    )

    args = parser.parse_args()
    pid = [args.p, args.i, args.d]

    print("Done parsing args")
    rl_walk = RLWalk(
        args.onnx_model_path,
        duck_config_path=args.duck_config_path,
        action_scale=args.action_scale,
        pid=pid,
        control_freq=args.control_freq,
        commands=args.commands,
        pitch_bias=args.pitch_bias,
        save_obs=args.save_obs,
        replay_obs=args.replay_obs,
        cutoff_frequency=args.cutoff_frequency,
        fixed_command_x=args.fixed_command_x,
        max_runtime_seconds=args.max_runtime_seconds,
        force_unpaused=args.force_unpaused,
        log_telemetry=args.log_telemetry,
        telemetry_path=args.telemetry_path,
        telemetry_read_voltage=args.telemetry_read_voltage,
        telemetry_every_n=args.telemetry_every_n,
    )
    print("Done instantiating RLWalk")
    
    # 根据参数选择控制器
    if args.commands and args.fixed_command_x is None:
        if args.controller == "f710":
            from mini_bdx_runtime.f710_controller import F710Controller
            rl_walk.xbox_controller = F710Controller(rl_walk.command_freq)
            print("[Controller] 使用 F710 控制器")
        else:
            from mini_bdx_runtime.xbox_controller import XBoxController
            rl_walk.xbox_controller = XBoxController(rl_walk.command_freq)
            print("[Controller] 使用 Xbox 控制器")
    
    rl_walk.run()
