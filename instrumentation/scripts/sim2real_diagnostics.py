#!/usr/bin/env python3
import argparse
import json
import math
import os
import inspect
import sys
import time
from pathlib import Path

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
RUNTIME_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(RUNTIME_ROOT / "mini_bdx_runtime"))
sys.path.insert(0, str(SCRIPT_DIR))

from mini_bdx_runtime.telemetry import (  # noqa: E402
    SCHEMA_VERSION,
    JsonlTelemetryLogger,
    default_telemetry_path,
    extract_onnx_obs_normalization,
    normalize_observation,
    require_onnx_obs_normalization,
    sha256_file,
    utc_timestamp,
)


JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def import_hardware():
    from mini_bdx_runtime.duck_config import DuckConfig
    from mini_bdx_runtime.feet_contacts import FeetContacts
    from mini_bdx_runtime.raw_imu import Imu
    from mini_bdx_runtime.rustypot_position_hwi import HWI

    return DuckConfig, HWI, Imu, FeetContacts


def safety_banner(moves_robot=False, grounded=False):
    print("=== Open Duck Mini sim-to-real diagnostic ===", flush=True)
    if moves_robot:
        print("SAFETY: this test moves hardware.", flush=True)
        if not grounded:
            print("SAFETY: robot must be supported; do not run standing free.", flush=True)
        else:
            print("SAFETY: grounded test; be ready to cut power immediately.", flush=True)
        print("SAFETY: keep fingers clear of joints and linkage.", flush=True)
        print("SAFETY: movement amplitudes are small by default.", flush=True)


def require_motion_ack(args):
    if not getattr(args, "i_understand_this_moves_the_robot", False):
        raise SystemExit(
            "Refusing to move hardware without --i-understand-this-moves-the-robot"
        )


def make_logger(path, default_name):
    if path is None:
        path = default_telemetry_path(default_name)
    logger = JsonlTelemetryLogger(path)
    print("logging:", logger.path, flush=True)
    return logger


def policy_meta(args):
    return {
        "onnx_path": getattr(args, "onnx_model_path", None),
        "onnx_sha256": sha256_file(getattr(args, "onnx_model_path", "")),
        "input_name": "obs",
        "output_name": "continuous_actions",
    }


def build_observation(
    imu_data,
    commands,
    dof_pos,
    dof_vel,
    home,
    last_action,
    last_last_action,
    last_last_last_action,
    motor_targets,
    feet_contacts,
    imitation_phase,
):
    return np.concatenate(
        [
            np.asarray(imu_data["gyro"], dtype=float),
            np.asarray(imu_data["accelero"], dtype=float),
            np.asarray(commands, dtype=float),
            np.asarray(dof_pos, dtype=float) - np.asarray(home, dtype=float),
            np.asarray(dof_vel, dtype=float) * 0.05,
            np.asarray(last_action, dtype=float),
            np.asarray(last_last_action, dtype=float),
            np.asarray(last_last_last_action, dtype=float),
            np.asarray(motor_targets, dtype=float),
            np.asarray(feet_contacts, dtype=float),
            np.asarray(imitation_phase, dtype=float),
        ]
    )


def accel_roll_pitch(accel):
    ax, ay, az = [float(v) for v in accel]
    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
    return roll, pitch


