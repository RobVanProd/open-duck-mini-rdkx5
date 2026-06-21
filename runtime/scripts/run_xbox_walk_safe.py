#!/usr/bin/env python3
"""Persistent safe launcher for Open Duck Mini Xbox walking.

Run from the runtime scripts directory on the robot. It starts the policy in
the configured paused state, logs telemetry to ~/duck_logs, and disables torque
when the process exits.
"""

import argparse
import os
import signal
import sys
import threading
import time

import numpy as np

from mini_bdx_runtime.xbox_controller import XBoxController
from v2_rl_walk_mujoco import RLWalk


HOME = os.path.expanduser("~")
DEFAULT_ONNX = os.path.join(HOME, "BEST_WALK_ONNX_2.onnx")
LOG_DIR = os.path.join(HOME, "duck_logs")


class SafeXboxController:
    """Safety wrapper around the stock Xbox controller.

    The stock controller can report a non-zero stick command while paused. If A
    is pressed in that state, the policy immediately starts with that command.
    This wrapper adds deadzone/clamping and blocks unpause until the command is
    neutral.
    """

    def __init__(self, command_freq, log, deadzone=0.025, max_x=0.05, max_y=0.05, max_yaw=0.15):
        self.inner = XBoxController(command_freq)
        self.log = log
        self.deadzone = deadzone
        self.max_x = max_x
        self.max_y = max_y
        self.max_yaw = max_yaw
        self.blocked_unpause_count = 0
        self.bias = np.zeros(3, dtype=float)
        self.calibrated = False
        self._calibrate_bias()

    def _read_raw_command(self):
        commands, buttons, left_trigger, right_trigger = self.inner.get_last_command()
        return np.asarray(commands, dtype=float).copy(), buttons, left_trigger, right_trigger

    def _calibrate_bias(self):
        samples = []
        deadline = time.time() + 1.0
        while time.time() < deadline:
            commands, _, left_trigger, right_trigger = self._read_raw_command()
            if left_trigger < 0.1 and right_trigger < 0.1:
                samples.append(commands[:3])
            time.sleep(0.05)
        if samples:
            self.bias = np.median(np.asarray(samples), axis=0)
            self.calibrated = True
        self.log("controller neutral bias=%s" % ([round(float(c), 3) for c in self.bias],))

    def get_last_command(self):
        commands, buttons, left_trigger, right_trigger = self._read_raw_command()
        commands[:3] -= self.bias

        for i in range(3):
            if abs(commands[i]) < self.deadzone:
                commands[i] = 0.0

        commands[0] = float(np.clip(commands[0], -self.max_x, self.max_x))
        commands[1] = float(np.clip(commands[1], -self.max_y, self.max_y))
        commands[2] = float(np.clip(commands[2], -self.max_yaw, self.max_yaw))

        neutral = (
            abs(commands[0]) < 1e-9
            and abs(commands[1]) < 1e-9
            and abs(commands[2]) < 1e-9
            and left_trigger < 0.1
            and right_trigger < 0.1
        )
        if buttons.A.triggered and not neutral:
            buttons.A.triggered = False
            self.blocked_unpause_count += 1
            self.log(
                "blocked A/unpause: sticks or triggers not neutral cmd=%s lt=%.3f rt=%.3f"
                % ([round(float(c), 3) for c in commands[:3]], left_trigger, right_trigger)
            )

        return commands, buttons, left_trigger, right_trigger


