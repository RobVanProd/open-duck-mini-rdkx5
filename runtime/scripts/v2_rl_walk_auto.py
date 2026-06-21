"""
自动行走版本 - 不需要手柄控制
机器人会以设定的速度自动往前走
"""
import time
import pickle

import numpy as np
from mini_bdx_runtime.rustypot_position_hwi import HWI
from mini_bdx_runtime.onnx_infer import OnnxInfer

from mini_bdx_runtime.raw_imu import Imu
from mini_bdx_runtime.poly_reference_motion import PolyReferenceMotion
from mini_bdx_runtime.feet_contacts import FeetContacts
from mini_bdx_runtime.eyes import Eyes
from mini_bdx_runtime.sounds import Sounds
from mini_bdx_runtime.antennas import Antennas
from mini_bdx_runtime.projector import Projector
from mini_bdx_runtime.rl_utils import make_action_dict, LowPassActionFilter
from mini_bdx_runtime.duck_config import DuckConfig

import os

HOME_DIR = os.path.expanduser("~")


class RLWalkAuto:
    def __init__(
        self,
        onnx_model_path: str,
        duck_config_path: str = f"{HOME_DIR}/duck_config.json",
        serial_port: str = "/dev/ttyACM0",
        control_freq: float = 50,
        pid=[30, 0, 0],
        action_scale=0.25,
        pitch_bias=0,
        save_obs=False,
        replay_obs=None,
        cutoff_frequency=None,
        # 自动行走参数
        forward_speed=0.08,  # 前进速度 (范围: -0.15 ~ 0.15)
        side_speed=0.0,      # 侧向速度 (范围: -0.2 ~ 0.2)
        turn_speed=0.0,      # 旋转速度 (范围: -1.0 ~ 1.0)
    ):

        self.duck_config = DuckConfig(config_json_path=duck_config_path)

        self.pitch_bias = pitch_bias

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

        # 自动行走命令 [lin_vel_x, lin_vel_y, ang_vel, neck_pitch, head_pitch, head_yaw, head_roll]
        self.forward_speed = forward_speed
        self.side_speed = side_speed
        self.turn_speed = turn_speed
        self.last_commands = [
            self.forward_speed,  # 前进速度
            self.side_speed,     # 侧向速度
            self.turn_speed,     # 旋转速度
            0.0,  # neck_pitch
            0.0,  # head_pitch
            0.0,  # head_yaw
            0.0,  # head_roll
        ]

        self.paused = self.duck_config.start_paused

        # Reference motion, but we only really need the length of one phase
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

    def set_velocity(self, forward=None, side=None, turn=None):
        """动态设置行走速度"""
        if forward is not None:
            self.forward_speed = np.clip(forward, -0.15, 0.15)
            self.last_commands[0] = self.forward_speed
        if side is not None:
            self.side_speed = np.clip(side, -0.2, 0.2)
            self.last_commands[1] = self.side_speed
        if turn is not None:
            self.turn_speed = np.clip(turn, -1.0, 1.0)
            self.last_commands[2] = self.turn_speed

    def run(self):
        i = 0
        try:
            print("Starting auto walk...")
            print(f"  Forward speed: {self.forward_speed}")
            print(f"  Side speed: {self.side_speed}")
            print(f"  Turn speed: {self.turn_speed}")
            print("Press Ctrl+C to stop")
            
            start_t = time.time()
            while True:
                t = time.time()

                if self.paused:
                    time.sleep(0.1)
                    continue

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

                self.motor_targets = self.init_pos + action * self.action_scale

                if self.action_filter is not None:
                    self.action_filter.push(self.motor_targets)
                    filtered_motor_targets = self.action_filter.get_filtered_action()
                    if (
                        time.time() - start_t > 1
                    ):  # give time to the filter to stabilize
                        self.motor_targets = filtered_motor_targets

                self.prev_motor_targets = self.motor_targets.copy()

                head_motor_targets = self.last_commands[3:] + self.motor_targets[5:9]
                self.motor_targets[5:9] = head_motor_targets

                action_dict = make_action_dict(
                    self.motor_targets, list(self.hwi.joints.keys())
                )

                self.hwi.set_position_all(action_dict)

                i += 1

                took = time.time() - t
                if (1 / self.control_freq - took) < 0:
                    print(
                        "Policy control budget exceeded by",
                        np.around(took - 1 / self.control_freq, 3),
                    )
                time.sleep(max(0, 1 / self.control_freq - took))

        except KeyboardInterrupt:
            print("\nStopping...")
            if self.duck_config.antennas:
                self.antennas.stop()
            if self.duck_config.eyes:
                self.eyes.stop()
            if self.duck_config.projector:
                self.projector.stop()
            self.feet_contacts.stop()

        if self.save_obs:
            pickle.dump(self.saved_obs, open("robot_saved_obs.pkl", "wb"))
        print("TURNING OFF")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto walk without controller")
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
    
    # 自动行走速度参数 (必须在训练范围内！)
    parser.add_argument(
        "--forward_speed",
        type=float,
        default=0.08,
        help="Forward walking speed, MUST be in [-0.15, 0.15], default 0.08",
    )
    parser.add_argument(
        "--side_speed",
        type=float,
        default=0.0,
        help="Sideways speed, MUST be in [-0.2, 0.2], default 0.0",
    )
    parser.add_argument(
        "--turn_speed",
        type=float,
        default=0.0,
        help="Turn speed, MUST be in [-1.0, 1.0], default 0.0",
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
        help="replay the observations from a previous run",
    )
    parser.add_argument("--cutoff_frequency", type=float, default=None)

    args = parser.parse_args()
    pid = [args.p, args.i, args.d]

    print("Done parsing args")
    
    # 检查并限制速度在训练范围内
    if args.forward_speed < -0.15 or args.forward_speed > 0.15:
        print(f"WARNING: forward_speed {args.forward_speed} is out of training range [-0.15, 0.15]!")
        args.forward_speed = np.clip(args.forward_speed, -0.15, 0.15)
        print(f"         Clipped to {args.forward_speed}")
    
    if args.side_speed < -0.2 or args.side_speed > 0.2:
        print(f"WARNING: side_speed {args.side_speed} is out of training range [-0.2, 0.2]!")
        args.side_speed = np.clip(args.side_speed, -0.2, 0.2)
        print(f"         Clipped to {args.side_speed}")
    
    if args.turn_speed < -1.0 or args.turn_speed > 1.0:
        print(f"WARNING: turn_speed {args.turn_speed} is out of training range [-1.0, 1.0]!")
        args.turn_speed = np.clip(args.turn_speed, -1.0, 1.0)
        print(f"         Clipped to {args.turn_speed}")
    
    print(f"Auto walk mode: forward={args.forward_speed}, side={args.side_speed}, turn={args.turn_speed}")
    
    rl_walk = RLWalkAuto(
        args.onnx_model_path,
        duck_config_path=args.duck_config_path,
        action_scale=args.action_scale,
        pid=pid,
        control_freq=args.control_freq,
        pitch_bias=args.pitch_bias,
        save_obs=args.save_obs,
        replay_obs=args.replay_obs,
        cutoff_frequency=args.cutoff_frequency,
        forward_speed=args.forward_speed,
        side_speed=args.side_speed,
        turn_speed=args.turn_speed,
    )
    print("Done instantiating RLWalkAuto")
    rl_walk.run()