def make_record(
    *,
    args,
    test,
    tick,
    t_mono,
    dt_s,
    duck_config,
    hwi=None,
    imu_data=None,
    feet_contacts=None,
    obs=None,
    norm=None,
    action=None,
    commanded=None,
    actual_pos=None,
    actual_vel=None,
    tracking_error=None,
    extra=None,
):
    joint_names = list(hwi.joints.keys()) if hwi is not None else JOINT_NAMES
    servo_ids = list(hwi.joints.values()) if hwi is not None else None
    offsets = (
        [hwi.joints_offsets.get(name) for name in joint_names] if hwi is not None else None
    )
    home = list(hwi.init_pos.values()) if hwi is not None else None
    mean = None if norm is None else norm.get("mean")
    std_recip = None if norm is None else norm.get("std_recip")
    normalized = normalize_observation(obs, mean, std_recip)
    raw_gyro = None if imu_data is None else imu_data.get("gyro")
    raw_accel = None if imu_data is None else imu_data.get("accelero")
    roll_pitch = None if raw_accel is None else accel_roll_pitch(raw_accel)
    record = {
        "schema_version": SCHEMA_VERSION,
        "tick": tick,
        "timestamp_monotonic_s": t_mono,
        "timestamp_wall": utc_timestamp(),
        "dt_s": dt_s,
        "test": test,
        "policy": policy_meta(args),
        "control": {
            "control_freq_hz": args.control_freq,
            "paused": True,
            "action_scale": getattr(args, "action_scale", None),
            "max_motor_velocity_rad_s": getattr(args, "max_motor_velocity", None),
            "commands": getattr(args, "commands_vector", [0.0] * 7),
            "imitation_i": 0,
            "imitation_phase": [0.0, 0.0],
            "feet_contacts": feet_contacts,
            "stop_reason": None,
        },
        "imu": {
            "imu_upside_down": getattr(duck_config, "imu_upside_down", None),
            "raw_gyro": raw_gyro,
            "raw_accelero": raw_accel,
            "policy_gyro": None if obs is None or len(obs) < 3 else obs[0:3],
            "policy_accelero": None if obs is None or len(obs) < 6 else obs[3:6],
            "diagnostic_roll_rad": None if roll_pitch is None else roll_pitch[0],
            "diagnostic_pitch_rad": None if roll_pitch is None else roll_pitch[1],
        },
        "joints": {
            "names": joint_names,
            "servo_ids": servo_ids,
            "offsets_rad": offsets,
            "home_rad": home,
            "commanded_position_rad": commanded,
            "actual_position_rad": actual_pos,
            "actual_velocity_rad_s": actual_vel,
            "tracking_error_rad": tracking_error,
            "battery_voltage_v": None,
        },
        "observation": {
            "raw_vector": obs,
            "normalized_vector": normalized,
            "normalization_mean": mean,
            "normalization_std_recip": std_recip,
            "normalization_source": None if norm is None else norm.get("source"),
            "normalization_error": None if norm is None else norm.get("error"),
        },
        "action": {
            "onnx_action": action,
            "scaled_delta_rad": None,
            "motor_targets_pre_rate_limit_rad": commanded,
            "motor_targets_post_rate_limit_rad": commanded,
            "motor_targets_sent_rad": commanded,
        },
        "bus": {
            "read_error_count": None
            if hwi is None
            else getattr(hwi, "read_error_count", None),
            "write_error_count": None
            if hwi is None
            else getattr(hwi, "write_error_count", None),
            "transport_reset_count": None
            if hwi is None
            else getattr(hwi, "transport_reset_count", None),
            "last_error": None if hwi is None else getattr(hwi, "last_error", None),
        },
    }
    if extra:
        record["extra"] = extra
    return record


def sample_home_like(args, hwi, imu, feet, norm, logger, test, duration):
    home = np.asarray(list(hwi.init_pos.values()), dtype=float)
    zeros = np.zeros(14)
    commands = np.zeros(7)
    phase = np.zeros(2)
    start = time.monotonic()
    last = None
    tick = 0
    while time.monotonic() - start < duration:
        t_mono = time.monotonic()
        dt_s = None if last is None else t_mono - last
        last = t_mono
        imu_data = imu.get_data()
        dof_pos = hwi.get_present_positions()
        dof_vel = hwi.get_present_velocities()
        contacts = feet.get()
        obs = None
        tracking = None
        if dof_pos is not None and dof_vel is not None:
            obs = build_observation(
                imu_data,
                commands,
                dof_pos,
                dof_vel,
                home,
                zeros,
                zeros,
                zeros,
                home,
                contacts,
                phase,
            )
            tracking = dof_pos - home
        logger.log(
            make_record(
                args=args,
                test=test,
                tick=tick,
                t_mono=t_mono,
                dt_s=dt_s,
                duck_config=hwi.duck_config,
                hwi=hwi,
                imu_data=imu_data,
                feet_contacts=contacts,
                obs=obs,
                norm=norm,
                commanded=home,
                actual_pos=dof_pos,
                actual_vel=dof_vel,
                tracking_error=tracking,
            )
        )
        tick += 1
        time.sleep(max(0, 1 / args.control_freq))


