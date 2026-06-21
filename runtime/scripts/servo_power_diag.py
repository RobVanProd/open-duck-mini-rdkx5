#!/usr/bin/env python3
"""Small powered diagnostics for Open Duck Mini servo reset isolation."""

import argparse
import os
import sys
import time

from mini_bdx_runtime.duck_config import DuckConfig
from mini_bdx_runtime.rustypot_position_hwi import HWI


HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "duck_logs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["enable_hold", "off_only"])
    parser.add_argument("--hold", type=float, default=20.0)
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "servo_power_diag_%d_%s.log" % (int(time.time()), args.mode))
    log_file = open(log_path, "a", buffering=1)

    def log(msg):
        line = "[%.2f] %s" % (time.time(), msg)
        print(line, flush=True)
        log_file.write(line + "\n")

    log("mode=%s hold=%s" % (args.mode, args.hold))
    cfg = DuckConfig()
    hwi = HWI(cfg)

    if args.mode == "enable_hold":
        log("turn_on begin")
        hwi.turn_on()
        log("turn_on complete")
        start = time.time()
        while time.time() - start < args.hold:
            pos = hwi.get_present_positions()
            log("holding t=%.1f pos=%s" % (time.time() - start, pos.tolist() if pos is not None else None))
            time.sleep(2.0)
        log("leaving torque enabled; exiting without turn_off")
        return 0

    if args.mode == "off_only":
        log("turn_off begin")
        hwi.turn_off()
        log("turn_off complete")
        time.sleep(3.0)
        log("still alive after turn_off")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