def main():
    parser = argparse.ArgumentParser(description="Safe Xbox walking launcher")
    parser.add_argument("--onnx_model_path", default=DEFAULT_ONNX)
    parser.add_argument("--duration", type=float, default=0.0,
                        help="Optional run duration in seconds. 0 means run until Ctrl+C.")
    parser.add_argument("--control_freq", type=int, default=50)
    parser.add_argument("--action_scale", type=float, default=0.25)
    parser.add_argument("--max_x", type=float, default=0.05)
    parser.add_argument("--max_y", type=float, default=0.05)
    parser.add_argument("--max_yaw", type=float, default=0.15)
    parser.add_argument("--deadzone", type=float, default=0.025)
    parser.add_argument("--imu_tare_seconds", type=float, default=2.0)
    parser.add_argument("--pitch_bias", type=float, default=0.0)
    parser.add_argument("--cutoff_frequency", type=float, default=None)
    parser.add_argument("--torque-off-on-exit", action="store_true",
                        help="Disable torque inside this process. Default leaves torque on; use servo_power_diag.py off_only after exit.")
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "xbox_walk_%d.log" % int(time.time()))
    log_file = open(log_path, "a", buffering=1)

    def log(message):
        line = "[%.2f] %s" % (time.time(), message)
        print(line, flush=True)
        log_file.write(line + "\n")

    log("=== Xbox walk launcher start ===")
    log("log=%s" % log_path)
    log("duration=%s action_scale=%s control_freq=%s" %
        (args.duration, args.action_scale, args.control_freq))

    rl_walk = None
    stop = threading.Event()

    def telemetry():
        while not stop.is_set():
            if rl_walk is None:
                time.sleep(0.2)
                continue
            try:
                imu = rl_walk.imu.get_data()
                accel = np.asarray(imu["accelero"], dtype=float)
                gyro = np.asarray(imu["gyro"], dtype=float)
                norm = np.linalg.norm(accel)
                tilt = -1.0
                if norm > 1.0:
                    tilt = float(np.degrees(np.arctan2(np.hypot(accel[0], accel[1]), abs(accel[2]))))
                cmd = [round(float(c), 3) for c in rl_walk.last_commands[:3]]
                log("paused=%s tilt=%.1fdeg gyro=%s accel=%s cmd=%s" %
                    (rl_walk.paused, tilt, np.round(gyro, 3).tolist(),
                     np.round(accel, 3).tolist(), cmd))
            except Exception as exc:
                log("telemetry_error=%r" % (exc,))
            time.sleep(1.0)

    def duration_stop():
        if args.duration <= 0:
            return
        time.sleep(args.duration)
        log("duration elapsed; requesting stop")
        os.kill(os.getpid(), signal.SIGINT)

    try:
        rl_walk = RLWalk(
            args.onnx_model_path,
            control_freq=args.control_freq,
            action_scale=args.action_scale,
            commands=True,
            pitch_bias=args.pitch_bias,
            cutoff_frequency=args.cutoff_frequency,
        )
        rl_walk.xbox_controller = SafeXboxController(
            rl_walk.command_freq,
            log,
            deadzone=args.deadzone,
            max_x=args.max_x,
            max_y=args.max_y,
            max_yaw=args.max_yaw,
        )
        log("controller attached")
        log(
            "paused_at_start=%s; center sticks/triggers, then press A to toggle pause/walk"
            % rl_walk.paused
        )
        log(
            "safety: deadzone=%.3f max_x=%.3f max_y=%.3f max_yaw=%.3f"
            % (args.deadzone, args.max_x, args.max_y, args.max_yaw)
        )
        if hasattr(rl_walk.imu, "x_offset") and args.imu_tare_seconds > 0:
            samples = []
            deadline = time.time() + args.imu_tare_seconds
            while time.time() < deadline:
                try:
                    accel = np.asarray(rl_walk.imu.get_data()["accelero"], dtype=float)
                    if np.linalg.norm(accel) > 1.0:
                        samples.append(accel[0])
                except Exception as exc:
                    log("imu_tare_sample_error=%r" % (exc,))
                time.sleep(0.05)
            if samples:
                rl_walk.imu.x_offset = float(np.median(np.asarray(samples)))
                log("imu raw accel x_offset tare=%.3f from %d samples" % (rl_walk.imu.x_offset, len(samples)))
            else:
                log("imu raw accel x_offset tare skipped: no valid samples")

        threading.Thread(target=telemetry, daemon=True).start()
        threading.Thread(target=duration_stop, daemon=True).start()
        rl_walk.run()
    finally:
        stop.set()
        if rl_walk is not None and args.torque_off_on_exit:
            try:
                log("disabling torque")
                rl_walk.hwi.turn_off()
            except Exception as exc:
                log("torque_off_error=%r" % (exc,))
        elif rl_walk is not None:
            log("leaving torque enabled; run servo_power_diag.py off_only when supported")
        log("=== Xbox walk launcher end ===")
        log_file.close()


if __name__ == "__main__":
    main()