def cmd_home_pose_log_test(args):
    require_motion_ack(args)
    safety_banner(moves_robot=True)
    DuckConfig, HWI, Imu, FeetContacts = import_hardware()
    cfg = DuckConfig(config_json_path=args.duck_config_path)
    hwi = HWI(cfg, args.serial_port)
    imu = Imu(args.control_freq, upside_down=cfg.imu_upside_down)
    feet = FeetContacts()
    norm = extract_onnx_obs_normalization(args.onnx_model_path)
    require_onnx_obs_normalization(norm, args.onnx_model_path)
    logger = make_logger(args.telemetry_path, "home_pose_log_test")
    try:
        hwi.turn_on()
        sample_home_like(args, hwi, imu, feet, norm, logger, "home_pose_log_test", args.duration)
    finally:
        logger.close()
        feet.stop()
        if args.torque_off_on_exit:
            hwi.turn_off()


def cmd_imu_tilt_test(args):
    safety_banner(moves_robot=False)
    print(
        "Tilt sequence: upright, nose forward, upright, nose backward, upright, left, upright, right.",
        flush=True,
    )
    DuckConfig, HWI, Imu, FeetContacts = import_hardware()
    cfg = DuckConfig(config_json_path=args.duck_config_path)
    hwi = HWI(cfg, args.serial_port) if args.read_joints else None
    imu = Imu(args.control_freq, upside_down=cfg.imu_upside_down)
    feet = FeetContacts()
    norm = extract_onnx_obs_normalization(args.onnx_model_path)
    require_onnx_obs_normalization(norm, args.onnx_model_path)
    logger = make_logger(args.telemetry_path, "imu_tilt_test")
    home = None if hwi is None else np.asarray(list(hwi.init_pos.values()), dtype=float)
    zeros = np.zeros(14)
    start = time.monotonic()
    last = None
    tick = 0
    try:
        while time.monotonic() - start < args.duration:
            t_mono = time.monotonic()
            dt_s = None if last is None else t_mono - last
            last = t_mono
            imu_data = imu.get_data()
            contacts = feet.get()
            dof_pos = hwi.get_present_positions() if hwi is not None else None
            dof_vel = hwi.get_present_velocities() if hwi is not None else None
            obs = np.concatenate([imu_data["gyro"], imu_data["accelero"]])
            if hwi is not None and dof_pos is not None and dof_vel is not None:
                obs = build_observation(
                    imu_data,
                    np.zeros(7),
                    dof_pos,
                    dof_vel,
                    home,
                    zeros,
                    zeros,
                    zeros,
                    home,
                    contacts,
                    np.zeros(2),
                )
            logger.log(
                make_record(
                    args=args,
                    test="imu_tilt_test",
                    tick=tick,
                    t_mono=t_mono,
                    dt_s=dt_s,
                    duck_config=cfg,
                    hwi=hwi,
                    imu_data=imu_data,
                    feet_contacts=contacts,
                    obs=obs,
                    norm=norm if len(obs) == 101 else None,
                    actual_pos=dof_pos,
                    actual_vel=dof_vel,
                )
            )
            tick += 1
            time.sleep(max(0, 1 / args.control_freq))
    finally:
        logger.close()
        feet.stop()


def cmd_foot_contact_test(args):
    safety_banner(moves_robot=False)
    DuckConfig, HWI, Imu, FeetContacts = import_hardware()
    cfg = DuckConfig(config_json_path=args.duck_config_path)
    feet = FeetContacts()
    logger = make_logger(args.telemetry_path, "foot_contact_test")
    start = time.monotonic()
    last = None
    tick = 0
    try:
        while time.monotonic() - start < args.duration:
            t_mono = time.monotonic()
            dt_s = None if last is None else t_mono - last
            last = t_mono
            contacts = feet.get()
            raw_gpio = {"left_raw_gpio_value": None, "right_raw_gpio_value": None}
            if getattr(feet, "_use_hobot", False):
                module = sys.modules.get(FeetContacts.__module__)
                left_pin = getattr(module, "LEFT_FOOT_PIN_BCM", 22)
                right_pin = getattr(module, "RIGHT_FOOT_PIN_BCM", 27)
                raw_gpio = {
                    "left_raw_gpio_value": bool(feet.GPIO.input(left_pin)),
                    "right_raw_gpio_value": bool(feet.GPIO.input(right_pin)),
                }
            elif hasattr(feet, "left_foot") and hasattr(feet, "right_foot"):
                raw_gpio = {
                    "left_raw_gpio_value": bool(feet.left_foot.value),
                    "right_raw_gpio_value": bool(feet.right_foot.value),
                }
            logger.log(
                make_record(
                    args=args,
                    test="foot_contact_test",
                    tick=tick,
                    t_mono=t_mono,
                    dt_s=dt_s,
                    duck_config=cfg,
                    feet_contacts=contacts,
                    extra=raw_gpio,
                )
            )
            print(f"tick={tick} contacts={contacts} raw={raw_gpio}", flush=True)
            tick += 1
            time.sleep(max(0, 1 / args.control_freq))
    finally:
        logger.close()
        feet.stop()


def cmd_joint_identity_test(args):
    require_motion_ack(args)
    safety_banner(moves_robot=True)
    DuckConfig, HWI, Imu, FeetContacts = import_hardware()
    cfg = DuckConfig(config_json_path=args.duck_config_path)
    hwi = HWI(cfg, args.serial_port)
    logger = make_logger(args.telemetry_path, "joint_identity_test")
    home = hwi.init_pos.copy()
    summary = []
    try:
        hwi.turn_on()
        hwi.set_position_all(home)
        time.sleep(1.0)
        tick = 0
        for joint in hwi.joints.keys():
            row = {"joint": joint, "servo_id": hwi.joints[joint], "amp_rad": args.amp}
            for label, sign in (("plus", 1.0), ("minus", -1.0)):
                target = home.copy()
                target[joint] = home[joint] + sign * args.amp
                hwi.set_position_all(target)
                time.sleep(args.hold)
                got = hwi.get_present_positions()
                names = list(hwi.joints.keys())
                if got is not None:
                    actual = dict(zip(names, [float(v) for v in got]))
                    row[f"{label}_actual_delta_rad"] = actual[joint] - home[joint]
                    row[f"{label}_tracking_error_rad"] = actual[joint] - target[joint]
                logger.log(
                    make_record(
                        args=args,
                        test="joint_identity_test",
                        tick=tick,
                        t_mono=time.monotonic(),
                        dt_s=None,
                        duck_config=cfg,
                        hwi=hwi,
                        commanded=[target[name] for name in names],
                        actual_pos=got,
                        tracking_error=None if got is None else got - np.asarray([target[name] for name in names]),
                        extra={"active_joint": joint, "phase": label, "visual_direction": "USER_FILL"},
                    )
                )
                tick += 1
                hwi.set_position_all(home)
                time.sleep(0.25)
            row["visual_positive_direction"] = "USER_FILL"
            summary.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
        hwi.set_position_all(home)
        if args.summary_path:
            Path(args.summary_path).parent.mkdir(parents=True, exist_ok=True)
            with open(args.summary_path, "w") as f:
                json.dump(summary, f, indent=2)
                f.write("\n")
            print("summary:", args.summary_path, flush=True)
    finally:
        logger.close()
        if args.torque_off_on_exit:
            hwi.turn_off()


def cmd_policy_replay(args):
    require_motion_ack(args)
    safety_banner(moves_robot=True, grounded=args.mode == "grounded_policy_replay")
    from v2_rl_walk_mujoco import RLWalk

    if args.telemetry_path is None:
        args.telemetry_path = default_telemetry_path(args.mode)
    kwargs = {
        "duck_config_path": args.duck_config_path,
        "serial_port": args.serial_port,
        "control_freq": args.control_freq,
        "action_scale": args.action_scale,
        "commands": False,
        "fixed_command_x": args.command_x,
        "max_runtime_seconds": args.duration,
        "force_unpaused": False,
        "kp_overrides": {
            name: value
            for name, value in (
                ("left_hip_pitch", args.left_hip_pitch_kp),
                ("left_knee", args.left_knee_kp),
            )
            if value is not None
        },
        "motor_velocity_limits_rad_s": args.motor_velocity_limits_rad_s,
    }
    required_telemetry_args = {
        "log_telemetry",
        "telemetry_path",
        "telemetry_read_voltage",
        "telemetry_every_n",
    }
    supported = set(inspect.signature(RLWalk.__init__).parameters)
    missing = sorted(required_telemetry_args - supported)
    if missing:
        raise SystemExit(
            "suspended_policy_replay requires RLWalk telemetry support. "
            "Deploy runtime telemetry patch first. "
            f"Missing args: {', '.join(missing)}"
        )
    kwargs.update(
        {
            "log_telemetry": True,
            "telemetry_path": args.telemetry_path,
            "telemetry_read_voltage": args.telemetry_read_voltage,
            "telemetry_every_n": args.telemetry_every_n,
        }
    )
    rl = RLWalk(args.onnx_model_path, **kwargs)
    ran = False
    try:
        rl.paused = True
        print("Policy replay initialized paused; telemetry file is open.", flush=True)
        input("Press Enter to unpause and start replay, or Ctrl+C to abort.")
        rl.paused = False
        ran = True
        rl.run()
    finally:
        if not ran:
            try:
                rl.cleanup()
            except Exception:
                pass


def cmd_actuator_sine_sweep(args):
    require_motion_ack(args)
    safety_banner(moves_robot=True)
    DuckConfig, HWI, Imu, FeetContacts = import_hardware()
    cfg = DuckConfig(config_json_path=args.duck_config_path)
    hwi = HWI(cfg, args.serial_port)
    logger = make_logger(args.telemetry_path, "actuator_sine_sweep")
    home = hwi.init_pos.copy()
    names = list(hwi.joints.keys())
    summary = []
    try:
        hwi.turn_on()
        hwi.set_position_all(home)
        time.sleep(1.0)
        tick = 0
        for joint in args.joints:
            if joint not in hwi.joints:
                print(f"skipping unknown joint {joint}", flush=True)
                continue
            for freq in args.frequencies:
                start = time.monotonic()
                errors = []
                while time.monotonic() - start < args.seconds_per_frequency:
                    elapsed = time.monotonic() - start
                    target = home.copy()
                    target[joint] = home[joint] + args.amp * math.sin(2 * math.pi * freq * elapsed)
                    hwi.set_position_all(target)
                    got = hwi.get_present_positions()
                    target_vec = np.asarray([target[name] for name in names])
                    error = None if got is None else got - target_vec
                    if error is not None:
                        errors.append(abs(float(error[names.index(joint)])))
                    logger.log(
                        make_record(
                            args=args,
                            test="actuator_sine_sweep",
                            tick=tick,
                            t_mono=time.monotonic(),
                            dt_s=None,
                            duck_config=cfg,
                            hwi=hwi,
                            commanded=target_vec,
                            actual_pos=got,
                            tracking_error=error,
                            extra={"active_joint": joint, "frequency_hz": freq},
                        )
                    )
                    tick += 1
                    time.sleep(max(0, 1 / args.control_freq))
                if errors:
                    errors = sorted(errors)
                    p95 = errors[int(0.95 * (len(errors) - 1))]
                    summary.append({"joint": joint, "frequency_hz": freq, "p95_abs_error_rad": p95})
                hwi.set_position_all(home)
                time.sleep(0.5)
        print(json.dumps(summary, indent=2), flush=True)
    finally:
        logger.close()
        hwi.set_position_all(home)
        if args.torque_off_on_exit:
            hwi.turn_off()


def add_common(sub):
    sub.add_argument("--duck_config_path", default=os.path.expanduser("~/duck_config.json"))
    sub.add_argument("--serial_port", default="/dev/ttyACM0")
    sub.add_argument("--control_freq", type=int, default=50)
    sub.add_argument("--telemetry-path", default=None)
    sub.add_argument("--onnx_model_path", default=os.path.expanduser("~/BEST_WALK_ONNX_2.onnx"))


def main():
    parser = argparse.ArgumentParser(description="Open Duck Mini sim-to-real diagnostics")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("home_pose_log_test")
    add_common(p)
    p.add_argument("--duration", type=float, default=10.0)
    p.add_argument("--torque-off-on-exit", action="store_true")
    p.add_argument("--i-understand-this-moves-the-robot", action="store_true")
    p.set_defaults(func=cmd_home_pose_log_test)

    p = subparsers.add_parser("imu_tilt_test")
    add_common(p)
    p.add_argument("--duration", type=float, default=35.0)
    p.add_argument("--read-joints", action="store_true")
    p.set_defaults(func=cmd_imu_tilt_test)

    p = subparsers.add_parser("foot_contact_test")
    add_common(p)
    p.add_argument("--duration", type=float, default=20.0)
    p.set_defaults(func=cmd_foot_contact_test)

    p = subparsers.add_parser("joint_identity_test")
    add_common(p)
    p.add_argument("--amp", type=float, default=0.03)
    p.add_argument("--hold", type=float, default=0.5)
    p.add_argument("--summary-path", default="outputs/telemetry/joint_identity_test_summary.json")
    p.add_argument("--torque-off-on-exit", action="store_true")
    p.add_argument("--i-understand-this-moves-the-robot", action="store_true")
    p.set_defaults(func=cmd_joint_identity_test)

    for name in ("suspended_policy_replay", "grounded_policy_replay"):
        p = subparsers.add_parser(name)
        add_common(p)
        p.add_argument("--duration", type=float, default=15.0)
        p.add_argument("--command-x", type=float, default=0.0)
        p.add_argument("--action_scale", type=float, default=0.25)
        p.add_argument("--max_motor_velocity", type=float, default=5.24)
        p.add_argument(
            "--motor-velocity-limits-rad-s",
            dest="motor_velocity_limits_rad_s",
            type=lambda text: [float(item.strip()) for item in text.split(",")],
            default=None,
        )
        p.add_argument("--telemetry-read-voltage", action="store_true")
        p.add_argument("--telemetry-every-n", type=int, default=1)
        p.add_argument("--left-hip-pitch-kp", type=float, default=None)
        p.add_argument("--left-knee-kp", type=float, default=None)
        p.add_argument("--i-understand-this-moves-the-robot", action="store_true")
        p.set_defaults(func=cmd_policy_replay, mode=name)

    p = subparsers.add_parser("actuator_sine_sweep")
    add_common(p)
    p.add_argument("--amp", type=float, default=0.03)
    p.add_argument("--frequencies", type=float, nargs="+", default=[0.25, 0.5, 1.0])
    p.add_argument("--seconds-per-frequency", type=float, default=6.0)
    p.add_argument(
        "--joints",
        nargs="+",
        default=[
            "left_hip_pitch",
            "right_hip_pitch",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle",
        ],
    )
    p.add_argument("--action_scale", type=float, default=None)
    p.add_argument("--max_motor_velocity", type=float, default=None)
    p.add_argument("--torque-off-on-exit", action="store_true")
    p.add_argument("--i-understand-this-moves-the-robot", action="store_true")
    p.set_defaults(func=cmd_actuator_sine_sweep)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
